"""
TradingAgents Conversational Agent

LangGraph-based ReAct agent for intelligent trading assistance.
"""

from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
import logging

from .tools import get_all_tools
from .prompts import TRADING_EXPERT_PROMPT

logger = logging.getLogger(__name__)


class TradingAgent:
    """
    Conversational AI agent for trading analysis and recommendations.

    Uses LangGraph's ReAct pattern to combine reasoning with tool usage.
    """

    def __init__(
        self,
        model_name: str = "llama3.3",
        base_url: str = "http://localhost:11434/v1",
        temperature: float = 0.7,
        debug: bool = False
    ):
        """
        Initialize the trading agent.

        Args:
            model_name: LLM model to use (default: llama3.3 via Ollama)
            base_url: API endpoint for LLM (default: Ollama local)
            temperature: Sampling temperature (default: 0.7)
            debug: Enable debug logging (default: False)
        """
        self.debug = debug

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model_name,
            base_url=base_url,
            api_key="ollama",  # Dummy key for Ollama
            temperature=temperature,
            timeout=120  # 2 minute timeout for tool calls
        )

        # Get all tools
        self.tools = get_all_tools()

        # Create ReAct agent with tools
        self.agent = create_react_agent(
            self.llm,
            self.tools,
            prompt=TRADING_EXPERT_PROMPT
        )

        logger.info(f"✓ TradingAgent initialized with {len(self.tools)} tools")

    def chat(self, message: str, conversation_history: Optional[list] = None) -> str:
        """
        Process a user message and return the agent's response.

        Args:
            message: User's message/question
            conversation_history: Previous messages for context (optional)

        Returns:
            Agent's response string
        """
        try:
            # Build input with history
            inputs = {
                "messages": conversation_history or []
            }

            # Add current message
            from langchain_core.messages import HumanMessage
            inputs["messages"].append(HumanMessage(content=message))

            if self.debug:
                logger.info(f"User: {message}")

            # Invoke agent
            result = self.agent.invoke(inputs)

            # Extract response
            response = result["messages"][-1].content

            if self.debug:
                logger.info(f"Agent: {response}")

            return response

        except Exception as e:
            logger.error(f"Error in agent.chat: {e}")
            return f"I encountered an error: {str(e)}\n\nPlease try rephrasing your question or being more specific."

    async def astream(self, message: str, conversation_history: Optional[list] = None):
        """
        Stream agent responses asynchronously (for Chainlit).

        Args:
            message: User's message/question
            conversation_history: Previous messages for context (optional)

        Yields:
            Chunks of the agent's response
        """
        try:
            # Build input
            inputs = {
                "messages": conversation_history or []
            }

            # Add current message
            from langchain_core.messages import HumanMessage
            inputs["messages"].append(HumanMessage(content=message))

            # Stream response
            async for chunk in self.agent.astream(inputs):
                # Extract content from the chunk
                if "messages" in chunk and len(chunk["messages"]) > 0:
                    last_message = chunk["messages"][-1]
                    if hasattr(last_message, 'content'):
                        yield last_message.content

        except Exception as e:
            logger.error(f"Error in agent.astream: {e}")
            yield f"Error: {str(e)}"

    def get_conversation_state(self) -> Dict[str, Any]:
        """
        Get current state of the conversation.

        Returns:
            Dictionary with conversation state
        """
        return {
            "tools_available": len(self.tools),
            "model": self.llm.model_name,
            "ready": True
        }


# Convenience function for quick testing
def create_agent(debug: bool = False) -> TradingAgent:
    """
    Create a TradingAgent instance with default settings.

    Args:
        debug: Enable debug logging

    Returns:
        Initialized TradingAgent
    """
    return TradingAgent(debug=debug)
