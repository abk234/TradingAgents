"""
Token tracking middleware for TradingAgents.

Tracks token usage across agent execution for cost monitoring and optimization.
"""

from typing import Dict, Any, List
from langchain_core.tools import BaseTool
from .base import TradingMiddleware
from .token_tracker import TokenTracker
import logging

logger = logging.getLogger(__name__)


class TokenTrackingMiddleware(TradingMiddleware):
    """
    Middleware for tracking token usage across agent execution.
    
    This middleware tracks token counts for each agent and adds them
    to the state for monitoring and cost analysis.
    """
    
    def __init__(self, model: str = "gpt-4o", track_per_agent: bool = True):
        """
        Initialize token tracking middleware.
        
        Args:
            model: Model name for token encoding (default: gpt-4o)
            track_per_agent: Whether to track tokens per agent (default: True)
        """
        self.model = model
        self.track_per_agent = track_per_agent
        self.tracker = TokenTracker(model=model)
        logger.info(f"Initialized TokenTrackingMiddleware (model: {model})")
    
    @property
    def tools(self) -> List[BaseTool]:
        """No tools provided by this middleware."""
        return []
    
    def modify_prompt(self, prompt: str, agent_type: str) -> str:
        """No prompt modification needed."""
        return prompt
    
    def pre_process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """No pre-processing needed."""
        return state
    
    def post_process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track tokens after agent execution.
        
        Args:
            state: Current agent state
        
        Returns:
            State with token counts added
        """
        # Determine agent name from state
        agent_name = state.get("sender", "unknown_agent")
        if agent_name == "unknown_agent":
            # Try to infer from state structure
            if state.get("market_report"):
                agent_name = "market_analyst"
            elif state.get("investment_plan"):
                agent_name = "research_manager"
            elif state.get("trader_investment_plan"):
                agent_name = "trader"
            elif state.get("final_trade_decision"):
                agent_name = "portfolio_manager"
        
        # Track tokens for this agent
        if self.track_per_agent:
            agent_tokens = self.tracker.track_agent_tokens(agent_name, state)
            state["_agent_token_count"] = agent_tokens
            state["_agent_name"] = agent_name
        
        # Add total token count
        total_tokens = self.tracker.get_total_tokens()
        state["_total_tokens"] = total_tokens
        
        # Add token summary to state
        if "_token_summary" not in state:
            state["_token_summary"] = {}
        
        state["_token_summary"][agent_name] = {
            "tokens": self.tracker.token_counts.get(agent_name, 0),
            "total": total_tokens
        }
        
        logger.debug(f"Token tracking: {agent_name} = {self.tracker.token_counts.get(agent_name, 0)} tokens, total = {total_tokens}")
        
        return state
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get token usage summary.
        
        Returns:
            Dictionary with token counts and totals
        """
        return self.tracker.get_summary()
    
    def reset(self):
        """Reset token tracking."""
        self.tracker.reset()

