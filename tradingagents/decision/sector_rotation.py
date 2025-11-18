"""
Sector Rotation Detection Module

High Impact Feature 4: Detect sector rotation patterns to identify emerging
strong sectors and weakening sectors for better allocation decisions.
"""

from typing import Dict, Any, List, Optional
from datetime import date, timedelta
from decimal import Decimal
import logging
import yfinance as yf
import pandas as pd

logger = logging.getLogger(__name__)


class SectorRotationDetector:
    """
    Detect sector rotation patterns and recommend sector allocation changes.
    
    Identifies:
    - Emerging strong sectors (accelerating momentum)
    - Weakening sectors (decelerating momentum)
    - Sector leadership changes
    """
    
    # Sector ETFs for tracking
    SECTOR_ETFS = {
        'Technology': 'XLK',
        'Healthcare': 'XLV',
        'Financial': 'XLF',
        'Consumer Discretionary': 'XLY',
        'Consumer Staples': 'XLP',
        'Energy': 'XLE',
        'Industrials': 'XLI',
        'Materials': 'XLB',
        'Real Estate': 'XLRE',
        'Utilities': 'XLU',
        'Communication': 'XLC'
    }
    
    def __init__(self, lookback_days: int = 180):
        """
        Initialize sector rotation detector.
        
        Args:
            lookback_days: Number of days to look back for analysis (default: 6 months)
        """
        self.lookback_days = lookback_days
        self._sector_data_cache = {}
    
    def get_sector_performance(
        self,
        sector: str,
        reference_date: date = None
    ) -> Dict[str, Any]:
        """
        Get performance metrics for a sector.
        
        Args:
            sector: Sector name
            reference_date: Date to analyze from (defaults to today)
            
        Returns:
            Dict with performance metrics:
            - 3m_return: 3-month return %
            - 6m_return: 6-month return %
            - momentum_score: 0-1 momentum score
            - trend: 'uptrend', 'downtrend', 'sideways'
        """
        if reference_date is None:
            reference_date = date.today()
        
        etf_symbol = self.SECTOR_ETFS.get(sector)
        if not etf_symbol:
            logger.warning(f"No ETF found for sector: {sector}")
            return {
                '3m_return': 0.0,
                '6m_return': 0.0,
                'momentum_score': 0.5,
                'trend': 'sideways'
            }
        
        try:
            # Fetch sector ETF data
            etf = yf.Ticker(etf_symbol)
            end_date = reference_date
            start_date = end_date - timedelta(days=self.lookback_days)
            
            hist = etf.history(start=start_date, end=end_date)
            
            if hist.empty or len(hist) < 60:
                logger.warning(f"Insufficient data for {sector} ({etf_symbol})")
                return {
                    '3m_return': 0.0,
                    '6m_return': 0.0,
                    'momentum_score': 0.5,
                    'trend': 'sideways'
                }
            
            # Calculate returns
            current_price = hist['Close'].iloc[-1]
            
            # 3-month return (~63 trading days)
            three_months_ago = max(0, len(hist) - 63)
            three_month_price = hist['Close'].iloc[three_months_ago]
            three_month_return = ((current_price - three_month_price) / three_month_price) * 100
            
            # 6-month return (~126 trading days)
            six_months_ago = max(0, len(hist) - 126)
            six_month_price = hist['Close'].iloc[six_months_ago]
            six_month_return = ((current_price - six_month_price) / six_month_price) * 100
            
            # Calculate momentum score (0-1)
            # Higher score = stronger momentum
            momentum_score = self._calculate_momentum_score(
                hist, three_month_return, six_month_return
            )
            
            # Determine trend
            trend = self._determine_trend(hist, three_month_return, six_month_return)
            
            return {
                '3m_return': three_month_return,
                '6m_return': six_month_return,
                'momentum_score': momentum_score,
                'trend': trend,
                'current_price': current_price
            }
            
        except Exception as e:
            logger.error(f"Error getting sector performance for {sector}: {e}")
            return {
                '3m_return': 0.0,
                '6m_return': 0.0,
                'momentum_score': 0.5,
                'trend': 'sideways'
            }
    
    def _calculate_momentum_score(
        self,
        hist: pd.DataFrame,
        three_month_return: float,
        six_month_return: float
    ) -> float:
        """
        Calculate momentum score (0-1) based on returns and price action.
        
        Higher score = stronger positive momentum
        """
        # Base score from returns
        if three_month_return > 0 and six_month_return > 0:
            # Both positive - strong momentum
            base_score = min(0.8, 0.5 + (three_month_return / 20))
        elif three_month_return > 0:
            # Recent positive, but longer-term negative
            base_score = 0.4 + (three_month_return / 30)
        else:
            # Negative momentum
            base_score = max(0.2, 0.5 + (three_month_return / 20))
        
        # Adjust for acceleration/deceleration
        if three_month_return > six_month_return * 1.2:
            # Accelerating (3m > 1.2x 6m)
            base_score += 0.15
        elif three_month_return < six_month_return * 0.8:
            # Decelerating (3m < 0.8x 6m)
            base_score -= 0.15
        
        # Check recent price action (last 20 days)
        if len(hist) >= 20:
            recent_20 = hist['Close'].iloc[-20:]
            recent_trend = (recent_20.iloc[-1] - recent_20.iloc[0]) / recent_20.iloc[0]
            
            if recent_trend > 0.05:  # 5% gain in last 20 days
                base_score += 0.1
            elif recent_trend < -0.05:  # 5% loss in last 20 days
                base_score -= 0.1
        
        return max(0.0, min(1.0, base_score))
    
    def _determine_trend(
        self,
        hist: pd.DataFrame,
        three_month_return: float,
        six_month_return: float
    ) -> str:
        """Determine overall trend direction."""
        if three_month_return > 5 and six_month_return > 5:
            return 'uptrend'
        elif three_month_return < -5 and six_month_return < -5:
            return 'downtrend'
        else:
            return 'sideways'
    
    def detect_sector_rotation(
        self,
        sectors: List[str] = None,
        reference_date: date = None
    ) -> Dict[str, str]:
        """
        Detect sector rotation and recommend allocation actions.
        
        High Impact Feature 4: Identify sectors to overweight/underweight.
        
        Args:
            sectors: List of sectors to analyze (defaults to all tracked sectors)
            reference_date: Date to analyze from (defaults to today)
            
        Returns:
            Dict mapping sector to action: 'OVERWEIGHT', 'UNDERWEIGHT', 'NEUTRAL'
        """
        if sectors is None:
            sectors = list(self.SECTOR_ETFS.keys())
        
        if reference_date is None:
            reference_date = date.today()
        
        sector_performances = {}
        actions = {}
        
        # Get performance for all sectors
        for sector in sectors:
            perf = self.get_sector_performance(sector, reference_date)
            sector_performances[sector] = perf
        
        # Calculate average momentum for comparison
        avg_momentum = sum(p['momentum_score'] for p in sector_performances.values()) / len(sector_performances)
        
        # Determine actions
        for sector, perf in sector_performances.items():
            momentum = perf['momentum_score']
            short_term = perf['3m_return']
            long_term = perf['6m_return']
            
            # Strong momentum + accelerating = overweight
            if momentum > 0.7 and short_term > long_term * 1.2:
                actions[sector] = 'OVERWEIGHT'
            # Weak momentum + decelerating = underweight
            elif momentum < 0.3 and short_term < long_term * 0.8:
                actions[sector] = 'UNDERWEIGHT'
            # Above average momentum = slight overweight
            elif momentum > avg_momentum * 1.2:
                actions[sector] = 'OVERWEIGHT'
            # Below average momentum = slight underweight
            elif momentum < avg_momentum * 0.8:
                actions[sector] = 'UNDERWEIGHT'
            else:
                actions[sector] = 'NEUTRAL'
        
        logger.info(f"Sector rotation detected: {sum(1 for a in actions.values() if a == 'OVERWEIGHT')} overweight, "
                   f"{sum(1 for a in actions.values() if a == 'UNDERWEIGHT')} underweight")
        
        return actions
    
    def get_top_sectors(
        self,
        limit: int = 3,
        reference_date: date = None
    ) -> List[Dict[str, Any]]:
        """
        Get top performing sectors by momentum.
        
        Args:
            limit: Number of top sectors to return
            reference_date: Date to analyze from
            
        Returns:
            List of sector performance dicts, sorted by momentum
        """
        if reference_date is None:
            reference_date = date.today()
        
        sector_data = []
        
        for sector in self.SECTOR_ETFS.keys():
            perf = self.get_sector_performance(sector, reference_date)
            sector_data.append({
                'sector': sector,
                **perf
            })
        
        # Sort by momentum score
        sector_data.sort(key=lambda x: x['momentum_score'], reverse=True)
        
        return sector_data[:limit]
    
    def should_overweight_sector(
        self,
        sector: str,
        reference_date: date = None
    ) -> bool:
        """
        Quick check if a sector should be overweighted.
        
        Args:
            sector: Sector name
            reference_date: Date to analyze from
            
        Returns:
            True if sector should be overweighted
        """
        actions = self.detect_sector_rotation([sector], reference_date)
        return actions.get(sector) == 'OVERWEIGHT'

