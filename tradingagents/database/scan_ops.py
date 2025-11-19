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
    if obj is None:
        return None
    # Check for numpy integer types
    elif isinstance(obj, (np.integer, np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64)):
        return int(obj)
    # Check for numpy floating types (avoid np.float_ which was removed in NumPy 2.0)
    elif isinstance(obj, (np.floating, np.float16, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    # Check for numpy bool types (np.bool was removed in NumPy 2.0)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, Decimal):
        return float(obj)
    elif hasattr(obj, 'item'):  # Handle pandas scalar types
        return obj.item()
    elif isinstance(obj, dict):
        return {k: json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [json_serializable(item) for item in obj]
    elif isinstance(obj, (str, int, float, bool)):
        return obj
    # Fallback: try to convert to float if it's a numeric type
    try:
        return float(obj)
    except (ValueError, TypeError):
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

        # Convert all numeric fields to ensure they're not numpy types
        data = {
            'ticker_id': ticker_id,
            'scan_date': scan_date,
            'price': json_serializable(scan_data.get('price')),
            'volume': json_serializable(scan_data.get('volume')),
            'priority_score': json_serializable(scan_data.get('priority_score')),
            'priority_rank': json_serializable(scan_data.get('priority_rank')),
            'technical_signals': json.dumps(technical_signals),
            'triggered_alerts': scan_data.get('triggered_alerts', []),
            'pe_ratio': json_serializable(scan_data.get('pe_ratio')),
            'forward_pe': json_serializable(scan_data.get('forward_pe')),
            'news_sentiment_score': json_serializable(scan_data.get('news_sentiment_score')),
            'scan_duration_seconds': json_serializable(scan_data.get('scan_duration_seconds')),
            # Entry price tracking fields
            'entry_price_min': json_serializable(scan_data.get('entry_price_min')),
            'entry_price_max': json_serializable(scan_data.get('entry_price_max')),
            'entry_price_reasoning': scan_data.get('entry_price_reasoning'),  # String, no conversion needed
            'bb_upper': json_serializable(scan_data.get('bb_upper')),
            'bb_lower': json_serializable(scan_data.get('bb_lower')),
            'bb_middle': json_serializable(scan_data.get('bb_middle')),
            'support_level': json_serializable(scan_data.get('support_level')),
            'resistance_level': json_serializable(scan_data.get('resistance_level')),
            'enterprise_value': json_serializable(scan_data.get('enterprise_value')),
            'enterprise_to_ebitda': json_serializable(scan_data.get('enterprise_to_ebitda')),
            'market_cap': json_serializable(scan_data.get('market_cap')),
            'entry_timing': scan_data.get('entry_timing'),  # String, no conversion needed
            'recommendation': scan_data.get('recommendation')  # Store recommendation for sector analysis
        }

        # Use upsert to handle re-running scans on same day
        query = """
            INSERT INTO daily_scans (
                ticker_id, scan_date, price, volume, priority_score, priority_rank,
                technical_signals, triggered_alerts, pe_ratio, forward_pe,
                news_sentiment_score, scan_duration_seconds,
                entry_price_min, entry_price_max, entry_price_reasoning,
                bb_upper, bb_lower, bb_middle,
                support_level, resistance_level,
                enterprise_value, enterprise_to_ebitda, market_cap,
                entry_timing, recommendation
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                scan_duration_seconds = EXCLUDED.scan_duration_seconds,
                entry_price_min = EXCLUDED.entry_price_min,
                entry_price_max = EXCLUDED.entry_price_max,
                entry_price_reasoning = EXCLUDED.entry_price_reasoning,
                bb_upper = EXCLUDED.bb_upper,
                bb_lower = EXCLUDED.bb_lower,
                bb_middle = EXCLUDED.bb_middle,
                support_level = EXCLUDED.support_level,
                resistance_level = EXCLUDED.resistance_level,
                enterprise_value = EXCLUDED.enterprise_value,
                enterprise_to_ebitda = EXCLUDED.enterprise_to_ebitda,
                market_cap = EXCLUDED.market_cap,
                entry_timing = EXCLUDED.entry_timing,
                recommendation = EXCLUDED.recommendation
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
                data['scan_duration_seconds'],
                data['entry_price_min'],
                data['entry_price_max'],
                data['entry_price_reasoning'],
                data['bb_upper'],
                data['bb_lower'],
                data['bb_middle'],
                data['support_level'],
                data['resistance_level'],
                data['enterprise_value'],
                data['enterprise_to_ebitda'],
                data['market_cap'],
                data['entry_timing'],
                data['recommendation']
            ),
            fetch_one=True
        )

        scan_id = result[0] if result else None
        logger.info(f"Stored scan result {scan_id} for ticker_id {ticker_id} with entry price: {data.get('entry_price_min')}-{data.get('entry_price_max')}")
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

    def create_entry_price_outcome(
        self,
        scan_id: int,
        ticker_id: int,
        scan_date: date,
        entry_price_min: Decimal,
        entry_price_max: Decimal,
        recommended_timing: str = None
    ) -> int:
        """
        Create an entry price outcome record for tracking.

        Args:
            scan_id: Scan ID this outcome tracks
            ticker_id: Ticker ID
            scan_date: Date of the original scan
            entry_price_min: Minimum recommended entry price
            entry_price_max: Maximum recommended entry price
            recommended_timing: Entry timing recommendation

        Returns:
            outcome_id of the created record
        """
        query = """
            INSERT INTO entry_price_outcomes (
                scan_id, ticker_id, scan_date,
                entry_price_min, entry_price_max,
                recommended_timing, outcome_status
            ) VALUES (%s, %s, %s, %s, %s, %s, 'STILL_WAITING')
            ON CONFLICT (scan_id) DO NOTHING
            RETURNING outcome_id
        """

        result = self.db.execute_query(
            query,
            (scan_id, ticker_id, scan_date, entry_price_min, entry_price_max, recommended_timing),
            fetch_one=True
        )

        outcome_id = result[0] if result else None
        if outcome_id:
            logger.info(f"Created entry price outcome {outcome_id} for scan {scan_id}")
        return outcome_id

    def update_entry_outcomes(self):
        """
        Update all entry price outcomes based on actual price movements.
        Calls the database function that checks if entry targets were hit.
        """
        query = "SELECT update_entry_price_outcomes()"
        self.db.execute_query(query, fetch=False)
        logger.info("Updated entry price outcomes")

    def get_entry_price_trends(
        self,
        ticker_id: int = None,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get entry price trends over time.

        Args:
            ticker_id: Ticker ID (optional, if None returns all tickers)
            days: Number of days to retrieve

        Returns:
            List of entry price history records
        """
        if ticker_id:
            query = """
                SELECT * FROM entry_price_history
                WHERE symbol = (SELECT symbol FROM tickers WHERE ticker_id = %s)
                    AND scan_date >= CURRENT_DATE - INTERVAL '%s days'
                ORDER BY scan_date DESC
            """
            return self.db.execute_dict_query(query, (ticker_id, days)) or []
        else:
            query = """
                SELECT * FROM entry_price_history
                WHERE scan_date >= CURRENT_DATE - INTERVAL '%s days'
                ORDER BY scan_date DESC, priority_score DESC
                LIMIT 100
            """
            return self.db.execute_dict_query(query, (days,)) or []
