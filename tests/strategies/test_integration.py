"""
Integration tests for strategy system.

Tests the full workflow: data collection -> strategy evaluation -> comparison.
"""

import unittest
from unittest.mock import Mock, patch
from tradingagents.strategies import (
    StrategyDataCollector,
    ValueStrategy,
    GrowthStrategy,
    StrategyComparator,
)


class TestStrategyIntegration(unittest.TestCase):
    """Integration tests for strategy system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.collector = StrategyDataCollector()
        self.ticker = "AAPL"
    
    @unittest.skip("Requires API access - run manually")
    def test_full_workflow_real_data(self):
        """Test full workflow with real data (requires API access)."""
        # Collect data
        data = self.collector.collect_all_data(self.ticker)
        
        # Verify data structure
        self.assertIn("market_data", data)
        self.assertIn("fundamental_data", data)
        self.assertIn("technical_data", data)
        
        # Run strategy
        strategy = ValueStrategy()
        result = strategy.evaluate(
            ticker=self.ticker,
            market_data=data["market_data"],
            fundamental_data=data["fundamental_data"],
            technical_data=data["technical_data"],
        )
        
        # Verify result
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.recommendation)
        self.assertGreaterEqual(result.confidence, 0)
        self.assertLessEqual(result.confidence, 100)
    
    def test_full_workflow_mock_data(self):
        """Test full workflow with mock data."""
        # Mock data
        mock_data = {
            "market_data": {
                "current_price": 175.50,
                "ticker": self.ticker,
            },
            "fundamental_data": {
                "pe_ratio": 28.5,
                "revenue_growth": 0.15,
                "debt_to_equity": 1.2,
            },
            "technical_data": {
                "rsi": 55.0,
                "ma_20": 170.0,
                "ma_50": 165.0,
            },
            "dividend_data": {},
            "news_data": {},
        }
        
        # Run strategies
        value_strategy = ValueStrategy()
        growth_strategy = GrowthStrategy()
        
        value_result = value_strategy.evaluate(
            ticker=self.ticker,
            market_data=mock_data["market_data"],
            fundamental_data=mock_data["fundamental_data"],
            technical_data=mock_data["technical_data"],
        )
        
        growth_result = growth_strategy.evaluate(
            ticker=self.ticker,
            market_data=mock_data["market_data"],
            fundamental_data=mock_data["fundamental_data"],
            technical_data=mock_data["technical_data"],
        )
        
        # Verify results
        self.assertIsNotNone(value_result)
        self.assertIsNotNone(growth_result)
        
        # Compare strategies
        comparator = StrategyComparator([value_strategy, growth_strategy])
        comparison = comparator.compare(
            ticker=self.ticker,
            market_data=mock_data["market_data"],
            fundamental_data=mock_data["fundamental_data"],
            technical_data=mock_data["technical_data"],
        )
        
        # Verify comparison
        self.assertIn("consensus", comparison)
        self.assertIn("strategies", comparison)
        self.assertEqual(len(comparison["strategies"]), 2)


if __name__ == "__main__":
    unittest.main()

