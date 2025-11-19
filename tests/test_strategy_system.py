"""
Quick test script for strategy system.

Run this to verify the strategy system works.
"""

import sys
from datetime import date

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from tradingagents.strategies import (
            InvestmentStrategy,
            StrategyResult,
            Recommendation,
            StrategyComparator,
            ValueStrategy,
            GrowthStrategy,
            DividendStrategy,
            MomentumStrategy,
            ContrarianStrategy,
            QuantitativeStrategy,
            SectorRotationStrategy,
            StrategyDataCollector,
        )
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_base_classes():
    """Test base classes."""
    print("\nTesting base classes...")
    try:
        from tradingagents.strategies.base import StrategyResult, Recommendation
        
        result = StrategyResult(
            recommendation=Recommendation.BUY,
            confidence=75,
            reasoning="Test",
        )
        
        assert result.recommendation == Recommendation.BUY
        assert result.confidence == 75
        print("✅ Base classes work")
        return True
    except Exception as e:
        print(f"❌ Base class test failed: {e}")
        return False


def test_strategies():
    """Test strategy instantiation."""
    print("\nTesting strategy instantiation...")
    try:
        from tradingagents.strategies import (
            ValueStrategy,
            GrowthStrategy,
            DividendStrategy,
            MomentumStrategy,
        )
        
        strategies = [
            ValueStrategy(),
            GrowthStrategy(),
            DividendStrategy(),
            MomentumStrategy(),
        ]
        
        for strategy in strategies:
            name = strategy.get_strategy_name()
            timeframe = strategy.get_timeframe()
            assert name is not None
            assert timeframe is not None
        
        print(f"✅ All {len(strategies)} strategies instantiate correctly")
        return True
    except Exception as e:
        print(f"❌ Strategy test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_strategy_evaluation():
    """Test strategy evaluation with mock data."""
    print("\nTesting strategy evaluation...")
    try:
        from tradingagents.strategies import ValueStrategy
        
        strategy = ValueStrategy()
        
        # Mock data
        market_data = {"current_price": 100.0}
        fundamental_data = {"pe_ratio": 20.0, "debt_to_equity": 0.5}
        technical_data = {"rsi": 50.0}
        
        result = strategy.evaluate(
            ticker="TEST",
            market_data=market_data,
            fundamental_data=fundamental_data,
            technical_data=technical_data,
        )
        
        assert result is not None
        assert result.recommendation is not None
        assert 0 <= result.confidence <= 100
        assert result.reasoning is not None
        
        print(f"✅ Strategy evaluation works: {result.recommendation.value} ({result.confidence}% confidence)")
        return True
    except Exception as e:
        print(f"❌ Strategy evaluation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_comparator():
    """Test strategy comparator."""
    print("\nTesting strategy comparator...")
    try:
        from tradingagents.strategies import (
            StrategyComparator,
            ValueStrategy,
            GrowthStrategy,
        )
        
        comparator = StrategyComparator([
            ValueStrategy(),
            GrowthStrategy(),
        ])
        
        # Mock data
        market_data = {"current_price": 100.0}
        fundamental_data = {"pe_ratio": 20.0, "revenue_growth": 0.15}
        technical_data = {"rsi": 50.0}
        
        comparison = comparator.compare(
            ticker="TEST",
            market_data=market_data,
            fundamental_data=fundamental_data,
            technical_data=technical_data,
        )
        
        assert "consensus" in comparison
        assert "strategies" in comparison
        assert len(comparison["strategies"]) == 2
        
        print(f"✅ Comparator works: {comparison['consensus']['recommendation']} "
              f"({comparison['consensus']['agreement_level']:.1f}% agreement)")
        return True
    except Exception as e:
        print(f"❌ Comparator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("Strategy System Test Suite")
    print("=" * 70)
    
    tests = [
        test_imports,
        test_base_classes,
        test_strategies,
        test_strategy_evaluation,
        test_comparator,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

