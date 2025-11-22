# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Profitability Enhancement Integration Module

Integrates all profitability improvements into the main trading graph.
This module enhances the TradingAgentsGraph with:
- Market regime detection
- Sector rotation analysis
- Correlation risk management
- Enhanced position sizing
- Exit strategy optimization
"""

from typing import Dict, Any, Optional, List
from datetime import date
from decimal import Decimal
import logging

from tradingagents.decision.market_regime import MarketRegimeDetector
from tradingagents.decision.sector_rotation import SectorRotationDetector
from tradingagents.portfolio.correlation_manager import CorrelationManager
from tradingagents.portfolio.position_sizer import PositionSizer
from tradingagents.database import get_db_connection, TickerOperations, PortfolioOperations

logger = logging.getLogger(__name__)


class ProfitabilityEnhancer:
    """
    Enhances trading decisions with profitability improvements.
    
    Integrates:
    - Market regime detection
    - Sector rotation
    - Correlation analysis
    - Enhanced position sizing
    - Exit strategy recommendations
    """
    
    def __init__(
        self,
        portfolio_value: Decimal = None,
        enable_regime_detection: bool = True,
        enable_sector_rotation: bool = True,
        enable_correlation_check: bool = True,
        db = None
    ):
        """
        Initialize profitability enhancer.
        
        Args:
            portfolio_value: Portfolio value for position sizing (optional)
            enable_regime_detection: Enable market regime detection
            enable_sector_rotation: Enable sector rotation detection
            enable_correlation_check: Enable correlation risk checks
            db: Database connection (optional)
        """
        self.db = db or get_db_connection()
        self.ticker_ops = TickerOperations(self.db)
        self.portfolio_ops = PortfolioOperations(self.db) if hasattr(PortfolioOperations, '__init__') else None
        
        self.enable_regime_detection = enable_regime_detection
        self.enable_sector_rotation = enable_sector_rotation
        self.enable_correlation_check = enable_correlation_check
        
        # Initialize detectors
        if enable_regime_detection:
            self.regime_detector = MarketRegimeDetector()
        else:
            self.regime_detector = None
        
        if enable_sector_rotation:
            self.sector_detector = SectorRotationDetector()
        else:
            self.sector_detector = None
        
        if enable_correlation_check:
            self.correlation_mgr = CorrelationManager()
        else:
            self.correlation_mgr = None
        
        # Position sizer (if portfolio value provided)
        self.position_sizer = None
        if portfolio_value:
            self.position_sizer = PositionSizer(portfolio_value=portfolio_value)
        
        logger.info("Profitability enhancer initialized")
    
    def enhance_analysis(
        self,
        ticker: str,
        final_state: Dict[str, Any],
        analysis_date: date = None
    ) -> Dict[str, Any]:
        """
        Enhance analysis with profitability improvements.
        
        Args:
            ticker: Ticker symbol
            final_state: Final state from trading graph
            analysis_date: Date of analysis
            
        Returns:
            Enhanced analysis dict with profitability insights
        """
        if analysis_date is None:
            analysis_date = date.today()
        
        enhancements = {
            'market_regime': None,
            'volatility_regime': None,
            'sector_action': None,
            'correlation_risk': None,
            'position_sizing': None,
            'exit_strategy': None
        }
        
        # 1. Market regime detection
        if self.enable_regime_detection and self.regime_detector:
            try:
                market_regime = self.regime_detector.detect_market_regime(analysis_date)
                volatility_regime = self.regime_detector.detect_volatility_regime(analysis_date)
                
                enhancements['market_regime'] = market_regime
                enhancements['volatility_regime'] = volatility_regime
                
                logger.info(f"Market regime: {market_regime}, Volatility: {volatility_regime}")
            except Exception as e:
                logger.warning(f"Error detecting market regime: {e}")
        
        # 2. Sector rotation detection
        if self.enable_sector_rotation and self.sector_detector:
            try:
                # Get ticker sector
                ticker_info = self.ticker_ops.get_ticker(symbol=ticker)
                sector = ticker_info.get('sector') if ticker_info else None
                
                if sector:
                    sector_actions = self.sector_detector.detect_sector_rotation(
                        [sector], analysis_date
                    )
                    enhancements['sector_action'] = sector_actions.get(sector, 'NEUTRAL')
                    
                    logger.info(f"Sector {sector} action: {enhancements['sector_action']}")
            except Exception as e:
                logger.warning(f"Error detecting sector rotation: {e}")
        
        # 3. Correlation risk check
        if self.enable_correlation_check and self.correlation_mgr:
            try:
                # Get existing holdings
                existing_holdings = self._get_existing_holdings()
                
                if existing_holdings:
                    is_safe, max_corr, correlations = self.correlation_mgr.check_correlation_risk(
                        ticker, existing_holdings, analysis_date
                    )
                    
                    enhancements['correlation_risk'] = {
                        'is_safe': is_safe,
                        'max_correlation': max_corr,
                        'correlations': correlations
                    }
                    
                    if not is_safe:
                        logger.warning(f"High correlation risk for {ticker}: {max_corr:.2f}")
            except Exception as e:
                logger.warning(f"Error checking correlation risk: {e}")
        
        # 4. Position sizing (if position sizer available)
        if self.position_sizer:
            try:
                # Extract confidence from final state
                confidence = self._extract_confidence(final_state)
                
                # Extract gate scores if available
                gate_scores = self._extract_gate_scores(final_state)
                timing_passed = self._extract_timing_passed(final_state)
                
                # Extract price data
                price_data = self._extract_price_data(final_state)
                
                if price_data and 'current_price' in price_data:
                    sizing = self.position_sizer.calculate_position_size(
                        confidence=confidence,
                        current_price=Decimal(str(price_data['current_price'])),
                        gate_scores=gate_scores,
                        timing_passed=timing_passed
                    )
                    
                    enhancements['position_sizing'] = {
                        'position_size_pct': float(sizing['position_size_pct']),
                        'recommended_amount': float(sizing['recommended_amount']),
                        'recommended_shares': sizing['recommended_shares'],
                        'sizing_reasoning': sizing['sizing_reasoning']
                    }
            except Exception as e:
                logger.warning(f"Error calculating position size: {e}")
        
        # 5. Exit strategy recommendations
        try:
            price_data = self._extract_price_data(final_state)
            if price_data and 'current_price' in price_data and self.position_sizer:
                # Calculate trailing stop
                entry_price = Decimal(str(price_data.get('current_price', 0)))
                stop_info = self.position_sizer.calculate_trailing_stop(
                    entry_price=entry_price,
                    current_price=entry_price,
                    highest_price=entry_price
                )
                
                # Partial profit recommendations
                profit_info = self.position_sizer.should_take_partial_profit(
                    entry_price=entry_price,
                    current_price=entry_price
                )
                
                enhancements['exit_strategy'] = {
                    'trailing_stop': float(stop_info['trailing_stop']),
                    'initial_stop_loss_pct': float(stop_info['stop_loss_pct']),
                    'partial_profit_levels': {
                        '5pct': {'sell_pct': 0.25, 'reasoning': 'Moderate gain'},
                        '10pct': {'sell_pct': 0.25, 'reasoning': 'Good gain'},
                        '15pct': {'sell_pct': 0.5, 'reasoning': 'Strong gain'}
                    }
                }
        except Exception as e:
            logger.warning(f"Error calculating exit strategy: {e}")
        
        return enhancements
    
    def get_dynamic_thresholds(
        self,
        confidence_score: int = None,
        analysis_date: date = None
    ) -> Dict[str, int]:
        """
        Get dynamic thresholds based on market regime and confidence.
        
        Args:
            confidence_score: Confidence score (0-100)
            analysis_date: Date for regime detection
            
        Returns:
            Dynamic thresholds dictionary
        """
        if not self.regime_detector:
            return {}
        
        if analysis_date is None:
            analysis_date = date.today()
        
        market_regime = self.regime_detector.detect_market_regime(analysis_date)
        volatility_regime = self.regime_detector.detect_volatility_regime(analysis_date)
        
        return self.regime_detector.get_dynamic_thresholds(
            market_regime=market_regime,
            volatility_regime=volatility_regime
        )
    
    def _get_existing_holdings(self) -> List[str]:
        """Get list of existing ticker symbols in portfolio."""
        try:
            if not self.portfolio_ops:
                return []
            
            # Try to get holdings from database
            # This is a placeholder - adjust based on actual PortfolioOperations API
            holdings = self.portfolio_ops.get_open_holdings() if hasattr(self.portfolio_ops, 'get_open_holdings') else []
            
            # Extract ticker symbols
            tickers = []
            for holding in holdings:
                if isinstance(holding, dict):
                    ticker = holding.get('symbol') or holding.get('ticker')
                    if ticker:
                        tickers.append(ticker)
                elif isinstance(holding, str):
                    tickers.append(holding)
            
            return tickers
        except Exception as e:
            logger.debug(f"Could not get existing holdings: {e}")
            return []
    
    def _extract_confidence(self, final_state: Dict[str, Any]) -> int:
        """Extract confidence score from final state."""
        # Try multiple possible locations
        confidence = final_state.get('confidence_score') or \
                    final_state.get('confidence') or \
                    final_state.get('final_confidence') or \
                    75  # Default
        
        return int(confidence) if confidence else 75
    
    def _extract_gate_scores(self, final_state: Dict[str, Any]) -> Optional[Dict[str, int]]:
        """Extract gate scores from final state if available."""
        # This would need to be populated if gates are evaluated
        # For now, return None
        return None
    
    def _extract_timing_passed(self, final_state: Dict[str, Any]) -> bool:
        """Extract timing gate status from final state."""
        # Check if timing gate passed
        # This would need to be populated if gates are evaluated
        return True  # Default
    
    def _extract_price_data(self, final_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract price data from final state."""
        # Try to extract price information
        # This is a placeholder - adjust based on actual state structure
        return {
            'current_price': 0  # Would need actual extraction logic
        }

