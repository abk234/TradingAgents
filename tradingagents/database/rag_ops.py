"""
RAG Operations Module

Provides vector similarity search and context retrieval for RAG.
"""

from typing import List, Dict, Any, Optional
import logging
import numpy as np

from .connection import get_db_connection, DatabaseConnection

logger = logging.getLogger(__name__)


class RAGOperations:
    """Operations for RAG context retrieval using vector similarity."""

    def __init__(self, db: Optional[DatabaseConnection] = None):
        """
        Initialize RAG operations.

        Args:
            db: DatabaseConnection instance (creates one if not provided)
        """
        self.db = db or get_db_connection()

    def find_similar_analyses(
        self,
        query_embedding: List[float],
        limit: int = 5,
        similarity_threshold: float = 0.7,
        ticker_id: int = None
    ) -> List[Dict[str, Any]]:
        """
        Find similar analyses using vector similarity search.

        Args:
            query_embedding: Query vector (768-dim)
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score (0-1)
            ticker_id: Optionally filter by ticker

        Returns:
            List of similar analyses with similarity scores
        """
        # Convert list to pgvector format
        embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'

        query = """
            SELECT
                analysis_id,
                ticker_id,
                analysis_date,
                final_decision,
                confidence_score,
                executive_summary,
                1 - (embedding <=> %s::vector) as similarity
            FROM analyses
            WHERE embedding IS NOT NULL
        """
        params = [embedding_str]

        if ticker_id:
            query += " AND ticker_id = %s"
            params.append(ticker_id)

        query += """
            AND 1 - (embedding <=> %s::vector) >= %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        params.extend([embedding_str, similarity_threshold, embedding_str, limit])

        results = self.db.execute_dict_query(query, tuple(params)) or []
        logger.info(f"Found {len(results)} similar analyses")
        return results

    def find_similar_patterns(
        self,
        query_embedding: List[float],
        limit: int = 5,
        pattern_type: str = None
    ) -> List[Dict[str, Any]]:
        """
        Find similar patterns in buy signals.

        Args:
            query_embedding: Query vector (768-dim)
            limit: Maximum number of results
            pattern_type: Filter by pattern type (optional)

        Returns:
            List of similar patterns
        """
        embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'

        query = """
            SELECT
                signal_id,
                ticker_id,
                signal_date,
                signal_type,
                pattern_matched,
                expected_return_pct,
                1 - (embedding <=> %s::vector) as similarity
            FROM buy_signals
            WHERE embedding IS NOT NULL
        """
        params = [embedding_str]

        if pattern_type:
            query += " AND pattern_matched = %s"
            params.append(pattern_type)

        query += """
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        params.extend([embedding_str, limit])

        return self.db.execute_dict_query(query, tuple(params)) or []

    def get_pattern_performance(self, pattern_type: str) -> Optional[Dict[str, Any]]:
        """
        Get performance statistics for a specific pattern type.

        Args:
            pattern_type: Pattern name (e.g., "OVERSOLD_BOUNCE")

        Returns:
            Performance statistics dictionary
        """
        query = """
            SELECT
                bs.pattern_matched,
                COUNT(*) as total_signals,
                AVG(pt.actual_return_pct) as avg_return,
                AVG(pt.holding_period_days) as avg_holding_days,
                SUM(CASE WHEN pt.beat_expectations THEN 1 ELSE 0 END)::FLOAT / NULLIF(COUNT(*), 0) as success_rate
            FROM buy_signals bs
            JOIN performance_tracking pt ON bs.signal_id = pt.signal_id
            WHERE bs.pattern_matched = %s
              AND pt.exit_date IS NOT NULL
            GROUP BY bs.pattern_matched
        """
        return self.db.execute_dict_query(query, (pattern_type,), fetch_one=True)

    # Placeholder methods for future implementation
    def find_similar_market_conditions(self, embedding: List[float]) -> List[Dict[str, Any]]:
        """Find similar market conditions (to be implemented)."""
        pass

    def get_contextual_learnings(self, context: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Get relevant learnings from performance tracking (to be implemented)."""
        pass
