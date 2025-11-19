"""
Tests for Strategy Comparator.
"""

import unittest
from tradingagents.strategies.comparator import StrategyComparator
from tradingagents.strategies.value import ValueStrategy
from tradingagents.strategies.growth import GrowthStrategy
from tradingagents.strategies.base import Recommendation


class MockStrategy:
    """Mock strategy for testing."""
    
    def get_strategy_name(self):
        return "Mock Strategy"
    
    def get_timeframe(self):
        return "1 year"
    
    def evaluate(self, ticker, market_data, fundamental_data, technical_data, additional_data=None):
        from tradingagents.strategies.base import StrategyResult
        return StrategyResult(
            recommendation=Recommendation.BUY,
            confidence=75,
            reasoning="Mock reasoning",
            strategy_name="Mock Strategy"
        )


class TestStrategyComparator(unittest.TestCase):
    """Test Strategy Comparator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.strategies = [
            ValueStrategy(),
            GrowthStrategy(),
        ]
        self.comparator = StrategyComparator(self.strategies)
    
    def test_comparator_initialization(self):
        """Test comparator initialization."""
        self.assertEqual(len(self.comparator.strategies), 2)
    
    def test_comparator_requires_strategies(self):
        """Test that comparator requires at least one strategy."""
        with self.assertRaises(ValueError):
            StrategyComparator([])
    
    def test_compare_strategies(self):
        """Test comparing strategies."""
        comparison = self.comparator.compare(
            ticker="TEST",
            market_data={"current_price": 100.0},
            fundamental_data={"pe_ratio": 20.0, "revenue_growth": 0.15},
            technical_data={"rsi": 50.0}
        )
        
        self.assertIn("ticker", comparison)
        self.assertIn("strategies", comparison)
        self.assertIn("consensus", comparison)
        self.assertIn("divergences", comparison)
        self.assertIn("insights", comparison)
        
        self.assertEqual(comparison["ticker"], "TEST")
        self.assertGreater(len(comparison["strategies"]), 0)
    
    def test_consensus_calculation(self):
        """Test consensus calculation."""
        # Create strategies that agree
        strategies = [MockStrategy(), MockStrategy(), MockStrategy()]
        comparator = StrategyComparator(strategies)
        
        comparison = comparator.compare(
            ticker="TEST",
            market_data={"current_price": 100.0},
            fundamental_data={},
            technical_data={}
        )
        
        consensus = comparison["consensus"]
        self.assertIn("recommendation", consensus)
        self.assertIn("agreement_level", consensus)
        self.assertGreaterEqual(consensus["agreement_level"], 0)
        self.assertLessEqual(consensus["agreement_level"], 100)
    
    def test_divergence_detection(self):
        """Test divergence detection."""
        # Strategies will likely diverge (value vs growth)
        comparison = self.comparator.compare(
            ticker="TEST",
            market_data={"current_price": 100.0},
            fundamental_data={"pe_ratio": 20.0, "revenue_growth": 0.15},
            technical_data={"rsi": 50.0}
        )
        
        # Should have divergences structure
        self.assertIsInstance(comparison["divergences"], list)
    
    def test_insights_generation(self):
        """Test insight generation."""
        comparison = self.comparator.compare(
            ticker="TEST",
            market_data={"current_price": 100.0},
            fundamental_data={"pe_ratio": 20.0, "revenue_growth": 0.15},
            technical_data={"rsi": 50.0}
        )
        
        self.assertIsInstance(comparison["insights"], list)
        self.assertGreater(len(comparison["insights"]), 0)


if __name__ == "__main__":
    unittest.main()

