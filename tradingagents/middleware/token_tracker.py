"""
Token counting utilities for TradingAgents.

Provides token counting functionality for cost tracking and optimization.
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logger.warning("tiktoken not available. Using approximate token counting.")


class TokenTracker:
    """
    Track token usage across agent execution.
    
    Provides accurate token counting when tiktoken is available,
    falls back to approximation otherwise.
    """
    
    def __init__(self, model: str = "gpt-4o"):
        """
        Initialize token tracker.
        
        Args:
            model: Model name for encoding (default: gpt-4o)
        """
        self.model = model
        self.token_counts: Dict[str, int] = {}
        self.encoding = None
        
        if TIKTOKEN_AVAILABLE:
            try:
                self.encoding = tiktoken.encoding_for_model(model)
                logger.debug(f"Initialized token tracker with encoding for {model}")
            except Exception as e:
                logger.warning(f"Could not load encoding for {model}: {e}. Using approximation.")
                self.encoding = None
        else:
            logger.info("Using approximate token counting (tiktoken not available)")
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.
        
        Args:
            text: Text to count tokens for
        
        Returns:
            Number of tokens
        """
        if not text:
            return 0
        
        if self.encoding:
            try:
                return len(self.encoding.encode(str(text)))
            except Exception as e:
                logger.warning(f"Error counting tokens with encoding: {e}. Using approximation.")
        
        # Fallback: approximate (4 characters = 1 token)
        return len(str(text)) // 4
    
    def count_state_tokens(self, state: Dict[str, Any], exclude_keys: Optional[List[str]] = None) -> int:
        """
        Count total tokens in state dictionary.
        
        Args:
            state: State dictionary
            exclude_keys: Keys to exclude from counting (e.g., ["_token_count"])
        
        Returns:
            Total token count
        """
        exclude_keys = exclude_keys or []
        total = 0
        
        for key, value in state.items():
            if key in exclude_keys:
                continue
            
            if isinstance(value, str):
                total += self.count_tokens(value)
            elif isinstance(value, dict):
                total += self.count_state_tokens(value, exclude_keys)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        total += self.count_tokens(item)
                    elif isinstance(item, dict):
                        total += self.count_state_tokens(item, exclude_keys)
            elif value is not None:
                # Count string representation of other types
                total += self.count_tokens(str(value))
        
        return total
    
    def track_agent_tokens(self, agent_name: str, state: Dict[str, Any]) -> int:
        """
        Track tokens for a specific agent execution.
        
        Args:
            agent_name: Name of the agent
            state: State after agent execution
        
        Returns:
            Token count for this agent
        """
        tokens = self.count_state_tokens(state, exclude_keys=["_token_count", "_total_tokens"])
        self.token_counts[agent_name] = tokens
        logger.debug(f"Tracked {tokens} tokens for {agent_name}")
        return tokens
    
    def get_total_tokens(self) -> int:
        """Get total tokens tracked across all agents."""
        return sum(self.token_counts.values())
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of token usage.
        
        Returns:
            Dictionary with token counts and totals
        """
        return {
            "agent_counts": self.token_counts.copy(),
            "total": self.get_total_tokens(),
            "agent_count": len(self.token_counts)
        }
    
    def reset(self):
        """Reset token counts."""
        self.token_counts.clear()
        logger.debug("Token tracker reset")

