# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Validation Gates for Data Quality

Implements validation gates that check data quality before trading decisions:
- Data Freshness Gate: Checks if data is recent enough
- Multi-Source Validation Gate: Cross-validates prices across sources
- Earnings Proximity Gate: Warns about earnings date volatility
- External Intelligence Gate: Validates against external signals (future)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationGateResult:
    """Result from a validation gate."""
    passed: bool
    gate_name: str
    score: int  # 0-100
    message: str
    details: Dict[str, Any]
    recommendations: List[str]


class DataFreshnessGate:
    """
    Validates that data is fresh enough for decision-making.

    Checks:
    - Timestamp of last data update
    - Age of data during market hours
    - Staleness warnings
    """

    def __init__(self, max_age_minutes: int = 15):
        """
        Initialize gate with maximum allowed data age.

        Args:
            max_age_minutes: Maximum data age in minutes during market hours
        """
        self.max_age_minutes = max_age_minutes

    def validate(
        self,
        ticker: str,
        data_timestamp: datetime,
        current_time: datetime = None
    ) -> ValidationGateResult:
        """
        Validate data freshness.

        Args:
            ticker: Ticker symbol
            data_timestamp: When data was last updated
            current_time: Current time (defaults to now)

        Returns:
            ValidationGateResult
        """
        if current_time is None:
            current_time = datetime.now()

        age_minutes = (current_time - data_timestamp).total_seconds() / 60
        age_hours = age_minutes / 60

        # Scoring based on age
        if age_minutes <= self.max_age_minutes:
            score = 100
            severity = "info"
            message = f"Data is fresh ({age_minutes:.1f} minutes old)"
            passed = True
        elif age_minutes <= 60:
            score = 80
            severity = "warning"
            message = f"Data is {age_minutes:.1f} minutes old (acceptable)"
            passed = True
        elif age_hours <= 24:
            score = 50
            severity = "warning"
            message = f"Data is {age_hours:.1f} hours old (consider refreshing)"
            passed = True
        else:
            score = 20
            severity = "error"
            message = f"Data is {age_hours:.1f} hours old (stale)"
            passed = False

        recommendations = []
        if not passed:
            recommendations.append("Refresh data before making trading decisions")
            recommendations.append("Verify market is open and data sources are accessible")
        elif score < 80:
            recommendations.append("Consider refreshing data for more accurate analysis")

        return ValidationGateResult(
            passed=passed,
            gate_name="Data Freshness",
            score=score,
            message=message,
            details={
                "ticker": ticker,
                "data_timestamp": data_timestamp.isoformat(),
                "current_time": current_time.isoformat(),
                "age_minutes": age_minutes,
                "max_age_minutes": self.max_age_minutes,
                "severity": severity
            },
            recommendations=recommendations
        )


class MultiSourceValidationGate:
    """
    Validates data consistency across multiple sources.

    Checks:
    - Price agreement across vendors
    - Volume consistency
    - Fundamental data alignment
    """

    def __init__(self, price_threshold_pct: float = 2.0):
        """
        Initialize gate with price discrepancy threshold.

        Args:
            price_threshold_pct: Maximum acceptable price difference (%)
        """
        self.price_threshold_pct = price_threshold_pct

    def validate(
        self,
        ticker: str,
        prices: Dict[str, float]
    ) -> ValidationGateResult:
        """
        Validate price consistency across sources.

        Args:
            ticker: Ticker symbol
            prices: Dict mapping source name to price (e.g., {"yfinance": 150.25, "alpha_vantage": 150.30})

        Returns:
            ValidationGateResult
        """
        if len(prices) < 2:
            return ValidationGateResult(
                passed=True,
                gate_name="Multi-Source Validation",
                score=50,
                message="Only one price source available (cannot cross-validate)",
                details={
                    "ticker": ticker,
                    "sources": list(prices.keys()),
                    "source_count": len(prices)
                },
                recommendations=["Consider enabling multiple data sources for cross-validation"]
            )

        # Calculate price statistics
        price_values = list(prices.values())
        min_price = min(price_values)
        max_price = max(price_values)
        avg_price = sum(price_values) / len(price_values)
        price_range = max_price - min_price
        discrepancy_pct = (price_range / min_price) * 100

        # Scoring based on discrepancy
        if discrepancy_pct <= self.price_threshold_pct / 2:
            score = 100
            severity = "info"
            message = f"Prices highly consistent across {len(prices)} sources ({discrepancy_pct:.2f}% variance)"
            passed = True
        elif discrepancy_pct <= self.price_threshold_pct:
            score = 85
            severity = "info"
            message = f"Prices consistent across {len(prices)} sources ({discrepancy_pct:.2f}% variance)"
            passed = True
        elif discrepancy_pct <= self.price_threshold_pct * 2:
            score = 60
            severity = "warning"
            message = f"Moderate price discrepancy detected ({discrepancy_pct:.2f}% variance)"
            passed = True
        else:
            score = 30
            severity = "error"
            message = f"High price discrepancy detected ({discrepancy_pct:.2f}% variance)"
            passed = False

        recommendations = []
        if not passed:
            recommendations.append("Investigate source of price discrepancy before trading")
            recommendations.append("Check for stock splits, dividends, or data errors")
            recommendations.append("Use the most reliable source or wait for consistency")
        elif score < 85:
            recommendations.append("Monitor price sources for convergence")

        return ValidationGateResult(
            passed=passed,
            gate_name="Multi-Source Validation",
            score=score,
            message=message,
            details={
                "ticker": ticker,
                "prices": prices,
                "min_price": min_price,
                "max_price": max_price,
                "avg_price": avg_price,
                "discrepancy_pct": discrepancy_pct,
                "threshold_pct": self.price_threshold_pct,
                "severity": severity
            },
            recommendations=recommendations
        )


class EarningsProximityGate:
    """
    Validates timing relative to earnings announcements.

    Checks:
    - Days until/since earnings
    - Volatility warning period
    - Recommendation to wait
    """

    def __init__(
        self,
        days_before: int = 7,
        days_after: int = 3
    ):
        """
        Initialize gate with earnings proximity windows.

        Args:
            days_before: Days before earnings to warn
            days_after: Days after earnings to warn
        """
        self.days_before = days_before
        self.days_after = days_after

    def validate(
        self,
        ticker: str,
        analysis_date: date,
        earnings_date: Optional[date] = None
    ) -> ValidationGateResult:
        """
        Validate timing relative to earnings.

        Args:
            ticker: Ticker symbol
            analysis_date: Date of analysis
            earnings_date: Next earnings date (None if unknown)

        Returns:
            ValidationGateResult
        """
        if earnings_date is None:
            return ValidationGateResult(
                passed=True,
                gate_name="Earnings Proximity",
                score=75,
                message="Earnings date unknown (cannot validate proximity)",
                details={
                    "ticker": ticker,
                    "analysis_date": analysis_date.isoformat(),
                    "earnings_date": None
                },
                recommendations=["Consider checking earnings calendar for upcoming dates"]
            )

        days_until = (earnings_date - analysis_date).days

        # Check if we're in the warning window
        in_warning_window = (
            (-self.days_after <= days_until <= self.days_before)
        )

        if in_warning_window:
            if days_until > 0:
                score = 40
                severity = "warning"
                message = f"Earnings in {days_until} days - high volatility period"
                position = "before"
            elif days_until == 0:
                score = 20
                severity = "error"
                message = "Earnings announcement today - avoid new positions"
                position = "today"
            else:
                score = 50
                severity = "warning"
                message = f"Earnings was {abs(days_until)} days ago - elevated volatility"
                position = "after"

            passed = score >= 50

            recommendations = [
                "Consider waiting until earnings volatility subsides",
                "If entering position, use smaller size and wider stops",
                "Monitor earnings call and guidance closely"
            ]
        else:
            score = 100
            severity = "info"
            if days_until > 0:
                message = f"Safe period: {days_until} days until earnings"
            else:
                message = f"Safe period: {abs(days_until)} days since earnings"
            passed = True
            position = "safe"
            recommendations = []

        return ValidationGateResult(
            passed=passed,
            gate_name="Earnings Proximity",
            score=score,
            message=message,
            details={
                "ticker": ticker,
                "analysis_date": analysis_date.isoformat(),
                "earnings_date": earnings_date.isoformat() if earnings_date else None,
                "days_until": days_until,
                "days_before_threshold": self.days_before,
                "days_after_threshold": self.days_after,
                "in_warning_window": in_warning_window,
                "position": position,
                "severity": severity
            },
            recommendations=recommendations
        )


class ValidationGateOrchestrator:
    """
    Orchestrates all validation gates for comprehensive data quality checks.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize orchestrator with configuration.

        Args:
            config: Configuration dict from DEFAULT_CONFIG
        """
        self.config = config or {}

        # Initialize gates based on config
        validation_config = self.config.get("validation", {})

        self.data_freshness_gate = DataFreshnessGate(
            max_age_minutes=validation_config.get("max_data_age_minutes", 15)
        )

        self.multi_source_gate = MultiSourceValidationGate(
            price_threshold_pct=validation_config.get("price_discrepancy_threshold", 2.0)
        )

        self.earnings_gate = EarningsProximityGate(
            days_before=validation_config.get("earnings_days_before", 7),
            days_after=validation_config.get("earnings_days_after", 3)
        )

        # Check which gates are enabled
        self.enable_freshness_check = validation_config.get("enable_price_staleness_check", True)
        self.enable_multi_source = validation_config.get("require_multi_source_validation", True)
        self.enable_earnings_check = validation_config.get("check_earnings_proximity", True)

    def validate_all(
        self,
        ticker: str,
        validation_data: Dict[str, Any]
    ) -> List[ValidationGateResult]:
        """
        Run all enabled validation gates.

        Args:
            ticker: Ticker symbol
            validation_data: Dictionary with validation inputs:
                - data_timestamp: datetime
                - prices: Dict[str, float]
                - earnings_date: date (optional)
                - analysis_date: date

        Returns:
            List of ValidationGateResult objects
        """
        results = []

        # Data freshness gate
        if self.enable_freshness_check and "data_timestamp" in validation_data:
            results.append(
                self.data_freshness_gate.validate(
                    ticker,
                    validation_data["data_timestamp"],
                    validation_data.get("current_time")
                )
            )

        # Multi-source validation gate
        if self.enable_multi_source and "prices" in validation_data:
            results.append(
                self.multi_source_gate.validate(
                    ticker,
                    validation_data["prices"]
                )
            )

        # Earnings proximity gate
        if self.enable_earnings_check and "analysis_date" in validation_data:
            results.append(
                self.earnings_gate.validate(
                    ticker,
                    validation_data["analysis_date"],
                    validation_data.get("earnings_date")
                )
            )

        return results

    def get_overall_result(
        self,
        results: List[ValidationGateResult]
    ) -> Dict[str, Any]:
        """
        Get overall validation result from individual gate results.

        Args:
            results: List of gate results

        Returns:
            Dictionary with overall assessment
        """
        if not results:
            return {
                "all_passed": True,
                "avg_score": 100,
                "gates_passed": 0,
                "gates_total": 0,
                "severity": "info",
                "message": "No validation gates executed"
            }

        passed_count = sum(1 for r in results if r.passed)
        total_count = len(results)
        avg_score = sum(r.score for r in results) / total_count

        all_passed = passed_count == total_count

        # Determine overall severity
        failed_results = [r for r in results if not r.passed]
        if failed_results:
            severity = "error"
            message = f"{len(failed_results)} validation gate(s) failed"
        else:
            low_scores = [r for r in results if r.score < 80]
            if low_scores:
                severity = "warning"
                message = f"{len(low_scores)} validation gate(s) have low confidence"
            else:
                severity = "info"
                message = "All validation gates passed"

        all_recommendations = []
        for result in results:
            all_recommendations.extend(result.recommendations)

        return {
            "all_passed": all_passed,
            "avg_score": avg_score,
            "gates_passed": passed_count,
            "gates_total": total_count,
            "severity": severity,
            "message": message,
            "individual_results": [
                {
                    "gate": r.gate_name,
                    "passed": r.passed,
                    "score": r.score,
                    "message": r.message
                }
                for r in results
            ],
            "recommendations": list(set(all_recommendations))  # Remove duplicates
        }
