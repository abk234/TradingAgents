# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Data Validation Module

Provides comprehensive data quality checks for stock market data before analysis.
Validates data freshness, completeness, consistency, and reasonableness.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date, timedelta
from dataclasses import dataclass
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result from a data validation check."""
    passed: bool
    severity: str  # "error", "warning", "info"
    message: str
    details: Dict[str, Any]


class DataValidator:
    """
    Validates stock market data quality before analysis.

    Checks:
    - Data freshness (timestamps, staleness)
    - Data completeness (required fields, null values)
    - Data consistency (cross-source validation)
    - Data reasonableness (value ranges, patterns)
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize validator with configuration.

        Args:
            config: Configuration dict with validation settings
        """
        self.config = config or {}

        # Validation thresholds (configurable)
        self.max_data_age_minutes = self.config.get("max_data_age_minutes", 15)
        self.price_discrepancy_threshold = self.config.get("price_discrepancy_threshold", 2.0)
        self.max_price_change_pct = self.config.get("max_price_change_pct", 20.0)
        self.min_volume = self.config.get("min_volume", 1000)

    def validate_stock_data(
        self,
        data: str,
        ticker: str,
        expected_date: str
    ) -> ValidationResult:
        """
        Validate stock OHLCV data.

        Args:
            data: CSV string with stock data
            ticker: Ticker symbol
            expected_date: Expected date in YYYY-MM-DD format

        Returns:
            ValidationResult
        """
        if not data or len(data) == 0:
            return ValidationResult(
                passed=False,
                severity="error",
                message="Empty stock data",
                details={"ticker": ticker, "expected_date": expected_date}
            )

        # Check for required fields
        required_fields = ["Date", "Open", "High", "Low", "Close", "Volume"]
        missing_fields = [f for f in required_fields if f not in data]

        if missing_fields:
            return ValidationResult(
                passed=False,
                severity="error",
                message=f"Missing required fields: {', '.join(missing_fields)}",
                details={"ticker": ticker, "missing_fields": missing_fields}
            )

        # Check data recency (parse dates from CSV)
        try:
            # Extract dates from CSV
            lines = data.split('\n')
            date_pattern = r'\d{4}-\d{2}-\d{2}'
            dates = []
            for line in lines:
                match = re.search(date_pattern, line)
                if match:
                    dates.append(datetime.strptime(match.group(), "%Y-%m-%d"))

            if dates:
                latest_date = max(dates)
                expected_datetime = datetime.strptime(expected_date, "%Y-%m-%d")
                age_days = (expected_datetime - latest_date).days

                if age_days > 7:
                    return ValidationResult(
                        passed=False,
                        severity="warning",
                        message=f"Stale data: latest data is {age_days} days old",
                        details={
                            "ticker": ticker,
                            "latest_date": latest_date.strftime("%Y-%m-%d"),
                            "age_days": age_days
                        }
                    )
        except Exception as e:
            logger.warning(f"Could not parse dates from stock data: {e}")

        return ValidationResult(
            passed=True,
            severity="info",
            message="Stock data validation passed",
            details={"ticker": ticker, "data_length": len(data)}
        )

    def validate_price_consistency(
        self,
        prices: Dict[str, float],
        ticker: str
    ) -> ValidationResult:
        """
        Validate price consistency across multiple sources.

        Args:
            prices: Dict mapping source name to price
            ticker: Ticker symbol

        Returns:
            ValidationResult
        """
        if len(prices) < 2:
            return ValidationResult(
                passed=True,
                severity="info",
                message="Only one price source available, cannot cross-validate",
                details={"ticker": ticker, "sources": list(prices.keys())}
            )

        # Calculate price range
        price_values = list(prices.values())
        min_price = min(price_values)
        max_price = max(price_values)
        price_range_pct = ((max_price - min_price) / min_price) * 100

        if price_range_pct > self.price_discrepancy_threshold:
            return ValidationResult(
                passed=False,
                severity="warning",
                message=f"Price discrepancy of {price_range_pct:.2f}% across sources",
                details={
                    "ticker": ticker,
                    "prices": prices,
                    "min_price": min_price,
                    "max_price": max_price,
                    "discrepancy_pct": price_range_pct
                }
            )

        return ValidationResult(
            passed=True,
            severity="info",
            message=f"Price consistency validated across {len(prices)} sources",
            details={
                "ticker": ticker,
                "prices": prices,
                "discrepancy_pct": price_range_pct
            }
        )

    def validate_price_reasonableness(
        self,
        current_price: float,
        previous_price: float = None,
        ticker: str = None
    ) -> ValidationResult:
        """
        Validate that price is within reasonable bounds.

        Args:
            current_price: Current stock price
            previous_price: Previous closing price (optional)
            ticker: Ticker symbol

        Returns:
            ValidationResult
        """
        # Check for invalid values
        if current_price <= 0:
            return ValidationResult(
                passed=False,
                severity="error",
                message=f"Invalid price: {current_price}",
                details={"ticker": ticker, "price": current_price}
            )

        # Check for unreasonable prices
        if current_price < 0.01 or current_price > 1000000:
            return ValidationResult(
                passed=False,
                severity="warning",
                message=f"Unusual price: {current_price}",
                details={
                    "ticker": ticker,
                    "price": current_price,
                    "reason": "Price outside typical range"
                }
            )

        # Check price change if previous price provided
        if previous_price:
            price_change_pct = abs((current_price - previous_price) / previous_price) * 100

            if price_change_pct > self.max_price_change_pct:
                return ValidationResult(
                    passed=False,
                    severity="warning",
                    message=f"Large price change: {price_change_pct:.2f}%",
                    details={
                        "ticker": ticker,
                        "current_price": current_price,
                        "previous_price": previous_price,
                        "change_pct": price_change_pct
                    }
                )

        return ValidationResult(
            passed=True,
            severity="info",
            message="Price reasonableness validated",
            details={"ticker": ticker, "price": current_price}
        )

    def validate_volume(
        self,
        volume: int,
        ticker: str
    ) -> ValidationResult:
        """
        Validate trading volume.

        Args:
            volume: Trading volume
            ticker: Ticker symbol

        Returns:
            ValidationResult
        """
        if volume < 0:
            return ValidationResult(
                passed=False,
                severity="error",
                message=f"Invalid volume: {volume}",
                details={"ticker": ticker, "volume": volume}
            )

        if volume < self.min_volume:
            return ValidationResult(
                passed=False,
                severity="warning",
                message=f"Very low volume: {volume}",
                details={
                    "ticker": ticker,
                    "volume": volume,
                    "min_volume": self.min_volume
                }
            )

        return ValidationResult(
            passed=True,
            severity="info",
            message="Volume validated",
            details={"ticker": ticker, "volume": volume}
        )

    def validate_fundamentals(
        self,
        fundamentals: Dict[str, Any],
        ticker: str
    ) -> ValidationResult:
        """
        Validate fundamental data completeness and reasonableness.

        Args:
            fundamentals: Dictionary with fundamental metrics
            ticker: Ticker symbol

        Returns:
            ValidationResult
        """
        if not fundamentals:
            return ValidationResult(
                passed=False,
                severity="warning",
                message="No fundamental data available",
                details={"ticker": ticker}
            )

        # Check for key metrics
        important_metrics = ["pe_ratio", "market_cap", "revenue"]
        missing_metrics = [m for m in important_metrics if m not in fundamentals or fundamentals[m] is None]

        if missing_metrics:
            return ValidationResult(
                passed=False,
                severity="warning",
                message=f"Missing important metrics: {', '.join(missing_metrics)}",
                details={
                    "ticker": ticker,
                    "missing_metrics": missing_metrics,
                    "available_metrics": list(fundamentals.keys())
                }
            )

        # Validate P/E ratio reasonableness
        if "pe_ratio" in fundamentals:
            pe_ratio = fundamentals["pe_ratio"]
            if pe_ratio and (pe_ratio < 0 or pe_ratio > 1000):
                return ValidationResult(
                    passed=False,
                    severity="warning",
                    message=f"Unusual P/E ratio: {pe_ratio}",
                    details={"ticker": ticker, "pe_ratio": pe_ratio}
                )

        return ValidationResult(
            passed=True,
            severity="info",
            message="Fundamentals validated",
            details={
                "ticker": ticker,
                "metrics_count": len(fundamentals)
            }
        )

    def validate_all(
        self,
        ticker: str,
        data_dict: Dict[str, Any]
    ) -> List[ValidationResult]:
        """
        Run all applicable validations on provided data.

        Args:
            ticker: Ticker symbol
            data_dict: Dictionary with various data types to validate

        Returns:
            List of ValidationResult objects
        """
        results = []

        # Validate stock data if provided
        if "stock_data" in data_dict:
            results.append(
                self.validate_stock_data(
                    data_dict["stock_data"],
                    ticker,
                    data_dict.get("expected_date", date.today().strftime("%Y-%m-%d"))
                )
            )

        # Validate price consistency if multiple sources
        if "prices" in data_dict and isinstance(data_dict["prices"], dict):
            results.append(
                self.validate_price_consistency(data_dict["prices"], ticker)
            )

        # Validate fundamentals if provided
        if "fundamentals" in data_dict:
            results.append(
                self.validate_fundamentals(data_dict["fundamentals"], ticker)
            )

        # Validate current price
        if "current_price" in data_dict:
            results.append(
                self.validate_price_reasonableness(
                    data_dict["current_price"],
                    data_dict.get("previous_price"),
                    ticker
                )
            )

        # Validate volume
        if "volume" in data_dict:
            results.append(
                self.validate_volume(data_dict["volume"], ticker)
            )

        return results

    def get_validation_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """
        Get summary of validation results.

        Args:
            results: List of ValidationResult objects

        Returns:
            Summary dictionary
        """
        passed = sum(1 for r in results if r.passed)
        failed = sum(1 for r in results if not r.passed)

        errors = [r for r in results if r.severity == "error"]
        warnings = [r for r in results if r.severity == "warning"]

        return {
            "total_checks": len(results),
            "passed": passed,
            "failed": failed,
            "errors": len(errors),
            "warnings": len(warnings),
            "all_passed": failed == 0 and len(errors) == 0,
            "error_messages": [r.message for r in errors],
            "warning_messages": [r.message for r in warnings]
        }
