#!/usr/bin/env python3
# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Test AI Pine Script Strategy with Real Market Data

This test demonstrates the strategy working with actual market data.
"""

import sys
from pathlib import Path
from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import yfinance as yf
from tradingagents.strategies.market_structure_cloud_trend import MarketStructureCloudTrendStrategy
from tradingagents.strategies.comparator import StrategyComparator
from tradingagents.strategies.value import ValueStrategy
from tradingagents.strategies.growth import GrowthStrategy

def test_with_real_data():
    """Test strategy with real market data."""
    print("="*70)
    print("MARKET STRUCTURE AND CLOUD TREND STRATEGY - REAL DATA TEST")
    print("="*70)
    
    ticker = "AAPL"
    print(f"\nTesting with {ticker}...")
    
    # Fetch real historical data
    print("Fetching historical data...")
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        
        if hist.empty:
            print(f"❌ No data available for {ticker}")
            return False
        
        print(f"✓ Fetched {len(hist)} days of data")
        
        # Prepare data
        data = pd.DataFrame({
            'high': hist['High'],
            'low': hist['Low'],
            'close': hist['Close'],
            'volume': hist['Volume']
        })
        
        # Get current price
        current_price = float(hist['Close'].iloc[-1])
        current_volume = int(hist['Volume'].iloc[-1])
        
        print(f"✓ Current Price: ${current_price:.2f}")
        print(f"✓ Current Volume: {current_volume:,}")
        
        # Create strategy
        strategy = MarketStructureCloudTrendStrategy(timeframe="swing", min_confidence=70)
        
        # Prepare market data
        market_data = {
            "current_price": current_price,
            "volume": current_volume
        }
        
        # Evaluate with historical data
        print("\nEvaluating strategy...")
        result = strategy.evaluate(
            ticker=ticker,
            market_data=market_data,
            fundamental_data={},
            technical_data={},
            additional_data={
                "ticker": ticker,
                "historical_data": data
            }
        )
        
        # Display results
        print("\n" + "="*70)
        print("STRATEGY RESULTS")
        print("="*70)
        print(f"Recommendation: {result.recommendation.value}")
        print(f"Confidence: {result.confidence}%")
        print(f"\nReasoning:")
        print(f"  {result.reasoning}")
        
        if result.entry_price:
            print(f"\nEntry Price: ${result.entry_price:.2f}")
        if result.stop_loss:
            print(f"Stop Loss: ${result.stop_loss:.2f}")
        if result.target_price:
            print(f"Take Profit: ${result.target_price:.2f}")
        
        if result.key_metrics:
            print(f"\nKey Metrics:")
            for key, value in result.key_metrics.items():
                if value is not None:
                    print(f"  {key}: {value}")
        
        if result.risks:
            print(f"\nRisks:")
            for risk in result.risks:
                print(f"  ⚠️ {risk}")
        
        print("\n" + "="*70)
        print("✓ Strategy evaluation completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multi_strategy_comparison():
    """Test multi-strategy comparison with real data."""
    print("\n" + "="*70)
    print("MULTI-STRATEGY COMPARISON TEST")
    print("="*70)
    
    ticker = "MSFT"
    print(f"\nComparing strategies for {ticker}...")
    
    try:
        # Fetch data
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        
        if hist.empty:
            print(f"❌ No data available for {ticker}")
            return False
        
        # Prepare data
        data = pd.DataFrame({
            'high': hist['High'],
            'low': hist['Low'],
            'close': hist['Close'],
            'volume': hist['Volume']
        })
        
        current_price = float(hist['Close'].iloc[-1])
        
        # Create strategies
        strategies = [
            MarketStructureCloudTrendStrategy(timeframe="swing"),
            ValueStrategy(),
            GrowthStrategy()
        ]
        
        comparator = StrategyComparator(strategies)
        
        # Prepare data
        market_data = {"current_price": current_price, "volume": int(hist['Volume'].iloc[-1])}
        fundamental_data = {}
        technical_data = {}
        
        # Compare
        print("Running comparison...")
        result = comparator.compare(
            ticker=ticker,
            market_data=market_data,
            fundamental_data=fundamental_data,
            technical_data=technical_data,
            additional_data={
                "ticker": ticker,
                "historical_data": data
            }
        )
        
        # Display results
        print("\n" + "="*70)
        print("COMPARISON RESULTS")
        print("="*70)
        
        print(f"\nConsensus: {result['consensus'].get('recommendation', 'N/A')}")
        print(f"Confidence: {result['consensus'].get('confidence', 0)}%")
        
        print(f"\nIndividual Strategy Results:")
        for name, strategy_result in result['strategies'].items():
            print(f"\n  {name}:")
            print(f"    Recommendation: {strategy_result['recommendation']}")
            print(f"    Confidence: {strategy_result['confidence']}%")
            if strategy_result.get('reasoning'):
                reasoning = strategy_result['reasoning'][:100]
                print(f"    Reasoning: {reasoning}...")
        
        if result.get('divergences'):
            print(f"\nDivergences Detected: {len(result['divergences'])}")
        
        print("\n" + "="*70)
        print("✓ Multi-strategy comparison completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("MARKET STRUCTURE AND CLOUD TREND STRATEGY - REAL DATA TESTING")
    print("="*70)
    
    tests = [
        ("Real Data Test", test_with_real_data),
        ("Multi-Strategy Comparison", test_multi_strategy_comparison),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} failed: {e}")
            results.append((name, False))
    
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
        print("\n✅ All real data tests passed!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

