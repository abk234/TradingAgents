#!/usr/bin/env python3
"""
Simple test to verify LangGraph agent streams properly
"""
import asyncio
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from langchain.tools import tool

# Create a simple test tool
@tool
def get_weather(city: str) -> str:
    """Get the weather for a city"""
    return f"The weather in {city} is sunny and 72°F"

async def test_simple():
    print("Testing simple LangGraph agent...")

    # Simple LLM
    llm = ChatOpenAI(
        model="llama3.3",
        base_url="http://localhost:11434/v1",
        api_key="ollama",
        temperature=0
    )

    # Simple tool list
    tools = [get_weather]

    # Create agent with simple prompt
    agent = create_react_agent(
        llm,
        tools,
        state_modifier="You are a helpful assistant. Use tools when needed to answer questions."
    )

    # Test message that should trigger tool use
    message = "What's the weather in San Francisco?"
    print(f"\nQuestion: {message}\n")

    inputs = {"messages": [HumanMessage(content=message)]}

    print("Streaming chunks:\n" + "="*60)
    async for chunk in agent.astream(inputs):
        if isinstance(chunk, dict) and 'agent' in chunk:
            if 'messages' in chunk['agent']:
                for msg in chunk['agent']['messages']:
                    if hasattr(msg, 'content') and msg.content:
                        print(f"Content: {msg.content}")
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        print(f"Tool calls: {[tc['name'] for tc in msg.tool_calls]}")

if __name__ == "__main__":
    asyncio.run(test_simple())
