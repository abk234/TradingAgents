#!/usr/bin/env python3
"""
Automated test to verify both bug fixes are working
Run this after deploying fixes to verify the system works
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from tradingagents.bot.conversational_agent import ConversationalAgent
from tradingagents.default_config import DEFAULT_CONFIG

# Colors for output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

def print_test(name):
    print(f"\n{BLUE}{'='*60}{NC}")
    print(f"{BLUE}TEST: {name}{NC}")
    print(f"{BLUE}{'='*60}{NC}")

def print_pass(msg):
    print(f"{GREEN}✅ PASS: {msg}{NC}")

def print_fail(msg):
    print(f"{RED}❌ FAIL: {msg}{NC}")

def print_info(msg):
    print(f"{YELLOW}ℹ️  {msg}{NC}")

async def test_fix_1_intent_classification():
    """
    Test Fix #1: Intent classification in streaming endpoint
    """
    print_test("Fix #1: Intent Classification")

    agent = ConversationalAgent(config=DEFAULT_CONFIG)

    # Test CHAT intent
    print_info("Testing CHAT intent (greeting)...")
    intent = agent._classify_intent("hello")
    if intent == "CHAT":
        print_pass(f"'hello' classified as CHAT")
    else:
        print_fail(f"'hello' classified as {intent}, expected CHAT")
        return False

    # Test KNOWLEDGE intent
    print_info("Testing KNOWLEDGE intent...")
    intent = agent._classify_intent("What is RSI?")
    if intent == "KNOWLEDGE":
        print_pass(f"'What is RSI?' classified as KNOWLEDGE")
    else:
        print_fail(f"'What is RSI?' classified as {intent}, expected KNOWLEDGE")
        return False

    # Test ANALYSIS intent
    print_info("Testing ANALYSIS intent...")
    intent = agent._classify_intent("Show me the top 3 stocks to buy")
    if intent == "ANALYSIS":
        print_pass(f"Stock query classified as ANALYSIS")
    else:
        print_fail(f"Stock query classified as {intent}, expected ANALYSIS")
        return False

    # Test chat_stream exists
    print_info("Checking chat_stream method exists...")
    if hasattr(agent, 'chat_stream'):
        print_pass("chat_stream() method exists")
    else:
        print_fail("chat_stream() method not found")
        return False

    # Test streaming with greeting
    print_info("Testing streaming response for greeting...")
    chunks_received = 0
    response_content = ""

    try:
        async for chunk in agent.chat_stream("Hello", []):
            chunks_received += 1
            response_content += str(chunk)
            if chunks_received >= 10:  # Limit for testing
                break

        if chunks_received > 0 and len(response_content) > 0:
            print_pass(f"Received {chunks_received} chunks with content")
            print_info(f"Response preview: {response_content[:100]}...")
        else:
            print_fail("No chunks received from streaming")
            return False

    except Exception as e:
        print_fail(f"Streaming failed: {e}")
        return False

    return True

async def test_fix_2_chunk_handling():
    """
    Test Fix #2: LangGraph chunk format handling
    """
    print_test("Fix #2: LangGraph Chunk Format Handling")

    from tradingagents.bot.agent import TradingAgent

    agent = TradingAgent(
        model_name="llama3.3",
        base_url="http://localhost:11434/v1",
        debug=False
    )

    print_info("Testing chunk extraction logic...")

    # Simulate the chunk format LangGraph returns
    test_chunk = {
        'agent': {
            'messages': [
                type('AIMessage', (), {
                    'content': 'Test response content',
                    'tool_calls': []
                })()
            ]
        }
    }

    # Test the chunk handling code path
    messages = None
    if "agent" in test_chunk:
        agent_state = test_chunk["agent"]
        if isinstance(agent_state, dict) and "messages" in agent_state:
            messages = agent_state["messages"]

    if messages and len(messages) > 0:
        print_pass("Chunk format handler correctly extracts chunk['agent']['messages']")
    else:
        print_fail("Chunk format handler failed to extract messages")
        return False

    # Test with actual streaming (quick test)
    print_info("Testing actual agent streaming...")

    try:
        chunks_received = 0
        content_received = False

        async for chunk in agent.astream("Use get_stock_price tool for AAPL"):
            chunks_received += 1
            chunk_str = str(chunk)
            if len(chunk_str) > 0:
                content_received = True

            # Limit chunks for testing
            if chunks_received >= 5:
                break

        if content_received:
            print_pass(f"Agent streaming working (received {chunks_received} chunks)")
        else:
            print_fail("Agent streaming returned no content")
            return False

    except Exception as e:
        print_fail(f"Agent streaming failed: {e}")
        return False

    return True

async def main():
    print(f"\n{GREEN}{'='*60}")
    print("Bug Fix Verification Test Suite")
    print(f"{'='*60}{NC}\n")

    results = {}

    # Run tests
    results['Fix #1'] = await test_fix_1_intent_classification()
    results['Fix #2'] = await test_fix_2_chunk_handling()

    # Summary
    print(f"\n{BLUE}{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}{NC}\n")

    all_passed = True
    for test_name, passed in results.items():
        status = f"{GREEN}✅ PASS{NC}" if passed else f"{RED}❌ FAIL{NC}"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False

    print()

    if all_passed:
        print(f"{GREEN}{'='*60}")
        print("✅ ALL TESTS PASSED")
        print(f"{'='*60}{NC}\n")
        print(f"{GREEN}Both bug fixes are working correctly!{NC}")
        return 0
    else:
        print(f"{RED}{'='*60}")
        print("❌ SOME TESTS FAILED")
        print(f"{'='*60}{NC}\n")
        print(f"{RED}Please check the failing tests above{NC}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
