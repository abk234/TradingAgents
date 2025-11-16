"""
Context Retriever Module

Retrieves relevant historical context using vector similarity search.
"""

from typing import List, Dict, Any, Optional
from datetime import date, datetime
import logging

from tradingagents.database import get_db_connection, DatabaseConnection, RAGOperations

logger = logging.getLogger(__name__)


class ContextRetriever:
    """Retrieve relevant historical context for analysis."""

    def __init__(self, db: Optional[DatabaseConnection] = None):
        """
        Initialize context retriever.

        Args:
            db: DatabaseConnection instance (optional)
        """
        self.db = db or get_db_connection()
        self.rag_ops = RAGOperations(self.db)

    def find_similar_analyses(
        self,
        query_embedding: List[float],
        ticker_id: int = None,
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Find similar past analyses.

        Args:
            query_embedding: Query embedding vector
            ticker_id: Filter by ticker (optional)
            limit: Maximum results
            similarity_threshold: Minimum similarity (0-1)

        Returns:
            List of similar analyses with similarity scores
        """
        results = self.rag_ops.find_similar_analyses(
            query_embedding,
            limit=limit,
            similarity_threshold=similarity_threshold,
            ticker_id=ticker_id
        )

        # Enrich with ticker information
        for result in results:
            ticker_query = """
                SELECT symbol, company_name, sector
                FROM tickers
                WHERE ticker_id = %s
            """
            ticker_info = self.db.execute_dict_query(
                ticker_query,
                (result['ticker_id'],),
                fetch_one=True
            )

            if ticker_info:
                result['symbol'] = ticker_info['symbol']
                result['company_name'] = ticker_info['company_name']
                result['sector'] = ticker_info['sector']

        return results

    def get_ticker_history(
        self,
        ticker_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get analysis history for a specific ticker.

        Args:
            ticker_id: Ticker ID
            limit: Maximum number of analyses

        Returns:
            List of past analyses
        """
        query = """
            SELECT
                analysis_id,
                analysis_date,
                price_at_analysis,
                final_decision,
                confidence_score,
                executive_summary,
                key_catalysts,
                risk_factors,
                expected_return_pct
            FROM analyses
            WHERE ticker_id = %s
            ORDER BY analysis_date DESC
            LIMIT %s
        """

        return self.db.execute_dict_query(query, (ticker_id, limit)) or []

    def get_pattern_success_rate(
        self,
        pattern_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get success rate for a specific pattern.

        Args:
            pattern_type: Pattern name

        Returns:
            Statistics dictionary or None
        """
        return self.rag_ops.get_pattern_performance(pattern_type)

    def find_cross_ticker_patterns(
        self,
        query_embedding: List[float],
        exclude_ticker_id: int = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar patterns in other tickers.

        Args:
            query_embedding: Query embedding
            exclude_ticker_id: Ticker to exclude (optional)
            limit: Maximum results

        Returns:
            List of similar patterns from other stocks
        """
        # Get all similar analyses
        all_similar = self.rag_ops.find_similar_analyses(
            query_embedding,
            limit=limit * 2,  # Get more to filter
            similarity_threshold=0.6
        )

        # Filter out the excluded ticker and limit results
        if exclude_ticker_id:
            filtered = [
                result for result in all_similar
                if result.get('ticker_id') != exclude_ticker_id
            ]
        else:
            filtered = all_similar

        return filtered[:limit]

    def get_sector_context(
        self,
        sector: str,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Get recent context for a sector.

        Args:
            sector: Sector name
            days_back: Number of days to look back

        Returns:
            Sector context dictionary
        """
        query = """
            SELECT
                t.symbol,
                a.analysis_date,
                a.final_decision,
                a.confidence_score,
                a.expected_return_pct
            FROM analyses a
            JOIN tickers t ON a.ticker_id = t.ticker_id
            WHERE t.sector = %s
              AND a.analysis_date >= CURRENT_DATE - INTERVAL '%s days'
            ORDER BY a.analysis_date DESC
        """

        analyses = self.db.execute_dict_query(
            query,
            (sector, days_back)
        ) or []

        # Aggregate statistics
        if analyses:
            total = len(analyses)
            buy_signals = sum(1 for a in analyses if a['final_decision'] == 'BUY')
            avg_confidence = sum(a['confidence_score'] or 0 for a in analyses) / total

            return {
                'sector': sector,
                'total_analyses': total,
                'buy_signals': buy_signals,
                'buy_signal_rate': buy_signals / total if total > 0 else 0,
                'average_confidence': avg_confidence,
                'recent_analyses': analyses[:5]
            }

        return {
            'sector': sector,
            'total_analyses': 0,
            'buy_signals': 0,
            'buy_signal_rate': 0,
            'average_confidence': 0,
            'recent_analyses': []
        }

    def build_historical_context(
        self,
        ticker_id: int,
        current_situation_embedding: List[float],
        symbol: str = None
    ) -> Dict[str, Any]:
        """
        Build comprehensive historical context for analysis.

        Args:
            ticker_id: Ticker ID
            current_situation_embedding: Embedding of current situation
            symbol: Ticker symbol (for logging)

        Returns:
            Complete context dictionary
        """
        context = {
            'ticker_id': ticker_id,
            'symbol': symbol,
            'timestamp': datetime.now()
        }

        # 1. Get ticker's own history
        ticker_history = self.get_ticker_history(ticker_id, limit=5)
        context['ticker_history'] = ticker_history

        if ticker_history:
            latest = ticker_history[0]
            context['last_analysis'] = {
                'date': latest['analysis_date'],
                'decision': latest['final_decision'],
                'confidence': latest['confidence_score'],
                'price': latest['price_at_analysis']
            }

        # 2. Find similar past situations
        similar_analyses = self.find_similar_analyses(
            current_situation_embedding,
            ticker_id=ticker_id,
            limit=3,
            similarity_threshold=0.7
        )
        context['similar_situations'] = similar_analyses

        # 3. Find cross-ticker patterns
        cross_ticker = self.find_cross_ticker_patterns(
            current_situation_embedding,
            exclude_ticker_id=ticker_id,
            limit=3
        )
        context['cross_ticker_patterns'] = cross_ticker

        # 4. Get sector context (if we know the sector)
        if ticker_history and ticker_history[0].get('sector'):
            sector = ticker_history[0]['sector']
            sector_context = self.get_sector_context(sector, days_back=30)
            context['sector_context'] = sector_context

        return context

    def summarize_context_for_prompt(
        self,
        context: Dict[str, Any]
    ) -> str:
        """
        Summarize context into a text format for LLM prompts.

        Args:
            context: Context dictionary from build_historical_context

        Returns:
            Formatted context string
        """
        lines = []

        lines.append("=== HISTORICAL INTELLIGENCE ===\n")

        # Last analysis
        if context.get('last_analysis'):
            last = context['last_analysis']
            lines.append(f"Last Analyzed: {last['date']}")
            lines.append(f"  Decision: {last['decision']}")
            lines.append(f"  Confidence: {last['confidence']}/100")
            lines.append(f"  Price Then: ${last['price']:.2f}")
            lines.append("")

        # Similar situations
        similar = context.get('similar_situations', [])
        if similar:
            lines.append("Similar Past Situations:")
            for i, situation in enumerate(similar[:3], 1):
                lines.append(f"{i}. {situation.get('analysis_date', 'Unknown date')}")
                lines.append(f"   Decision: {situation.get('final_decision', 'N/A')}")
                lines.append(f"   Similarity: {situation.get('similarity', 0):.2f}")
                if situation.get('executive_summary'):
                    summary = situation['executive_summary'][:150]
                    lines.append(f"   Summary: {summary}...")
                lines.append("")

        # Cross-ticker patterns
        cross = context.get('cross_ticker_patterns', [])
        if cross:
            lines.append("Similar Patterns in Other Stocks:")
            for i, pattern in enumerate(cross[:2], 1):
                symbol = pattern.get('symbol', 'Unknown')
                lines.append(f"{i}. {symbol} - {pattern.get('analysis_date', 'Unknown')}")
                lines.append(f"   Decision: {pattern.get('final_decision', 'N/A')}")
                lines.append(f"   Similarity: {pattern.get('similarity', 0):.2f}")
            lines.append("")

        # Sector context
        sector_ctx = context.get('sector_context')
        if sector_ctx and sector_ctx.get('total_analyses', 0) > 0:
            lines.append(f"Sector Analysis ({sector_ctx['sector']}):")
            lines.append(f"  Recent analyses: {sector_ctx['total_analyses']}")
            lines.append(f"  Buy signals: {sector_ctx['buy_signals']} ({sector_ctx['buy_signal_rate']:.1%})")
            lines.append(f"  Avg confidence: {sector_ctx['average_confidence']:.1f}/100")
            lines.append("")

        lines.append("=== END HISTORICAL INTELLIGENCE ===")

        return "\n".join(lines)
