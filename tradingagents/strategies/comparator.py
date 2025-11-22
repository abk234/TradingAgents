# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Strategy Comparator

Compares multiple strategies on the same stock and calculates consensus.
"""

from typing import Dict, Any, List, Optional
import logging
from collections import Counter

from .base import InvestmentStrategy, StrategyResult, Recommendation

logger = logging.getLogger(__name__)


class StrategyComparator:
    """
    Compare multiple strategies on the same stock.
    
    Calculates consensus, identifies divergences, and generates insights.
    """
    
    def __init__(self, strategies: List[InvestmentStrategy]):
        """
        Initialize comparator with list of strategies.
        
        Args:
            strategies: List of InvestmentStrategy instances
        """
        if not strategies:
            raise ValueError("At least one strategy is required")
        
        self.strategies = strategies
        logger.info(f"Initialized StrategyComparator with {len(strategies)} strategies")
    
    def compare(
        self,
        ticker: str,
        market_data: Dict[str, Any],
        fundamental_data: Dict[str, Any],
        technical_data: Dict[str, Any],
        additional_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run all strategies and compare results.
        
        Args:
            ticker: Stock symbol
            market_data: Market data dictionary
            fundamental_data: Fundamental data dictionary
            technical_data: Technical data dictionary
            additional_data: Additional data (optional)
        
        Returns:
            Comparison report dictionary:
            {
                "ticker": str,
                "strategies": {strategy_name: StrategyResult},
                "consensus": {...},
                "divergences": [...],
                "insights": [...]
            }
        """
        logger.info(f"Comparing {len(self.strategies)} strategies for {ticker}")
        
        results = {}
        
        # Run each strategy
        for strategy in self.strategies:
            try:
                strategy_name = strategy.get_strategy_name()
                logger.debug(f"Running {strategy_name} for {ticker}")
                
                result = strategy.evaluate(
                    ticker=ticker,
                    market_data=market_data,
                    fundamental_data=fundamental_data,
                    technical_data=technical_data,
                    additional_data=additional_data
                )
                
                # Set strategy name if not set
                if result.strategy_name is None:
                    result.strategy_name = strategy_name
                
                results[strategy_name] = result
                logger.debug(f"{strategy_name}: {result.recommendation.value} ({result.confidence}% confidence)")
            
            except Exception as e:
                logger.error(f"Error running {strategy.get_strategy_name()} for {ticker}: {e}")
                # Create error result
                results[strategy.get_strategy_name()] = StrategyResult(
                    recommendation=Recommendation.WAIT,
                    confidence=0,
                    reasoning=f"Error: {str(e)}",
                    strategy_name=strategy.get_strategy_name()
                )
        
        # Calculate consensus
        consensus = self._calculate_consensus(results)
        
        # Identify divergences
        divergences = self._identify_divergences(results)
        
        # Generate insights
        insights = self._generate_insights(results, consensus, divergences)
        
        return {
            "ticker": ticker,
            "strategies": {name: result.to_dict() for name, result in results.items()},
            "consensus": consensus,
            "divergences": divergences,
            "insights": insights,
        }
    
    def _calculate_consensus(self, results: Dict[str, StrategyResult]) -> Dict[str, Any]:
        """
        Calculate agreement level between strategies.
        
        Args:
            results: Dictionary of strategy_name -> StrategyResult
        
        Returns:
            Consensus dictionary with recommendation, agreement level, etc.
        """
        if not results:
            return {
                "recommendation": None,
                "agreement_level": 0,
                "buy_count": 0,
                "sell_count": 0,
                "hold_count": 0,
                "wait_count": 0,
            }
        
        # Count recommendations
        recommendations = [r.recommendation for r in results.values()]
        rec_counts = Counter(recommendations)
        
        total = len(recommendations)
        max_count = max(rec_counts.values()) if rec_counts else 0
        agreement_level = (max_count / total) * 100 if total > 0 else 0
        
        # Determine consensus recommendation
        consensus_rec = max(rec_counts.items(), key=lambda x: x[1])[0] if rec_counts else None
        
        return {
            "recommendation": consensus_rec.value if consensus_rec else None,
            "agreement_level": round(agreement_level, 1),
            "buy_count": rec_counts.get(Recommendation.BUY, 0),
            "sell_count": rec_counts.get(Recommendation.SELL, 0),
            "hold_count": rec_counts.get(Recommendation.HOLD, 0),
            "wait_count": rec_counts.get(Recommendation.WAIT, 0),
            "total_strategies": total,
        }
    
    def _identify_divergences(self, results: Dict[str, StrategyResult]) -> List[Dict[str, Any]]:
        """
        Identify where strategies disagree.
        
        Args:
            results: Dictionary of strategy_name -> StrategyResult
        
        Returns:
            List of divergence dictionaries
        """
        divergences = []
        
        # Group strategies by recommendation
        by_recommendation = {}
        for name, result in results.items():
            rec = result.recommendation
            if rec not in by_recommendation:
                by_recommendation[rec] = []
            by_recommendation[rec].append(name)
        
        # If more than one recommendation type, there's divergence
        if len(by_recommendation) > 1:
            for rec, strategies in by_recommendation.items():
                divergences.append({
                    "recommendation": rec.value,
                    "strategies": strategies,
                    "count": len(strategies),
                })
        
        return divergences
    
    def _generate_insights(
        self,
        results: Dict[str, StrategyResult],
        consensus: Dict[str, Any],
        divergences: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate human-readable insights.
        
        Args:
            results: Dictionary of strategy_name -> StrategyResult
            consensus: Consensus dictionary
            divergences: List of divergence dictionaries
        
        Returns:
            List of insight strings
        """
        insights = []
        
        # Consensus insight
        agreement_level = consensus.get("agreement_level", 0)
        consensus_rec = consensus.get("recommendation")
        
        if agreement_level >= 80:
            insights.append(
                f"Strong consensus: {consensus['buy_count'] + consensus['sell_count']} of "
                f"{consensus['total_strategies']} strategies recommend {consensus_rec}"
            )
        elif agreement_level >= 60:
            insights.append(
                f"Moderate consensus: Majority of strategies recommend {consensus_rec}"
            )
        elif agreement_level >= 40:
            insights.append(
                f"Mixed signals: Strategies are split ({len(divergences)} different recommendations)"
            )
        else:
            insights.append(
                f"Strong divergence: Strategies disagree significantly ({len(divergences)} different recommendations)"
            )
        
        # Divergence insights
        if divergences:
            for div in divergences:
                strategies_str = ", ".join(div["strategies"])
                insights.append(
                    f"{strategies_str} recommend {div['recommendation']} "
                    f"({div['count']} strategy{'s' if div['count'] > 1 else ''})"
                )
        
        # Key metric insights
        for name, result in results.items():
            if result.key_metrics:
                # Extract notable metrics
                notable = []
                if "margin_of_safety" in result.key_metrics:
                    mos = result.key_metrics["margin_of_safety"]
                    if mos > 30:
                        notable.append(f"{name} sees {mos:.1f}% margin of safety")
                
                if "target_price" in result.key_metrics and result.target_price:
                    current_price = result.key_metrics.get("current_price")
                    if current_price:
                        upside = ((result.target_price - current_price) / current_price) * 100
                        if upside > 20:
                            notable.append(f"{name} projects {upside:.1f}% upside")
                
                insights.extend(notable)
        
        return insights

