#!/usr/bin/env python3
# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""Test the real TradingAgent with a clear question"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from tradingagents.bot.agent import TradingAgent
from langchain_core.messages import HumanMessage

async def main():
    print("Testing real TradingAgent...")

    agent = TradingAgent(
        model_name="llama3.3",
        base_url="http://localhost:11434/v1",
        debug=True
    )

    # Try a very clear, direct question that should trigger tool use
    message = "Use the run_screener tool to show me the top stocks."
    print(f"\nQuestion: {message}\n")
    print("="*60)

    chunk_count = 0
    full_content = ""

    async for chunk in agent.astream(message):
        chunk_count += 1
        chunk_str = str(chunk)

        # Show first few chunks in detail
        if chunk_count <= 3:
            print(f"\nChunk {chunk_count}: {chunk_str[:200]}")

        full_content += chunk_str

    print("\n" + "="*60)
    print(f"Total chunks: {chunk_count}")
    print(f"Total content length: {len(full_content)}")
    print(f"\nFinal response:\n{full_content[:500]}")

if __name__ == "__main__":
    asyncio.run(main())
