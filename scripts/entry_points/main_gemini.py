"""
Example: Using TradingAgents with Google Gemini API

This example shows how to configure TradingAgents to use Gemini models
instead of OpenAI models. This can be more cost-effective for some use cases.

Prerequisites:
1. Get a Google Gemini API key from: https://aistudio.google.com/app/apikey
2. Set the GOOGLE_API_KEY environment variable or add it to .env file
"""

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create a custom config for Gemini
config = DEFAULT_CONFIG.copy()

# Configure to use Google Gemini models
config["llm_provider"] = "google"  # Use Google/Gemini instead of OpenAI
config["deep_think_llm"] = "gemini-2.0-flash"  # Deep thinking model
config["quick_think_llm"] = "gemini-2.0-flash-lite"  # Quick thinking model (faster, cheaper)
config["max_debate_rounds"] = 1  # Number of debate rounds

# Configure data vendors (default uses yfinance and alpha_vantage)
config["data_vendors"] = {
    "core_stock_apis": "yfinance",           # Options: yfinance, alpha_vantage, local
    "technical_indicators": "yfinance",      # Options: yfinance, alpha_vantage, local
    "fundamental_data": "alpha_vantage",     # Options: openai, alpha_vantage, local
    "news_data": "alpha_vantage",            # Options: openai, alpha_vantage, google, local
}

# Initialize with Gemini config
print("Initializing TradingAgents with Google Gemini models...")
ta = TradingAgentsGraph(debug=True, config=config)

# Run analysis for a ticker and date
print("\nRunning analysis for NVDA on 2024-05-10...")
_, decision = ta.propagate("NVDA", "2024-05-10")
print("\n" + "="*60)
print("Final Trading Decision:")
print("="*60)
print(decision)

# Note: You can also use reflect_and_remember to learn from results
# ta.reflect_and_remember(1000)  # parameter is the position returns

