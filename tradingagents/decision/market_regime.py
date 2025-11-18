"""
Market Regime Detection Module

High Impact Feature 1: Dynamic gate thresholds based on market regime.
Detects bull/bear markets and volatility regimes to adjust decision thresholds.
"""

from typing import Dict, Any, Optional
from datetime import date, timedelta
import logging
import yfinance as yf
import pandas as pd

logger = logging.getLogger(__name__)


class MarketRegimeDetector:
    """
    Detect market regime (bull/bear) and volatility regime (high/low).
    
    Used to dynamically adjust gate thresholds for better profitability.
    """
    
    def __init__(self, lookback_days: int = 252):
        """
        Initialize market regime detector.
        
        Args:
            lookback_days: Number of days to look back for regime detection (default: 1 year)
        """
        self.lookback_days = lookback_days
        self._sp500_data = None
    
    def detect_market_regime(self, reference_date: date = None) -> str:
        """
        Detect current market regime: 'bull', 'bear', or 'neutral'.
        
        Uses S&P 500 performance over lookback period:
        - Bull: >10% gain over 6 months
        - Bear: <-10% decline over 6 months
        - Neutral: Between -10% and +10%
        
        Args:
            reference_date: Date to analyze from (defaults to today)
            
        Returns:
            'bull', 'bear', or 'neutral'
        """
        if reference_date is None:
            reference_date = date.today()
        
        try:
            # Fetch S&P 500 data
            sp500 = yf.Ticker("^GSPC")
            end_date = reference_date
            start_date = end_date - timedelta(days=self.lookback_days)
            
            hist = sp500.history(start=start_date, end=end_date)
            
            if hist.empty or len(hist) < 60:
                logger.warning("Insufficient S&P 500 data for regime detection")
                return 'neutral'
            
            # Calculate returns
            start_price = hist['Close'].iloc[0]
            end_price = hist['Close'].iloc[-1]
            total_return = ((end_price - start_price) / start_price) * 100
            
            # Calculate 6-month return
            six_months_ago = max(0, len(hist) - 126)  # ~6 months
            six_month_price = hist['Close'].iloc[six_months_ago]
            six_month_return = ((end_price - six_month_price) / six_month_price) * 100
            
            # Determine regime
            if six_month_return > 10:
                return 'bull'
            elif six_month_return < -10:
                return 'bear'
            else:
                return 'neutral'
                
        except Exception as e:
            logger.error(f"Error detecting market regime: {e}")
            return 'neutral'
    
    def detect_volatility_regime(self, reference_date: date = None) -> str:
        """
        Detect volatility regime: 'high', 'low', or 'normal'.
        
        Uses VIX (volatility index) or S&P 500 volatility:
        - High: VIX > 25 or 30-day volatility > 30%
        - Low: VIX < 15 or 30-day volatility < 15%
        - Normal: Between thresholds
        
        Args:
            reference_date: Date to analyze from (defaults to today)
            
        Returns:
            'high', 'low', or 'normal'
        """
        if reference_date is None:
            reference_date = date.today()
        
        try:
            # Try VIX first
            try:
                vix = yf.Ticker("^VIX")
                end_date = reference_date
                start_date = end_date - timedelta(days=30)
                
                hist = vix.history(start=start_date, end=end_date)
                
                if not hist.empty:
                    avg_vix = hist['Close'].mean()
                    
                    if avg_vix > 25:
                        return 'high'
                    elif avg_vix < 15:
                        return 'low'
                    else:
                        return 'normal'
            except:
                pass
            
            # Fallback to S&P 500 volatility
            sp500 = yf.Ticker("^GSPC")
            end_date = reference_date
            start_date = end_date - timedelta(days=60)
            
            hist = sp500.history(start=start_date, end=end_date)
            
            if hist.empty or len(hist) < 30:
                return 'normal'
            
            # Calculate 30-day volatility
            returns = hist['Close'].pct_change().dropna()
            volatility = returns.std() * (252 ** 0.5) * 100  # Annualized
            
            if volatility > 30:
                return 'high'
            elif volatility < 15:
                return 'low'
            else:
                return 'normal'
                
        except Exception as e:
            logger.error(f"Error detecting volatility regime: {e}")
            return 'normal'
    
    def get_dynamic_thresholds(
        self,
        market_regime: str = None,
        volatility_regime: str = None
    ) -> Dict[str, int]:
        """
        Get dynamic gate thresholds based on market and volatility regimes.
        
        High Impact Feature 1: Adjust thresholds for better profitability.
        
        Bull Market:
        - Lower fundamental threshold (65 vs 70) - more opportunities
        - Raise technical threshold (70 vs 65) - require stronger technicals
        
        Bear Market:
        - Raise fundamental threshold (75 vs 70) - stricter value requirement
        - Lower technical threshold (60 vs 65) - accept weaker technicals
        
        High Volatility:
        - Raise risk threshold (75 vs 70) - stricter risk management
        - Require higher risk/reward (2.5:1 vs 2:1)
        
        Low Volatility:
        - Standard thresholds
        - Allow lower risk/reward (1.5:1)
        
        Args:
            market_regime: 'bull', 'bear', or 'neutral' (auto-detected if None)
            volatility_regime: 'high', 'low', or 'normal' (auto-detected if None)
            
        Returns:
            Dictionary with adjusted thresholds
        """
        # Base thresholds
        thresholds = {
            'fundamental_min_score': 70,
            'technical_min_score': 65,
            'risk_min_score': 70,
            'timing_min_score': 60,
            'min_risk_reward': 2.0
        }
        
        # Detect regimes if not provided
        if market_regime is None:
            market_regime = self.detect_market_regime()
        
        if volatility_regime is None:
            volatility_regime = self.detect_volatility_regime()
        
        # Adjust for market regime
        if market_regime == 'bull':
            thresholds['fundamental_min_score'] = 65  # Lower (more permissive)
            thresholds['technical_min_score'] = 70     # Higher (require stronger technicals)
        elif market_regime == 'bear':
            thresholds['fundamental_min_score'] = 75  # Higher (stricter value)
            thresholds['technical_min_score'] = 60     # Lower (accept weaker technicals)
        
        # Adjust for volatility regime
        if volatility_regime == 'high':
            thresholds['risk_min_score'] = 75         # Higher (stricter risk)
            thresholds['min_risk_reward'] = 2.5       # Higher R/R requirement
        elif volatility_regime == 'low':
            thresholds['min_risk_reward'] = 1.5       # Lower R/R acceptable
        
        logger.info(
            f"Market regime: {market_regime}, Volatility: {volatility_regime} - "
            f"Thresholds: F={thresholds['fundamental_min_score']}, "
            f"T={thresholds['technical_min_score']}, R={thresholds['risk_min_score']}"
        )
        
        return thresholds

