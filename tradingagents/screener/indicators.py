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
            signals['price_above_ma20'] = latest['close'] > latest['ma_20']
            signals['price_above_ma50'] = latest['close'] > latest['ma_50']
            signals['ma20_above_ma50'] = latest['ma_20'] > latest['ma_50']

            if pd.notna(latest['ma_200']):
                signals['price_above_ma200'] = latest['close'] > latest['ma_200']

        # Volume signals
        if pd.notna(latest['volume_ratio']):
            signals['volume_spike'] = latest['volume_ratio'] > 1.5
            signals['volume_ratio'] = latest['volume_ratio']

        # Bollinger Bands
        if pd.notna(latest['bb_lower']) and pd.notna(latest['bb_upper']):
            signals['near_bb_lower'] = latest['close'] < latest['bb_lower'] * 1.02
            signals['near_bb_upper'] = latest['close'] > latest['bb_upper'] * 0.98

        # Price momentum
        if len(data) >= 5:
            five_day_return = (latest['close'] / data.iloc[-5]['close']) - 1
            signals['five_day_return'] = five_day_return

        if len(data) >= 20:
            twenty_day_return = (latest['close'] / data.iloc[-20]['close']) - 1
            signals['twenty_day_return'] = twenty_day_return

        return signals
