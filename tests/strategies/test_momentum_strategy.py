"""
Tests for Momentum Strategy.
"""

import unittest
from tradingagents.strategies.momentum import MomentumStrategy
from tradingagents.strategies.base import Recommendation


class TestMomentumStrategy(unittest.TestCase):
    """Test Momentum Strategy implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.strategy = MomentumStrategy()
    
    def test_strategy_name(self):
        """Test strategy name."""
        self.assertEqual(self.strategy.get_strategy_name(), "Momentum Trading")
    
    def test_timeframe(self):
        """Test timeframe."""
        self.assertEqual(self.strategy.get_timeframe(), "30-90 days")
    
    def test_evaluate_with_strong_momentum(self):
        """Test evaluation with strong momentum."""
        result = self.strategy.evaluate(
            ticker="TEST",
            market_data={"current_price": 100.0},
            fundamental_data={"pe_ratio": 20.0},  # Add fundamental data for validation
            technical_data={
                "rsi": 60.0,  # Favorable RSI
                "ma_20": 95.0,
                "ma_50": 90.0,
                "macd": 2.0,
                "macd_signal": 1.5,
                "volume_ratio": 1.8,
            }
        )
        
        # Should recommend BUY or HOLD for strong momentum (or WAIT if data insufficient)
        self.assertIn(result.recommendation, [Recommendation.BUY, Recommendation.HOLD, Recommendation.WAIT])
        self.assertGreaterEqual(result.confidence, 0)
    
    def test_evaluate_with_weak_momentum(self):
        """Test evaluation with weak momentum."""
        result = self.strategy.evaluate(
            ticker="TEST",
            market_data={"current_price": 100.0},
            fundamental_data={},
            technical_data={
                "rsi": 25.0,  # Oversold
                "ma_20": 105.0,
                "ma_50": 110.0,
                "macd": 0.5,
                "macd_signal": 1.5,
                "volume_ratio": 0.6,
            }
        )
        
        # Should recommend SELL or WAIT for weak momentum
        self.assertIn(result.recommendation, [Recommendation.SELL, Recommendation.WAIT, Recommendation.HOLD])
    
    def test_rsi_scoring(self):
        """Test RSI scoring."""
        # Favorable RSI (50-70)
        result1 = self.strategy.evaluate(
            ticker="TEST",
            market_data={"current_price": 100.0},
            fundamental_data={},
            technical_data={"rsi": 60.0, "ma_20": 95.0, "ma_50": 90.0}
        )
        
        # Overbought RSI (> 70)
        result2 = self.strategy.evaluate(
            ticker="TEST",
            market_data={"current_price": 100.0},
            fundamental_data={},
            technical_data={"rsi": 75.0, "ma_20": 95.0, "ma_50": 90.0}
        )
        
        # First should score higher
        self.assertGreaterEqual(result1.confidence, result2.confidence)


if __name__ == "__main__":
    unittest.main()

