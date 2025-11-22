# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

# TradingAgents/graph/propagation.py

from typing import Dict, Any
from tradingagents.agents.utils.agent_states import (
    AgentState,
    InvestDebateState,
    RiskDebateState,
)


class Propagator:
    """Handles state initialization and propagation through the graph."""

    def __init__(self, max_recur_limit=100):
        """Initialize with configuration parameters."""
        self.max_recur_limit = max_recur_limit

    def create_initial_state(
        self, company_name: str, trade_date: str, historical_context: str = None
    ) -> Dict[str, Any]:
        """Create the initial state for the agent graph.

        Args:
            company_name: Company ticker symbol
            trade_date: Date of analysis
            historical_context: Formatted historical intelligence from RAG system
        """
        return {
            "messages": [("human", company_name)],
            "company_of_interest": company_name,
            "trade_date": str(trade_date),
            "historical_context": historical_context or "",
            "investment_debate_state": InvestDebateState(
                {"history": "", "current_response": "", "count": 0}
            ),
            "risk_debate_state": RiskDebateState(
                {
                    "history": "",
                    "current_risky_response": "",
                    "current_safe_response": "",
                    "current_neutral_response": "",
                    "count": 0,
                }
            ),
            "market_report": "",
            "fundamentals_report": "",
            "sentiment_report": "",
            "news_report": "",
        }

    def get_graph_args(self, callbacks=None) -> Dict[str, Any]:
        """Get arguments for the graph invocation.
        
        Args:
            callbacks: Optional list of callback handlers (e.g., Langfuse)
        
        Returns:
            Dictionary with graph arguments including callbacks
        """
        config = {"recursion_limit": self.max_recur_limit}
        
        args = {
            "stream_mode": "values",
            "config": config,
        }
        
        # Add callbacks if provided
        if callbacks:
            if "callbacks" not in config:
                config["callbacks"] = []
            if isinstance(callbacks, list):
                config["callbacks"].extend(callbacks)
            else:
                config["callbacks"].append(callbacks)
        
        return args
