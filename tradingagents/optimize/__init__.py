# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Portfolio optimization module.

This module provides functionality for:
- Sector rebalancing and allocation management
- Tax-loss harvesting with wash sale detection
- Risk metrics calculation (Sharpe, Sortino, Beta, Alpha)
- Portfolio optimization (Modern Portfolio Theory)
- Risk-adjusted performance analysis
"""

from .sector_rebalancer import SectorRebalancer
from .tax_harvester import TaxLossHarvester
from .risk_metrics import RiskMetricsCalculator
from .portfolio_optimizer import PortfolioOptimizer

__all__ = [
    'SectorRebalancer',
    'TaxLossHarvester',
    'RiskMetricsCalculator',
    'PortfolioOptimizer',
]
