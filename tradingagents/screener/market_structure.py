# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Market Structure Detection

Detects institutional trading patterns including:
- Swing points (highs and lows)
- Break of Structure (BOS)
- Change of Character (Chach)
- Inducements (fake breakouts)
- Liquidity sweeps
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class MarketStructure:
    """Detect market structure patterns for institutional trading analysis."""
    
    @staticmethod
    def detect_swing_points(
        data: pd.DataFrame,
        lookback: int = 5,
        min_swing_strength: float = 0.01
    ) -> Dict[str, Any]:
        """
        Detect swing highs and swing lows.
        
        Swing points are local maxima (highs) and minima (lows) that represent
        key price levels where institutions may place orders.
        
        Args:
            data: DataFrame with 'high', 'low', 'close' columns
            lookback: Number of bars on each side to confirm swing point
            min_swing_strength: Minimum price move to qualify as swing (1% default)
        
        Returns:
            Dictionary with swing highs and lows
        """
        if len(data) < lookback * 2 + 1:
            return {
                'swing_highs': [],
                'swing_lows': [],
                'latest_swing_high': None,
                'latest_swing_low': None
            }
        
        high = data['high']
        low = data['low']
        close = data['close']
        
        swing_highs = []
        swing_lows = []
        
        # Detect swing highs
        for i in range(lookback, len(data) - lookback):
            current_high = high.iloc[i]
            
            # Check if current high is higher than surrounding bars
            is_swing_high = True
            for j in range(i - lookback, i + lookback + 1):
                if j != i and high.iloc[j] >= current_high:
                    is_swing_high = False
                    break
            
            if is_swing_high:
                # Check swing strength (minimum move from previous swing)
                if not swing_highs or (current_high / swing_highs[-1][1] - 1) >= min_swing_strength:
                    swing_highs.append((i, current_high, data.index[i]))
        
        # Detect swing lows
        for i in range(lookback, len(data) - lookback):
            current_low = low.iloc[i]
            
            # Check if current low is lower than surrounding bars
            is_swing_low = True
            for j in range(i - lookback, i + lookback + 1):
                if j != i and low.iloc[j] <= current_low:
                    is_swing_low = False
                    break
            
            if is_swing_low:
                # Check swing strength (minimum move from previous swing)
                if not swing_lows or (swing_lows[-1][1] / current_low - 1) >= min_swing_strength:
                    swing_lows.append((i, current_low, data.index[i]))
        
        # Get latest swing points
        latest_swing_high = swing_highs[-1] if swing_highs else None
        latest_swing_low = swing_lows[-1] if swing_lows else None
        
        return {
            'swing_highs': swing_highs,
            'swing_lows': swing_lows,
            'latest_swing_high': latest_swing_high,
            'latest_swing_low': latest_swing_low
        }
    
    @staticmethod
    def identify_structure_breaks(
        data: pd.DataFrame,
        swing_points: Dict[str, Any],
        min_break_strength: float = 0.005
    ) -> Dict[str, Any]:
        """
        Identify Break of Structure (BOS) and Change of Character (Chach).
        
        - BOS: Price breaks previous swing high/low, indicating trend continuation
        - Chach: Price breaks swing point in opposite direction, indicating potential reversal
        
        Args:
            data: DataFrame with price data
            swing_points: Result from detect_swing_points()
            min_break_strength: Minimum price move to confirm break (0.5% default)
        
        Returns:
            Dictionary with BOS and Chach signals
        """
        if not swing_points['swing_highs'] or not swing_points['swing_lows']:
            return {
                'bos_bullish': False,
                'bos_bearish': False,
                'chach_bullish': False,
                'chach_bearish': False,
                'structure_breaks': []
            }
        
        current_price = data['close'].iloc[-1]
        current_high = data['high'].iloc[-1]
        current_low = data['low'].iloc[-1]
        
        structure_breaks = []
        
        # Get latest swing points
        latest_swing_high = swing_points['latest_swing_high']
        latest_swing_low = swing_points['latest_swing_low']
        
        # Check for Bullish BOS (break above previous swing high)
        bos_bullish = False
        if latest_swing_high:
            swing_high_price = latest_swing_high[1]
            if current_high > swing_high_price * (1 + min_break_strength):
                bos_bullish = True
                structure_breaks.append({
                    'type': 'BOS_BULLISH',
                    'price': current_high,
                    'broken_level': swing_high_price,
                    'strength': (current_high / swing_high_price - 1) * 100
                })
        
        # Check for Bearish BOS (break below previous swing low)
        bos_bearish = False
        if latest_swing_low:
            swing_low_price = latest_swing_low[1]
            if current_low < swing_low_price * (1 - min_break_strength):
                bos_bearish = True
                structure_breaks.append({
                    'type': 'BOS_BEARISH',
                    'price': current_low,
                    'broken_level': swing_low_price,
                    'strength': (1 - current_low / swing_low_price) * 100
                })
        
        # Check for Bullish Chach (break above previous swing low in downtrend)
        chach_bullish = False
        if latest_swing_low and len(swing_points['swing_highs']) >= 2:
            # Check if we're in a downtrend (lower highs)
            last_two_highs = swing_points['swing_highs'][-2:]
            if last_two_highs[1][1] < last_two_highs[0][1]:  # Lower high = downtrend
                swing_low_price = latest_swing_low[1]
                if current_high > swing_low_price * (1 + min_break_strength):
                    chach_bullish = True
                    structure_breaks.append({
                        'type': 'CHACH_BULLISH',
                        'price': current_high,
                        'broken_level': swing_low_price,
                        'strength': (current_high / swing_low_price - 1) * 100
                    })
        
        # Check for Bearish Chach (break below previous swing high in uptrend)
        chach_bearish = False
        if latest_swing_high and len(swing_points['swing_lows']) >= 2:
            # Check if we're in an uptrend (higher lows)
            last_two_lows = swing_points['swing_lows'][-2:]
            if last_two_lows[1][1] > last_two_lows[0][1]:  # Higher low = uptrend
                swing_high_price = latest_swing_high[1]
                if current_low < swing_high_price * (1 - min_break_strength):
                    chach_bearish = True
                    structure_breaks.append({
                        'type': 'CHACH_BEARISH',
                        'price': current_low,
                        'broken_level': swing_high_price,
                        'strength': (1 - current_low / swing_high_price) * 100
                    })
        
        return {
            'bos_bullish': bos_bullish,
            'bos_bearish': bos_bearish,
            'chach_bullish': chach_bullish,
            'chach_bearish': chach_bearish,
            'structure_breaks': structure_breaks
        }
    
    @staticmethod
    def detect_inducements(
        data: pd.DataFrame,
        structure_breaks: Dict[str, Any],
        volume: pd.Series,
        tolerance: float = 0.001
    ) -> Dict[str, Any]:
        """
        Detect inducements (fake breakouts designed to trap retail traders).
        
        Inducements are characterized by:
        - Price breaks structure but quickly reverses
        - Low volume on the break
        - Price returns to previous range within a few bars
        
        Args:
            data: DataFrame with price data
            structure_breaks: Result from identify_structure_breaks()
            volume: Volume series
            tolerance: Tolerance for reversal detection (0.1% default)
        
        Returns:
            Dictionary with inducement detection results
        """
        if not structure_breaks.get('structure_breaks'):
            return {
                'has_inducement': False,
                'inducement_type': None,
                'inducement_confidence': 0.0
            }
        
        # Check recent structure breaks
        recent_breaks = structure_breaks['structure_breaks']
        if not recent_breaks:
            return {
                'has_inducement': False,
                'inducement_type': None,
                'inducement_confidence': 0.0
            }
        
        # Get latest break
        latest_break = recent_breaks[-1]
        break_type = latest_break['type']
        
        # Check if price reversed after break (inducement signal)
        current_price = data['close'].iloc[-1]
        broken_level = latest_break['broken_level']
        
        is_inducement = False
        confidence = 0.0
        
        # For bullish breaks, check if price fell back below level
        if 'BULLISH' in break_type:
            if current_price < broken_level * (1 - tolerance):
                is_inducement = True
                # Confidence based on how far price fell
                confidence = min(1.0, (broken_level - current_price) / broken_level)
        
        # For bearish breaks, check if price rose back above level
        elif 'BEARISH' in break_type:
            if current_price > broken_level * (1 + tolerance):
                is_inducement = True
                # Confidence based on how far price rose
                confidence = min(1.0, (current_price - broken_level) / broken_level)
        
        # Check volume (low volume on break = higher inducement probability)
        if is_inducement and len(volume) >= 20:
            avg_volume = volume.tail(20).mean()
            break_volume = volume.iloc[-1] if len(volume) > 0 else avg_volume
            volume_ratio = break_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Low volume increases inducement confidence
            if volume_ratio < 0.8:
                confidence = min(1.0, confidence + 0.2)
        
        return {
            'has_inducement': is_inducement,
            'inducement_type': break_type if is_inducement else None,
            'inducement_confidence': confidence
        }
    
    @staticmethod
    def detect_liquidity_sweeps(
        data: pd.DataFrame,
        swing_points: Dict[str, Any],
        tolerance: float = 0.001
    ) -> Dict[str, Any]:
        """
        Detect liquidity sweeps (stop loss hunts).
        
        Liquidity sweeps occur when price briefly moves beyond a key level
        (triggering stop losses) before reversing in the intended direction.
        
        Args:
            data: DataFrame with price data
            swing_points: Result from detect_swing_points()
            tolerance: Tolerance for sweep detection (0.1% default)
        
        Returns:
            Dictionary with liquidity sweep detection results
        """
        if not swing_points['swing_highs'] and not swing_points['swing_lows']:
            return {
                'has_sweep': False,
                'sweep_type': None,
                'sweep_confidence': 0.0
            }
        
        current_high = data['high'].iloc[-1]
        current_low = data['low'].iloc[-1]
        current_close = data['close'].iloc[-1]
        
        has_sweep = False
        sweep_type = None
        confidence = 0.0
        
        # Check for bullish sweep (price briefly broke below swing low then reversed up)
        if swing_points['latest_swing_low']:
            swing_low = swing_points['latest_swing_low'][1]
            
            # Check if low broke below swing low but close is above
            if current_low < swing_low * (1 - tolerance) and current_close > swing_low:
                has_sweep = True
                sweep_type = 'BULLISH_SWEEP'
                # Confidence based on how far price swept and reversed
                sweep_distance = (swing_low - current_low) / swing_low
                reversal_distance = (current_close - swing_low) / swing_low
                confidence = min(1.0, (sweep_distance + reversal_distance) * 10)
        
        # Check for bearish sweep (price briefly broke above swing high then reversed down)
        if swing_points['latest_swing_high']:
            swing_high = swing_points['latest_swing_high'][1]
            
            # Check if high broke above swing high but close is below
            if current_high > swing_high * (1 + tolerance) and current_close < swing_high:
                has_sweep = True
                sweep_type = 'BEARISH_SWEEP'
                # Confidence based on how far price swept and reversed
                sweep_distance = (current_high - swing_high) / swing_high
                reversal_distance = (swing_high - current_close) / swing_high
                confidence = min(1.0, (sweep_distance + reversal_distance) * 10)
        
        return {
            'has_sweep': has_sweep,
            'sweep_type': sweep_type,
            'sweep_confidence': confidence
        }
    
    @classmethod
    def analyze_market_structure(
        cls,
        data: pd.DataFrame,
        volume: pd.Series,
        lookback: int = 5,
        min_swing_strength: float = 0.01,
        min_break_strength: float = 0.005
    ) -> Dict[str, Any]:
        """
        Complete market structure analysis.
        
        Args:
            data: DataFrame with 'high', 'low', 'close' columns
            volume: Volume series
            lookback: Bars to look back for swing confirmation
            min_swing_strength: Minimum swing strength (1% default)
            min_break_strength: Minimum break strength (0.5% default)
        
        Returns:
            Complete market structure analysis
        """
        # Detect swing points
        swing_points = cls.detect_swing_points(
            data, lookback=lookback, min_swing_strength=min_swing_strength
        )
        
        # Identify structure breaks
        structure_breaks = cls.identify_structure_breaks(
            data, swing_points, min_break_strength=min_break_strength
        )
        
        # Detect inducements
        inducements = cls.detect_inducements(
            data, structure_breaks, volume
        )
        
        # Detect liquidity sweeps
        sweeps = cls.detect_liquidity_sweeps(
            data, swing_points
        )
        
        return {
            'swing_points': swing_points,
            'structure_breaks': structure_breaks,
            'inducements': inducements,
            'sweeps': sweeps,
            'current_trend': cls._determine_trend(swing_points)
        }
    
    @staticmethod
    def _determine_trend(swing_points: Dict[str, Any]) -> str:
        """Determine current trend from swing points."""
        if not swing_points['swing_highs'] or not swing_points['swing_lows']:
            return 'UNKNOWN'
        
        # Check if we have enough swing points
        if len(swing_points['swing_highs']) < 2 or len(swing_points['swing_lows']) < 2:
            return 'UNKNOWN'
        
        # Check for higher highs and higher lows (uptrend)
        last_two_highs = swing_points['swing_highs'][-2:]
        last_two_lows = swing_points['swing_lows'][-2:]
        
        higher_highs = last_two_highs[1][1] > last_two_highs[0][1]
        higher_lows = last_two_lows[1][1] > last_two_lows[0][1]
        
        if higher_highs and higher_lows:
            return 'UPTREND'
        
        # Check for lower highs and lower lows (downtrend)
        lower_highs = last_two_highs[1][1] < last_two_highs[0][1]
        lower_lows = last_two_lows[1][1] < last_two_lows[0][1]
        
        if lower_highs and lower_lows:
            return 'DOWNTREND'
        
        return 'RANGING'

