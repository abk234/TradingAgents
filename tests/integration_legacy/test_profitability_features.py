# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Test Script for Profitability Features

Validates all profitability improvements are working correctly.
"""

import sys
from datetime import date
from decimal import Decimal
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_dynamic_thresholds():
    """Test dynamic gate thresholds."""
    logger.info("="*70)
    logger.info("Testing Dynamic Gate Thresholds")
    logger.info("="*70)
    
    from tradingagents.decision.four_gate import FourGateFramework
    from tradingagents.decision.market_regime import MarketRegimeDetector
    
    framework = FourGateFramework()
    regime_detector = MarketRegimeDetector()
    
    # Test confidence-based thresholds
    thresholds_high_conf = framework.get_dynamic_thresholds(confidence_score=90)
    thresholds_low_conf = framework.get_dynamic_thresholds(confidence_score=55)
    
    logger.info(f"High confidence thresholds: {thresholds_high_conf}")
    logger.info(f"Low confidence thresholds: {thresholds_low_conf}")
    
    assert thresholds_high_conf['fundamental_min_score'] <= 70, "High confidence should lower thresholds"
    assert thresholds_low_conf['fundamental_min_score'] >= 70, "Low confidence should raise thresholds"
    
    # Test market regime detection
    market_regime = regime_detector.detect_market_regime()
    volatility_regime = regime_detector.detect_volatility_regime()
    
    logger.info(f"Market regime: {market_regime}")
    logger.info(f"Volatility regime: {volatility_regime}")
    
    # Test regime-based thresholds
    regime_thresholds = regime_detector.get_dynamic_thresholds(market_regime, volatility_regime)
    logger.info(f"Regime-based thresholds: {regime_thresholds}")
    
    logger.info("✅ Dynamic thresholds test PASSED\n")
    return True

def test_position_sizing():
    """Test enhanced position sizing."""
    logger.info("="*70)
    logger.info("Testing Enhanced Position Sizing")
    logger.info("="*70)
    
    from tradingagents.portfolio.position_sizer import PositionSizer
    
    sizer = PositionSizer(
        portfolio_value=Decimal('100000'),
        max_position_pct=Decimal('10.0'),
        risk_tolerance='moderate'
    )
    
    # Test high confidence (should allow up to 12%)
    sizing_high = sizer.calculate_position_size(
        confidence=92,
        current_price=Decimal('175.00')
    )
    
    logger.info(f"High confidence (92): {sizing_high['position_size_pct']}% position")
    assert sizing_high['position_size_pct'] <= 12.0, "High confidence should allow up to 12%"
    
    # Test with gate scores
    gate_scores = {
        'fundamental': 88,
        'technical': 85,
        'risk': 82,
        'timing': 80
    }
    
    sizing_with_gates = sizer.calculate_position_size(
        confidence=85,
        current_price=Decimal('175.00'),
        gate_scores=gate_scores,
        timing_passed=True
    )
    
    logger.info(f"With high gate scores: {sizing_with_gates['position_size_pct']}% position")
    
    # Test trailing stop
    stop_info = sizer.calculate_trailing_stop(
        entry_price=Decimal('175.00'),
        current_price=Decimal('190.00'),
        highest_price=Decimal('195.00')
    )
    
    logger.info(f"Trailing stop: ${stop_info['trailing_stop']}")
    assert stop_info['trailing_stop'] > Decimal('175.00') * Decimal('0.92'), "Stop should trail up"
    
    # Test partial profit
    profit_info = sizer.should_take_partial_profit(
        entry_price=Decimal('175.00'),
        current_price=Decimal('183.75')  # 5% gain
    )
    
    logger.info(f"Partial profit at 5%: {profit_info}")
    assert profit_info['should_take_profit'] == True, "Should take profit at 5%"
    
    logger.info("✅ Position sizing test PASSED\n")
    return True

def test_sector_rotation():
    """Test sector rotation detection."""
    logger.info("="*70)
    logger.info("Testing Sector Rotation Detection")
    logger.info("="*70)
    
    from tradingagents.decision.sector_rotation import SectorRotationDetector
    
    detector = SectorRotationDetector()
    
    # Test sector rotation detection
    actions = detector.detect_sector_rotation()
    
    logger.info(f"Sector actions: {len([a for a in actions.values() if a == 'OVERWEIGHT'])} overweight, "
               f"{len([a for a in actions.values() if a == 'UNDERWEIGHT'])} underweight")
    
    # Test top sectors
    top_sectors = detector.get_top_sectors(limit=3)
    logger.info(f"Top 3 sectors by momentum:")
    for sector_data in top_sectors:
        logger.info(f"  {sector_data['sector']}: {sector_data['momentum_score']:.2f}")
    
    logger.info("✅ Sector rotation test PASSED\n")
    return True

def test_correlation_management():
    """Test correlation-based risk management."""
    logger.info("="*70)
    logger.info("Testing Correlation Risk Management")
    logger.info("="*70)
    
    from tradingagents.portfolio.correlation_manager import CorrelationManager
    
    mgr = CorrelationManager()
    
    # Test correlation check
    existing_holdings = ['AAPL', 'MSFT']
    new_ticker = 'GOOGL'
    
    is_safe, max_corr, correlations = mgr.check_correlation_risk(
        new_ticker, existing_holdings
    )
    
    logger.info(f"Correlation check for {new_ticker}:")
    logger.info(f"  Is safe: {is_safe}")
    logger.info(f"  Max correlation: {max_corr:.2f}")
    logger.info(f"  Correlations: {correlations}")
    
    # Test diversification score
    diversification = mgr.get_diversification_score(
        tickers=['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']
    )
    
    logger.info(f"Diversification score: {diversification['score']:.2f}")
    logger.info(f"Average correlation: {diversification['avg_correlation']:.2f}")
    
    logger.info("✅ Correlation management test PASSED\n")
    return True

def test_earnings_check():
    """Test earnings proximity check."""
    logger.info("="*70)
    logger.info("Testing Earnings Proximity Check")
    logger.info("="*70)
    
    from tradingagents.screener.screener import DailyScreener
    
    screener = DailyScreener()
    
    # Test earnings check
    should_skip, reason = screener.should_skip_ticker('AAPL')
    
    logger.info(f"Should skip AAPL: {should_skip}")
    if should_skip:
        logger.info(f"Reason: {reason}")
    
    logger.info("✅ Earnings check test PASSED\n")
    return True

def test_integration():
    """Test integration of all features."""
    logger.info("="*70)
    logger.info("Testing Feature Integration")
    logger.info("="*70)
    
    from tradingagents.graph.profitability_enhancer import ProfitabilityEnhancer
    
    enhancer = ProfitabilityEnhancer(
        portfolio_value=Decimal('100000'),
        enable_regime_detection=True,
        enable_sector_rotation=True,
        enable_correlation_check=True
    )
    
    # Test dynamic thresholds
    thresholds = enhancer.get_dynamic_thresholds(confidence_score=85)
    logger.info(f"Dynamic thresholds: {thresholds}")
    
    # Test enhancement (mock final state)
    mock_final_state = {
        'confidence_score': 85,
        'final_trade_decision': 'BUY'
    }
    
    enhancements = enhancer.enhance_analysis(
        ticker='AAPL',
        final_state=mock_final_state
    )
    
    logger.info(f"Enhancements: {enhancements}")
    
    logger.info("✅ Integration test PASSED\n")
    return True

def run_all_tests():
    """Run all tests."""
    logger.info("\n" + "="*70)
    logger.info("PROFITABILITY FEATURES TEST SUITE")
    logger.info("="*70 + "\n")
    
    tests = [
        ("Dynamic Thresholds", test_dynamic_thresholds),
        ("Position Sizing", test_position_sizing),
        ("Sector Rotation", test_sector_rotation),
        ("Correlation Management", test_correlation_management),
        ("Earnings Check", test_earnings_check),
        ("Integration", test_integration),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                logger.error(f"❌ {test_name} test FAILED")
        except Exception as e:
            failed += 1
            logger.error(f"❌ {test_name} test FAILED with error: {e}", exc_info=True)
    
    logger.info("="*70)
    logger.info("TEST SUMMARY")
    logger.info("="*70)
    logger.info(f"Passed: {passed}/{len(tests)}")
    logger.info(f"Failed: {failed}/{len(tests)}")
    logger.info("="*70)
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

