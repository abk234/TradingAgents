"""
Daily Scans Operations Module

Provides operations for storing and retrieving daily screening results.
"""

from typing import List, Dict, Any, Optional
from datetime import date, datetime
from decimal import Decimal
import logging
import json
import numpy as np

from .connection import get_db_connection, DatabaseConnection

logger = logging.getLogger(__name__)


def json_serializable(obj):
    """Convert numpy/pandas/decimal types to JSON-serializable types."""
    if isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [json_serializable(item) for item in obj]
    return obj


class ScanOperations:
    """Operations for managing daily scan results."""

    def __init__(self, db: Optional[DatabaseConnection] = None):
        """
        Initialize scan operations.

        Args:
            db: DatabaseConnection instance (creates one if not provided)
        """
        self.db = db or get_db_connection()

    def store_scan_result(
        self,
        ticker_id: int,
        scan_date: date,
        scan_data: Dict[str, Any]
    ) -> int:
        """
        Store a daily scan result.

        Args:
            ticker_id: Ticker ID
            scan_date: Date of the scan
            scan_data: Dictionary containing scan results

        Returns:
            scan_id of the stored result
        """
        # Make technical signals JSON-serializable
        technical_signals = json_serializable(scan_data.get('technical_signals', {}))

        data = {
            'ticker_id': ticker_id,
            'scan_date': scan_date,
            'price': scan_data.get('price'),
            'volume': scan_data.get('volume'),
            'priority_score': scan_data.get('priority_score'),
            'priority_rank': scan_data.get('priority_rank'),
            'technical_signals': json.dumps(technical_signals),
            'triggered_alerts': scan_data.get('triggered_alerts', []),
            'pe_ratio': scan_data.get('pe_ratio'),
            'forward_pe': scan_data.get('forward_pe'),
            'news_sentiment_score': scan_data.get('news_sentiment_score'),
            'scan_duration_seconds': scan_data.get('scan_duration_seconds')
        }

        # Use upsert to handle re-running scans on same day
        query = """
            INSERT INTO daily_scans (
                ticker_id, scan_date, price, volume, priority_score, priority_rank,
                technical_signals, triggered_alerts, pe_ratio, forward_pe,
                news_sentiment_score, scan_duration_seconds
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (ticker_id, scan_date) DO UPDATE
            SET price = EXCLUDED.price,
                volume = EXCLUDED.volume,
                priority_score = EXCLUDED.priority_score,
                priority_rank = EXCLUDED.priority_rank,
                technical_signals = EXCLUDED.technical_signals,
                triggered_alerts = EXCLUDED.triggered_alerts,
                pe_ratio = EXCLUDED.pe_ratio,
                forward_pe = EXCLUDED.forward_pe,
                news_sentiment_score = EXCLUDED.news_sentiment_score,
                scan_duration_seconds = EXCLUDED.scan_duration_seconds
            RETURNING scan_id
        """

        result = self.db.execute_query(
            query,
            (
                ticker_id,
                scan_date,
                data['price'],
                data['volume'],
                data['priority_score'],
                data['priority_rank'],
                data['technical_signals'],
                data['triggered_alerts'],
                data['pe_ratio'],
                data['forward_pe'],
                data['news_sentiment_score'],
                data['scan_duration_seconds']
            ),
            fetch_one=True
        )

        scan_id = result[0] if result else None
        logger.info(f"Stored scan result {scan_id} for ticker_id {ticker_id}")
        return scan_id

    def get_latest_scan(
        self,
        ticker_id: int = None,
        scan_date: date = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get the latest scan for a ticker or date.

        Args:
            ticker_id: Ticker ID (optional)
            scan_date: Scan date (optional, defaults to today)

        Returns:
            Scan result dictionary or None
        """
        if scan_date is None:
            scan_date = date.today()

        if ticker_id:
            query = """
                SELECT * FROM daily_scans
                WHERE ticker_id = %s AND scan_date = %s
            """
            return self.db.execute_dict_query(query, (ticker_id, scan_date), fetch_one=True)
        else:
            query = """
                SELECT * FROM daily_scans
                WHERE scan_date = %s
                ORDER BY priority_rank
            """
            return self.db.execute_dict_query(query, (scan_date,))

    def get_scan_results(
        self,
        scan_date: date = None
    ) -> List[Dict[str, Any]]:
        """
        Get all scan results for a date with ticker information.

        Args:
            scan_date: Scan date (defaults to today)

        Returns:
            List of all scan results with ticker info
        """
        if scan_date is None:
            scan_date = date.today()

        query = """
            SELECT
                ds.*,
                t.symbol,
                t.company_name,
                t.sector
            FROM daily_scans ds
            JOIN tickers t ON ds.ticker_id = t.ticker_id
            WHERE ds.scan_date = %s
            ORDER BY ds.priority_rank
        """

        return self.db.execute_dict_query(query, (scan_date,)) or []

    def get_top_opportunities(
        self,
        scan_date: date = None,
        limit: int = 5,
        filter_buy_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get top opportunities from a scan.

        Args:
            scan_date: Scan date (defaults to today)
            limit: Number of results to return
            filter_buy_only: If True, prioritize BUY recommendations

        Returns:
            List of top-ranked scan results with ticker info, dividend yield, and entry price
        """
        if scan_date is None:
            scan_date = date.today()

        # Base query with dividend yield
        # Use NULL instead of 0 to distinguish "no data" from "0% yield"
        query = """
            SELECT
                ds.*,
                t.symbol,
                t.company_name,
                t.sector,
                dyc.dividend_yield_pct,
                dyc.annual_dividend
            FROM daily_scans ds
            JOIN tickers t ON ds.ticker_id = t.ticker_id
            LEFT JOIN dividend_yield_cache dyc ON t.ticker_id = dyc.ticker_id
            WHERE ds.scan_date = %s
        """
        
        params = [scan_date]
        
        # If filtering for BUY only, we'll need to check recommendations
        # For now, order by priority_rank (we'll filter in Python after getting recommendations)
        query += " ORDER BY ds.priority_rank LIMIT %s"
        params.append(limit * 3 if filter_buy_only else limit)  # Get more to filter BUY recommendations

        results = self.db.execute_dict_query(query, tuple(params)) or []
        
        # If filtering for BUY, we need to check recommendations
        if filter_buy_only and results:
            # We'll filter after adding recommendations in the formatter
            # For now, just return results
            pass
        
        return results

    def get_scan_history(
        self,
        ticker_id: int,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get scan history for a ticker.

        Args:
            ticker_id: Ticker ID
            days: Number of days to retrieve

        Returns:
            List of scan results
        """
        query = """
            SELECT * FROM daily_scans
            WHERE ticker_id = %s
            ORDER BY scan_date DESC
            LIMIT %s
        """

        return self.db.execute_dict_query(query, (ticker_id, days)) or []

    def get_scan_summary(self, scan_date: date = None) -> Dict[str, Any]:
        """
        Get summary statistics for a scan.

        Args:
            scan_date: Scan date (defaults to today)

        Returns:
            Summary dictionary
        """
        if scan_date is None:
            scan_date = date.today()

        query = """
            SELECT
                COUNT(*) as total_scanned,
                AVG(priority_score) as avg_score,
                MAX(priority_score) as max_score,
                MIN(priority_score) as min_score
            FROM daily_scans
            WHERE scan_date = %s
        """

        result = self.db.execute_dict_query(query, (scan_date,), fetch_one=True)

        if result:
            # Get alert breakdown
            alert_query = """
                SELECT alert, COUNT(*) as count
                FROM (
                    SELECT UNNEST(triggered_alerts) as alert
                    FROM daily_scans
                    WHERE scan_date = %s
                ) AS alerts
                GROUP BY alert
                ORDER BY count DESC
            """
            alerts = self.db.execute_dict_query(alert_query, (scan_date,)) or []
            result['alert_breakdown'] = alerts
            result['total_alerts'] = len(alerts)

        return result or {}

    def update_rankings(self, scan_date: date = None):
        """
        Update priority rankings after all scans are complete.

        Args:
            scan_date: Scan date (defaults to today)
        """
        if scan_date is None:
            scan_date = date.today()

        # Update rankings based on priority_score
        query = """
            WITH ranked AS (
                SELECT
                    scan_id,
                    ROW_NUMBER() OVER (ORDER BY priority_score DESC) as rank
                FROM daily_scans
                WHERE scan_date = %s
            )
            UPDATE daily_scans ds
            SET priority_rank = ranked.rank
            FROM ranked
            WHERE ds.scan_id = ranked.scan_id
        """

        self.db.execute_query(query, (scan_date,), fetch=False)
        logger.info(f"Updated rankings for {scan_date}")
