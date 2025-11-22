# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Strategy Utilities

Shared utility functions for strategy implementations.
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert value to float.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
    
    Returns:
        Float value or default
    """
    if value is None:
        return default
    
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert value to int.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
    
    Returns:
        Integer value or default
    """
    if value is None:
        return default
    
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def extract_metric(
    data: Dict[str, Any],
    key: str,
    default: Any = None,
    data_type: type = float
) -> Any:
    """
    Extract metric from data dictionary, handling various key formats.
    
    Args:
        data: Data dictionary
        key: Key to look for (tries multiple variations)
        default: Default value if not found
        data_type: Type to convert to (float, int, str)
    
    Returns:
        Extracted value or default
    """
    # Handle None or non-dict data
    if data is None or not isinstance(data, dict):
        return default
    
    # Try exact key
    if key in data:
        value = data[key]
        if value is not None:
            try:
                return data_type(value)
            except (ValueError, TypeError):
                pass
    
    # Try lowercase key
    key_lower = key.lower()
    if key_lower in data:
        value = data[key_lower]
        if value is not None:
            try:
                return data_type(value)
            except (ValueError, TypeError):
                pass
    
    # Try title case key
    key_title = key.title()
    if key_title in data:
        value = data[key_title]
        if value is not None:
            try:
                return data_type(value)
            except (ValueError, TypeError):
                pass
    
    return default


def calculate_margin_of_safety(
    intrinsic_value: float,
    current_price: float
) -> float:
    """
    Calculate margin of safety percentage.
    
    Args:
        intrinsic_value: Estimated intrinsic value per share
        current_price: Current market price per share
    
    Returns:
        Margin of safety as percentage (positive = discount, negative = premium)
    """
    if intrinsic_value <= 0 or current_price <= 0:
        return 0.0
    
    return ((intrinsic_value - current_price) / intrinsic_value) * 100


def calculate_peg_ratio(
    pe_ratio: float,
    earnings_growth: float
) -> Optional[float]:
    """
    Calculate PEG ratio (P/E divided by earnings growth).
    
    Args:
        pe_ratio: Price-to-earnings ratio
        earnings_growth: Earnings growth rate (as decimal, e.g., 0.20 for 20%)
    
    Returns:
        PEG ratio or None if invalid
    """
    if pe_ratio <= 0 or earnings_growth <= 0:
        return None
    
    return pe_ratio / (earnings_growth * 100)  # Convert growth to percentage


def normalize_confidence(
    score: float,
    min_score: float = 0,
    max_score: float = 100
) -> int:
    """
    Normalize score to 0-100 confidence range.
    
    Args:
        score: Raw score
        min_score: Minimum possible score
        max_score: Maximum possible score
    
    Returns:
        Normalized confidence (0-100)
    """
    if max_score == min_score:
        return 50  # Neutral if no range
    
    normalized = ((score - min_score) / (max_score - min_score)) * 100
    return max(0, min(100, int(normalized)))


def format_reasoning(
    points: list,
    separator: str = " | "
) -> str:
    """
    Format reasoning points into readable string.
    
    Args:
        points: List of reasoning points
        separator: Separator between points
    
    Returns:
        Formatted reasoning string
    """
    if not points:
        return "Insufficient data for analysis"
    
    return separator.join(str(p) for p in points if p)

