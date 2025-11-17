"""
Chainlit Chat Interface for TradingAgents Bot

Web-based conversational interface for the trading assistant.
"""

import chainlit as cl
from chainlit.input_widget import Select, Slider
import logging
from typing import Optional

from tradingagents.bot.agent import TradingAgent
from tradingagents.bot.prompts import WELCOME_MESSAGE

logger = logging.getLogger(__name__)

# Global agent instance
agent: Optional[TradingAgent] = None


@cl.on_chat_start
async def start():
    """Initialize the chat session."""
    global agent

    # Show welcome message
    await cl.Message(
        content=WELCOME_MESSAGE,
        author="Eddie"
    ).send()

    # Initialize agent
    try:
        agent = TradingAgent(
            model_name="llama3.3",
            base_url="http://localhost:11434/v1",
            temperature=0.7,
            debug=False
        )

        # Store in session
        cl.user_session.set("agent", agent)
        cl.user_session.set("conversation_history", [])

        # Show system info
        await cl.Message(
            content="✓ Agent ready with access to all TradingAgents tools and data",
            author="System"
        ).send()

    except Exception as e:
        logger.error(f"Error initializing agent: {e}")
        await cl.Message(
            content=f"⚠️ Error initializing agent: {str(e)}\n\nPlease ensure Ollama is running and llama3.3 is available.",
            author="System"
        ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming user messages."""
    # Get agent from session
    agent = cl.user_session.get("agent")

    if not agent:
        await cl.Message(
            content="⚠️ Agent not initialized. Please refresh the page.",
            author="System"
        ).send()
        return

    # Get conversation history
    history = cl.user_session.get("conversation_history", [])

    try:
        # Show thinking indicator
        thinking_msg = await cl.Message(
            content="🤔 Thinking...",
            author="Eddie"
        ).send()
        
        # Create placeholder for response
        msg = cl.Message(content="", author="Eddie")

        # Stream response with timeout handling
        import asyncio
        
        # Create a task for the async generator
        async def stream_with_timeout():
            chunks_received = 0
            has_content = False
            full_response = ""
            
            try:
                logger.info(f"Starting astream for message: {message.content[:50]}...")
                
                async for chunk in agent.astream(message.content, conversation_history=history):
                    if chunk:
                        # Clean up chunk (remove None, empty strings)
                        chunk_str = str(chunk).strip() if chunk else ""
                        if chunk_str:
                            logger.debug(f"Received chunk: {chunk_str[:50]}...")
                            await msg.stream_token(chunk_str)
                            full_response += chunk_str
                            chunks_received += 1
                            has_content = True
                
                logger.info(f"Streaming completed. Chunks: {chunks_received}, Has content: {has_content}")
                
                # If no chunks received, get response synchronously as fallback
                if not has_content:
                    logger.warning("No chunks received from astream, trying synchronous chat")
                    response = agent.chat(message.content, conversation_history=history)
                    if response:
                        logger.info(f"Fallback chat returned {len(response)} characters")
                        await msg.stream_token(response)
                        full_response = response
                        has_content = True
                
                return chunks_received, has_content, full_response
            except Exception as stream_error:
                logger.error(f"Error in streaming: {stream_error}", exc_info=True)
                # Fallback to synchronous chat
                try:
                    logger.info("Attempting fallback to synchronous chat")
                    response = agent.chat(message.content, conversation_history=history)
                    if response:
                        logger.info(f"Fallback chat returned {len(response)} characters")
                        await msg.stream_token(response)
                        return 1, True, response
                    else:
                        logger.error("Fallback chat returned empty response")
                        return 0, False, ""
                except Exception as chat_error:
                    logger.error(f"Error in fallback chat: {chat_error}", exc_info=True)
                    raise stream_error
        
        try:
            # Run with timeout (reduced to 60 seconds for faster feedback)
            chunks_received, has_content, full_response = await asyncio.wait_for(stream_with_timeout(), timeout=60.0)  # 60 second timeout

            logger.info(f"Stream completed. Chunks: {chunks_received}, Has content: {has_content}, Response length: {len(full_response) if full_response else 0}")

            # Only send if we have content
            if has_content and full_response:
                # Send final message
                await msg.send()
                logger.info("Message sent successfully")
            else:
                # If no content, send a helpful message
                logger.warning("No content received, sending fallback message")
                await msg.stream_token("I received your message but didn't generate a response. ")
                await msg.stream_token("Please try rephrasing your question or being more specific.")
                await msg.send()
            
            # Remove thinking indicator
            await thinking_msg.remove()

            # Update history
            from langchain_core.messages import HumanMessage, AIMessage
            history.append(HumanMessage(content=message.content))
            history.append(AIMessage(content=full_response if full_response else msg.content))
            cl.user_session.set("conversation_history", history)
        
        except asyncio.TimeoutError:
            await thinking_msg.remove()
            await cl.Message(
                content="⚠️ Request timed out after 60 seconds.\n\nThe agent may be:\n- Making tool calls that take time\n- Waiting for database/API responses\n- Processing a complex query\n\n**Try:**\n1. Using a simpler query (e.g., \"Hello\" or \"What is your name?\")\n2. Being more specific\n3. Checking if Ollama is running: `curl http://localhost:11434/api/tags`\n4. For stock analysis, try: \"What stocks should I look at?\" (uses screener, faster)",
                author="System"
            ).send()
            logger.error("Request timed out after 60 seconds")

    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        
        # Remove thinking indicator if it exists
        try:
            if 'thinking_msg' in locals():
                await thinking_msg.remove()
        except:
            pass
        
        error_msg = f"⚠️ Error: {str(e)}\n\n"
        
        # Provide helpful error messages
        if "psycopg2" in str(e) or "database" in str(e).lower():
            error_msg += "Database connection issue detected.\n"
            error_msg += "Some features require PostgreSQL database.\n"
            error_msg += "Try simpler queries that don't need database.\n\n"
        elif "aiter" in str(e).lower() or "async" in str(e).lower():
            error_msg += "Async processing error detected.\n"
            error_msg += "Please refresh the page and try again.\n\n"
        
        error_msg += "Try:\n1. Rephrasing your question\n2. Being more specific\n3. Checking if Ollama is running"
        
        await cl.Message(
            content=error_msg,
            author="System"
        ).send()


@cl.on_settings_update
async def setup_agent(settings):
    """Handle settings updates."""
    logger.info(f"Settings updated: {settings}")


# Authentication disabled for local development
# Uncomment and add CHAINLIT_AUTH_SECRET to .env to enable
# @cl.password_auth_callback
# def auth_callback(username: str, password: str):
#     """
#     Optional: Add authentication if needed.
#     """
#     return cl.User(
#         identifier=username,
#         metadata={"role": "user"}
#     )


# Settings for the chat interface
@cl.set_chat_profiles
async def chat_profile():
    """Define chat profiles for different use cases."""
    return [
        cl.ChatProfile(
            name="Standard",
            markdown_description="Standard trading assistant with full capabilities",
            icon="📊",
        ),
        cl.ChatProfile(
            name="Quick Screener",
            markdown_description="Focused on quick market scans and top picks",
            icon="⚡",
        ),
        cl.ChatProfile(
            name="Deep Analysis",
            markdown_description="Detailed AI-powered stock analysis",
            icon="🔍",
        ),
    ]


if __name__ == "__main__":
    # For development testing
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)
