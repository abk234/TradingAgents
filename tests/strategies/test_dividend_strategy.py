"""
Tests for Dividend Strategy.
"""

import unittest
from tradingagents.strategies.dividend import DividendStrategy
from tradingagents.strategies.base import Recommendation


class TestDividendStrategy(unittest.TestCase):
    """Test Dividend Strategy implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.strategy = DividendStrategy()
    
    def test_strategy_name(self):
        """Test strategy name."""
        self.assertEqual(self.strategy.get_strategy_name(), "Dividend Investing")
    
    def test_timeframe(self):
        """Test timeframe."""
        self.assertEqual(self.strategy.get_timeframe(), "5+ years")
    
    def test_evaluate_with_high_yield(self):
        """Test evaluation with high dividend yield."""
        result = self.strategy.evaluate(
            ticker="TEST",
            market_data={"current_price": 100.0},
            fundamental_data={"dividend_yield": 0.05},  # 5% yield
            technical_data={"rsi": 50.0},  # Add technical data for validation
            additional_data={
                "dividend_data": {
                    "safety_analysis": {
                        "payout_ratio": 0.60,
                        "consecutive_years": 10,
                        "growth_rate": 0.08,
                    }
                }
            }
        )
        
        # Should recommend BUY or HOLD for high yield (or WAIT if data insufficient)
        self.assertIn(result.recommendation, [Recommendation.BUY, Recommendation.HOLD, Recommendation.WAIT])
        self.assertGreaterEqual(result.confidence, 0)
    
    def test_evaluate_with_low_yield(self):
        """Test evaluation with low dividend yield."""
        result = self.strategy.evaluate(
            ticker="TEST",
            market_data={"current_price": 100.0},
            fundamental_data={"dividend_yield": 0.005},  # 0.5% yield
            technical_data={},
            additional_data={
                "dividend_data": {
                    "safety_analysis": {}
                }
            }
        )
        
        # Should recommend SELL or WAIT for low yield
        self.assertIn(result.recommendation, [Recommendation.SELL, Recommendation.WAIT, Recommendation.HOLD])
    
    def test_payout_ratio_scoring(self):
        """Test payout ratio scoring."""
        # Safe payout ratio (< 60%)
        result1 = self.strategy.evaluate(
            ticker="TEST",
            market_data={"current_price": 100.0},
            fundamental_data={"dividend_yield": 0.04, "payout_ratio": 0.50},
            technical_data={},
            additional_data={
                "dividend_data": {
                    "safety_analysis": {
                        "consecutive_years": 5,
                    }
                }
            }
        )
        
        # High payout ratio (> 90%)
        result2 = self.strategy.evaluate(
            ticker="TEST",
            market_data={"current_price": 100.0},
            fundamental_data={"dividend_yield": 0.04, "payout_ratio": 0.95},
            technical_data={},
            additional_data={
                "dividend_data": {
                    "safety_analysis": {
                        "consecutive_years": 5,
                    }
                }
            }
        )
        
        # First should score higher
        self.assertGreaterEqual(result1.confidence, result2.confidence)


if __name__ == "__main__":
    unittest.main()

