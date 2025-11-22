# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Dividend tracking and analysis module.

This module provides functionality for:
- Fetching dividend history from yfinance
- Tracking upcoming dividend payments
- Calculating dividend yields and metrics
- Managing dividend income
- Generating dividend reinvestment recommendations
"""

from .dividend_fetcher import DividendFetcher
from .dividend_calendar import DividendCalendar
from .dividend_tracker import DividendTracker
from .dividend_metrics import DividendMetrics

__all__ = [
    'DividendFetcher',
    'DividendCalendar',
    'DividendTracker',
    'DividendMetrics',
]
