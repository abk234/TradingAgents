"""
Outcome Tracker - Phase 6

Tracks what happens to stocks after we recommend them.
This creates a feedback loop for continuous AI improvement.
"""

from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
import logging

import yfinance as yf

from tradingagents.database import get_db_connection

logger = logging.getLogger(__name__)


class OutcomeTracker:
    """Track outcomes of stock recommendations."""

    def __init__(self):
        """Initialize outcome tracker."""
        self.db = get_db_connection()

    def backfill_historical_recommendations(self, days_back: int = 90):
        """
        Create outcome records for historical analyses.

        Args:
            days_back: How many days back to look for analyses
        """
        logger.info(f"Backfilling recommendation outcomes for last {days_back} days...")

        # Find all analyses from the last N days that don't have outcome records yet
        query = """
            SELECT a.analysis_id, a.ticker_id, a.analysis_date,
                   a.final_decision, a.confidence_score, t.symbol
            FROM analyses a
            JOIN tickers t ON a.ticker_id = t.ticker_id
            WHERE a.analysis_date >= CURRENT_DATE - INTERVAL '%s days'
            AND NOT EXISTS (
                SELECT 1 FROM recommendation_outcomes ro
                WHERE ro.analysis_id = a.analysis_id
            )
            ORDER BY a.analysis_date DESC
        """

        analyses = self.db.execute_dict_query(query, (days_back,))
        if analyses is None:
            analyses = []
        logger.info(f"Found {len(analyses)} analyses to backfill")

        created_count = 0
        for analysis in analyses:
            try:
                self._create_outcome_record(analysis)
                created_count += 1
            except Exception as e:
                logger.error(f"Failed to create outcome for analysis {analysis['analysis_id']}: {e}")

        logger.info(f"Created {created_count} outcome records")
        return created_count

    def _create_outcome_record(self, analysis: Dict[str, Any]):
        """Create an outcome record for an analysis."""
        analysis_id = analysis['analysis_id']
        ticker_id = analysis['ticker_id']
        symbol = analysis['symbol']
        analyzed_at = analysis['analysis_date']
        decision = analysis['final_decision']
        confidence = analysis['confidence_score']

        # Get the recommendation date (date portion of analysis_date)
        recommendation_date = analyzed_at.date() if isinstance(analyzed_at, datetime) else analyzed_at

        # Fetch historical price data for this stock
        # We need: entry price + prices at various intervals
        try:
            ticker = yf.Ticker(symbol)

            # Fetch enough history to cover all intervals
            start_date = recommendation_date - timedelta(days=5)  # A bit before to get entry price
            end_date = date.today()

            hist = ticker.history(start=start_date, end=end_date)

            if hist.empty:
                logger.warning(f"No price data for {symbol}")
                return

            # Get entry price (close price on recommendation date)
            entry_price = self._get_price_on_date(hist, recommendation_date)
            if not entry_price:
                logger.warning(f"No entry price for {symbol} on {recommendation_date}")
                return

            # Get position recommendation if it exists
            rec_query = """
                SELECT recommended_amount, position_size_pct, target_price, entry_price as rec_entry_price
                FROM position_recommendations
                WHERE analysis_id = %s
                LIMIT 1
            """
            rec_data = self.db.execute_dict_query(rec_query, (analysis_id,), fetch_one=True)

            recommended_amount = rec_data['recommended_amount'] if rec_data else None
            position_size_pct = rec_data['position_size_pct'] if rec_data else None
            target_price = rec_data['target_price'] if rec_data else None

            # Insert outcome record
            insert_query = """
                INSERT INTO recommendation_outcomes (
                    analysis_id, ticker_id, recommendation_date, analyzed_at,
                    decision, confidence, recommended_entry_price,
                    recommended_position_amount, recommended_position_size_pct,
                    target_price, evaluation_status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'PENDING')
                RETURNING outcome_id
            """

            result = self.db.execute_query(
                insert_query,
                (analysis_id, ticker_id, recommendation_date, analyzed_at,
                 decision, confidence, entry_price,
                 recommended_amount, position_size_pct, target_price),
                fetch_one=True
            )

            outcome_id = result[0]
            logger.info(f"Created outcome record {outcome_id} for {symbol} (analysis {analysis_id})")

        except Exception as e:
            logger.error(f"Error creating outcome for {symbol}: {e}")
            raise

    def update_outcomes(self, lookback_days: int = 90):
        """
        Update outcome records with latest price data.

        Args:
            lookback_days: Update outcomes from last N days
        """
        logger.info(f"Updating outcomes for last {lookback_days} days...")

        # Get all outcomes that need updating
        query = """
            SELECT ro.outcome_id, ro.recommendation_date, ro.recommended_entry_price,
                   ro.target_price, ro.stop_loss_price, ro.decision,
                   t.symbol, ro.evaluation_status
            FROM recommendation_outcomes ro
            JOIN tickers t ON ro.ticker_id = t.ticker_id
            WHERE ro.recommendation_date >= CURRENT_DATE - INTERVAL '%s days'
            AND ro.evaluation_status IN ('PENDING', 'TRACKING')
            ORDER BY ro.recommendation_date DESC
        """

        outcomes = self.db.execute_dict_query(query, (lookback_days,))
        if outcomes is None:
            outcomes = []
        logger.info(f"Found {len(outcomes)} outcomes to update")

        updated_count = 0
        for outcome in outcomes:
            try:
                self._update_outcome_prices(outcome)
                updated_count += 1
            except Exception as e:
                logger.error(f"Failed to update outcome {outcome['outcome_id']}: {e}")

        logger.info(f"Updated {updated_count} outcomes")
        return updated_count

    def _update_outcome_prices(self, outcome: Dict[str, Any]):
        """Update prices and returns for an outcome."""
        outcome_id = outcome['outcome_id']
        symbol = outcome['symbol']
        rec_date = outcome['recommendation_date']
        entry_price = Decimal(str(outcome['recommended_entry_price']))
        decision = outcome['decision']

        # Calculate target dates
        today = date.today()
        date_1day = rec_date + timedelta(days=1)
        date_3days = rec_date + timedelta(days=3)
        date_7days = rec_date + timedelta(days=7)
        date_14days = rec_date + timedelta(days=14)
        date_30days = rec_date + timedelta(days=30)
        date_60days = rec_date + timedelta(days=60)
        date_90days = rec_date + timedelta(days=90)

        # Don't fetch future prices
        if date_1day > today:
            logger.debug(f"Skipping {symbol} - too recent (< 1 day old)")
            return

        try:
            # Fetch price history
            ticker = yf.Ticker(symbol)
            start_date = rec_date
            end_date = min(date_90days + timedelta(days=5), today)  # Add buffer, cap at today

            hist = ticker.history(start=start_date, end=end_date)

            if hist.empty:
                logger.warning(f"No price data for {symbol}")
                return

            # Get prices at each interval
            price_1day = self._get_price_on_date(hist, date_1day) if date_1day <= today else None
            price_3days = self._get_price_on_date(hist, date_3days) if date_3days <= today else None
            price_7days = self._get_price_on_date(hist, date_7days) if date_7days <= today else None
            price_14days = self._get_price_on_date(hist, date_14days) if date_14days <= today else None
            price_30days = self._get_price_on_date(hist, date_30days) if date_30days <= today else None
            price_60days = self._get_price_on_date(hist, date_60days) if date_60days <= today else None
            price_90days = self._get_price_on_date(hist, date_90days) if date_90days <= today else None

            # Calculate returns
            def calc_return(price):
                if price and entry_price:
                    return ((Decimal(str(price)) - entry_price) / entry_price * 100).quantize(Decimal('0.01'))
                return None

            return_1day = calc_return(price_1day)
            return_3days = calc_return(price_3days)
            return_7days = calc_return(price_7days)
            return_14days = calc_return(price_14days)
            return_30days = calc_return(price_30days)
            return_60days = calc_return(price_60days)
            return_90days = calc_return(price_90days)

            # Find peak and trough
            all_prices = hist['Close'].values
            peak_price = float(max(all_prices))
            trough_price = float(min(all_prices))
            peak_return = calc_return(peak_price)
            trough_return = calc_return(trough_price)

            # Find dates
            peak_date = hist['Close'].idxmax().date()
            trough_date = hist['Close'].idxmin().date()

            # Check if hit target or stop loss
            target_price = outcome.get('target_price')
            stop_loss_price = outcome.get('stop_loss_price')

            hit_target = False
            hit_stop_loss = False

            if target_price and peak_price >= float(target_price):
                hit_target = True

            if stop_loss_price and trough_price <= float(stop_loss_price):
                hit_stop_loss = True

            # Determine evaluation status
            days_since = (today - rec_date).days
            if days_since >= 90:
                eval_status = 'COMPLETED'
            else:
                eval_status = 'TRACKING'

            # Update the outcome record
            update_query = """
                UPDATE recommendation_outcomes
                SET price_after_1day = %s,
                    price_after_3days = %s,
                    price_after_7days = %s,
                    price_after_14days = %s,
                    price_after_30days = %s,
                    price_after_60days = %s,
                    price_after_90days = %s,
                    return_1day_pct = %s,
                    return_3days_pct = %s,
                    return_7days_pct = %s,
                    return_14days_pct = %s,
                    return_30days_pct = %s,
                    return_60days_pct = %s,
                    return_90days_pct = %s,
                    peak_price = %s,
                    peak_date = %s,
                    peak_return_pct = %s,
                    trough_price = %s,
                    trough_date = %s,
                    trough_return_pct = %s,
                    hit_target = %s,
                    hit_stop_loss = %s,
                    evaluation_status = %s,
                    last_evaluated_at = CURRENT_TIMESTAMP
                WHERE outcome_id = %s
            """

            self.db.execute_query(
                update_query,
                (price_1day, price_3days, price_7days, price_14days,
                 price_30days, price_60days, price_90days,
                 return_1day, return_3days, return_7days, return_14days,
                 return_30days, return_60days, return_90days,
                 peak_price, peak_date, peak_return,
                 trough_price, trough_date, trough_return,
                 hit_target, hit_stop_loss, eval_status,
                 outcome_id),
                fetch=False
            )

            logger.debug(f"Updated outcome {outcome_id} for {symbol}: {return_30days}% (30d)")

        except Exception as e:
            logger.error(f"Error updating outcome for {symbol}: {e}")
            raise

    def _get_price_on_date(self, hist, target_date: date) -> Optional[float]:
        """
        Get closing price on a specific date from price history.

        If exact date doesn't exist (weekend/holiday), get nearest date.
        """
        try:
            # Convert target_date to pandas Timestamp for comparison
            import pandas as pd
            target_ts = pd.Timestamp(target_date)

            # Try exact date first
            if target_ts in hist.index:
                return float(hist.loc[target_ts, 'Close'])

            # If not, find nearest date (forward fill)
            valid_dates = hist.index[hist.index >= target_ts]
            if len(valid_dates) > 0:
                nearest_date = valid_dates[0]
                return float(hist.loc[nearest_date, 'Close'])

            # If no future dates, use last available
            if len(hist) > 0:
                return float(hist.iloc[-1]['Close'])

            return None

        except Exception as e:
            logger.debug(f"Could not get price for {target_date}: {e}")
            return None

    def update_sp500_benchmark(self, days_back: int = 90):
        """
        Fetch and store S&P 500 (SPY) prices for benchmark comparison.

        Args:
            days_back: How many days of history to fetch
        """
        logger.info("Updating S&P 500 benchmark data...")

        try:
            spy = yf.Ticker('SPY')
            start_date = date.today() - timedelta(days=days_back)
            hist = spy.history(start=start_date)

            if hist.empty:
                logger.error("Failed to fetch SPY data")
                return 0

            inserted = 0
            for idx, row in hist.iterrows():
                price_date = idx.date()

                query = """
                    INSERT INTO benchmark_prices (
                        benchmark_symbol, price_date, close_price,
                        open_price, high_price, low_price, volume
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (benchmark_symbol, price_date)
                    DO UPDATE SET
                        close_price = EXCLUDED.close_price,
                        open_price = EXCLUDED.open_price,
                        high_price = EXCLUDED.high_price,
                        low_price = EXCLUDED.low_price,
                        volume = EXCLUDED.volume
                """

                self.db.execute_query(
                    query,
                    ('SPY', price_date, float(row['Close']),
                     float(row['Open']), float(row['High']),
                     float(row['Low']), int(row['Volume'])),
                    fetch=False
                )
                inserted += 1

            logger.info(f"Updated {inserted} days of S&P 500 data")
            return inserted

        except Exception as e:
            logger.error(f"Error updating S&P 500 benchmark: {e}")
            return 0

    def calculate_alpha(self):
        """
        Calculate alpha (excess return vs S&P 500) for all outcomes.
        """
        logger.info("Calculating alpha vs S&P 500...")

        # Get all outcomes with 30-day returns
        query = """
            SELECT ro.outcome_id, ro.recommendation_date,
                   ro.return_30days_pct, ro.return_90days_pct
            FROM recommendation_outcomes ro
            WHERE ro.return_30days_pct IS NOT NULL
            AND ro.sp500_return_30days_pct IS NULL
        """

        outcomes = self.db.execute_dict_query(query)
        if outcomes is None:
            outcomes = []
        logger.info(f"Calculating alpha for {len(outcomes)} outcomes")

        updated = 0
        for outcome in outcomes:
            try:
                outcome_id = outcome['outcome_id']
                rec_date = outcome['recommendation_date']

                # Get SPY prices
                date_30 = rec_date + timedelta(days=30)
                date_90 = rec_date + timedelta(days=90)

                # 30-day SPY return
                spy_30 = self._get_spy_return(rec_date, date_30)
                # 90-day SPY return
                spy_90 = self._get_spy_return(rec_date, date_90) if outcome['return_90days_pct'] else None

                # Calculate alpha
                alpha_30 = None
                alpha_90 = None

                if spy_30 and outcome['return_30days_pct']:
                    alpha_30 = outcome['return_30days_pct'] - spy_30

                if spy_90 and outcome['return_90days_pct']:
                    alpha_90 = outcome['return_90days_pct'] - spy_90

                # Update record
                update_query = """
                    UPDATE recommendation_outcomes
                    SET sp500_return_30days_pct = %s,
                        sp500_return_90days_pct = %s,
                        alpha_30days_pct = %s,
                        alpha_90days_pct = %s
                    WHERE outcome_id = %s
                """

                self.db.execute_query(
                    update_query,
                    (spy_30, spy_90, alpha_30, alpha_90, outcome_id),
                    fetch=False
                )

                updated += 1

            except Exception as e:
                logger.error(f"Error calculating alpha for outcome {outcome['outcome_id']}: {e}")

        logger.info(f"Updated alpha for {updated} outcomes")
        return updated

    def _get_spy_return(self, start_date: date, end_date: date) -> Optional[Decimal]:
        """Calculate SPY return between two dates."""
        try:
            # Get prices from database
            query = """
                SELECT close_price FROM benchmark_prices
                WHERE benchmark_symbol = 'SPY' AND price_date >= %s
                ORDER BY price_date ASC LIMIT 1
            """
            start_row = self.db.execute_dict_query(query, (start_date,), fetch_one=True)

            query = """
                SELECT close_price FROM benchmark_prices
                WHERE benchmark_symbol = 'SPY' AND price_date >= %s
                ORDER BY price_date ASC LIMIT 1
            """
            end_row = self.db.execute_dict_query(query, (end_date,), fetch_one=True)

            if not start_row or not end_row:
                return None

            start_price = Decimal(str(start_row['close_price']))
            end_price = Decimal(str(end_row['close_price']))

            spy_return = ((end_price - start_price) / start_price * 100).quantize(Decimal('0.01'))
            return spy_return

        except Exception as e:
            logger.debug(f"Could not calculate SPY return: {e}")
            return None
