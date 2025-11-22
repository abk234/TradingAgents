# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
System Operations Module

Provides system-level operations and statistics for the dashboard.
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import date, datetime, timedelta

from .connection import get_db_connection, DatabaseConnection

logger = logging.getLogger(__name__)


class SystemOperations:
    """Operations for system monitoring and statistics."""

    def __init__(self, db: Optional[DatabaseConnection] = None):
        """
        Initialize system operations.

        Args:
            db: DatabaseConnection instance (creates one if not provided)
        """
        self.db = db or get_db_connection()

    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the database content.

        Returns:
            Dictionary with counts and stats
        """
        stats = {}
        
        # Count tickers
        query_tickers = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN active THEN 1 ELSE 0 END) as active
            FROM tickers
        """
        ticker_res = self.db.execute_dict_query(query_tickers, fetch_one=True)
        if ticker_res:
            stats['tickers'] = ticker_res

        # Count scans
        query_scans = """
            SELECT 
                COUNT(*) as total,
                COUNT(DISTINCT scan_date) as days_scanned,
                MAX(scan_date) as last_scan_date
            FROM daily_scans
        """
        scan_res = self.db.execute_dict_query(query_scans, fetch_one=True)
        if scan_res:
            stats['scans'] = scan_res

        # Count analyses
        query_analyses = "SELECT COUNT(*) as total FROM analyses"
        analysis_res = self.db.execute_dict_query(query_analyses, fetch_one=True)
        if analysis_res:
            stats['analyses'] = analysis_res

        # Count buy signals
        query_signals = "SELECT COUNT(*) as total FROM buy_signals"
        signal_res = self.db.execute_dict_query(query_signals, fetch_one=True)
        if signal_res:
            stats['signals'] = signal_res
            
        return stats

    def get_missing_data_report(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Identify tickers with missing or outdated data.

        Returns:
            Dictionary with lists of tickers needing updates
        """
        report = {
            'missing_scans': [],
            'missing_analysis': [],
            'missing_fundamentals': []
        }
        
        # 1. Tickers with no scan in last 3 days (if active)
        query_scans = """
            SELECT t.ticker_id, t.symbol, t.company_name, MAX(ds.scan_date) as last_scan
            FROM tickers t
            LEFT JOIN daily_scans ds ON t.ticker_id = ds.ticker_id
            WHERE t.active = true
            GROUP BY t.ticker_id
            HAVING MAX(ds.scan_date) < CURRENT_DATE - INTERVAL '3 days' 
                OR MAX(ds.scan_date) IS NULL
            ORDER BY last_scan ASC NULLS FIRST
            LIMIT 20
        """
        report['missing_scans'] = self.db.execute_dict_query(query_scans) or []
        
        # 2. Active tickers with no analysis in last 30 days
        query_analysis = """
            SELECT t.ticker_id, t.symbol, t.company_name, MAX(a.analysis_date) as last_analysis
            FROM tickers t
            LEFT JOIN analyses a ON t.ticker_id = a.ticker_id
            WHERE t.active = true
            GROUP BY t.ticker_id
            HAVING MAX(a.analysis_date) < CURRENT_DATE - INTERVAL '30 days'
                OR MAX(a.analysis_date) IS NULL
            ORDER BY last_analysis ASC NULLS FIRST
            LIMIT 20
        """
        report['missing_analysis'] = self.db.execute_dict_query(query_analysis) or []
        
        return report

    def get_service_status(self) -> Dict[str, str]:
        """
        Check status of connected services (Database, Redis, etc.)
        
        Returns:
            Dictionary of service statuses
        """
        services = {
            'database': 'unknown',
            'redis': 'unknown',
            'pgvector': 'unknown'
        }
        
        # Check Database
        try:
            self.db.execute_query("SELECT 1", fetch_one=True)
            services['database'] = 'online'
        except Exception:
            services['database'] = 'offline'
            
        # Check Redis
        try:
            r = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=int(os.getenv('REDIS_PORT', 6379)), socket_connect_timeout=1)
            r.ping()
            services["redis"] = "online"
        except Exception:
            services["redis"] = "offline"

        # Check PGVector
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector'")
                if cursor.fetchone():
                    services["pgvector"] = "online"
                else:
                    services["pgvector"] = "not_installed"
        except Exception:
            services["pgvector"] = "error"
                
        return services

