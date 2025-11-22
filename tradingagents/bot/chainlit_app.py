# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Chainlit App for Eddie - AI Trading Expert

Eddie v2.0 conversational interface using Chainlit.
"""

import chainlit as cl
import logging
from typing import Optional, Dict, Any

from tradingagents.bot.conversational_agent import ConversationalAgent
from tradingagents.bot.state_tracker import get_state_tracker, EddieState
from tradingagents.default_config import DEFAULT_CONFIG

logger = logging.getLogger(__name__)

# Initialize agent
_agent: Optional[ConversationalAgent] = None


def get_agent() -> ConversationalAgent:
    """Get or create the conversational agent."""
    global _agent
    if _agent is None:
        _agent = ConversationalAgent(config=DEFAULT_CONFIG)
    return _agent


@cl.on_chat_start
async def on_chat_start():
    """Called when a chat session starts."""
    state_tracker = get_state_tracker()
    state_tracker.set_state(EddieState.IDLE, "Ready to help")
    
    await cl.Message(
        content="👋 **Hello! I'm Eddie, your AI Trading Expert.**\n\n"
                "I can help you with:\n"
                "• Market analysis and stock screening\n"
                "• Deep stock analysis with BUY/SELL/HOLD recommendations\n"
                "• Sector analysis and market trends\n"
                "• Risk management and position sizing\n"
                "• System health checks (v2.0)\n"
                "• Voice synthesis (v2.0)\n"
                "• Web research (v2.0)\n\n"
                "**Try asking:**\n"
                "- 'What are the best stocks right now?'\n"
                "- 'Analyze AAPL for me'\n"
                "- 'Run a system health check for AAPL'\n"
                "- 'I'm worried about my portfolio'\n\n"
                "Let's get started! 🚀"
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming messages."""
    state_tracker = get_state_tracker()
    agent = get_agent()
    
    try:
        # Update state to processing
        state_tracker.set_state(EddieState.PROCESSING, "Processing your request...")
        
        # Get conversation history
        history = []
        async for msg in cl.Message.list():
            if msg.author == "user":
                history.append({"role": "user", "content": msg.content})
            elif msg.author == "assistant":
                history.append({"role": "assistant", "content": msg.content})
        
        # Update state to speaking
        state_tracker.set_state(EddieState.SPEAKING, "Generating response...")
        
        # Get response from agent
        response = await agent.chat(
            message=message.content,
            history=history,
            user_preferences=None,
            prompt_metadata=None
        )
        
        # Update state back to idle
        state_tracker.set_state(EddieState.IDLE, "Ready")
        
        # Send response
        await cl.Message(content=response).send()
        
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        state_tracker.set_state(EddieState.ERROR, f"Error: {str(e)}")
        
        await cl.Message(
            content=f"⚠️ I encountered an error: {str(e)}\n\n"
                    "Please try rephrasing your question or being more specific."
        ).send()


@cl.on_stop
async def on_stop():
    """Called when the user stops the chat."""
    state_tracker = get_state_tracker()
    state_tracker.set_state(EddieState.IDLE, "Session ended")
    logger.info("Chat session ended")

