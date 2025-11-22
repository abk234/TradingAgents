# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Test strategy system with real stock data.

This test requires API access and may take time to run.
Run manually: PYTHONPATH=. python tests/test_real_stock_data.py
"""

import sys
import unittest
from datetime import date

# Add project root to path
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents.strategies import (
    StrategyDataCollector,
    StrategyComparator,
    ValueStrategy,
    GrowthStrategy,
    DividendStrategy,
    MomentumStrategy,
)


class TestRealStockData(unittest.TestCase):
    """Test strategies with real stock data."""
    
    @unittest.skipUnless(
        os.getenv("RUN_REAL_DATA_TESTS", "").lower() == "true",
        "Set RUN_REAL_DATA_TESTS=true to run real data tests"
    )
    def test_collect_real_data(self):
        """Test collecting real data for a stock."""
        collector = StrategyDataCollector()
        
        try:
            data = collector.collect_all_data("AAPL", date.today().strftime("%Y-%m-%d"))
            
            # Verify data structure
            self.assertIn("market_data", data)
            self.assertIn("fundamental_data", data)
            self.assertIn("technical_data", data)
            self.assertIn("ticker", data)
            self.assertEqual(data["ticker"], "AAPL")
            
            print(f"\n✅ Successfully collected data for AAPL")
            print(f"   Market data keys: {list(data['market_data'].keys())}")
            print(f"   Fundamental data keys: {list(data['fundamental_data'].keys())[:5]}...")
            print(f"   Technical data keys: {list(data['technical_data'].keys())}")
            
        except Exception as e:
            self.fail(f"Failed to collect real data: {e}")
    
    @unittest.skipUnless(
        os.getenv("RUN_REAL_DATA_TESTS", "").lower() == "true",
        "Set RUN_REAL_DATA_TESTS=true to run real data tests"
    )
    def test_evaluate_real_stock(self):
        """Test evaluating a real stock with strategies."""
        collector = StrategyDataCollector()
        
        try:
            # Collect data
            data = collector.collect_all_data("AAPL", date.today().strftime("%Y-%m-%d"))
            
            # Run Value Strategy
            value_strategy = ValueStrategy()
            value_result = value_strategy.evaluate(
                ticker="AAPL",
                market_data=data["market_data"],
                fundamental_data=data["fundamental_data"],
                technical_data=data["technical_data"],
                additional_data={
                    "dividend_data": data.get("dividend_data", {}),
                }
            )
            
            # Verify result
            self.assertIsNotNone(value_result)
            self.assertIsNotNone(value_result.recommendation)
            self.assertGreaterEqual(value_result.confidence, 0)
            self.assertLessEqual(value_result.confidence, 100)
            
            print(f"\n✅ Value Strategy Result:")
            print(f"   Recommendation: {value_result.recommendation.value}")
            print(f"   Confidence: {value_result.confidence}%")
            print(f"   Reasoning: {value_result.reasoning[:100]}...")
            
        except Exception as e:
            self.fail(f"Failed to evaluate real stock: {e}")
    
    @unittest.skipUnless(
        os.getenv("RUN_REAL_DATA_TESTS", "").lower() == "true",
        "Set RUN_REAL_DATA_TESTS=true to run real data tests"
    )
    def test_compare_real_stock(self):
        """Test comparing strategies on a real stock."""
        collector = StrategyDataCollector()
        
        try:
            # Collect data
            print("\nCollecting data for AAPL...")
            data = collector.collect_all_data("AAPL", date.today().strftime("%Y-%m-%d"))
            
            # Create comparator
            comparator = StrategyComparator([
                ValueStrategy(),
                GrowthStrategy(),
                DividendStrategy(),
                MomentumStrategy(),
            ])
            
            # Compare strategies
            print("Comparing strategies...")
            comparison = comparator.compare(
                ticker="AAPL",
                market_data=data["market_data"],
                fundamental_data=data["fundamental_data"],
                technical_data=data["technical_data"],
                additional_data={
                    "analysis_date": date.today().strftime("%Y-%m-%d"),
                    "dividend_data": data.get("dividend_data", {}),
                    "news_data": data.get("news_data", {}),
                }
            )
            
            # Verify comparison
            self.assertIn("consensus", comparison)
            self.assertIn("strategies", comparison)
            self.assertGreater(len(comparison["strategies"]), 0)
            
            print(f"\n✅ Strategy Comparison Results:")
            print(f"   Consensus: {comparison['consensus']['recommendation']}")
            print(f"   Agreement: {comparison['consensus']['agreement_level']:.1f}%")
            print(f"\n   Individual Results:")
            for name, result in comparison["strategies"].items():
                print(f"     {name}: {result['recommendation']} ({result['confidence']}%)")
            
            print(f"\n   Insights:")
            for insight in comparison["insights"][:3]:
                print(f"     • {insight}")
            
        except Exception as e:
            self.fail(f"Failed to compare strategies on real stock: {e}")


def main():
    """Run tests."""
    print("=" * 70)
    print("Real Stock Data Test Suite")
    print("=" * 70)
    print("\n⚠️  These tests require API access and may take time.")
    print("⚠️  Set RUN_REAL_DATA_TESTS=true to run them.")
    print("=" * 70)
    
    # Run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())

