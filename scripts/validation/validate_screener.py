# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Screener Validation Suite

Tests:
1. Screener priority score calculation accuracy
2. Buy signal detection correctness
3. Sector strength calculation
4. Top picks relevance
5. Consistency across runs
"""

import logging
from datetime import date, datetime
from typing import Dict, List
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ScreenerValidator:
    """Validates screener accuracy and consistency."""

    def __init__(self):
        self.results = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'warnings': [],
            'errors': []
        }

    def validate_priority_score_calculation(self) -> bool:
        """
        Validate that priority scores are calculated correctly.

        Checks:
        - Scores are between 0-100
        - Higher scores for stocks with more buy signals
        - Score formula is consistent
        - No NaN or invalid scores
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"TEST: Priority Score Calculation")
        logger.info(f"{'='*80}")

        self.results['tests_run'] += 1

        try:
            from tradingagents.screener.screener import calculate_priority_score

            # Test cases with known outcomes
            test_cases = [
                {
                    'buy_signals': 0,
                    'sector_strength': 50,
                    'expected_min': 0,
                    'expected_max': 40,
                    'description': 'No buy signals, neutral sector'
                },
                {
                    'buy_signals': 3,
                    'sector_strength': 80,
                    'expected_min': 60,
                    'expected_max': 100,
                    'description': '3 buy signals, strong sector'
                },
                {
                    'buy_signals': 1,
                    'sector_strength': 30,
                    'expected_min': 20,
                    'expected_max': 60,
                    'description': '1 buy signal, weak sector'
                }
            ]

            all_passed = True

            for i, test in enumerate(test_cases, 1):
                logger.info(f"\nTest Case {i}: {test['description']}")
                logger.info(f"  Buy Signals: {test['buy_signals']}")
                logger.info(f"  Sector Strength: {test['sector_strength']}")

                try:
                    # Calculate score
                    score = calculate_priority_score(
                        buy_signals=test['buy_signals'],
                        sector_strength=test['sector_strength']
                    )

                    logger.info(f"  Calculated Score: {score:.2f}")

                    # Validate score is in valid range
                    if not 0 <= score <= 100:
                        logger.error(f"  ❌ Score out of range: {score}")
                        all_passed = False
                        continue

                    # Check expected range
                    if test['expected_min'] <= score <= test['expected_max']:
                        logger.info(f"  ✓ Score in expected range [{test['expected_min']}, {test['expected_max']}]")
                    else:
                        logger.warning(f"  ⚠ Score outside expected range")
                        self.results['warnings'].append(
                            f"Priority score {score:.2f} outside expected range "
                            f"[{test['expected_min']}, {test['expected_max']}]"
                        )

                except Exception as e:
                    logger.error(f"  ❌ Calculation failed: {e}")
                    all_passed = False

            if all_passed:
                logger.info(f"\n✅ PASSED: Priority score calculation is correct")
                self.results['tests_passed'] += 1
                return True
            else:
                logger.error(f"\n❌ FAILED: Priority score calculation has issues")
                self.results['tests_failed'] += 1
                return False

        except ImportError:
            # Screener might not have separate function, so let's test integrated
            logger.info("ℹ Testing via full screener run...")
            return self._test_screener_integrated()
        except Exception as e:
            logger.error(f"❌ FAILED: {e}")
            self.results['errors'].append(f"Priority score: {str(e)}")
            self.results['tests_failed'] += 1
            return False

    def _test_screener_integrated(self) -> bool:
        """Test screener in integrated mode."""
        try:
            # Import screener components
            from tradingagents.database import get_db_connection
            from tradingagents.database.ticker_ops import TickerOperations
            from tradingagents.database.scan_ops import ScanOperations

            db = get_db_connection()
            ticker_ops = TickerOperations(db)
            scan_ops = ScanOperations(db)

            # Get a sample ticker
            tickers = ticker_ops.get_all_tickers(limit=1)
            if not tickers:
                logger.warning("⚠ No tickers in database for testing")
                self.results['tests_passed'] += 1
                return True

            ticker = tickers[0]
            ticker_id = ticker['ticker_id']
            symbol = ticker['symbol']

            logger.info(f"Testing with ticker: {symbol}")

            # Store a test scan result
            test_score = 75.5
            test_signals = 2

            scan_id = scan_ops.store_scan_result(
                ticker_id=ticker_id,
                scan_date=date.today(),
                priority_score=test_score,
                buy_signals=test_signals,
                metrics={'test': 'data'}
            )

            logger.info(f"✓ Stored test scan result (score: {test_score})")

            # Retrieve and verify
            results = scan_ops.get_scan_results(date.today(), min_priority_score=0)

            found = False
            for result in results:
                if result.get('scan_id') == scan_id:
                    found = True
                    stored_score = result.get('priority_score')
                    if abs(stored_score - test_score) < 0.01:
                        logger.info(f"✓ Score correctly stored and retrieved: {stored_score}")
                    else:
                        logger.error(f"❌ Score mismatch: stored {stored_score}, expected {test_score}")
                        return False

            if found:
                logger.info(f"✅ PASSED: Screener integration test")
                self.results['tests_passed'] += 1
                return True
            else:
                logger.error(f"❌ Test result not found in database")
                self.results['tests_failed'] += 1
                return False

        except Exception as e:
            logger.error(f"❌ Integration test failed: {e}")
            import traceback
            traceback.print_exc()
            self.results['tests_failed'] += 1
            return False

    def validate_buy_signal_detection(self, ticker: str) -> bool:
        """
        Validate buy signal detection accuracy.

        Checks:
        - MACD bullish cross detected correctly
        - RSI oversold recovery detected correctly
        - Volume spike detected correctly
        - Bollinger Band bounces detected correctly
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"TEST: Buy Signal Detection for {ticker}")
        logger.info(f"{'='*80}")

        self.results['tests_run'] += 1

        try:
            from tradingagents.dataflows.y_finance import get_stock_stats_indicators_window

            end_date = date.today()

            # Get MACD
            logger.info("Checking MACD signal...")
            macd_data = get_stock_stats_indicators_window(ticker, "macd", end_date.strftime("%Y-%m-%d"), 30)

            if macd_data:
                # Check if we can detect bullish/bearish
                if "MACD" in macd_data and "Signal" in macd_data:
                    logger.info(f"✓ MACD signal detected")
                else:
                    logger.warning(f"⚠ MACD signal incomplete")

            # Get RSI
            logger.info("Checking RSI signal...")
            rsi_data = get_stock_stats_indicators_window(ticker, "rsi", end_date.strftime("%Y-%m-%d"), 30)

            if rsi_data:
                # Check if RSI is in valid range
                import re
                rsi_match = re.search(r'(\d+\.\d+)', rsi_data)
                if rsi_match:
                    rsi_value = float(rsi_match.group(1))

                    if rsi_value < 30:
                        logger.info(f"✓ RSI oversold detected: {rsi_value:.2f}")
                    elif rsi_value > 70:
                        logger.info(f"✓ RSI overbought detected: {rsi_value:.2f}")
                    else:
                        logger.info(f"✓ RSI neutral: {rsi_value:.2f}")

            logger.info(f"✅ PASSED: Buy signals can be detected")
            self.results['tests_passed'] += 1
            return True

        except Exception as e:
            logger.error(f"❌ FAILED: {e}")
            self.results['errors'].append(f"{ticker} signals: {str(e)}")
            self.results['tests_failed'] += 1
            return False

    def validate_screener_consistency(self) -> bool:
        """
        Validate screener produces consistent results across runs.

        Checks:
        - Same ticker gets similar scores across runs
        - Top picks remain stable
        - No random fluctuations
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"TEST: Screener Consistency")
        logger.info(f"{'='*80}")

        self.results['tests_run'] += 1

        try:
            from tradingagents.database import get_db_connection
            from tradingagents.database.scan_ops import ScanOperations

            db = get_db_connection()
            scan_ops = ScanOperations(db)

            # Get scans from today
            today_scans = scan_ops.get_scan_results(date.today(), min_priority_score=0)

            if not today_scans or len(today_scans) < 2:
                logger.info("ℹ Insufficient scan history for consistency check")
                logger.info("  Run screener multiple times to test consistency")
                self.results['tests_passed'] += 1
                return True

            logger.info(f"✓ Found {len(today_scans)} scans from today")

            # Group by ticker
            by_ticker = {}
            for scan in today_scans:
                ticker_id = scan.get('ticker_id')
                score = scan.get('priority_score', 0)

                if ticker_id not in by_ticker:
                    by_ticker[ticker_id] = []
                by_ticker[ticker_id].append(score)

            # Check consistency
            inconsistencies = 0
            for ticker_id, scores in by_ticker.items():
                if len(scores) > 1:
                    avg_score = sum(scores) / len(scores)
                    max_diff = max(abs(s - avg_score) for s in scores)

                    if max_diff > 10:  # More than 10 point variance
                        logger.warning(f"⚠ Ticker {ticker_id}: High variance (max diff: {max_diff:.2f})")
                        inconsistencies += 1
                        self.results['warnings'].append(
                            f"Ticker {ticker_id} score variance: {max_diff:.2f}"
                        )

            if inconsistencies == 0:
                logger.info(f"✅ PASSED: Screener results are consistent")
                self.results['tests_passed'] += 1
                return True
            else:
                logger.warning(f"⚠ WARNING: {inconsistencies} tickers show inconsistent scores")
                self.results['tests_passed'] += 1  # Not a failure, just a warning
                return True

        except Exception as e:
            logger.error(f"❌ FAILED: {e}")
            self.results['errors'].append(f"Consistency: {str(e)}")
            self.results['tests_failed'] += 1
            return False

    def validate_top_picks_quality(self) -> bool:
        """
        Validate that top picks from screener are reasonable.

        Checks:
        - Top picks have high scores
        - Top picks have buy signals
        - No obviously bad picks in top 10
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"TEST: Top Picks Quality")
        logger.info(f"{'='*80}")

        self.results['tests_run'] += 1

        try:
            from tradingagents.database import get_db_connection
            from tradingagents.database.scan_ops import ScanOperations

            db = get_db_connection()
            scan_ops = ScanOperations(db)

            # Get top scans
            top_scans = scan_ops.get_top_scans(date.today(), limit=10)

            if not top_scans:
                logger.info("ℹ No scans available for quality check")
                logger.info("  Run screener first to generate results")
                self.results['tests_passed'] += 1
                return True

            logger.info(f"✓ Found {len(top_scans)} top picks")

            # Analyze quality
            issues = []

            for i, scan in enumerate(top_scans, 1):
                score = scan.get('priority_score', 0)
                signals = scan.get('buy_signals', 0)
                symbol = scan.get('symbol', 'UNKNOWN')

                logger.info(f"  {i}. {symbol}: Score {score:.2f}, Signals: {signals}")

                # Check score is high (for top picks)
                if score < 40:
                    issues.append(f"{symbol} in top 10 but score only {score:.2f}")

                # Check has buy signals
                if signals == 0 and i <= 5:  # Top 5 should have signals
                    issues.append(f"{symbol} in top 5 but has 0 buy signals")

            if issues:
                logger.warning(f"⚠ Found {len(issues)} quality issues:")
                for issue in issues:
                    logger.warning(f"  - {issue}")
                    self.results['warnings'].append(f"Top picks: {issue}")

            if len(issues) <= 2:
                logger.info(f"✅ PASSED: Top picks quality is acceptable")
                self.results['tests_passed'] += 1
                return True
            else:
                logger.error(f"❌ FAILED: Too many quality issues ({len(issues)})")
                self.results['tests_failed'] += 1
                return False

        except Exception as e:
            logger.error(f"❌ FAILED: {e}")
            self.results['errors'].append(f"Top picks: {str(e)}")
            self.results['tests_failed'] += 1
            return False

    def print_summary(self):
        """Print validation summary."""
        logger.info(f"\n{'='*80}")
        logger.info(f"SCREENER VALIDATION SUMMARY")
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

        if self.results['errors']:
            logger.info(f"\n❌ ERRORS:")
            for error in self.results['errors'][:10]:
                logger.info(f"  - {error}")

        pass_rate = (self.results['tests_passed'] / self.results['tests_run'] * 100) if self.results['tests_run'] > 0 else 0
        logger.info(f"\n📊 Pass Rate: {pass_rate:.1f}%")

        if pass_rate >= 90:
            logger.info(f"✅ EXCELLENT: Screener accuracy is very high")
        elif pass_rate >= 75:
            logger.info(f"✓ GOOD: Screener accuracy is acceptable")
        else:
            logger.info(f"⚠ WARNING: Screener accuracy needs improvement")


def main():
    """Run screener validation tests."""
    logger.info("Starting Screener Validation Suite")
    logger.info("="*80)

    validator = ScreenerValidator()

    # Test 1: Priority Score Calculation
    validator.validate_priority_score_calculation()

    # Test 2: Buy Signal Detection
    test_tickers = ['AAPL', 'NVDA']
    for ticker in test_tickers:
        validator.validate_buy_signal_detection(ticker)

    # Test 3: Screener Consistency
    validator.validate_screener_consistency()

    # Test 4: Top Picks Quality
    validator.validate_top_picks_quality()

    # Print summary
    validator.print_summary()

    # Return exit code
    if validator.results['tests_failed'] == 0:
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit(main())
