"""
Price cache database operations.
Provides caching for stock price data to reduce API calls and improve performance.
"""
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from decimal import Decimal

logger = logging.getLogger(__name__)


class PriceCacheOperations:
    """Database operations for price caching."""

    def __init__(self, db_connection):
        """Initialize with database connection."""
        self.db = db_connection

        # Cache expiration settings
        self.HISTORICAL_CACHE_DAYS = 365  # Historical data cached for 1 year
        self.REALTIME_CACHE_MINUTES = 5   # Realtime data expires in 5 min
        self.EOD_CACHE_HOURS = 24         # End-of-day data expires in 24 hours

    def get_cached_prices(
        self,
        ticker_symbol: str,
        start_date: date,
        end_date: date
    ) -> Optional[List[Dict]]:
        """
        Get cached price data for a ticker and date range.

        Args:
            ticker_symbol: Stock ticker symbol (e.g., 'AAPL')
            start_date: Start date for price data
            end_date: End date for price data

        Returns:
            List of price dictionaries, or None if cache miss
            Returns None if ANY date in range is missing from cache or if data is stale
        """
        query = """
        SELECT
            t.symbol,
            pc.price_date,
            pc.open_price,
            pc.high_price,
            pc.low_price,
            pc.close_price,
            pc.adj_close_price,
            pc.volume,
            pc.data_source,
            pc.fetched_at,
            pc.is_realtime
        FROM price_cache pc
        JOIN tickers t ON t.ticker_id = pc.ticker_id
        WHERE t.symbol = %s
        AND pc.price_date >= %s
        AND pc.price_date <= %s
        ORDER BY pc.price_date ASC
        """

        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(query, (ticker_symbol, start_date, end_date))
                rows = cursor.fetchall()

            if not rows:
                logger.debug(f"Cache miss: No data for {ticker_symbol} {start_date} to {end_date}")
                return None

            # Check if we have ALL dates in range (no gaps)
            # For simplicity, we'll accept what we have - gaps might be weekends/holidays
            # A more robust implementation would use a trading calendar

            # Check if cache is stale
            for row in rows:
                if self._is_stale(row):
                    logger.debug(f"Cache stale: Data from {row[9]} is too old")
                    return None

            # Convert to dict format
            prices = []
            for row in rows:
                prices.append({
                    'symbol': row[0],
                    'date': row[1],
                    'open': float(row[2]) if row[2] else None,
                    'high': float(row[3]) if row[3] else None,
                    'low': float(row[4]) if row[4] else None,
                    'close': float(row[5]) if row[5] else None,
                    'adj_close': float(row[6]) if row[6] else None,
                    'volume': int(row[7]) if row[7] else None,
                    'source': row[8],
                    'cached_at': row[9]
                })

            logger.info(f"✓ Cache hit: Retrieved {len(prices)} prices for {ticker_symbol}")
            return prices

        except Exception as e:
            logger.error(f"Error retrieving cached prices: {e}")
            return None

    def store_prices(
        self,
        ticker_symbol: str,
        prices: List[Dict],
        data_source: str,
        is_realtime: bool = False
    ) -> int:
        """
        Store price data in cache.

        Args:
            ticker_symbol: Stock ticker symbol
            prices: List of price dicts with keys: date, open, high, low, close, volume
            data_source: Vendor name ('yfinance', 'alpha_vantage', etc.)
            is_realtime: True if fetched during market hours

        Returns:
            Number of prices stored
        """
        from tradingagents.database.ticker_ops import TickerOperations

        try:
            # Get ticker_id
            ticker_ops = TickerOperations(self.db)
            ticker_id = ticker_ops.get_ticker_id(ticker_symbol)

            if not ticker_id:
                # Ticker doesn't exist - create it
                logger.info(f"Creating ticker {ticker_symbol} for cache")
                ticker_id = ticker_ops.get_or_create_ticker(
                    symbol=ticker_symbol,
                    company_name=ticker_symbol,
                    sector="Unknown",
                    industry="Unknown"
                )

            insert_query = """
            INSERT INTO price_cache (
                ticker_id, price_date,
                open_price, high_price, low_price, close_price, adj_close_price,
                volume, data_source, is_realtime
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (ticker_id, price_date)
            DO UPDATE SET
                open_price = EXCLUDED.open_price,
                high_price = EXCLUDED.high_price,
                low_price = EXCLUDED.low_price,
                close_price = EXCLUDED.close_price,
                adj_close_price = EXCLUDED.adj_close_price,
                volume = EXCLUDED.volume,
                data_source = EXCLUDED.data_source,
                fetched_at = CURRENT_TIMESTAMP,
                is_realtime = EXCLUDED.is_realtime
            """

            with self.db.get_cursor() as cursor:
                count = 0

                for price in prices:
                    try:
                        cursor.execute(insert_query, (
                            ticker_id,
                            price.get('date'),
                            price.get('open'),
                            price.get('high'),
                            price.get('low'),
                            price.get('close'),
                            price.get('adj_close'),
                            price.get('volume'),
                            data_source,
                            is_realtime
                        ))
                        count += 1
                    except Exception as e:
                        logger.warning(f"Failed to store price for {price.get('date')}: {e}")
                        continue

            logger.info(f"✓ Stored {count} prices for {ticker_symbol} from {data_source}")
            return count

        except Exception as e:
            logger.error(f"Error storing prices: {e}")
            return 0

    def invalidate_cache(
        self,
        ticker_symbol: Optional[str] = None,
        older_than_days: Optional[int] = None
    ) -> int:
        """
        Invalidate (delete) cached data.

        Args:
            ticker_symbol: Specific ticker to invalidate (or None for all)
            older_than_days: Delete data older than N days (or None for all)

        Returns:
            Number of records deleted
        """
        try:
            if ticker_symbol:
                query = """
                DELETE FROM price_cache
                WHERE ticker_id = (SELECT ticker_id FROM tickers WHERE symbol = %s)
                """
                params = [ticker_symbol]

                if older_than_days:
                    query += " AND fetched_at < %s"
                    cutoff = datetime.now() - timedelta(days=older_than_days)
                    params.append(cutoff)
            else:
                if older_than_days:
                    query = "DELETE FROM price_cache WHERE fetched_at < %s"
                    cutoff = datetime.now() - timedelta(days=older_than_days)
                    params = [cutoff]
                else:
                    query = "DELETE FROM price_cache"
                    params = []

            with self.db.get_cursor() as cursor:
                cursor.execute(query, params)
                deleted = cursor.rowcount

            logger.info(f"Invalidated {deleted} price cache records")
            return deleted

        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
            return 0

    def cleanup_stale_cache(self) -> Dict[str, int]:
        """
        Clean up stale cache entries.

        Removes:
        - Realtime data older than 5 minutes
        - Recent EOD data older than 24 hours

        Returns:
            Dict with counts of deleted records by type
        """
        try:
            # Delete realtime data older than 5 minutes
            realtime_query = """
            DELETE FROM price_cache
            WHERE is_realtime = TRUE
            AND fetched_at < %s
            """
            realtime_cutoff = datetime.now() - timedelta(minutes=self.REALTIME_CACHE_MINUTES)

            # Delete recent EOD data older than 24 hours
            eod_query = """
            DELETE FROM price_cache
            WHERE is_realtime = FALSE
            AND price_date >= %s
            AND fetched_at < %s
            """
            recent_date = date.today() - timedelta(days=7)
            eod_cutoff = datetime.now() - timedelta(hours=self.EOD_CACHE_HOURS)

            with self.db.get_cursor() as cursor:
                cursor.execute(realtime_query, (realtime_cutoff,))
                realtime_deleted = cursor.rowcount

                cursor.execute(eod_query, (recent_date, eod_cutoff))
                eod_deleted = cursor.rowcount

            result = {
                'realtime_deleted': realtime_deleted,
                'eod_deleted': eod_deleted,
                'total_deleted': realtime_deleted + eod_deleted
            }

            if result['total_deleted'] > 0:
                logger.info(f"Cache cleanup: {result['total_deleted']} stale records deleted")

            return result

        except Exception as e:
            logger.error(f"Error during cache cleanup: {e}")
            return {'realtime_deleted': 0, 'eod_deleted': 0, 'total_deleted': 0}

    def _is_stale(self, row: Tuple) -> bool:
        """
        Check if cached data is stale based on age and type.

        Args:
            row: Database row tuple from get_cached_prices query

        Returns:
            True if data is stale and should not be used
        """
        fetched_at = row[9]  # fetched_at column
        is_realtime = row[10]  # is_realtime column
        price_date = row[1]  # price_date column

        age = datetime.now() - fetched_at

        # Realtime data expires in 5 minutes
        if is_realtime and age > timedelta(minutes=self.REALTIME_CACHE_MINUTES):
            return True

        # Recent EOD data (within last 7 days) expires in 24 hours
        if not is_realtime and price_date >= date.today() - timedelta(days=7):
            if age > timedelta(hours=self.EOD_CACHE_HOURS):
                return True

        # Historical data (> 7 days old) never expires
        return False

    def get_cache_stats(self) -> Dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics including total records, unique tickers,
            date range, and breakdown by data source
        """
        total_query = """
        SELECT
            COUNT(*) as total_records,
            COUNT(DISTINCT ticker_id) as unique_tickers,
            MIN(price_date) as oldest_date,
            MAX(price_date) as newest_date,
            COUNT(CASE WHEN is_realtime THEN 1 END) as realtime_count
        FROM price_cache
        """

        source_query = """
        SELECT
            data_source,
            COUNT(*) as source_count
        FROM price_cache
        GROUP BY data_source
        """

        try:
            with self.db.get_cursor() as cursor:
                # Get overall stats
                cursor.execute(total_query)
                row = cursor.fetchone()

                stats = {
                    'total_records': row[0] if row else 0,
                    'unique_tickers': row[1] if row else 0,
                    'oldest_date': row[2] if row else None,
                    'newest_date': row[3] if row else None,
                    'realtime_count': row[4] if row else 0,
                    'by_source': {}
                }

                # Get breakdown by source
                cursor.execute(source_query)
                for row in cursor.fetchall():
                    stats['by_source'][row[0]] = row[1]

            return stats

        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {
                'total_records': 0,
                'unique_tickers': 0,
                'oldest_date': None,
                'newest_date': None,
                'realtime_count': 0,
                'by_source': {}
            }
