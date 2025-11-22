# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Strategy Validator

Validates strategies before deployment using backtesting.
"""

from typing import Dict, Any, Optional
from datetime import date, timedelta
import logging

from .backtest_engine import BacktestEngine, BacktestResult

logger = logging.getLogger(__name__)


class StrategyValidator:
    """
    Validates trading strategies before deployment.
    
    Uses backtesting to ensure strategies meet minimum performance criteria.
    """
    
    # Minimum performance thresholds
    MIN_WIN_RATE = 55.0  # 55% win rate
    MIN_AVG_RETURN = 5.0  # 5% average return
    MIN_SHARPE_RATIO = 0.5  # Sharpe ratio > 0.5
    MAX_DRAWDOWN = 25.0  # Max drawdown < 25%
    
    def __init__(self, backtest_engine: Optional[BacktestEngine] = None):
        """Initialize strategy validator."""
        self.backtest_engine = backtest_engine or BacktestEngine()
    
    def validate_strategy(
        self,
        strategy_name: str,
        strategy_config: Dict[str, Any],
        test_tickers: list,
        test_period_days: int = 90
    ) -> Dict[str, Any]:
        """
        Validate a strategy using backtesting.
        
        Args:
            strategy_name: Name of the strategy
            strategy_config: Strategy configuration (gate thresholds, etc.)
            test_tickers: List of tickers to test on
            test_period_days: Number of days to backtest
        
        Returns:
            Validation result with pass/fail and metrics
        """
        logger.info(f"Validating strategy: {strategy_name}")
        
        # Calculate test period
        end_date = date.today()
        start_date = end_date - timedelta(days=test_period_days)
        
        # Run backtest
        backtest_result = self.backtest_engine.test_strategy(
            strategy_name=strategy_name,
            start_date=start_date,
            end_date=end_date,
            tickers=test_tickers,
            holding_period_days=strategy_config.get('holding_period_days', 30),
            min_confidence=strategy_config.get('min_confidence', 70)
        )
        
        # Evaluate against thresholds
        validation_result = {
            'strategy_name': strategy_name,
            'validated': False,
            'backtest_result': backtest_result.to_dict(),
            'thresholds_met': {},
            'issues': []
        }
        
        # Check win rate
        win_rate_ok = backtest_result.win_rate >= self.MIN_WIN_RATE
        validation_result['thresholds_met']['win_rate'] = win_rate_ok
        if not win_rate_ok:
            validation_result['issues'].append(
                f"Win rate {backtest_result.win_rate:.1f}% below minimum {self.MIN_WIN_RATE}%"
            )
        
        # Check average return
        avg_return_ok = backtest_result.avg_return >= self.MIN_AVG_RETURN
        validation_result['thresholds_met']['avg_return'] = avg_return_ok
        if not avg_return_ok:
            validation_result['issues'].append(
                f"Avg return {backtest_result.avg_return:.2f}% below minimum {self.MIN_AVG_RETURN}%"
            )
        
        # Check Sharpe ratio
        sharpe_ok = backtest_result.sharpe_ratio >= self.MIN_SHARPE_RATIO
        validation_result['thresholds_met']['sharpe_ratio'] = sharpe_ok
        if not sharpe_ok:
            validation_result['issues'].append(
                f"Sharpe ratio {backtest_result.sharpe_ratio:.2f} below minimum {self.MIN_SHARPE_RATIO}"
            )
        
        # Check max drawdown
        drawdown_ok = backtest_result.max_drawdown <= self.MAX_DRAWDOWN
        validation_result['thresholds_met']['max_drawdown'] = drawdown_ok
        if not drawdown_ok:
            validation_result['issues'].append(
                f"Max drawdown {backtest_result.max_drawdown:.2f}% exceeds maximum {self.MAX_DRAWDOWN}%"
            )
        
        # Overall validation
        all_ok = all(validation_result['thresholds_met'].values())
        validation_result['validated'] = all_ok
        
        if all_ok:
            logger.info(f"Strategy {strategy_name} validated successfully")
        else:
            logger.warning(
                f"Strategy {strategy_name} failed validation: "
                f"{', '.join(validation_result['issues'])}"
            )
        
        return validation_result
    
    def get_validation_summary(self, validation_result: Dict[str, Any]) -> str:
        """Get human-readable validation summary."""
        result = validation_result['backtest_result']
        
        summary = f"""
Strategy Validation: {validation_result['strategy_name']}
{'=' * 60}

Backtest Results:
  Period: {result['start_date']} to {result['end_date']}
  Trades: {result['total_trades']} (Win: {result['winning_trades']}, Loss: {result['losing_trades']})
  Win Rate: {result['win_rate']:.1f}% {'✅' if validation_result['thresholds_met']['win_rate'] else '❌'}
  Avg Return: {result['avg_return']:.2f}% {'✅' if validation_result['thresholds_met']['avg_return'] else '❌'}
  Sharpe Ratio: {result['sharpe_ratio']:.2f} {'✅' if validation_result['thresholds_met']['sharpe_ratio'] else '❌'}
  Max Drawdown: {result['max_drawdown']:.2f}% {'✅' if validation_result['thresholds_met']['max_drawdown'] else '❌'}

Validation Status: {'✅ PASSED' if validation_result['validated'] else '❌ FAILED'}
"""
        
        if validation_result['issues']:
            summary += "\nIssues:\n"
            for issue in validation_result['issues']:
                summary += f"  - {issue}\n"
        
        return summary

