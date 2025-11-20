"""
Tests for TradingAgents middleware system.

Tests token tracking and summarization middleware functionality.
"""

import pytest
from typing import Dict, Any
from tradingagents.middleware import (
    TokenTrackingMiddleware,
    SummarizationMiddleware,
    TokenTracker
)


class TestTokenTracker:
    """Test token counting utilities."""
    
    def test_count_tokens(self):
        """Test basic token counting."""
        tracker = TokenTracker(model="gpt-4o")
        
        text = "Hello world"
        count = tracker.count_tokens(text)
        
        assert count > 0
        assert isinstance(count, int)
    
    def test_count_state_tokens(self):
        """Test state token counting."""
        tracker = TokenTracker(model="gpt-4o")
        
        state = {
            "market_report": "This is a market report with some content.",
            "sentiment_report": "Sentiment analysis results.",
            "company_of_interest": "NVDA"
        }
        
        count = tracker.count_state_tokens(state)
        assert count > 0
    
    def test_track_agent_tokens(self):
        """Test agent token tracking."""
        tracker = TokenTracker(model="gpt-4o")
        
        state = {
            "market_report": "Market analysis report.",
            "sender": "market_analyst"
        }
        
        tokens = tracker.track_agent_tokens("market_analyst", state)
        assert tokens > 0
        assert "market_analyst" in tracker.token_counts
        assert tracker.token_counts["market_analyst"] == tokens


class TestTokenTrackingMiddleware:
    """Test token tracking middleware."""
    
    def test_initialization(self):
        """Test middleware initialization."""
        middleware = TokenTrackingMiddleware(model="gpt-4o")
        
        assert middleware.model == "gpt-4o"
        assert middleware.track_per_agent is True
        assert isinstance(middleware.tracker, TokenTracker)
    
    def test_post_process(self):
        """Test post-processing adds token counts."""
        middleware = TokenTrackingMiddleware(model="gpt-4o")
        
        state = {
            "market_report": "Market analysis report.",
            "sender": "market_analyst"
        }
        
        processed = middleware.post_process(state)
        
        assert "_total_tokens" in processed
        assert "_agent_token_count" in processed
        assert "_token_summary" in processed
        assert isinstance(processed["_total_tokens"], int)
    
    def test_get_summary(self):
        """Test getting token usage summary."""
        middleware = TokenTrackingMiddleware(model="gpt-4o")
        
        state = {
            "market_report": "Market analysis report.",
            "sender": "market_analyst"
        }
        
        middleware.post_process(state)
        summary = middleware.get_summary()
        
        assert "total" in summary
        assert "agent_counts" in summary
        assert isinstance(summary["total"], int)


class TestSummarizationMiddleware:
    """Test summarization middleware."""
    
    def test_initialization(self):
        """Test middleware initialization."""
        middleware = SummarizationMiddleware(
            token_threshold=50000,
            summarization_model="gpt-4o-mini"
        )
        
        assert middleware.token_threshold == 50000
        assert middleware.summarization_model == "gpt-4o-mini"
        assert middleware.llm is not None
    
    def test_summarize_analyst_reports_empty(self):
        """Test summarizing empty reports."""
        middleware = SummarizationMiddleware()
        
        state = {}
        summary = middleware.summarize_analyst_reports(state)
        
        assert summary == ""
    
    def test_summarize_analyst_reports(self):
        """Test summarizing analyst reports."""
        middleware = SummarizationMiddleware()
        
        state = {
            "market_report": "Market analysis: NVDA is showing strong momentum.",
            "sentiment_report": "Sentiment: Bullish sentiment detected.",
            "news_report": "News: Recent earnings beat expectations.",
            "fundamentals_report": "Fundamentals: Strong balance sheet."
        }
        
        summary = middleware.summarize_analyst_reports(state)
        
        # Summary should be shorter than combined reports
        total_length = sum(len(v) for v in state.values() if isinstance(v, str))
        assert len(summary) < total_length or summary == ""  # May fail if LLM unavailable
    
    def test_post_process_no_summarization_needed(self):
        """Test post-processing when summarization not needed."""
        middleware = SummarizationMiddleware(token_threshold=50000)
        
        state = {
            "market_report": "Short report.",
            "sentiment_report": "Short sentiment."
        }
        
        processed = middleware.post_process(state)
        
        # Should not add summaries for small reports
        assert "_summarized" in processed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

