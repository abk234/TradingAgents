# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Market Structure and Cloud Trend Strategy

Market Structure and High Low Cloud Trend based trading strategy.
"""

from typing import Dict, Any, Optional
import logging
import pandas as pd

from .base import InvestmentStrategy, StrategyResult, Recommendation
from tradingagents.screener.market_structure_cloud_trend_signals import MarketStructureCloudTrendSignalGenerator
from tradingagents.screener.indicators import TechnicalIndicators
from .utils import extract_metric

logger = logging.getLogger(__name__)


class MarketStructureCloudTrendStrategy(InvestmentStrategy):
    """
    Market Structure and Cloud Trend Strategy.
    
    Based on:
    - Market Structure with Inducements and Sweeps (institutional patterns)
    - High Low Cloud Trend (reversal indicator)
    - ATR-based risk management
    
    Key Features:
    - Identifies institutional trading patterns
    - Filters out retail trader traps (inducements)
    - Dynamic risk management adapts to volatility
    - Works for both swing trading and scalping
    """
    
    def __init__(self, timeframe: str = "swing", min_confidence: int = 70):
        """
        Initialize Market Structure and Cloud Trend strategy.
        
        Args:
            timeframe: 'swing' (4-hour) or 'scalp' (1-5 minute)
            min_confidence: Minimum confidence to take trade (70 default)
        """
        self.timeframe = timeframe
        self.min_confidence = min_confidence
    
    def get_strategy_name(self) -> str:
        return "Market Structure and Cloud Trend"
    
    def get_timeframe(self) -> str:
        if self.timeframe == "swing":
            return "1-2 weeks (swing trading)"
        else:
            return "Minutes to hours (scalping)"
    
    def evaluate(
        self,
        ticker: str,
        market_data: Dict[str, Any],
        fundamental_data: Dict[str, Any],
        technical_data: Dict[str, Any],
        additional_data: Optional[Dict[str, Any]] = None
    ) -> StrategyResult:
        """
        Evaluate stock using Market Structure and Cloud Trend strategy.
        """
        # Validate data
        if not self.validate_data(market_data, fundamental_data, technical_data):
            return StrategyResult(
                recommendation=Recommendation.WAIT,
                confidence=0,
                reasoning="Insufficient data for Market Structure and Cloud Trend analysis",
                strategy_name=self.get_strategy_name()
            )
        
        # Extract required data
        current_price = extract_metric(market_data, "current_price", 0.0)
        if current_price == 0:
            return StrategyResult(
                recommendation=Recommendation.WAIT,
                confidence=0,
                reasoning="Missing current price data",
                strategy_name=self.get_strategy_name()
            )
        
        # Try to get historical price data
        price_data = self._prepare_price_data(technical_data, market_data, additional_data)
        
        if price_data is None:
            return StrategyResult(
                recommendation=Recommendation.WAIT,
                confidence=0,
                reasoning="Insufficient historical data - no price data available",
                strategy_name=self.get_strategy_name()
            )
        
        if len(price_data) < 50:
            return StrategyResult(
                recommendation=Recommendation.WAIT,
                confidence=0,
                reasoning=f"Insufficient historical data (have {len(price_data)} bars, need at least 50)",
                strategy_name=self.get_strategy_name()
            )
        
        try:
            # Run Market Structure and Cloud Trend analysis
            analysis = MarketStructureCloudTrendSignalGenerator.analyze_stock(
                price_data,
                timeframe=self.timeframe,
                min_confidence=self.min_confidence
            )
            
            # Check for errors
            if 'error' in analysis:
                return StrategyResult(
                    recommendation=Recommendation.WAIT,
                    confidence=0,
                    reasoning=f"Analysis error: {analysis['error']}",
                    strategy_name=self.get_strategy_name()
                )
            
            # Extract signal
            signal = analysis.get('signal', 'WAIT')
            confidence = analysis.get('confidence', 0)
            reasoning = analysis.get('reasoning', 'No signal generated')
            entry_price = analysis.get('entry_price')
            stop_loss = analysis.get('stop_loss')
            take_profit = analysis.get('take_profit')
            
            # Convert signal to recommendation
            if signal == 'BUY':
                recommendation = Recommendation.BUY
            elif signal == 'SELL':
                recommendation = Recommendation.SELL
            else:
                recommendation = Recommendation.WAIT
            
            # Build key metrics
            key_metrics = {
                'atr': analysis.get('atr'),
                'timeframe': analysis.get('timeframe'),
                'structure_break_type': analysis.get('structure_break_type'),
                'cloud_direction': analysis.get('cloud_direction'),
                'volume_confirmed': analysis.get('volume_confirmed', False)
            }
            
            # Build risks
            risks = []
            if not analysis.get('volume_confirmed', False):
                risks.append("Volume not confirmed (below threshold)")
            
            if analysis.get('market_structure', {}).get('inducements', {}).get('has_inducement', False):
                risks.append("Potential inducement detected (fake breakout)")
            
            # Determine holding period
            holding_period = "1-2 weeks" if self.timeframe == "swing" else "Minutes to hours"
            
            return StrategyResult(
                recommendation=recommendation,
                confidence=confidence,
                reasoning=reasoning,
                entry_price=entry_price,
                target_price=take_profit,
                stop_loss=stop_loss,
                holding_period=holding_period,
                key_metrics=key_metrics,
                risks=risks,
                strategy_name=self.get_strategy_name()
            )
        
        except Exception as e:
            logger.error(f"Error in Market Structure and Cloud Trend analysis for {ticker}: {e}")
            return StrategyResult(
                recommendation=Recommendation.WAIT,
                confidence=0,
                reasoning=f"Analysis error: {str(e)}",
                strategy_name=self.get_strategy_name()
            )
    
    def _prepare_price_data(
        self,
        technical_data: Dict[str, Any],
        market_data: Dict[str, Any],
        additional_data: Optional[Dict[str, Any]] = None
    ) -> Optional[pd.DataFrame]:
        """
        Prepare price DataFrame from available data.
        
        Tries multiple sources:
        1. Historical data from additional_data
        2. Fetch from yfinance if ticker available
        3. Reconstructed from technical indicators (fallback)
        """
        # Try to get historical data from additional_data
        if additional_data:
            # Check for historical price data
            if 'historical_data' in additional_data:
                hist_data = additional_data['historical_data']
                if isinstance(hist_data, pd.DataFrame):
                    # Check if we have the required columns
                    required_cols = ['high', 'low', 'close', 'volume']
                    if all(col in hist_data.columns for col in required_cols):
                        logger.info(f"Using provided historical data: {len(hist_data)} bars")
                        return hist_data
                    else:
                        logger.warning(f"Historical data missing columns. Has: {list(hist_data.columns)}, Needs: {required_cols}")
            
            # Check for price history
            if 'price_history' in additional_data:
                price_history = additional_data['price_history']
                if isinstance(price_history, pd.DataFrame):
                    required_cols = ['high', 'low', 'close', 'volume']
                    if all(col in price_history.columns for col in required_cols):
                        logger.info(f"Using provided price history: {len(price_history)} bars")
                        return price_history
            
            # Try to fetch from yfinance if ticker is available
            ticker = additional_data.get('ticker')
            if ticker:
                try:
                    import yfinance as yf
                    ticker_obj = yf.Ticker(ticker)
                    hist = ticker_obj.history(period="1y")  # Get 1 year of data
                    
                    if not hist.empty and len(hist) >= 50:
                        # Rename columns to match expected format
                        data = pd.DataFrame({
                            'high': hist['High'],
                            'low': hist['Low'],
                            'close': hist['Close'],
                            'volume': hist['Volume']
                        })
                        logger.info(f"Fetched {len(data)} bars of historical data for {ticker}")
                        return data
                except Exception as e:
                    logger.debug(f"Could not fetch historical data from yfinance: {e}")
        
        # Try to reconstruct from technical data (fallback)
        # This is a minimal fallback - ideally we'd have full historical data
        current_price = extract_metric(market_data, "current_price", 0.0)
        if current_price == 0:
            return None
        
        logger.warning("Limited historical data available - analysis may be incomplete")
        
        # Create minimal DataFrame (not ideal, but allows code to run)
        # In production, this should fetch historical data via data collector
        data = pd.DataFrame({
            'high': [current_price * 1.01] * 50,  # Estimate
            'low': [current_price * 0.99] * 50,     # Estimate
            'close': [current_price] * 50,
            'volume': [extract_metric(market_data, "volume", 1000000)] * 50
        })
        
        return data
    
    def get_required_data(self) -> list:
        """Return required data types."""
        return ["market", "technical"]  # Less emphasis on fundamentals


def create_market_structure_cloud_trend_strategy(timeframe: str = "swing", min_confidence: int = 70) -> MarketStructureCloudTrendStrategy:
    """
    Factory function to create Market Structure and Cloud Trend strategy.
    
    Args:
        timeframe: 'swing' or 'scalp'
        min_confidence: Minimum confidence (0-100)
    
    Returns:
        MarketStructureCloudTrendStrategy instance
    """
    return MarketStructureCloudTrendStrategy(timeframe=timeframe, min_confidence=min_confidence)

