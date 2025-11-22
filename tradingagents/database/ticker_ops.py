# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Ticker Operations Module

Provides CRUD operations for managing watchlist tickers.
"""

from typing import List, Dict, Any, Optional
from datetime import date, datetime
import logging

from .connection import get_db_connection, DatabaseConnection

logger = logging.getLogger(__name__)


class TickerOperations:
    """Operations for managing tickers in the watchlist."""

    def __init__(self, db: Optional[DatabaseConnection] = None):
        """
        Initialize ticker operations.

        Args:
            db: DatabaseConnection instance (creates one if not provided)
        """
        self.db = db or get_db_connection()

    def add_ticker(
        self,
        symbol: str,
        company_name: str = None,
        sector: str = None,
        industry: str = None,
        market_cap: int = None,
        priority_tier: int = 1,
        tags: List[str] = None,
        notes: str = None
    ) -> int:
        """
        Add a new ticker to the watchlist.

        Args:
            symbol: Ticker symbol (e.g., 'NVDA')
            company_name: Company name
            sector: Business sector
            industry: Industry classification
            market_cap: Market capitalization
            priority_tier: Priority level (1=high, 2=medium, 3=low)
            tags: List of tags for categorization
            notes: Additional notes

        Returns:
            ticker_id of the newly created ticker

        Raises:
            psycopg2.IntegrityError: If ticker symbol already exists
        """
        data = {
            'symbol': symbol.upper(),
            'company_name': company_name,
            'sector': sector,
            'industry': industry,
            'market_cap': market_cap,
            'priority_tier': priority_tier,
            'tags': tags,
            'notes': notes,
            'added_date': date.today()
        }

        ticker_id = self.db.insert('tickers', data, returning='ticker_id')
        logger.info(f"Added ticker {symbol} with ID {ticker_id}")
        return ticker_id

    def get_ticker(
        self,
        symbol: str = None,
        ticker_id: int = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get ticker information by symbol or ID.

        Args:
            symbol: Ticker symbol
            ticker_id: Ticker ID

        Returns:
            Ticker information as dictionary, or None if not found
        """
        if ticker_id:
            query = "SELECT * FROM tickers WHERE ticker_id = %s"
            params = (ticker_id,)
        elif symbol:
            query = "SELECT * FROM tickers WHERE symbol = %s"
            params = (symbol.upper(),)
        else:
            raise ValueError("Must provide either symbol or ticker_id")

        return self.db.execute_dict_query(query, params, fetch_one=True)

    def get_all_tickers(
        self,
        active_only: bool = True,
        priority_tier: int = None
    ) -> List[Dict[str, Any]]:
        """
        Get all tickers in the watchlist.

        Args:
            active_only: Only return active tickers
            priority_tier: Filter by priority tier

        Returns:
            List of ticker dictionaries
        """
        query = "SELECT * FROM tickers WHERE 1=1"
        params = []

        if active_only:
            query += " AND active = true"

        if priority_tier:
            query += " AND priority_tier = %s"
            params.append(priority_tier)

        query += " ORDER BY priority_tier, symbol"

        return self.db.execute_dict_query(query, tuple(params)) or []

    def update_ticker(
        self,
        symbol: str,
        **kwargs
    ) -> bool:
        """
        Update ticker information.

        Args:
            symbol: Ticker symbol to update
            **kwargs: Fields to update (company_name, sector, etc.)

        Returns:
            True if updated, False if not found
        """
        # Remove None values
        update_data = {k: v for k, v in kwargs.items() if v is not None}

        if not update_data:
            return False

        rows_updated = self.db.update(
            'tickers',
            update_data,
            {'symbol': symbol.upper()}
        )

        if rows_updated > 0:
            logger.info(f"Updated ticker {symbol}")
            return True
        return False

    def remove_ticker(
        self,
        symbol: str,
        soft_delete: bool = True
    ) -> bool:
        """
        Remove a ticker from the watchlist.

        Args:
            symbol: Ticker symbol to remove
            soft_delete: If True, mark as inactive; if False, delete from DB

        Returns:
            True if removed, False if not found
        """
        symbol = symbol.upper()

        if soft_delete:
            rows_updated = self.db.update(
                'tickers',
                {'active': False, 'removed_date': date.today()},
                {'symbol': symbol}
            )
            success = rows_updated > 0
        else:
            rows_deleted = self.db.delete('tickers', {'symbol': symbol})
            success = rows_deleted > 0

        if success:
            logger.info(f"Removed ticker {symbol} (soft_delete={soft_delete})")
        return success

    def get_ticker_id(self, symbol: str) -> Optional[int]:
        """
        Get ticker_id for a given symbol.

        Args:
            symbol: Ticker symbol

        Returns:
            ticker_id or None if not found
        """
        ticker = self.get_ticker(symbol=symbol)
        return ticker['ticker_id'] if ticker else None

    def get_or_create_ticker(
        self,
        symbol: str,
        company_name: str = None,
        sector: str = None,
        industry: str = None,
        **kwargs
    ) -> int:
        """
        Get existing ticker or create new one if it doesn't exist.

        This is a convenience method that combines get_ticker and add_ticker.

        Args:
            symbol: Ticker symbol (e.g., 'NVDA')
            company_name: Company name
            sector: Business sector
            industry: Industry classification
            **kwargs: Additional fields (market_cap, priority_tier, tags, notes)

        Returns:
            ticker_id

        Example:
            >>> ticker_ops = TickerOperations(db)
            >>> ticker_id = ticker_ops.get_or_create_ticker(
            ...     "AAPL",
            ...     company_name="Apple Inc.",
            ...     sector="Technology",
            ...     industry="Consumer Electronics"
            ... )
        """
        # Try to get existing ticker
        ticker = self.get_ticker(symbol=symbol)

        if ticker:
            # Ticker exists, return its ID
            return ticker['ticker_id']
        else:
            # Ticker doesn't exist, create it
            return self.add_ticker(
                symbol=symbol,
                company_name=company_name,
                sector=sector,
                industry=industry,
                **kwargs
            )

    def add_tags(self, symbol: str, tags: List[str]) -> bool:
        """
        Add tags to a ticker.

        Args:
            symbol: Ticker symbol
            tags: List of tags to add

        Returns:
            True if successful
        """
        ticker = self.get_ticker(symbol=symbol)
        if not ticker:
            return False

        existing_tags = ticker.get('tags') or []
        new_tags = list(set(existing_tags + tags))

        return self.update_ticker(symbol, tags=new_tags)

    def remove_tags(self, symbol: str, tags: List[str]) -> bool:
        """
        Remove tags from a ticker.

        Args:
            symbol: Ticker symbol
            tags: List of tags to remove

        Returns:
            True if successful
        """
        ticker = self.get_ticker(symbol=symbol)
        if not ticker:
            return False

        existing_tags = ticker.get('tags') or []
        new_tags = [tag for tag in existing_tags if tag not in tags]

        return self.update_ticker(symbol, tags=new_tags)

    def get_tickers_by_tag(self, tag: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get all tickers with a specific tag.

        Args:
            tag: Tag to search for
            active_only: Only return active tickers

        Returns:
            List of ticker dictionaries
        """
        query = "SELECT * FROM tickers WHERE %s = ANY(tags)"
        params = [tag]

        if active_only:
            query += " AND active = true"

        query += " ORDER BY symbol"

        return self.db.execute_dict_query(query, tuple(params)) or []

    def get_tickers_by_sector(self, sector: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get all tickers in a specific sector.

        Args:
            sector: Sector name
            active_only: Only return active tickers

        Returns:
            List of ticker dictionaries
        """
        query = "SELECT * FROM tickers WHERE sector = %s"
        params = [sector]

        if active_only:
            query += " AND active = true"

        query += " ORDER BY symbol"

        return self.db.execute_dict_query(query, tuple(params)) or []

    def bulk_add_tickers(self, tickers_data: List[Dict[str, Any]]) -> int:
        """
        Add multiple tickers at once.

        Args:
            tickers_data: List of ticker dictionaries

        Returns:
            Number of tickers added
        """
        # Ensure all symbols are uppercase and add added_date
        for ticker in tickers_data:
            ticker['symbol'] = ticker['symbol'].upper()
            ticker['added_date'] = ticker.get('added_date', date.today())

        count = self.db.bulk_insert('tickers', tickers_data)
        logger.info(f"Bulk added {count} tickers")
        return count

    def get_watchlist_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the watchlist.

        Returns:
            Dictionary with watchlist statistics
        """
        query = """
            SELECT
                COUNT(*) as total_tickers,
                SUM(CASE WHEN active THEN 1 ELSE 0 END) as active_tickers,
                SUM(CASE WHEN priority_tier = 1 THEN 1 ELSE 0 END) as high_priority,
                SUM(CASE WHEN priority_tier = 2 THEN 1 ELSE 0 END) as medium_priority,
                SUM(CASE WHEN priority_tier = 3 THEN 1 ELSE 0 END) as low_priority,
                COUNT(DISTINCT sector) as sectors_count
            FROM tickers
        """
        result = self.db.execute_dict_query(query, fetch_one=True)

        # Get sector breakdown
        sector_query = """
            SELECT sector, COUNT(*) as count
            FROM tickers
            WHERE active = true AND sector IS NOT NULL
            GROUP BY sector
            ORDER BY count DESC
        """
        sectors = self.db.execute_dict_query(sector_query) or []

        if result:
            result['sectors'] = sectors
            return result

        return {}
