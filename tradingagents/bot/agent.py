# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
TradingAgents Conversational Agent

LangGraph-based ReAct agent for intelligent trading assistance.
"""

from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
import logging

from .tools import get_all_tools, get_core_tools
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
        debug: bool = False,
        use_core_tools: bool = False
    ):
        """
        Initialize the trading agent.

        Args:
            model_name: LLM model to use (default: llama3.3 via Ollama)
            base_url: API endpoint for LLM (default: Ollama local)
            temperature: Sampling temperature (default: 0.7)
            debug: Enable debug logging (default: False)
            use_core_tools: Use reduced tool set for smaller models (default: False)
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

        # Get tools - use core set for smaller models if requested
        if use_core_tools:
            self.tools = get_core_tools()
            logger.info(f"Using core tools set ({len(self.tools)} tools) for model {model_name}")
        else:
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
            from langchain_core.messages import HumanMessage, ToolMessage
            inputs["messages"].append(HumanMessage(content=message))

            if self.debug:
                logger.info(f"Starting astream for: {message[:50]}...")

            # Track what we've already yielded to avoid duplication
            previous_content = ""
            chunks_processed = 0
            last_yield_time = None
            
            # Track tool calls and results for fallback response generation
            tool_calls_made = []
            tool_results = []
            final_state_messages = []

            # Stream response with better chunk handling
            async for chunk in self.agent.astream(inputs):
                chunks_processed += 1

                # Debug: Log every chunk in debug mode
                if self.debug and chunks_processed <= 5:
                    logger.info(f"Chunk {chunks_processed} type: {type(chunk)}, keys: {chunk.keys() if isinstance(chunk, dict) else 'N/A'}")
                    if isinstance(chunk, dict):
                        # Log all available keys and their content types
                        for key in chunk.keys():
                            val = chunk[key]
                            logger.info(f"  Key '{key}': type={type(val)}")

                            # If it's a dict, show its keys
                            if isinstance(val, dict):
                                logger.info(f"    Dict keys: {list(val.keys())}")
                                if 'messages' in val:
                                    logger.info(f"    Has messages: count={len(val['messages'])}, types={[type(m).__name__ for m in val['messages']]}")
                            # If it's a list
                            elif isinstance(val, list):
                                logger.info(f"    List count: {len(val)}, types: {[type(m).__name__ for m in val]}")
                            # If it has messages attribute
                            elif hasattr(val, 'messages'):
                                logger.info(f"    Has messages attribute: {len(val.messages)}, types: {[type(m).__name__ for m in val.messages]}")

                # Log progress every 10 chunks
                if chunks_processed % 10 == 0:
                    logger.debug(f"Processed {chunks_processed} chunks...")

                # Handle different chunk formats
                if isinstance(chunk, dict):
                    # LangGraph can return chunks in different formats
                    messages = None

                    # Format 1: Direct messages key
                    if "messages" in chunk and chunk["messages"]:
                        messages = chunk["messages"]
                    # Format 2: Agent dict state with messages
                    elif "agent" in chunk:
                        agent_state = chunk["agent"]
                        if isinstance(agent_state, dict) and "messages" in agent_state:
                            messages = agent_state["messages"]
                        elif hasattr(agent_state, 'messages'):
                            messages = agent_state.messages
                    # Format 3: Other node keys that might contain messages
                    if not messages:
                        for key, value in chunk.items():
                            if isinstance(value, dict) and "messages" in value and value["messages"]:
                                messages = value["messages"]
                                break
                            elif hasattr(value, 'messages') and value.messages:
                                messages = value.messages
                                break

                    # Process messages if found
                    if messages and len(messages) > 0:
                        last_message = messages[-1]
                        final_state_messages = messages  # Keep track of all messages
                        
                        # Handle AIMessage with content
                        if hasattr(last_message, 'content') and last_message.content:
                            current_content = str(last_message.content)
                            
                            # Only yield the new part (incremental)
                            if current_content != previous_content:
                                if current_content.startswith(previous_content):
                                    # Yield only the new portion
                                    new_content = current_content[len(previous_content):]
                                    if new_content.strip():
                                        yield new_content
                                        last_yield_time = chunks_processed
                                else:
                                    # Content changed completely, yield all
                                    if current_content.strip():
                                        yield current_content
                                        last_yield_time = chunks_processed
                                
                                previous_content = current_content
                        
                        # Handle tool calls - yield indicator and track
                        elif hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                            tool_names = [tc.get('name', 'tool') if isinstance(tc, dict) else getattr(tc, 'name', 'tool') for tc in last_message.tool_calls]
                            tool_calls_made.extend(tool_names)
                            yield f"\n\n🔧 Using tools: {', '.join(tool_names)}...\n"
                            last_yield_time = chunks_processed
                        
                        # Track tool results - check message type name
                        elif hasattr(last_message, '__class__') and 'Tool' in last_message.__class__.__name__:
                            tool_name = getattr(last_message, 'name', 'unknown_tool')
                            tool_content = str(getattr(last_message, 'content', ''))[:500]
                            tool_results.append({
                                'name': tool_name,
                                'content': tool_content
                            })
                
                # If we haven't yielded anything in a while, yield a progress indicator
                if last_yield_time and (chunks_processed - last_yield_time) > 50:
                    yield "."
                    last_yield_time = chunks_processed

            if self.debug:
                logger.info(f"Streaming completed. Processed {chunks_processed} chunks, yielded content: {bool(previous_content)}, tools used: {len(tool_calls_made)}")

            # If no content was yielded but tools were used, generate a summary response
            if not previous_content and tool_calls_made:
                logger.warning(f"No content yielded from astream - tools were used: {tool_calls_made}")
                
                # Extract tool results from final state messages if we didn't capture them during streaming
                if not tool_results and final_state_messages:
                    for msg in final_state_messages:
                        if hasattr(msg, '__class__') and 'Tool' in msg.__class__.__name__:
                            tool_name = getattr(msg, 'name', 'unknown_tool')
                            tool_content = str(getattr(msg, 'content', ''))[:500]
                            tool_results.append({
                                'name': tool_name,
                                'content': tool_content
                            })
                
                # Try to generate a summary response based on tool results
                try:
                    # Build a prompt to summarize the tool results
                    summary_prompt = f"""Based on the following tool results, provide a helpful summary response to the user's query: "{message}"

Tools used: {', '.join(set(tool_calls_made))}

Tool results:
"""
                    for i, result in enumerate(tool_results[:5], 1):  # Limit to first 5 results
                        summary_prompt += f"\n{i}. {result['name']}: {result['content'][:400]}...\n"
                    
                    summary_prompt += "\n\nProvide a clear, helpful response summarizing the findings and answering the user's question. Be specific and actionable."
                    
                    # Generate summary using LLM
                    from langchain_core.messages import SystemMessage
                    summary_messages = [
                        SystemMessage(content=TRADING_EXPERT_PROMPT),
                        HumanMessage(content=summary_prompt)
                    ]
                    
                    summary_response = await self.llm.ainvoke(summary_messages)
                    summary_text = summary_response.content if hasattr(summary_response, 'content') else str(summary_response)
                    
                    if summary_text and summary_text.strip():
                        yield f"\n\n{summary_text}"
                    else:
                        # Fallback if LLM doesn't generate content
                        yield f"\n\n✅ I've completed the analysis using {', '.join(set(tool_calls_made))}. "
                        yield "Here's what I found:\n\n"
                        for result in tool_results[:3]:
                            yield f"**{result['name']}**: {result['content'][:200]}...\n\n"
                        yield "\nWould you like me to provide more details on any specific aspect?"
                except Exception as e:
                    logger.error(f"Error generating summary response: {e}", exc_info=True)
                    yield f"\n\n✅ I've completed the analysis using {', '.join(set(tool_calls_made))}. "
                    yield "The tools have finished processing. Would you like me to provide more specific information?"
            
            # If no content and no tools were used, show the original warning
            elif not previous_content:
                logger.warning("No content yielded from astream - no tools were used either")
                yield "\n\n⚠️ Processing complete, but no text response was generated. The agent may have used tools. Try asking a more specific question."

        except Exception as e:
            logger.error(f"Error in agent.astream: {e}", exc_info=True)
            yield f"\n\n⚠️ Error: {str(e)}"

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
