# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Correlation-Based Risk Management Module

High Impact Feature 5: Manage portfolio risk through correlation analysis.
Limits exposure to highly correlated positions and ensures diversification.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import date, timedelta
from decimal import Decimal
import logging
import yfinance as yf
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class CorrelationManager:
    """
    Manage portfolio risk through correlation analysis.
    
    Features:
    - Calculate correlation between positions
    - Limit exposure to highly correlated stocks
    - Ensure diversification across uncorrelated sectors
    - Add correlation penalty to risk gate
    """
    
    def __init__(self, lookback_days: int = 252):
        """
        Initialize correlation manager.
        
        Args:
            lookback_days: Number of days to use for correlation calculation (default: 1 year)
        """
        self.lookback_days = lookback_days
        self._correlation_cache = {}
        self.max_correlation = 0.75  # Maximum allowed correlation between positions
    
    def calculate_correlation(
        self,
        ticker1: str,
        ticker2: str,
        reference_date: date = None
    ) -> float:
        """
        Calculate correlation coefficient between two tickers.
        
        Args:
            ticker1: First ticker symbol
            ticker2: Second ticker symbol
            reference_date: Date to calculate from (defaults to today)
            
        Returns:
            Correlation coefficient (-1 to 1)
        """
        if reference_date is None:
            reference_date = date.today()
        
        # Check cache
        cache_key = tuple(sorted([ticker1, ticker2]))
        if cache_key in self._correlation_cache:
            cached_date, cached_corr = self._correlation_cache[cache_key]
            if (reference_date - cached_date).days < 7:  # Cache valid for 7 days
                return cached_corr
        
        try:
            # Fetch price data for both tickers
            end_date = reference_date
            start_date = end_date - timedelta(days=self.lookback_days)
            
            ticker1_data = yf.Ticker(ticker1)
            ticker2_data = yf.Ticker(ticker2)
            
            hist1 = ticker1_data.history(start=start_date, end=end_date)
            hist2 = ticker2_data.history(start=start_date, end=end_date)
            
            if hist1.empty or hist2.empty:
                logger.warning(f"Insufficient data for correlation: {ticker1} vs {ticker2}")
                return 0.0  # Assume no correlation if no data
            
            # Align dates
            common_dates = hist1.index.intersection(hist2.index)
            if len(common_dates) < 60:  # Need at least 60 days
                logger.warning(f"Insufficient overlapping data: {ticker1} vs {ticker2}")
                return 0.0
            
            hist1_aligned = hist1.loc[common_dates]['Close']
            hist2_aligned = hist2.loc[common_dates]['Close']
            
            # Calculate daily returns
            returns1 = hist1_aligned.pct_change().dropna()
            returns2 = hist2_aligned.pct_change().dropna()
            
            # Align returns
            common_returns = returns1.index.intersection(returns2.index)
            returns1_aligned = returns1.loc[common_returns]
            returns2_aligned = returns2.loc[common_returns]
            
            if len(returns1_aligned) < 30:
                return 0.0
            
            # Calculate correlation
            correlation = returns1_aligned.corr(returns2_aligned)
            
            # Cache result
            self._correlation_cache[cache_key] = (reference_date, correlation)
            
            return correlation if not np.isnan(correlation) else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating correlation {ticker1} vs {ticker2}: {e}")
            return 0.0
    
    def check_correlation_risk(
        self,
        new_ticker: str,
        existing_holdings: List[str],
        reference_date: date = None
    ) -> Tuple[bool, float, Dict[str, float]]:
        """
        Check if adding new ticker increases correlation risk.
        
        High Impact Feature 5: Reject positions that are too correlated with existing holdings.
        
        Args:
            new_ticker: Ticker symbol to check
            existing_holdings: List of existing ticker symbols in portfolio
            reference_date: Date to calculate from
            
        Returns:
            Tuple of:
            - is_safe: True if correlation risk is acceptable
            - max_correlation: Maximum correlation with any existing holding
            - correlations: Dict mapping existing ticker to correlation
        """
        if reference_date is None:
            reference_date = date.today()
        
        if not existing_holdings:
            return True, 0.0, {}
        
        correlations = {}
        max_corr = 0.0
        
        for holding in existing_holdings:
            if holding == new_ticker:
                continue  # Skip self
            
            corr = self.calculate_correlation(new_ticker, holding, reference_date)
            correlations[holding] = corr
            max_corr = max(max_corr, abs(corr))
        
        # Reject if correlation > threshold
        is_safe = max_corr < self.max_correlation
        
        if not is_safe:
            logger.warning(
                f"High correlation risk for {new_ticker}: "
                f"max correlation {max_corr:.2f} with existing holdings"
            )
        
        return is_safe, max_corr, correlations
    
    def calculate_portfolio_correlation_matrix(
        self,
        tickers: List[str],
        reference_date: date = None
    ) -> pd.DataFrame:
        """
        Calculate correlation matrix for a portfolio.
        
        Args:
            tickers: List of ticker symbols
            reference_date: Date to calculate from
            
        Returns:
            DataFrame with correlation matrix
        """
        if reference_date is None:
            reference_date = date.today()
        
        if len(tickers) < 2:
            return pd.DataFrame()
        
        # Fetch all price data
        end_date = reference_date
        start_date = end_date - timedelta(days=self.lookback_days)
        
        returns_data = {}
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(start=start_date, end=end_date)
                
                if not hist.empty:
                    returns = hist['Close'].pct_change().dropna()
                    returns_data[ticker] = returns
            except Exception as e:
                logger.warning(f"Error fetching data for {ticker}: {e}")
        
        if len(returns_data) < 2:
            return pd.DataFrame()
        
        # Align all returns to common dates
        common_dates = None
        for returns in returns_data.values():
            if common_dates is None:
                common_dates = returns.index
            else:
                common_dates = common_dates.intersection(returns.index)
        
        if len(common_dates) < 30:
            return pd.DataFrame()
        
        # Create aligned returns DataFrame
        aligned_returns = pd.DataFrame()
        for ticker, returns in returns_data.items():
            aligned_returns[ticker] = returns.loc[common_dates]
        
        # Calculate correlation matrix
        correlation_matrix = aligned_returns.corr()
        
        return correlation_matrix
    
    def get_diversification_score(
        self,
        tickers: List[str],
        reference_date: date = None
    ) -> Dict[str, Any]:
        """
        Calculate portfolio diversification score.
        
        Args:
            tickers: List of ticker symbols in portfolio
            reference_date: Date to calculate from
            
        Returns:
            Dict with diversification metrics:
            - score: Diversification score (0-1, higher is better)
            - avg_correlation: Average pairwise correlation
            - max_correlation: Maximum pairwise correlation
            - highly_correlated_pairs: List of pairs with correlation > 0.7
        """
        if reference_date is None:
            reference_date = date.today()
        
        if len(tickers) < 2:
            return {
                'score': 0.5,
                'avg_correlation': 0.0,
                'max_correlation': 0.0,
                'highly_correlated_pairs': []
            }
        
        # Calculate correlation matrix
        corr_matrix = self.calculate_portfolio_correlation_matrix(tickers, reference_date)
        
        if corr_matrix.empty:
            return {
                'score': 0.5,
                'avg_correlation': 0.0,
                'max_correlation': 0.0,
                'highly_correlated_pairs': []
            }
        
        # Get upper triangle (avoid duplicates and diagonal)
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
        correlations = corr_matrix.where(mask).stack().abs()
        
        avg_correlation = correlations.mean()
        max_correlation = correlations.max()
        
        # Find highly correlated pairs
        highly_correlated_pairs = []
        for i in range(len(corr_matrix.index)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr = abs(corr_matrix.iloc[i, j])
                if corr > 0.7:
                    highly_correlated_pairs.append({
                        'ticker1': corr_matrix.index[i],
                        'ticker2': corr_matrix.columns[j],
                        'correlation': corr
                    })
        
        # Calculate diversification score
        # Lower average correlation = higher score
        # Score ranges from 0 (perfectly correlated) to 1 (uncorrelated)
        score = max(0.0, min(1.0, 1.0 - avg_correlation))
        
        return {
            'score': score,
            'avg_correlation': avg_correlation,
            'max_correlation': max_correlation,
            'highly_correlated_pairs': highly_correlated_pairs
        }
    
    def recommend_position_adjustment(
        self,
        new_ticker: str,
        existing_holdings: List[Dict[str, Any]],
        proposed_position_pct: float
    ) -> Dict[str, Any]:
        """
        Recommend position size adjustment based on correlation.
        
        Args:
            new_ticker: Ticker to add
            existing_holdings: List of dicts with 'ticker' and 'position_pct'
            proposed_position_pct: Proposed position size %
            
        Returns:
            Dict with recommendation:
            - adjusted_position_pct: Adjusted position size
            - reduction_reason: Reason for reduction
            - max_correlation: Maximum correlation found
        """
        existing_tickers = [h['ticker'] for h in existing_holdings]
        
        is_safe, max_corr, correlations = self.check_correlation_risk(
            new_ticker, existing_tickers
        )
        
        adjusted_position_pct = proposed_position_pct
        reduction_reason = ""
        
        if not is_safe:
            # Reduce position size based on correlation
            # High correlation (>0.75) = reduce by 50%
            # Medium correlation (0.6-0.75) = reduce by 25%
            if max_corr > 0.75:
                adjusted_position_pct = proposed_position_pct * 0.5
                reduction_reason = f"High correlation ({max_corr:.2f}) - position reduced by 50%"
            elif max_corr > 0.6:
                adjusted_position_pct = proposed_position_pct * 0.75
                reduction_reason = f"Moderate correlation ({max_corr:.2f}) - position reduced by 25%"
        
        return {
            'adjusted_position_pct': adjusted_position_pct,
            'reduction_reason': reduction_reason,
            'max_correlation': max_corr,
            'is_safe': is_safe,
            'correlations': correlations
        }

