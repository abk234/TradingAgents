"""
Base middleware class for TradingAgents.

Middleware provides a way to extend agent capabilities without modifying
agent code directly. Each middleware can:
- Add tools to agents
- Modify prompts
- Process state before/after agent execution
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from langchain_core.tools import BaseTool
import logging

logger = logging.getLogger(__name__)


class TradingMiddleware(ABC):
    """
    Base class for TradingAgents middleware.
    
    Middleware wraps agents and injects capabilities without modifying
    agent code directly. This enables clean extensibility.
    """
    
    @property
    @abstractmethod
    def tools(self) -> List[BaseTool]:
        """
        Tools this middleware provides to agents.
        
        Returns:
            List of LangChain tools
        """
        pass
    
    def modify_prompt(self, prompt: str, agent_type: str) -> str:
        """
        Modify system prompt for a specific agent type.
        
        Args:
            prompt: Original system prompt
            agent_type: Type of agent (e.g., "market_analyst", "trader")
        
        Returns:
            Modified prompt (default: returns original unchanged)
        """
        return prompt
    
    def pre_process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process state before agent execution.
        
        Args:
            state: Current agent state
        
        Returns:
            Modified state (default: returns original unchanged)
        """
        return state
    
    def post_process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process state after agent execution.
        
        Args:
            state: Current agent state
        
        Returns:
            Modified state (default: returns original unchanged)
        """
        return state
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get middleware configuration.
        
        Returns:
            Configuration dictionary
        """
        return {}
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

