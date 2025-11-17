# TradingAgents Setup Guide for Junior Developers

## Overview

**TradingAgents** is a multi-agent LLM-powered financial trading framework that simulates a real-world trading firm. It uses specialized AI agents (analysts, researchers, traders, risk managers) that work together to analyze market conditions and make trading decisions.

### What This Application Does

The framework decomposes complex trading tasks into specialized roles:

1. **Analyst Team**: Analyzes market data, sentiment, news, and fundamentals
2. **Research Team**: Bull and bear researchers debate investment strategies
3. **Trader Agent**: Makes trading decisions based on research
4. **Risk Management Team**: Evaluates and adjusts trading strategies
5. **Portfolio Manager**: Final approval/rejection of trades

## Prerequisites

Before setting up TradingAgents, ensure you have the following:

### 1. System Requirements

- **Python**: Version 3.10 or higher (3.13 recommended)
- **Operating System**: macOS, Linux, or Windows
- **Memory**: At least 4GB RAM (8GB+ recommended)
- **Internet Connection**: Required for API calls and data fetching

### 2. Required API Keys

You'll need API keys from the following services:

#### a. LLM API Key (Required - Choose One)

**Option 1: OpenAI API Key (Default)**
- **Purpose**: Powers all LLM agents in the framework
- **How to get**: 
  1. Go to https://platform.openai.com/
  2. Sign up or log in
  3. Navigate to API Keys section
  4. Create a new secret key
- **Cost**: Pay-per-use (recommended models for testing: `gpt-4o-mini`, `o4-mini` to save costs)
- **Note**: The framework makes **many** API calls, so monitor your usage

**Option 2: Google Gemini API Key (Alternative)**
- **Purpose**: Use Gemini models instead of OpenAI (often more cost-effective)
- **How to get**:
  1. Go to https://aistudio.google.com/app/apikey
  2. Sign in with your Google Account
  3. Click "Get API Key" or "Create API Key"
  4. Select or create a Google Cloud project
  5. Copy your API key
- **Cost**: Free tier available with generous limits
- **Models**: `gemini-2.0-flash-lite`, `gemini-2.0-flash`, `gemini-2.5-flash`, etc.
- **Note**: Set `llm_provider` to `"google"` in your config to use Gemini

#### b. Alpha Vantage API Key (Required for default config)
- **Purpose**: Provides fundamental data and news data
- **How to get**:
  1. Go to https://www.alphavantage.co/support/#api-key
  2. Fill out the form to get a free API key
  3. Free tier has 60 requests/minute with no daily limits (special rate for TradingAgents)
- **Cost**: Free tier available
- **Alternative**: You can configure the app to use OpenAI for these data sources instead

### 3. Python Environment Manager

Choose one of the following:
- **Conda** (recommended): https://www.anaconda.com/download
- **venv**: Built into Python 3.3+
- **virtualenv**: `pip install virtualenv`

## Installation Steps

### Step 1: Clone the Repository

```bash
git clone https://github.com/TauricResearch/TradingAgents.git
cd TradingAgents
```

### Step 2: Create a Virtual Environment

**Using Conda (Recommended):**
```bash
conda create -n tradingagents python=3.13
conda activate tradingagents
```

**Using venv:**
```bash
python3 -m venv tradingagents-env
source tradingagents-env/bin/activate  # On macOS/Linux
# OR
tradingagents-env\Scripts\activate  # On Windows
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: This may take a few minutes as it installs many packages including:
- LangChain and LangGraph (for agent orchestration)
- OpenAI SDK (for LLM interactions)
- Financial data libraries (yfinance, pandas)
- UI libraries (rich, questionary for CLI)

### Step 4: Configure API Keys

You have two options for setting API keys:

#### Option A: Using Environment Variables (Recommended for Development)

**macOS/Linux (OpenAI):**
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
export ALPHA_VANTAGE_API_KEY="your-alpha-vantage-api-key-here"
```

**macOS/Linux (Gemini):**
```bash
export GOOGLE_API_KEY="your-google-api-key-here"
export ALPHA_VANTAGE_API_KEY="your-alpha-vantage-api-key-here"
```

**Windows (PowerShell - OpenAI):**
```powershell
$env:OPENAI_API_KEY="your-openai-api-key-here"
$env:ALPHA_VANTAGE_API_KEY="your-alpha-vantage-api-key-here"
```

**Windows (PowerShell - Gemini):**
```powershell
$env:GOOGLE_API_KEY="your-google-api-key-here"
$env:ALPHA_VANTAGE_API_KEY="your-alpha-vantage-api-key-here"
```

**Windows (Command Prompt - OpenAI):**
```cmd
set OPENAI_API_KEY=your-openai-api-key-here
set ALPHA_VANTAGE_API_KEY=your-alpha-vantage-api-key-here
```

**Windows (Command Prompt - Gemini):**
```cmd
set GOOGLE_API_KEY=your-google-api-key-here
set ALPHA_VANTAGE_API_KEY=your-alpha-vantage-api-key-here
```

#### Option B: Using .env File (Recommended for Production)

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API keys:

**For OpenAI:**
```
OPENAI_API_KEY=your-openai-api-key-here
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-api-key-here
```

**For Gemini:**
```
GOOGLE_API_KEY=your-google-api-key-here
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-api-key-here
```

The application will automatically load these from the `.env` file.

### Step 5: Verify Installation

Test that everything is installed correctly:

```bash
python -c "import tradingagents; print('Installation successful!')"
```

## Running the Application

### Option 1: Interactive CLI (Recommended for Learning)

Run the interactive command-line interface:

```bash
python -m cli.main analyze
```

This will:
1. Show a welcome screen
2. Prompt you to select:
   - Ticker symbol (e.g., "AAPL", "NVDA", "SPY")
   - Analysis date (YYYY-MM-DD format)
   - Which analysts to use
   - Research depth
   - LLM models to use
3. Display a live dashboard showing:
   - Agent progress
   - Tool calls and messages
   - Analysis reports as they're generated
4. Show the complete final report

### Option 2: Programmatic Usage

**Using OpenAI (default):**

Create a Python script (or use the provided `main.py`):

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create configuration
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "gpt-4o-mini"  # Use cheaper model for testing
config["quick_think_llm"] = "gpt-4o-mini"
config["max_debate_rounds"] = 1

# Initialize the trading graph
ta = TradingAgentsGraph(debug=True, config=config)

# Run analysis for a ticker and date
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)
```

**Using Gemini:**

Use the provided `main_gemini.py` or create your own:

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create configuration for Gemini
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "google"  # Use Gemini instead of OpenAI
config["deep_think_llm"] = "gemini-2.0-flash"
config["quick_think_llm"] = "gemini-2.0-flash-lite"  # Faster and cheaper
config["max_debate_rounds"] = 1

# Initialize the trading graph
ta = TradingAgentsGraph(debug=True, config=config)

# Run analysis for a ticker and date
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)
```

Run it:
```bash
python main.py          # For OpenAI
python main_gemini.py   # For Gemini
```

## Understanding the Workflow

When you run an analysis, here's what happens:

1. **Analyst Team** (parallel analysis):
   - Market Analyst: Technical indicators (MACD, RSI, etc.)
   - Social Analyst: Sentiment from Reddit/social media
   - News Analyst: News articles and macroeconomic events
   - Fundamentals Analyst: Company financials and metrics

2. **Research Team** (debate):
   - Bull Researcher: Argues for buying
   - Bear Researcher: Argues against buying
   - Research Manager: Makes final research decision

3. **Trader Agent**:
   - Synthesizes all reports into a trading plan

4. **Risk Management Team** (debate):
   - Risky Analyst: Argues for aggressive strategy
   - Safe Analyst: Argues for conservative strategy
   - Neutral Analyst: Provides balanced view
   - Portfolio Manager: Makes final decision

5. **Final Decision**: Buy, Sell, or Hold recommendation

## Configuration Options

You can customize the application by editing `tradingagents/default_config.py` or creating a custom config:

```python
config = DEFAULT_CONFIG.copy()

# Change LLM provider (OpenAI, Google/Gemini, Anthropic, etc.)
config["llm_provider"] = "google"  # Use Gemini instead of OpenAI

# Change LLM models
# For OpenAI:
config["deep_think_llm"] = "gpt-4o"  # More powerful but expensive
config["quick_think_llm"] = "gpt-4o-mini"  # Faster and cheaper

# For Gemini:
config["deep_think_llm"] = "gemini-2.0-flash"
config["quick_think_llm"] = "gemini-2.0-flash-lite"  # Faster and cheaper

# Adjust debate rounds (more rounds = more thorough but slower)
config["max_debate_rounds"] = 2
config["max_risk_discuss_rounds"] = 2

# Change data vendors
config["data_vendors"] = {
    "core_stock_apis": "yfinance",  # Free, no API key needed
    "technical_indicators": "yfinance",
    "fundamental_data": "alpha_vantage",  # Requires API key
    "news_data": "alpha_vantage",  # Requires API key
}
```

## Common Issues and Solutions

### Issue: "ALPHA_VANTAGE_API_KEY environment variable is not set"
**Solution**: Make sure you've set the API key using one of the methods in Step 4.

### Issue: "OpenAI API key not found" or "Google API key not found"
**Solution**: 
- For OpenAI: Set your `OPENAI_API_KEY` environment variable or add it to `.env` file
- For Gemini: Set your `GOOGLE_API_KEY` environment variable or add it to `.env` file
- Make sure you're using the correct API key for your chosen provider

### Issue: Rate limit errors from Alpha Vantage
**Solution**: 
- Wait a minute and try again (free tier: 60 requests/minute)
- Consider upgrading to Alpha Vantage Premium
- Or switch to using OpenAI for data sources (modify config)

### Issue: High API costs
**Solution**: 
- **Switch to Gemini**: Often more cost-effective. Set `llm_provider` to `"google"` and use `gemini-2.0-flash-lite`
- **Use cheaper models**: 
  - OpenAI: `gpt-4o-mini` instead of `gpt-4o`
  - Gemini: `gemini-2.0-flash-lite` for quick tasks
- Reduce `max_debate_rounds` to 1
- Monitor your usage:
  - OpenAI: https://platform.openai.com/usage
  - Gemini: https://aistudio.google.com/

### Issue: Import errors
**Solution**: 
- Make sure you activated your virtual environment
- Reinstall dependencies: `pip install -r requirements.txt --upgrade`

## Project Structure

```
TradingAgents/
├── tradingagents/          # Main package
│   ├── agents/             # Agent implementations
│   │   ├── analysts/       # Market, News, Social, Fundamentals analysts
│   │   ├── researchers/    # Bull and Bear researchers
│   │   ├── trader/         # Trader agent
│   │   ├── managers/       # Research and Risk managers
│   │   └── risk_mgmt/      # Risk management debaters
│   ├── dataflows/          # Data fetching modules
│   │   ├── y_finance.py    # Yahoo Finance integration
│   │   ├── alpha_vantage_*.py  # Alpha Vantage integrations
│   │   └── ...
│   └── graph/              # LangGraph workflow definitions
│       └── trading_graph.py  # Main trading graph
├── cli/                    # Command-line interface
│   └── main.py             # CLI entry point
├── main.py                 # Example programmatic usage
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # Project documentation
```

## Learning Resources

1. **Start Simple**: Run the CLI with default settings on a well-known stock (e.g., "AAPL")
2. **Read the Code**: Start with `main.py` to see basic usage
3. **Explore Agents**: Look at `tradingagents/agents/` to understand each agent's role
4. **Understand the Graph**: Check `tradingagents/graph/trading_graph.py` for workflow
5. **Experiment**: Try different tickers, dates, and configurations

## Next Steps

1. ✅ Complete installation and setup
2. ✅ Run your first analysis using the CLI
3. ✅ Try programmatic usage with `main.py`
4. ✅ Experiment with different configurations
5. ✅ Read the agent code to understand how they work
6. ✅ Modify agents or create custom ones

## Getting Help

- **GitHub Issues**: https://github.com/TauricResearch/TradingAgents/issues
- **Discord**: https://discord.com/invite/hk9PGKShPK
- **Documentation**: See README.md for more details

## Important Notes

⚠️ **This is a research framework, not financial advice!**
- The framework is designed for research and educational purposes
- Trading performance varies based on many factors
- Always do your own research before making real trading decisions
- See the disclaimer: https://tauric.ai/disclaimer/

💰 **Cost Awareness**:
- The framework makes many API calls
- Monitor your OpenAI usage to avoid unexpected charges
- Start with cheaper models (`gpt-4o-mini`) for testing

---

Happy learning! 🚀

