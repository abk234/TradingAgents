"""
Strategy Scorer

Scores and ranks trading strategies based on performance.
"""

from typing import Dict, Any, List
import logging

from tradingagents.database import get_db_connection

logger = logging.getLogger(__name__)


class StrategyScorer:
    """Score and rank trading strategies."""
    
    # Scoring weights
    WIN_RATE_WEIGHT = 0.4
    AVG_RETURN_WEIGHT = 0.3
    SHARPE_WEIGHT = 0.3
    
    def __init__(self, db=None):
        """Initialize strategy scorer."""
        self.db = db or get_db_connection()
    
    def calculate_strategy_score(
        self,
        win_rate: float,
        avg_return_pct: float,
        sharpe_ratio: float
    ) -> float:
        """
        Calculate overall strategy score.
        
        Args:
            win_rate: Win rate percentage (0-100)
            avg_return_pct: Average return percentage
            sharpe_ratio: Sharpe ratio
        
        Returns:
            Strategy score (0-100)
        """
        # Normalize win rate (0-100 -> 0-1)
        win_rate_norm = win_rate / 100.0
        
        # Normalize avg return (assume max 50% -> 0-1)
        return_norm = min(avg_return_pct / 50.0, 1.0)
        
        # Normalize Sharpe (assume max 3.0 -> 0-1)
        sharpe_norm = min(sharpe_ratio / 3.0, 1.0)
        
        # Weighted score
        score = (
            win_rate_norm * self.WIN_RATE_WEIGHT +
            return_norm * self.AVG_RETURN_WEIGHT +
            sharpe_norm * self.SHARPE_WEIGHT
        ) * 100
        
        return round(score, 2)
    
    def rank_strategies(self, strategies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank strategies by score.
        
        Args:
            strategies: List of strategy dictionaries
        
        Returns:
            Ranked list of strategies with scores
        """
        scored = []
        
        for strategy in strategies:
            win_rate = strategy.get('win_rate', 0) or 0
            avg_return = strategy.get('avg_return_pct', 0) or 0
            sharpe = strategy.get('sharpe_ratio', 0) or 0
            
            score = self.calculate_strategy_score(win_rate, avg_return, sharpe)
            
            scored.append({
                **strategy,
                'strategy_score': score
            })
        
        # Sort by score descending
        scored.sort(key=lambda x: x['strategy_score'], reverse=True)
        
        return scored
    
    def get_best_strategy(self) -> Dict[str, Any]:
        """Get the best performing strategy."""
        query = """
            SELECT 
                strategy_id, strategy_name, strategy_version,
                win_rate, avg_return_pct, sharpe_ratio,
                indicator_combination, gate_thresholds
            FROM trading_strategies
            WHERE is_active = TRUE
                AND is_validated = TRUE
            ORDER BY 
                (win_rate * 0.4 + avg_return_pct * 0.3 + sharpe_ratio * 10 * 0.3) DESC
            LIMIT 1
        """
        
        result = self.db.execute_dict_query(query, fetch_one=True)
        return result or {}

