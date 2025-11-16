"""
Data Fetcher Module

Fetches and updates price data for watchlist tickers.
"""

import yfinance as yf
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
import logging

from tradingagents.database import DatabaseConnection, get_db_connection

logger = logging.getLogger(__name__)


class DataFetcher:
    """Fetches and manages price data for tickers."""

    def __init__(self, db: Optional[DatabaseConnection] = None):
        """
        Initialize data fetcher.

        Args:
            db: DatabaseConnection instance
        """
        self.db = db or get_db_connection()

    def fetch_latest_prices(
        self,
        symbol: str,
        days_back: int = 250
    ) -> Optional[pd.DataFrame]:
        """
        Fetch latest price data for a ticker.

        Args:
            symbol: Ticker symbol
            days_back: Number of days of history to fetch

        Returns:
            DataFrame with OHLCV data
        """
        try:
            ticker = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)

            # Download data
            df = ticker.history(start=start_date, end=end_date)

            if df.empty:
                logger.warning(f"No data returned for {symbol}")
                return None

            # Rename columns to match our schema
            df = df.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })

            # Reset index to get date as column
            df = df.reset_index()
            df = df.rename(columns={'Date': 'price_date'})

            # Select only needed columns
            df = df[['price_date', 'open', 'high', 'low', 'close', 'volume']]

            logger.info(f"Fetched {len(df)} days of data for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None

    def get_latest_price_date(self, ticker_id: int) -> Optional[date]:
        """
        Get the most recent price date for a ticker.

        Args:
            ticker_id: Ticker ID

        Returns:
            Most recent price date or None
        """
        query = """
            SELECT MAX(price_date) as latest_date
            FROM daily_prices
            WHERE ticker_id = %s
        """
        result = self.db.execute_dict_query(query, (ticker_id,), fetch_one=True)

        if result and result['latest_date']:
            return result['latest_date']
        return None

    def store_price_data(
        self,
        ticker_id: int,
        price_data: pd.DataFrame
    ) -> int:
        """
        Store price data in the database.

        Args:
            ticker_id: Ticker ID
            price_data: DataFrame with price data

        Returns:
            Number of rows inserted
        """
        if price_data is None or price_data.empty:
            return 0

        # Add ticker_id to each row
        price_data = price_data.copy()
        price_data['ticker_id'] = ticker_id

        # Convert DataFrame to list of dicts
        records = price_data.to_dict('records')

        # Insert using ON CONFLICT to avoid duplicates
        inserted = 0
        for record in records:
            try:
                query = """
                    INSERT INTO daily_prices (
                        ticker_id, price_date, open, high, low, close, volume
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (ticker_id, price_date) DO UPDATE
                    SET open = EXCLUDED.open,
                        high = EXCLUDED.high,
                        low = EXCLUDED.low,
                        close = EXCLUDED.close,
                        volume = EXCLUDED.volume
                """
                self.db.execute_query(
                    query,
                    (
                        record['ticker_id'],
                        record['price_date'],
                        float(record['open']),
                        float(record['high']),
                        float(record['low']),
                        float(record['close']),
                        int(record['volume'])
                    ),
                    fetch=False
                )
                inserted += 1
            except Exception as e:
                logger.error(f"Error inserting price data: {e}")
                continue

        logger.info(f"Stored {inserted} price records for ticker_id {ticker_id}")
        return inserted

    def update_ticker_prices(
        self,
        ticker_id: int,
        symbol: str,
        incremental: bool = True
    ) -> int:
        """
        Update prices for a single ticker.

        Args:
            ticker_id: Ticker ID
            symbol: Ticker symbol
            incremental: If True, only fetch new data

        Returns:
            Number of records added/updated
        """
        if incremental:
            # Get latest date in database
            latest_date = self.get_latest_price_date(ticker_id)

            if latest_date:
                # Fetch only new data (with 5-day overlap for safety)
                days_back = (datetime.now().date() - latest_date).days + 5
                days_back = max(days_back, 10)  # At least 10 days
            else:
                # No data yet, fetch full history
                days_back = 250
        else:
            # Full refresh
            days_back = 250

        # Fetch data
        price_data = self.fetch_latest_prices(symbol, days_back=days_back)

        if price_data is None:
            return 0

        # Store data
        return self.store_price_data(ticker_id, price_data)

    def update_all_tickers(
        self,
        ticker_list: List[Dict[str, Any]] = None,
        incremental: bool = True
    ) -> Dict[str, int]:
        """
        Update prices for all tickers in watchlist.

        Args:
            ticker_list: List of ticker dicts (if None, fetches from DB)
            incremental: If True, only fetch new data

        Returns:
            Dictionary with update statistics
        """
        # Get tickers from database if not provided
        if ticker_list is None:
            query = """
                SELECT ticker_id, symbol
                FROM tickers
                WHERE active = true
                ORDER BY symbol
            """
            ticker_list = self.db.execute_dict_query(query) or []

        stats = {
            'total': len(ticker_list),
            'successful': 0,
            'failed': 0,
            'records_added': 0
        }

        logger.info(f"Updating prices for {stats['total']} tickers...")

        for ticker in ticker_list:
            ticker_id = ticker['ticker_id']
            symbol = ticker['symbol']

            try:
                records = self.update_ticker_prices(ticker_id, symbol, incremental)

                if records > 0:
                    stats['successful'] += 1
                    stats['records_added'] += records
                    logger.info(f"  ✓ {symbol}: {records} records")
                else:
                    stats['failed'] += 1
                    logger.warning(f"  ⊙ {symbol}: No new data")

            except Exception as e:
                stats['failed'] += 1
                logger.error(f"  ✗ {symbol}: {e}")

        logger.info(f"Update complete: {stats['successful']}/{stats['total']} successful")
        return stats

    def get_latest_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get the latest quote for a ticker (real-time).

        Args:
            symbol: Ticker symbol

        Returns:
            Dictionary with current price, volume, etc.
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Get today's data
            today_data = ticker.history(period='1d')

            if today_data.empty:
                return None

            latest = today_data.iloc[-1]

            quote = {
                'symbol': symbol,
                'price': float(latest['Close']),
                'open': float(latest['Open']),
                'high': float(latest['High']),
                'low': float(latest['Low']),
                'volume': int(latest['Volume']),
                'timestamp': datetime.now(),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
            }

            return quote

        except Exception as e:
            logger.error(f"Error getting quote for {symbol}: {e}")
            return None

    def get_price_history(
        self,
        ticker_id: int,
        days: int = 250
    ) -> Optional[pd.DataFrame]:
        """
        Get price history from database.

        Args:
            ticker_id: Ticker ID
            days: Number of days to retrieve

        Returns:
            DataFrame with price history
        """
        query = """
            SELECT price_date, open, high, low, close, volume, ma_20, ma_50, ma_200, rsi_14
            FROM daily_prices
            WHERE ticker_id = %s
            ORDER BY price_date DESC
            LIMIT %s
        """

        with self.db.get_cursor() as cursor:
            cursor.execute(query, (ticker_id, days))
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()

            if not data:
                return None

            df = pd.DataFrame(data, columns=columns)
            # Reverse to get chronological order
            df = df.iloc[::-1].reset_index(drop=True)

            return df
