"""
Tests for Growth Strategy.
"""

import unittest
from tradingagents.strategies.growth import GrowthStrategy
from tradingagents.strategies.base import Recommendation


class TestGrowthStrategy(unittest.TestCase):
    """Test Growth Strategy implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.strategy = GrowthStrategy()
    
    def test_strategy_name(self):
        """Test strategy name."""
        self.assertEqual(self.strategy.get_strategy_name(), "Growth Investing")
    
    def test_timeframe(self):
        """Test timeframe."""
        self.assertEqual(self.strategy.get_timeframe(), "1-5 years")
    
    def test_evaluate_with_strong_growth(self):
        """Test evaluation with strong growth metrics."""
        result = self.strategy.evaluate(
            ticker="TEST",
            market_data={"current_price": 100.0},
            fundamental_data={
                "revenue_growth": 0.25,  # 25% growth
                "earnings_growth": 0.30,  # 30% growth
                "pe_ratio": 25.0,
            },
            technical_data={"rsi": 50.0}
        )
        
        # Should recommend BUY for strong growth
        self.assertIn(result.recommendation, [Recommendation.BUY, Recommendation.HOLD])
        self.assertGreater(result.confidence, 50)
    
    def test_evaluate_with_negative_growth(self):
        """Test evaluation with negative growth."""
        result = self.strategy.evaluate(
            ticker="TEST",
            market_data={"current_price": 100.0},
            fundamental_data={
                "revenue_growth": -0.10,  # Negative growth
                "earnings_growth": -0.05,
                "pe_ratio": 30.0,
            },
            technical_data={"rsi": 50.0}
        )
        
        # Should recommend SELL or WAIT for negative growth
        self.assertIn(result.recommendation, [Recommendation.SELL, Recommendation.WAIT, Recommendation.HOLD])
    
    def test_peg_ratio_scoring(self):
        """Test PEG ratio scoring."""
        # Good PEG ratio (< 1.0)
        result1 = self.strategy.evaluate(
            ticker="TEST",
            market_data={"current_price": 100.0},
            fundamental_data={
                "pe_ratio": 20.0,
                "earnings_growth": 0.25,  # 25% growth
            },
            technical_data={}
        )
        
        # High PEG ratio (> 2.0)
        result2 = self.strategy.evaluate(
            ticker="TEST",
            market_data={"current_price": 100.0},
            fundamental_data={
                "pe_ratio": 50.0,
                "earnings_growth": 0.10,  # 10% growth
            },
            technical_data={}
        )
        
        # First should score higher
        self.assertGreaterEqual(result1.confidence, result2.confidence)


if __name__ == "__main__":
    unittest.main()

