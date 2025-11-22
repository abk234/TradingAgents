# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Enhanced Tools for Eddie

Additional tools that integrate backtesting, dividend analysis, and sector balance.
"""

from typing import Dict, Any, Optional
from datetime import date, timedelta
import logging

from langchain_core.tools import tool

from tradingagents.database import get_db_connection
from tradingagents.backtest import BacktestEngine, StrategyValidator
from tradingagents.strategy import StrategyStorage, StrategyScorer
from tradingagents.dividends.dividend_metrics import DividendMetrics
from tradingagents.screener.sector_analyzer import SectorAnalyzer

logger = logging.getLogger(__name__)


@tool
def get_dividend_analysis(ticker: str) -> str:
    """
    Get comprehensive dividend analysis for a stock.
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        Dividend yield, safety score, growth rate, and recommendations
    """
    try:
        db = get_db_connection()
        dividend_metrics = DividendMetrics(db)
        
        metrics = dividend_metrics.calculate_dividend_metrics(ticker.upper())
        
        if not metrics:
            return f"No dividend data available for {ticker.upper()}"
        
        response = [
            f"💵 Dividend Analysis: {ticker.upper()}\n",
            f"Dividend Yield: {metrics.get('dividend_yield_pct', 0):.2f}%",
            f"Annual Dividend: ${metrics.get('annual_dividend_per_share', 0):.2f} per share",
            f"Payment Frequency: {metrics.get('payment_frequency', 'N/A')}"
        ]
        
        if metrics.get('growth_3yr_pct'):
            response.append(f"3-Year Growth Rate: {metrics['growth_3yr_pct']:.2f}%")
        
        safety = dividend_metrics.analyze_dividend_safety(ticker.upper())
        if safety:
            response.append(f"\nSafety Score: {safety.get('safety_score', 0)}/100")
            response.append(f"Payout Ratio: {safety.get('payout_ratio', 0):.1f}%")
        
        return "\n".join(response)
    
    except Exception as e:
        logger.error(f"Error getting dividend analysis: {e}")
        return f"Error analyzing dividends for {ticker}: {str(e)}"


@tool
def check_sector_balance(ticker: str, current_portfolio_sectors: Optional[Dict[str, float]] = None) -> str:
    """
    Check sector balance and diversification for a stock recommendation.
    
    Args:
        ticker: Stock ticker symbol
        current_portfolio_sectors: Current sector allocation (optional)
    
    Returns:
        Sector balance analysis and recommendations
    """
    try:
        db = get_db_connection()
        ticker_ops = TickerOperations(db)
        sector_analyzer = SectorAnalyzer(db)
        
        ticker_info = ticker_ops.get_ticker(symbol=ticker.upper())
        if not ticker_info:
            return f"Ticker {ticker} not found"
        
        sector = ticker_info.get('sector', 'Unknown')
        
        response = [
            f"📊 Sector Balance Analysis: {ticker.upper()}\n",
            f"Sector: {sector}"
        ]
        
        # Get sector strength
        all_sectors = sector_analyzer.analyze_all_sectors()
        sector_data = next((s for s in all_sectors if s['sector'] == sector), None)
        
        if sector_data:
            strength = sector_data.get('strength_score', 0)
            response.append(f"Sector Strength: {strength:.1f}%")
            
            if strength > 40:
                response.append("✅ Strong sector - good opportunities")
            elif strength < 20:
                response.append("⚠️ Weak sector - proceed with caution")
        
        # Check portfolio balance if provided
        if current_portfolio_sectors:
            current_exposure = current_portfolio_sectors.get(sector, 0)
            response.append(f"\nCurrent Portfolio Exposure: {current_exposure:.1f}%")
            response.append(f"Recommended Limit: 35%")
            
            if current_exposure > 35:
                response.append("❌ OVERWEIGHT - Would exceed sector limit")
            elif current_exposure > 30:
                response.append("⚠️ Approaching limit - consider diversification")
            elif current_exposure < 15:
                response.append("✅ Underweight - good diversification opportunity")
        else:
            response.append("\n💡 Tip: Keep sector exposure below 35% for proper diversification")
        
        return "\n".join(response)
    
    except Exception as e:
        logger.error(f"Error checking sector balance: {e}")
        return f"Error checking sector balance: {str(e)}"


@tool
def validate_strategy_backtest(strategy_name: str = "Four-Gate Framework", test_tickers: Optional[list] = None) -> str:
    """
    Validate a trading strategy using backtesting.
    
    Args:
        strategy_name: Name of strategy to validate
        test_tickers: List of tickers to test (default: ['AAPL', 'MSFT', 'GOOGL'])
    
    Returns:
        Backtest validation results
    """
    try:
        if not test_tickers:
            test_tickers = ['AAPL', 'MSFT', 'GOOGL']
        
        validator = StrategyValidator()
        
        validation_result = validator.validate_strategy(
            strategy_name=strategy_name,
            strategy_config={
                'holding_period_days': 30,
                'min_confidence': 70
            },
            test_tickers=test_tickers,
            test_period_days=90
        )
        
        summary = validator.get_validation_summary(validation_result)
        return summary
    
    except Exception as e:
        logger.error(f"Error validating strategy: {e}")
        return f"Error validating strategy: {str(e)}"


@tool
def get_top_strategies(limit: int = 5) -> str:
    """
    Get top performing trading strategies.
    
    Args:
        limit: Number of strategies to return
    
    Returns:
        List of top strategies with performance metrics
    """
    try:
        storage = StrategyStorage()
        scorer = StrategyScorer()
        
        top_strategies = storage.get_top_strategies(limit=limit)
        ranked = scorer.rank_strategies(top_strategies)
        
        if not ranked:
            return "No validated strategies found. Run backtesting to validate strategies."
        
        response = [f"🏆 Top {len(ranked)} Trading Strategies:\n"]
        
        for i, strategy in enumerate(ranked, 1):
            response.append(
                f"{i}. {strategy['strategy_name']} v{strategy.get('strategy_version', 1)}\n"
                f"   Score: {strategy.get('strategy_score', 0):.1f}/100\n"
                f"   Win Rate: {strategy.get('win_rate', 0):.1f}%\n"
                f"   Avg Return: {strategy.get('avg_return_pct', 0):.2f}%\n"
                f"   Sharpe Ratio: {strategy.get('sharpe_ratio', 0):.2f}\n"
            )
        
        return "\n".join(response)
    
    except Exception as e:
        logger.error(f"Error getting top strategies: {e}")
        return f"Error retrieving strategies: {str(e)}"

