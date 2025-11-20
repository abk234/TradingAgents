"""
Priority Scorer Module

Calculates priority scores for tickers based on technical and fundamental signals.
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class PriorityScorer:
    """Calculate priority scores for screening."""

    # Default scoring weights
    DEFAULT_WEIGHTS = {
        'technical': 0.40,
        'fundamental': 0.25,
        'volume': 0.20,
        'momentum': 0.15,
    }

    # Technical scoring rules
    TECHNICAL_RULES = {
        'rsi_oversold': 15,  # RSI < 30
        'rsi_optimal': 10,   # RSI 30-50
        'rsi_overbought': -10,  # RSI > 70 (penalty)
        'near_bb_lower': 10,  # Near lower Bollinger Band
        'near_bb_upper': -5,  # Near upper Bollinger Band (overbought)
        'macd_bullish_crossover': 15,
        'macd_bearish_crossover': -15,  # MACD bearish (penalty)
        'price_above_ma20': 5,
        'price_above_ma50': 5,
        'ma20_above_ma50': 10,
        'price_below_ma20': -5,  # Below MA20 (penalty)
        'price_below_ma50': -10,  # Below MA50 (penalty)
    }

    # Volume scoring rules
    VOLUME_RULES = {
        'volume_spike_high': 20,  # >2x average
        'volume_spike_med': 10,   # 1.5-2x average
        'volume_normal': 5,       # >average
    }

    # Momentum scoring rules
    MOMENTUM_RULES = {
        'strong_positive': 15,   # >5% in 20 days
        'positive': 10,          # 0-5% in 20 days
        'negative': -5,          # <0% in 20 days
    }

    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize priority scorer.

        Args:
            weights: Custom scoring weights (optional)
        """
        self.weights = weights or self.DEFAULT_WEIGHTS

    def score_technical(self, signals: Dict[str, Any]) -> int:
        """
        Score technical indicators.

        Args:
            signals: Dictionary of technical signals

        Returns:
            Technical score (0-100)
        """
        score = 50  # Start with neutral baseline (was 0, which biased toward low scores)

        # RSI scoring
        rsi = signals.get('rsi')
        if rsi is not None:
            if signals.get('rsi_oversold'):
                score += self.TECHNICAL_RULES['rsi_oversold']
            elif 30 <= rsi <= 50:
                score += self.TECHNICAL_RULES['rsi_optimal']
            elif signals.get('rsi_overbought'):
                score += self.TECHNICAL_RULES['rsi_overbought']  # Penalty

        # Bollinger Bands
        if signals.get('near_bb_lower'):
            score += self.TECHNICAL_RULES['near_bb_lower']
        elif signals.get('near_bb_upper'):
            score += self.TECHNICAL_RULES['near_bb_upper']  # Penalty for overbought

        # MACD - CRITICAL FIX: Penalize bearish signals
        if signals.get('macd_bullish_crossover'):
            score += self.TECHNICAL_RULES['macd_bullish_crossover']
        elif signals.get('macd_bearish_crossover'):
            score += self.TECHNICAL_RULES['macd_bearish_crossover']  # Penalty for bearish

        # Moving averages
        if signals.get('price_above_ma20'):
            score += self.TECHNICAL_RULES['price_above_ma20']
        elif signals.get('price_below_ma20'):
            score += self.TECHNICAL_RULES['price_below_ma20']  # Penalty

        if signals.get('price_above_ma50'):
            score += self.TECHNICAL_RULES['price_above_ma50']
        elif signals.get('price_below_ma50'):
            score += self.TECHNICAL_RULES['price_below_ma50']  # Penalty

        if signals.get('ma20_above_ma50'):
            score += self.TECHNICAL_RULES['ma20_above_ma50']

        return max(0, min(score, 100))  # Clamp between 0-100

    def score_volume(self, signals: Dict[str, Any]) -> int:
        """
        Score volume patterns.

        Args:
            signals: Dictionary of signals

        Returns:
            Volume score (0-100)
        """
        score = 0

        volume_ratio = signals.get('volume_ratio', 0)

        if volume_ratio > 2.0:
            score += self.VOLUME_RULES['volume_spike_high']
        elif volume_ratio > 1.5:
            score += self.VOLUME_RULES['volume_spike_med']
        elif volume_ratio > 1.0:
            score += self.VOLUME_RULES['volume_normal']

        return min(score, 100)

    def score_momentum(self, signals: Dict[str, Any]) -> int:
        """
        Score price momentum.

        Args:
            signals: Dictionary of signals

        Returns:
            Momentum score (0-100)
        """
        score = 50  # Neutral baseline

        twenty_day_return = signals.get('twenty_day_return')

        if twenty_day_return is not None:
            if twenty_day_return > 0.05:
                score += self.MOMENTUM_RULES['strong_positive']
            elif twenty_day_return > 0:
                score += self.MOMENTUM_RULES['positive']
            else:
                score += self.MOMENTUM_RULES['negative']

        return max(0, min(score, 100))

    def score_fundamental(self, quote: Dict[str, Any]) -> int:
        """
        Score fundamental metrics.

        Args:
            quote: Quote data with PE ratio, etc.

        Returns:
            Fundamental score (0-100)
        """
        score = 50  # Neutral baseline

        pe_ratio = quote.get('pe_ratio')
        forward_pe = quote.get('forward_pe')

        # PE ratio scoring (relative value)
        if pe_ratio:
            if pe_ratio < 15:
                score += 20  # Undervalued
            elif pe_ratio < 25:
                score += 10  # Fair value
            elif pe_ratio > 50:
                score -= 10  # Overvalued

        # Forward PE (growth expectations)
        if forward_pe and pe_ratio:
            peg_proxy = forward_pe / pe_ratio if pe_ratio > 0 else 1
            if peg_proxy < 0.9:
                score += 15  # Improving growth

        return max(0, min(score, 100))

    def calculate_priority_score(
        self,
        signals: Dict[str, Any],
        quote: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate overall priority score.

        Args:
            signals: Technical signals
            quote: Current quote data

        Returns:
            Dictionary with scores and priority
        """
        # Calculate component scores
        technical_score = self.score_technical(signals)
        volume_score = self.score_volume(signals)
        momentum_score = self.score_momentum(signals)
        fundamental_score = self.score_fundamental(quote)

        # Calculate weighted total
        total_score = (
            technical_score * self.weights['technical'] +
            volume_score * self.weights['volume'] +
            momentum_score * self.weights['momentum'] +
            fundamental_score * self.weights['fundamental']
        )

        # Normalize score to 0-100 range for better user interpretation
        # Current scoring typically produces 30-60 range
        # Map 30->0, 60->100 using linear scaling: (score - min) / (max - min) * 100
        MIN_EXPECTED = 30
        MAX_EXPECTED = 60
        normalized_score = ((total_score - MIN_EXPECTED) / (MAX_EXPECTED - MIN_EXPECTED)) * 100
        normalized_score = max(0, min(100, normalized_score))  # Clamp to 0-100

        # Identify triggered alerts
        alerts = self.identify_alerts(signals)

        result = {
            'priority_score': int(normalized_score),
            'technical_score': technical_score,
            'volume_score': volume_score,
            'momentum_score': momentum_score,
            'fundamental_score': fundamental_score,
            'triggered_alerts': alerts
        }

        return result

    def identify_alerts(self, signals: Dict[str, Any]) -> List[str]:
        """
        Identify specific trading alerts.
        
        CRITICAL SIGNALS are prioritized first (divergence, squeeze, etc.)
        Then standard signals (MACD, RSI, etc.)

        Args:
            signals: Technical signals

        Returns:
            List of alert strings (prioritized by importance)
        """
        alerts = []
        
        # === CRITICAL SIGNALS (Highest Priority) ===
        # These should appear first as they're most important
        
        # RSI Divergence (CRITICAL - can indicate reversals)
        rsi_bullish_div = signals.get('rsi_bullish_divergence', False)
        rsi_bearish_div = signals.get('rsi_bearish_divergence', False)
        div_strength = signals.get('rsi_divergence_strength', 0)
        
        if rsi_bearish_div and div_strength > 0.5:
            # Bearish divergence is CRITICAL warning (e.g., NUE)
            alerts.append('⚠️ BEARISH_RSI_DIVERGENCE')
        elif rsi_bullish_div and div_strength > 0.5:
            # Bullish divergence is strong reversal signal
            alerts.append('BULLISH_RSI_DIVERGENCE')
        
        # Bollinger Band Squeeze (CRITICAL - breakout imminent)
        bb_squeeze = signals.get('bb_squeeze_detected', False)
        squeeze_strength = signals.get('bb_squeeze_strength', 0)
        if bb_squeeze and squeeze_strength > 0.7:
            alerts.append('BB_SQUEEZE')
        
        # === STANDARD SIGNALS (Medium Priority) ===
        
        # MACD signals (important momentum indicators)
        if signals.get('macd_bearish_crossover'):
            alerts.append('MACD_BEARISH_CROSS')
        elif signals.get('macd_bullish_crossover'):
            alerts.append('MACD_BULLISH_CROSS')
        
        # RSI extremes
        if signals.get('rsi_oversold'):
            alerts.append('RSI_OVERSOLD')
        
        if signals.get('rsi_overbought'):
            alerts.append('RSI_OVERBOUGHT')
        
        # Volume signals
        if signals.get('volume_spike'):
            alerts.append('VOLUME_SPIKE')

        # Bollinger Band alerts - validate that both can't be true simultaneously
        bb_lower = signals.get('near_bb_lower', False)
        bb_upper = signals.get('near_bb_upper', False)

        if bb_lower and bb_upper:
            # Impossible condition - log warning and skip both
            logger.warning(f"Invalid signal combination: BB_LOWER_TOUCH and BB_UPPER_TOUCH both true")
        elif bb_lower:
            alerts.append('BB_LOWER_TOUCH')
        elif bb_upper:
            alerts.append('BB_UPPER_TOUCH')

        # Support/resistance alerts
        if signals.get('near_support'):
            alerts.append('SUPPORT_HOLDING')

        if signals.get('near_resistance'):
            alerts.append('RESISTANCE_TEST')

        # Momentum alerts
        twenty_day = signals.get('twenty_day_return', 0)
        if twenty_day > 0.10:
            alerts.append('STRONG_MOMENTUM')
        elif twenty_day < -0.10:
            alerts.append('WEAK_MOMENTUM')

        return alerts
