#!/usr/bin/env python3
# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
TradingAgents with Ollama (Local LLMs)

This script runs TradingAgents using local Ollama models for stable,
private, and cost-free AI-powered trading analysis.

Prerequisites:
1. Ollama must be running: ollama serve
2. Required models must be pulled:
   - ollama pull llama3.3
   - ollama pull 0xroyce/plutus
   - ollama pull nomic-embed-text
"""

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Create a custom config for Ollama
config = DEFAULT_CONFIG.copy()

# Configure to use Ollama (local models)
config["llm_provider"] = "ollama"
config["backend_url"] = "http://localhost:11434/v1"

# Model selection - using models that support tool calling
# Note: Models must support function calling for the agent framework to work
# llama3.3 (70B) is excellent for trading analysis and supports tools
config["deep_think_llm"] = "llama3.3"  # 70B model for deep analysis
config["quick_think_llm"] = "llama3.3"  # Also use llama3.3 for consistency (supports tools)

# Reduce debate rounds for faster execution (you can increase for more thorough analysis)
config["max_debate_rounds"] = 1
config["max_risk_discuss_rounds"] = 1

# Configure data vendors (using free/open sources)
config["data_vendors"] = {
    "core_stock_apis": "yfinance",           # Free stock data
    "technical_indicators": "yfinance",      # Free technical indicators
    "fundamental_data": "alpha_vantage",     # Alpha Vantage for fundamentals
    "news_data": "alpha_vantage",            # Alpha Vantage for news
}

print("="*70)
print("TradingAgents - Running with Ollama (Local LLMs)")
print("="*70)
print(f"Deep Thinker Model: {config['deep_think_llm']}")
print(f"Quick Thinker Model: {config['quick_think_llm']}")
print(f"Ollama Backend: {config['backend_url']}")
print(f"Research Depth: {config['max_debate_rounds']} debate round(s)")
print("="*70)
print()

# Initialize with Ollama config
print("Initializing TradingAgents with Ollama models...")
print("(This may take a moment to load models and initialize ChromaDB)")
print()

ta = TradingAgentsGraph(debug=True, config=config)

# Run analysis for a ticker and date
ticker = "NVDA"
date = "2024-05-10"

print(f"\nRunning analysis for {ticker} on {date}...")
print("="*70)
print()

_, decision = ta.propagate(ticker, date)

print("\n" + "="*70)
print("Final Trading Decision:")
print("="*70)
print(decision)
print()

# Note: You can also use reflect_and_remember to learn from results
# ta.reflect_and_remember(1000)  # parameter is the position returns

print("="*70)
print("Analysis Complete!")
print("="*70)
