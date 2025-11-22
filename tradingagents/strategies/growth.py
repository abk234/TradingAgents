# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Growth Investing Strategy

Focuses on revenue/earnings growth, PEG ratio, and market expansion.
"""

from typing import Dict, Any, Optional
import logging

from .base import InvestmentStrategy, StrategyResult, Recommendation
from .utils import (
    safe_float,
    extract_metric,
    calculate_peg_ratio,
    normalize_confidence,
    format_reasoning,
)

logger = logging.getLogger(__name__)


class GrowthStrategy(InvestmentStrategy):
    """
    Growth investing strategy (Peter Lynch / GARP style).
    
    Key principles:
    - Buy companies with strong revenue/earnings growth
    - Focus on future potential, not just current value
    - PEG ratio < 1.5 (growth-adjusted valuation)
    - Look for expanding markets and market share gains
    """
    
    def get_strategy_name(self) -> str:
        return "Growth Investing"
    
    def get_timeframe(self) -> str:
        return "1-5 years"
    
    def evaluate(
        self,
        ticker: str,
        market_data: Dict[str, Any],
        fundamental_data: Dict[str, Any],
        technical_data: Dict[str, Any],
        additional_data: Optional[Dict[str, Any]] = None
    ) -> StrategyResult:
        """
        Evaluate stock using growth investing principles.
        """
        # Validate data
        if not self.validate_data(market_data, fundamental_data, technical_data):
            return StrategyResult(
                recommendation=Recommendation.WAIT,
                confidence=0,
                reasoning="Insufficient data for growth analysis",
                strategy_name=self.get_strategy_name()
            )
        
        # Extract key metrics
        current_price = extract_metric(market_data, "current_price", 0.0)
        pe_ratio = extract_metric(fundamental_data, "pe_ratio") or extract_metric(fundamental_data, "Trailing P/E")
        revenue_growth = extract_metric(fundamental_data, "revenue_growth") or extract_metric(fundamental_data, "Revenue Growth")
        earnings_growth = extract_metric(fundamental_data, "earnings_growth") or extract_metric(fundamental_data, "Earnings Growth")
        roe = extract_metric(fundamental_data, "roe") or extract_metric(fundamental_data, "ROE")
        
        # Calculate PEG ratio
        peg_ratio = None
        if pe_ratio and earnings_growth:
            peg_ratio = calculate_peg_ratio(pe_ratio, earnings_growth / 100 if earnings_growth > 1 else earnings_growth)
        
        # Score the investment
        score = 50  # Neutral baseline
        reasons = []
        risks = []
        key_metrics = {
            "current_price": current_price,
            "pe_ratio": pe_ratio,
            "peg_ratio": peg_ratio,
            "revenue_growth": revenue_growth,
            "earnings_growth": earnings_growth,
            "roe": roe,
        }
        
        # Revenue growth scoring
        if revenue_growth:
            if revenue_growth > 0.20:  # 20%+
                score += 25
                reasons.append(f"Strong revenue growth ({revenue_growth:.1%})")
            elif revenue_growth > 0.10:  # 10-20%
                score += 15
                reasons.append(f"Good revenue growth ({revenue_growth:.1%})")
            elif revenue_growth > 0.05:  # 5-10%
                score += 5
                reasons.append(f"Moderate revenue growth ({revenue_growth:.1%})")
            elif revenue_growth < 0:
                score -= 20
                reasons.append("Declining revenue (concern)")
                risks.append("Negative revenue growth indicates shrinking business")
        
        # Earnings growth scoring
        if earnings_growth:
            if earnings_growth > 0.25:  # 25%+
                score += 20
                reasons.append(f"Strong earnings growth ({earnings_growth:.1%})")
            elif earnings_growth > 0.15:  # 15-25%
                score += 10
                reasons.append(f"Good earnings growth ({earnings_growth:.1%})")
            elif earnings_growth < 0:
                score -= 15
                reasons.append("Declining earnings (concern)")
                risks.append("Negative earnings growth indicates profitability issues")
        
        # PEG ratio scoring
        if peg_ratio:
            if peg_ratio < 1.0:
                score += 20
                reasons.append(f"Excellent PEG ratio ({peg_ratio:.2f}) - growth at reasonable price")
            elif peg_ratio < 1.5:
                score += 10
                reasons.append(f"Good PEG ratio ({peg_ratio:.2f})")
            elif peg_ratio > 2.0:
                score -= 15
                reasons.append(f"High PEG ratio ({peg_ratio:.2f}) - growth may be overpriced")
                risks.append("High PEG ratio suggests overvaluation relative to growth")
        
        # P/E ratio scoring (more lenient for growth stocks)
        if pe_ratio:
            if pe_ratio < 30:
                score += 10
                reasons.append(f"Reasonable P/E for growth stock ({pe_ratio:.1f})")
            elif pe_ratio > 60:
                score -= 10
                reasons.append(f"High P/E ratio ({pe_ratio:.1f}) - premium valuation")
                risks.append("Very high P/E ratio increases valuation risk")
        
        # ROE scoring
        if roe:
            if roe > 0.20:  # 20%
                score += 15
                reasons.append(f"Strong ROE ({roe:.1%})")
            elif roe < 0.10:  # 10%
                score -= 10
                reasons.append(f"Low ROE ({roe:.1%})")
                risks.append("Low return on equity indicates inefficient capital use")
        
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
        
        # Calculate target price (based on growth projections)
        target_price = None
        if current_price > 0 and earnings_growth and earnings_growth > 0:
            # Simple projection: assume earnings grow at current rate for 3 years
            growth_multiplier = (1 + min(earnings_growth, 0.50)) ** 3  # Cap at 50% growth
            target_price = current_price * min(growth_multiplier, 2.0)  # Cap at 2x
        
        return StrategyResult(
            recommendation=recommendation,
            confidence=confidence,
            reasoning=format_reasoning(reasons),
            entry_price=current_price if current_price > 0 else None,
            target_price=target_price,
            holding_period="1-5 years",
            key_metrics=key_metrics,
            risks=risks,
            strategy_name=self.get_strategy_name()
        )

