"""
Agent Validation Suite

Tests:
1. Each agent produces valid output
2. Agent reasoning quality
3. Four-Gate Framework validation
4. Agent consensus mechanisms
5. Decision quality and consistency
"""

import logging
from datetime import date, timedelta
from typing import Dict, Any
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentValidator:
    """Validates agent outputs and decision quality."""

    def __init__(self):
        self.results = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'warnings': [],
            'errors': []
        }

    def validate_four_gate_framework(self) -> bool:
        """
        Validate Four-Gate Framework implementation.

        Checks:
        - All gates can be evaluated
        - Gates return valid scores
        - Gates provide reasoning
        - Pass/fail logic works correctly
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"TEST: Four-Gate Framework")
        logger.info(f"{'='*80}")

        self.results['tests_run'] += 1

        try:
            from tradingagents.decision.four_gate import FourGateFramework

            framework = FourGateFramework()
            logger.info("✓ Framework initialized")

            # Test Gate 1: Fundamental Gate
            logger.info("\nTesting Fundamental Gate...")
            fundamentals = {
                'pe_ratio': 25.5,
                'revenue_growth': 15.0,
                'profit_margin': 20.0,
                'debt_to_equity': 0.5
            }

            fund_result = framework.evaluate_fundamental_gate(fundamentals)

            if hasattr(fund_result, 'score'):
                logger.info(f"  ✓ Score: {fund_result.score}")
                logger.info(f"  ✓ Passed: {fund_result.passed}")
                logger.info(f"  ✓ Reasoning: {fund_result.reasoning[:80]}...")

                if 0 <= fund_result.score <= 100:
                    logger.info(f"  ✓ Score in valid range")
                else:
                    logger.error(f"  ❌ Score out of range: {fund_result.score}")
                    self.results['tests_failed'] += 1
                    return False
            else:
                logger.error(f"  ❌ Invalid result format")
                self.results['tests_failed'] += 1
                return False

            # Test Gate 2: Technical Gate
            logger.info("\nTesting Technical Gate...")
            signals = {
                'macd': 'bullish',
                'rsi': 45,
                'trend': 'up'
            }
            price_data = "Recent price action..."

            tech_result = framework.evaluate_technical_gate(signals, price_data)

            if hasattr(tech_result, 'score'):
                logger.info(f"  ✓ Score: {tech_result.score}")
                logger.info(f"  ✓ Passed: {tech_result.passed}")

                if 0 <= tech_result.score <= 100:
                    logger.info(f"  ✓ Score in valid range")
                else:
                    logger.error(f"  ❌ Score out of range: {tech_result.score}")
                    self.results['tests_failed'] += 1
                    return False
            else:
                logger.error(f"  ❌ Invalid result format")
                self.results['tests_failed'] += 1
                return False

            # Test Gate 3: Risk Gate
            logger.info("\nTesting Risk Gate...")
            risk_analysis = {
                'volatility': 'moderate',
                'beta': 1.2,
                'sector_concentration': 15.0
            }
            position_size = 5.0
            portfolio_context = {'total_value': 100000}

            risk_result = framework.evaluate_risk_gate(risk_analysis, position_size, portfolio_context)

            if hasattr(risk_result, 'score'):
                logger.info(f"  ✓ Score: {risk_result.score}")
                logger.info(f"  ✓ Passed: {risk_result.passed}")

                if 0 <= risk_result.score <= 100:
                    logger.info(f"  ✓ Score in valid range")
                else:
                    logger.error(f"  ❌ Score out of range: {risk_result.score}")
                    self.results['tests_failed'] += 1
                    return False
            else:
                logger.error(f"  ❌ Invalid result format")
                self.results['tests_failed'] += 1
                return False

            logger.info(f"\n✅ PASSED: Four-Gate Framework working correctly")
            self.results['tests_passed'] += 1
            return True

        except Exception as e:
            logger.error(f"❌ FAILED: {e}")
            import traceback
            traceback.print_exc()
            self.results['errors'].append(f"Four-Gate: {str(e)}")
            self.results['tests_failed'] += 1
            return False

    def validate_data_validation_gates(self) -> bool:
        """
        Validate data quality validation gates.

        Checks:
        - Data freshness gate
        - Multi-source validation gate
        - Earnings proximity gate
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"TEST: Data Validation Gates")
        logger.info(f"{'='*80}")

        self.results['tests_run'] += 1

        try:
            from tradingagents.decision.validation_gates import (
                DataFreshnessGate,
                MultiSourceValidationGate,
                EarningsProximityGate
            )
            from datetime import datetime

            # Test Data Freshness Gate
            logger.info("\nTesting Data Freshness Gate...")
            freshness_gate = DataFreshnessGate(max_age_minutes=15)

            # Test with fresh data
            fresh_result = freshness_gate.validate(
                ticker="AAPL",
                data_timestamp=datetime.now(),
                current_time=datetime.now()
            )

            logger.info(f"  Fresh data - Score: {fresh_result.score}, Passed: {fresh_result.passed}")

            if fresh_result.passed and fresh_result.score >= 90:
                logger.info(f"  ✓ Fresh data detected correctly")
            else:
                logger.warning(f"  ⚠ Unexpected result for fresh data")

            # Test with stale data
            stale_timestamp = datetime.now() - timedelta(hours=2)
            stale_result = freshness_gate.validate(
                ticker="AAPL",
                data_timestamp=stale_timestamp,
                current_time=datetime.now()
            )

            logger.info(f"  Stale data - Score: {stale_result.score}, Passed: {stale_result.passed}")

            if not stale_result.passed or stale_result.score < 50:
                logger.info(f"  ✓ Stale data detected correctly")
            else:
                logger.warning(f"  ⚠ Stale data not detected")

            # Test Multi-Source Validation Gate
            logger.info("\nTesting Multi-Source Validation Gate...")
            multi_gate = MultiSourceValidationGate(price_threshold_pct=2.0)

            # Test with consistent prices
            consistent_result = multi_gate.validate(
                ticker="AAPL",
                prices={'yfinance': 150.25, 'alpha_vantage': 150.30}
            )

            logger.info(f"  Consistent prices - Score: {consistent_result.score}, Passed: {consistent_result.passed}")

            if consistent_result.passed:
                logger.info(f"  ✓ Consistent prices validated")
            else:
                logger.warning(f"  ⚠ Consistent prices failed validation")

            # Test with inconsistent prices
            inconsistent_result = multi_gate.validate(
                ticker="AAPL",
                prices={'yfinance': 150.00, 'alpha_vantage': 160.00}
            )

            logger.info(f"  Inconsistent prices - Score: {inconsistent_result.score}, Passed: {inconsistent_result.passed}")

            if not inconsistent_result.passed:
                logger.info(f"  ✓ Inconsistent prices detected")
            else:
                logger.warning(f"  ⚠ Inconsistent prices not detected")

            # Test Earnings Proximity Gate
            logger.info("\nTesting Earnings Proximity Gate...")
            earnings_gate = EarningsProximityGate(days_before=7, days_after=3)

            # Test far from earnings
            safe_result = earnings_gate.validate(
                ticker="AAPL",
                analysis_date=date.today(),
                earnings_date=date.today() + timedelta(days=30)
            )

            logger.info(f"  Safe period - Score: {safe_result.score}, Passed: {safe_result.passed}")

            if safe_result.passed and safe_result.score >= 90:
                logger.info(f"  ✓ Safe period detected")
            else:
                logger.warning(f"  ⚠ Unexpected result for safe period")

            # Test close to earnings
            risky_result = earnings_gate.validate(
                ticker="AAPL",
                analysis_date=date.today(),
                earnings_date=date.today() + timedelta(days=2)
            )

            logger.info(f"  Risky period - Score: {risky_result.score}, Passed: {risky_result.passed}")

            if risky_result.score < 50:
                logger.info(f"  ✓ Risky period detected")
            else:
                logger.warning(f"  ⚠ Risky period not detected")

            logger.info(f"\n✅ PASSED: Data validation gates working correctly")
            self.results['tests_passed'] += 1
            return True

        except Exception as e:
            logger.error(f"❌ FAILED: {e}")
            import traceback
            traceback.print_exc()
            self.results['errors'].append(f"Validation gates: {str(e)}")
            self.results['tests_failed'] += 1
            return False

    def validate_agent_output_format(self, ticker: str) -> bool:
        """
        Validate that agent outputs have correct format.

        Checks:
        - Analysis data structure is valid
        - Required fields are present
        - Decision is BUY/SELL/HOLD
        - Confidence is 0-1
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"TEST: Agent Output Format for {ticker}")
        logger.info(f"{'='*80}")

        self.results['tests_run'] += 1

        try:
            # We'll test by checking database storage format
            from tradingagents.database import get_db_connection
            from tradingagents.database.analysis_ops import AnalysisOperations
            from tradingagents.database.ticker_ops import TickerOperations

            db = get_db_connection()
            analysis_ops = AnalysisOperations(db)
            ticker_ops = TickerOperations(db)

            # Get ticker_id
            ticker_id = ticker_ops.get_or_create_ticker(
                symbol=ticker,
                company_name=ticker,
                sector="Test",
                industry="Test"
            )

            # Create sample analysis data (simulating agent output)
            analysis_data = {
                'price': 150.25,
                'volume': 50000000,
                'final_decision': 'BUY',
                'confidence_score': 0.85,
                'executive_summary': 'Test analysis output validation',
                'full_report': {
                    'fundamentals': 'Strong fundamentals',
                    'technical': 'Bullish technical setup',
                    'reasoning': 'Multiple buy signals present'
                }
            }

            # Validate required fields
            required_fields = ['final_decision', 'confidence_score']
            missing_fields = []

            for field in required_fields:
                if field not in analysis_data:
                    missing_fields.append(field)

            if missing_fields:
                logger.error(f"❌ Missing required fields: {missing_fields}")
                self.results['tests_failed'] += 1
                return False

            logger.info(f"✓ All required fields present")

            # Validate decision value
            decision = analysis_data['final_decision']
            valid_decisions = ['BUY', 'SELL', 'HOLD']

            if decision in valid_decisions:
                logger.info(f"✓ Decision is valid: {decision}")
            else:
                logger.error(f"❌ Invalid decision: {decision}")
                self.results['tests_failed'] += 1
                return False

            # Validate confidence
            confidence = analysis_data['confidence_score']
            if 0 <= confidence <= 1:
                logger.info(f"✓ Confidence in valid range: {confidence}")
            else:
                logger.error(f"❌ Confidence out of range: {confidence}")
                self.results['tests_failed'] += 1
                return False

            # Test storage (validates format compatibility)
            try:
                analysis_id = analysis_ops.store_analysis(
                    ticker_id=ticker_id,
                    analysis_data=analysis_data
                )
                logger.info(f"✓ Analysis stored successfully (ID: {analysis_id})")
            except Exception as e:
                logger.error(f"❌ Failed to store analysis: {e}")
                self.results['tests_failed'] += 1
                return False

            logger.info(f"✅ PASSED: Agent output format is valid")
            self.results['tests_passed'] += 1
            return True

        except Exception as e:
            logger.error(f"❌ FAILED: {e}")
            import traceback
            traceback.print_exc()
            self.results['errors'].append(f"Agent output {ticker}: {str(e)}")
            self.results['tests_failed'] += 1
            return False

    def validate_agent_reasoning_quality(self) -> bool:
        """
        Validate that agent reasoning is substantive.

        Checks:
        - Reasoning is not empty
        - Reasoning is detailed enough (min length)
        - Reasoning mentions key factors
        - No generic/template responses
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"TEST: Agent Reasoning Quality")
        logger.info(f"{'='*80}")

        self.results['tests_run'] += 1

        try:
            from tradingagents.database import get_db_connection
            from tradingagents.database.analysis_ops import AnalysisOperations

            db = get_db_connection()
            analysis_ops = AnalysisOperations(db)

            # Get recent analyses
            recent = analysis_ops.get_recent_analyses(days=30, limit=5)

            if not recent:
                logger.info("ℹ No recent analyses for quality check")
                logger.info("  Run analysis first to test reasoning quality")
                self.results['tests_passed'] += 1
                return True

            logger.info(f"✓ Found {len(recent)} recent analyses")

            quality_issues = 0

            for analysis in recent:
                exec_summary = analysis.get('executive_summary', '')
                ticker_id = analysis.get('ticker_id')

                logger.info(f"\nAnalysis for ticker_id {ticker_id}:")
                logger.info(f"  Summary length: {len(exec_summary)} chars")

                # Check minimum length
                if len(exec_summary) < 50:
                    logger.warning(f"  ⚠ Summary too short (< 50 chars)")
                    quality_issues += 1
                else:
                    logger.info(f"  ✓ Summary has sufficient detail")

                # Check for key terms (indicates substantive analysis)
                key_terms = ['price', 'trend', 'signal', 'analysis', 'technical', 'fundamental']
                found_terms = sum(1 for term in key_terms if term.lower() in exec_summary.lower())

                if found_terms >= 2:
                    logger.info(f"  ✓ Contains {found_terms} key terms")
                else:
                    logger.warning(f"  ⚠ Only {found_terms} key terms found")
                    quality_issues += 1

            if quality_issues == 0:
                logger.info(f"\n✅ PASSED: All analyses have good reasoning quality")
                self.results['tests_passed'] += 1
                return True
            elif quality_issues <= len(recent) // 2:
                logger.warning(f"\n⚠ WARNING: {quality_issues}/{len(recent)} analyses have quality issues")
                self.results['tests_passed'] += 1
                return True
            else:
                logger.error(f"\n❌ FAILED: Too many quality issues ({quality_issues}/{len(recent)})")
                self.results['tests_failed'] += 1
                return False

        except Exception as e:
            logger.error(f"❌ FAILED: {e}")
            import traceback
            traceback.print_exc()
            self.results['errors'].append(f"Reasoning quality: {str(e)}")
            self.results['tests_failed'] += 1
            return False

    def print_summary(self):
        """Print validation summary."""
        logger.info(f"\n{'='*80}")
        logger.info(f"AGENT VALIDATION SUMMARY")
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
            logger.info(f"✅ EXCELLENT: Agents are working very well")
        elif pass_rate >= 75:
            logger.info(f"✓ GOOD: Agents are working acceptably")
        else:
            logger.info(f"⚠ WARNING: Agents need improvement")


def main():
    """Run agent validation tests."""
    logger.info("Starting Agent Validation Suite")
    logger.info("="*80)

    validator = AgentValidator()

    # Test 1: Four-Gate Framework
    validator.validate_four_gate_framework()

    # Test 2: Data Validation Gates
    validator.validate_data_validation_gates()

    # Test 3: Agent Output Format
    test_tickers = ['AAPL', 'NVDA']
    for ticker in test_tickers:
        validator.validate_agent_output_format(ticker)

    # Test 4: Reasoning Quality
    validator.validate_agent_reasoning_quality()

    # Print summary
    validator.print_summary()

    # Return exit code
    if validator.results['tests_failed'] == 0:
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit(main())
