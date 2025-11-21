#!/usr/bin/env python3
"""
Test script to understand LangGraph output format
"""
import asyncio
import sys
import os

# Add the project to path
sys.path.insert(0, os.path.dirname(__file__))

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from tradingagents.bot.tools import get_all_tools
from tradingagents.bot.prompts import TRADING_EXPERT_PROMPT

async def test_langgraph():
    print("=" * 80)
    print("Testing LangGraph Output Format")
    print("=" * 80)

    # Initialize LLM
    llm = ChatOpenAI(
        model="llama3.3",
        base_url="http://localhost:11434/v1",
        api_key="ollama",
        temperature=0.7,
        timeout=120
    )

    # Get tools
    tools = get_all_tools()
    print(f"\n✅ Loaded {len(tools)} tools")

    # Create agent
    agent = create_react_agent(llm, tools, prompt=TRADING_EXPERT_PROMPT)
    print("✅ Created ReAct agent")

    # Test message
    message = "What is the current price of AAPL?"
    print(f"\n📝 Test message: {message}")

    # Prepare inputs
    inputs = {
        "messages": [HumanMessage(content=message)]
    }

    print("\n" + "=" * 80)
    print("Streaming chunks from LangGraph:")
    print("=" * 80)

    chunk_count = 0
    async for chunk in agent.astream(inputs):
        chunk_count += 1
        print(f"\n--- Chunk {chunk_count} ---")
        print(f"Type: {type(chunk)}")

        if isinstance(chunk, dict):
            print(f"Keys: {list(chunk.keys())}")

            for key, value in chunk.items():
                print(f"\n  Key '{key}':")
                print(f"    Type: {type(value)}")

                if isinstance(value, dict):
                    print(f"    Dict keys: {list(value.keys())}")

                    # Check for messages
                    if 'messages' in value:
                        msgs = value['messages']
                        print(f"    Has 'messages': count={len(msgs)}")

                        for i, msg in enumerate(msgs):
                            print(f"      Message {i}: type={type(msg).__name__}")
                            if hasattr(msg, 'content'):
                                content_preview = str(msg.content)[:100]
                                print(f"        Content preview: {content_preview}")
                            if hasattr(msg, 'tool_calls'):
                                print(f"        Tool calls: {msg.tool_calls}")

                elif isinstance(value, list):
                    print(f"    List length: {len(value)}")
                    for i, item in enumerate(value[:3]):  # Show first 3 items
                        print(f"      Item {i}: type={type(item).__name__}")

                elif hasattr(value, '__dict__'):
                    print(f"    Object attributes: {list(vars(value).keys())[:5]}")

        # Limit to first 5 chunks for testing
        if chunk_count >= 5:
            print("\n... (stopping after 5 chunks for testing)")
            break

    print(f"\n✅ Total chunks received: {chunk_count}")

if __name__ == "__main__":
    asyncio.run(test_langgraph())
