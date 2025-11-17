"""
TradingAgents Validation Module

Provides data quality validation, multi-source verification, and credibility scoring
to ensure Eddie's recommendations are trustworthy.
"""

from .data_quality import (
    check_price_staleness,
    validate_data_quality,
    DataQualityReport,
)

from .price_validation import (
    validate_price_multi_source,
    PriceValidationReport,
    check_volume_anomaly,
    get_yfinance_current_price,
    get_alphavantage_current_price,
)

from .earnings_calendar import (
    check_earnings_proximity,
    EarningsProximityReport,
    EarningsEvent,
    get_earnings_calendar_yfinance,
    get_earnings_calendar_alphavantage,
)

__all__ = [
    # Phase 1: Data Quality
    'check_price_staleness',
    'validate_data_quality',
    'DataQualityReport',

    # Phase 2: Multi-Source Price Validation
    'validate_price_multi_source',
    'PriceValidationReport',
    'check_volume_anomaly',
    'get_yfinance_current_price',
    'get_alphavantage_current_price',

    # Phase 2: Earnings Calendar
    'check_earnings_proximity',
    'EarningsProximityReport',
    'EarningsEvent',
    'get_earnings_calendar_yfinance',
    'get_earnings_calendar_alphavantage',
]
