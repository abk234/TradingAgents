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
        # Create placeholder for response
        msg = cl.Message(content="", author="Eddie")

        # Stream response
        async for chunk in agent.astream(message.content, conversation_history=history):
            if chunk:
                await msg.stream_token(chunk)

        # Send final message
        await msg.send()

        # Update history
        from langchain_core.messages import HumanMessage, AIMessage
        history.append(HumanMessage(content=message.content))
        history.append(AIMessage(content=msg.content))
        cl.user_session.set("conversation_history", history)

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await cl.Message(
            content=f"⚠️ Error: {str(e)}\n\nTry:\n1. Rephrasing your question\n2. Being more specific\n3. Checking if Ollama is running",
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
