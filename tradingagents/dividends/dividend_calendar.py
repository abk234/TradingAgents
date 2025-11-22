# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Dividend calendar for upcoming dividend payments.

Predicts future dividend payments based on historical patterns.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
from collections import defaultdict

from tradingagents.database import DatabaseConnection
from .dividend_fetcher import get_ticker_id

logger = logging.getLogger(__name__)


class DividendCalendar:
    """Manages upcoming dividend payment calendar."""

    def __init__(self, db_conn: Optional[DatabaseConnection] = None):
        """
        Initialize dividend calendar.

        Args:
            db_conn: Database connection (creates new if not provided)
        """
        self.db = db_conn or DatabaseConnection()

    def predict_next_dividend(
        self,
        symbol: str
    ) -> Optional[Dict[str, Any]]:
        """
        Predict next dividend payment based on historical pattern.

        Args:
            symbol: Stock symbol

        Returns:
            Dict with predicted dividend info or None
        """
        try:
            ticker_id = get_ticker_id(self.db, symbol)
            if ticker_id is None:
                return None

            # Get recent dividend history
            query = """
                SELECT
                    ex_dividend_date,
                    dividend_per_share,
                    payment_date
                FROM dividend_payments
                WHERE ticker_id = %s
                    AND status = 'PAID'
                ORDER BY ex_dividend_date DESC
                LIMIT 8
            """

            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (ticker_id,))
                    history = cur.fetchall()

            if len(history) < 2:
                return None

            # Calculate average interval between dividends
            intervals = []
            for i in range(len(history) - 1):
                days = (history[i][0] - history[i+1][0]).days
                intervals.append(days)

            avg_interval = sum(intervals) / len(intervals)

            # Predict next ex-date
            last_ex_date = history[0][0]
            next_ex_date = last_ex_date + timedelta(days=int(avg_interval))

            # Only predict if it's in the future
            if next_ex_date <= datetime.now().date():
                # Adjust to future
                while next_ex_date <= datetime.now().date():
                    next_ex_date += timedelta(days=int(avg_interval))

            # Predict payment date (average delay)
            payment_delays = [
                (h[2] - h[0]).days
                for h in history
                if h[2] is not None
            ]
            avg_payment_delay = sum(payment_delays) / len(payment_delays) if payment_delays else 21
            next_payment_date = next_ex_date + timedelta(days=int(avg_payment_delay))

            # Predict amount (use recent average)
            recent_amounts = [h[1] for h in history[:4]]
            predicted_amount = sum(recent_amounts) / len(recent_amounts)

            return {
                'symbol': symbol,
                'expected_ex_date': next_ex_date,
                'expected_payment_date': next_payment_date,
                'expected_amount_per_share': predicted_amount,
                'is_confirmed': False,
                'based_on_history': len(history),
                'confidence': self._calculate_confidence(intervals)
            }

        except Exception as e:
            logger.error(f"Error predicting dividend for {symbol}: {e}")
            return None

    def _calculate_confidence(self, intervals: List[int]) -> str:
        """
        Calculate confidence in prediction based on interval consistency.

        Args:
            intervals: List of day intervals between dividends

        Returns:
            Confidence level: HIGH, MEDIUM, or LOW
        """
        if len(intervals) < 2:
            return 'LOW'

        # Calculate standard deviation
        avg = sum(intervals) / len(intervals)
        variance = sum((x - avg) ** 2 for x in intervals) / len(intervals)
        std_dev = variance ** 0.5

        # Coefficient of variation
        cv = (std_dev / avg) if avg > 0 else 1.0

        if cv < 0.05:  # Very consistent
            return 'HIGH'
        elif cv < 0.15:  # Reasonably consistent
            return 'MEDIUM'
        else:
            return 'LOW'

    def update_calendar(self, days_ahead: int = 180) -> int:
        """
        Update dividend calendar with predictions for all tickers.

        Args:
            days_ahead: How many days ahead to predict

        Returns:
            Number of predictions added
        """
        try:
            # Get all active tickers with dividend history
            query = """
                SELECT DISTINCT t.ticker_id, t.symbol
                FROM tickers t
                JOIN dividend_payments dp ON t.ticker_id = dp.ticker_id
                WHERE t.active = TRUE
                ORDER BY t.symbol
            """

            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    tickers = cur.fetchall()

            count = 0
            cutoff_date = datetime.now().date() + timedelta(days=days_ahead)

            for ticker_id, symbol in tickers:
                prediction = self.predict_next_dividend(symbol)

                if prediction and prediction['expected_ex_date'] <= cutoff_date:
                    # Store in calendar
                    if self._store_prediction(ticker_id, prediction):
                        count += 1

            logger.info(f"Updated dividend calendar: {count} predictions")
            return count

        except Exception as e:
            logger.error(f"Error updating calendar: {e}")
            return 0

    def _store_prediction(
        self,
        ticker_id: int,
        prediction: Dict[str, Any]
    ) -> bool:
        """Store dividend prediction in calendar."""
        try:
            query = """
                INSERT INTO dividend_calendar (
                    ticker_id,
                    expected_ex_date,
                    expected_payment_date,
                    expected_amount_per_share,
                    is_confirmed
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (ticker_id, expected_ex_date)
                DO UPDATE SET
                    expected_payment_date = EXCLUDED.expected_payment_date,
                    expected_amount_per_share = EXCLUDED.expected_amount_per_share,
                    updated_at = CURRENT_TIMESTAMP
            """

            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (
                        ticker_id,
                        prediction['expected_ex_date'],
                        prediction['expected_payment_date'],
                        prediction['expected_amount_per_share'],
                        prediction['is_confirmed']
                    ))
                    conn.commit()

            return True

        except Exception as e:
            logger.error(f"Error storing prediction: {e}")
            return False

    def get_upcoming_dividends(
        self,
        days_ahead: int = 60,
        min_yield: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Get upcoming dividend payments.

        Args:
            days_ahead: How many days to look ahead
            min_yield: Minimum dividend yield filter (optional)

        Returns:
            List of upcoming dividend records
        """
        try:
            query = """
                SELECT
                    t.symbol,
                    t.company_name,
                    dc.expected_ex_date,
                    dc.expected_payment_date,
                    dc.expected_amount_per_share,
                    dc.is_confirmed,
                    dyc.dividend_yield_pct,
                    dyc.payout_frequency,
                    CASE
                        WHEN dc.expected_ex_date <= CURRENT_DATE + INTERVAL '7 days' THEN 'THIS_WEEK'
                        WHEN dc.expected_ex_date <= CURRENT_DATE + INTERVAL '30 days' THEN 'THIS_MONTH'
                        ELSE 'FUTURE'
                    END as timeframe
                FROM dividend_calendar dc
                JOIN tickers t ON dc.ticker_id = t.ticker_id
                LEFT JOIN dividend_yield_cache dyc ON dc.ticker_id = dyc.ticker_id
                WHERE dc.expected_ex_date >= CURRENT_DATE
                    AND dc.expected_ex_date <= CURRENT_DATE + INTERVAL '%s days'
            """

            params = [days_ahead]

            if min_yield is not None:
                query += " AND dyc.dividend_yield_pct >= %s"
                params.append(min_yield)

            query += " ORDER BY dc.expected_ex_date ASC"

            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, tuple(params))
                    rows = cur.fetchall()

            results = []
            for row in rows:
                results.append({
                    'symbol': row[0],
                    'company_name': row[1],
                    'ex_date': row[2],
                    'payment_date': row[3],
                    'amount_per_share': float(row[4]) if row[4] else None,
                    'is_confirmed': row[5],
                    'dividend_yield': float(row[6]) if row[6] else None,
                    'frequency': row[7],
                    'timeframe': row[8]
                })

            return results

        except Exception as e:
            logger.error(f"Error getting upcoming dividends: {e}")
            return []

    def get_dividends_for_portfolio(
        self,
        days_ahead: int = 90
    ) -> Dict[str, Any]:
        """
        Get upcoming dividends for portfolio holdings.

        Args:
            days_ahead: How many days to look ahead

        Returns:
            Dict with dividend summary for portfolio
        """
        try:
            query = """
                SELECT
                    t.symbol,
                    dc.expected_ex_date,
                    dc.expected_payment_date,
                    dc.expected_amount_per_share,
                    ph.shares,
                    (dc.expected_amount_per_share * ph.shares) as expected_payment
                FROM portfolio_holdings ph
                JOIN tickers t ON ph.ticker_id = t.ticker_id
                JOIN dividend_calendar dc ON ph.ticker_id = dc.ticker_id
                WHERE ph.is_open = TRUE
                    AND dc.expected_ex_date >= CURRENT_DATE
                    AND dc.expected_ex_date <= CURRENT_DATE + INTERVAL '%s days'
                ORDER BY dc.expected_payment_date ASC
            """

            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (days_ahead,))
                    rows = cur.fetchall()

            if not rows:
                return {
                    'total_expected': 0.0,
                    'payment_count': 0,
                    'payments': []
                }

            payments = []
            total = 0.0

            for row in rows:
                payment = {
                    'symbol': row[0],
                    'ex_date': row[1],
                    'payment_date': row[2],
                    'amount_per_share': float(row[3]),
                    'shares': float(row[4]),
                    'total_payment': float(row[5])
                }
                payments.append(payment)
                total += payment['total_payment']

            # Group by month
            by_month = defaultdict(list)
            for p in payments:
                month_key = p['payment_date'].strftime('%Y-%m')
                by_month[month_key].append(p)

            return {
                'total_expected': total,
                'payment_count': len(payments),
                'payments': payments,
                'by_month': dict(by_month),
                'annualized_estimate': total * (365 / days_ahead) if days_ahead > 0 else 0
            }

        except Exception as e:
            logger.error(f"Error getting portfolio dividends: {e}")
            return {
                'total_expected': 0.0,
                'payment_count': 0,
                'payments': []
            }

    def format_calendar(
        self,
        days_ahead: int = 60,
        min_yield: Optional[float] = None
    ) -> str:
        """
        Format upcoming dividends as a readable calendar.

        Args:
            days_ahead: How many days to look ahead
            min_yield: Minimum yield filter

        Returns:
            Formatted calendar string
        """
        dividends = self.get_upcoming_dividends(days_ahead, min_yield)

        if not dividends:
            return "No upcoming dividends found."

        output = []
        output.append("=" * 80)
        output.append(f"UPCOMING DIVIDEND CALENDAR (Next {days_ahead} Days)")
        output.append("=" * 80)
        output.append("")

        # Group by timeframe
        this_week = [d for d in dividends if d['timeframe'] == 'THIS_WEEK']
        this_month = [d for d in dividends if d['timeframe'] == 'THIS_MONTH']
        future = [d for d in dividends if d['timeframe'] == 'FUTURE']

        def format_section(title: str, items: List[Dict]):
            if not items:
                return

            output.append(f"{title}")
            output.append("-" * 80)

            for div in items:
                confirmed = "✓" if div['is_confirmed'] else "~"
                yield_str = f"{div['dividend_yield']:.2f}%" if div['dividend_yield'] else "N/A"

                output.append(
                    f"{confirmed} {div['symbol']:6} | "
                    f"Ex: {div['ex_date']} | "
                    f"Pay: {div['payment_date']} | "
                    f"${div['amount_per_share']:.4f} | "
                    f"Yield: {yield_str}"
                )

            output.append("")

        format_section("📅 THIS WEEK", this_week)
        format_section("📅 THIS MONTH", this_month)
        format_section("📅 FUTURE", future)

        output.append("=" * 80)
        output.append(f"Total: {len(dividends)} upcoming dividend payments")
        output.append("✓ = Confirmed | ~ = Estimated")
        output.append("=" * 80)

        return "\n".join(output)
