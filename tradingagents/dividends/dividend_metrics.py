"""
Dividend metrics and analysis.

Provides dividend-based investment analysis and recommendations.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

from tradingagents.database import DatabaseConnection
from .dividend_fetcher import DividendFetcher, get_ticker_id
from .dividend_calendar import DividendCalendar

logger = logging.getLogger(__name__)


class DividendMetrics:
    """Calculates dividend-based investment metrics and provides recommendations."""

    def __init__(self, db_conn: Optional[DatabaseConnection] = None):
        """
        Initialize dividend metrics calculator.

        Args:
            db_conn: Database connection (creates new if not provided)
        """
        self.db = db_conn or DatabaseConnection()
        self.fetcher = DividendFetcher(db_conn)
        self.calendar = DividendCalendar(db_conn)

    def get_high_yield_stocks(
        self,
        min_yield: float = 3.0,
        min_consecutive_years: int = 5,
        max_payout_ratio: Optional[float] = 80.0
    ) -> List[Dict[str, Any]]:
        """
        Find high-quality dividend stocks.

        Args:
            min_yield: Minimum dividend yield percentage
            min_consecutive_years: Minimum years of consecutive payments
            max_payout_ratio: Maximum payout ratio (sustainability check)

        Returns:
            List of high-yield dividend stocks
        """
        try:
            query = """
                SELECT
                    t.symbol,
                    t.company_name,
                    t.sector,
                    dyc.dividend_yield_pct,
                    dyc.annual_dividend,
                    dyc.current_price,
                    dyc.payout_frequency,
                    dyc.dividend_growth_1yr_pct,
                    dyc.dividend_growth_3yr_pct,
                    dyc.dividend_growth_5yr_pct,
                    dyc.consecutive_years_paid,
                    dyc.payout_ratio_pct,
                    dyc.last_dividend_amount,
                    dyc.last_ex_date
                FROM dividend_yield_cache dyc
                JOIN tickers t ON dyc.ticker_id = t.ticker_id
                WHERE t.active = TRUE
                    AND dyc.dividend_yield_pct >= %s
                    AND dyc.consecutive_years_paid >= %s
            """

            params = [min_yield, min_consecutive_years]

            if max_payout_ratio is not None:
                query += " AND (dyc.payout_ratio_pct IS NULL OR dyc.payout_ratio_pct <= %s)"
                params.append(max_payout_ratio)

            query += " ORDER BY dyc.dividend_yield_pct DESC"

            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, tuple(params))
                    rows = cur.fetchall()

            results = []
            for row in rows:
                results.append({
                    'symbol': row[0],
                    'company_name': row[1],
                    'sector': row[2],
                    'dividend_yield_pct': float(row[3]),
                    'annual_dividend': float(row[4]),
                    'current_price': float(row[5]),
                    'frequency': row[6],
                    'growth_1yr_pct': float(row[7]) if row[7] else None,
                    'growth_3yr_pct': float(row[8]) if row[8] else None,
                    'growth_5yr_pct': float(row[9]) if row[9] else None,
                    'consecutive_years': row[10],
                    'payout_ratio_pct': float(row[11]) if row[11] else None,
                    'last_dividend': float(row[12]) if row[12] else None,
                    'last_ex_date': row[13]
                })

            return results

        except Exception as e:
            logger.error(f"Error getting high yield stocks: {e}")
            return []

    def get_dividend_aristocrats(self) -> List[Dict[str, Any]]:
        """
        Get dividend aristocrats (25+ years of consecutive increases).

        Returns:
            List of dividend aristocrat stocks
        """
        return self.get_high_yield_stocks(
            min_yield=0.0,  # Any yield
            min_consecutive_years=25,
            max_payout_ratio=None
        )

    def analyze_dividend_safety(
        self,
        symbol: str
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze dividend safety and sustainability.

        Args:
            symbol: Stock symbol

        Returns:
            Dict with safety analysis or None
        """
        try:
            # Get dividend metrics from cache
            ticker_id = get_ticker_id(self.db, symbol)
            if ticker_id is None:
                return None

            query = """
                SELECT
                    dividend_yield_pct,
                    annual_dividend,
                    payout_frequency,
                    dividend_growth_1yr_pct,
                    dividend_growth_3yr_pct,
                    dividend_growth_5yr_pct,
                    consecutive_years_paid,
                    payout_ratio_pct
                FROM dividend_yield_cache
                WHERE ticker_id = %s
            """

            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (ticker_id,))
                    metrics = cur.fetchone()

            if not metrics:
                logger.warning(f"No dividend metrics found for {symbol}")
                return None

            # Safety scoring
            safety_score = 0
            max_score = 100
            factors = []

            # Factor 1: Consecutive years (40 points max)
            consecutive_years = metrics[6] if metrics[6] else 0
            if consecutive_years >= 25:
                years_score = 40
                factors.append("✓ Dividend Aristocrat (25+ years)")
            elif consecutive_years >= 10:
                years_score = 30
                factors.append("✓ Long dividend history (10+ years)")
            elif consecutive_years >= 5:
                years_score = 20
                factors.append("○ Moderate dividend history (5+ years)")
            else:
                years_score = 10
                factors.append("⚠ Short dividend history (<5 years)")

            safety_score += years_score

            # Factor 2: Payout ratio (30 points max)
            payout_ratio = metrics[7] if metrics[7] else None
            if payout_ratio is not None:
                if payout_ratio <= 50:
                    payout_score = 30
                    factors.append("✓ Conservative payout ratio (<50%)")
                elif payout_ratio <= 70:
                    payout_score = 20
                    factors.append("○ Moderate payout ratio (50-70%)")
                elif payout_ratio <= 90:
                    payout_score = 10
                    factors.append("⚠ High payout ratio (70-90%)")
                else:
                    payout_score = 0
                    factors.append("✗ Unsustainable payout ratio (>90%)")
            else:
                payout_score = 15  # Neutral if unknown
                factors.append("? Payout ratio unavailable")

            safety_score += payout_score

            # Factor 3: Dividend growth (30 points max)
            growth_3yr = metrics[4] if metrics[4] else None
            if growth_3yr is not None:
                if growth_3yr >= 10:
                    growth_score = 30
                    factors.append(f"✓ Strong growth ({growth_3yr:.1f}% 3yr avg)")
                elif growth_3yr >= 5:
                    growth_score = 20
                    factors.append(f"○ Moderate growth ({growth_3yr:.1f}% 3yr avg)")
                elif growth_3yr >= 0:
                    growth_score = 10
                    factors.append(f"○ Slow growth ({growth_3yr:.1f}% 3yr avg)")
                else:
                    growth_score = 0
                    factors.append(f"✗ Declining dividends ({growth_3yr:.1f}% 3yr avg)")
            else:
                growth_score = 15  # Neutral if unknown
                factors.append("? Growth data unavailable")

            safety_score += growth_score

            # Determine safety rating
            if safety_score >= 80:
                safety_rating = "VERY_SAFE"
                recommendation = "Excellent dividend safety profile"
            elif safety_score >= 60:
                safety_rating = "SAFE"
                recommendation = "Good dividend safety"
            elif safety_score >= 40:
                safety_rating = "MODERATE"
                recommendation = "Moderate dividend safety - monitor closely"
            else:
                safety_rating = "AT_RISK"
                recommendation = "Dividend may be at risk - caution advised"

            return {
                'symbol': symbol,
                'safety_score': safety_score,
                'safety_rating': safety_rating,
                'recommendation': recommendation,
                'factors': factors,
                'dividend_yield_pct': float(metrics[0]) if metrics[0] else None,
                'annual_dividend': float(metrics[1]) if metrics[1] else None,
                'consecutive_years': consecutive_years,
                'payout_ratio_pct': float(metrics[7]) if metrics[7] else None,
                'growth_3yr_pct': float(metrics[4]) if metrics[4] else None
            }

        except Exception as e:
            logger.error(f"Error analyzing dividend safety for {symbol}: {e}")
            return None

    def suggest_dividend_reinvestment(
        self,
        available_cash: float,
        min_yield: float = 2.0,
        prefer_growth: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Suggest stocks for dividend reinvestment.

        Args:
            available_cash: Amount of cash available to invest
            min_yield: Minimum dividend yield
            prefer_growth: Prefer dividend growth over high yield

        Returns:
            List of recommended stocks for reinvestment
        """
        try:
            # Get high-quality dividend stocks
            candidates = self.get_high_yield_stocks(
                min_yield=min_yield,
                min_consecutive_years=3,
                max_payout_ratio=80.0
            )

            if not candidates:
                return []

            # Score each candidate
            scored = []
            for stock in candidates:
                score = 0

                # Yield component (max 40 points)
                if not prefer_growth:
                    yield_score = min(stock['dividend_yield_pct'] * 4, 40)
                else:
                    yield_score = min(stock['dividend_yield_pct'] * 2, 20)
                score += yield_score

                # Growth component (max 40 points)
                growth_3yr = stock.get('growth_3yr_pct') or 0
                if prefer_growth:
                    growth_score = min(max(growth_3yr, 0) * 4, 40)
                else:
                    growth_score = min(max(growth_3yr, 0) * 2, 20)
                score += growth_score

                # Safety component (max 20 points)
                consecutive = stock['consecutive_years']
                safety_score = min(consecutive * 2, 20)
                score += safety_score

                # Calculate shares affordable
                price = stock['current_price']
                affordable_shares = int(available_cash / price) if price > 0 else 0

                scored.append({
                    **stock,
                    'reinvestment_score': score,
                    'affordable_shares': affordable_shares,
                    'investment_amount': affordable_shares * price
                })

            # Sort by score
            scored.sort(key=lambda x: x['reinvestment_score'], reverse=True)

            return scored[:10]  # Top 10 recommendations

        except Exception as e:
            logger.error(f"Error suggesting reinvestment: {e}")
            return []

    def format_high_yield_report(
        self,
        min_yield: float = 3.0,
        limit: int = 20
    ) -> str:
        """
        Format high-yield dividend stocks report.

        Args:
            min_yield: Minimum yield filter
            limit: Maximum number of stocks to show

        Returns:
            Formatted report string
        """
        stocks = self.get_high_yield_stocks(min_yield=min_yield)[:limit]

        if not stocks:
            return f"No stocks found with yield >= {min_yield}%"

        output = []
        output.append("=" * 80)
        output.append(f"HIGH-YIELD DIVIDEND STOCKS (Yield >= {min_yield}%)")
        output.append("=" * 80)
        output.append("")

        output.append(
            f"{'Rank':<6} {'Symbol':<8} {'Yield':<8} {'Price':<10} "
            f"{'Annual $':<10} {'Years':<7} {'Growth':<8}"
        )
        output.append("-" * 80)

        for i, stock in enumerate(stocks, 1):
            growth = stock.get('growth_3yr_pct')
            growth_str = f"+{growth:.1f}%" if growth and growth > 0 else (
                f"{growth:.1f}%" if growth else "N/A"
            )

            output.append(
                f"#{i:<5} {stock['symbol']:<8} "
                f"{stock['dividend_yield_pct']:<7.2f}% "
                f"${stock['current_price']:<9.2f} "
                f"${stock['annual_dividend']:<9.2f} "
                f"{stock['consecutive_years']:<7} "
                f"{growth_str:<8}"
            )

        output.append("")
        output.append("=" * 80)
        output.append(f"Total: {len(stocks)} high-yield dividend stocks")
        output.append("=" * 80)

        return "\n".join(output)
