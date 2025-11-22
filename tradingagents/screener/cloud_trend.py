# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
High Low Cloud Trend

Calculates dynamic support/resistance bands based on highest high and lowest low.
Identifies trend reversals when price enters the cloud.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class HighLowCloudTrend:
    """Calculate and analyze High Low Cloud Trend indicator."""
    
    @staticmethod
    def calculate_cloud_bands(
        data: pd.DataFrame,
        period: int = 20
    ) -> pd.DataFrame:
        """
        Calculate High Low Cloud bands.
        
        The cloud is formed by:
        - Upper band: Highest high over period
        - Lower band: Lowest low over period
        
        Args:
            data: DataFrame with 'high', 'low', 'close' columns
            period: Period for cloud calculation (20 default)
        
        Returns:
            DataFrame with cloud bands added
        """
        result = data.copy()
        
        # Calculate rolling highest high and lowest low
        result['cloud_upper'] = data['high'].rolling(window=period).max()
        result['cloud_lower'] = data['low'].rolling(window=period).min()
        
        # Calculate cloud midpoint
        result['cloud_mid'] = (result['cloud_upper'] + result['cloud_lower']) / 2
        
        # Calculate cloud width (as percentage)
        result['cloud_width_pct'] = (
            (result['cloud_upper'] - result['cloud_lower']) / result['cloud_mid'] * 100
        )
        
        return result
    
    @staticmethod
    def detect_cloud_entry(
        data: pd.DataFrame,
        cloud_bands: pd.DataFrame
    ) -> pd.Series:
        """
        Detect when price enters the cloud.
        
        Price entering the cloud suggests potential trend reversal.
        
        Args:
            data: Original DataFrame with price data
            cloud_bands: DataFrame with cloud bands (from calculate_cloud_bands)
        
        Returns:
            Series indicating cloud entry status
        """
        close = data['close']
        cloud_upper = cloud_bands['cloud_upper']
        cloud_lower = cloud_bands['cloud_lower']
        
        # Price is in cloud when between upper and lower bands
        in_cloud = (close >= cloud_lower) & (close <= cloud_upper)
        
        # Detect entry (price just entered cloud)
        cloud_entry = pd.Series(False, index=data.index)
        for i in range(1, len(data)):
            if in_cloud.iloc[i] and not in_cloud.iloc[i-1]:
                cloud_entry.iloc[i] = True
        
        return cloud_entry
    
    @staticmethod
    def determine_cloud_direction(
        data: pd.DataFrame,
        cloud_bands: pd.DataFrame
    ) -> pd.Series:
        """
        Determine if cloud is bullish or bearish.
        
        - Bullish: Price above cloud midpoint
        - Bearish: Price below cloud midpoint
        
        Args:
            data: Original DataFrame with price data
            cloud_bands: DataFrame with cloud bands
        
        Returns:
            Series with 'BULLISH', 'BEARISH', or 'NEUTRAL'
        """
        close = data['close']
        cloud_mid = cloud_bands['cloud_mid']
        
        cloud_direction = pd.Series('NEUTRAL', index=data.index)
        cloud_direction[close > cloud_mid] = 'BULLISH'
        cloud_direction[close < cloud_mid] = 'BEARISH'
        
        return cloud_direction
    
    @staticmethod
    def detect_cloud_reversal(
        data: pd.DataFrame,
        cloud_bands: pd.DataFrame,
        cloud_direction: pd.Series,
        min_reversal_strength: float = 0.003
    ) -> Dict[str, Any]:
        """
        Detect potential trend reversals based on cloud interaction.
        
        Reversal signals:
        - Price enters cloud from above (bearish reversal)
        - Price enters cloud from below (bullish reversal)
        - Price crosses cloud midpoint (direction change)
        
        Args:
            data: Original DataFrame with price data
            cloud_bands: DataFrame with cloud bands
            cloud_direction: Cloud direction series
            min_reversal_strength: Minimum move to confirm reversal (0.3% default)
        
        Returns:
            Dictionary with reversal signals
        """
        close = data['close']
        cloud_upper = cloud_bands['cloud_upper']
        cloud_lower = cloud_bands['cloud_lower']
        cloud_mid = cloud_bands['cloud_mid']
        
        # Check if price is in cloud
        in_cloud = (close >= cloud_lower) & (close <= cloud_upper)
        current_in_cloud = in_cloud.iloc[-1] if len(in_cloud) > 0 else False
        
        # Get current values
        current_price = close.iloc[-1] if len(close) > 0 else None
        current_direction = cloud_direction.iloc[-1] if len(cloud_direction) > 0 else 'NEUTRAL'
        
        if current_price is None:
            return {
                'has_reversal': False,
                'reversal_type': None,
                'reversal_strength': 0.0,
                'in_cloud': False
            }
        
        # Check for bullish reversal (price entering cloud from below)
        bullish_reversal = False
        if current_in_cloud and len(close) >= 2:
            prev_price = close.iloc[-2]
            prev_in_cloud = in_cloud.iloc[-2] if len(in_cloud) > 1 else False
            
            if not prev_in_cloud and prev_price < cloud_lower.iloc[-2]:
                # Price was below cloud, now entered
                move_strength = (current_price - prev_price) / prev_price
                if move_strength >= min_reversal_strength:
                    bullish_reversal = True
        
        # Check for bearish reversal (price entering cloud from above)
        bearish_reversal = False
        if current_in_cloud and len(close) >= 2:
            prev_price = close.iloc[-2]
            prev_in_cloud = in_cloud.iloc[-2] if len(in_cloud) > 1 else False
            
            if not prev_in_cloud and prev_price > cloud_upper.iloc[-2]:
                # Price was above cloud, now entered
                move_strength = (prev_price - current_price) / prev_price
                if move_strength >= min_reversal_strength:
                    bearish_reversal = True
        
        # Check for midpoint crossover (direction change)
        midpoint_crossover = False
        crossover_type = None
        if len(close) >= 2:
            prev_price = close.iloc[-2]
            prev_direction = cloud_direction.iloc[-2] if len(cloud_direction) > 1 else 'NEUTRAL'
            current_mid = cloud_mid.iloc[-1] if len(cloud_mid) > 0 else None
            
            if current_mid:
                # Bullish crossover: price crosses above midpoint
                if prev_price <= current_mid and current_price > current_mid:
                    midpoint_crossover = True
                    crossover_type = 'BULLISH'
                # Bearish crossover: price crosses below midpoint
                elif prev_price >= current_mid and current_price < current_mid:
                    midpoint_crossover = True
                    crossover_type = 'BEARISH'
        
        # Determine overall reversal
        has_reversal = bullish_reversal or bearish_reversal or midpoint_crossover
        reversal_type = None
        reversal_strength = 0.0
        
        if bullish_reversal:
            reversal_type = 'BULLISH'
            reversal_strength = min(1.0, (current_price - cloud_lower.iloc[-1]) / cloud_lower.iloc[-1] * 100)
        elif bearish_reversal:
            reversal_type = 'BEARISH'
            reversal_strength = min(1.0, (cloud_upper.iloc[-1] - current_price) / cloud_upper.iloc[-1] * 100)
        elif midpoint_crossover:
            reversal_type = crossover_type
            reversal_strength = 0.5  # Moderate strength for midpoint crossovers
        
        return {
            'has_reversal': has_reversal,
            'reversal_type': reversal_type,
            'reversal_strength': reversal_strength,
            'in_cloud': current_in_cloud,
            'cloud_direction': current_direction
        }
    
    @classmethod
    def analyze_cloud_trend(
        cls,
        data: pd.DataFrame,
        period: int = 20,
        min_reversal_strength: float = 0.003
    ) -> Dict[str, Any]:
        """
        Complete High Low Cloud Trend analysis.
        
        Args:
            data: DataFrame with 'high', 'low', 'close' columns
            period: Period for cloud calculation
            min_reversal_strength: Minimum reversal strength
        
        Returns:
            Complete cloud trend analysis
        """
        # Calculate cloud bands
        cloud_bands = cls.calculate_cloud_bands(data, period=period)
        
        # Detect cloud entry
        cloud_entry = cls.detect_cloud_entry(data, cloud_bands)
        
        # Determine cloud direction
        cloud_direction = cls.determine_cloud_direction(data, cloud_bands)
        
        # Detect reversals
        reversal = cls.detect_cloud_reversal(
            data, cloud_bands, cloud_direction, min_reversal_strength=min_reversal_strength
        )
        
        # Get current cloud values
        current_upper = cloud_bands['cloud_upper'].iloc[-1] if len(cloud_bands) > 0 else None
        current_lower = cloud_bands['cloud_lower'].iloc[-1] if len(cloud_bands) > 0 else None
        current_mid = cloud_bands['cloud_mid'].iloc[-1] if len(cloud_bands) > 0 else None
        current_width = cloud_bands['cloud_width_pct'].iloc[-1] if len(cloud_bands) > 0 else None
        
        return {
            'cloud_bands': cloud_bands,
            'cloud_entry': cloud_entry,
            'cloud_direction': cloud_direction,
            'reversal': reversal,
            'current_upper': current_upper,
            'current_lower': current_lower,
            'current_mid': current_mid,
            'current_width_pct': current_width
        }

