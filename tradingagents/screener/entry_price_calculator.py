"""
Entry Price Calculator Module

Calculates recommended entry prices based on technical analysis, support/resistance,
Bollinger Bands, moving averages, and enterprise value metrics.
"""

from decimal import Decimal
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class EntryPriceCalculator:
    """Calculate recommended entry prices for stock positions."""

    def __init__(self):
        """Initialize entry price calculator."""
        pass

    def calculate_entry_price(
        self,
        current_price: float,
        technical_signals: Dict[str, Any],
        quote: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Calculate recommended entry price with full reasoning.

        Args:
            current_price: Current stock price
            technical_signals: Technical analysis signals dict
            quote: Quote data with fundamentals (optional)

        Returns:
            Dictionary with entry price recommendation:
            {
                'entry_price_min': float,
                'entry_price_max': float,
                'entry_timing': str,  # 'BUY_NOW', 'WAIT_FOR_PULLBACK', 'ACCUMULATE'
                'entry_price_reasoning': str,
                'bb_upper': float,
                'bb_lower': float,
                'bb_middle': float,
                'support_level': float,
                'resistance_level': float,
                'enterprise_value': int,
                'enterprise_to_ebitda': float,
                'market_cap': int
            }
        """
        if current_price is None or current_price <= 0:
            return self._empty_result()

        # Extract technical indicators
        rsi = technical_signals.get('rsi')
        bb_lower = technical_signals.get('bb_lower')
        bb_upper = technical_signals.get('bb_upper')
        bb_middle = technical_signals.get('bb_middle')
        ma_20 = technical_signals.get('ma_20') or technical_signals.get('ma20')
        ma_50 = technical_signals.get('ma_50') or technical_signals.get('ma50')
        ma_200 = technical_signals.get('ma_200') or technical_signals.get('ma200')

        # Extract new indicators (VWAP, Pivot Points, ATR)
        vwap = technical_signals.get('vwap')
        pivot_point = technical_signals.get('pivot_point')
        pivot_s1 = technical_signals.get('pivot_s1')
        pivot_s2 = technical_signals.get('pivot_s2')
        pivot_r1 = technical_signals.get('pivot_r1')
        pivot_r2 = technical_signals.get('pivot_r2')
        atr = technical_signals.get('atr')
        atr_pct = technical_signals.get('atr_pct')

        # Extract fundamental data if available
        enterprise_value = None
        enterprise_to_ebitda = None
        market_cap = None

        if quote:
            enterprise_value = quote.get('enterprise_value')
            enterprise_to_ebitda = quote.get('enterprise_to_ebitda')
            market_cap = quote.get('market_cap')

        # Calculate Bollinger Band middle if not provided
        if bb_lower and bb_upper and not bb_middle:
            bb_middle = (bb_lower + bb_upper) / 2

        # Determine support level (now includes pivot points)
        support_level = self._calculate_support(
            current_price, bb_lower, ma_50, ma_200, pivot_s1, pivot_s2
        )

        # Determine resistance level (now includes pivot points)
        resistance_level = self._calculate_resistance(
            current_price, bb_upper, ma_50, ma_200, pivot_r1, pivot_r2
        )

        # Calculate entry price range (now includes VWAP, ATR, pivot points)
        entry_min, entry_max, timing, reasoning = self._calculate_entry_range(
            current_price=current_price,
            rsi=rsi,
            bb_lower=bb_lower,
            bb_upper=bb_upper,
            bb_middle=bb_middle,
            ma_20=ma_20,
            ma_50=ma_50,
            support_level=support_level,
            enterprise_value=enterprise_value,
            enterprise_to_ebitda=enterprise_to_ebitda,
            market_cap=market_cap,
            vwap=vwap,
            pivot_point=pivot_point,
            pivot_s1=pivot_s1,
            pivot_r1=pivot_r1,
            atr=atr,
            atr_pct=atr_pct
        )

        return {
            'entry_price_min': round(entry_min, 2) if entry_min else None,
            'entry_price_max': round(entry_max, 2) if entry_max else None,
            'entry_timing': timing,
            'entry_price_reasoning': reasoning,
            'bb_upper': round(bb_upper, 2) if bb_upper else None,
            'bb_lower': round(bb_lower, 2) if bb_lower else None,
            'bb_middle': round(bb_middle, 2) if bb_middle else None,
            'support_level': round(support_level, 2) if support_level else None,
            'resistance_level': round(resistance_level, 2) if resistance_level else None,
            'enterprise_value': int(enterprise_value) if enterprise_value else None,
            'enterprise_to_ebitda': round(enterprise_to_ebitda, 2) if enterprise_to_ebitda else None,
            'market_cap': int(market_cap) if market_cap else None
        }

    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure."""
        return {
            'entry_price_min': None,
            'entry_price_max': None,
            'entry_timing': None,
            'entry_price_reasoning': 'Insufficient data',
            'bb_upper': None,
            'bb_lower': None,
            'bb_middle': None,
            'support_level': None,
            'resistance_level': None,
            'enterprise_value': None,
            'enterprise_to_ebitda': None,
            'market_cap': None
        }

    def _calculate_support(
        self,
        current_price: float,
        bb_lower: Optional[float],
        ma_50: Optional[float],
        ma_200: Optional[float],
        pivot_s1: Optional[float] = None,
        pivot_s2: Optional[float] = None
    ) -> Optional[float]:
        """
        Calculate support level from technical indicators and pivot points.

        Args:
            current_price: Current stock price
            bb_lower: Bollinger Band lower band
            ma_50: 50-day moving average
            ma_200: 200-day moving average
            pivot_s1: First pivot support level
            pivot_s2: Second pivot support level

        Returns:
            Highest support level below current price
        """
        support_candidates = []

        if bb_lower and bb_lower < current_price:
            support_candidates.append(bb_lower)

        if ma_50 and ma_50 < current_price:
            support_candidates.append(ma_50)

        if ma_200 and ma_200 < current_price:
            support_candidates.append(ma_200)

        # Add pivot support levels
        if pivot_s1 and pivot_s1 < current_price:
            support_candidates.append(pivot_s1)

        if pivot_s2 and pivot_s2 < current_price:
            support_candidates.append(pivot_s2)

        # Return the highest support level below current price
        return max(support_candidates) if support_candidates else None

    def _calculate_resistance(
        self,
        current_price: float,
        bb_upper: Optional[float],
        ma_50: Optional[float],
        ma_200: Optional[float],
        pivot_r1: Optional[float] = None,
        pivot_r2: Optional[float] = None
    ) -> Optional[float]:
        """
        Calculate resistance level from technical indicators and pivot points.

        Args:
            current_price: Current stock price
            bb_upper: Bollinger Band upper band
            ma_50: 50-day moving average
            ma_200: 200-day moving average
            pivot_r1: First pivot resistance level
            pivot_r2: Second pivot resistance level

        Returns:
            Lowest resistance level above current price
        """
        resistance_candidates = []

        if bb_upper and bb_upper > current_price:
            resistance_candidates.append(bb_upper)

        if ma_50 and ma_50 > current_price:
            resistance_candidates.append(ma_50)

        if ma_200 and ma_200 > current_price:
            resistance_candidates.append(ma_200)

        # Add pivot resistance levels
        if pivot_r1 and pivot_r1 > current_price:
            resistance_candidates.append(pivot_r1)

        if pivot_r2 and pivot_r2 > current_price:
            resistance_candidates.append(pivot_r2)

        # Return the lowest resistance level above current price
        return min(resistance_candidates) if resistance_candidates else None

    def _calculate_entry_range(
        self,
        current_price: float,
        rsi: Optional[float],
        bb_lower: Optional[float],
        bb_upper: Optional[float],
        bb_middle: Optional[float],
        ma_20: Optional[float],
        ma_50: Optional[float],
        support_level: Optional[float],
        enterprise_value: Optional[float],
        enterprise_to_ebitda: Optional[float],
        market_cap: Optional[float],
        vwap: Optional[float] = None,
        pivot_point: Optional[float] = None,
        pivot_s1: Optional[float] = None,
        pivot_r1: Optional[float] = None,
        atr: Optional[float] = None,
        atr_pct: Optional[float] = None
    ) -> Tuple[float, float, str, str]:
        """
        Calculate entry price range with timing and reasoning.

        Now includes institutional-grade indicators:
        - VWAP: Primary institutional benchmark
        - Pivot Points: Floor trader support/resistance
        - ATR: Volatility-adjusted entry ranges

        Returns:
            (entry_min, entry_max, timing, reasoning)
        """
        reasoning_parts = []
        entry_base = current_price
        adjustment_pct = 0.0

        # === PRIORITY 1: VWAP ANALYSIS (Institutional Benchmark) ===
        # VWAP is the single most important indicator for institutional traders
        # Price below VWAP = bullish opportunity, above = wait for pullback
        vwap_entry_confidence = 0.0  # Track how strong the VWAP signal is

        if vwap:
            vwap_distance_pct = ((current_price - vwap) / vwap) * 100

            if current_price < vwap * 0.995:  # More than 0.5% below VWAP
                # EXCELLENT ENTRY - Institutions accumulating at discount
                vwap_entry_confidence = 0.9
                entry_min = current_price * 0.99
                entry_max = vwap * 0.998  # Target up to VWAP
                timing = 'BUY_NOW'
                reasoning_parts.append(f"Price {abs(vwap_distance_pct):.1f}% below VWAP - institutional buy zone")

            elif current_price < vwap * 1.005:  # Within 0.5% of VWAP
                # GOOD ENTRY - Near institutional benchmark
                vwap_entry_confidence = 0.7
                entry_min = current_price * 0.995
                entry_max = current_price * 1.005
                timing = 'ACCUMULATE'
                reasoning_parts.append(f"Price near VWAP ({vwap_distance_pct:+.1f}%) - good institutional level")

            elif current_price > vwap * 1.02:  # More than 2% above VWAP
                # WAIT FOR PULLBACK - Price extended above institutional benchmark
                vwap_entry_confidence = 0.3
                # Target pullback to VWAP
                if pivot_s1 and pivot_s1 < vwap:
                    # Use pivot support if it's below VWAP
                    entry_min = pivot_s1 * 0.995
                    entry_max = vwap * 1.002
                else:
                    entry_min = vwap * 0.995
                    entry_max = vwap * 1.005
                timing = 'WAIT_FOR_PULLBACK'
                reasoning_parts.append(f"Price {vwap_distance_pct:.1f}% above VWAP - wait for institutional retest")

            else:  # Between +0.5% and +2% above VWAP
                # CAUTIOUS ENTRY - Slightly extended but not extreme
                vwap_entry_confidence = 0.5
                entry_min = vwap * 0.998
                entry_max = current_price * 1.00
                timing = 'ACCUMULATE'
                reasoning_parts.append(f"Price {vwap_distance_pct:.1f}% above VWAP - cautious entry near benchmark")

        # === PRIORITY 2: VOLATILITY ADJUSTMENT (ATR) ===
        # Use ATR to set realistic entry ranges based on stock's volatility
        if atr and atr_pct:
            # ATR percentage tells us how volatile the stock is
            # High volatility stocks need wider ranges, low volatility need tighter ranges

            if vwap_entry_confidence > 0.5:
                # Good VWAP signal - use ATR to refine range
                if atr_pct > 3.0:
                    # High volatility - widen the range
                    range_multiplier = 1.5
                    reasoning_parts.append(f"High volatility (ATR {atr_pct:.1f}%) - wider entry range")
                elif atr_pct < 1.0:
                    # Low volatility - tighten the range
                    range_multiplier = 0.6
                    reasoning_parts.append(f"Low volatility (ATR {atr_pct:.1f}%) - tight entry range")
                else:
                    # Normal volatility
                    range_multiplier = 1.0

                # Adjust entry range based on volatility
                if timing in ['BUY_NOW', 'ACCUMULATE']:
                    # For buy signals, use ATR to set realistic downside target
                    atr_adjusted_min = entry_min - (atr * range_multiplier * 0.5)
                    # Don't go below support
                    if support_level:
                        entry_min = max(atr_adjusted_min, support_level * 0.995)
                    else:
                        entry_min = atr_adjusted_min

                elif timing == 'WAIT_FOR_PULLBACK':
                    # For pullback scenarios, expect movement proportional to ATR
                    expected_pullback = atr * range_multiplier
                    entry_min = current_price - expected_pullback
                    entry_max = current_price - (expected_pullback * 0.3)

        # === PRIORITY 3: PIVOT POINT ANALYSIS ===
        # Pivot points provide additional support/resistance confirmation
        if pivot_point and pivot_s1 and pivot_r1:
            if current_price > pivot_r1:
                # Above resistance - likely extended
                if 'VWAP' not in reasoning_parts[-1] if reasoning_parts else False:
                    # Only override if no strong VWAP signal
                    timing = 'WAIT_FOR_PULLBACK'
                    entry_min = pivot_point * 0.998
                    entry_max = pivot_r1 * 0.995
                    reasoning_parts.append("Price above pivot R1 - wait for retest")

            elif current_price < pivot_s1:
                # Below support - oversold
                if timing != 'BUY_NOW':
                    timing = 'BUY_NOW'
                entry_min = current_price * 0.98
                entry_max = pivot_s1 * 1.02
                reasoning_parts.append("Price below pivot S1 - oversold bounce candidate")

            elif pivot_s1 < current_price < pivot_point:
                # Between support and pivot - good accumulation zone
                reasoning_parts.append("Price in pivot accumulation zone (S1 to PP)")

            elif pivot_point < current_price < pivot_r1:
                # Between pivot and resistance - neutral zone
                reasoning_parts.append("Price in pivot neutral zone (PP to R1)")

        # === FALLBACK: RSI LOGIC (if no VWAP signal) ===
        # If VWAP didn't provide a strong signal, use traditional RSI-based entry
        if not vwap or vwap_entry_confidence < 0.5:
            # RSI-based entry strategy
            if rsi:
                if rsi < 30:
                    # Oversold - excellent entry opportunity
                    entry_min = current_price * 0.97
                    entry_max = current_price * 1.00
                    timing = 'BUY_NOW'
                    reasoning_parts.append(f"RSI {rsi:.1f} is oversold")
                elif rsi < 40:
                    # Approaching oversold - good entry
                    entry_min = current_price * 0.98
                    entry_max = current_price * 1.01
                    timing = 'ACCUMULATE'
                    reasoning_parts.append(f"RSI {rsi:.1f} approaching oversold")
                elif rsi > 70:
                    # Overbought - wait for pullback
                    if support_level:
                        entry_min = support_level * 0.99
                        entry_max = support_level * 1.02
                    else:
                        entry_min = current_price * 0.92
                        entry_max = current_price * 0.96
                    timing = 'WAIT_FOR_PULLBACK'
                    reasoning_parts.append(f"RSI {rsi:.1f} is overbought, wait for pullback")
                elif rsi > 60:
                    # Slightly overbought - wait for slight dip
                    entry_min = current_price * 0.97
                    entry_max = current_price * 0.99
                    timing = 'WAIT_FOR_PULLBACK'
                    reasoning_parts.append(f"RSI {rsi:.1f} slightly elevated")
                else:
                    # Neutral RSI - enter near support or current price
                    if support_level and support_level < current_price:
                        entry_min = support_level * 1.00
                        entry_max = current_price * 0.98
                        timing = 'ACCUMULATE'
                        reasoning_parts.append(f"RSI {rsi:.1f} neutral, target support")
                    else:
                        entry_min = current_price * 0.98
                        entry_max = current_price * 1.02
                        timing = 'ACCUMULATE'
                        reasoning_parts.append(f"RSI {rsi:.1f} neutral")
            else:
                # No RSI data - use Bollinger Bands if available
                if bb_lower and bb_middle:
                    if current_price < bb_middle:
                        # Below mid-band - good entry
                        entry_min = max(bb_lower * 1.01, current_price * 0.98)
                        entry_max = bb_middle
                        timing = 'ACCUMULATE'
                        reasoning_parts.append("Price below BB mid-band")
                    else:
                        # Above mid-band - wait for pullback
                        entry_min = bb_lower * 1.01
                        entry_max = bb_middle * 0.99
                        timing = 'WAIT_FOR_PULLBACK'
                        reasoning_parts.append("Price above BB mid-band")
                else:
                    # No technical data - use conservative range
                    entry_min = current_price * 0.98
                    entry_max = current_price * 1.02
                    timing = 'ACCUMULATE'
                    reasoning_parts.append("Limited technical data")

        # === ENTERPRISE VALUE ANALYSIS (Always apply as adjustment) ===
        if enterprise_value and market_cap and market_cap > 0:
            ev_to_mcap = enterprise_value / market_cap
            if ev_to_mcap < 0.9:
                adjustment_pct -= 0.02  # 2% discount - undervalued
                reasoning_parts.append(f"EV/Market Cap {ev_to_mcap:.2f} suggests undervaluation")
            elif ev_to_mcap > 1.2:
                adjustment_pct += 0.03  # Wait for better entry
                reasoning_parts.append(f"High EV/Market Cap {ev_to_mcap:.2f} suggests high debt")

        if enterprise_to_ebitda:
            if enterprise_to_ebitda < 5:
                adjustment_pct = min(adjustment_pct - 0.03, -0.05)
                reasoning_parts.append(f"Excellent EV/EBITDA {enterprise_to_ebitda:.1f}")
            elif enterprise_to_ebitda < 10:
                adjustment_pct = min(adjustment_pct - 0.01, -0.02)
                reasoning_parts.append(f"Good EV/EBITDA {enterprise_to_ebitda:.1f}")
            elif enterprise_to_ebitda > 20:
                adjustment_pct = max(adjustment_pct + 0.02, 0.03)
                reasoning_parts.append(f"High EV/EBITDA {enterprise_to_ebitda:.1f}")

        # === APPLY ENTERPRISE VALUE ADJUSTMENTS ===
        # Apply enterprise value adjustments to entry prices
        if adjustment_pct != 0:
            entry_min *= (1 + adjustment_pct)
            entry_max *= (1 + adjustment_pct)

        # Use Bollinger Bands for refinement if available
        if bb_lower and bb_middle and current_price < bb_middle:
            entry_min = max(entry_min, bb_lower * 1.01)
            entry_max = min(entry_max, bb_middle)

        # Build reasoning string
        reasoning = "; ".join(reasoning_parts) if reasoning_parts else "Standard technical analysis"

        return entry_min, entry_max, timing, reasoning
