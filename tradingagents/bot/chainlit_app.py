"""
Chainlit Chat Interface for TradingAgents Bot

Web-based conversational interface for the trading assistant.
"""

import chainlit as cl
from chainlit.input_widget import Select, Slider
import logging
from typing import Optional
import re
import asyncio
from datetime import date

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, AIMessage

from tradingagents.bot.agent import TradingAgent
from tradingagents.bot.prompts import WELCOME_MESSAGE
from tradingagents.bot.ui_components import create_stock_chart
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.propagation import Propagator

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

        # Initialize settings
        settings = await cl.ChatSettings(
            [
                Select(
                    id="Risk Level",
                    label="Risk Tolerance",
                    values=["Conservative", "Moderate", "Aggressive"],
                    initial_index=1,
                ),
                Select(
                    id="Investment Style",
                    label="Investment Style",
                    values=["Value", "Growth", "Momentum", "Dividend"],
                    initial_index=1,
                ),
                Slider(
                    id="Max Positions",
                    label="Max Positions",
                    initial=5,
                    min=1,
                    max=20,
                    step=1,
                ),
            ]
        ).send()
        await setup_agent(settings)

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

    # Check for chart requests
    chart_match = re.search(r"chart\s+(\w+)", message.content, re.IGNORECASE)
    if chart_match:
        ticker = chart_match.group(1).upper()
        
        # Send a loading message
        msg = cl.Message(content=f"Generating chart for {ticker}...")
        await msg.send()
        
        # Generate chart
        chart = create_stock_chart(ticker)
        
        if chart:
            # Update message with chart
            msg.content = f"Here is the chart for {ticker}:"
            msg.elements = [cl.Plotly(name=f"{ticker} Chart", figure=chart, display="inline")]
            await msg.update()
        else:
            msg.content = f"Could not generate chart for {ticker}. Please check if the ticker is valid."
            await msg.update()
            
        return

    # Check for direct analysis requests (optimization)
    analysis_match = re.search(r"^(analyze|research)\s+(\w+)$", message.content.strip(), re.IGNORECASE)
    if analysis_match:
        command = analysis_match.group(1)
        ticker = analysis_match.group(2).upper()
        await run_direct_analysis(ticker)
        return

    try:
        # Show thinking indicator
        thinking_msg = await cl.Message(
            content="🤔 Thinking...",
            author="Eddie"
        ).send()
        
        # Create placeholder for response
        msg = cl.Message(content="", author="Eddie")

        # Stream response with timeout handling
        
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


async def run_direct_analysis(ticker: str):
    """
    Run analysis directly using the graph streaming for better performance and UI feedback.
    Bypasses the ReAct agent loop.
    """
    # Send initial message
    msg = cl.Message(content=f"🚀 Starting fast analysis for **{ticker}**...")
    await msg.send()
    
    # Get settings from session
    settings = cl.user_session.get("settings", {})
    
    # Create config
    config = DEFAULT_CONFIG.copy()
    # Apply settings if available (simplified mapping)
    if settings.get("Risk Level") == "Aggressive":
        config["max_risk_discuss_rounds"] = 1
    elif settings.get("Risk Level") == "Conservative":
        config["max_risk_discuss_rounds"] = 3
        
    # Initialize graph
    graph = TradingAgentsGraph(
        selected_analysts=["market", "social", "news", "fundamentals"],
        config=config,
        enable_rag=True
    )
    
    # Create steps for UI feedback
    steps = {
        "market": cl.Step(name="Market Analyst", type="run"),
        "social": cl.Step(name="Social Analyst", type="run"),
        "news": cl.Step(name="News Analyst", type="run"),
        "fundamentals": cl.Step(name="Fundamentals Analyst", type="run"),
        "research": cl.Step(name="Research Team", type="run"),
        "risk": cl.Step(name="Risk Management", type="run"),
        "trader": cl.Step(name="Trader", type="run"),
    }
    
    # Start all steps initially as "queued" (visual effect)
    # We'll send them as we go
    
    # Run the graph with streaming
    final_state = None
    
    # We need to map graph nodes to our UI steps
    # Node names from the graph definition
    node_map = {
        "market_analyst": "market",
        "social_analyst": "social",
        "news_analyst": "news",
        "fundamentals_analyst": "fundamentals",
        "bull_researcher": "research",
        "bear_researcher": "research",
        "research_manager": "research",
        "risk_manager": "risk", 
        "trader": "trader"
    }
    
    current_step = None
    
    try:
        # Use the propagate logic but stream it
        # We need to manually construct the input for the graph since propagate doesn't stream
        # But we can use graph.stream directly with the initial state
        
        propagator = Propagator()
        
        # Generate context (simplified for direct run)
        historical_context = None
        if graph.enable_rag:
             historical_context = graph._generate_historical_context(ticker)
             
        init_state = propagator.create_initial_state(ticker, date.today(), historical_context)
        
        # Stream execution
        async for event in graph.graph.astream(init_state):
            for node_name, state in event.items():
                # Identify which UI step this node belongs to
                step_key = node_map.get(node_name)
                
                if step_key:
                    step = steps[step_key]
                    
                    # If this is a new step starting
                    if current_step != step:
                        # Finish previous step if exists
                        if current_step:
                            current_step.output = "Done"
                            await current_step.update()
                        
                        # Start new step
                        current_step = step
                        await current_step.send()
                    
                    # Update current step content with a snippet
                    # We can try to extract some meaningful text from the state update
                    if node_name == "market_analyst" and state.get("market_report"):
                        step.output = "Analyzing technical indicators..."
                    elif node_name == "news_analyst" and state.get("news_report"):
                        step.output = "Reading latest news..."
                    
                    await step.update()
                    
                # Capture final state
                final_state = state
        
        # Finish the last step
        if current_step:
            current_step.output = "Done"
            await current_step.update()
            
        # Render Final Report
        if final_state:
            decision = final_state.get("final_trade_decision", "No decision made")
            
            # Create a nice summary
            summary = f"""# 📊 Analysis Report: {ticker}
            
## 🎯 Final Decision
{decision}

## 📈 Analyst Reports
"""
            if final_state.get("market_report"):
                summary += f"\n### Market Analysis\n{final_state['market_report']}\n"
            if final_state.get("news_report"):
                summary += f"\n### News Analysis\n{final_state['news_report']}\n"
            if final_state.get("fundamentals_report"):
                summary += f"\n### Fundamentals\n{final_state['fundamentals_report']}\n"
                
            await cl.Message(content=summary).send()
            
    except Exception as e:
        await cl.Message(content=f"❌ Error during analysis: {str(e)}").send()


@cl.on_settings_update
async def setup_agent(settings):
    """Handle settings updates."""
    logger.info(f"Settings updated: {settings}")
    
    # Store settings in session
    cl.user_session.set("settings", settings)
    
    # Update agent config if needed (placeholder)
    # agent = cl.user_session.get("agent")
    # if agent:
    #     agent.update_config(settings)
    
    await cl.Message(
        content=f"✓ Settings updated: Risk={settings['Risk Level']}, Style={settings['Investment Style']}",
        author="System"
    ).send()


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
