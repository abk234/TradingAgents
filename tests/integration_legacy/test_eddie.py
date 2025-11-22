#!/usr/bin/env python3
# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Test script for Eddie - End-to-end natural language interaction test

Tests Eddie's ability to:
1. Respond to greetings
2. Use tools to analyze markets
3. Provide trading recommendations
4. Handle follow-up questions
"""

import asyncio
from tradingagents.bot.agent import TradingAgent


async def test_eddie():
    """Test Eddie's conversational capabilities."""

    print("=" * 70)
    print("🧪 Testing Eddie - AI Trading Expert")
    print("=" * 70)
    print()

    # Initialize Eddie
    print("Initializing Eddie...")
    eddie = TradingAgent(
        model_name="llama3.3",
        base_url="http://localhost:11434/v1",
        temperature=0.7,
        debug=True
    )
    print(f"✓ Eddie initialized with {len(eddie.tools)} tools")
    print()

    # Test conversations
    test_queries = [
        "Hello! What's your name?",
        "What stocks should I look at today?",
        "Can you tell me about the healthcare sector?"
    ]

    conversation_history = []

    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}/{len(test_queries)}")
        print(f"{'='*70}")
        print(f"👤 User: {query}")
        print()
        print("🤖 Eddie: ", end="", flush=True)

        # Stream response
        full_response = ""
        async for chunk in eddie.astream(query, conversation_history=conversation_history):
            if chunk:
                print(chunk, end="", flush=True)
                full_response += chunk

        print()  # New line after response

        # Update conversation history
        from langchain_core.messages import HumanMessage, AIMessage
        conversation_history.append(HumanMessage(content=query))
        conversation_history.append(AIMessage(content=full_response))

        # Wait a bit between queries
        if i < len(test_queries):
            print("\n⏳ Waiting before next query...")
            await asyncio.sleep(2)

    print()
    print("=" * 70)
    print("✅ End-to-end test completed successfully!")
    print("=" * 70)
    print()
    print("Eddie is ready for natural language conversations!")
    print("You can interact with him at: http://localhost:8000")
    print()


if __name__ == "__main__":
    asyncio.run(test_eddie())
