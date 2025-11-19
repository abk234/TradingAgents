"""
Value Investing Strategy (Buffett-style)

Focuses on intrinsic value, margin of safety, economic moat, and management quality.
"""

from typing import Dict, Any, Optional
import logging

from .base import InvestmentStrategy, StrategyResult, Recommendation
from .utils import (
    safe_float,
    extract_metric,
    calculate_margin_of_safety,
    normalize_confidence,
    format_reasoning,
)

logger = logging.getLogger(__name__)


class ValueStrategy(InvestmentStrategy):
    """
    Value investing strategy (Buffett-style).
    
    Key principles:
    - Buy undervalued stocks (price < intrinsic value)
    - Focus on fundamental analysis
    - Long-term holding (5-10 years)
    - Margin of safety (30%+ discount preferred)
    - Economic moat analysis
    - Management quality assessment
    """
    
    def get_strategy_name(self) -> str:
        return "Value Investing"
    
    def get_timeframe(self) -> str:
        return "5-10 years"
    
    def evaluate(
        self,
        ticker: str,
        market_data: Dict[str, Any],
        fundamental_data: Dict[str, Any],
        technical_data: Dict[str, Any],
        additional_data: Optional[Dict[str, Any]] = None
    ) -> StrategyResult:
        """
        Evaluate stock using value investing principles.
        """
        # Validate data
        if not self.validate_data(market_data, fundamental_data, technical_data):
            return StrategyResult(
                recommendation=Recommendation.WAIT,
                confidence=0,
                reasoning="Insufficient data for value analysis",
                strategy_name=self.get_strategy_name()
            )
        
        # Extract key metrics
        current_price = extract_metric(market_data, "current_price", 0.0)
        pe_ratio = extract_metric(fundamental_data, "pe_ratio") or extract_metric(fundamental_data, "Trailing P/E")
        pb_ratio = extract_metric(fundamental_data, "price_to_book") or extract_metric(fundamental_data, "Price to Book")
        debt_to_equity = extract_metric(fundamental_data, "debt_to_equity") or extract_metric(fundamental_data, "Debt to Equity")
        roe = extract_metric(fundamental_data, "roe") or extract_metric(fundamental_data, "ROE")
        revenue_growth = extract_metric(fundamental_data, "revenue_growth") or extract_metric(fundamental_data, "Revenue Growth")
        
        # Calculate intrinsic value (simplified - using P/E relative valuation)
        intrinsic_value = self._calculate_intrinsic_value(
            current_price=current_price,
            pe_ratio=pe_ratio,
            fundamental_data=fundamental_data
        )
        
        # Calculate margin of safety
        margin_of_safety = calculate_margin_of_safety(intrinsic_value, current_price) if intrinsic_value > 0 else 0
        
        # Assess economic moat (simplified)
        moat_score = self._assess_moat(fundamental_data)
        
        # Assess management quality (simplified)
        management_score = self._assess_management(fundamental_data)
        
        # Score the investment
        score = 50  # Neutral baseline
        reasons = []
        risks = []
        key_metrics = {
            "current_price": current_price,
            "intrinsic_value": intrinsic_value,
            "margin_of_safety": margin_of_safety,
            "pe_ratio": pe_ratio,
            "pb_ratio": pb_ratio,
            "debt_to_equity": debt_to_equity,
            "roe": roe,
            "moat_score": moat_score,
            "management_score": management_score,
        }
        
        # Valuation scoring
        if margin_of_safety > 30:
            score += 25
            reasons.append(f"Strong margin of safety ({margin_of_safety:.1f}% discount)")
        elif margin_of_safety > 20:
            score += 15
            reasons.append(f"Good margin of safety ({margin_of_safety:.1f}% discount)")
        elif margin_of_safety > 10:
            score += 5
            reasons.append(f"Moderate margin of safety ({margin_of_safety:.1f}% discount)")
        elif margin_of_safety < 0:
            score -= 20
            reasons.append(f"Overvalued ({abs(margin_of_safety):.1f}% premium)")
            risks.append("Stock is overvalued relative to intrinsic value")
        
        # P/E ratio scoring
        if pe_ratio:
            if pe_ratio < 15:
                score += 15
                reasons.append(f"Low P/E ratio ({pe_ratio:.1f}) indicates value")
            elif pe_ratio < 25:
                score += 5
                reasons.append(f"Reasonable P/E ratio ({pe_ratio:.1f})")
            elif pe_ratio > 50:
                score -= 15
                reasons.append(f"High P/E ratio ({pe_ratio:.1f}) indicates premium valuation")
                risks.append("High P/E ratio suggests overvaluation")
        
        # Balance sheet strength
        if debt_to_equity is not None:
            if debt_to_equity < 0.5:
                score += 10
                reasons.append("Strong balance sheet (low debt)")
            elif debt_to_equity > 2.0:
                score -= 10
                reasons.append("High leverage (risk)")
                risks.append("High debt-to-equity ratio increases financial risk")
        
        # ROE scoring
        if roe:
            if roe > 0.15:  # 15%
                score += 10
                reasons.append(f"Strong ROE ({roe:.1%})")
            elif roe < 0.05:  # 5%
                score -= 10
                reasons.append(f"Low ROE ({roe:.1%})")
                risks.append("Low return on equity indicates poor profitability")
        
        # Moat scoring
        if moat_score > 70:
            score += 15
            reasons.append(f"Strong economic moat (score: {moat_score}/100)")
        elif moat_score < 50:
            score -= 10
            reasons.append(f"Weak economic moat (score: {moat_score}/100)")
            risks.append("Weak competitive advantages may not be sustainable")
        
        # Management scoring
        if management_score > 70:
            score += 10
            reasons.append(f"Good management quality (score: {management_score}/100)")
        elif management_score < 50:
            score -= 5
            reasons.append(f"Management concerns (score: {management_score}/100)")
        
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
        
        # Calculate target price (20% above intrinsic value for long-term)
        target_price = intrinsic_value * 1.20 if intrinsic_value > 0 else None
        
        return StrategyResult(
            recommendation=recommendation,
            confidence=confidence,
            reasoning=format_reasoning(reasons),
            entry_price=current_price if current_price > 0 else None,
            target_price=target_price,
            holding_period="5-10 years",
            key_metrics=key_metrics,
            risks=risks,
            strategy_name=self.get_strategy_name()
        )
    
    def _calculate_intrinsic_value(
        self,
        current_price: float,
        pe_ratio: Optional[float],
        fundamental_data: Dict[str, Any]
    ) -> float:
        """
        Calculate intrinsic value using simplified method.
        
        Uses relative valuation (P/E vs sector/historical average).
        In a full implementation, this would use DCF or owner earnings model.
        """
        if current_price <= 0:
            return 0.0
        
        # Simplified: Assume fair P/E is 20 (can be enhanced with sector/historical data)
        fair_pe = 20.0
        
        if pe_ratio and pe_ratio > 0:
            # Intrinsic value = current_price * (fair_pe / current_pe)
            intrinsic_value = current_price * (fair_pe / pe_ratio)
        else:
            # If no P/E, use current price as baseline
            intrinsic_value = current_price * 0.8  # Assume 20% discount
        
        return intrinsic_value
    
    def _assess_moat(self, fundamental_data: Dict[str, Any]) -> float:
        """
        Assess economic moat strength (0-100).
        
        Simplified assessment based on:
        - Profit margins (high = moat)
        - ROE (high = moat)
        - Market position (would need additional data)
        """
        score = 50  # Neutral
        
        # Check profit margins
        profit_margin = extract_metric(fundamental_data, "profit_margin") or extract_metric(fundamental_data, "Profit Margin")
        if profit_margin:
            if profit_margin > 0.20:  # 20%
                score += 20
            elif profit_margin > 0.10:  # 10%
                score += 10
            elif profit_margin < 0.05:  # 5%
                score -= 10
        
        # Check ROE
        roe = extract_metric(fundamental_data, "roe") or extract_metric(fundamental_data, "ROE")
        if roe:
            if roe > 0.20:  # 20%
                score += 20
            elif roe > 0.15:  # 15%
                score += 10
            elif roe < 0.10:  # 10%
                score -= 10
        
        return max(0, min(100, score))
    
    def _assess_management(self, fundamental_data: Dict[str, Any]) -> float:
        """
        Assess management quality (0-100).
        
        Simplified assessment based on:
        - Capital allocation (ROE trends)
        - Financial health (debt management)
        - Profitability consistency
        """
        score = 50  # Neutral
        
        # Check ROE (proxy for capital allocation)
        roe = extract_metric(fundamental_data, "roe") or extract_metric(fundamental_data, "ROE")
        if roe and roe > 0.15:
            score += 20
        
        # Check debt management
        debt_to_equity = extract_metric(fundamental_data, "debt_to_equity") or extract_metric(fundamental_data, "Debt to Equity")
        if debt_to_equity is not None and debt_to_equity < 1.0:
            score += 15
        
        # Check profitability
        profit_margin = extract_metric(fundamental_data, "profit_margin") or extract_metric(fundamental_data, "Profit Margin")
        if profit_margin and profit_margin > 0.10:
            score += 15
        
        return max(0, min(100, score))

