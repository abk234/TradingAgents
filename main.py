from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create a custom config
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "gpt-4o-mini"  # Use a different model
config["quick_think_llm"] = "gpt-4o-mini"  # Use a different model
config["max_debate_rounds"] = 1  # Increase debate rounds

# Configure data vendors (default uses yfinance and alpha_vantage)
config["data_vendors"] = {
    "core_stock_apis": "yfinance",           # Options: yfinance, alpha_vantage, local
    "technical_indicators": "yfinance",      # Options: yfinance, alpha_vantage, local
    "fundamental_data": "alpha_vantage",     # Options: openai, alpha_vantage, local
    "news_data": "alpha_vantage",            # Options: openai, alpha_vantage, google, local
}

# ✅ Profitability Features are ENABLED by default in DEFAULT_CONFIG
# Adjust portfolio value to match your actual portfolio
config["portfolio_value"] = 100000  # Change this to your portfolio value

# Initialize with custom config
ta = TradingAgentsGraph(debug=True, config=config)

# forward propagate - profitability enhancements automatically applied
_, decision = ta.propagate("NVDA", "2024-05-10", store_analysis=True)
print(decision)

# Access profitability enhancements (if available)
# Enhancements are automatically included in the analysis

# Memorize mistakes and reflect
# ta.reflect_and_remember(1000) # parameter is the position returns
