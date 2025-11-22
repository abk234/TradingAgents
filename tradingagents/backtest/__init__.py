# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Backtesting Module

Provides backtesting capabilities for trading strategies with anti-lookahead protection.
"""

from .backtest_engine import BacktestEngine, BacktestResult
from .historical_replay import HistoricalReplay
from .strategy_validator import StrategyValidator

__all__ = [
    'BacktestEngine',
    'BacktestResult',
    'HistoricalReplay',
    'StrategyValidator',
]

