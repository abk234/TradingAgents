#!/usr/bin/env python3
# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
TradingAgents with Ollama - Fast Version (Smaller Models)

This script uses smaller, faster Ollama models for quicker analysis.
Good for testing and rapid iterations.

Prerequisites:
1. Ollama must be running: ollama serve
2. Pull the required model: ollama pull llama3.1
"""

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create config for fast Ollama models
config = DEFAULT_CONFIG.copy()

config["llm_provider"] = "ollama"
config["backend_url"] = "http://localhost:11434/v1"

# Use smaller, faster models (8B parameters instead of 70B)
config["deep_think_llm"] = "llama3.1"  # 8B model - fast and supports tools
config["quick_think_llm"] = "llama3.1"  # Same model for consistency

# Minimal debate rounds for speed
config["max_debate_rounds"] = 1
config["max_risk_discuss_rounds"] = 1

# Use free data sources
config["data_vendors"] = {
    "core_stock_apis": "yfinance",
    "technical_indicators": "yfinance",
    "fundamental_data": "alpha_vantage",
    "news_data": "alpha_vantage",
}

print("="*70)
print("TradingAgents - Fast Mode with Ollama")
print("="*70)
print(f"Model: {config['deep_think_llm']} (8B parameters)")
print(f"Backend: {config['backend_url']}")
print(f"Research Depth: {config['max_debate_rounds']} round (faster)")
print("="*70)
print()

print("Initializing TradingAgents...")
ta = TradingAgentsGraph(debug=True, config=config)

# Run analysis
ticker = "NVDA"
date = "2024-05-10"

print(f"\nAnalyzing {ticker} on {date}...")
print("="*70)
print()

_, decision = ta.propagate(ticker, date)

print("\n" + "="*70)
print("Final Trading Decision:")
print("="*70)
print(decision)
print()
print("="*70)
print("Analysis Complete!")
print("="*70)
