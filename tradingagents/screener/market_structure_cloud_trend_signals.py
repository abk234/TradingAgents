# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Market Structure and Cloud Trend Signal Generation

Generates trading signals based on Market Structure and High Low Cloud Trend.
"""

import pandas as pd
from typing import Dict, Any, Optional
import logging

from tradingagents.screener.market_structure import MarketStructure
from tradingagents.screener.cloud_trend import HighLowCloudTrend
from tradingagents.screener.indicators import TechnicalIndicators

logger = logging.getLogger(__name__)


class MarketStructureCloudTrendSignalGenerator:
    """Generate trading signals based on Market Structure and Cloud Trend strategy."""
    
    @staticmethod
    def calculate_entry_exit_levels(
        entry_price: float,
        atr: float,
        timeframe: str = "swing"
    ) -> Dict[str, float]:
        """
        Calculate stop loss and take profit based on ATR.
        
        Args:
            entry_price: Entry price
            atr: Average True Range value
            timeframe: 'swing' or 'scalp'
        
        Returns:
            Dictionary with stop_loss and take_profit
        """
        if timeframe == "swing":
            stop_multiplier = 1.5
            target_multiplier = 2.5
        else:  # scalping
            stop_multiplier = 0.75
            target_multiplier = 1.25
        
        stop_loss = entry_price - (atr * stop_multiplier)
        take_profit = entry_price + (atr * target_multiplier)
        
        return {
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'risk_reward_ratio': target_multiplier / stop_multiplier
        }
    
    @staticmethod
    def generate_signals(
        data: pd.DataFrame,
        market_structure: Dict[str, Any],
        cloud_trend: Dict[str, Any],
        atr: float,
        volume: pd.Series,
        timeframe: str = "swing",
        min_confidence: int = 70,
        min_volume_confirmation: float = 1.2
    ) -> Dict[str, Any]:
        """
        Generate trading signals based on Market Structure and Cloud Trend strategy.
        
        Entry Signals:
        - BUY: BOS bullish with cloud trend confirmation
        - BUY: Chach bullish with cloud entry
        - SELL: BOS bearish with cloud trend confirmation
        - SELL: Chach bearish with cloud entry
        
        Filters:
        - Must pass inducement validation
        - Volume confirmation required
        - Structure confirmation required
        
        Args:
            data: DataFrame with price data
            market_structure: Result from MarketStructure.analyze_market_structure()
            cloud_trend: Result from HighLowCloudTrend.analyze_cloud_trend()
            atr: Average True Range value
            volume: Volume series
            timeframe: 'swing' or 'scalp'
            min_confidence: Minimum confidence to take trade (70 default)
            min_volume_confirmation: Minimum volume ratio (1.2 = 20% above average)
        
        Returns:
            Dictionary with trading signals and confidence
        """
        current_price = data['close'].iloc[-1] if len(data) > 0 else None
        if current_price is None:
            return {
                'signal': 'WAIT',
                'confidence': 0,
                'reasoning': 'Insufficient data',
                'entry_price': None,
                'stop_loss': None,
                'take_profit': None
            }
        
        # Get structure breaks
        structure_breaks = market_structure.get('structure_breaks', {})
        bos_bullish = structure_breaks.get('bos_bullish', False)
        bos_bearish = structure_breaks.get('bos_bearish', False)
        chach_bullish = structure_breaks.get('chach_bullish', False)
        chach_bearish = structure_breaks.get('chach_bearish', False)
        
        # Get inducement detection
        inducements = market_structure.get('inducements', {})
        has_inducement = inducements.get('has_inducement', False)
        
        # Get cloud trend
        cloud_reversal = cloud_trend.get('reversal', {})
        cloud_has_reversal = cloud_reversal.get('has_reversal', False)
        cloud_reversal_type = cloud_reversal.get('reversal_type')
        cloud_direction = cloud_reversal.get('cloud_direction', 'NEUTRAL')
        
        # Check volume confirmation
        volume_confirmed = False
        if len(volume) >= 20:
            avg_volume = volume.tail(20).mean()
            current_volume = volume.iloc[-1] if len(volume) > 0 else avg_volume
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            volume_confirmed = volume_ratio >= min_volume_confirmation
        
        # Generate signals
        signal = 'WAIT'
        confidence = 0
        reasoning_parts = []
        entry_price = current_price
        
        # BULLISH SIGNALS
        if bos_bullish or chach_bullish:
            # Check for inducement (filter out fake breakouts)
            if has_inducement:
                reasoning_parts.append("Structure break detected but inducement filter triggered - waiting")
                signal = 'WAIT'
                confidence = 30
            else:
                # Check cloud trend confirmation
                cloud_confirmed = False
                if cloud_has_reversal and cloud_reversal_type == 'BULLISH':
                    cloud_confirmed = True
                    reasoning_parts.append("Cloud trend reversal bullish")
                elif cloud_direction == 'BULLISH':
                    cloud_confirmed = True
                    reasoning_parts.append("Price above cloud (bullish)")
                
                if cloud_confirmed:
                    # Check volume confirmation
                    if volume_confirmed:
                        signal = 'BUY'
                        confidence = 75
                        if bos_bullish:
                            reasoning_parts.append("Bullish BOS with cloud and volume confirmation")
                        else:
                            reasoning_parts.append("Bullish Chach with cloud and volume confirmation")
                    else:
                        signal = 'WAIT'
                        confidence = 50
                        reasoning_parts.append("Structure break detected but volume not confirmed")
                else:
                    signal = 'WAIT'
                    confidence = 40
                    reasoning_parts.append("Structure break detected but cloud trend not confirmed")
        
        # BEARISH SIGNALS
        elif bos_bearish or chach_bearish:
            # Check for inducement
            if has_inducement:
                reasoning_parts.append("Structure break detected but inducement filter triggered - waiting")
                signal = 'WAIT'
                confidence = 30
            else:
                # Check cloud trend confirmation
                cloud_confirmed = False
                if cloud_has_reversal and cloud_reversal_type == 'BEARISH':
                    cloud_confirmed = True
                    reasoning_parts.append("Cloud trend reversal bearish")
                elif cloud_direction == 'BEARISH':
                    cloud_confirmed = True
                    reasoning_parts.append("Price below cloud (bearish)")
                
                if cloud_confirmed:
                    # Check volume confirmation
                    if volume_confirmed:
                        signal = 'SELL'
                        confidence = 75
                        if bos_bearish:
                            reasoning_parts.append("Bearish BOS with cloud and volume confirmation")
                        else:
                            reasoning_parts.append("Bearish Chach with cloud and volume confirmation")
                    else:
                        signal = 'WAIT'
                        confidence = 50
                        reasoning_parts.append("Structure break detected but volume not confirmed")
                else:
                    signal = 'WAIT'
                    confidence = 40
                    reasoning_parts.append("Structure break detected but cloud trend not confirmed")
        
        # Check liquidity sweeps (additional confirmation)
        sweeps = market_structure.get('sweeps', {})
        if sweeps.get('has_sweep', False):
            sweep_type = sweeps.get('sweep_type')
            if sweep_type == 'BULLISH_SWEEP' and signal == 'BUY':
                confidence = min(100, confidence + 10)
                reasoning_parts.append("Bullish liquidity sweep confirmed")
            elif sweep_type == 'BEARISH_SWEEP' and signal == 'SELL':
                confidence = min(100, confidence + 10)
                reasoning_parts.append("Bearish liquidity sweep confirmed")
        
        # Apply minimum confidence filter
        if confidence < min_confidence:
            if signal != 'WAIT':
                signal = 'WAIT'
                reasoning_parts.append(f"Confidence {confidence}% below minimum {min_confidence}%")
        
        # Calculate entry/exit levels
        stop_loss = None
        take_profit = None
        if signal in ['BUY', 'SELL'] and atr > 0:
            levels = MarketStructureCloudTrendSignalGenerator.calculate_entry_exit_levels(
                entry_price, atr, timeframe
            )
            stop_loss = levels['stop_loss']
            take_profit = levels['take_profit']
        
        # Build reasoning
        reasoning = ". ".join(reasoning_parts) if reasoning_parts else "No clear signal"
        
        return {
            'signal': signal,
            'confidence': confidence,
            'reasoning': reasoning,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'atr': atr,
            'timeframe': timeframe,
            'structure_break_type': 'BOS' if (bos_bullish or bos_bearish) else ('CHACH' if (chach_bullish or chach_bearish) else None),
            'cloud_direction': cloud_direction,
            'volume_confirmed': volume_confirmed
        }
    
    @classmethod
    def analyze_stock(
        cls,
        data: pd.DataFrame,
        timeframe: str = "swing",
        min_confidence: int = 70,
        cloud_period: int = 20,
        swing_lookback: int = 5
    ) -> Dict[str, Any]:
        """
        Complete Market Structure and Cloud Trend analysis for a stock.
        
        Args:
            data: DataFrame with 'high', 'low', 'close', 'volume' columns
            timeframe: 'swing' or 'scalp'
            min_confidence: Minimum confidence to take trade
            cloud_period: Period for cloud calculation
            swing_lookback: Lookback for swing points
        
        Returns:
            Complete analysis with signals
        """
        if len(data) < 50:
            return {
                'signal': 'WAIT',
                'confidence': 0,
                'reasoning': 'Insufficient historical data',
                'error': 'Need at least 50 bars of data'
            }
        
        # Calculate ATR
        atr_series = TechnicalIndicators.calculate_atr(
            data['high'], data['low'], data['close']
        )
        atr = atr_series.iloc[-1] if len(atr_series) > 0 and not pd.isna(atr_series.iloc[-1]) else 0
        
        if atr == 0:
            return {
                'signal': 'WAIT',
                'confidence': 0,
                'reasoning': 'Unable to calculate ATR',
                'error': 'ATR calculation failed'
            }
        
        # Analyze market structure
        market_structure = MarketStructure.analyze_market_structure(
            data, data['volume'], lookback=swing_lookback
        )
        
        # Analyze cloud trend
        cloud_trend = HighLowCloudTrend.analyze_cloud_trend(
            data, period=cloud_period
        )
        
        # Generate signals
        signals = cls.generate_signals(
            data,
            market_structure,
            cloud_trend,
            atr,
            data['volume'],
            timeframe=timeframe,
            min_confidence=min_confidence
        )
        
        return {
            **signals,
            'market_structure': market_structure,
            'cloud_trend': cloud_trend,
            'analysis_complete': True
        }

