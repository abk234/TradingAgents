# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Dividend income tracker.

Tracks actual dividend income received and calculates portfolio dividend metrics.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
from decimal import Decimal

from tradingagents.database import DatabaseConnection
from .dividend_fetcher import get_ticker_id

logger = logging.getLogger(__name__)


class DividendTracker:
    """Tracks dividend income for portfolio."""

    def __init__(self, db_conn: Optional[DatabaseConnection] = None):
        """
        Initialize dividend tracker.

        Args:
            db_conn: Database connection (creates new if not provided)
        """
        self.db = db_conn or DatabaseConnection()

    def record_dividend_income(
        self,
        symbol: str,
        payment_date: datetime,
        shares_owned: float,
        amount_per_share: float,
        ex_date: Optional[datetime] = None,
        tax_withheld: float = 0.0,
        notes: Optional[str] = None
    ) -> bool:
        """
        Record dividend income received.

        Args:
            symbol: Stock symbol
            payment_date: Date dividend was paid
            shares_owned: Number of shares owned
            amount_per_share: Dividend amount per share
            ex_date: Ex-dividend date
            tax_withheld: Tax withheld (if any)
            notes: Optional notes

        Returns:
            True if successful
        """
        try:
            ticker_id = get_ticker_id(self.db, symbol)
            if ticker_id is None:
                logger.error(f"Ticker {symbol} not found")
                return False

            # Get holding_id if exists
            holding_id = self._get_holding_id(ticker_id)

            total_amount = shares_owned * amount_per_share

            query = """
                INSERT INTO dividend_income (
                    ticker_id,
                    holding_id,
                    payment_date,
                    ex_date,
                    shares_owned,
                    amount_per_share,
                    total_amount,
                    tax_withheld,
                    notes
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING income_id
            """

            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (
                        ticker_id,
                        holding_id,
                        payment_date,
                        ex_date,
                        shares_owned,
                        amount_per_share,
                        total_amount,
                        tax_withheld,
                        notes
                    ))
                    income_id = cur.fetchone()[0]
                    conn.commit()

            logger.info(
                f"Recorded dividend income: {symbol} - "
                f"${total_amount:.2f} ({shares_owned} shares @ ${amount_per_share:.4f})"
            )
            return True

        except Exception as e:
            logger.error(f"Error recording dividend income for {symbol}: {e}")
            return False

    def _get_holding_id(self, ticker_id: int) -> Optional[int]:
        """Get holding_id for a ticker if it exists in portfolio."""
        try:
            query = """
                SELECT holding_id
                FROM portfolio_holdings
                WHERE ticker_id = %s
                    AND is_open = TRUE
                LIMIT 1
            """

            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (ticker_id,))
                    result = cur.fetchone()
                    return result[0] if result else None

        except Exception:
            return None

    def get_dividend_income_summary(
        self,
        year: Optional[int] = None,
        symbol: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get dividend income summary.

        Args:
            year: Year to filter by (defaults to current year)
            symbol: Optional symbol filter

        Returns:
            Dict with income summary
        """
        try:
            if year is None:
                year = datetime.now().year

            query = """
                SELECT
                    COUNT(*) as payment_count,
                    SUM(total_amount) as total_gross,
                    SUM(tax_withheld) as total_tax,
                    SUM(net_amount) as total_net,
                    COUNT(DISTINCT ticker_id) as unique_tickers,
                    MIN(payment_date) as first_payment,
                    MAX(payment_date) as last_payment
                FROM dividend_income
                WHERE EXTRACT(YEAR FROM payment_date) = %s
            """

            params = [year]

            if symbol:
                ticker_id = get_ticker_id(self.db, symbol)
                if ticker_id:
                    query += " AND ticker_id = %s"
                    params.append(ticker_id)

            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, tuple(params))
                    row = cur.fetchone()

            if row[0] == 0:
                return {
                    'year': year,
                    'payment_count': 0,
                    'total_gross_income': 0.0,
                    'total_tax_withheld': 0.0,
                    'total_net_income': 0.0,
                    'unique_tickers': 0
                }

            return {
                'year': year,
                'payment_count': row[0],
                'total_gross_income': float(row[1]) if row[1] else 0.0,
                'total_tax_withheld': float(row[2]) if row[2] else 0.0,
                'total_net_income': float(row[3]) if row[3] else 0.0,
                'unique_tickers': row[4],
                'first_payment': row[5],
                'last_payment': row[6]
            }

        except Exception as e:
            logger.error(f"Error getting income summary: {e}")
            return {}

    def get_dividend_income_by_ticker(
        self,
        year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get dividend income breakdown by ticker.

        Args:
            year: Year to filter by (defaults to current year)

        Returns:
            List of ticker dividend summaries
        """
        try:
            if year is None:
                year = datetime.now().year

            query = """
                SELECT
                    t.symbol,
                    t.company_name,
                    COUNT(*) as payment_count,
                    SUM(di.total_amount) as total_income,
                    AVG(di.amount_per_share) as avg_amount_per_share,
                    SUM(di.tax_withheld) as total_tax,
                    SUM(di.net_amount) as total_net
                FROM dividend_income di
                JOIN tickers t ON di.ticker_id = t.ticker_id
                WHERE EXTRACT(YEAR FROM di.payment_date) = %s
                GROUP BY t.symbol, t.company_name
                ORDER BY total_income DESC
            """

            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (year,))
                    rows = cur.fetchall()

            results = []
            for row in rows:
                results.append({
                    'symbol': row[0],
                    'company_name': row[1],
                    'payment_count': row[2],
                    'total_income': float(row[3]),
                    'avg_amount_per_share': float(row[4]),
                    'total_tax': float(row[5]) if row[5] else 0.0,
                    'total_net': float(row[6]) if row[6] else 0.0
                })

            return results

        except Exception as e:
            logger.error(f"Error getting income by ticker: {e}")
            return []

    def get_monthly_income(
        self,
        year: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Get monthly dividend income for a year.

        Args:
            year: Year (defaults to current year)

        Returns:
            Dict mapping month to total income
        """
        try:
            if year is None:
                year = datetime.now().year

            query = """
                SELECT
                    EXTRACT(MONTH FROM payment_date) as month,
                    SUM(total_amount) as total
                FROM dividend_income
                WHERE EXTRACT(YEAR FROM payment_date) = %s
                GROUP BY EXTRACT(MONTH FROM payment_date)
                ORDER BY month
            """

            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (year,))
                    rows = cur.fetchall()

            # Initialize all months to 0
            monthly = {i: 0.0 for i in range(1, 13)}

            for row in rows:
                month = int(row[0])
                total = float(row[1])
                monthly[month] = total

            return monthly

        except Exception as e:
            logger.error(f"Error getting monthly income: {e}")
            return {}

    def calculate_yield_on_cost(
        self,
        symbol: str
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate yield on cost for a holding.

        Args:
            symbol: Stock symbol

        Returns:
            Dict with yield on cost metrics or None
        """
        try:
            ticker_id = get_ticker_id(self.db, symbol)
            if ticker_id is None:
                return None

            # Get holding info
            query = """
                SELECT
                    shares,
                    avg_cost_basis
                FROM portfolio_holdings
                WHERE ticker_id = %s
                    AND is_open = TRUE
                LIMIT 1
            """

            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (ticker_id,))
                    holding = cur.fetchone()

            if not holding:
                logger.warning(f"No open holding found for {symbol}")
                return None

            shares = float(holding[0])
            cost_basis = float(holding[1])
            total_invested = shares * cost_basis

            # Get dividend income for last 12 months
            query = """
                SELECT SUM(total_amount)
                FROM dividend_income
                WHERE ticker_id = %s
                    AND payment_date >= CURRENT_DATE - INTERVAL '12 months'
            """

            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (ticker_id,))
                    result = cur.fetchone()

            annual_income = float(result[0]) if result[0] else 0.0

            if total_invested <= 0:
                return None

            yield_on_cost = (annual_income / total_invested) * 100

            return {
                'symbol': symbol,
                'shares': shares,
                'cost_basis': cost_basis,
                'total_invested': total_invested,
                'annual_dividend_income': annual_income,
                'yield_on_cost_pct': yield_on_cost
            }

        except Exception as e:
            logger.error(f"Error calculating yield on cost for {symbol}: {e}")
            return None

    def format_income_report(
        self,
        year: Optional[int] = None
    ) -> str:
        """
        Format dividend income report.

        Args:
            year: Year to report on

        Returns:
            Formatted report string
        """
        if year is None:
            year = datetime.now().year

        summary = self.get_dividend_income_summary(year)
        by_ticker = self.get_dividend_income_by_ticker(year)
        monthly = self.get_monthly_income(year)

        output = []
        output.append("=" * 80)
        output.append(f"DIVIDEND INCOME REPORT - {year}")
        output.append("=" * 80)
        output.append("")

        # Overall summary
        output.append("📊 OVERALL SUMMARY")
        output.append("-" * 80)
        output.append(f"Total Payments Received: {summary.get('payment_count', 0)}")
        output.append(f"Unique Tickers:          {summary.get('unique_tickers', 0)}")
        output.append(f"Gross Income:            ${summary.get('total_gross_income', 0):.2f}")
        output.append(f"Tax Withheld:            ${summary.get('total_tax_withheld', 0):.2f}")
        output.append(f"Net Income:              ${summary.get('total_net_income', 0):.2f}")
        output.append("")

        # By ticker
        if by_ticker:
            output.append("💵 INCOME BY TICKER")
            output.append("-" * 80)
            output.append(f"{'Symbol':<8} {'Payments':<10} {'Total Income':<15} {'Avg/Share':<12}")
            output.append("-" * 80)

            for ticker in by_ticker:
                output.append(
                    f"{ticker['symbol']:<8} "
                    f"{ticker['payment_count']:<10} "
                    f"${ticker['total_income']:<14.2f} "
                    f"${ticker['avg_amount_per_share']:<11.4f}"
                )

            output.append("")

        # Monthly breakdown
        if monthly:
            output.append("📅 MONTHLY BREAKDOWN")
            output.append("-" * 80)

            month_names = [
                'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
            ]

            for month_num, month_name in enumerate(month_names, 1):
                amount = monthly.get(month_num, 0.0)
                bar = "█" * int(amount / 100) if amount > 0 else ""
                output.append(f"{month_name}: ${amount:>8.2f} {bar}")

            output.append("")

        output.append("=" * 80)

        return "\n".join(output)
