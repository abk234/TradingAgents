#!/usr/bin/env python3
"""Test agent streaming to understand the format"""
import asyncio
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from langchain.tools import tool

@tool
def get_stock_price(ticker: str) -> str:
    """Get the current stock price for a ticker"""
    prices = {"AAPL": "$150.25", "TSLA": "$245.80", "NVDA": "$495.30"}
    return f"The current price of {ticker} is {prices.get(ticker, '$100.00')}"

async def main():
    llm = ChatOpenAI(
        model="llama3.3",
        base_url="http://localhost:11434/v1",
        api_key="ollama",
        temperature=0
    )

    tools = [get_stock_price]

    # Use prompt parameter like the real agent does
    agent = create_react_agent(
        llm,
        tools,
        prompt="You are a stock assistant. When asked about stock prices, use the get_stock_price tool."
    )

    message = "What is the price of AAPL?"
    inputs = {"messages": [HumanMessage(content=message)]}

    print(f"Question: {message}\n")
    print("="*60)

    chunk_num = 0
    async for chunk in agent.astream(inputs):
        chunk_num += 1
        print(f"\n--- Chunk {chunk_num} ---")

        if isinstance(chunk, dict) and 'agent' in chunk and 'messages' in chunk['agent']:
            for msg in chunk['agent']['messages']:
                msg_type = type(msg).__name__
                print(f"Message type: {msg_type}")

                if hasattr(msg, 'content') and msg.content:
                    print(f"Content: {msg.content[:200]}")

                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    print(f"Tool calls: {msg.tool_calls}")

if __name__ == "__main__":
    asyncio.run(main())
