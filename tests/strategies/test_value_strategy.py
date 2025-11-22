# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Tests for Value Strategy.
"""

import unittest
from tradingagents.strategies.value import ValueStrategy
from tradingagents.strategies.base import Recommendation


class TestValueStrategy(unittest.TestCase):
    """Test Value Strategy implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.strategy = ValueStrategy()
    
    def test_strategy_name(self):
        """Test strategy name."""
        self.assertEqual(self.strategy.get_strategy_name(), "Value Investing")
    
    def test_timeframe(self):
        """Test timeframe."""
        self.assertEqual(self.strategy.get_timeframe(), "5-10 years")
    
    def test_evaluate_with_minimal_data(self):
        """Test evaluation with minimal data."""
        result = self.strategy.evaluate(
            ticker="TEST",
            market_data={"current_price": 100.0},
            fundamental_data={"pe_ratio": 20.0},
            technical_data={"rsi": 50.0}
        )
        
        self.assertIsInstance(result.recommendation, Recommendation)
        self.assertGreaterEqual(result.confidence, 0)
        self.assertLessEqual(result.confidence, 100)
        self.assertIsNotNone(result.reasoning)
    
    def test_evaluate_with_good_value(self):
        """Test evaluation with good value metrics."""
        result = self.strategy.evaluate(
            ticker="TEST",
            market_data={"current_price": 100.0},
            fundamental_data={
                "pe_ratio": 12.0,  # Low P/E
                "debt_to_equity": 0.3,  # Low debt
                "roe": 0.20,  # Good ROE
            },
            technical_data={"rsi": 50.0}
        )
        
        # Should recommend BUY or HOLD for good value
        self.assertIn(result.recommendation, [Recommendation.BUY, Recommendation.HOLD])
        self.assertGreater(result.confidence, 50)
    
    def test_evaluate_with_poor_value(self):
        """Test evaluation with poor value metrics."""
        result = self.strategy.evaluate(
            ticker="TEST",
            market_data={"current_price": 100.0},
            fundamental_data={
                "pe_ratio": 60.0,  # High P/E
                "debt_to_equity": 3.0,  # High debt
                "roe": 0.05,  # Low ROE
            },
            technical_data={"rsi": 50.0}
        )
        
        # Should recommend SELL or WAIT for poor value
        self.assertIn(result.recommendation, [Recommendation.SELL, Recommendation.WAIT, Recommendation.HOLD])
    
    def test_validate_data(self):
        """Test data validation."""
        # Valid data
        self.assertTrue(self.strategy.validate_data(
            {"current_price": 100.0},
            {"pe_ratio": 20.0},
            {"rsi": 50.0}
        ))
        
        # Invalid data (empty dicts)
        self.assertFalse(self.strategy.validate_data({}, {}, {}))


if __name__ == "__main__":
    unittest.main()

