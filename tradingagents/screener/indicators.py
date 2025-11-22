# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Technical Indicators Module

Calculates technical indicators for screening.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """Calculate technical indicators for price data."""

    @staticmethod
    def calculate_sma(data: pd.Series, period: int) -> pd.Series:
        """Calculate Simple Moving Average."""
        return data.rolling(window=period).mean()

    @staticmethod
    def calculate_ema(data: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average."""
        return data.ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index.

        Args:
            data: Price series (typically close prices)
            period: RSI period (default 14)

        Returns:
            RSI series (0-100)
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def calculate_macd(
        data: pd.Series,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Dict[str, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence).

        Args:
            data: Price series (typically close prices)
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period

        Returns:
            Dictionary with macd, signal, histogram
        """
        ema_fast = data.ewm(span=fast, adjust=False).mean()
        ema_slow = data.ewm(span=slow, adjust=False).mean()

        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line

        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }

    @staticmethod
    def calculate_bollinger_bands(
        data: pd.Series,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Dict[str, pd.Series]:
        """
        Calculate Bollinger Bands.

        Args:
            data: Price series
            period: Moving average period
            std_dev: Number of standard deviations

        Returns:
            Dictionary with upper, middle, lower bands
        """
        middle = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()

        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)

        return {
            'upper': upper,
            'middle': middle,
            'lower': lower
        }

    @staticmethod
    def calculate_atr(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """
        Calculate Average True Range.

        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: ATR period

        Returns:
            ATR series
        """
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())

        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()

        return atr

    @staticmethod
    def calculate_vwap(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        volume: pd.Series
    ) -> pd.Series:
        """
        Calculate Volume Weighted Average Price (VWAP).

        VWAP is the average price weighted by volume - the key benchmark
        institutional traders use for execution quality. Price above VWAP
        indicates bullish pressure, below indicates bearish pressure.

        Args:
            high: High prices
            low: Low prices
            close: Close prices
            volume: Volume data

        Returns:
            VWAP series

        Note:
            VWAP is typically calculated intraday and reset daily. For daily
            data, we calculate cumulative VWAP using typical price.
        """
        # Calculate typical price (HLC/3)
        typical_price = (high + low + close) / 3

        # Calculate cumulative (TP * volume)
        cumulative_tp_volume = (typical_price * volume).cumsum()

        # Calculate cumulative volume
        cumulative_volume = volume.cumsum()

        # VWAP = cumulative(TP * volume) / cumulative(volume)
        vwap = cumulative_tp_volume / cumulative_volume

        return vwap

    @staticmethod
    def calculate_pivot_points(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series
    ) -> Dict[str, pd.Series]:
        """
        Calculate Standard Pivot Points.

        Pivot points are price levels calculated from the previous period's
        high, low, and close. They're used by floor traders to identify
        potential support and resistance levels for the current period.

        Args:
            high: High prices (previous period)
            low: Low prices (previous period)
            close: Close prices (previous period)

        Returns:
            Dictionary with PP (pivot point), R1/R2/R3 (resistance), S1/S2/S3 (support)

        Note:
            For daily data, these use previous day's HLC to calculate today's levels.
            Self-fulfilling prophecy: many traders watch the same levels.
        """
        # Shift to use previous day's data
        prev_high = high.shift(1)
        prev_low = low.shift(1)
        prev_close = close.shift(1)

        # Pivot Point = (High + Low + Close) / 3
        pp = (prev_high + prev_low + prev_close) / 3

        # Resistance levels
        r1 = (2 * pp) - prev_low
        r2 = pp + (prev_high - prev_low)
        r3 = prev_high + 2 * (pp - prev_low)

        # Support levels
        s1 = (2 * pp) - prev_high
        s2 = pp - (prev_high - prev_low)
        s3 = prev_low - 2 * (prev_high - pp)

        return {
            'pp': pp,       # Pivot Point (primary level)
            'r1': r1,       # First resistance
            'r2': r2,       # Second resistance
            'r3': r3,       # Third resistance
            's1': s1,       # First support
            's2': s2,       # Second support
            's3': s3        # Third support
        }

    @staticmethod
    def detect_rsi_divergence(
        price_data: pd.Series,
        rsi_data: pd.Series,
        lookback: int = 20
    ) -> Dict[str, Any]:
        """
        Detect bullish and bearish RSI divergence.

        Divergence occurs when price and RSI move in opposite directions:
        - Bullish Divergence: Price makes lower low, RSI makes higher low → Reversal UP
        - Bearish Divergence: Price makes higher high, RSI makes lower high → Reversal DOWN

        Args:
            price_data: Price series (typically close prices)
            rsi_data: RSI series
            lookback: Periods to look back for swing points

        Returns:
            Dictionary with divergence signals and strength
        """
        if len(price_data) < lookback or len(rsi_data) < lookback:
            return {
                'bullish_divergence': False,
                'bearish_divergence': False,
                'divergence_strength': 0.0,
                'divergence_type': None
            }

        recent_price = price_data.tail(lookback)
        recent_rsi = rsi_data.tail(lookback)

        # Find swing lows (local minima) in price
        price_lows = []
        for i in range(2, len(recent_price) - 2):
            if (recent_price.iloc[i] < recent_price.iloc[i-1] and
                recent_price.iloc[i] < recent_price.iloc[i-2] and
                recent_price.iloc[i] < recent_price.iloc[i+1] and
                recent_price.iloc[i] < recent_price.iloc[i+2]):
                price_lows.append((i, recent_price.iloc[i]))

        # Find swing highs (local maxima) in price
        price_highs = []
        for i in range(2, len(recent_price) - 2):
            if (recent_price.iloc[i] > recent_price.iloc[i-1] and
                recent_price.iloc[i] > recent_price.iloc[i-2] and
                recent_price.iloc[i] > recent_price.iloc[i+1] and
                recent_price.iloc[i] > recent_price.iloc[i+2]):
                price_highs.append((i, recent_price.iloc[i]))

        # Find corresponding RSI swing points
        rsi_lows = []
        for idx, _ in price_lows:
            rsi_lows.append((idx, recent_rsi.iloc[idx]))

        rsi_highs = []
        for idx, _ in price_highs:
            rsi_highs.append((idx, recent_rsi.iloc[idx]))

        # Check for bullish divergence (price lower low, RSI higher low)
        bullish_divergence = False
        bullish_strength = 0.0
        if len(price_lows) >= 2 and len(rsi_lows) >= 2:
            last_price_low = price_lows[-1][1]
            prev_price_low = price_lows[-2][1]
            last_rsi_low = rsi_lows[-1][1]
            prev_rsi_low = rsi_lows[-2][1]

            if last_price_low < prev_price_low and last_rsi_low > prev_rsi_low:
                bullish_divergence = True
                # Strength based on magnitude of divergence
                price_drop_pct = ((prev_price_low - last_price_low) / prev_price_low) * 100
                rsi_rise = last_rsi_low - prev_rsi_low
                bullish_strength = min(0.95, (price_drop_pct / 5.0 + rsi_rise / 20.0) / 2.0)

        # Check for bearish divergence (price higher high, RSI lower high)
        bearish_divergence = False
        bearish_strength = 0.0
        if len(price_highs) >= 2 and len(rsi_highs) >= 2:
            last_price_high = price_highs[-1][1]
            prev_price_high = price_highs[-2][1]
            last_rsi_high = rsi_highs[-1][1]
            prev_rsi_high = rsi_highs[-2][1]

            if last_price_high > prev_price_high and last_rsi_high < prev_rsi_high:
                bearish_divergence = True
                # Strength based on magnitude of divergence
                price_rise_pct = ((last_price_high - prev_price_high) / prev_price_high) * 100
                rsi_drop = prev_rsi_high - last_rsi_high
                bearish_strength = min(0.95, (price_rise_pct / 5.0 + rsi_drop / 20.0) / 2.0)

        # Determine overall divergence type
        divergence_type = None
        divergence_strength = 0.0
        if bullish_divergence and bearish_divergence:
            # Both present - use stronger signal
            if bullish_strength > bearish_strength:
                divergence_type = 'bullish'
                divergence_strength = bullish_strength
            else:
                divergence_type = 'bearish'
                divergence_strength = bearish_strength
        elif bullish_divergence:
            divergence_type = 'bullish'
            divergence_strength = bullish_strength
        elif bearish_divergence:
            divergence_type = 'bearish'
            divergence_strength = bearish_strength

        return {
            'bullish_divergence': bullish_divergence,
            'bearish_divergence': bearish_divergence,
            'divergence_strength': divergence_strength,
            'divergence_type': divergence_type
        }

    @staticmethod
    def calculate_fibonacci_retracements(
        data: pd.DataFrame,
        lookback: int = 20
    ) -> Dict[str, float]:
        """
        Calculate Fibonacci retracement levels.

        Fibonacci levels are horizontal lines that indicate where support and
        resistance are likely to occur. Based on Fibonacci sequence: 23.6%, 38.2%,
        50%, 61.8%, 78.6%.

        Args:
            data: DataFrame with OHLC data
            lookback: Period to identify swing high/low

        Returns:
            Dictionary with Fibonacci levels and current price position
        """
        if len(data) < lookback:
            return {
                'swing_high': None,
                'swing_low': None,
                'fib_236': None,
                'fib_382': None,
                'fib_500': None,
                'fib_618': None,
                'fib_786': None,
                'current_fib_level': None
            }

        recent_data = data.tail(lookback)
        swing_high = recent_data['high'].max()
        swing_low = recent_data['low'].min()
        current_price = data['close'].iloc[-1]

        diff = swing_high - swing_low

        # Calculate retracement levels (from swing high)
        fib_levels = {
            'swing_high': swing_high,
            'swing_low': swing_low,
            'fib_236': swing_high - (diff * 0.236),
            'fib_382': swing_high - (diff * 0.382),
            'fib_500': swing_high - (diff * 0.500),
            'fib_618': swing_high - (diff * 0.618),
            'fib_786': swing_high - (diff * 0.786)
        }

        # Determine which Fibonacci level price is near
        tolerance = diff * 0.02  # 2% tolerance
        current_fib_level = None

        for level_name in ['fib_236', 'fib_382', 'fib_500', 'fib_618', 'fib_786']:
            level_value = fib_levels[level_name]
            if abs(current_price - level_value) < tolerance:
                current_fib_level = level_name
                break

        fib_levels['current_fib_level'] = current_fib_level

        return fib_levels

    @staticmethod
    def detect_bollinger_band_squeeze(
        bb_data: pd.DataFrame,
        lookback: int = 20
    ) -> Dict[str, Any]:
        """
        Detect Bollinger Band squeeze (volatility compression).

        A squeeze occurs when Bollinger Bands contract to their narrowest width
        in the lookback period. This indicates low volatility and often precedes
        a significant price move (breakout).

        Args:
            bb_data: DataFrame with bb_upper, bb_middle, bb_lower columns
            lookback: Period to compare BB width

        Returns:
            Dictionary with squeeze detection and strength
        """
        if len(bb_data) < lookback:
            return {
                'squeeze_detected': False,
                'squeeze_strength': 0.0,
                'bb_width': None,
                'bb_width_percentile': None
            }

        # Calculate Bollinger Band width
        bb_data['bb_width'] = (bb_data['bb_upper'] - bb_data['bb_lower']) / bb_data['bb_middle']

        recent_width = bb_data['bb_width'].tail(lookback)
        current_width = bb_data['bb_width'].iloc[-1]

        # Calculate percentile of current width
        bb_width_percentile = (recent_width < current_width).sum() / len(recent_width)

        # Squeeze detected if current width is in bottom 15%
        squeeze_detected = bb_width_percentile < 0.15

        # Squeeze strength (0 to 1, where 1 is tightest squeeze)
        squeeze_strength = 0.0
        if squeeze_detected:
            squeeze_strength = 1.0 - (bb_width_percentile / 0.15)

        return {
            'squeeze_detected': squeeze_detected,
            'squeeze_strength': squeeze_strength,
            'bb_width': current_width,
            'bb_width_percentile': bb_width_percentile
        }

    @staticmethod
    def calculate_volume_profile(
        data: pd.DataFrame,
        lookback: int = 20,
        num_bins: int = 20
    ) -> Dict[str, Any]:
        """
        Calculate Volume Profile - identifies price levels with highest trading activity.

        Volume Profile shows where the most volume traded at each price level.
        Key levels:
        - POC (Point of Control): Price level with highest volume (strongest support/resistance)
        - VAH (Value Area High): Top of 70% volume range
        - VAL (Value Area Low): Bottom of 70% volume range

        Args:
            data: DataFrame with OHLC + volume
            lookback: Number of days to analyze
            num_bins: Number of price bins for profile

        Returns:
            Dictionary with volume profile metrics
        """
        if len(data) < lookback:
            return {
                'poc': None,
                'vah': None,
                'val': None,
                'volume_nodes': [],
                'low_volume_nodes': []
            }

        recent_data = data.tail(lookback).copy()

        # Get price range
        price_min = recent_data['low'].min()
        price_max = recent_data['high'].max()

        # Create price bins
        price_bins = np.linspace(price_min, price_max, num_bins + 1)
        bin_centers = (price_bins[:-1] + price_bins[1:]) / 2

        # Aggregate volume at each price level
        volume_at_price = np.zeros(num_bins)

        for idx, row in recent_data.iterrows():
            # For each candle, distribute volume across price bins it touched
            candle_low = row['low']
            candle_high = row['high']
            candle_volume = row['volume']

            # Find bins this candle touched
            bins_touched = []
            for i, (bin_low, bin_high) in enumerate(zip(price_bins[:-1], price_bins[1:])):
                if candle_high >= bin_low and candle_low <= bin_high:
                    bins_touched.append(i)

            # Distribute volume equally across touched bins
            if bins_touched:
                volume_per_bin = candle_volume / len(bins_touched)
                for bin_idx in bins_touched:
                    volume_at_price[bin_idx] += volume_per_bin

        # Calculate POC (Point of Control) - price with highest volume
        poc_idx = np.argmax(volume_at_price)
        poc = bin_centers[poc_idx]
        poc_volume = volume_at_price[poc_idx]

        # Calculate Value Area (70% of volume)
        total_volume = volume_at_price.sum()
        target_volume = total_volume * 0.70

        # Start from POC and expand outward
        value_area_volume = volume_at_price[poc_idx]
        lower_idx = poc_idx
        upper_idx = poc_idx

        while value_area_volume < target_volume:
            # Determine which direction to expand (choose side with more volume)
            lower_vol = volume_at_price[lower_idx - 1] if lower_idx > 0 else 0
            upper_vol = volume_at_price[upper_idx + 1] if upper_idx < num_bins - 1 else 0

            if lower_vol > upper_vol and lower_idx > 0:
                lower_idx -= 1
                value_area_volume += volume_at_price[lower_idx]
            elif upper_idx < num_bins - 1:
                upper_idx += 1
                value_area_volume += volume_at_price[upper_idx]
            else:
                break

        vah = bin_centers[upper_idx]  # Value Area High
        val = bin_centers[lower_idx]  # Value Area Low

        # Identify high volume nodes (> 80th percentile)
        volume_threshold_high = np.percentile(volume_at_price, 80)
        high_volume_nodes = []
        for i, (price, vol) in enumerate(zip(bin_centers, volume_at_price)):
            if vol >= volume_threshold_high:
                high_volume_nodes.append({
                    'price': price,
                    'volume': vol,
                    'volume_pct': (vol / total_volume) * 100
                })

        # Identify low volume nodes (< 20th percentile) - potential breakout zones
        volume_threshold_low = np.percentile(volume_at_price, 20)
        low_volume_nodes = []
        for i, (price, vol) in enumerate(zip(bin_centers, volume_at_price)):
            if vol <= volume_threshold_low and vol > 0:
                low_volume_nodes.append({
                    'price': price,
                    'volume': vol,
                    'volume_pct': (vol / total_volume) * 100
                })

        # Current price position relative to volume profile
        current_price = data['close'].iloc[-1]

        if current_price > vah:
            profile_position = 'ABOVE_VALUE_AREA'
            position_signal = 'Price above fair value - consider selling'
        elif current_price < val:
            profile_position = 'BELOW_VALUE_AREA'
            position_signal = 'Price below fair value - consider buying'
        elif abs(current_price - poc) / poc < 0.01:  # Within 1% of POC
            profile_position = 'AT_POC'
            position_signal = 'Price at highest volume - expect consolidation'
        else:
            profile_position = 'WITHIN_VALUE_AREA'
            position_signal = 'Price within fair value range'

        return {
            'poc': poc,  # Point of Control
            'vah': vah,  # Value Area High
            'val': val,  # Value Area Low
            'poc_volume': poc_volume,
            'total_volume': total_volume,
            'value_area_volume_pct': (value_area_volume / total_volume) * 100,
            'profile_position': profile_position,
            'position_signal': position_signal,
            'volume_nodes': high_volume_nodes[:3],  # Top 3 high volume nodes
            'low_volume_nodes': low_volume_nodes[:3],  # Top 3 low volume nodes
            'distance_to_poc_pct': ((current_price - poc) / poc) * 100,
            'distance_to_vah_pct': ((current_price - vah) / vah) * 100,
            'distance_to_val_pct': ((current_price - val) / val) * 100
        }

    @staticmethod
    def analyze_order_flow(
        data: pd.DataFrame,
        lookback: int = 10
    ) -> Dict[str, Any]:
        """
        Analyze order flow to detect institutional buying/selling.

        Uses volume and price action patterns to identify:
        - Accumulation (institutions buying)
        - Distribution (institutions selling)
        - Smart money activity

        Args:
            data: DataFrame with OHLC + volume
            lookback: Number of days to analyze

        Returns:
            Dictionary with order flow analysis
        """
        if len(data) < lookback:
            return {
                'order_flow_signal': 'INSUFFICIENT_DATA',
                'institutional_activity': 'UNKNOWN',
                'buying_pressure': 0,
                'selling_pressure': 0
            }

        recent_data = data.tail(lookback).copy()

        # Calculate buying vs selling pressure using candle bodies and volume
        buying_pressure = 0
        selling_pressure = 0

        for idx, row in recent_data.iterrows():
            candle_range = row['high'] - row['low']
            if candle_range == 0:
                continue

            # Green candle (close > open) = buying pressure
            if row['close'] > row['open']:
                body_pct = (row['close'] - row['open']) / candle_range
                buying_pressure += row['volume'] * body_pct
            # Red candle (close < open) = selling pressure
            elif row['close'] < row['open']:
                body_pct = (row['open'] - row['close']) / candle_range
                selling_pressure += row['volume'] * body_pct

        total_pressure = buying_pressure + selling_pressure
        if total_pressure == 0:
            return {
                'order_flow_signal': 'NEUTRAL',
                'institutional_activity': 'UNKNOWN',
                'buying_pressure': 0,
                'selling_pressure': 0
            }

        # Calculate ratios
        buying_pct = (buying_pressure / total_pressure) * 100
        selling_pct = (selling_pressure / total_pressure) * 100

        # === VALIDATION: Check if order flow matches price action ===
        # If price changed significantly, order flow MUST align with price direction
        # This prevents false signals in ranging/consolidating stocks
        price_change_10d = ((recent_data['close'].iloc[-1] - recent_data['close'].iloc[0]) /
                           recent_data['close'].iloc[0]) * 100

        # If strong selling (>70%) but price stable/up, likely ranging - rebalance to 50/50
        if selling_pct > 70 and price_change_10d > -2:
            # Price didn't fall despite heavy selling = balanced market or accumulation
            buying_pct = 50.0
            selling_pct = 50.0
            logger.debug(f"Order flow rebalanced: {selling_pct:.1f}% selling but price only changed {price_change_10d:+.1f}%")

        # If strong buying (>70%) but price stable/down, likely ranging - rebalance to 50/50
        elif buying_pct > 70 and price_change_10d < 2:
            # Price didn't rise despite heavy buying = balanced market or distribution
            buying_pct = 50.0
            selling_pct = 50.0
            logger.debug(f"Order flow rebalanced: {buying_pct:.1f}% buying but price only changed {price_change_10d:+.1f}%")

        # Detect accumulation/distribution patterns
        # Accumulation: Price stable/down slightly but volume increasing
        price_change = ((recent_data['close'].iloc[-1] - recent_data['close'].iloc[0]) /
                       recent_data['close'].iloc[0]) * 100

        volume_trend = recent_data['volume'].iloc[-5:].mean() / recent_data['volume'].iloc[:5].mean()

        # Pattern detection
        if buying_pct > 65 and volume_trend > 1.2:
            if price_change < 5:  # Price not moving much despite buying
                institutional_activity = 'ACCUMULATION'
                order_flow_signal = 'BULLISH_ACCUMULATION'
                signal_strength = min((buying_pct - 50) / 50, 1.0)  # 0-1 scale
            else:
                institutional_activity = 'BUYING'
                order_flow_signal = 'STRONG_BUYING'
                signal_strength = min((buying_pct - 50) / 50, 1.0)
        elif selling_pct > 65 and volume_trend > 1.2:
            if price_change > -5:  # Price not dropping much despite selling
                institutional_activity = 'DISTRIBUTION'
                order_flow_signal = 'BEARISH_DISTRIBUTION'
                signal_strength = min((selling_pct - 50) / 50, 1.0)
            else:
                institutional_activity = 'SELLING'
                order_flow_signal = 'STRONG_SELLING'
                signal_strength = min((selling_pct - 50) / 50, 1.0)
        elif buying_pct > 55:
            institutional_activity = 'MODERATE_BUYING'
            order_flow_signal = 'BULLISH'
            signal_strength = (buying_pct - 50) / 50
        elif selling_pct > 55:
            institutional_activity = 'MODERATE_SELLING'
            order_flow_signal = 'BEARISH'
            signal_strength = (selling_pct - 50) / 50
        else:
            institutional_activity = 'NEUTRAL'
            order_flow_signal = 'BALANCED'
            signal_strength = 0.5

        # Detect unusual volume spikes (potential institutional activity)
        avg_volume = recent_data['volume'].mean()
        current_volume = recent_data['volume'].iloc[-1]
        volume_spike = current_volume > avg_volume * 2

        return {
            'order_flow_signal': order_flow_signal,
            'institutional_activity': institutional_activity,
            'signal_strength': signal_strength,
            'buying_pressure': buying_pressure,
            'selling_pressure': selling_pressure,
            'buying_pct': buying_pct,
            'selling_pct': selling_pct,
            'volume_trend': volume_trend,
            'volume_spike_detected': volume_spike,
            'price_change_pct': price_change
        }

    @staticmethod
    def analyze_multi_timeframe(
        daily_data: pd.DataFrame,
        weekly_data: pd.DataFrame = None,
        monthly_data: pd.DataFrame = None
    ) -> Dict[str, Any]:
        """
        Analyze multiple timeframes to confirm signals.

        Professional traders use multi-timeframe analysis to:
        1. Confirm trend direction across timeframes
        2. Identify best entry timing
        3. Reduce false signals

        Rule: Trend on higher timeframe > trend on lower timeframe
        - Monthly trend determines overall direction
        - Weekly trend confirms intermediate term
        - Daily trend provides entry timing

        Args:
            daily_data: Daily OHLC data
            weekly_data: Weekly OHLC data (optional, will resample if not provided)
            monthly_data: Monthly OHLC data (optional, will resample if not provided)

        Returns:
            Dictionary with multi-timeframe analysis
        """
        if len(daily_data) < 50:
            return {
                'alignment': 'INSUFFICIENT_DATA',
                'signal': 'WAIT',
                'timeframe_scores': {}
            }

        # Resample to weekly and monthly if not provided
        if weekly_data is None:
            weekly_data = daily_data.resample('W').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }).dropna()

        if monthly_data is None:
            monthly_data = daily_data.resample('ME').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }).dropna()

        # Analyze each timeframe
        timeframes = {
            'daily': daily_data,
            'weekly': weekly_data,
            'monthly': monthly_data
        }

        timeframe_analysis = {}

        for tf_name, tf_data in timeframes.items():
            if len(tf_data) < 20:
                continue

            # Calculate key indicators for this timeframe
            close = tf_data['close']
            ma_20 = close.rolling(20).mean()
            ma_50 = close.rolling(50).mean() if len(close) >= 50 else ma_20

            current_price = close.iloc[-1]
            current_ma_20 = ma_20.iloc[-1]
            current_ma_50 = ma_50.iloc[-1]

            # Determine trend
            if current_price > current_ma_20 > current_ma_50:
                trend = 'UPTREND'
                trend_strength = ((current_price - current_ma_50) / current_ma_50) * 100
                score = min(trend_strength * 2, 10)  # 0-10 scale
            elif current_price < current_ma_20 < current_ma_50:
                trend = 'DOWNTREND'
                trend_strength = ((current_ma_50 - current_price) / current_ma_50) * 100
                score = -min(trend_strength * 2, 10)  # -10 to 0 scale
            else:
                trend = 'NEUTRAL'
                score = 0
                trend_strength = 0

            # Calculate RSI for this timeframe
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1] if not rsi.empty else 50

            timeframe_analysis[tf_name] = {
                'trend': trend,
                'trend_strength': trend_strength,
                'score': score,
                'rsi': current_rsi,
                'ma_20': current_ma_20,
                'ma_50': current_ma_50,
                'price': current_price
            }

        # Check alignment across timeframes
        if not timeframe_analysis:
            return {
                'alignment': 'INSUFFICIENT_DATA',
                'signal': 'WAIT',
                'timeframe_scores': {}
            }

        # Get trends from each timeframe
        daily_trend = timeframe_analysis.get('daily', {}).get('trend', 'NEUTRAL')
        weekly_trend = timeframe_analysis.get('weekly', {}).get('trend', 'NEUTRAL')
        monthly_trend = timeframe_analysis.get('monthly', {}).get('trend', 'NEUTRAL')

        # Determine alignment
        if daily_trend == weekly_trend == monthly_trend == 'UPTREND':
            alignment = 'PERFECT_BULLISH_ALIGNMENT'
            signal = 'STRONG_BUY'
            confidence = 0.95
        elif daily_trend == weekly_trend == monthly_trend == 'DOWNTREND':
            alignment = 'PERFECT_BEARISH_ALIGNMENT'
            signal = 'STRONG_SELL'
            confidence = 0.95
        elif weekly_trend == 'UPTREND' and monthly_trend == 'UPTREND':
            # Higher timeframes bullish, daily can vary
            if daily_trend == 'DOWNTREND':
                alignment = 'PULLBACK_IN_UPTREND'
                signal = 'BUY_THE_DIP'  # Excellent entry
                confidence = 0.85
            else:
                alignment = 'BULLISH_ALIGNMENT'
                signal = 'BUY'
                confidence = 0.75
        elif weekly_trend == 'DOWNTREND' and monthly_trend == 'DOWNTREND':
            # Higher timeframes bearish, daily can vary
            if daily_trend == 'UPTREND':
                alignment = 'BOUNCE_IN_DOWNTREND'
                signal = 'SELL_THE_RALLY'  # Exit opportunity
                confidence = 0.85
            else:
                alignment = 'BEARISH_ALIGNMENT'
                signal = 'SELL'
                confidence = 0.75
        elif monthly_trend == 'UPTREND':
            # Monthly bullish but mixed signals
            alignment = 'MIXED_CONSOLIDATION_BULLISH_BIAS'
            signal = 'WAIT_FOR_DAILY_CONFIRMATION'
            confidence = 0.60
        elif monthly_trend == 'DOWNTREND':
            # Monthly bearish but mixed signals
            alignment = 'MIXED_CONSOLIDATION_BEARISH_BIAS'
            signal = 'AVOID_LONGS'
            confidence = 0.60
        elif daily_trend == 'UPTREND' and weekly_trend == 'NEUTRAL' and monthly_trend == 'NEUTRAL':
            # Daily uptrend with neutral higher timeframes - short-term bullish opportunity
            alignment = 'SHORT_TERM_BULLISH'
            signal = 'BUY'
            confidence = 0.65
        elif daily_trend == 'DOWNTREND' and weekly_trend == 'NEUTRAL' and monthly_trend == 'NEUTRAL':
            # Daily downtrend with neutral higher timeframes - short-term bearish
            alignment = 'SHORT_TERM_BEARISH'
            signal = 'SELL'
            confidence = 0.65
        elif daily_trend == 'UPTREND':
            # Daily bullish with mixed higher timeframes
            alignment = 'MIXED_DAILY_BULLISH'
            signal = 'CAUTIOUS_BUY'
            confidence = 0.55
        elif daily_trend == 'DOWNTREND':
            # Daily bearish with mixed higher timeframes
            alignment = 'MIXED_DAILY_BEARISH'
            signal = 'CAUTIOUS_SELL'
            confidence = 0.55
        else:
            # Check if all timeframes are neutral (range-bound opportunity)
            if daily_trend == 'NEUTRAL' and weekly_trend == 'NEUTRAL' and monthly_trend == 'NEUTRAL':
                alignment = 'RANGE_BOUND'
                signal = 'RANGE_TRADE'
                confidence = 0.60  # Higher confidence for range trading
            else:
                alignment = 'NO_CLEAR_TREND'
                signal = 'NEUTRAL'
                confidence = 0.50

        # Calculate composite score
        daily_score = timeframe_analysis.get('daily', {}).get('score', 0)
        weekly_score = timeframe_analysis.get('weekly', {}).get('score', 0)
        monthly_score = timeframe_analysis.get('monthly', {}).get('score', 0)

        # Weight higher timeframes more heavily
        composite_score = (
            daily_score * 0.3 +
            weekly_score * 0.4 +
            monthly_score * 0.3
        )

        return {
            'alignment': alignment,
            'signal': signal,
            'confidence': confidence,
            'composite_score': composite_score,
            'timeframe_scores': timeframe_analysis,
            'daily_trend': daily_trend,
            'weekly_trend': weekly_trend,
            'monthly_trend': monthly_trend,
            'recommendation': TechnicalIndicators._get_mtf_recommendation(alignment, timeframe_analysis)
        }

    @staticmethod
    def _get_mtf_recommendation(alignment: str, timeframe_analysis: Dict) -> str:
        """Get trading recommendation based on multi-timeframe alignment."""

        if alignment == 'PERFECT_BULLISH_ALIGNMENT':
            return "All timeframes bullish - Strong buy signal. Enter on any pullback to MA 20 on daily."

        elif alignment == 'PULLBACK_IN_UPTREND':
            daily_rsi = timeframe_analysis.get('daily', {}).get('rsi', 50)
            if daily_rsi < 40:
                return "Higher timeframes bullish, daily pullback with RSI < 40 - EXCELLENT BUY opportunity"
            else:
                return "Higher timeframes bullish, daily pullback - Good buy opportunity, wait for RSI < 40 for best entry"

        elif alignment == 'BULLISH_ALIGNMENT':
            return "Higher timeframes bullish - Buy on daily dips to VWAP or MA 20"

        elif alignment == 'PERFECT_BEARISH_ALIGNMENT':
            return "All timeframes bearish - Strong sell signal. Exit positions or short on rallies."

        elif alignment == 'BOUNCE_IN_DOWNTREND':
            daily_rsi = timeframe_analysis.get('daily', {}).get('rsi', 50)
            if daily_rsi > 60:
                return "Higher timeframes bearish, daily bounce with RSI > 60 - EXCELLENT SELL opportunity"
            else:
                return "Higher timeframes bearish, daily bounce - Consider taking profits or selling"

        elif alignment == 'BEARISH_ALIGNMENT':
            return "Higher timeframes bearish - Sell on daily rallies to VWAP or MA 20"

        elif alignment == 'MIXED_CONSOLIDATION_BULLISH_BIAS':
            return "Monthly bullish but consolidating - Wait for daily breakout above resistance"

        elif alignment == 'MIXED_CONSOLIDATION_BEARISH_BIAS':
            return "Monthly bearish but consolidating - Avoid longs, wait for clarity"

        elif alignment == 'SHORT_TERM_BULLISH':
            return "Daily uptrend with neutral higher timeframes - Favor long entries with tight stops (short-term trades only)"

        elif alignment == 'SHORT_TERM_BEARISH':
            return "Daily downtrend with neutral higher timeframes - Favor short entries or take profits (short-term trades)"

        elif alignment == 'MIXED_DAILY_BULLISH':
            return "Daily bullish but higher timeframes mixed - Cautiously favor longs on pullbacks with tight stops"

        elif alignment == 'MIXED_DAILY_BEARISH':
            return "Daily bearish but higher timeframes mixed - Cautiously favor shorts on rallies with tight stops"

        elif alignment == 'RANGE_BOUND':
            return "All timeframes neutral - Range-bound stock. Consider trading the range: sell resistance, buy support"

        else:
            return "No clear trend across timeframes - Stay on sidelines until alignment improves"

    @staticmethod
    def detect_support_resistance(
        data: pd.DataFrame,
        window: int = 20,
        tolerance: float = 0.02
    ) -> Dict[str, Any]:
        """
        Detect support and resistance levels.

        Args:
            data: DataFrame with OHLC data
            window: Lookback window
            tolerance: Price tolerance (2% default)

        Returns:
            Dictionary with support/resistance levels
        """
        if len(data) < window:
            return {'support': None, 'resistance': None}

        recent_high = data['high'].tail(window).max()
        recent_low = data['low'].tail(window).min()
        current_price = data['close'].iloc[-1]

        # Calculate distance to support/resistance
        distance_to_resistance = (recent_high - current_price) / current_price
        distance_to_support = (current_price - recent_low) / current_price

        return {
            'support': recent_low,
            'resistance': recent_high,
            'current_price': current_price,
            'distance_to_resistance': distance_to_resistance,
            'distance_to_support': distance_to_support,
            'near_support': distance_to_support < tolerance,
            'near_resistance': distance_to_resistance < tolerance
        }

    @classmethod
    def calculate_all_indicators(
        cls,
        data: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate all technical indicators for a dataset.

        Args:
            data: DataFrame with OHLC data (columns: open, high, low, close, volume)

        Returns:
            DataFrame with all indicators added
        """
        df = data.copy()

        # Moving averages
        df['ma_20'] = cls.calculate_sma(df['close'], 20)
        df['ma_50'] = cls.calculate_sma(df['close'], 50)
        df['ma_200'] = cls.calculate_sma(df['close'], 200)

        # RSI
        df['rsi_14'] = cls.calculate_rsi(df['close'], 14)

        # MACD
        macd = cls.calculate_macd(df['close'])
        df['macd'] = macd['macd']
        df['macd_signal'] = macd['signal']
        df['macd_histogram'] = macd['histogram']

        # Bollinger Bands
        bb = cls.calculate_bollinger_bands(df['close'])
        df['bb_upper'] = bb['upper']
        df['bb_middle'] = bb['middle']
        df['bb_lower'] = bb['lower']

        # ATR
        df['atr'] = cls.calculate_atr(df['high'], df['low'], df['close'])

        # VWAP (Volume Weighted Average Price)
        df['vwap'] = cls.calculate_vwap(df['high'], df['low'], df['close'], df['volume'])

        # Pivot Points
        pivots = cls.calculate_pivot_points(df['high'], df['low'], df['close'])
        df['pivot_point'] = pivots['pp']
        df['pivot_r1'] = pivots['r1']
        df['pivot_r2'] = pivots['r2']
        df['pivot_r3'] = pivots['r3']
        df['pivot_s1'] = pivots['s1']
        df['pivot_s2'] = pivots['s2']
        df['pivot_s3'] = pivots['s3']

        # Volume analysis
        df['volume_ma_20'] = cls.calculate_sma(df['volume'], 20)
        df['volume_ratio'] = df['volume'] / df['volume_ma_20']

        return df

    @staticmethod
    def generate_signals(data: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate trading signals from indicators.

        Args:
            data: DataFrame with indicators calculated

        Returns:
            Dictionary of trading signals
        """
        if data.empty or len(data) < 2:
            return {}

        latest = data.iloc[-1]
        prev = data.iloc[-2]

        signals = {}

        # RSI signals
        if pd.notna(latest['rsi_14']):
            signals['rsi'] = latest['rsi_14']
            signals['rsi_oversold'] = latest['rsi_14'] < 30
            signals['rsi_overbought'] = latest['rsi_14'] > 70

        # MACD signals
        if pd.notna(latest['macd']) and pd.notna(latest['macd_signal']):
            # Store MACD values for detailed reporting
            signals['macd'] = float(latest['macd'])
            signals['macd_signal'] = float(latest['macd_signal'])
            if pd.notna(latest['macd_histogram']):
                signals['macd_histogram'] = float(latest['macd_histogram'])
            
            # Store crossover signals
            signals['macd_bullish_crossover'] = (
                prev['macd'] < prev['macd_signal'] and
                latest['macd'] > latest['macd_signal']
            )
            signals['macd_bearish_crossover'] = (
                prev['macd'] > prev['macd_signal'] and
                latest['macd'] < latest['macd_signal']
            )

        # Moving average signals
        if pd.notna(latest['ma_20']) and pd.notna(latest['ma_50']):
            # Store MA values for detailed reporting
            signals['ma_20'] = float(latest['ma_20'])
            signals['ma_50'] = float(latest['ma_50'])
            if pd.notna(latest['ma_200']):
                signals['ma_200'] = float(latest['ma_200'])
            
            # Store position signals
            signals['price_above_ma20'] = latest['close'] > latest['ma_20']
            signals['price_below_ma20'] = latest['close'] <= latest['ma_20']
            signals['price_above_ma50'] = latest['close'] > latest['ma_50']
            signals['price_below_ma50'] = latest['close'] <= latest['ma_50']
            signals['ma20_above_ma50'] = latest['ma_20'] > latest['ma_50']

            if pd.notna(latest['ma_200']):
                signals['price_above_ma200'] = latest['close'] > latest['ma_200']

        # Volume signals
        if pd.notna(latest['volume_ratio']):
            signals['volume_spike'] = latest['volume_ratio'] > 1.5
            signals['volume_ratio'] = latest['volume_ratio']

        # Bollinger Bands
        if pd.notna(latest['bb_lower']) and pd.notna(latest['bb_upper']):
            # Calculate proximity to bands
            near_lower = latest['close'] < latest['bb_lower'] * 1.02
            near_upper = latest['close'] > latest['bb_upper'] * 0.98

            # Mutual exclusion: price can't be near both bands simultaneously
            # If somehow both are true (data error), determine which is closer
            if near_lower and near_upper:
                dist_to_lower = abs(latest['close'] - latest['bb_lower'])
                dist_to_upper = abs(latest['close'] - latest['bb_upper'])
                if dist_to_lower < dist_to_upper:
                    signals['near_bb_lower'] = True
                    signals['near_bb_upper'] = False
                else:
                    signals['near_bb_lower'] = False
                    signals['near_bb_upper'] = True
            else:
                signals['near_bb_lower'] = near_lower
                signals['near_bb_upper'] = near_upper

            signals['bb_upper'] = latest['bb_upper']
            signals['bb_middle'] = latest['bb_middle']
            signals['bb_lower'] = latest['bb_lower']

            # Calculate BB position (0-100%, where 0 = lower band, 100 = upper band)
            bb_range = latest['bb_upper'] - latest['bb_lower']
            if bb_range > 0:
                signals['bb_position_pct'] = ((latest['close'] - latest['bb_lower']) / bb_range) * 100
            else:
                signals['bb_position_pct'] = 50  # Default to middle if bands collapsed

        # VWAP signals
        if pd.notna(latest['vwap']):
            signals['vwap'] = latest['vwap']
            signals['price_above_vwap'] = latest['close'] > latest['vwap']
            signals['price_below_vwap'] = latest['close'] < latest['vwap']

            # Calculate distance from VWAP (in percentage)
            vwap_distance = ((latest['close'] - latest['vwap']) / latest['vwap']) * 100
            signals['vwap_distance_pct'] = vwap_distance

            # Strong signals based on VWAP position
            signals['significantly_above_vwap'] = vwap_distance > 2.0  # > 2% above
            signals['significantly_below_vwap'] = vwap_distance < -2.0  # > 2% below
            signals['near_vwap'] = abs(vwap_distance) < 0.5  # Within 0.5% of VWAP

        # Pivot Point signals
        if pd.notna(latest['pivot_point']):
            current_price = latest['close']
            pp = latest['pivot_point']

            # Store pivot levels
            signals['pivot_point'] = pp
            signals['pivot_r1'] = latest['pivot_r1']
            signals['pivot_r2'] = latest['pivot_r2']
            signals['pivot_r3'] = latest['pivot_r3']
            signals['pivot_s1'] = latest['pivot_s1']
            signals['pivot_s2'] = latest['pivot_s2']
            signals['pivot_s3'] = latest['pivot_s3']

            # Determine position relative to pivot
            signals['above_pivot'] = current_price > pp
            signals['below_pivot'] = current_price < pp

            # Identify which zone price is in
            if pd.notna(latest['pivot_r1']) and pd.notna(latest['pivot_s1']):
                if current_price > latest['pivot_r1']:
                    if pd.notna(latest['pivot_r2']) and current_price > latest['pivot_r2']:
                        signals['pivot_zone'] = 'above_r2'  # Strong bullish
                    else:
                        signals['pivot_zone'] = 'r1_to_r2'  # Bullish
                elif current_price > pp:
                    signals['pivot_zone'] = 'pp_to_r1'  # Mildly bullish
                elif current_price > latest['pivot_s1']:
                    signals['pivot_zone'] = 'pp_to_s1'  # Mildly bearish
                else:
                    if pd.notna(latest['pivot_s2']) and current_price > latest['pivot_s2']:
                        signals['pivot_zone'] = 's1_to_s2'  # Bearish
                    else:
                        signals['pivot_zone'] = 'below_s2'  # Strong bearish

                # Near support/resistance (within 1%)
                tolerance = 0.01
                signals['near_pivot_support'] = (
                    abs(current_price - latest['pivot_s1']) / current_price < tolerance or
                    (pd.notna(latest['pivot_s2']) and abs(current_price - latest['pivot_s2']) / current_price < tolerance)
                )
                signals['near_pivot_resistance'] = (
                    abs(current_price - latest['pivot_r1']) / current_price < tolerance or
                    (pd.notna(latest['pivot_r2']) and abs(current_price - latest['pivot_r2']) / current_price < tolerance)
                )

        # ATR for volatility context
        if pd.notna(latest['atr']):
            signals['atr'] = latest['atr']
            # ATR as percentage of price (useful for position sizing)
            signals['atr_pct'] = (latest['atr'] / latest['close']) * 100

        # Price momentum
        if len(data) >= 5:
            five_day_return = (latest['close'] / data.iloc[-5]['close']) - 1
            signals['five_day_return'] = five_day_return

        if len(data) >= 20:
            twenty_day_return = (latest['close'] / data.iloc[-20]['close']) - 1
            signals['twenty_day_return'] = twenty_day_return

        # RSI Divergence Detection (Phase 2 Enhancement)
        if len(data) >= 20 and pd.notna(latest['rsi_14']):
            from tradingagents.screener.indicators import TechnicalIndicators
            divergence = TechnicalIndicators.detect_rsi_divergence(
                data['close'],
                data['rsi_14'],
                lookback=20
            )
            signals['rsi_bullish_divergence'] = divergence['bullish_divergence']
            signals['rsi_bearish_divergence'] = divergence['bearish_divergence']
            signals['rsi_divergence_type'] = divergence['divergence_type']
            signals['rsi_divergence_strength'] = divergence['divergence_strength']

        # Fibonacci Retracement Levels (Phase 2 Enhancement)
        if len(data) >= 20:
            from tradingagents.screener.indicators import TechnicalIndicators
            fib_levels = TechnicalIndicators.calculate_fibonacci_retracements(data, lookback=20)
            if fib_levels['fib_500']:
                signals['fib_swing_high'] = fib_levels['swing_high']
                signals['fib_swing_low'] = fib_levels['swing_low']
                signals['fib_236'] = fib_levels['fib_236']
                signals['fib_382'] = fib_levels['fib_382']
                signals['fib_500'] = fib_levels['fib_500']
                signals['fib_618'] = fib_levels['fib_618']
                signals['fib_786'] = fib_levels['fib_786']
                signals['current_fib_level'] = fib_levels['current_fib_level']

                # Determine if price is near key Fibonacci support
                current_price = latest['close']
                tolerance = (fib_levels['swing_high'] - fib_levels['swing_low']) * 0.02
                signals['near_fib_support'] = (
                    abs(current_price - fib_levels['fib_618']) < tolerance or
                    abs(current_price - fib_levels['fib_500']) < tolerance
                )

        # Bollinger Band Squeeze Detection (Phase 2 Enhancement)
        if len(data) >= 20 and pd.notna(latest['bb_upper']):
            from tradingagents.screener.indicators import TechnicalIndicators
            bb_squeeze = TechnicalIndicators.detect_bollinger_band_squeeze(
                data[['bb_upper', 'bb_middle', 'bb_lower']].copy(),
                lookback=20
            )
            signals['bb_squeeze_detected'] = bb_squeeze['squeeze_detected']
            signals['bb_squeeze_strength'] = bb_squeeze['squeeze_strength']
            signals['bb_width'] = bb_squeeze['bb_width']
            signals['bb_width_percentile'] = bb_squeeze['bb_width_percentile']

        # Volume Profile Analysis (Phase 3 Enhancement)
        if len(data) >= 20 and 'volume' in data.columns:
            from tradingagents.screener.indicators import TechnicalIndicators
            volume_profile = TechnicalIndicators.calculate_volume_profile(data, lookback=20)
            if volume_profile.get('poc'):
                signals['vp_poc'] = volume_profile['poc']
                signals['vp_vah'] = volume_profile['vah']
                signals['vp_val'] = volume_profile['val']
                signals['vp_profile_position'] = volume_profile['profile_position']
                signals['vp_position_signal'] = volume_profile['position_signal']
                signals['vp_distance_to_poc_pct'] = volume_profile['distance_to_poc_pct']

                # Store top volume nodes
                if volume_profile.get('volume_nodes'):
                    signals['vp_high_volume_nodes'] = len(volume_profile['volume_nodes'])
                if volume_profile.get('low_volume_nodes'):
                    signals['vp_low_volume_nodes'] = len(volume_profile['low_volume_nodes'])

        # Order Flow Analysis (Phase 3 Enhancement)
        if len(data) >= 10 and 'volume' in data.columns and 'open' in data.columns:
            from tradingagents.screener.indicators import TechnicalIndicators
            order_flow = TechnicalIndicators.analyze_order_flow(data, lookback=10)
            signals['of_signal'] = order_flow['order_flow_signal']
            signals['of_institutional_activity'] = order_flow['institutional_activity']
            signals['of_signal_strength'] = order_flow['signal_strength']
            signals['of_buying_pct'] = order_flow['buying_pct']
            signals['of_selling_pct'] = order_flow['selling_pct']
            signals['of_volume_spike'] = order_flow['volume_spike_detected']

            # Flag strong institutional signals
            signals['institutional_accumulation'] = (
                order_flow['institutional_activity'] == 'ACCUMULATION'
            )
            signals['institutional_distribution'] = (
                order_flow['institutional_activity'] == 'DISTRIBUTION'
            )

        # Multi-Timeframe Analysis (Phase 3 Enhancement)
        # Proceed if we have enough data (index conversion handled below)
        if len(data) >= 60:
            from tradingagents.screener.indicators import TechnicalIndicators

            # Ensure datetime index for resampling
            if isinstance(data.index, pd.DatetimeIndex):
                data_indexed = data.copy()
            elif 'price_date' in data.columns:
                # Use price_date column as index
                data_indexed = data.copy()
                data_indexed['price_date'] = pd.to_datetime(data_indexed['price_date'])
                data_indexed = data_indexed.set_index('price_date')
            else:
                # Try to convert existing index to datetime
                data_indexed = data.copy()
                try:
                    data_indexed.index = pd.to_datetime(data_indexed.index)
                except (ValueError, TypeError):
                    # If conversion fails, skip multi-timeframe analysis
                    logger.debug("Cannot convert index to datetime for multi-timeframe analysis")
                    data_indexed = None

            if data_indexed is not None:
                mtf_analysis = TechnicalIndicators.analyze_multi_timeframe(data_indexed)
                if mtf_analysis['alignment'] != 'INSUFFICIENT_DATA':
                    signals['mtf_alignment'] = mtf_analysis['alignment']
                    signals['mtf_signal'] = mtf_analysis['signal']
                    signals['mtf_confidence'] = mtf_analysis['confidence']
                    signals['mtf_composite_score'] = mtf_analysis['composite_score']
                    signals['mtf_daily_trend'] = mtf_analysis['daily_trend']
                    signals['mtf_weekly_trend'] = mtf_analysis['weekly_trend']
                    signals['mtf_monthly_trend'] = mtf_analysis['monthly_trend']
                    signals['mtf_recommendation'] = mtf_analysis['recommendation']

        return signals
