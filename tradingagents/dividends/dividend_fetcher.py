"""
Dividend data fetcher using yfinance API.

Fetches historical dividend data and stores it in the database.
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import psycopg2
from psycopg2.extras import execute_values
import logging

from tradingagents.database import DatabaseConnection

logger = logging.getLogger(__name__)


def get_ticker_id(db_conn: DatabaseConnection, symbol: str) -> Optional[int]:
    """
    Get ticker_id for a symbol.

    Args:
        db_conn: Database connection
        symbol: Stock symbol

    Returns:
        ticker_id or None if not found
    """
    try:
        query = "SELECT ticker_id FROM tickers WHERE symbol = %s"
        with db_conn.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (symbol,))
                result = cur.fetchone()
                return result[0] if result else None
    except Exception as e:
        logger.error(f"Error getting ticker_id for {symbol}: {e}")
        return None


class DividendFetcher:
    """Fetches dividend data from yfinance and stores in database."""

    def __init__(self, db_conn: Optional[DatabaseConnection] = None):
        """
        Initialize dividend fetcher.

        Args:
            db_conn: Database connection (creates new if not provided)
        """
        self.db = db_conn or DatabaseConnection()

    def fetch_dividend_history(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch dividend history for a symbol from yfinance.

        Args:
            symbol: Stock symbol
            start_date: Start date (defaults to 5 years ago)
            end_date: End date (defaults to today)

        Returns:
            List of dividend records
        """
        try:
            # Default to 5 years of history
            if start_date is None:
                start_date = datetime.now() - timedelta(days=5*365)
            if end_date is None:
                end_date = datetime.now()

            # Fetch from yfinance
            ticker = yf.Ticker(symbol)
            dividends = ticker.dividends

            if dividends is None or len(dividends) == 0:
                logger.info(f"No dividend history found for {symbol}")
                return []

            # Convert to list of dicts
            dividend_records = []
            for date, amount in dividends.items():
                # Convert to date for comparison (removes timezone info)
                date_only = date.date() if hasattr(date, 'date') else date
                start_date_only = start_date.date() if hasattr(start_date, 'date') else start_date
                end_date_only = end_date.date() if hasattr(end_date, 'date') else end_date

                if start_date_only <= date_only <= end_date_only:
                    dividend_records.append({
                        'date': date_only,
                        'amount': float(amount),
                        'symbol': symbol
                    })

            logger.info(f"Fetched {len(dividend_records)} dividend records for {symbol}")
            return dividend_records

        except Exception as e:
            logger.error(f"Error fetching dividends for {symbol}: {e}")
            return []

    def store_dividend_history(
        self,
        symbol: str,
        dividends: List[Dict[str, Any]],
        dividend_type: str = 'REGULAR'
    ) -> int:
        """
        Store dividend history in database.

        Args:
            symbol: Stock symbol
            dividends: List of dividend records
            dividend_type: Type of dividend (REGULAR, SPECIAL, etc.)

        Returns:
            Number of records inserted
        """
        if not dividends:
            return 0

        try:
            # Get ticker_id
            ticker_id = get_ticker_id(self.db, symbol)
            if ticker_id is None:
                logger.error(f"Ticker {symbol} not found in database")
                return 0

            # Prepare data for insertion
            records = []
            for div in dividends:
                # Estimate payment date (typically 2-4 weeks after ex-date)
                ex_date = div['date']
                payment_date = ex_date + timedelta(days=21)  # Estimate

                records.append((
                    ticker_id,
                    ex_date,
                    payment_date,
                    ex_date,  # record_date (estimate)
                    div['amount'],
                    dividend_type,
                    'PAID'  # status
                ))

            # Insert with ON CONFLICT DO UPDATE
            query = """
                INSERT INTO dividend_payments (
                    ticker_id,
                    ex_dividend_date,
                    payment_date,
                    record_date,
                    dividend_per_share,
                    dividend_type,
                    status
                )
                VALUES %s
                ON CONFLICT (ticker_id, ex_dividend_date)
                DO UPDATE SET
                    payment_date = EXCLUDED.payment_date,
                    dividend_per_share = EXCLUDED.dividend_per_share,
                    dividend_type = EXCLUDED.dividend_type,
                    status = EXCLUDED.status,
                    updated_at = CURRENT_TIMESTAMP
            """

            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    execute_values(cur, query, records)
                    conn.commit()
                    inserted_count = len(records)

            logger.info(f"Stored {inserted_count} dividend records for {symbol}")
            return inserted_count

        except Exception as e:
            logger.error(f"Error storing dividends for {symbol}: {e}")
            return 0

    def fetch_and_store(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """
        Fetch and store dividend history in one operation.

        Args:
            symbol: Stock symbol
            start_date: Start date
            end_date: End date

        Returns:
            Number of records stored
        """
        dividends = self.fetch_dividend_history(symbol, start_date, end_date)
        return self.store_dividend_history(symbol, dividends)

    def backfill_all_tickers(
        self,
        years_back: int = 5,
        active_only: bool = True
    ) -> Dict[str, int]:
        """
        Backfill dividend history for all tickers in database.

        Args:
            years_back: How many years of history to fetch
            active_only: Only process active tickers

        Returns:
            Dict mapping symbol to number of records stored
        """
        start_date = datetime.now() - timedelta(days=years_back*365)

        # Get all tickers
        query = """
            SELECT ticker_id, symbol
            FROM tickers
            WHERE active = TRUE
            ORDER BY symbol
        """ if active_only else """
            SELECT ticker_id, symbol
            FROM tickers
            ORDER BY symbol
        """

        results = {}

        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                tickers = cur.fetchall()

        logger.info(f"Backfilling dividends for {len(tickers)} tickers...")

        for ticker_id, symbol in tickers:
            try:
                count = self.fetch_and_store(symbol, start_date)
                results[symbol] = count

                if count > 0:
                    print(f"✓ {symbol}: {count} dividends")
                else:
                    print(f"- {symbol}: No dividends")

            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                results[symbol] = 0
                print(f"✗ {symbol}: Error")

        total = sum(results.values())
        logger.info(f"Backfill complete: {total} total dividend records")

        return results

    def calculate_dividend_metrics(
        self,
        symbol: str,
        current_price: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate dividend metrics for a symbol.

        Args:
            symbol: Stock symbol
            current_price: Current stock price (fetches if not provided)

        Returns:
            Dict with dividend metrics or None if no dividends
        """
        try:
            ticker_id = get_ticker_id(self.db, symbol)
            if ticker_id is None:
                return None

            # Get dividend history from database
            query = """
                SELECT
                    ex_dividend_date,
                    dividend_per_share,
                    payment_date
                FROM dividend_payments
                WHERE ticker_id = %s
                    AND ex_dividend_date >= CURRENT_DATE - INTERVAL '5 years'
                ORDER BY ex_dividend_date DESC
            """

            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (ticker_id,))
                    dividends = cur.fetchall()

            if not dividends:
                return None

            # Calculate metrics
            recent_dividends = [float(d[1]) for d in dividends[:4]]  # Last 4 dividends
            annual_dividend = sum(recent_dividends)

            # Get current price if not provided
            if current_price is None:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                current_price = info.get('currentPrice') or info.get('regularMarketPrice')

            if current_price is None or current_price <= 0:
                logger.warning(f"Could not get valid price for {symbol}")
                return None

            # Calculate yield
            dividend_yield = (annual_dividend / current_price) * 100

            # Determine frequency
            if len(dividends) >= 4:
                # Calculate average days between dividends
                dates = [d[0] for d in dividends[:4]]
                intervals = [(dates[i] - dates[i+1]).days for i in range(len(dates)-1)]
                avg_interval = sum(intervals) / len(intervals) if intervals else 0

                if avg_interval < 45:
                    frequency = 'MONTHLY'
                elif avg_interval < 120:
                    frequency = 'QUARTERLY'
                elif avg_interval < 210:
                    frequency = 'SEMI_ANNUAL'
                else:
                    frequency = 'ANNUAL'
            else:
                frequency = 'UNKNOWN'

            # Calculate growth rates
            growth_1yr = self._calculate_dividend_growth(dividends, 1)
            growth_3yr = self._calculate_dividend_growth(dividends, 3)
            growth_5yr = self._calculate_dividend_growth(dividends, 5)

            # Count consecutive years with dividends
            consecutive_years = self._count_consecutive_years(dividends)

            return {
                'symbol': symbol,
                'current_price': current_price,
                'annual_dividend': annual_dividend,
                'dividend_yield_pct': dividend_yield,
                'frequency': frequency,
                'last_dividend_amount': dividends[0][1] if dividends else None,
                'last_ex_date': dividends[0][0] if dividends else None,
                'dividend_growth_1yr_pct': growth_1yr,
                'dividend_growth_3yr_pct': growth_3yr,
                'dividend_growth_5yr_pct': growth_5yr,
                'consecutive_years_paid': consecutive_years,
                'total_dividends_count': len(dividends)
            }

        except Exception as e:
            logger.error(f"Error calculating dividend metrics for {symbol}: {e}")
            return None

    def _calculate_dividend_growth(
        self,
        dividends: List[tuple],
        years: int
    ) -> Optional[float]:
        """Calculate annualized dividend growth rate."""
        try:
            cutoff_date = datetime.now().date() - timedelta(days=years*365)
            recent = [float(d[1]) for d in dividends if d[0] > cutoff_date]
            old = [float(d[1]) for d in dividends if d[0] <= cutoff_date][:4]

            if not recent or not old:
                return None

            recent_annual = sum(recent[:4])
            old_annual = sum(old)

            if old_annual <= 0:
                return None

            growth = ((recent_annual / old_annual) ** (1 / years) - 1) * 100
            return round(growth, 2)

        except Exception:
            return None

    def _count_consecutive_years(self, dividends: List[tuple]) -> int:
        """Count consecutive years with dividend payments."""
        if not dividends:
            return 0

        years_with_dividends = set(d[0].year for d in dividends)
        current_year = datetime.now().year

        consecutive = 0
        year = current_year

        while year in years_with_dividends:
            consecutive += 1
            year -= 1

            if year < min(years_with_dividends) - 1:
                break

        return consecutive

    def update_yield_cache(
        self,
        symbol: str,
        cache_hours: int = 24
    ) -> bool:
        """
        Update dividend yield cache for a symbol.

        Args:
            symbol: Stock symbol
            cache_hours: How long cache should be valid

        Returns:
            True if successful
        """
        try:
            ticker_id = get_ticker_id(self.db, symbol)
            if ticker_id is None:
                return False

            # Calculate metrics
            metrics = self.calculate_dividend_metrics(symbol)
            if metrics is None:
                logger.warning(f"No dividend metrics for {symbol}")
                return False

            # Store in cache
            query = """
                INSERT INTO dividend_yield_cache (
                    ticker_id,
                    current_price,
                    annual_dividend,
                    dividend_yield_pct,
                    payout_frequency,
                    last_dividend_amount,
                    last_ex_date,
                    dividend_growth_1yr_pct,
                    dividend_growth_3yr_pct,
                    dividend_growth_5yr_pct,
                    consecutive_years_paid,
                    calculated_at,
                    valid_until
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP + INTERVAL '%s hours'
                )
                ON CONFLICT (ticker_id)
                DO UPDATE SET
                    current_price = EXCLUDED.current_price,
                    annual_dividend = EXCLUDED.annual_dividend,
                    dividend_yield_pct = EXCLUDED.dividend_yield_pct,
                    payout_frequency = EXCLUDED.payout_frequency,
                    last_dividend_amount = EXCLUDED.last_dividend_amount,
                    last_ex_date = EXCLUDED.last_ex_date,
                    dividend_growth_1yr_pct = EXCLUDED.dividend_growth_1yr_pct,
                    dividend_growth_3yr_pct = EXCLUDED.dividend_growth_3yr_pct,
                    dividend_growth_5yr_pct = EXCLUDED.dividend_growth_5yr_pct,
                    consecutive_years_paid = EXCLUDED.consecutive_years_paid,
                    calculated_at = CURRENT_TIMESTAMP,
                    valid_until = CURRENT_TIMESTAMP + INTERVAL '%s hours'
            """

            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (
                        ticker_id,
                        metrics['current_price'],
                        metrics['annual_dividend'],
                        metrics['dividend_yield_pct'],
                        metrics['frequency'],
                        metrics['last_dividend_amount'],
                        metrics['last_ex_date'],
                        metrics['dividend_growth_1yr_pct'],
                        metrics['dividend_growth_3yr_pct'],
                        metrics['dividend_growth_5yr_pct'],
                        metrics['consecutive_years_paid'],
                        cache_hours,
                        cache_hours
                    ))
                    conn.commit()

            logger.info(f"Updated yield cache for {symbol}: {metrics['dividend_yield_pct']:.2f}%")
            return True

        except Exception as e:
            logger.error(f"Error updating yield cache for {symbol}: {e}")
            return False
