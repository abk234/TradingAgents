"""
Integration Layer

Bridges the new strategy system with the existing TradingAgents system.
Allows running both systems and comparing results.
"""

from .strategy_adapter import HybridStrategyAdapter
from .comparison_runner import ComparisonRunner

__all__ = [
    "HybridStrategyAdapter",
    "ComparisonRunner",
]

__version__ = "1.0.0"

