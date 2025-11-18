import os

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_dir": os.getenv("TRADINGAGENTS_DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data")),
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # LLM settings
    # Options: "openai", "google" (Gemini), "anthropic" (Claude), "openrouter", "ollama"
    "llm_provider": "ollama",
    # For Ollama: "llama3.1", "llama3.3", "mistral", "qwen2.5", etc.
    # For OpenAI: "gpt-4o-mini", "gpt-4o", "o4-mini", "o3-mini", etc.
    # For Google/Gemini: "gemini-2.0-flash-lite", "gemini-2.0-flash", "gemini-2.5-flash", etc.
    # For Anthropic: "claude-3-5-haiku-latest", "claude-3-5-sonnet-latest", etc.
    "deep_think_llm": "llama3.3",
    "quick_think_llm": "llama3.1",
    "backend_url": "http://localhost:11434/v1",  # Ollama's OpenAI-compatible endpoint
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    # Data vendor configuration
    # Category-level configuration (default for all tools in category)
    "data_vendors": {
        "core_stock_apis": "yfinance",       # Options: yfinance, alpha_vantage, local
        "technical_indicators": "yfinance",  # Options: yfinance, alpha_vantage, local
        "fundamental_data": "yfinance",      # Options: yfinance, alpha_vantage, local (using yfinance - no API key needed)
        "news_data": "alpha_vantage",        # UPDATED: Use Alpha Vantage for better news coverage and sentiment analysis
    },
    # Validation settings (Eddie's credibility enhancements)
    "validation": {
        # Phase 1: Data Quality
        "enable_price_staleness_check": True,      # ✅ Warn if data is stale
        "max_data_age_minutes": 15,                # ✅ Flag data older than this during market hours
        "show_data_sources": True,                 # ✅ Show which sources were used in analysis

        # Phase 2: Multi-Source Validation & Earnings Risk (ACTIVE!)
        "require_multi_source_validation": True,   # ✅ Cross-validate prices across sources
        "check_earnings_proximity": True,          # ✅ Warn about earnings volatility windows
        "price_discrepancy_threshold": 2.0,        # ✅ Max acceptable price difference (%)
        "earnings_days_before": 7,                 # ✅ Days before earnings to warn
        "earnings_days_after": 3,                  # ✅ Days after earnings to warn

        # Phase 3: External Intelligence (TODO)
        "enable_social_sentiment": False,          # 🔜 Reddit, StockTwits sentiment
        "enable_analyst_consensus": False,         # 🔜 Wall Street consensus comparison
        "enable_insider_tracking": False,          # 🔜 Insider trading detection
    },
    # Tool-level configuration (takes precedence over category-level)
    "tool_vendors": {
        # Example: "get_stock_data": "alpha_vantage",  # Override category default
        # Example: "get_news": "openai",               # Override category default
    },
    # Profitability Features Configuration
    # Enable profitability improvements for enhanced trading performance
    "enable_profitability_features": True,  # ✅ ENABLED: All profitability features active
    "portfolio_value": 10000,  # Portfolio value in USD (adjust to your portfolio size)
    "enable_regime_detection": True,  # Market regime detection (bull/bear/volatility)
    "enable_sector_rotation": True,  # Sector rotation detection
    "enable_correlation_check": True,  # Correlation-based risk management
}
