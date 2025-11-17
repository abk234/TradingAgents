"""
Data Quality Validation

Checks data freshness, detects stale prices, and validates data quality
to ensure Eddie makes decisions based on accurate, timely information.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class DataQualityReport:
    """Report on data quality and validation status."""

    ticker: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Data freshness
    price_age_minutes: Optional[float] = None
    is_price_stale: bool = False
    last_price_update: Optional[datetime] = None

    # Data sources used
    price_sources: List[str] = field(default_factory=list)
    news_sources: List[str] = field(default_factory=list)
    fundamental_sources: List[str] = field(default_factory=list)

    # Validation results
    validation_score: float = 0.0  # 0-10 scale
    warnings: List[str] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)

    # Market context
    is_market_hours: bool = False
    is_trading_day: bool = True

    def add_warning(self, message: str):
        """Add a validation warning."""
        self.warnings.append(message)
        logger.warning(f"[{self.ticker}] {message}")

    def add_flag(self, message: str):
        """Add a validation flag."""
        self.flags.append(message)
        logger.info(f"[{self.ticker}] FLAG: {message}")

    def calculate_score(self) -> float:
        """
        Calculate overall data quality score (0-10).

        Scoring factors:
        - Data freshness: 4 points
        - Source diversity: 3 points
        - Warning severity: -1 per warning
        - Flags: informational only
        """
        score = 10.0

        # Penalize stale data
        if self.is_price_stale:
            if self.is_market_hours:
                score -= 4.0  # Severe penalty during market hours
            else:
                score -= 1.0  # Mild penalty outside market hours

        # Reward source diversity
        total_sources = len(set(
            self.price_sources +
            self.news_sources +
            self.fundamental_sources
        ))
        if total_sources == 1:
            score -= 2.0  # Single source = less confident
        elif total_sources == 2:
            score -= 0.5  # Two sources = acceptable
        # 3+ sources = full points

        # Penalize warnings
        score -= len(self.warnings) * 1.0

        # Ensure score stays in range
        score = max(0.0, min(10.0, score))

        self.validation_score = score
        return score

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary format."""
        return {
            "ticker": self.ticker,
            "timestamp": self.timestamp.isoformat(),
            "price_age_minutes": self.price_age_minutes,
            "is_price_stale": self.is_price_stale,
            "last_price_update": self.last_price_update.isoformat() if self.last_price_update else None,
            "price_sources": self.price_sources,
            "news_sources": self.news_sources,
            "fundamental_sources": self.fundamental_sources,
            "validation_score": self.validation_score,
            "warnings": self.warnings,
            "flags": self.flags,
            "is_market_hours": self.is_market_hours,
        }

    def format_for_display(self) -> str:
        """Format report for user display."""
        lines = [
            f"\n📊 **Data Quality Report for {self.ticker}**",
            f"Validation Score: **{self.validation_score:.1f}/10**",
        ]

        # Data freshness
        if self.price_age_minutes is not None:
            age_str = f"{self.price_age_minutes:.0f} minutes ago"
            status = "🔴 STALE" if self.is_price_stale else "✅ Fresh"
            lines.append(f"Price Data: {status} ({age_str})")

        # Data sources
        if self.price_sources:
            lines.append(f"Price Sources: {', '.join(self.price_sources)}")
        if self.news_sources:
            lines.append(f"News Sources: {', '.join(self.news_sources)}")
        if self.fundamental_sources:
            lines.append(f"Fundamental Sources: {', '.join(self.fundamental_sources)}")

        # Warnings
        if self.warnings:
            lines.append("\n⚠️ **Warnings:**")
            for warning in self.warnings:
                lines.append(f"  - {warning}")

        # Flags
        if self.flags:
            lines.append("\nℹ️ **Context:**")
            for flag in self.flags:
                lines.append(f"  - {flag}")

        return "\n".join(lines)


def is_market_open() -> bool:
    """
    Check if US stock market is currently open.

    Simple heuristic: Mon-Fri, 9:30 AM - 4:00 PM ET
    TODO: Improve with proper market calendar and holiday detection
    """
    now = datetime.now(timezone.utc)
    # Convert to Eastern Time (approximate)
    et_offset = timedelta(hours=-5)  # ET is UTC-5 (ignoring DST for simplicity)
    et_now = now + et_offset

    # Check if weekday
    if et_now.weekday() >= 5:  # Saturday=5, Sunday=6
        return False

    # Check if within market hours (9:30 AM - 4:00 PM ET)
    hour = et_now.hour
    minute = et_now.minute

    if hour < 9 or hour >= 16:
        return False
    if hour == 9 and minute < 30:
        return False

    return True


def check_price_staleness(
    ticker: str,
    last_updated: datetime,
    max_age_minutes: int = 15
) -> tuple[bool, float]:
    """
    Check if price data is stale.

    Args:
        ticker: Stock ticker symbol
        last_updated: Timestamp of last price update
        max_age_minutes: Maximum acceptable age in minutes

    Returns:
        (is_stale, age_in_minutes)
    """
    now = datetime.now(timezone.utc)

    # Ensure last_updated is timezone-aware
    if last_updated.tzinfo is None:
        last_updated = last_updated.replace(tzinfo=timezone.utc)

    age = now - last_updated
    age_minutes = age.total_seconds() / 60

    # Only flag as stale during market hours
    is_stale = False
    if is_market_open():
        is_stale = age_minutes > max_age_minutes
    else:
        # Outside market hours, allow data to be older (up to 24 hours)
        is_stale = age_minutes > (24 * 60)

    if is_stale:
        logger.warning(
            f"Stale price data for {ticker}: {age_minutes:.0f} minutes old "
            f"(threshold: {max_age_minutes} min)"
        )

    return is_stale, age_minutes


def validate_data_quality(
    ticker: str,
    price_timestamp: Optional[datetime] = None,
    price_source: str = "yfinance",
    news_source: Optional[str] = None,
    fundamental_source: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None
) -> DataQualityReport:
    """
    Validate data quality and generate a comprehensive report.

    Args:
        ticker: Stock ticker symbol
        price_timestamp: When price data was last updated
        price_source: Source of price data
        news_source: Source of news data (if available)
        fundamental_source: Source of fundamental data
        config: Validation configuration (from DEFAULT_CONFIG["validation"])

    Returns:
        DataQualityReport with validation results
    """
    if config is None:
        # Use default config
        from tradingagents.default_config import DEFAULT_CONFIG
        config = DEFAULT_CONFIG.get("validation", {})

    report = DataQualityReport(ticker=ticker)
    report.is_market_hours = is_market_open()

    # Track data sources
    report.price_sources.append(price_source)
    if news_source:
        report.news_sources.append(news_source)
    if fundamental_source:
        report.fundamental_sources.append(fundamental_source)

    # Check price staleness
    if config.get("enable_price_staleness_check", True) and price_timestamp:
        max_age = config.get("max_data_age_minutes", 15)
        is_stale, age_minutes = check_price_staleness(ticker, price_timestamp, max_age)

        report.is_price_stale = is_stale
        report.price_age_minutes = age_minutes
        report.last_price_update = price_timestamp

        if is_stale:
            if report.is_market_hours:
                report.add_warning(
                    f"Price data is {age_minutes:.0f} minutes old during market hours"
                )
            else:
                report.add_flag(
                    f"Price data is {age_minutes:.0f} minutes old (market closed, acceptable)"
                )

    # Check source diversity
    total_sources = len(set(report.price_sources + report.news_sources + report.fundamental_sources))
    if total_sources == 1:
        report.add_flag(
            "Using single data source - limited validation"
        )
    elif total_sources >= 3:
        report.add_flag(
            f"Using {total_sources} data sources - good diversity"
        )

    # Check if news data is available
    if not news_source and config.get("show_data_sources", True):
        report.add_warning(
            "No news data source configured - missing market context"
        )

    # Calculate overall validation score
    report.calculate_score()

    logger.info(
        f"Data quality validation for {ticker}: "
        f"Score={report.validation_score:.1f}/10, "
        f"Sources={total_sources}, "
        f"Warnings={len(report.warnings)}"
    )

    return report
