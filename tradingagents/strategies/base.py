# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Base Strategy Interface

Defines the common interface that all investment strategies must implement.
This allows strategies to be compared and combined easily.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Recommendation(Enum):
    """Standard recommendation types."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    WAIT = "WAIT"


@dataclass
class StrategyResult:
    """
    Standardized result from any investment strategy.
    
    All strategies return this format, allowing easy comparison.
    """
    recommendation: Recommendation
    confidence: int  # 0-100
    reasoning: str
    entry_price: Optional[float] = None
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    holding_period: Optional[str] = None
    key_metrics: Dict[str, Any] = field(default_factory=dict)
    risks: List[str] = field(default_factory=list)
    strategy_name: Optional[str] = None
    
    def __post_init__(self):
        """Validate and set defaults."""
        if not isinstance(self.confidence, int) or not (0 <= self.confidence <= 100):
            raise ValueError(f"Confidence must be integer between 0-100, got {self.confidence}")
        
        if self.key_metrics is None:
            self.key_metrics = {}
        if self.risks is None:
            self.risks = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "recommendation": self.recommendation.value,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "entry_price": self.entry_price,
            "target_price": self.target_price,
            "stop_loss": self.stop_loss,
            "holding_period": self.holding_period,
            "key_metrics": self.key_metrics,
            "risks": self.risks,
            "strategy_name": self.strategy_name,
        }


class InvestmentStrategy(ABC):
    """
    Base class for all investment strategies.
    
    All strategies must implement this interface to ensure:
    - Consistent evaluation interface
    - Standardized results
    - Easy comparison and combination
    """
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """
        Return human-readable strategy name.
        
        Returns:
            Strategy name (e.g., "Value Investing", "Growth Investing")
        """
        pass
    
    @abstractmethod
    def get_timeframe(self) -> str:
        """
        Return typical holding period for this strategy.
        
        Returns:
            Timeframe description (e.g., "5-10 years", "30-90 days")
        """
        pass
    
    @abstractmethod
    def evaluate(
        self,
        ticker: str,
        market_data: Dict[str, Any],
        fundamental_data: Dict[str, Any],
        technical_data: Dict[str, Any],
        additional_data: Optional[Dict[str, Any]] = None
    ) -> StrategyResult:
        """
        Evaluate stock using this strategy.
        
        Args:
            ticker: Stock symbol (e.g., "AAPL")
            market_data: Current price, volume, market cap, etc.
                Expected keys: current_price, volume, market_cap, etc.
            fundamental_data: P/E ratio, revenue, earnings, etc.
                Expected keys: pe_ratio, revenue, earnings, debt_to_equity, etc.
            technical_data: RSI, MACD, moving averages, etc.
                Expected keys: rsi, macd, ma_20, ma_50, etc.
            additional_data: Strategy-specific data (optional)
                Can include: sector data, news, sentiment, etc.
        
        Returns:
            StrategyResult with recommendation, confidence, reasoning, etc.
        """
        pass
    
    def get_required_data(self) -> List[str]:
        """
        Return list of required data types.
        
        Used by data collector to know what to fetch.
        Default implementation returns all standard types.
        
        Returns:
            List of data type names: ["market", "fundamental", "technical"]
        """
        return ["market", "fundamental", "technical"]
    
    def validate_data(
        self,
        market_data: Dict[str, Any],
        fundamental_data: Dict[str, Any],
        technical_data: Dict[str, Any]
    ) -> bool:
        """
        Validate that required data is present.
        
        Override in subclasses to add strategy-specific validation.
        
        Args:
            market_data: Market data dictionary
            fundamental_data: Fundamental data dictionary
            technical_data: Technical data dictionary
        
        Returns:
            True if data is valid, False otherwise
        """
        # Basic validation - check that dictionaries are not empty
        if not market_data or not isinstance(market_data, dict):
            logger.warning(f"{self.get_strategy_name()}: Missing or invalid market_data")
            return False
        
        if not fundamental_data or not isinstance(fundamental_data, dict):
            logger.warning(f"{self.get_strategy_name()}: Missing or invalid fundamental_data")
            return False
        
        if not technical_data or not isinstance(technical_data, dict):
            logger.warning(f"{self.get_strategy_name()}: Missing or invalid technical_data")
            return False
        
        return True

