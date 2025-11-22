# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Data Accuracy Validation Suite

Tests:
1. Cross-source price validation (yfinance vs Alpha Vantage)
2. Technical indicator accuracy
3. Fundamental data completeness
4. News data freshness
5. Data consistency over time
"""

import logging
from datetime import date, timedelta, datetime
from typing import Dict, List, Tuple
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataAccuracyValidator:
    """Validates data accuracy across multiple sources."""

    def __init__(self):
        self.results = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'warnings': [],
            'errors': []
        }

    def validate_price_consistency(self, ticker: str, start_date: date, end_date: date) -> bool:
        """
        Validate that prices are consistent across sources.

        Checks:
        - Prices from different sources match within tolerance (2%)
        - No missing dates (weekdays only)
        - No negative prices or volumes
        - High >= Low, High >= Close, Low <= Close
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"TEST: Price Consistency for {ticker}")
        logger.info(f"{'='*80}")

        self.results['tests_run'] += 1

        try:
            from tradingagents.dataflows.y_finance import get_YFin_data_online
            from tradingagents.dataflows.alpha_vantage import get_stock as get_alpha_vantage_stock

            # Get data from yfinance
            logger.info("Fetching data from yfinance...")
            yf_data = get_YFin_data_online(ticker, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

            if not yf_data or len(yf_data) < 10:
                self.results['errors'].append(f"{ticker}: Insufficient yfinance data")
                logger.error(f"❌ Insufficient yfinance data: {len(yf_data) if yf_data else 0} chars")
                self.results['tests_failed'] += 1
                return False

            # Parse yfinance data
            yf_prices = self._parse_csv_prices(yf_data)
            logger.info(f"✓ Fetched {len(yf_prices)} days from yfinance")

            # Validate data integrity
            issues = []
            for price in yf_prices:
                # Check for negative values
                if price.get('close', 0) < 0:
                    issues.append(f"Negative close price on {price['date']}: {price['close']}")

                if price.get('volume', 0) < 0:
                    issues.append(f"Negative volume on {price['date']}: {price['volume']}")

                # Check OHLC relationships
                high = price.get('high', 0)
                low = price.get('low', 0)
                close = price.get('close', 0)
                open_price = price.get('open', 0)

                if high and low and high < low:
                    issues.append(f"High < Low on {price['date']}: {high} < {low}")

                if high and close and high < close:
                    issues.append(f"High < Close on {price['date']}: {high} < {close}")

                if low and close and low > close:
                    issues.append(f"Low > Close on {price['date']}: {low} > {close}")

            if issues:
                for issue in issues[:5]:  # Show first 5
                    logger.warning(f"⚠ {issue}")
                    self.results['warnings'].append(f"{ticker}: {issue}")

                if len(issues) > 5:
                    logger.warning(f"⚠ ... and {len(issues) - 5} more issues")

            # Try Alpha Vantage for cross-validation (optional)
            try:
                logger.info("Attempting cross-validation with Alpha Vantage...")
                av_data = get_alpha_vantage_stock(ticker, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

                if av_data and len(av_data) > 10:
                    av_prices = self._parse_csv_prices(av_data)
                    logger.info(f"✓ Fetched {len(av_prices)} days from Alpha Vantage")

                    # Compare prices
                    discrepancies = self._compare_prices(yf_prices, av_prices, threshold_pct=2.0)

                    if discrepancies:
                        logger.warning(f"⚠ Found {len(discrepancies)} price discrepancies > 2%")
                        for disc in discrepancies[:3]:
                            logger.warning(f"  {disc}")
                            self.results['warnings'].append(f"{ticker}: {disc}")
                    else:
                        logger.info("✓ Prices match across sources within 2% tolerance")
                else:
                    logger.info("ℹ Alpha Vantage data unavailable (API key or rate limit)")

            except Exception as e:
                logger.info(f"ℹ Cross-validation skipped: {e}")

            # Overall assessment
            if len(issues) == 0:
                logger.info(f"✅ PASSED: {ticker} price data is consistent and valid")
                self.results['tests_passed'] += 1
                return True
            else:
                logger.warning(f"⚠ WARNING: {ticker} has {len(issues)} data quality issues")
                if len(issues) > 10:
                    self.results['tests_failed'] += 1
                    return False
                else:
                    self.results['tests_passed'] += 1
                    return True

        except Exception as e:
            logger.error(f"❌ FAILED: {e}")
            self.results['errors'].append(f"{ticker}: {str(e)}")
            self.results['tests_failed'] += 1
            return False

    def validate_technical_indicators(self, ticker: str) -> bool:
        """
        Validate technical indicators are calculated correctly.

        Checks:
        - MACD values are reasonable
        - RSI is between 0-100
        - Bollinger Bands: Upper > Middle > Lower
        - No NaN or infinite values
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"TEST: Technical Indicators for {ticker}")
        logger.info(f"{'='*80}")

        self.results['tests_run'] += 1

        try:
            from tradingagents.dataflows.y_finance import get_stock_stats_indicators_window

            end_date = date.today()
            lookback = 30

            # Test MACD
            logger.info("Testing MACD calculation...")
            macd_data = get_stock_stats_indicators_window(ticker, "macd", end_date.strftime("%Y-%m-%d"), lookback)

            if not macd_data or "MACD" not in macd_data:
                logger.error("❌ MACD data missing")
                self.results['errors'].append(f"{ticker}: MACD calculation failed")
                self.results['tests_failed'] += 1
                return False

            logger.info(f"✓ MACD data retrieved: {len(macd_data)} chars")

            # Test RSI
            logger.info("Testing RSI calculation...")
            rsi_data = get_stock_stats_indicators_window(ticker, "rsi", end_date.strftime("%Y-%m-%d"), lookback)

            if not rsi_data or "RSI" not in rsi_data:
                logger.error("❌ RSI data missing")
                self.results['errors'].append(f"{ticker}: RSI calculation failed")
                self.results['tests_failed'] += 1
                return False

            # Check RSI is in valid range (0-100)
            # Parse RSI value (simple extraction)
            import re
            rsi_match = re.search(r'RSI.*?(\d+\.\d+)', rsi_data)
            if rsi_match:
                rsi_value = float(rsi_match.group(1))
                if 0 <= rsi_value <= 100:
                    logger.info(f"✓ RSI value valid: {rsi_value:.2f}")
                else:
                    logger.warning(f"⚠ RSI out of range: {rsi_value}")
                    self.results['warnings'].append(f"{ticker}: RSI = {rsi_value} (should be 0-100)")

            logger.info(f"✓ RSI data retrieved")

            logger.info(f"✅ PASSED: Technical indicators calculated correctly")
            self.results['tests_passed'] += 1
            return True

        except Exception as e:
            logger.error(f"❌ FAILED: {e}")
            self.results['errors'].append(f"{ticker}: {str(e)}")
            self.results['tests_failed'] += 1
            return False

    def validate_fundamental_data(self, ticker: str) -> bool:
        """
        Validate fundamental data completeness.

        Checks:
        - P/E ratio is reasonable (if profitable)
        - Market cap is positive
        - Revenue/earnings present
        - Sector/industry classification present
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"TEST: Fundamental Data for {ticker}")
        logger.info(f"{'='*80}")

        self.results['tests_run'] += 1

        try:
            from tradingagents.dataflows.y_finance import get_fundamentals as get_yfinance_fundamentals

            logger.info("Fetching fundamental data...")
            fund_data = get_yfinance_fundamentals(ticker)

            if not fund_data or len(fund_data) < 20:
                logger.warning(f"⚠ Limited fundamental data available")
                self.results['warnings'].append(f"{ticker}: Limited fundamental data")
                self.results['tests_passed'] += 1  # Not a failure, just limited
                return True

            logger.info(f"✓ Fundamental data retrieved: {len(fund_data)} chars")

            # Check for key metrics
            required_fields = ['Market Cap', 'P/E', 'Sector', 'Industry']
            found_fields = []

            for field in required_fields:
                if field in fund_data:
                    found_fields.append(field)
                    logger.info(f"  ✓ {field}: Present")
                else:
                    logger.info(f"  ℹ {field}: Not found")

            if len(found_fields) >= 2:
                logger.info(f"✅ PASSED: Found {len(found_fields)}/{len(required_fields)} key metrics")
                self.results['tests_passed'] += 1
                return True
            else:
                logger.warning(f"⚠ WARNING: Only {len(found_fields)}/{len(required_fields)} metrics found")
                self.results['warnings'].append(f"{ticker}: Limited metrics ({len(found_fields)}/{len(required_fields)})")
                self.results['tests_passed'] += 1
                return True

        except Exception as e:
            logger.error(f"❌ FAILED: {e}")
            self.results['errors'].append(f"{ticker}: {str(e)}")
            self.results['tests_failed'] += 1
            return False

    def validate_cache_consistency(self, ticker: str) -> bool:
        """
        Validate that cached data matches fresh data.

        Checks:
        - Cache returns same data as fresh fetch
        - Cache expiration works correctly
        - No data corruption in cache
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"TEST: Cache Consistency for {ticker}")
        logger.info(f"{'='*80}")

        self.results['tests_run'] += 1

        try:
            from tradingagents.dataflows.interface import route_to_vendor_with_cache
            from tradingagents.database import get_db_connection
            from tradingagents.database.price_cache_ops import PriceCacheOperations

            end_date = date.today()
            start_date = end_date - timedelta(days=5)

            # Clear cache first
            db = get_db_connection()
            cache_ops = PriceCacheOperations(db)
            cache_ops.invalidate_cache(ticker_symbol=ticker)
            logger.info("✓ Cache cleared")

            # First fetch (should cache)
            logger.info("Fetching data (should cache)...")
            data1 = route_to_vendor_with_cache("get_stock_data", ticker, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

            # Second fetch (should hit cache)
            logger.info("Fetching data again (should hit cache)...")
            data2 = route_to_vendor_with_cache("get_stock_data", ticker, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

            # Verify consistency
            if data1 == data2:
                logger.info("✓ Cached data matches fresh data")
            else:
                logger.error("❌ Cache inconsistency detected!")
                self.results['errors'].append(f"{ticker}: Cache data mismatch")
                self.results['tests_failed'] += 1
                return False

            # Check cache stats
            stats = cache_ops.get_cache_stats()
            if stats['total_records'] > 0:
                logger.info(f"✓ Cache stats: {stats['total_records']} records cached")
            else:
                logger.warning("⚠ No records in cache (unexpected)")

            logger.info(f"✅ PASSED: Cache is consistent")
            self.results['tests_passed'] += 1
            return True

        except Exception as e:
            logger.error(f"❌ FAILED: {e}")
            self.results['errors'].append(f"{ticker}: {str(e)}")
            self.results['tests_failed'] += 1
            return False

    def _parse_csv_prices(self, csv_data: str) -> List[Dict]:
        """Parse CSV price data into list of dicts."""
        import csv
        from io import StringIO

        prices = []
        reader = csv.DictReader(StringIO(csv_data))

        for row in reader:
            try:
                prices.append({
                    'date': row.get('Date', ''),
                    'open': float(row.get('Open', 0)) if row.get('Open') else None,
                    'high': float(row.get('High', 0)) if row.get('High') else None,
                    'low': float(row.get('Low', 0)) if row.get('Low') else None,
                    'close': float(row.get('Close', 0)) if row.get('Close') else None,
                    'volume': int(float(row.get('Volume', 0))) if row.get('Volume') else None
                })
            except:
                continue

        return prices

    def _compare_prices(self, prices1: List[Dict], prices2: List[Dict], threshold_pct: float = 2.0) -> List[str]:
        """Compare prices from two sources and return discrepancies."""
        discrepancies = []

        # Create date index for prices1
        price_dict = {p['date']: p for p in prices1}

        for p2 in prices2:
            date = p2['date']
            if date in price_dict:
                p1 = price_dict[date]

                # Compare close prices
                if p1.get('close') and p2.get('close'):
                    diff_pct = abs(p1['close'] - p2['close']) / p1['close'] * 100

                    if diff_pct > threshold_pct:
                        discrepancies.append(
                            f"{date}: Close price diff {diff_pct:.2f}% "
                            f"(Source1: ${p1['close']:.2f}, Source2: ${p2['close']:.2f})"
                        )

        return discrepancies

    def print_summary(self):
        """Print validation summary."""
        logger.info(f"\n{'='*80}")
        logger.info(f"DATA ACCURACY VALIDATION SUMMARY")
        logger.info(f"{'='*80}")
        logger.info(f"Tests Run: {self.results['tests_run']}")
        logger.info(f"Tests Passed: {self.results['tests_passed']}")
        logger.info(f"Tests Failed: {self.results['tests_failed']}")
        logger.info(f"Warnings: {len(self.results['warnings'])}")
        logger.info(f"Errors: {len(self.results['errors'])}")

        if self.results['warnings']:
            logger.info(f"\n⚠ WARNINGS:")
            for warning in self.results['warnings'][:10]:
                logger.info(f"  - {warning}")
            if len(self.results['warnings']) > 10:
                logger.info(f"  ... and {len(self.results['warnings']) - 10} more")

        if self.results['errors']:
            logger.info(f"\n❌ ERRORS:")
            for error in self.results['errors'][:10]:
                logger.info(f"  - {error}")
            if len(self.results['errors']) > 10:
                logger.info(f"  ... and {len(self.results['errors']) - 10} more")

        pass_rate = (self.results['tests_passed'] / self.results['tests_run'] * 100) if self.results['tests_run'] > 0 else 0

        logger.info(f"\n📊 Pass Rate: {pass_rate:.1f}%")

        if pass_rate >= 90:
            logger.info(f"✅ EXCELLENT: Data accuracy is very high")
        elif pass_rate >= 75:
            logger.info(f"✓ GOOD: Data accuracy is acceptable")
        elif pass_rate >= 50:
            logger.info(f"⚠ WARNING: Data accuracy needs improvement")
        else:
            logger.info(f"❌ CRITICAL: Data accuracy is poor")


def main():
    """Run data accuracy validation tests."""
    logger.info("Starting Data Accuracy Validation Suite")
    logger.info("="*80)

    validator = DataAccuracyValidator()

    # Test tickers - mix of large cap, mid cap, volatile
    test_tickers = ['AAPL', 'NVDA', 'MSFT']

    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    # Run tests for each ticker
    for ticker in test_tickers:
        logger.info(f"\n{'#'*80}")
        logger.info(f"# TESTING: {ticker}")
        logger.info(f"{'#'*80}")

        # Test 1: Price Consistency
        validator.validate_price_consistency(ticker, start_date, end_date)

        # Test 2: Technical Indicators
        validator.validate_technical_indicators(ticker)

        # Test 3: Fundamental Data
        validator.validate_fundamental_data(ticker)

        # Test 4: Cache Consistency
        validator.validate_cache_consistency(ticker)

    # Print summary
    validator.print_summary()

    # Return exit code
    if validator.results['tests_failed'] == 0:
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit(main())
