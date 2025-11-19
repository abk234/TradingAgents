"""
Quantitative / Systematic Investing Strategy

Focuses on data-driven, factor-based decisions.
"""

from typing import Dict, Any, Optional
import logging

from .base import InvestmentStrategy, StrategyResult, Recommendation
from .utils import (
    safe_float,
    extract_metric,
    normalize_confidence,
    format_reasoning,
)

logger = logging.getLogger(__name__)


class QuantitativeStrategy(InvestmentStrategy):
    """
    Quantitative / systematic investing strategy.
    
    Key principles:
    - Data-driven, rule-based decisions
    - Factor-based investing (value, momentum, quality, size)
    - Multi-factor scoring
    - Systematic approach
    """
    
    def get_strategy_name(self) -> str:
        return "Quantitative Investing"
    
    def get_timeframe(self) -> str:
        return "Weeks to months"
    
    def evaluate(
        self,
        ticker: str,
        market_data: Dict[str, Any],
        fundamental_data: Dict[str, Any],
        technical_data: Dict[str, Any],
        additional_data: Optional[Dict[str, Any]] = None
    ) -> StrategyResult:
        """
        Evaluate stock using quantitative / systematic principles.
        """
        # Validate data
        if not self.validate_data(market_data, fundamental_data, technical_data):
            return StrategyResult(
                recommendation=Recommendation.WAIT,
                confidence=0,
                reasoning="Insufficient data for quantitative analysis",
                strategy_name=self.get_strategy_name()
            )
        
        # Extract metrics for factor analysis
        current_price = extract_metric(market_data, "current_price", 0.0)
        pe_ratio = extract_metric(fundamental_data, "pe_ratio") or extract_metric(fundamental_data, "Trailing P/E")
        pb_ratio = extract_metric(fundamental_data, "price_to_book") or extract_metric(fundamental_data, "Price to Book")
        revenue_growth = extract_metric(fundamental_data, "revenue_growth") or extract_metric(fundamental_data, "Revenue Growth")
        roe = extract_metric(fundamental_data, "roe") or extract_metric(fundamental_data, "ROE")
        rsi = extract_metric(technical_data, "rsi") or extract_metric(technical_data, "RSI")
        market_cap = extract_metric(market_data, "market_cap", 0.0)
        
        # Calculate factor scores (0-100 each)
        value_score = self._calculate_value_factor(pe_ratio, pb_ratio)
        momentum_score = self._calculate_momentum_factor(rsi, technical_data)
        quality_score = self._calculate_quality_factor(roe, fundamental_data)
        size_score = self._calculate_size_factor(market_cap)
        
        # Weighted composite score
        weights = {
            "value": 0.30,
            "momentum": 0.25,
            "quality": 0.25,
            "size": 0.20,
        }
        
        composite_score = (
            value_score * weights["value"] +
            momentum_score * weights["momentum"] +
            quality_score * weights["quality"] +
            size_score * weights["size"]
        )
        
        # Score the investment
        score = composite_score
        reasons = []
        risks = []
        key_metrics = {
            "current_price": current_price,
            "value_score": value_score,
            "momentum_score": momentum_score,
            "quality_score": quality_score,
            "size_score": size_score,
            "composite_score": composite_score,
        }
        
        # Factor-based reasoning
        if value_score > 70:
            reasons.append(f"Strong value factor ({value_score:.0f}/100)")
        elif value_score < 30:
            reasons.append(f"Weak value factor ({value_score:.0f}/100)")
            risks.append("Poor value metrics indicate overvaluation")
        
        if momentum_score > 70:
            reasons.append(f"Strong momentum factor ({momentum_score:.0f}/100)")
        elif momentum_score < 30:
            reasons.append(f"Weak momentum factor ({momentum_score:.0f}/100)")
            risks.append("Poor momentum suggests weak price action")
        
        if quality_score > 70:
            reasons.append(f"Strong quality factor ({quality_score:.0f}/100)")
        elif quality_score < 30:
            reasons.append(f"Weak quality factor ({quality_score:.0f}/100)")
            risks.append("Poor quality metrics indicate weak fundamentals")
        
        if size_score > 70:
            reasons.append(f"Favorable size factor ({size_score:.0f}/100)")
        
        # Determine recommendation
        confidence = normalize_confidence(score, 0, 100)
        
        if score >= 70:
            recommendation = Recommendation.BUY
        elif score >= 50:
            recommendation = Recommendation.HOLD
        elif score >= 30:
            recommendation = Recommendation.WAIT
        else:
            recommendation = Recommendation.SELL
        
        # Calculate target price (based on factor improvement)
        target_price = current_price * 1.20 if current_price > 0 and score > 70 else None
        
        return StrategyResult(
            recommendation=recommendation,
            confidence=confidence,
            reasoning=format_reasoning(reasons),
            entry_price=current_price if current_price > 0 else None,
            target_price=target_price,
            holding_period="Weeks to months",
            key_metrics=key_metrics,
            risks=risks,
            strategy_name=self.get_strategy_name()
        )
    
    def _calculate_value_factor(self, pe_ratio: Optional[float], pb_ratio: Optional[float]) -> float:
        """Calculate value factor score (0-100)."""
        score = 50  # Neutral
        
        if pe_ratio:
            if pe_ratio < 15:
                score += 25
            elif pe_ratio < 25:
                score += 10
            elif pe_ratio > 50:
                score -= 25
        
        if pb_ratio:
            if pb_ratio < 2:
                score += 15
            elif pb_ratio > 5:
                score -= 15
        
        return max(0, min(100, score))
    
    def _calculate_momentum_factor(self, rsi: Optional[float], technical_data: Dict[str, Any]) -> float:
        """Calculate momentum factor score (0-100)."""
        score = 50  # Neutral
        
        if rsi is not None:
            if 50 <= rsi <= 70:
                score += 30
            elif 30 <= rsi < 50:
                score += 10
            elif rsi > 70:
                score -= 20
            elif rsi < 30:
                score -= 10
        
        return max(0, min(100, score))
    
    def _calculate_quality_factor(self, roe: Optional[float], fundamental_data: Dict[str, Any]) -> float:
        """Calculate quality factor score (0-100)."""
        score = 50  # Neutral
        
        if roe:
            if roe > 0.20:  # 20%
                score += 30
            elif roe > 0.15:  # 15%
                score += 15
            elif roe < 0.10:  # 10%
                score -= 20
        
        # Check profit margins
        profit_margin = extract_metric(fundamental_data, "profit_margin") or extract_metric(fundamental_data, "Profit Margin")
        if profit_margin:
            if profit_margin > 0.15:  # 15%
                score += 20
            elif profit_margin < 0.05:  # 5%
                score -= 15
        
        return max(0, min(100, score))
    
    def _calculate_size_factor(self, market_cap: float) -> float:
        """Calculate size factor score (0-100)."""
        # Prefer mid-cap to large-cap (not micro-cap)
        if market_cap > 10_000_000_000:  # >$10B (large-cap)
            return 70
        elif market_cap > 2_000_000_000:  # $2B-$10B (mid-cap)
            return 80
        elif market_cap > 300_000_000:  # $300M-$2B (small-cap)
            return 60
        else:  # <$300M (micro-cap)
            return 40

