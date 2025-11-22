# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Test script for core Eddie improvements (no database dependencies).

Tests:
1. Dividend integration in profit calculations
2. Sector balance enforcement
3. Dividend consideration in fundamental gate
"""

import sys
from decimal import Decimal

# Add project root to path
sys.path.insert(0, '/Users/lxupkzwjs/Developer/eval/TradingAgents')

# Direct imports to avoid database dependencies
from tradingagents.portfolio.position_sizer import PositionSizer
from tradingagents.decision.four_gate import FourGateFramework


def test_dividend_integration():
    """Test dividend integration in profit calculations."""
    print("\n" + "="*60)
    print("TEST 1: Dividend Integration in Profit Calculations")
    print("="*60)
    
    sizer = PositionSizer(
        portfolio_value=Decimal('100000'),
        max_position_pct=Decimal('10.0'),
        risk_tolerance='moderate'
    )
    
    # Test without dividend
    result_no_div = sizer.calculate_position_size(
        confidence=75,
        current_price=Decimal('100.00'),
        target_price=Decimal('110.00')
    )
    
    print(f"\nWithout Dividend:")
    print(f"  Expected Return: {result_no_div['expected_return_pct']}%")
    print(f"  Price Appreciation: {result_no_div.get('price_appreciation_pct', 'N/A')}%")
    print(f"  Dividend Yield: {result_no_div.get('dividend_yield_pct', 'N/A')}%")
    
    # Test with dividend
    result_with_div = sizer.calculate_position_size(
        confidence=75,
        current_price=Decimal('100.00'),
        target_price=Decimal('110.00'),
        annual_dividend_yield=Decimal('3.5')  # 3.5% dividend yield
    )
    
    print(f"\nWith 3.5% Dividend Yield:")
    print(f"  Expected Return: {result_with_div['expected_return_pct']}%")
    print(f"  Price Appreciation: {result_with_div.get('price_appreciation_pct', 'N/A')}%")
    print(f"  Dividend Yield: {result_with_div.get('dividend_yield_pct', 'N/A')}%")
    
    # Verify dividend is included
    if (result_with_div['expected_return_pct'] and 
        result_no_div['expected_return_pct'] and
        result_with_div['expected_return_pct'] > result_no_div['expected_return_pct']):
        print("\n✅ PASS: Dividend yield correctly included in expected return")
        return True
    else:
        print("\n❌ FAIL: Dividend yield not included")
        return False


def test_sector_balance():
    """Test sector balance enforcement."""
    print("\n" + "="*60)
    print("TEST 2: Sector Balance Enforcement")
    print("="*60)
    
    framework = FourGateFramework()
    
    # Test case 1: Would exceed sector limit
    portfolio_context_exceed = {
        'sector': 'Technology',
        'sector_exposure': 32.0,  # Already at 32%
        'sector_limit': 35.0
    }
    
    result_exceed = framework.evaluate_risk_gate(
        risk_analysis={
            'max_expected_drawdown_pct': 10.0,
            'risk_reward_ratio': 2.5,
            'red_flags': []
        },
        position_size_pct=5.0,  # Would bring to 37%
        portfolio_context=portfolio_context_exceed
    )
    
    print(f"\nTest: Adding 5% position when already at 32% (limit: 35%)")
    print(f"  Gate Passed: {result_exceed.passed}")
    print(f"  Score: {result_exceed.score}/100")
    print(f"  Reasoning: {result_exceed.reasoning}")
    
    # Test case 2: Underweight sector (diversification opportunity)
    portfolio_context_underweight = {
        'sector': 'Healthcare',
        'sector_exposure': 10.0,  # Only 10%
        'sector_limit': 35.0
    }
    
    result_underweight = framework.evaluate_risk_gate(
        risk_analysis={
            'max_expected_drawdown_pct': 10.0,
            'risk_reward_ratio': 2.5,
            'red_flags': []
        },
        position_size_pct=5.0,
        portfolio_context=portfolio_context_underweight
    )
    
    print(f"\nTest: Adding 5% position when at 10% (diversification opportunity)")
    print(f"  Gate Passed: {result_underweight.passed}")
    print(f"  Score: {result_underweight.score}/100")
    print(f"  Reasoning: {result_underweight.reasoning}")
    
    # Verify sector limit enforcement
    if not result_exceed.passed and result_underweight.passed:
        print("\n✅ PASS: Sector balance correctly enforced")
        return True
    else:
        print("\n❌ FAIL: Sector balance not properly enforced")
        return False


def test_dividend_in_fundamental_gate():
    """Test dividend consideration in fundamental gate."""
    print("\n" + "="*60)
    print("TEST 3: Dividend Consideration in Fundamental Gate")
    print("="*60)
    
    framework = FourGateFramework()
    
    # Test without dividend
    result_no_div = framework.evaluate_fundamental_gate(
        fundamentals={
            'pe_ratio': 20.0,
            'revenue_growth_yoy': 0.15
        }
    )
    
    print(f"\nWithout Dividend Yield:")
    print(f"  Score: {result_no_div.score}/100")
    
    # Test with high dividend yield
    result_high_div = framework.evaluate_fundamental_gate(
        fundamentals={
            'pe_ratio': 20.0,
            'revenue_growth_yoy': 0.15,
            'dividend_yield': 4.0  # 4% dividend yield
        }
    )
    
    print(f"\nWith 4% Dividend Yield:")
    print(f"  Score: {result_high_div.score}/100")
    print(f"  Reasoning: {result_high_div.reasoning}")
    
    # Verify dividend boosts score
    if result_high_div.score > result_no_div.score:
        print("\n✅ PASS: Dividend yield correctly boosts fundamental score")
        return True
    else:
        print("\n❌ FAIL: Dividend yield not considered")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("EDDIE CORE IMPROVEMENTS TEST SUITE")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Dividend Integration", test_dividend_integration()))
    results.append(("Sector Balance", test_sector_balance()))
    results.append(("Dividend in Fundamental Gate", test_dividend_in_fundamental_gate()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All core tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())

