"""
Tests for Strategy Adapter (integration with existing system).
"""

import unittest
from unittest.mock import Mock, patch
from tradingagents.integration.strategy_adapter import HybridStrategyAdapter
from tradingagents.strategies.base import Recommendation


class TestHybridStrategyAdapter(unittest.TestCase):
    """Test Hybrid Strategy Adapter."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the graph to avoid running full analysis
        self.mock_graph = Mock()
        self.mock_graph.propagate = Mock(return_value=(
            {
                "final_trade_decision": "BUY",
                "confidence_score": 75,
                "investment_plan": "Test plan",
                "profitability_enhancements": {
                    "gate_results": {
                        "fundamental": {"passed": True, "score": 80},
                        "technical": {"passed": True, "score": 70},
                    }
                }
            },
            "BUY"
        ))
    
    def test_strategy_name(self):
        """Test strategy name."""
        adapter = HybridStrategyAdapter(graph=self.mock_graph)
        self.assertEqual(adapter.get_strategy_name(), "Hybrid (Four-Gate + Multi-Agent)")
    
    def test_timeframe(self):
        """Test timeframe."""
        adapter = HybridStrategyAdapter(graph=self.mock_graph)
        self.assertEqual(adapter.get_timeframe(), "30-90 days")
    
    @patch('tradingagents.integration.strategy_adapter.TradingAgentsGraph')
    def test_evaluate_calls_propagate(self, mock_graph_class):
        """Test that evaluate calls propagate."""
        mock_graph = Mock()
        mock_graph.propagate = Mock(return_value=(
            {
                "final_trade_decision": "BUY",
                "confidence_score": 75,
            },
            "BUY"
        ))
        mock_graph_class.return_value = mock_graph
        
        adapter = HybridStrategyAdapter()
        result = adapter.evaluate(
            ticker="TEST",
            market_data={"current_price": 100.0},
            fundamental_data={},
            technical_data={},
            additional_data={"analysis_date": "2024-11-17"}
        )
        
        # Verify propagate was called
        mock_graph.propagate.assert_called_once()
        
        # Verify result
        self.assertIsNotNone(result)
        self.assertIsInstance(result.recommendation, Recommendation)


if __name__ == "__main__":
    unittest.main()

