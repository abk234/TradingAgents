# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Sub-agent delegation middleware for TradingAgents.

Enables dynamic spawning of isolated sub-agents for specialized tasks.
"""

from typing import List, Dict, Any, Optional, Callable
from langchain_core.tools import tool, BaseTool
from datetime import date
import logging

from .base import TradingMiddleware

logger = logging.getLogger(__name__)

# Try to import TradingAgentsGraph for sub-agent creation
try:
    from tradingagents.graph.trading_graph import TradingAgentsGraph
    TRADING_GRAPH_AVAILABLE = True
except ImportError:
    TRADING_GRAPH_AVAILABLE = False
    TradingAgentsGraph = None


class SubAgentDefinition:
    """Definition of a sub-agent that can be spawned."""
    
    def __init__(
        self,
        name: str,
        description: str,
        analyst_types: List[str],
        prompt: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        Initialize sub-agent definition.
        
        Args:
            name: Name of the sub-agent
            description: Description of what this sub-agent does
            analyst_types: List of analyst types to include (e.g., ["market"], ["fundamentals"])
            prompt: Optional custom prompt
            model: Optional custom model (defaults to main agent model)
        """
        self.name = name
        self.description = description
        self.analyst_types = analyst_types
        self.prompt = prompt
        self.model = model


# Default sub-agent definitions
DEFAULT_SUBAGENTS = {
    "market_analyst": SubAgentDefinition(
        name="market_analyst",
        description="Specialized agent for technical analysis (charts, indicators, trends)",
        analyst_types=["market"]
    ),
    "fundamentals_analyst": SubAgentDefinition(
        name="fundamentals_analyst",
        description="Specialized agent for fundamental analysis (financials, ratios, company health)",
        analyst_types=["fundamentals"]
    ),
    "news_analyst": SubAgentDefinition(
        name="news_analyst",
        description="Specialized agent for news and sentiment analysis",
        analyst_types=["news"]
    ),
    "social_analyst": SubAgentDefinition(
        name="social_analyst",
        description="Specialized agent for social media sentiment analysis",
        analyst_types=["social"]
    ),
    "technical_only": SubAgentDefinition(
        name="technical_only",
        description="Quick technical analysis (market analyst only)",
        analyst_types=["market"]
    ),
    "fundamentals_only": SubAgentDefinition(
        name="fundamentals_only",
        description="Quick fundamentals check (fundamentals analyst only)",
        analyst_types=["fundamentals"]
    ),
}


def create_subagent_graph(
    subagent_def: SubAgentDefinition,
    config: Dict[str, Any],
    enable_rag: bool = False
) -> Optional[Any]:
    """
    Create a TradingAgentsGraph instance for a sub-agent.
    
    Args:
        subagent_def: Sub-agent definition
        config: Configuration dictionary
        enable_rag: Whether to enable RAG (default: False for isolation)
    
    Returns:
        TradingAgentsGraph instance or None if not available
    """
    if not TRADING_GRAPH_AVAILABLE or not TradingAgentsGraph:
        logger.warning("TradingAgentsGraph not available for sub-agent creation")
        return None
    
    try:
        graph = TradingAgentsGraph(
            selected_analysts=subagent_def.analyst_types,
            debug=False,
            config=config,
            enable_rag=enable_rag,
            enable_token_tracking=False,  # Don't double-track tokens
            enable_summarization=False,  # Sub-agents are already focused
            enable_todo_lists=False,  # Keep sub-agents simple
            enable_filesystem=False
        )
        return graph
    except Exception as e:
        logger.error(f"Error creating sub-agent graph: {e}")
        return None


def create_delegate_tool(config: Dict[str, Any] = None):
    """
    Create delegate_to_subagent tool with config access.
    
    Args:
        config: Configuration dictionary for sub-agent creation
    
    Returns:
        Tool instance
    """
    from tradingagents.default_config import DEFAULT_CONFIG
    tool_config = config or DEFAULT_CONFIG
    
    @tool
    def delegate_to_subagent(
        task: str,
        subagent_type: str,
        ticker: str = None,
        context: Dict[str, Any] = None
    ) -> str:
        """
        Delegate a task to a specialized sub-agent with isolated context.
    
    Use this when:
    - You need specialized analysis (e.g., only technical, only fundamentals)
    - You want faster results (single analyst vs full team)
    - You need isolated context (sub-agent doesn't see full conversation)
    - You want to parallelize work (spawn multiple sub-agents)
    
    Do NOT use for:
    - Simple queries that don't need analysis
    - Tasks that can be done with existing tools
    - When full analysis is already running
    
    Available sub-agent types:
    - "market_analyst": Technical analysis (charts, indicators)
    - "fundamentals_analyst": Fundamental analysis (financials, ratios)
    - "news_analyst": News and sentiment analysis
    - "social_analyst": Social media sentiment
    - "technical_only": Quick technical check (alias for market_analyst)
    - "fundamentals_only": Quick fundamentals check (alias for fundamentals_analyst)
    
    Args:
        task: Description of the task to delegate (e.g., "Analyze NVDA technical indicators")
        subagent_type: Type of sub-agent to use (see available types above)
        ticker: Optional ticker symbol (extracted from task if not provided)
        context: Optional context dictionary to pass to sub-agent
    
    Returns:
        Result from sub-agent analysis
        """
        # This will be called by agents, but we need access to config
        # In practice, this would be injected via middleware context
        # For now, we'll use a simplified approach
        
        if not TRADING_GRAPH_AVAILABLE:
            return "❌ Error: Sub-agent delegation not available (TradingAgentsGraph not imported)"
        
        # Get sub-agent definition
        subagent_def = DEFAULT_SUBAGENTS.get(subagent_type)
        if not subagent_def:
            available = ", ".join(DEFAULT_SUBAGENTS.keys())
            return f"❌ Error: Unknown sub-agent type '{subagent_type}'. Available: {available}"
        
        # Extract ticker from task if not provided
        if not ticker:
            # Simple extraction - look for common ticker patterns
            import re
            ticker_match = re.search(r'\b([A-Z]{1,5})\b', task.upper())
            if ticker_match:
                ticker = ticker_match.group(1)
            else:
                return f"❌ Error: Could not extract ticker from task. Please provide ticker parameter."
        
        # Use config from closure
        config = tool_config
        
        # Create sub-agent graph
        graph = create_subagent_graph(subagent_def, config, enable_rag=False)
        if not graph:
            return f"❌ Error: Failed to create sub-agent '{subagent_type}'"
        
        try:
            # Run sub-agent with isolated context
            logger.info(f"🤖 Delegating to sub-agent '{subagent_type}' for {ticker}: {task}")
            
            final_state, decision = graph.propagate(
                company_name=ticker,
                trade_date=date.today(),
                store_analysis=False
            )
            
            # Extract relevant report based on sub-agent type
            if "market" in subagent_def.analyst_types:
                result = final_state.get("market_report", "No market report generated")
            elif "fundamentals" in subagent_def.analyst_types:
                result = final_state.get("fundamentals_report", "No fundamentals report generated")
            elif "news" in subagent_def.analyst_types:
                result = final_state.get("news_report", "No news report generated")
            elif "social" in subagent_def.analyst_types:
                result = final_state.get("sentiment_report", "No sentiment report generated")
            else:
                result = str(final_state.get("final_trade_decision", "Analysis completed"))
            
            logger.info(f"✅ Sub-agent '{subagent_type}' completed for {ticker}")
            
            return f"📊 **{subagent_def.name.upper()} Result for {ticker}:**\n\n{result}"
            
        except Exception as e:
            logger.error(f"Error running sub-agent '{subagent_type}': {e}")
            return f"❌ Error: Sub-agent execution failed: {str(e)}"
    
    return delegate_to_subagent


class SubAgentMiddleware(TradingMiddleware):
    """
    Middleware for dynamic sub-agent delegation.
    
    Enables agents to spawn isolated sub-agents for specialized tasks.
    """
    
    def __init__(
        self,
        subagent_definitions: Optional[Dict[str, SubAgentDefinition]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize sub-agent middleware.
        
        Args:
            subagent_definitions: Optional custom sub-agent definitions
            config: Optional configuration (for sub-agent creation)
        """
        self.subagent_definitions = subagent_definitions or DEFAULT_SUBAGENTS.copy()
        self.config = config
        logger.info(f"Initialized SubAgentMiddleware with {len(self.subagent_definitions)} sub-agents")
    
    @property
    def tools(self) -> List[BaseTool]:
        """Tools provided by this middleware."""
        if TRADING_GRAPH_AVAILABLE:
            # Create tool with config access
            tool = create_delegate_tool(self.config)
            return [tool]
        else:
            logger.warning("Sub-agent tools not available (TradingAgentsGraph not imported)")
            return []
    
    def modify_prompt(self, prompt: str, agent_type: str) -> str:
        """Add sub-agent delegation instructions to prompt."""
        subagent_instructions = """
        
## Sub-Agent Delegation

You can delegate tasks to specialized sub-agents for faster, focused analysis:
- `delegate_to_subagent(task, subagent_type, ticker, context)`: Delegate to a specialized sub-agent

**When to use sub-agents:**
- Need only one type of analysis (e.g., just technical, just fundamentals)
- Want faster results (single analyst vs full team)
- Need isolated context (sub-agent doesn't see full conversation)
- Want to parallelize work (spawn multiple sub-agents simultaneously)

**When NOT to use sub-agents:**
- Simple queries that don't need analysis
- Tasks that can be done with existing tools
- When full analysis is already running
- For quick lookups (use tools instead)

**Available Sub-Agent Types:**
- `market_analyst`: Technical analysis (charts, indicators, trends)
- `fundamentals_analyst`: Fundamental analysis (financials, ratios, company health)
- `news_analyst`: News and sentiment analysis
- `social_analyst`: Social media sentiment analysis
- `technical_only`: Quick technical check (alias)
- `fundamentals_only`: Quick fundamentals check (alias)

**Example Usage:**
- "Get technical analysis for NVDA": `delegate_to_subagent("Analyze NVDA technical indicators", "market_analyst", "NVDA")`
- "Check fundamentals": `delegate_to_subagent("Analyze AAPL fundamentals", "fundamentals_analyst", "AAPL")`
- "What's the news sentiment?": `delegate_to_subagent("Analyze MSFT news sentiment", "news_analyst", "MSFT")`

**Benefits:**
- Faster execution (5-15 seconds vs 30-90 seconds)
- Isolated context (fresh analysis)
- Cost efficient (only run needed analysts)
- Can parallelize (spawn multiple simultaneously)
"""
        return prompt + subagent_instructions
    
    def pre_process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """No pre-processing needed."""
        return state
    
    def post_process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """No post-processing needed."""
        return state
    
    def register_subagent(self, definition: SubAgentDefinition):
        """Register a custom sub-agent definition."""
        self.subagent_definitions[definition.name] = definition
        logger.info(f"Registered custom sub-agent: {definition.name}")
    
    def get_available_subagents(self) -> List[str]:
        """Get list of available sub-agent types."""
        return list(self.subagent_definitions.keys())

