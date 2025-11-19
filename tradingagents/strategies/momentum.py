"""
Momentum Trading Strategy

Focuses on price trends, technical indicators, and short-term momentum.
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


class MomentumStrategy(InvestmentStrategy):
    """
    Momentum trading strategy.
    
    Key principles:
    - "The trend is your friend" - buy rising stocks
    - Use technical indicators (RSI, MACD, moving averages)
    - Short-term holding (days to weeks)
    - Stop-losses and take-profits
    - Volume confirmation
    """
    
    def get_strategy_name(self) -> str:
        return "Momentum Trading"
    
    def get_timeframe(self) -> str:
        return "30-90 days"
    
    def evaluate(
        self,
        ticker: str,
        market_data: Dict[str, Any],
        fundamental_data: Dict[str, Any],
        technical_data: Dict[str, Any],
        additional_data: Optional[Dict[str, Any]] = None
    ) -> StrategyResult:
        """
        Evaluate stock using momentum trading principles.
        """
        # Validate data
        if not self.validate_data(market_data, fundamental_data, technical_data):
            return StrategyResult(
                recommendation=Recommendation.WAIT,
                confidence=0,
                reasoning="Insufficient data for momentum analysis",
                strategy_name=self.get_strategy_name()
            )
        
        # Extract technical metrics
        current_price = extract_metric(market_data, "current_price", 0.0)
        rsi = extract_metric(technical_data, "rsi") or extract_metric(technical_data, "RSI")
        ma_20 = extract_metric(technical_data, "ma_20") or extract_metric(technical_data, "MA_20")
        ma_50 = extract_metric(technical_data, "ma_50") or extract_metric(technical_data, "MA_50")
        macd = extract_metric(technical_data, "macd") or extract_metric(technical_data, "MACD")
        macd_signal = extract_metric(technical_data, "macd_signal") or extract_metric(technical_data, "MACD_Signal")
        volume_ratio = extract_metric(technical_data, "volume_ratio", 1.0)
        
        # Score the investment
        score = 50  # Neutral baseline
        reasons = []
        risks = []
        key_metrics = {
            "current_price": current_price,
            "rsi": rsi,
            "ma_20": ma_20,
            "ma_50": ma_50,
            "macd": macd,
            "volume_ratio": volume_ratio,
        }
        
        # RSI scoring (momentum)
        if rsi is not None:
            if 50 <= rsi <= 70:
                score += 20
                reasons.append(f"RSI favorable ({rsi:.1f}) - bullish momentum")
            elif 30 <= rsi < 50:
                score += 10
                reasons.append(f"RSI recovering ({rsi:.1f}) - momentum building")
            elif rsi > 70:
                score -= 15
                reasons.append(f"RSI overbought ({rsi:.1f}) - may reverse")
                risks.append("Overbought conditions suggest potential pullback")
            elif rsi < 30:
                score -= 10
                reasons.append(f"RSI oversold ({rsi:.1f}) - weak momentum")
        
        # Moving average scoring (trend)
        if current_price > 0 and ma_20 and ma_50:
            if current_price > ma_20 > ma_50:
                score += 25
                reasons.append("Price above both MAs - strong uptrend")
            elif current_price > ma_20:
                score += 10
                reasons.append("Price above 20-day MA - bullish")
            elif current_price < ma_20 < ma_50:
                score -= 20
                reasons.append("Price below both MAs - downtrend")
                risks.append("Downtrend indicates weak momentum")
        
        # MACD scoring (momentum confirmation)
        if macd is not None and macd_signal is not None:
            if macd > macd_signal:
                score += 15
                reasons.append("MACD bullish - momentum confirmed")
            elif macd < macd_signal:
                score -= 15
                reasons.append("MACD bearish - momentum fading")
                risks.append("Bearish MACD suggests momentum loss")
        
        # Volume confirmation
        if volume_ratio:
            if volume_ratio > 1.5:
                score += 15
                reasons.append(f"Strong volume ({volume_ratio:.1f}x average) - confirms move")
            elif volume_ratio < 0.7:
                score -= 10
                reasons.append(f"Low volume ({volume_ratio:.1f}x average) - weak confirmation")
                risks.append("Low volume suggests lack of conviction")
        
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
        
        # Calculate entry/exit prices
        entry_price = current_price if current_price > 0 else None
        
        # Stop loss (5-10% below entry)
        stop_loss = entry_price * 0.92 if entry_price else None
        
        # Target price (10-20% above entry)
        target_price = entry_price * 1.15 if entry_price else None
        
        return StrategyResult(
            recommendation=recommendation,
            confidence=confidence,
            reasoning=format_reasoning(reasons),
            entry_price=entry_price,
            target_price=target_price,
            stop_loss=stop_loss,
            holding_period="30-90 days",
            key_metrics=key_metrics,
            risks=risks,
            strategy_name=self.get_strategy_name()
        )

