# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Contrarian Investing Strategy

Focuses on buying when others fear (oversold conditions, negative sentiment).
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


class ContrarianStrategy(InvestmentStrategy):
    """
    Contrarian investing strategy.
    
    Key principles:
    - Buy when everyone is selling (fear)
    - Sell when everyone is buying (greed)
    - Focus on oversold conditions
    - Look for market overreactions
    - Value + sentiment combination
    """
    
    def get_strategy_name(self) -> str:
        return "Contrarian Investing"
    
    def get_timeframe(self) -> str:
        return "Months to years"
    
    def evaluate(
        self,
        ticker: str,
        market_data: Dict[str, Any],
        fundamental_data: Dict[str, Any],
        technical_data: Dict[str, Any],
        additional_data: Optional[Dict[str, Any]] = None
    ) -> StrategyResult:
        """
        Evaluate stock using contrarian investing principles.
        """
        # Validate data
        if not self.validate_data(market_data, fundamental_data, technical_data):
            return StrategyResult(
                recommendation=Recommendation.WAIT,
                confidence=0,
                reasoning="Insufficient data for contrarian analysis",
                strategy_name=self.get_strategy_name()
            )
        
        # Extract metrics
        current_price = extract_metric(market_data, "current_price", 0.0)
        week_52_high = extract_metric(market_data, "week_52_high") or extract_metric(market_data, "52_week_high")
        week_52_low = extract_metric(market_data, "week_52_low") or extract_metric(market_data, "52_week_low")
        rsi = extract_metric(technical_data, "rsi") or extract_metric(technical_data, "RSI")
        pe_ratio = extract_metric(fundamental_data, "pe_ratio") or extract_metric(fundamental_data, "Trailing P/E")
        
        # Get sentiment data
        news_data = additional_data.get("news_data", {}) if additional_data else {}
        sentiment = news_data.get("sentiment", 0.0)  # -1 to 1, negative = fear
        
        # Calculate price position
        pct_from_high = 0.0
        pct_from_low = 0.0
        if week_52_high and current_price:
            pct_from_high = ((week_52_high - current_price) / week_52_high) * 100
        if week_52_low and current_price:
            pct_from_low = ((current_price - week_52_low) / week_52_low) * 100
        
        # Score the investment
        score = 50  # Neutral baseline
        reasons = []
        risks = []
        key_metrics = {
            "current_price": current_price,
            "pct_from_52w_high": pct_from_high,
            "pct_from_52w_low": pct_from_low,
            "rsi": rsi,
            "pe_ratio": pe_ratio,
            "sentiment": sentiment,
        }
        
        # Oversold condition scoring (key for contrarian)
        if rsi is not None:
            if rsi < 30:
                score += 30
                reasons.append(f"RSI oversold ({rsi:.1f}) - fear-driven selling")
            elif rsi < 40:
                score += 15
                reasons.append(f"RSI approaching oversold ({rsi:.1f})")
            elif rsi > 70:
                score -= 20
                reasons.append(f"RSI overbought ({rsi:.1f}) - greed-driven buying")
                risks.append("Overbought conditions suggest overvaluation")
        
        # Price position scoring (pullback from highs)
        if pct_from_high > 20:
            score += 25
            reasons.append(f"Significant pullback from 52-week high ({pct_from_high:.1f}%)")
        elif pct_from_high > 10:
            score += 10
            reasons.append(f"Moderate pullback from 52-week high ({pct_from_high:.1f}%)")
        elif pct_from_high < 5:
            score -= 15
            reasons.append(f"Near 52-week high ({pct_from_high:.1f}% below) - not contrarian opportunity")
            risks.append("Stock near highs - not a contrarian buy")
        
        # Sentiment scoring (negative = opportunity)
        if sentiment < -0.3:  # Very negative
            score += 20
            reasons.append("Very negative sentiment - fear-driven selling")
        elif sentiment < -0.1:  # Negative
            score += 10
            reasons.append("Negative sentiment - potential overreaction")
        elif sentiment > 0.3:  # Very positive
            score -= 15
            reasons.append("Very positive sentiment - may be overbought")
            risks.append("High positive sentiment suggests overvaluation")
        
        # Valuation scoring (cheap = contrarian opportunity)
        if pe_ratio:
            if pe_ratio < 15:
                score += 15
                reasons.append(f"Low P/E ratio ({pe_ratio:.1f}) - value opportunity")
            elif pe_ratio > 50:
                score -= 10
                reasons.append(f"High P/E ratio ({pe_ratio:.1f}) - not contrarian")
        
        # Determine recommendation
        confidence = normalize_confidence(score, 0, 100)
        
        # Contrarian logic: BUY when oversold, SELL when overbought
        if score >= 70:
            recommendation = Recommendation.BUY
        elif score >= 50:
            recommendation = Recommendation.HOLD
        elif score >= 30:
            recommendation = Recommendation.WAIT
        else:
            recommendation = Recommendation.SELL
        
        # Calculate target price (mean reversion to fair value)
        target_price = None
        if current_price > 0 and week_52_high:
            # Target: halfway between current and 52-week high (mean reversion)
            target_price = (current_price + week_52_high) / 2
        
        return StrategyResult(
            recommendation=recommendation,
            confidence=confidence,
            reasoning=format_reasoning(reasons),
            entry_price=current_price if current_price > 0 else None,
            target_price=target_price,
            holding_period="Months to years",
            key_metrics=key_metrics,
            risks=risks,
            strategy_name=self.get_strategy_name()
        )

