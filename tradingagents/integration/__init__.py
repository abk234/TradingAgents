# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

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

