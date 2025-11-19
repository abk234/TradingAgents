"""
Recommendation Aligner Utility

Compares recommendations from different systems (Screener, Strategies, Sector Analysis)
to identify alignment and discrepancies. Helps users understand when systems agree/disagree.
"""

from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RecommendationType(Enum):
    """Types of recommendations from different systems."""
    BUY = "BUY"
    STRONG_BUY = "STRONG BUY"
    HOLD = "HOLD"
    WAIT = "WAIT"
    NEUTRAL = "NEUTRAL"
    SELL = "SELL"
    STRONG_SELL = "STRONG SELL"


class AlignmentLevel(Enum):
    """Level of alignment between systems."""
    STRONG_ALIGNMENT = "STRONG_ALIGNMENT"  # All systems agree (BUY/BUY/BUY)
    MODERATE_ALIGNMENT = "MODERATE_ALIGNMENT"  # Most systems agree (BUY/BUY/HOLD)
    WEAK_ALIGNMENT = "WEAK_ALIGNMENT"  # Some agreement (BUY/HOLD/WAIT)
    NO_ALIGNMENT = "NO_ALIGNMENT"  # Systems disagree (BUY/HOLD/SELL)
    CONFLICT = "CONFLICT"  # Direct conflict (BUY/SELL)


class RecommendationAligner:
    """
    Aligns and compares recommendations from different systems.
    
    Helps users understand:
    - When screener (technical) and strategies (fundamental) agree
    - When they disagree and why
    - What action to take based on alignment
    """
    
    # Map recommendation strings to normalized types
    RECOMMENDATION_MAP = {
        "STRONG BUY": RecommendationType.STRONG_BUY,
        "BUY": RecommendationType.BUY,
        "BUY DIP": RecommendationType.BUY,
        "ACCUMULATION": RecommendationType.BUY,
        "BUY (Below VAL)": RecommendationType.BUY,
        "HOLD": RecommendationType.HOLD,
        "NEUTRAL": RecommendationType.NEUTRAL,
        "WAIT": RecommendationType.WAIT,
        "BREAKOUT IMMINENT": RecommendationType.WAIT,
        "SELL": RecommendationType.SELL,
        "STRONG SELL": RecommendationType.STRONG_SELL,
        "DISTRIBUTION": RecommendationType.SELL,
        "SELL RALLY": RecommendationType.SELL,
    }
    
    def __init__(self):
        """Initialize recommendation aligner."""
        pass
    
    def align_recommendations(
        self,
        screener_recommendation: Optional[str],
        strategy_consensus: Optional[str],
        sector_strength: Optional[float] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Align recommendations from different systems.
        
        Args:
            screener_recommendation: Recommendation from screener (technical)
            strategy_consensus: Consensus recommendation from strategies (fundamental)
            sector_strength: Sector strength score (0-100)
            additional_context: Additional context (e.g., priority_score, RSI, etc.)
        
        Returns:
            Dictionary with alignment analysis:
            {
                "alignment_level": AlignmentLevel,
                "screener_type": RecommendationType,
                "strategy_type": RecommendationType,
                "interpretation": str,
                "action": str,
                "confidence": float,  # 0-1
                "warnings": List[str],
                "insights": List[str]
            }
        """
        # Normalize recommendations
        screener_type = self._normalize_recommendation(screener_recommendation)
        strategy_type = self._normalize_recommendation(strategy_consensus)
        
        # Determine alignment level
        alignment_level = self._determine_alignment(screener_type, strategy_type)
        
        # Generate interpretation
        interpretation = self._generate_interpretation(
            screener_type, strategy_type, sector_strength, alignment_level
        )
        
        # Generate action recommendation
        action = self._generate_action(screener_type, strategy_type, alignment_level)
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            screener_type, strategy_type, sector_strength, alignment_level
        )
        
        # Generate warnings
        warnings = self._generate_warnings(
            screener_type, strategy_type, sector_strength, additional_context
        )
        
        # Generate insights
        insights = self._generate_insights(
            screener_type, strategy_type, sector_strength, alignment_level
        )
        
        return {
            "alignment_level": alignment_level.value,
            "screener_recommendation": screener_recommendation,
            "screener_type": screener_type.value if screener_type else None,
            "strategy_consensus": strategy_consensus,
            "strategy_type": strategy_type.value if strategy_type else None,
            "sector_strength": sector_strength,
            "interpretation": interpretation,
            "action": action,
            "confidence": confidence,
            "warnings": warnings,
            "insights": insights,
        }
    
    def _normalize_recommendation(self, recommendation: Optional[str]) -> Optional[RecommendationType]:
        """Normalize recommendation string to RecommendationType."""
        if not recommendation:
            return None
        
        # Try exact match first
        rec_upper = recommendation.upper().strip()
        if rec_upper in self.RECOMMENDATION_MAP:
            return self.RECOMMENDATION_MAP[rec_upper]
        
        # Try partial matches
        for key, rec_type in self.RECOMMENDATION_MAP.items():
            if key.upper() in rec_upper or rec_upper in key.upper():
                return rec_type
        
        # Default mapping based on keywords
        if "BUY" in rec_upper and "STRONG" in rec_upper:
            return RecommendationType.STRONG_BUY
        elif "BUY" in rec_upper:
            return RecommendationType.BUY
        elif "SELL" in rec_upper and "STRONG" in rec_upper:
            return RecommendationType.STRONG_SELL
        elif "SELL" in rec_upper:
            return RecommendationType.SELL
        elif "WAIT" in rec_upper:
            return RecommendationType.WAIT
        elif "NEUTRAL" in rec_upper:
            return RecommendationType.NEUTRAL
        elif "HOLD" in rec_upper:
            return RecommendationType.HOLD
        
        return None
    
    def _determine_alignment(
        self,
        screener_type: Optional[RecommendationType],
        strategy_type: Optional[RecommendationType]
    ) -> AlignmentLevel:
        """Determine alignment level between screener and strategy recommendations."""
        if not screener_type or not strategy_type:
            return AlignmentLevel.NO_ALIGNMENT
        
        # Strong alignment: Both BUY or both SELL
        if screener_type == strategy_type:
            return AlignmentLevel.STRONG_ALIGNMENT
        
        # Both bullish (STRONG_BUY or BUY)
        if (screener_type in [RecommendationType.STRONG_BUY, RecommendationType.BUY] and
            strategy_type in [RecommendationType.STRONG_BUY, RecommendationType.BUY]):
            return AlignmentLevel.STRONG_ALIGNMENT
        
        # Both bearish (STRONG_SELL or SELL)
        if (screener_type in [RecommendationType.STRONG_SELL, RecommendationType.SELL] and
            strategy_type in [RecommendationType.STRONG_SELL, RecommendationType.SELL]):
            return AlignmentLevel.STRONG_ALIGNMENT
        
        # Direct conflict: BUY vs SELL
        if ((screener_type in [RecommendationType.STRONG_BUY, RecommendationType.BUY] and
             strategy_type in [RecommendationType.STRONG_SELL, RecommendationType.SELL]) or
            (screener_type in [RecommendationType.STRONG_SELL, RecommendationType.SELL] and
             strategy_type in [RecommendationType.STRONG_BUY, RecommendationType.BUY])):
            return AlignmentLevel.CONFLICT
        
        # Moderate alignment: BUY/HOLD or SELL/HOLD
        if (screener_type == RecommendationType.BUY and strategy_type == RecommendationType.HOLD) or \
           (screener_type == RecommendationType.HOLD and strategy_type == RecommendationType.BUY) or \
           (screener_type == RecommendationType.SELL and strategy_type == RecommendationType.HOLD) or \
           (screener_type == RecommendationType.HOLD and strategy_type == RecommendationType.SELL):
            return AlignmentLevel.MODERATE_ALIGNMENT
        
        # Weak alignment: BUY/WAIT or SELL/WAIT
        if (screener_type == RecommendationType.BUY and strategy_type == RecommendationType.WAIT) or \
           (screener_type == RecommendationType.WAIT and strategy_type == RecommendationType.BUY):
            return AlignmentLevel.WEAK_ALIGNMENT
        
        # Default: no alignment
        return AlignmentLevel.NO_ALIGNMENT
    
    def _generate_interpretation(
        self,
        screener_type: Optional[RecommendationType],
        strategy_type: Optional[RecommendationType],
        sector_strength: Optional[float],
        alignment_level: AlignmentLevel
    ) -> str:
        """Generate human-readable interpretation of alignment."""
        if alignment_level == AlignmentLevel.STRONG_ALIGNMENT:
            if screener_type == RecommendationType.BUY:
                return "Strong buy signal: Both technical (screener) and fundamental (strategies) analysis agree this is a BUY opportunity."
            elif screener_type == RecommendationType.SELL:
                return "Strong sell signal: Both technical and fundamental analysis agree this stock should be sold."
        
        if alignment_level == AlignmentLevel.CONFLICT:
            return "⚠️ CONFLICT: Technical analysis suggests BUY but fundamental analysis suggests SELL (or vice versa). This indicates mixed signals - proceed with caution."
        
        if alignment_level == AlignmentLevel.MODERATE_ALIGNMENT:
            if screener_type == RecommendationType.BUY and strategy_type == RecommendationType.HOLD:
                return "Technical analysis shows BUY signal, but fundamental analysis is neutral (HOLD). Good short-term opportunity, but fundamentals don't strongly support long-term hold."
            elif screener_type == RecommendationType.HOLD and strategy_type == RecommendationType.BUY:
                return "Fundamental analysis suggests BUY, but technical indicators are neutral. Good long-term value, but timing may not be optimal."
        
        if alignment_level == AlignmentLevel.WEAK_ALIGNMENT:
            return "Weak alignment: Technical and fundamental analysis show different signals. Consider waiting for clearer signals or deeper analysis."
        
        return "No clear alignment: Systems show different recommendations. Review individual analysis details."
    
    def _generate_action(
        self,
        screener_type: Optional[RecommendationType],
        strategy_type: Optional[RecommendationType],
        alignment_level: AlignmentLevel
    ) -> str:
        """Generate actionable recommendation based on alignment."""
        if alignment_level == AlignmentLevel.STRONG_ALIGNMENT:
            if screener_type == RecommendationType.BUY:
                return "✅ STRONG BUY - Both systems agree. Consider entering position."
            elif screener_type == RecommendationType.SELL:
                return "❌ STRONG SELL - Both systems agree. Consider exiting position."
        
        if alignment_level == AlignmentLevel.CONFLICT:
            return "⚠️ WAIT - Systems conflict. Do not trade until signals align or conduct deeper analysis."
        
        if alignment_level == AlignmentLevel.MODERATE_ALIGNMENT:
            if screener_type == RecommendationType.BUY:
                return "🟡 CAUTIOUS BUY - Technical signal present, but fundamentals neutral. Consider smaller position size."
            else:
                return "🟡 CAUTIOUS HOLD - Fundamentals positive, but technical timing not optimal. Wait for better entry."
        
        if alignment_level == AlignmentLevel.WEAK_ALIGNMENT:
            return "⏸️ WAIT - Weak signals. Monitor for stronger alignment before taking action."
        
        return "❓ REVIEW - No clear action. Review detailed analysis from each system."
    
    def _calculate_confidence(
        self,
        screener_type: Optional[RecommendationType],
        strategy_type: Optional[RecommendationType],
        sector_strength: Optional[float],
        alignment_level: AlignmentLevel
    ) -> float:
        """Calculate confidence score (0-1) based on alignment."""
        base_confidence = {
            AlignmentLevel.STRONG_ALIGNMENT: 0.85,
            AlignmentLevel.MODERATE_ALIGNMENT: 0.60,
            AlignmentLevel.WEAK_ALIGNMENT: 0.40,
            AlignmentLevel.NO_ALIGNMENT: 0.25,
            AlignmentLevel.CONFLICT: 0.15,
        }.get(alignment_level, 0.5)
        
        # Adjust for sector strength
        if sector_strength is not None:
            if sector_strength > 50:
                base_confidence += 0.10
            elif sector_strength < 30:
                base_confidence -= 0.10
        
        return max(0.0, min(1.0, base_confidence))
    
    def _generate_warnings(
        self,
        screener_type: Optional[RecommendationType],
        strategy_type: Optional[RecommendationType],
        sector_strength: Optional[float],
        additional_context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate warnings based on recommendations and context."""
        warnings = []
        
        # Conflict warning
        if screener_type and strategy_type:
            if (screener_type in [RecommendationType.BUY, RecommendationType.STRONG_BUY] and
                strategy_type in [RecommendationType.SELL, RecommendationType.STRONG_SELL]):
                warnings.append("⚠️ Direct conflict: Technical BUY vs Fundamental SELL - high risk")
            elif (screener_type in [RecommendationType.SELL, RecommendationType.STRONG_SELL] and
                  strategy_type in [RecommendationType.BUY, RecommendationType.STRONG_BUY]):
                warnings.append("⚠️ Direct conflict: Technical SELL vs Fundamental BUY - high risk")
        
        # Sector weakness warning
        if sector_strength is not None and sector_strength < 25:
            warnings.append("⚠️ Sector strength is weak - consider sector-wide risks")
        
        # Missing data warnings
        if not screener_type:
            warnings.append("⚠️ Screener recommendation missing - technical analysis incomplete")
        if not strategy_type:
            warnings.append("⚠️ Strategy consensus missing - fundamental analysis incomplete")
        
        return warnings
    
    def _generate_insights(
        self,
        screener_type: Optional[RecommendationType],
        strategy_type: Optional[RecommendationType],
        sector_strength: Optional[float],
        alignment_level: AlignmentLevel
    ) -> List[str]:
        """Generate insights based on alignment."""
        insights = []
        
        if alignment_level == AlignmentLevel.STRONG_ALIGNMENT:
            insights.append("✅ High confidence: Both technical and fundamental analysis align")
            if screener_type == RecommendationType.BUY:
                insights.append("💡 Consider: This is a strong opportunity with both short-term (technical) and long-term (fundamental) support")
        
        if alignment_level == AlignmentLevel.MODERATE_ALIGNMENT:
            if screener_type == RecommendationType.BUY:
                insights.append("💡 Technical signal suggests good entry timing, but fundamentals are neutral")
                insights.append("💡 Consider: This may be a short-term trading opportunity rather than long-term investment")
            else:
                insights.append("💡 Fundamentals are positive, but technical timing is not optimal")
                insights.append("💡 Consider: Wait for technical confirmation or use dollar-cost averaging")
        
        if alignment_level == AlignmentLevel.CONFLICT:
            insights.append("💡 Conflict suggests: Market may be in transition or stock has mixed characteristics")
            insights.append("💡 Consider: Wait for clearer signals or conduct deeper analysis before trading")
        
        if sector_strength is not None:
            if sector_strength > 50:
                insights.append(f"📈 Sector strength is strong ({sector_strength:.1f}%) - favorable sector tailwinds")
            elif sector_strength < 30:
                insights.append(f"📉 Sector strength is weak ({sector_strength:.1f}%) - consider sector headwinds")
        
        return insights


def align_stock_recommendations(
    ticker: str,
    screener_recommendation: Optional[str],
    strategy_consensus: Optional[str],
    sector_strength: Optional[float] = None,
    additional_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to align recommendations for a stock.
    
    Args:
        ticker: Stock symbol
        screener_recommendation: Screener recommendation
        strategy_consensus: Strategy consensus recommendation
        sector_strength: Sector strength score
        additional_context: Additional context
        
    Returns:
        Alignment analysis dictionary
    """
    aligner = RecommendationAligner()
    result = aligner.align_recommendations(
        screener_recommendation=screener_recommendation,
        strategy_consensus=strategy_consensus,
        sector_strength=sector_strength,
        additional_context=additional_context
    )
    result["ticker"] = ticker
    return result

