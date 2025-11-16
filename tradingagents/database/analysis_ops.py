"""
Analysis Operations Module

Provides operations for storing and retrieving analysis results.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import json

from .connection import get_db_connection, DatabaseConnection

logger = logging.getLogger(__name__)


class AnalysisOperations:
    """Operations for managing analysis results and buy signals."""

    def __init__(self, db: Optional[DatabaseConnection] = None):
        """
        Initialize analysis operations.

        Args:
            db: DatabaseConnection instance (creates one if not provided)
        """
        self.db = db or get_db_connection()

    def store_analysis(
        self,
        ticker_id: int,
        analysis_data: Dict[str, Any],
        embedding: List[float] = None
    ) -> int:
        """
        Store a deep analysis result.

        Args:
            ticker_id: ID of the ticker analyzed
            analysis_data: Dictionary containing analysis results
            embedding: Vector embedding for RAG (768-dim array)

        Returns:
            analysis_id of the stored analysis
        """
        data = {
            'ticker_id': ticker_id,
            'analysis_date': datetime.now(),
            'price_at_analysis': analysis_data.get('price'),
            'volume_at_analysis': analysis_data.get('volume'),
            'full_report': json.dumps(analysis_data.get('full_report', {})),
            'executive_summary': analysis_data.get('executive_summary'),
            'final_decision': analysis_data.get('final_decision'),
            'confidence_score': analysis_data.get('confidence_score'),
            'fundamental_gate_passed': analysis_data.get('fundamental_gate_passed'),
            'technical_gate_passed': analysis_data.get('technical_gate_passed'),
            'risk_gate_passed': analysis_data.get('risk_gate_passed'),
            'timing_score': analysis_data.get('timing_score'),
            'key_catalysts': analysis_data.get('key_catalysts'),
            'risk_factors': analysis_data.get('risk_factors'),
            'bull_case': analysis_data.get('bull_case'),
            'bear_case': analysis_data.get('bear_case'),
            'entry_price_target': analysis_data.get('entry_price_target'),
            'stop_loss_price': analysis_data.get('stop_loss_price'),
            'position_size_pct': analysis_data.get('position_size_pct'),
            'expected_return_pct': analysis_data.get('expected_return_pct'),
            'expected_holding_period_days': analysis_data.get('expected_holding_period_days'),
            'llm_model_used': analysis_data.get('llm_model_used'),
            'embedding': embedding
        }

        analysis_id = self.db.insert('analyses', data, returning='analysis_id')
        logger.info(f"Stored analysis {analysis_id} for ticker_id {ticker_id}")
        return analysis_id

    def get_analyses_for_ticker(
        self,
        ticker_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent analyses for a ticker.

        Args:
            ticker_id: Ticker ID
            limit: Maximum number of results

        Returns:
            List of analysis dictionaries
        """
        query = """
            SELECT * FROM analyses
            WHERE ticker_id = %s
            ORDER BY analysis_date DESC
            LIMIT %s
        """
        return self.db.execute_dict_query(query, (ticker_id, limit)) or []

    def get_latest_analysis(self, ticker_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the most recent analysis for a ticker.

        Args:
            ticker_id: Ticker ID

        Returns:
            Analysis dictionary or None
        """
        query = """
            SELECT * FROM analyses
            WHERE ticker_id = %s
            ORDER BY analysis_date DESC
            LIMIT 1
        """
        return self.db.execute_dict_query(query, (ticker_id,), fetch_one=True)

    # Placeholder methods for future implementation
    def store_buy_signal(self, signal_data: Dict[str, Any]) -> int:
        """Store a buy/sell signal (to be implemented)."""
        pass

    def store_portfolio_action(self, action_data: Dict[str, Any]) -> int:
        """Store a portfolio action (to be implemented)."""
        pass

    def track_performance(self, tracking_data: Dict[str, Any]) -> int:
        """Track performance of a position (to be implemented)."""
        pass
