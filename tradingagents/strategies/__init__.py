"""
Multi-Strategy Investment Analysis System

This module provides multiple investment strategies that can be used independently
or compared against each other. All strategies implement a common interface,
allowing for easy comparison and consensus analysis.

Strategies:
- Value Investing (Buffett-style)
- Growth Investing
- Dividend Investing
- Momentum Trading
- Contrarian Investing
- Quantitative/Systematic
- Sector Rotation

Usage:
    from tradingagents.strategies import StrategyComparator, ValueStrategy, GrowthStrategy
    
    comparator = StrategyComparator([ValueStrategy(), GrowthStrategy()])
    result = comparator.compare("AAPL", market_data, fundamental_data, technical_data)
"""

from .base import (
    InvestmentStrategy,
    StrategyResult,
    Recommendation,
)

from .comparator import StrategyComparator
from .data_collector import StrategyDataCollector

# Import strategies (may fail if dependencies missing, but that's OK)
try:
    from .value import ValueStrategy
except ImportError as e:
    ValueStrategy = None

try:
    from .growth import GrowthStrategy
except ImportError as e:
    GrowthStrategy = None

try:
    from .dividend import DividendStrategy
except ImportError as e:
    DividendStrategy = None

try:
    from .momentum import MomentumStrategy
except ImportError as e:
    MomentumStrategy = None

try:
    from .contrarian import ContrarianStrategy
except ImportError as e:
    ContrarianStrategy = None

try:
    from .quantitative import QuantitativeStrategy
except ImportError as e:
    QuantitativeStrategy = None

try:
    from .sector_rotation import SectorRotationStrategy
except ImportError as e:
    SectorRotationStrategy = None

__all__ = [
    "InvestmentStrategy",
    "StrategyResult",
    "Recommendation",
    "StrategyComparator",
    "StrategyDataCollector",
]

# Add strategies to __all__ if they're available
if ValueStrategy:
    __all__.append("ValueStrategy")
if GrowthStrategy:
    __all__.append("GrowthStrategy")
if DividendStrategy:
    __all__.append("DividendStrategy")
if MomentumStrategy:
    __all__.append("MomentumStrategy")
if ContrarianStrategy:
    __all__.append("ContrarianStrategy")
if QuantitativeStrategy:
    __all__.append("QuantitativeStrategy")
if SectorRotationStrategy:
    __all__.append("SectorRotationStrategy")

__version__ = "1.0.0"

