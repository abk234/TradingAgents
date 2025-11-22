# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Dividend Investing Strategy

Focuses on dividend yield, dividend growth, and dividend safety.
"""

from typing import Dict, Any, Optional
import logging

from .base import InvestmentStrategy, StrategyResult, Recommendation
from .utils import (
    safe_float,
    safe_int,
    extract_metric,
    normalize_confidence,
    format_reasoning,
)

logger = logging.getLogger(__name__)


class DividendStrategy(InvestmentStrategy):
    """
    Dividend investing strategy.
    
    Key principles:
    - Buy stocks with high, sustainable dividend yields
    - Focus on dividend growth over time
    - Dividend safety (payout ratio < 80%, consistent payments)
    - Reinvest dividends for compound growth
    """
    
    def get_strategy_name(self) -> str:
        return "Dividend Investing"
    
    def get_timeframe(self) -> str:
        return "5+ years"
    
    def evaluate(
        self,
        ticker: str,
        market_data: Dict[str, Any],
        fundamental_data: Dict[str, Any],
        technical_data: Dict[str, Any],
        additional_data: Optional[Dict[str, Any]] = None
    ) -> StrategyResult:
        """
        Evaluate stock using dividend investing principles.
        """
        # Validate data
        if not self.validate_data(market_data, fundamental_data, technical_data):
            return StrategyResult(
                recommendation=Recommendation.WAIT,
                confidence=0,
                reasoning="Insufficient data for dividend analysis",
                strategy_name=self.get_strategy_name()
            )
        
        # Extract dividend data
        dividend_yield = extract_metric(fundamental_data, "dividend_yield") or extract_metric(fundamental_data, "Dividend Yield")
        current_price = extract_metric(market_data, "current_price", 0.0)
        
        # Get dividend data from additional_data if available
        dividend_data = additional_data.get("dividend_data", {}) if additional_data else {}
        dividend_safety_raw = dividend_data.get("safety_analysis") if dividend_data else None
        dividend_safety = dividend_safety_raw if dividend_safety_raw and isinstance(dividend_safety_raw, dict) else {}
        
        # Extract safety metrics
        payout_ratio = extract_metric(fundamental_data, "payout_ratio") or extract_metric(dividend_safety, "payout_ratio")
        consecutive_years = safe_int(dividend_safety.get("consecutive_years", 0)) if dividend_safety else 0
        dividend_growth = extract_metric(dividend_safety, "growth_rate")
        
        # Score the investment
        score = 50  # Neutral baseline
        reasons = []
        risks = []
        key_metrics = {
            "current_price": current_price,
            "dividend_yield": dividend_yield,
            "payout_ratio": payout_ratio,
            "consecutive_years": consecutive_years,
            "dividend_growth": dividend_growth,
        }
        
        # Dividend yield scoring
        if dividend_yield:
            if dividend_yield >= 0.04:  # 4%+
                score += 25
                reasons.append(f"Attractive dividend yield ({dividend_yield:.2%})")
            elif dividend_yield >= 0.03:  # 3-4%
                score += 15
                reasons.append(f"Good dividend yield ({dividend_yield:.2%})")
            elif dividend_yield >= 0.02:  # 2-3%
                score += 5
                reasons.append(f"Moderate dividend yield ({dividend_yield:.2%})")
            elif dividend_yield < 0.01:  # <1%
                score -= 20
                reasons.append("Low dividend yield - not suitable for dividend strategy")
                risks.append("Very low dividend yield doesn't meet income objectives")
        else:
            score -= 30
            reasons.append("No dividend yield data - may not pay dividends")
            risks.append("Stock may not pay dividends")
        
        # Payout ratio scoring (safety)
        if payout_ratio is not None:
            if payout_ratio < 0.60:  # <60%
                score += 20
                reasons.append(f"Safe payout ratio ({payout_ratio:.1%}) - room for growth")
            elif payout_ratio < 0.80:  # 60-80%
                score += 10
                reasons.append(f"Reasonable payout ratio ({payout_ratio:.1%})")
            elif payout_ratio > 0.90:  # >90%
                score -= 20
                reasons.append(f"High payout ratio ({payout_ratio:.1%}) - dividend at risk")
                risks.append("Very high payout ratio may not be sustainable")
        
        # Consecutive years scoring (consistency)
        if consecutive_years:
            if consecutive_years >= 10:
                score += 20
                reasons.append(f"Excellent dividend history ({consecutive_years} consecutive years)")
            elif consecutive_years >= 5:
                score += 10
                reasons.append(f"Good dividend history ({consecutive_years} consecutive years)")
            elif consecutive_years < 3:
                score -= 10
                reasons.append(f"Short dividend history ({consecutive_years} years)")
                risks.append("Short dividend history increases risk of cuts")
        
        # Dividend growth scoring
        if dividend_growth:
            if dividend_growth > 0.10:  # 10%+
                score += 15
                reasons.append(f"Strong dividend growth ({dividend_growth:.1%})")
            elif dividend_growth > 0.05:  # 5-10%
                score += 5
                reasons.append(f"Moderate dividend growth ({dividend_growth:.1%})")
            elif dividend_growth < 0:
                score -= 15
                reasons.append("Declining dividends (concern)")
                risks.append("Dividend cuts indicate financial stress")
        
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
        
        # Calculate target price (conservative, income-focused)
        target_price = current_price * 1.15 if current_price > 0 else None  # Modest appreciation expected
        
        return StrategyResult(
            recommendation=recommendation,
            confidence=confidence,
            reasoning=format_reasoning(reasons),
            entry_price=current_price if current_price > 0 else None,
            target_price=target_price,
            holding_period="5+ years",
            key_metrics=key_metrics,
            risks=risks,
            strategy_name=self.get_strategy_name()
        )

