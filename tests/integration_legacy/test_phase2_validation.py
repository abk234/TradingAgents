# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Test script for Phase 2 validation features
"""

import sys
sys.path.insert(0, '/Users/lxupkzwjs/Developer/eval/TradingAgents')

from tradingagents.validation import (
    validate_price_multi_source,
    check_earnings_proximity,
    check_volume_anomaly,
)

def test_price_validation():
    """Test multi-source price validation"""
    print("\n" + "="*70)
    print("TEST 1: Multi-Source Price Validation")
    print("="*70)

    ticker = "AAPL"
    print(f"\nTesting price validation for {ticker}...")

    try:
        report = validate_price_multi_source(ticker)
        print(report.format_for_display())
        print(f"\n✅ Price validation test PASSED for {ticker}")
        return True
    except Exception as e:
        print(f"\n❌ Price validation test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_earnings_proximity():
    """Test earnings proximity checking"""
    print("\n" + "="*70)
    print("TEST 2: Earnings Proximity Check")
    print("="*70)

    ticker = "AAPL"
    print(f"\nTesting earnings proximity for {ticker}...")

    try:
        report = check_earnings_proximity(ticker)
        print(report.format_for_display())
        print(f"\n✅ Earnings proximity test PASSED for {ticker}")
        return True
    except Exception as e:
        print(f"\n❌ Earnings proximity test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_volume_anomaly():
    """Test volume anomaly detection"""
    print("\n" + "="*70)
    print("TEST 3: Volume Anomaly Detection")
    print("="*70)

    ticker = "AAPL"
    print(f"\nTesting volume anomaly for {ticker}...")

    try:
        # Get current volume first
        from tradingagents.validation import get_yfinance_current_price
        price, volume = get_yfinance_current_price(ticker)

        if volume:
            is_anomalous, ratio = check_volume_anomaly(ticker, volume)

            if ratio:
                print(f"\nVolume: {volume:,}")
                print(f"Volume Ratio: {ratio:.2f}x average")
                print(f"Anomalous: {'Yes' if is_anomalous else 'No'}")
            else:
                print(f"\nVolume: {volume:,}")
                print("Could not calculate volume ratio (insufficient historical data)")

            print(f"\n✅ Volume anomaly test PASSED for {ticker}")
            return True
        else:
            print(f"\n⚠️ No volume data available for {ticker}")
            return True
    except Exception as e:
        print(f"\n❌ Volume anomaly test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tools_import():
    """Test that Eddie's tools can import the new validation functions"""
    print("\n" + "="*70)
    print("TEST 4: Tool Integration Check")
    print("="*70)

    try:
        from tradingagents.bot.tools import get_all_tools

        tools = get_all_tools()
        tool_names = [tool.name for tool in tools]

        print(f"\nTotal tools available: {len(tools)}")
        print(f"\nValidation tools:")

        validation_tools = [name for name in tool_names if 'data' in name or 'price' in name or 'earnings' in name]
        for tool in validation_tools:
            print(f"  ✓ {tool}")

        # Check for Phase 2 tools
        expected_tools = ['check_data_quality', 'validate_price_sources', 'check_earnings_risk']
        missing_tools = [t for t in expected_tools if t not in tool_names]

        if missing_tools:
            print(f"\n❌ Missing tools: {missing_tools}")
            return False
        else:
            print(f"\n✅ All Phase 2 tools present!")
            print(f"   - check_data_quality (Phase 1)")
            print(f"   - validate_price_sources (Phase 2)")
            print(f"   - check_earnings_risk (Phase 2)")
            return True

    except Exception as e:
        print(f"\n❌ Tool integration test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Phase 2 validation tests"""
    print("\n" + "="*70)
    print("PHASE 2 VALIDATION TEST SUITE")
    print("="*70)

    results = []

    # Test 1: Price Validation
    results.append(("Multi-Source Price Validation", test_price_validation()))

    # Test 2: Earnings Proximity
    results.append(("Earnings Proximity Check", test_earnings_proximity()))

    # Test 3: Volume Anomaly
    results.append(("Volume Anomaly Detection", test_volume_anomaly()))

    # Test 4: Tool Integration
    results.append(("Tool Integration", test_tools_import()))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All Phase 2 validation tests PASSED!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) FAILED")
        return 1


if __name__ == "__main__":
    exit(main())
