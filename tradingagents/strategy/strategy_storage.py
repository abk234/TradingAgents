"""
Strategy Storage

Manages storage and retrieval of trading strategies.
"""

from typing import Dict, Any, List, Optional
from datetime import date
import logging
import json

from tradingagents.database import get_db_connection

logger = logging.getLogger(__name__)


class StrategyStorage:
    """Store and retrieve trading strategies."""
    
    def __init__(self, db=None):
        """Initialize strategy storage."""
        self.db = db or get_db_connection()
    
    def save_strategy(
        self,
        strategy_name: str,
        strategy_description: str,
        indicator_combination: Dict[str, Any],
        gate_thresholds: Dict[str, int],
        sector_focus: List[str] = None,
        min_confidence: int = 70,
        holding_period_days: int = 30,
        backtest_results: Dict[str, Any] = None,
        parent_strategy_id: int = None,
        improvement_notes: str = None
    ) -> int:
        """
        Save a trading strategy.
        
        Returns:
            strategy_id
        """
        # Get next version number
        version_query = """
            SELECT COALESCE(MAX(strategy_version), 0) + 1
            FROM trading_strategies
            WHERE strategy_name = %s
        """
        version_result = self.db.execute_query(version_query, (strategy_name,), fetch_one=True)
        version = version_result[0] if version_result else 1
        
        # Extract performance metrics from backtest results
        win_rate = None
        avg_return_pct = None
        sharpe_ratio = None
        max_drawdown_pct = None
        total_trades = None
        is_validated = False
        
        if backtest_results:
            win_rate = backtest_results.get('win_rate')
            avg_return_pct = backtest_results.get('avg_return')
            sharpe_ratio = backtest_results.get('sharpe_ratio')
            max_drawdown_pct = backtest_results.get('max_drawdown')
            total_trades = backtest_results.get('total_trades')
            
            # Check if validated (meets minimum thresholds)
            is_validated = (
                win_rate and win_rate >= 55.0 and
                avg_return_pct and avg_return_pct >= 5.0 and
                sharpe_ratio and sharpe_ratio >= 0.5 and
                max_drawdown_pct and max_drawdown_pct <= 25.0
            )
        
        query = """
            INSERT INTO trading_strategies (
                strategy_name, strategy_description, strategy_version,
                indicator_combination, gate_thresholds, sector_focus,
                min_confidence, holding_period_days,
                backtest_results, win_rate, avg_return_pct, sharpe_ratio,
                max_drawdown_pct, total_trades,
                is_validated, validation_date,
                parent_strategy_id, improvement_notes,
                last_backtest_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING strategy_id
        """
        
        validation_date = date.today() if is_validated else None
        last_backtest_date = date.today() if backtest_results else None
        
        result = self.db.execute_query(
            query,
            (
                strategy_name, strategy_description, version,
                json.dumps(indicator_combination), json.dumps(gate_thresholds),
                sector_focus or [],
                min_confidence, holding_period_days,
                json.dumps(backtest_results) if backtest_results else None,
                win_rate, avg_return_pct, sharpe_ratio,
                max_drawdown_pct, total_trades,
                is_validated, validation_date,
                parent_strategy_id, improvement_notes,
                last_backtest_date
            ),
            fetch_one=True
        )
        
        strategy_id = result[0]
        logger.info(f"Saved strategy: {strategy_name} v{version} (ID: {strategy_id})")
        
        return strategy_id
    
    def get_strategy(self, strategy_id: int) -> Optional[Dict[str, Any]]:
        """Get a strategy by ID."""
        query = """
            SELECT 
                strategy_id, strategy_name, strategy_description, strategy_version,
                indicator_combination, gate_thresholds, sector_focus,
                min_confidence, holding_period_days,
                backtest_results, win_rate, avg_return_pct, sharpe_ratio,
                max_drawdown_pct, total_trades,
                is_active, is_validated, validation_date,
                parent_strategy_id, improvement_notes,
                created_at, updated_at, last_backtest_date
            FROM trading_strategies
            WHERE strategy_id = %s
        """
        
        result = self.db.execute_dict_query(query, (strategy_id,), fetch_one=True)
        
        if result:
            # Parse JSONB fields
            if result.get('indicator_combination'):
                result['indicator_combination'] = json.loads(result['indicator_combination']) if isinstance(result['indicator_combination'], str) else result['indicator_combination']
            if result.get('gate_thresholds'):
                result['gate_thresholds'] = json.loads(result['gate_thresholds']) if isinstance(result['gate_thresholds'], str) else result['gate_thresholds']
            if result.get('backtest_results'):
                result['backtest_results'] = json.loads(result['backtest_results']) if isinstance(result['backtest_results'], str) else result['backtest_results']
        
        return result
    
    def get_top_strategies(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing strategies."""
        query = """
            SELECT 
                strategy_id, strategy_name, strategy_version,
                win_rate, avg_return_pct, sharpe_ratio, max_drawdown_pct,
                total_trades, is_validated, last_backtest_date
            FROM v_top_strategies
            LIMIT %s
        """
        
        results = self.db.execute_dict_query(query, (limit,))
        return results or []
    
    def update_strategy_backtest(
        self,
        strategy_id: int,
        backtest_results: Dict[str, Any]
    ) -> bool:
        """Update strategy with new backtest results."""
        win_rate = backtest_results.get('win_rate')
        avg_return_pct = backtest_results.get('avg_return')
        sharpe_ratio = backtest_results.get('sharpe_ratio')
        max_drawdown_pct = backtest_results.get('max_drawdown')
        total_trades = backtest_results.get('total_trades')
        
        # Check validation
        is_validated = (
            win_rate and win_rate >= 55.0 and
            avg_return_pct and avg_return_pct >= 5.0 and
            sharpe_ratio and sharpe_ratio >= 0.5 and
            max_drawdown_pct and max_drawdown_pct <= 25.0
        )
        
        query = """
            UPDATE trading_strategies
            SET 
                backtest_results = %s,
                win_rate = %s,
                avg_return_pct = %s,
                sharpe_ratio = %s,
                max_drawdown_pct = %s,
                total_trades = %s,
                is_validated = %s,
                validation_date = CASE WHEN %s THEN CURRENT_DATE ELSE validation_date END,
                last_backtest_date = CURRENT_DATE
            WHERE strategy_id = %s
        """
        
        self.db.execute_query(
            query,
            (
                json.dumps(backtest_results),
                win_rate, avg_return_pct, sharpe_ratio,
                max_drawdown_pct, total_trades,
                is_validated, is_validated,
                strategy_id
            )
        )
        
        logger.info(f"Updated strategy {strategy_id} with backtest results")
        return True

