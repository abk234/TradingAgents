"""
Multi-Source Price Validation Module

Validates stock prices by cross-referencing multiple data sources (yfinance and Alpha Vantage).
Detects price discrepancies and provides confidence metrics for price data.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple, List
import pandas as pd
from io import StringIO

@dataclass
class PriceValidationReport:
    """Report containing multi-source price validation results"""
    ticker: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Price data from different sources
    yfinance_price: Optional[float] = None
    alphavantage_price: Optional[float] = None

    # Validation metrics
    price_discrepancy_percent: Optional[float] = None
    is_discrepancy_significant: bool = False
    validation_passed: bool = True
    confidence_score: float = 0.0  # 0-10 scale

    # Volume data
    yfinance_volume: Optional[int] = None
    alphavantage_volume: Optional[int] = None
    volume_discrepancy_percent: Optional[float] = None

    # Metadata
    warnings: List[str] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)
    sources_checked: List[str] = field(default_factory=list)

    def calculate_discrepancy(self, threshold_percent: float = 2.0) -> None:
        """
        Calculate price discrepancy between sources.

        Args:
            threshold_percent: Maximum acceptable discrepancy (default 2%)
        """
        if self.yfinance_price and self.alphavantage_price:
            diff = abs(self.yfinance_price - self.alphavantage_price)
            avg_price = (self.yfinance_price + self.alphavantage_price) / 2
            self.price_discrepancy_percent = (diff / avg_price) * 100 if avg_price > 0 else 0

            if self.price_discrepancy_percent > threshold_percent:
                self.is_discrepancy_significant = True
                self.validation_passed = False
                self.warnings.append(
                    f"Price discrepancy: {self.price_discrepancy_percent:.2f}% "
                    f"(yfinance: ${self.yfinance_price:.2f}, "
                    f"alphavantage: ${self.alphavantage_price:.2f})"
                )
            else:
                self.flags.append(
                    f"Prices validated across sources (discrepancy: {self.price_discrepancy_percent:.2f}%)"
                )

    def calculate_volume_discrepancy(self, threshold_percent: float = 10.0) -> None:
        """Calculate volume discrepancy between sources"""
        if self.yfinance_volume and self.alphavantage_volume:
            diff = abs(self.yfinance_volume - self.alphavantage_volume)
            avg_volume = (self.yfinance_volume + self.alphavantage_volume) / 2
            self.volume_discrepancy_percent = (diff / avg_volume) * 100 if avg_volume > 0 else 0

            if self.volume_discrepancy_percent > threshold_percent:
                self.warnings.append(
                    f"Volume discrepancy: {self.volume_discrepancy_percent:.1f}% "
                    f"between sources"
                )

    def calculate_confidence(self) -> float:
        """
        Calculate overall confidence score (0-10) for price validation.

        Scoring:
        - 10: Perfect match between sources
        - 7-9: Small discrepancy (<1%)
        - 4-6: Moderate discrepancy (1-2%)
        - 0-3: Large discrepancy (>2%) or missing data
        """
        score = 10.0

        # Penalize if only one source available
        if not self.yfinance_price or not self.alphavantage_price:
            score = 6.0  # Single source = moderate confidence
            self.flags.append("Single price source - reduced confidence")

        # Penalize based on price discrepancy
        if self.price_discrepancy_percent is not None:
            if self.price_discrepancy_percent > 2.0:
                score = 3.0  # Severe discrepancy
            elif self.price_discrepancy_percent > 1.0:
                score = min(score, 6.0)
            elif self.price_discrepancy_percent > 0.5:
                score = min(score, 8.0)

        # Penalize for validation failure
        if not self.validation_passed:
            score = min(score, 4.0)

        # Reward for warnings-free validation
        if not self.warnings and len(self.sources_checked) >= 2:
            score = max(score, 9.0)

        self.confidence_score = max(0.0, min(10.0, score))
        return self.confidence_score

    def format_for_display(self) -> str:
        """Format the validation report for user-friendly display"""
        lines = [f"📊 Multi-Source Price Validation for {self.ticker}"]
        lines.append(f"Confidence Score: {self.confidence_score:.1f}/10")
        lines.append("")

        # Price comparison
        if self.yfinance_price and self.alphavantage_price:
            lines.append(f"Price Comparison:")
            lines.append(f"  yfinance:     ${self.yfinance_price:.2f}")
            lines.append(f"  Alpha Vantage: ${self.alphavantage_price:.2f}")
            if self.price_discrepancy_percent is not None:
                symbol = "✅" if self.price_discrepancy_percent < 1.0 else "⚠️"
                lines.append(f"  Discrepancy: {symbol} {self.price_discrepancy_percent:.2f}%")
        else:
            lines.append(f"Price Data:")
            if self.yfinance_price:
                lines.append(f"  yfinance: ${self.yfinance_price:.2f}")
            if self.alphavantage_price:
                lines.append(f"  Alpha Vantage: ${self.alphavantage_price:.2f}")

        lines.append("")

        # Volume comparison
        if self.yfinance_volume and self.alphavantage_volume:
            lines.append(f"Volume Comparison:")
            lines.append(f"  yfinance:     {self.yfinance_volume:,}")
            lines.append(f"  Alpha Vantage: {self.alphavantage_volume:,}")
            if self.volume_discrepancy_percent is not None:
                lines.append(f"  Discrepancy: {self.volume_discrepancy_percent:.1f}%")
            lines.append("")

        # Validation status
        if self.validation_passed:
            lines.append("✅ Validation: PASSED")
        else:
            lines.append("❌ Validation: FAILED")

        lines.append(f"Sources Checked: {', '.join(self.sources_checked)}")
        lines.append("")

        # Warnings
        if self.warnings:
            lines.append("⚠️ Warnings:")
            for warning in self.warnings:
                lines.append(f"  - {warning}")
            lines.append("")

        # Context flags
        if self.flags:
            lines.append("ℹ️ Context:")
            for flag in self.flags:
                lines.append(f"  - {flag}")

        return "\n".join(lines)


def get_yfinance_current_price(ticker: str) -> Tuple[Optional[float], Optional[int]]:
    """
    Fetch current price and volume from yfinance.

    Returns:
        Tuple of (price, volume) or (None, None) on error
    """
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        info = stock.info

        # Try to get the most recent price
        price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
        volume = info.get('volume') or info.get('regularMarketVolume')

        return (price, volume)
    except Exception as e:
        print(f"Error fetching yfinance data for {ticker}: {e}")
        return (None, None)


def get_alphavantage_current_price(ticker: str) -> Tuple[Optional[float], Optional[int]]:
    """
    Fetch current price and volume from Alpha Vantage.
    Uses GLOBAL_QUOTE API for real-time data.

    Returns:
        Tuple of (price, volume) or (None, None) on error
    """
    try:
        from tradingagents.dataflows.alpha_vantage_common import _make_api_request, AlphaVantageRateLimitError

        params = {
            "symbol": ticker,
        }

        response = _make_api_request("GLOBAL_QUOTE", params)

        # Parse JSON response
        import json
        data = json.loads(response)

        if "Global Quote" in data:
            quote = data["Global Quote"]
            price = float(quote.get("05. price", 0))
            volume = int(quote.get("06. volume", 0))
            return (price if price > 0 else None, volume if volume > 0 else None)

        return (None, None)
    except AlphaVantageRateLimitError as e:
        print(f"Alpha Vantage rate limit for {ticker}: {e}")
        return (None, None)
    except Exception as e:
        print(f"Error fetching Alpha Vantage data for {ticker}: {e}")
        return (None, None)


def validate_price_multi_source(
    ticker: str,
    discrepancy_threshold: float = 2.0,
    volume_threshold: float = 10.0
) -> PriceValidationReport:
    """
    Validate stock price by comparing multiple data sources.

    Args:
        ticker: Stock ticker symbol
        discrepancy_threshold: Maximum acceptable price discrepancy (%)
        volume_threshold: Maximum acceptable volume discrepancy (%)

    Returns:
        PriceValidationReport with validation results
    """
    report = PriceValidationReport(ticker=ticker.upper())

    # Fetch from yfinance
    yf_price, yf_volume = get_yfinance_current_price(ticker)
    if yf_price:
        report.yfinance_price = yf_price
        report.yfinance_volume = yf_volume
        report.sources_checked.append("yfinance")

    # Fetch from Alpha Vantage
    av_price, av_volume = get_alphavantage_current_price(ticker)
    if av_price:
        report.alphavantage_price = av_price
        report.alphavantage_volume = av_volume
        report.sources_checked.append("alpha_vantage")

    # Calculate discrepancies
    report.calculate_discrepancy(threshold_percent=discrepancy_threshold)
    report.calculate_volume_discrepancy(threshold_percent=volume_threshold)

    # Calculate overall confidence
    report.calculate_confidence()

    # Add warning if no sources available
    if not report.sources_checked:
        report.warnings.append("No price data sources available")
        report.validation_passed = False
        report.confidence_score = 0.0

    return report


def check_volume_anomaly(ticker: str, current_volume: int, lookback_days: int = 20) -> Tuple[bool, Optional[float]]:
    """
    Check if current volume is anomalous compared to historical average.

    Args:
        ticker: Stock ticker symbol
        current_volume: Current trading volume
        lookback_days: Days to look back for average calculation

    Returns:
        Tuple of (is_anomalous, volume_ratio)
    """
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)

        # Get historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days + 5)
        hist = stock.history(start=start_date, end=end_date)

        if hist.empty or len(hist) < lookback_days:
            return (False, None)

        # Calculate average volume
        avg_volume = hist['Volume'].tail(lookback_days).mean()

        if avg_volume == 0:
            return (False, None)

        volume_ratio = current_volume / avg_volume

        # Volume spike if 2x+ average, or volume drought if <0.3x average
        is_anomalous = volume_ratio > 2.0 or volume_ratio < 0.3

        return (is_anomalous, volume_ratio)

    except Exception as e:
        print(f"Error checking volume anomaly for {ticker}: {e}")
        return (False, None)
