# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Comparison Runner

Runs both existing TradingAgents system and new strategy system,
then compares results.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import date

from tradingagents.strategies import (
    StrategyComparator,
    StrategyDataCollector,
    ValueStrategy,
    GrowthStrategy,
    DividendStrategy,
    MomentumStrategy,
    ContrarianStrategy,
    QuantitativeStrategy,
    SectorRotationStrategy,
)
from tradingagents.integration.strategy_adapter import HybridStrategyAdapter
from tradingagents.graph.trading_graph import TradingAgentsGraph

logger = logging.getLogger(__name__)


class ComparisonRunner:
    """
    Runs both existing and new systems and compares results.
    
    This allows users to:
    1. See how existing system compares to individual strategies
    2. Validate existing system recommendations
    3. Understand differences between approaches
    """
    
    def __init__(
        self,
        include_existing: bool = True,
        strategies: Optional[List] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize comparison runner.
        
        Args:
            include_existing: Whether to include existing system in comparison
            strategies: List of strategy instances (uses all if None)
            config: Configuration dictionary (optional)
        """
        self.include_existing = include_existing
        self.config = config
        
        # Build strategy list
        self.strategies = []
        
        if include_existing:
            # Add existing system as strategy
            self.strategies.append(HybridStrategyAdapter(config=config))
        
        # Add individual strategies
        if strategies:
            self.strategies.extend(strategies)
        else:
            # Use all available strategies
            self.strategies.extend([
                ValueStrategy(),
                GrowthStrategy(),
                DividendStrategy(),
                MomentumStrategy(),
                ContrarianStrategy(),
                QuantitativeStrategy(),
                SectorRotationStrategy(),
            ])
        
        logger.info(f"Initialized ComparisonRunner with {len(self.strategies)} strategies")
    
    def compare_both_systems(
        self,
        ticker: str,
        analysis_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run both existing and new systems and compare results.
        
        Args:
            ticker: Stock symbol to analyze
            analysis_date: Analysis date (YYYY-MM-DD), defaults to today
        
        Returns:
            Comparison report with both systems' results
        """
        if analysis_date is None:
            analysis_date = date.today().strftime("%Y-%m-%d")
        
        logger.info(f"Comparing both systems for {ticker} on {analysis_date}")
        
        # Collect data once
        collector = StrategyDataCollector(config=self.config)
        try:
            data = collector.collect_all_data(ticker, analysis_date)
        except Exception as e:
            logger.error(f"Error collecting data for {ticker}: {e}")
            return {
                "error": str(e),
                "ticker": ticker,
                "analysis_date": analysis_date,
            }
        
        # Run comparison
        comparator = StrategyComparator(self.strategies)
        comparison = comparator.compare(
            ticker=ticker,
            market_data=data["market_data"],
            fundamental_data=data["fundamental_data"],
            technical_data=data["technical_data"],
            additional_data={
                "analysis_date": analysis_date,
                "dividend_data": data.get("dividend_data", {}),
                "news_data": data.get("news_data", {}),
            }
        )
        
        # Add metadata
        comparison["metadata"] = {
            "analysis_date": analysis_date,
            "total_strategies": len(self.strategies),
            "includes_existing_system": self.include_existing,
        }
        
        return comparison
    
    def compare_new_strategies_only(
        self,
        ticker: str,
        analysis_date: Optional[str] = None,
        strategy_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compare only new strategies (exclude existing system).
        
        Args:
            ticker: Stock symbol
            analysis_date: Analysis date (optional)
            strategy_names: List of strategy names to include (all if None)
        
        Returns:
            Comparison report
        """
        if analysis_date is None:
            analysis_date = date.today().strftime("%Y-%m-%d")
        
        # Build strategy list (exclude existing)
        strategies = []
        strategy_map = {
            "value": ValueStrategy(),
            "growth": GrowthStrategy(),
            "dividend": DividendStrategy(),
            "momentum": MomentumStrategy(),
            "contrarian": ContrarianStrategy(),
            "quantitative": QuantitativeStrategy(),
            "sector_rotation": SectorRotationStrategy(),
        }
        
        if strategy_names:
            for name in strategy_names:
                if name.lower() in strategy_map:
                    strategies.append(strategy_map[name.lower()])
        else:
            strategies = list(strategy_map.values())
        
        # Collect data
        collector = StrategyDataCollector(config=self.config)
        try:
            data = collector.collect_all_data(ticker, analysis_date)
        except Exception as e:
            logger.error(f"Error collecting data for {ticker}: {e}")
            return {"error": str(e), "ticker": ticker}
        
        # Run comparison
        comparator = StrategyComparator(strategies)
        comparison = comparator.compare(
            ticker=ticker,
            market_data=data["market_data"],
            fundamental_data=data["fundamental_data"],
            technical_data=data["technical_data"],
            additional_data={
                "analysis_date": analysis_date,
                "dividend_data": data.get("dividend_data", {}),
                "news_data": data.get("news_data", {}),
            }
        )
        
        comparison["metadata"] = {
            "analysis_date": analysis_date,
            "strategies_compared": [s.get_strategy_name() for s in strategies],
        }
        
        return comparison
    
    def compare_with_existing_only(
        self,
        ticker: str,
        analysis_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compare existing system with a single strategy.
        
        Useful for validating existing system against a specific approach.
        """
        if analysis_date is None:
            analysis_date = date.today().strftime("%Y-%m-%d")
        
        # Use existing system + one strategy
        strategies = [
            HybridStrategyAdapter(config=self.config),
            ValueStrategy(),  # Default to value strategy
        ]
        
        # Collect data
        collector = StrategyDataCollector(config=self.config)
        try:
            data = collector.collect_all_data(ticker, analysis_date)
        except Exception as e:
            logger.error(f"Error collecting data for {ticker}: {e}")
            return {"error": str(e), "ticker": ticker}
        
        # Run comparison
        comparator = StrategyComparator(strategies)
        comparison = comparator.compare(
            ticker=ticker,
            market_data=data["market_data"],
            fundamental_data=data["fundamental_data"],
            technical_data=data["technical_data"],
            additional_data={
                "analysis_date": analysis_date,
                "dividend_data": data.get("dividend_data", {}),
                "news_data": data.get("news_data", {}),
            }
        )
        
        return comparison

