# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

import os

# Fast-mode configuration for quick morning screening
# Optimized for speed: skips news, uses local data, minimal external API calls

FAST_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_dir": "/Users/yluo/Documents/Code/ScAI/FR1-data",
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),

    # LLM settings - Use Ollama for fast local inference
    "llm_provider": "ollama",
    "deep_think_llm": "llama3.3",  # Use Ollama model
    "quick_think_llm": "llama3.1",  # Use Ollama model
    "backend_url": "http://localhost:11434/v1",  # Ollama endpoint

    # Reduced debate rounds for speed
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 0,  # Skip risk discussion in fast mode
    "max_recur_limit": 50,  # Reduced from 100

    # Data vendor configuration - OPTIMIZED FOR SPEED
    # Only use configured vendors, NO automatic fallbacks to alpha_vantage/openai
    "data_vendors": {
        "core_stock_apis": "yfinance",      # Price data from yfinance only
        "technical_indicators": "yfinance",  # Technical indicators from yfinance only
        "fundamental_data": "yfinance",      # Fundamentals from yfinance only
        "news_data": "skip",                 # SKIP NEWS - major speed improvement!
    },

    # Tool-level overrides - explicitly skip slow operations
    "tool_vendors": {
        "get_news": "skip",           # Skip company news
        "get_global_news": "skip",    # Skip global news
        "get_insider_sentiment": "skip",  # Skip insider sentiment
    },

    # Fast mode flags
    "skip_news": True,
    "skip_fundamentals": False,  # Keep fundamentals (fast from yfinance)
    "use_cache": True,
    "cache_ttl_seconds": 3600,  # 1 hour cache
}
