#!/usr/bin/env python3
# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Update Dividend Data

Fetches dividend data from yfinance and populates dividend tracking tables.

This script:
1. Fetches dividend history for all active tickers
2. Calculates dividend metrics (yield, growth, payout ratio, etc.)
3. Updates dividend_history table
4. Updates dividend_yield_cache table
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List, Optional, Tuple
import yfinance as yf
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tradingagents.database import get_db_connection

logger = logging.getLogger(__name__)


class DividendDataFetcher:
    """Fetch and update dividend data for all tickers."""

    def __init__(self, db=None):
        self.db = db or get_db_connection()

    def get_active_tickers(self) -> List[Dict[str, Any]]:
        """Get all active tickers from database."""
        query = """
            SELECT ticker_id, symbol, company_name
            FROM tickers
            WHERE active = TRUE
            ORDER BY symbol
        """
        tickers = self.db.execute_dict_query(query)
        return tickers if tickers else []

    def fetch_dividend_history(self, symbol: str, years: int = 10) -> Optional[pd.DataFrame]:
        """
        Fetch dividend history from yfinance.

        Args:
            symbol: Ticker symbol
            years: Number of years of history to fetch

        Returns:
            DataFrame with dividend history or None
        """
        try:
            ticker = yf.Ticker(symbol)

            # Get dividends
            dividends = ticker.dividends

            if dividends is None or len(dividends) == 0:
                logger.debug(f"{symbol}: No dividends returned from yfinance")
                return None

            # Filter to last N years - make cutoff_date timezone aware if needed
            cutoff_date = pd.Timestamp.now() - pd.DateOffset(years=years)

            # Make cutoff_date timezone-aware if dividends index is timezone-aware
            if dividends.index.tz is not None:
                cutoff_date = cutoff_date.tz_localize(dividends.index.tz)

            dividends = dividends[dividends.index >= cutoff_date]

            if len(dividends) == 0:
                logger.debug(f"{symbol}: No dividends in last {years} years")
                return None

            # Convert to DataFrame
            df = pd.DataFrame({
                'date': dividends.index,
                'amount': dividends.values
            })

            # Convert to date (remove timezone and time)
            df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None).dt.date

            logger.debug(f"{symbol}: Found {len(df)} dividend payments")
            return df

        except Exception as e:
            logger.warning(f"Error fetching dividends for {symbol}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None

    def calculate_consecutive_years(self, dividends_df: pd.DataFrame) -> int:
        """
        Calculate number of consecutive years paying dividends.

        Args:
            dividends_df: DataFrame with dividend history

        Returns:
            Number of consecutive years
        """
        if dividends_df is None or len(dividends_df) == 0:
            return 0

        # Group by year and count payments
        dividends_df['year'] = pd.to_datetime(dividends_df['date']).dt.year
        years_with_payments = dividends_df.groupby('year')['amount'].sum()
        years_with_payments = years_with_payments[years_with_payments > 0]

        if len(years_with_payments) == 0:
            return 0

        # Check consecutive years from most recent
        current_year = datetime.now().year
        consecutive = 0

        for year in range(current_year, current_year - 50, -1):
            if year in years_with_payments.index:
                consecutive += 1
            else:
                break

        return consecutive

    def calculate_dividend_growth(
        self,
        dividends_df: pd.DataFrame,
        years: int
    ) -> Optional[float]:
        """
        Calculate dividend growth rate over N years.

        Args:
            dividends_df: DataFrame with dividend history
            years: Number of years to calculate growth over

        Returns:
            Annualized growth rate as decimal or None
        """
        if dividends_df is None or len(dividends_df) == 0:
            return None

        try:
            dividends_df['year'] = pd.to_datetime(dividends_df['date']).dt.year
            annual_dividends = dividends_df.groupby('year')['amount'].sum()

            if len(annual_dividends) < 2:
                return None

            # Get dividends from N years ago and most recent year
            sorted_years = sorted(annual_dividends.index, reverse=True)

            if len(sorted_years) < years + 1:
                return None

            recent_year = sorted_years[0]
            old_year = sorted_years[min(years, len(sorted_years) - 1)]

            recent_div = annual_dividends[recent_year]
            old_div = annual_dividends[old_year]

            if old_div <= 0:
                return None

            # Calculate CAGR
            years_diff = recent_year - old_year
            if years_diff <= 0:
                return None

            growth_rate = (recent_div / old_div) ** (1 / years_diff) - 1

            return float(growth_rate)

        except Exception as e:
            logger.debug(f"Error calculating growth: {e}")
            return None

    def determine_payout_frequency(self, dividends_df: pd.DataFrame) -> str:
        """
        Determine dividend payout frequency.

        Args:
            dividends_df: DataFrame with dividend history

        Returns:
            Frequency string: MONTHLY, QUARTERLY, SEMI_ANNUAL, ANNUAL, IRREGULAR
        """
        if dividends_df is None or len(dividends_df) == 0:
            return "UNKNOWN"

        # Count payments in the last year
        one_year_ago = date.today() - timedelta(days=365)
        recent_divs = dividends_df[pd.to_datetime(dividends_df['date']) >= pd.Timestamp(one_year_ago)]

        payment_count = len(recent_divs)

        if payment_count >= 11:
            return "MONTHLY"
        elif payment_count >= 4:
            return "QUARTERLY"
        elif payment_count >= 2:
            return "SEMI_ANNUAL"
        elif payment_count >= 1:
            return "ANNUAL"
        else:
            return "IRREGULAR"

    def fetch_current_price_and_info(self, symbol: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """
        Fetch current price and fundamental info.

        Args:
            symbol: Ticker symbol

        Returns:
            Tuple of (current_price, trailing_eps, payout_ratio)
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            trailing_eps = info.get('trailingEps')
            payout_ratio = info.get('payoutRatio')

            return current_price, trailing_eps, payout_ratio

        except Exception as e:
            logger.debug(f"Error fetching info for {symbol}: {e}")
            return None, None, None

    def update_dividend_history(self, ticker_id: int, symbol: str, dividends_df: pd.DataFrame) -> int:
        """
        Update dividend_history table with new dividends.

        Args:
            ticker_id: Ticker ID
            symbol: Ticker symbol
            dividends_df: DataFrame with dividend history

        Returns:
            Number of records inserted/updated
        """
        if dividends_df is None or len(dividends_df) == 0:
            return 0

        inserted = 0

        for _, row in dividends_df.iterrows():
            try:
                query = """
                    INSERT INTO dividend_history (
                        ticker_id,
                        ex_date,
                        amount_per_share,
                        dividend_type,
                        currency
                    ) VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (ticker_id, ex_date)
                    DO UPDATE SET
                        amount_per_share = EXCLUDED.amount_per_share,
                        updated_at = CURRENT_TIMESTAMP
                """

                self.db.execute_query(
                    query,
                    (ticker_id, row['date'], Decimal(str(row['amount'])), 'CASH', 'USD'),
                    fetch=False
                )
                inserted += 1

            except Exception as e:
                logger.debug(f"Error inserting dividend for {symbol} on {row['date']}: {e}")

        return inserted

    def update_dividend_cache(
        self,
        ticker_id: int,
        symbol: str,
        dividends_df: pd.DataFrame,
        current_price: float,
        payout_ratio: Optional[float]
    ) -> bool:
        """
        Update dividend_yield_cache table.

        Args:
            ticker_id: Ticker ID
            symbol: Ticker symbol
            dividends_df: DataFrame with dividend history
            current_price: Current stock price
            payout_ratio: Payout ratio (if available)

        Returns:
            True if successful
        """
        try:
            # Calculate annual dividend (last 12 months)
            one_year_ago = date.today() - timedelta(days=365)
            recent_divs = dividends_df[pd.to_datetime(dividends_df['date']) >= pd.Timestamp(one_year_ago)]
            annual_dividend = float(recent_divs['amount'].sum()) if len(recent_divs) > 0 else 0

            if annual_dividend <= 0 or current_price is None or current_price <= 0:
                return False

            # Calculate dividend yield
            dividend_yield = (annual_dividend / current_price) * 100

            # Get last dividend info
            last_dividend = dividends_df.iloc[-1]
            last_amount = float(last_dividend['amount'])
            last_ex_date = last_dividend['date']

            # Calculate consecutive years
            consecutive_years = self.calculate_consecutive_years(dividends_df)

            # Calculate growth rates
            growth_1yr = self.calculate_dividend_growth(dividends_df, 1)
            growth_3yr = self.calculate_dividend_growth(dividends_df, 3)
            growth_5yr = self.calculate_dividend_growth(dividends_df, 5)

            # Determine frequency
            frequency = self.determine_payout_frequency(dividends_df)

            # Convert payout ratio to percentage
            payout_ratio_pct = payout_ratio * 100 if payout_ratio is not None else None

            # Calculate cache validity (update weekly)
            valid_until = datetime.now() + timedelta(days=7)

            # Insert/update cache
            query = """
                INSERT INTO dividend_yield_cache (
                    ticker_id,
                    current_price,
                    annual_dividend,
                    dividend_yield_pct,
                    payout_frequency,
                    last_dividend_amount,
                    last_ex_date,
                    dividend_growth_1yr_pct,
                    dividend_growth_3yr_pct,
                    dividend_growth_5yr_pct,
                    consecutive_years_paid,
                    payout_ratio_pct,
                    calculated_at,
                    valid_until
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s
                )
                ON CONFLICT (ticker_id)
                DO UPDATE SET
                    current_price = EXCLUDED.current_price,
                    annual_dividend = EXCLUDED.annual_dividend,
                    dividend_yield_pct = EXCLUDED.dividend_yield_pct,
                    payout_frequency = EXCLUDED.payout_frequency,
                    last_dividend_amount = EXCLUDED.last_dividend_amount,
                    last_ex_date = EXCLUDED.last_ex_date,
                    dividend_growth_1yr_pct = EXCLUDED.dividend_growth_1yr_pct,
                    dividend_growth_3yr_pct = EXCLUDED.dividend_growth_3yr_pct,
                    dividend_growth_5yr_pct = EXCLUDED.dividend_growth_5yr_pct,
                    consecutive_years_paid = EXCLUDED.consecutive_years_paid,
                    payout_ratio_pct = EXCLUDED.payout_ratio_pct,
                    calculated_at = CURRENT_TIMESTAMP,
                    valid_until = EXCLUDED.valid_until
            """

            self.db.execute_query(
                query,
                (
                    ticker_id,
                    Decimal(str(current_price)),
                    Decimal(str(annual_dividend)),
                    Decimal(str(dividend_yield)),
                    frequency,
                    Decimal(str(last_amount)),
                    last_ex_date,
                    Decimal(str(growth_1yr * 100)) if growth_1yr is not None else None,
                    Decimal(str(growth_3yr * 100)) if growth_3yr is not None else None,
                    Decimal(str(growth_5yr * 100)) if growth_5yr is not None else None,
                    consecutive_years,
                    Decimal(str(payout_ratio_pct)) if payout_ratio_pct is not None else None,
                    valid_until
                ),
                fetch=False
            )

            return True

        except Exception as e:
            logger.error(f"Error updating cache for {symbol}: {e}")
            return False

    def process_ticker(self, ticker_id: int, symbol: str) -> bool:
        """
        Process a single ticker: fetch data and update database.

        Args:
            ticker_id: Ticker ID
            symbol: Ticker symbol

        Returns:
            True if successful
        """
        try:
            # Fetch dividend history
            dividends_df = self.fetch_dividend_history(symbol, years=10)

            if dividends_df is None or len(dividends_df) == 0:
                logger.info(f"  ⊙ {symbol:6s} - No dividend data")
                return False

            # Fetch current price and info
            current_price, trailing_eps, payout_ratio = self.fetch_current_price_and_info(symbol)

            if current_price is None or current_price <= 0:
                logger.info(f"  ⊙ {symbol:6s} - Could not get current price")
                return False

            # Update dividend history
            history_records = self.update_dividend_history(ticker_id, symbol, dividends_df)

            # Update cache
            cache_success = self.update_dividend_cache(
                ticker_id,
                symbol,
                dividends_df,
                current_price,
                payout_ratio
            )

            if cache_success:
                # Get yield for logging
                annual_dividend = dividends_df[
                    pd.to_datetime(dividends_df['date']) >= pd.Timestamp(date.today() - timedelta(days=365))
                ]['amount'].sum()
                dividend_yield = (annual_dividend / current_price) * 100

                logger.info(
                    f"  ✓ {symbol:6s} - Yield: {dividend_yield:5.2f}% "
                    f"| ${annual_dividend:.2f}/yr | {history_records} records"
                )
                return True
            else:
                logger.warning(f"  ✗ {symbol:6s} - Failed to update cache")
                return False

        except Exception as e:
            logger.error(f"  ✗ {symbol:6s} - Error: {e}")
            return False

    def update_all(self, limit: Optional[int] = None) -> Dict[str, int]:
        """
        Update dividend data for all active tickers.

        Args:
            limit: Optional limit on number of tickers to process

        Returns:
            Statistics dictionary
        """
        logger.info("=" * 70)
        logger.info("Dividend Data Update - Starting")
        logger.info("=" * 70)

        tickers = self.get_active_tickers()

        if limit:
            tickers = tickers[:limit]

        logger.info(f"Processing {len(tickers)} tickers...\n")

        stats = {
            'total': len(tickers),
            'successful': 0,
            'no_dividends': 0,
            'failed': 0
        }

        for ticker in tickers:
            success = self.process_ticker(ticker['ticker_id'], ticker['symbol'])

            if success:
                stats['successful'] += 1
            else:
                # Check if it's because no dividends vs actual error
                # This is a simple heuristic
                stats['no_dividends'] += 1

        logger.info("")
        logger.info("=" * 70)
        logger.info("Update Complete")
        logger.info("=" * 70)
        logger.info(f"Total tickers: {stats['total']}")
        logger.info(f"Successful: {stats['successful']}")
        logger.info(f"No dividends: {stats['no_dividends']}")
        logger.info(f"Failed: {stats['failed']}")

        if stats['successful'] > 0:
            logger.info(f"\n✓ Dividend data updated for {stats['successful']} tickers")
            logger.info(f"✓ Ready to run: ./quick_run.sh dividend-income")

        return stats


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Update dividend data from yfinance"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of tickers to process (for testing)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Minimal output"
    )

    args = parser.parse_args()

    # Configure logging
    if args.quiet:
        logging.basicConfig(level=logging.WARNING, format='%(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s')

    try:
        db = get_db_connection()
        fetcher = DividendDataFetcher(db)

        stats = fetcher.update_all(limit=args.limit)

        return 0 if stats['successful'] > 0 else 1

    except KeyboardInterrupt:
        logger.info("\n\nUpdate interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
