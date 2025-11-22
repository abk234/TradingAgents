# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Tests for base strategy classes.
"""

import unittest
from tradingagents.strategies.base import (
    InvestmentStrategy,
    StrategyResult,
    Recommendation,
)


class TestStrategyResult(unittest.TestCase):
    """Test StrategyResult dataclass."""
    
    def test_strategy_result_creation(self):
        """Test creating a StrategyResult."""
        result = StrategyResult(
            recommendation=Recommendation.BUY,
            confidence=75,
            reasoning="Test reasoning",
            strategy_name="Test Strategy"
        )
        
        self.assertEqual(result.recommendation, Recommendation.BUY)
        self.assertEqual(result.confidence, 75)
        self.assertEqual(result.reasoning, "Test reasoning")
        self.assertEqual(result.strategy_name, "Test Strategy")
    
    def test_strategy_result_defaults(self):
        """Test StrategyResult with defaults."""
        result = StrategyResult(
            recommendation=Recommendation.HOLD,
            confidence=50,
            reasoning="Test"
        )
        
        self.assertIsNotNone(result.key_metrics)
        self.assertIsNotNone(result.risks)
        self.assertEqual(len(result.risks), 0)
    
    def test_strategy_result_confidence_validation(self):
        """Test confidence validation."""
        # Valid confidence
        result = StrategyResult(
            recommendation=Recommendation.BUY,
            confidence=75,
            reasoning="Test"
        )
        self.assertEqual(result.confidence, 75)
        
        # Invalid confidence (should raise ValueError)
        with self.assertRaises(ValueError):
            StrategyResult(
                recommendation=Recommendation.BUY,
                confidence=150,  # Invalid
                reasoning="Test"
            )
    
    def test_strategy_result_to_dict(self):
        """Test conversion to dictionary."""
        result = StrategyResult(
            recommendation=Recommendation.BUY,
            confidence=75,
            reasoning="Test reasoning",
            entry_price=100.0,
            target_price=120.0,
            strategy_name="Test Strategy"
        )
        
        result_dict = result.to_dict()
        
        self.assertEqual(result_dict["recommendation"], "BUY")
        self.assertEqual(result_dict["confidence"], 75)
        self.assertEqual(result_dict["reasoning"], "Test reasoning")
        self.assertEqual(result_dict["entry_price"], 100.0)
        self.assertEqual(result_dict["target_price"], 120.0)
        self.assertEqual(result_dict["strategy_name"], "Test Strategy")


class TestRecommendation(unittest.TestCase):
    """Test Recommendation enum."""
    
    def test_recommendation_values(self):
        """Test Recommendation enum values."""
        self.assertEqual(Recommendation.BUY.value, "BUY")
        self.assertEqual(Recommendation.SELL.value, "SELL")
        self.assertEqual(Recommendation.HOLD.value, "HOLD")
        self.assertEqual(Recommendation.WAIT.value, "WAIT")


if __name__ == "__main__":
    unittest.main()

