"""
Earnings Calendar Integration Module

Checks for upcoming earnings announcements and warns when recommendations
are made close to earnings dates (increased volatility risk).
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict
import json
import pandas as pd

@dataclass
class EarningsEvent:
    """Represents an upcoming or recent earnings event"""
    ticker: str
    report_date: datetime
    fiscal_period: str  # e.g., "2024 Q3"
    estimate_eps: Optional[float] = None
    reported_eps: Optional[float] = None
    surprise_percent: Optional[float] = None
    is_upcoming: bool = True

    def days_until_earnings(self) -> int:
        """Calculate days until (or since) earnings"""
        delta = self.report_date - datetime.now(timezone.utc)
        return delta.days

    def is_earnings_proximity(self, days_before: int = 7, days_after: int = 3) -> bool:
        """Check if we're in earnings proximity window"""
        days = self.days_until_earnings()
        return -days_after <= days <= days_before


@dataclass
class EarningsProximityReport:
    """Report on earnings calendar proximity for trading decisions"""
    ticker: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    upcoming_earnings: Optional[EarningsEvent] = None
    recent_earnings: Optional[EarningsEvent] = None

    is_in_proximity_window: bool = False
    days_until_next_earnings: Optional[int] = None
    proximity_risk_level: str = "LOW"  # LOW, MEDIUM, HIGH

    warnings: List[str] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)

    def calculate_risk_level(self) -> str:
        """
        Calculate risk level based on earnings proximity.

        Risk Levels:
        - HIGH: Within 3 days before or 1 day after earnings
        - MEDIUM: Within 7 days before or 3 days after earnings
        - LOW: Outside earnings window
        """
        if not self.upcoming_earnings:
            return "LOW"

        days = self.upcoming_earnings.days_until_earnings()

        if -1 <= days <= 3:
            self.proximity_risk_level = "HIGH"
            self.is_in_proximity_window = True
            self.warnings.append(
                f"⚠️ EARNINGS IN {abs(days)} DAYS - Very high volatility risk"
            )
        elif -3 <= days <= 7:
            self.proximity_risk_level = "MEDIUM"
            self.is_in_proximity_window = True
            self.warnings.append(
                f"⚠️ Earnings in {days} days - Elevated volatility risk"
            )
        else:
            self.proximity_risk_level = "LOW"
            self.flags.append(f"Next earnings in {days} days - Safe window")

        return self.proximity_risk_level

    def format_for_display(self) -> str:
        """Format the earnings proximity report for display"""
        lines = [f"📅 Earnings Calendar Check for {self.ticker}"]
        lines.append("")

        if self.upcoming_earnings:
            days = self.upcoming_earnings.days_until_earnings()
            date_str = self.upcoming_earnings.report_date.strftime("%Y-%m-%d")

            if days > 0:
                lines.append(f"Next Earnings: {date_str} ({days} days away)")
            elif days == 0:
                lines.append(f"⚠️ EARNINGS TODAY: {date_str}")
            else:
                lines.append(f"Recent Earnings: {date_str} ({abs(days)} days ago)")

            lines.append(f"Fiscal Period: {self.upcoming_earnings.fiscal_period}")

            if self.upcoming_earnings.estimate_eps:
                lines.append(f"EPS Estimate: ${self.upcoming_earnings.estimate_eps:.2f}")

            lines.append("")

        # Risk assessment
        risk_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
        emoji = risk_emoji.get(self.proximity_risk_level, "⚪")
        lines.append(f"Proximity Risk: {emoji} {self.proximity_risk_level}")
        lines.append("")

        # Warnings
        if self.warnings:
            lines.append("⚠️ Warnings:")
            for warning in self.warnings:
                lines.append(f"  - {warning}")
            lines.append("")

        # Context
        if self.flags:
            lines.append("ℹ️ Context:")
            for flag in self.flags:
                lines.append(f"  - {flag}")

        # Trading recommendation
        if self.proximity_risk_level == "HIGH":
            lines.append("")
            lines.append("💡 Recommendation: Avoid new positions - wait until after earnings")
        elif self.proximity_risk_level == "MEDIUM":
            lines.append("")
            lines.append("💡 Recommendation: Exercise caution - consider waiting for earnings clarity")

        return "\n".join(lines)


def get_earnings_calendar_yfinance(ticker: str) -> Optional[EarningsEvent]:
    """
    Fetch earnings calendar from yfinance.

    Returns:
        EarningsEvent or None if no data available
    """
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)

        # Get earnings dates
        calendar = stock.calendar

        if calendar is None:
            return None

        # Handle both DataFrame and dict return types from yfinance
        if isinstance(calendar, dict):
            # If calendar is a dict, extract earnings date directly
            earnings_date_str = None
            eps_estimate = None
            
            # Try different possible keys in the dict
            if 'Earnings Date' in calendar:
                earnings_date_str = calendar['Earnings Date']
            elif 'earningsDate' in calendar:
                earnings_date_str = calendar['earningsDate']
            
            if 'Earnings Estimate' in calendar:
                try:
                    eps_estimate = float(calendar['Earnings Estimate'])
                except (ValueError, TypeError):
                    pass
            
            if not earnings_date_str:
                return None
            
            # Handle multiple dates (can be a list or tuple)
            if isinstance(earnings_date_str, (list, tuple)) and len(earnings_date_str) > 0:
                earnings_date_str = earnings_date_str[0]
            elif not isinstance(earnings_date_str, str):
                return None
            
            earnings_date = pd.to_datetime(earnings_date_str)
            
        elif isinstance(calendar, pd.DataFrame):
            # Original DataFrame handling
            if calendar.empty:
                return None

            # Extract next earnings date
            if 'Earnings Date' not in calendar.index:
                return None
                
            earnings_dates = calendar.loc['Earnings Date']

            if isinstance(earnings_dates, str):
                # Single date
                earnings_date = pd.to_datetime(earnings_dates)
            elif hasattr(earnings_dates, '__iter__') and len(earnings_dates) > 0:
                # Multiple dates - take the first (earliest)
                earnings_date = pd.to_datetime(earnings_dates[0])
            else:
                return None

            # Get EPS estimate if available
            eps_estimate = None
            if 'Earnings Estimate' in calendar.index:
                try:
                    eps_estimate = float(calendar.loc['Earnings Estimate'])
                except (ValueError, TypeError):
                    pass
        else:
            # Unknown type
            return None

        # Convert to timezone-aware datetime
        if earnings_date.tzinfo is None:
            earnings_date = earnings_date.replace(tzinfo=timezone.utc)

        return EarningsEvent(
            ticker=ticker,
            report_date=earnings_date,
            fiscal_period="Unknown",  # yfinance doesn't provide this easily
            estimate_eps=eps_estimate,
            is_upcoming=(earnings_date > datetime.now(timezone.utc))
        )

    except Exception as e:
        print(f"Error fetching yfinance earnings calendar for {ticker}: {e}")
        return None


def get_earnings_calendar_alphavantage(ticker: str) -> Optional[EarningsEvent]:
    """
    Fetch earnings calendar from Alpha Vantage.
    Uses EARNINGS_CALENDAR API.

    Returns:
        EarningsEvent or None if no data available
    """
    try:
        from tradingagents.dataflows.alpha_vantage_common import _make_api_request, AlphaVantageRateLimitError, get_api_key

        # Check if API key is available before attempting request
        try:
            api_key = get_api_key()
        except ValueError:
            # API key not set - silently return None (this is expected for many users)
            return None

        # Note: EARNINGS_CALENDAR requires premium API key
        # For free tier, we'll use EARNINGS API which gives historical data
        params = {
            "symbol": ticker,
        }

        response = _make_api_request("EARNINGS", params)

        # Parse JSON response
        data = json.loads(response)

        if "quarterlyEarnings" in data and len(data["quarterlyEarnings"]) > 0:
            # Get the most recent quarterly earnings
            latest = data["quarterlyEarnings"][0]

            report_date_str = latest.get("reportedDate")
            if not report_date_str:
                return None

            report_date = datetime.strptime(report_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)

            reported_eps = None
            estimate_eps = None
            surprise_percent = None

            try:
                reported_eps = float(latest.get("reportedEPS", 0))
                estimate_eps = float(latest.get("estimatedEPS", 0))
                if reported_eps and estimate_eps:
                    surprise_percent = ((reported_eps - estimate_eps) / abs(estimate_eps)) * 100
            except (ValueError, TypeError, ZeroDivisionError):
                pass

            fiscal_period = f"{latest.get('fiscalDateEnding', 'Unknown')}"

            return EarningsEvent(
                ticker=ticker,
                report_date=report_date,
                fiscal_period=fiscal_period,
                estimate_eps=estimate_eps,
                reported_eps=reported_eps,
                surprise_percent=surprise_percent,
                is_upcoming=(report_date > datetime.now(timezone.utc))
            )

    except AlphaVantageRateLimitError as e:
        print(f"Alpha Vantage rate limit for earnings calendar {ticker}: {e}")
        return None
    except Exception as e:
        print(f"Error fetching Alpha Vantage earnings calendar for {ticker}: {e}")
        return None


def check_earnings_proximity(
    ticker: str,
    days_before: int = 7,
    days_after: int = 3
) -> EarningsProximityReport:
    """
    Check if stock is in earnings proximity window.

    Args:
        ticker: Stock ticker symbol
        days_before: Days before earnings to consider risky (default 7)
        days_after: Days after earnings to consider risky (default 3)

    Returns:
        EarningsProximityReport with risk assessment
    """
    report = EarningsProximityReport(ticker=ticker.upper())

    # Try yfinance first (has forward-looking calendar)
    upcoming = get_earnings_calendar_yfinance(ticker)

    # Fallback to Alpha Vantage if yfinance fails
    if not upcoming:
        upcoming = get_earnings_calendar_alphavantage(ticker)

    if upcoming:
        report.upcoming_earnings = upcoming
        report.days_until_next_earnings = upcoming.days_until_earnings()

        # Categorize as upcoming or recent
        if upcoming.is_upcoming:
            report.upcoming_earnings = upcoming
        else:
            report.recent_earnings = upcoming

        # Calculate risk level
        report.calculate_risk_level()
    else:
        report.flags.append("No earnings data available")
        report.proximity_risk_level = "UNKNOWN"

    return report
