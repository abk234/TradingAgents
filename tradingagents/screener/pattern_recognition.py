"""
Pattern Recognition Module

Identifies high-probability trading patterns by combining multiple technical indicators.
Patterns are scored for reliability and provide actionable trading signals.
"""

from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class PatternSignal:
    """Pattern detection result"""
    pattern_name: str
    signal_type: str  # 'BUY', 'SELL', 'WAIT', 'BREAKOUT'
    probability: float  # 0.0 to 1.0
    strength: str  # 'STRONG', 'MODERATE', 'WEAK'
    conditions_met: List[str]
    conditions_failed: List[str]
    reasoning: str
    score: int  # -10 to +10


class PatternRecognition:
    """Detect and score trading patterns from technical indicators."""

    @staticmethod
    def analyze_patterns(technical_signals: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze all patterns and return the strongest signal.

        Args:
            technical_signals: Dictionary of technical indicator values

        Returns:
            Dictionary with pattern analysis results
        """
        # Detect all patterns
        patterns = []

        # Pattern 1: Strong Buy
        strong_buy = PatternRecognition._detect_strong_buy(technical_signals)
        if strong_buy:
            patterns.append(strong_buy)

        # Pattern 2: Regular Buy
        buy = PatternRecognition._detect_buy(technical_signals)
        if buy:
            patterns.append(buy)

        # Pattern 3: Wait for Pullback
        wait = PatternRecognition._detect_wait_for_pullback(technical_signals)
        if wait:
            patterns.append(wait)

        # Pattern 4: Strong Sell
        strong_sell = PatternRecognition._detect_strong_sell(technical_signals)
        if strong_sell:
            patterns.append(strong_sell)

        # Pattern 5: Breakout Imminent
        breakout = PatternRecognition._detect_breakout_imminent(technical_signals)
        if breakout:
            patterns.append(breakout)

        # Pattern 6: Bullish Divergence Reversal
        divergence = PatternRecognition._detect_divergence_reversal(technical_signals)
        if divergence:
            patterns.append(divergence)

        # Find strongest pattern
        primary_pattern = None
        if patterns:
            # Sort by probability, then by score
            patterns.sort(key=lambda p: (p.probability, abs(p.score)), reverse=True)
            primary_pattern = patterns[0]

        # Calculate overall signal score
        overall_score = PatternRecognition._calculate_signal_score(technical_signals)

        return {
            'primary_pattern': primary_pattern,
            'all_patterns': patterns,
            'overall_score': overall_score,
            'overall_signal': PatternRecognition._score_to_signal(overall_score),
            'has_strong_signal': primary_pattern and primary_pattern.strength == 'STRONG' if primary_pattern else False
        }

    @staticmethod
    def _detect_strong_buy(signals: Dict[str, Any]) -> PatternSignal:
        """
        Detect STRONG BUY pattern.

        Required: ALL of these conditions
        - RSI < 35 (oversold)
        - Price < VWAP - 1% (below institutional benchmark)
        - Price near Pivot S1 or S2 (support level)
        - MACD bullish crossover (momentum turning)
        - Volume ratio > 1.3 (strong buying interest)
        - Price > MA 50 (still in uptrend)
        """
        conditions_met = []
        conditions_failed = []

        # Required conditions
        rsi = signals.get('rsi', 50)
        rsi_ok = rsi < 35
        if rsi_ok:
            conditions_met.append(f"RSI {rsi:.1f} < 35 (oversold)")
        else:
            conditions_failed.append(f"RSI {rsi:.1f} not oversold")

        vwap_dist = signals.get('vwap_distance_pct', 0)
        vwap_ok = vwap_dist < -1.0
        if vwap_ok:
            conditions_met.append(f"Price {vwap_dist:.1f}% below VWAP")
        else:
            conditions_failed.append(f"Price not significantly below VWAP ({vwap_dist:.1f}%)")

        pivot_zone = signals.get('pivot_zone', '')
        pivot_ok = pivot_zone in ['s1_to_s2', 'below_s2', 'pp_to_s1']
        if pivot_ok:
            conditions_met.append(f"Price in support zone ({pivot_zone})")
        else:
            conditions_failed.append(f"Price not in support zone ({pivot_zone})")

        macd_bullish = signals.get('macd_bullish_crossover', False)
        if macd_bullish:
            conditions_met.append("MACD bullish crossover")
        else:
            conditions_failed.append("No MACD bullish crossover")

        volume_ratio = signals.get('volume_ratio', 1.0)
        volume_ok = volume_ratio > 1.3
        if volume_ok:
            conditions_met.append(f"Volume {volume_ratio:.1f}x average")
        else:
            conditions_failed.append(f"Volume not elevated ({volume_ratio:.1f}x)")

        price_above_ma50 = signals.get('price_above_ma50', False)
        if price_above_ma50:
            conditions_met.append("Price above MA50 (uptrend intact)")
        else:
            conditions_failed.append("Price below MA50")

        # Calculate score and probability
        required_conditions = 6
        conditions_met_count = len(conditions_met)
        probability = conditions_met_count / required_conditions

        # Need at least 5/6 conditions for STRONG BUY
        if conditions_met_count >= 5:
            strength = 'STRONG' if conditions_met_count == 6 else 'MODERATE'

            # Optional enhancers
            if signals.get('rsi_bullish_divergence'):
                conditions_met.append("Bullish RSI divergence detected")
                probability = min(0.95, probability + 0.05)
            if signals.get('near_fib_support'):
                conditions_met.append("Near Fibonacci support level")
                probability = min(0.95, probability + 0.03)

            return PatternSignal(
                pattern_name='STRONG_BUY',
                signal_type='BUY',
                probability=probability,
                strength=strength,
                conditions_met=conditions_met,
                conditions_failed=conditions_failed,
                reasoning=f"Oversold + institutional support + momentum turning ({conditions_met_count}/6 conditions)",
                score=9 if conditions_met_count == 6 else 7
            )

        return None

    @staticmethod
    def _detect_buy(signals: Dict[str, Any]) -> PatternSignal:
        """
        Detect regular BUY pattern.

        Required: 3+ of these conditions
        - RSI 30-40 (approaching oversold)
        - Price < VWAP (below benchmark)
        - Price in pivot accumulation zone (S1 to PP)
        - Price near MA 20 or MA 50
        - Volume ratio > 1.0
        """
        conditions_met = []
        conditions_failed = []

        rsi = signals.get('rsi', 50)
        if 30 <= rsi <= 40:
            conditions_met.append(f"RSI {rsi:.1f} approaching oversold")
        else:
            conditions_failed.append(f"RSI {rsi:.1f} not in buy zone")

        vwap_below = signals.get('price_below_vwap', False)
        if vwap_below:
            vwap_dist = signals.get('vwap_distance_pct', 0)
            conditions_met.append(f"Price below VWAP ({vwap_dist:.1f}%)")
        else:
            conditions_failed.append("Price above VWAP")

        pivot_zone = signals.get('pivot_zone', '')
        if pivot_zone in ['pp_to_s1', 's1_to_s2']:
            conditions_met.append(f"Pivot accumulation zone ({pivot_zone})")
        else:
            conditions_failed.append(f"Not in accumulation zone ({pivot_zone})")

        # Near MA support
        near_ma = False
        if signals.get('price_above_ma20') and signals.get('price_above_ma50'):
            near_ma = True
            conditions_met.append("Price near MA support")
        else:
            conditions_failed.append("Not near MA support")

        volume_ratio = signals.get('volume_ratio', 0)
        if volume_ratio > 1.0:
            conditions_met.append(f"Healthy volume ({volume_ratio:.1f}x)")
        else:
            conditions_failed.append(f"Low volume ({volume_ratio:.1f}x)")

        # Need 3+ conditions
        if len(conditions_met) >= 3:
            probability = len(conditions_met) / 5  # 5 total possible conditions
            strength = 'MODERATE' if len(conditions_met) >= 4 else 'WEAK'

            return PatternSignal(
                pattern_name='BUY',
                signal_type='BUY',
                probability=probability,
                strength=strength,
                conditions_met=conditions_met,
                conditions_failed=conditions_failed,
                reasoning=f"Multiple buy signals aligning ({len(conditions_met)}/5 conditions)",
                score=5 if len(conditions_met) >= 4 else 3
            )

        return None

    @staticmethod
    def _detect_wait_for_pullback(signals: Dict[str, Any]) -> PatternSignal:
        """
        Detect WAIT FOR PULLBACK pattern.

        Conditions:
        - RSI > 65 (approaching overbought)
        - Price > VWAP + 2% (above institutional benchmark)
        - Price above Pivot R1
        """
        conditions_met = []

        rsi = signals.get('rsi', 50)
        if rsi > 65:
            conditions_met.append(f"RSI {rsi:.1f} elevated")

        vwap_dist = signals.get('vwap_distance_pct', 0)
        if vwap_dist > 2.0:
            conditions_met.append(f"Price {vwap_dist:.1f}% above VWAP (extended)")

        pivot_zone = signals.get('pivot_zone', '')
        if pivot_zone in ['r1_to_r2', 'above_r2']:
            conditions_met.append(f"Price at resistance ({pivot_zone})")

        # Need 2+ conditions
        if len(conditions_met) >= 2:
            probability = 0.65 if len(conditions_met) == 3 else 0.55

            return PatternSignal(
                pattern_name='WAIT_FOR_PULLBACK',
                signal_type='WAIT',
                probability=probability,
                strength='MODERATE',
                conditions_met=conditions_met,
                conditions_failed=[],
                reasoning=f"Price extended, wait for better entry ({len(conditions_met)} warning signs)",
                score=0  # Neutral
            )

        return None

    @staticmethod
    def _detect_strong_sell(signals: Dict[str, Any]) -> PatternSignal:
        """
        Detect STRONG SELL pattern.

        Required: ALL of these conditions
        - RSI > 75 (overbought)
        - Price > VWAP + 3% (way above institutional benchmark)
        - Bearish MACD crossover
        - Price at/above Pivot R2
        - Volume spike on down day
        """
        conditions_met = []
        conditions_failed = []

        rsi = signals.get('rsi', 50)
        rsi_ok = rsi > 75
        if rsi_ok:
            conditions_met.append(f"RSI {rsi:.1f} overbought")
        else:
            conditions_failed.append(f"RSI {rsi:.1f} not extremely overbought")

        vwap_dist = signals.get('vwap_distance_pct', 0)
        vwap_ok = vwap_dist > 3.0
        if vwap_ok:
            conditions_met.append(f"Price {vwap_dist:.1f}% above VWAP (extreme)")
        else:
            conditions_failed.append(f"Price not extremely extended ({vwap_dist:.1f}%)")

        macd_bearish = signals.get('macd_bearish_crossover', False)
        if macd_bearish:
            conditions_met.append("MACD bearish crossover")
        else:
            conditions_failed.append("No MACD bearish crossover")

        pivot_zone = signals.get('pivot_zone', '')
        pivot_ok = pivot_zone in ['above_r2', 'r1_to_r2']
        if pivot_ok:
            conditions_met.append(f"At resistance level ({pivot_zone})")
        else:
            conditions_failed.append(f"Not at strong resistance ({pivot_zone})")

        # Note: For volume spike on down day, we'd need price change data
        # For now, just check for volume spike
        volume_ratio = signals.get('volume_ratio', 1.0)
        volume_ok = volume_ratio > 1.5
        if volume_ok:
            conditions_met.append(f"Volume spike {volume_ratio:.1f}x")
        else:
            conditions_failed.append(f"No volume spike ({volume_ratio:.1f}x)")

        # Calculate score
        conditions_met_count = len(conditions_met)
        probability = conditions_met_count / 5

        # Need at least 4/5 conditions for STRONG SELL
        if conditions_met_count >= 4:
            strength = 'STRONG' if conditions_met_count == 5 else 'MODERATE'

            # Optional enhancers
            if signals.get('rsi_bearish_divergence'):
                conditions_met.append("Bearish RSI divergence detected")
                probability = min(0.95, probability + 0.05)

            return PatternSignal(
                pattern_name='STRONG_SELL',
                signal_type='SELL',
                probability=probability,
                strength=strength,
                conditions_met=conditions_met,
                conditions_failed=conditions_failed,
                reasoning=f"Overbought + extended + momentum failing ({conditions_met_count}/5 conditions)",
                score=-9 if conditions_met_count == 5 else -7
            )

        return None

    @staticmethod
    def _detect_breakout_imminent(signals: Dict[str, Any]) -> PatternSignal:
        """
        Detect BREAKOUT IMMINENT pattern.

        Required:
        - BB Squeeze detected (width percentile < 15%)
        - Squeeze strength > 0.6
        - Volume declining (< 0.8x) - quiet before storm
        """
        conditions_met = []
        conditions_failed = []

        bb_squeeze = signals.get('bb_squeeze_detected', False)
        squeeze_strength = signals.get('bb_squeeze_strength', 0)

        if bb_squeeze:
            conditions_met.append(f"BB Squeeze detected (strength {squeeze_strength:.2f})")
        else:
            conditions_failed.append("No BB Squeeze")

        if squeeze_strength > 0.6:
            conditions_met.append("Strong compression (strength > 0.6)")
        else:
            conditions_failed.append(f"Weak compression ({squeeze_strength:.2f})")

        volume_ratio = signals.get('volume_ratio', 1.0)
        if volume_ratio < 0.8:
            conditions_met.append(f"Low volume ({volume_ratio:.1f}x) - quiet consolidation")
        else:
            conditions_failed.append(f"Volume not declining ({volume_ratio:.1f}x)")

        # Need 2+ conditions
        if len(conditions_met) >= 2:
            probability = 0.75 if len(conditions_met) == 3 else 0.60

            # Check for bias direction
            trend_hint = ""
            if signals.get('price_above_vwap') and signals.get('pivot_zone', '').startswith('pp'):
                trend_hint = " (likely UP breakout)"
            elif signals.get('price_below_vwap') and signals.get('pivot_zone', '').startswith('pp'):
                trend_hint = " (likely DOWN breakout)"

            return PatternSignal(
                pattern_name='BREAKOUT_IMMINENT',
                signal_type='BREAKOUT',
                probability=probability,
                strength='MODERATE',
                conditions_met=conditions_met,
                conditions_failed=conditions_failed,
                reasoning=f"Volatility compression - major move coming{trend_hint}",
                score=0  # Neutral until direction confirmed
            )

        return None

    @staticmethod
    def _detect_divergence_reversal(signals: Dict[str, Any]) -> PatternSignal:
        """
        Detect DIVERGENCE REVERSAL pattern.

        Required:
        - Bullish RSI divergence (strength > 0.6)
        - Price near Pivot S1 or Fib 61.8% (support)
        - Volume declining on down days (exhaustion)
        """
        conditions_met = []
        conditions_failed = []

        # Check for divergence
        divergence_type = signals.get('rsi_divergence_type')
        divergence_strength = signals.get('rsi_divergence_strength', 0)

        if divergence_type == 'bullish' and divergence_strength > 0.6:
            conditions_met.append(f"Bullish RSI divergence (strength {divergence_strength:.2f})")
        elif divergence_type == 'bearish' and divergence_strength > 0.6:
            conditions_met.append(f"Bearish RSI divergence (strength {divergence_strength:.2f})")
        else:
            conditions_failed.append(f"No strong divergence ({divergence_type}, {divergence_strength:.2f})")
            return None  # Divergence is required

        # Check for support/resistance
        at_support = False
        pivot_zone = signals.get('pivot_zone', '')
        near_fib = signals.get('near_fib_support', False)

        if divergence_type == 'bullish':
            if pivot_zone in ['s1_to_s2', 'below_s2', 'pp_to_s1'] or near_fib:
                at_support = True
                conditions_met.append(f"At support level ({pivot_zone})")
            else:
                conditions_failed.append(f"Not at support ({pivot_zone})")
        else:  # bearish
            if pivot_zone in ['r1_to_r2', 'above_r2']:
                at_support = True
                conditions_met.append(f"At resistance level ({pivot_zone})")
            else:
                conditions_failed.append(f"Not at resistance ({pivot_zone})")

        # Check for volume exhaustion (declining volume)
        volume_ratio = signals.get('volume_ratio', 1.0)
        if volume_ratio < 0.9:
            conditions_met.append(f"Volume declining ({volume_ratio:.1f}x) - exhaustion")
        else:
            conditions_failed.append(f"Volume not showing exhaustion ({volume_ratio:.1f}x)")

        # Need divergence + at least 1 other condition
        if len(conditions_met) >= 2:
            probability = 0.75 if len(conditions_met) >= 3 else 0.65
            signal_type = 'BUY' if divergence_type == 'bullish' else 'SELL'
            score = 7 if divergence_type == 'bullish' else -7

            return PatternSignal(
                pattern_name=f'{divergence_type.upper()}_DIVERGENCE_REVERSAL',
                signal_type=signal_type,
                probability=probability,
                strength='STRONG' if len(conditions_met) >= 3 else 'MODERATE',
                conditions_met=conditions_met,
                conditions_failed=conditions_failed,
                reasoning=f"{divergence_type.capitalize()} reversal setup ({len(conditions_met)} confirmations)",
                score=score
            )

        return None

    @staticmethod
    def _calculate_signal_score(signals: Dict[str, Any]) -> int:
        """
        Calculate overall signal score from -10 (strong sell) to +10 (strong buy).

        Scoring system:
        +1 for each bullish indicator
        -1 for each bearish indicator
        0 for neutral
        """
        score = 0

        # RSI scoring
        rsi = signals.get('rsi', 50)
        if rsi < 30:
            score += 2  # Strong buy
        elif rsi < 40:
            score += 1  # Buy
        elif rsi > 70:
            score -= 2  # Strong sell
        elif rsi > 60:
            score -= 1  # Sell

        # VWAP scoring
        vwap_dist = signals.get('vwap_distance_pct', 0)
        if vwap_dist < -2.0:
            score += 2
        elif vwap_dist < -0.5:
            score += 1
        elif vwap_dist > 3.0:
            score -= 2
        elif vwap_dist > 1.0:
            score -= 1

        # Pivot zone scoring
        pivot_zone = signals.get('pivot_zone', '')
        if pivot_zone in ['below_s2', 's1_to_s2']:
            score += 2
        elif pivot_zone == 'pp_to_s1':
            score += 1
        elif pivot_zone == 'pp_to_r1':
            score += 0  # Neutral
        elif pivot_zone == 'r1_to_r2':
            score -= 1
        elif pivot_zone == 'above_r2':
            score -= 2

        # MACD scoring
        if signals.get('macd_bullish_crossover'):
            score += 1
        if signals.get('macd_bearish_crossover'):
            score -= 1

        # Volume scoring (confirmation)
        volume_ratio = signals.get('volume_ratio', 1.0)
        if volume_ratio > 1.5:
            # High volume confirms the direction
            if score > 0:
                score += 1  # Confirm bullish
            elif score < 0:
                score -= 1  # Confirm bearish

        # Divergence scoring
        if signals.get('rsi_bullish_divergence'):
            divergence_strength = signals.get('rsi_divergence_strength', 0)
            if divergence_strength > 0.7:
                score += 2
            elif divergence_strength > 0.5:
                score += 1
        if signals.get('rsi_bearish_divergence'):
            divergence_strength = signals.get('rsi_divergence_strength', 0)
            if divergence_strength > 0.7:
                score -= 2
            elif divergence_strength > 0.5:
                score -= 1

        # BB Squeeze (neutral but important)
        # Doesn't affect score but signals prepare

        # Clamp to -10 to +10
        return max(-10, min(10, score))

    @staticmethod
    def _score_to_signal(score: int) -> str:
        """Convert numerical score to signal string."""
        if score >= 7:
            return 'STRONG_BUY'
        elif score >= 4:
            return 'BUY'
        elif score >= 1:
            return 'WEAK_BUY'
        elif score == 0:
            return 'NEUTRAL'
        elif score >= -3:
            return 'WEAK_SELL'
        elif score >= -6:
            return 'SELL'
        else:
            return 'STRONG_SELL'
