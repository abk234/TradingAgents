# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TradingAgents is a multi-agent LLM-powered trading framework built with LangGraph. It simulates a real trading firm structure with specialized agents (analysts, researchers, traders, risk managers) that collaboratively evaluate stocks and make trading decisions. The system supports multiple LLM providers (OpenAI, Anthropic, Google Gemini, Ollama) and includes advanced features like RAG-based historical context, PostgreSQL database integration, and a Chainlit-based chat interface ("Eddie").

**Note:** This is a research framework designed for experimentation, not production trading.

## Development Setup

### Environment Setup
```bash
# Create virtual environment
conda create -n tradingagents python=3.13
conda activate tradingagents

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys (OPENAI_API_KEY, ALPHA_VANTAGE_API_KEY required)
```

### Database Setup (Optional but Recommended)
```bash
# Install PostgreSQL 14
brew install postgresql@14
brew services start postgresql@14

# Initialize database
export PATH="/opt/homebrew/opt/postgresql@14/bin:$PATH"
python scripts/init_database.py
```

### Common Commands

#### Running Analysis
```bash
# CLI interface
python -m cli.main

# Python API
python main.py

# Fast mode with Ollama
python main_ollama_fast.py

# With Gemini
python main_gemini.py
```

#### Testing
```bash
# Run basic test
python test.py

# Test improvements
python test_improvements.py

# Test natural language interface
python test_natural_language.py

# Validate high-priority fixes
python validate_high_priority_fixes.py
```

#### Interactive Shell & Bot
```bash
# Launch interactive shell (comprehensive menu system)
./trading_interactive.sh

# Launch Eddie chatbot (Chainlit interface)
./trading_bot.sh
# or
venv/bin/chainlit run tradingagents/bot/chainlit_app.py

# Quick screener run
./run_screener.sh
```

#### Scripts
```bash
# Database backup
./scripts/backup_database.sh

# Daily analysis (cron-ready)
./scripts/run_daily_analysis.sh

# Morning briefing
./scripts/morning_briefing.sh

# Setup automated cron jobs
./scripts/setup_cron.sh

# Evaluate performance
./scripts/evaluate.sh

# Track progress
./scripts/progress_tracker.py watch
```

## Architecture

### Core Components

**1. TradingAgentsGraph** (`tradingagents/graph/trading_graph.py`)
- Main orchestrator class that coordinates all agents
- Implements LangGraph workflow with conditional routing
- Manages LLM initialization (OpenAI, Anthropic, Google, Ollama)
- Integrates RAG system for historical context
- Entry point: `TradingAgentsGraph.propagate(ticker, date)`

**2. Agent System** (`tradingagents/agents/`)
- **analysts/** - Fundamentals, Technical, News, Sentiment analysts
- **researchers/** - Bull/Bear researchers (debate framework)
- **trader/** - Trading decision agent
- **risk_mgmt/** - Risk assessment and portfolio management
- **managers/** - Portfolio manager (final approval)
- Each agent uses specialized tools from `agents/utils/agent_utils.py`

**3. Multi-Source Data Layer** (`tradingagents/dataflows/`)
- **interface.py** - Abstract vendor-agnostic API with caching and metadata tracking:
  - `route_to_vendor()` - Basic vendor routing with fallback
  - `route_to_vendor_with_metadata()` - Returns data + vendor metadata (NEW)
  - `route_to_vendor_with_cache()` - Automatic price caching (NEW - 10x faster repeat analyses)
- **y_finance.py** - yfinance implementation (default for prices/technicals)
- **alpha_vantage.py** - Alpha Vantage implementation (default for fundamentals/news)
- **local.py** - Cached data for offline/testing
- **openai.py**, **google.py** - LLM-based data extraction
- Configuration via `default_config.py` → `data_vendors` dict
- **Price Caching**: Automatic caching of stock prices (5min realtime, 24hr EOD, permanent historical)

**4. RAG System** (`tradingagents/rag/`)
- **EmbeddingGenerator** - Creates embeddings for historical analyses
- **ContextRetriever** - Fetches relevant past decisions
- **PromptFormatter** - Augments prompts with historical context
- Stores/retrieves from PostgreSQL via `database/rag_ops.py`

**5. Database Layer** (`tradingagents/database/`)
- **connection.py** - DatabaseConnection singleton with connection pooling
- **ticker_ops.py** - Stock metadata operations (includes `get_or_create_ticker()` helper)
- **portfolio_ops.py** - Position tracking, transactions
- **analysis_ops.py** - Store analysis results with LLM tracking support
- **price_cache_ops.py** - Price caching operations (NEW - reduces API calls by 80%)
- **rag_ops.py** - Embeddings and similarity search
- **scan_ops.py** - Screener results storage

**6. Decision Framework** (`tradingagents/decision/`)
- **FourGateFramework** - Multi-gate validation system:
  - Data Freshness Gate
  - Multi-Source Validation Gate
  - Earnings Proximity Gate
  - External Intelligence Gate (future)
- **validation_gates.py** - Comprehensive validation gate system (NEW):
  - `DataFreshnessGate` - Validates data recency
  - `MultiSourceValidationGate` - Cross-validates prices across vendors
  - `EarningsProximityGate` - Warns about earnings volatility periods
  - `ValidationGateOrchestrator` - Runs all gates and aggregates results
- Enhances credibility with cross-validation

**7. Screener** (`tradingagents/screener/`)
- Sector-based stock screening
- Technical indicator analysis (MACD, RSI, Bollinger Bands)
- Priority scoring algorithm
- Fast mode for quick scans

**8. Eddie Bot** (`tradingagents/bot/`)
- **chainlit_app.py** - Chainlit chat interface
- **agent.py** - Natural language command routing
- **tools.py** - Extensive tool library (70+ tools)
- **prompts.py** - System prompts and templates
- Supports conversational stock analysis and screening

**9. Orchestration** (`tradingagents/orchestration/`)
- High-level orchestration for batch operations
- Quick analysis modes for faster execution

**10. Data Validation** (`tradingagents/utils/`)
- **data_validator.py** - Comprehensive data quality checks (NEW):
  - Stock data validation (completeness, freshness)
  - Price consistency validation (cross-source)
  - Price reasonableness checks (range, change %)
  - Volume validation
  - Fundamentals validation

### Data Flow

```
User Request
    ↓
TradingAgentsGraph.propagate(ticker, date)
    ↓
Data Layer (dataflows/interface.py)
    ↓ [checks cache first, then fetches via configured vendor]
    ↓ [caches results for future use]
    ↓
Data Validation (data_validator.py) - NEW
    ↓ [validates freshness, consistency, reasonableness]
    ↓
Analyst Agents (parallel execution)
    ↓ [fundamental, technical, news, sentiment]
    ↓ [LLM prompts/responses tracked]
    ↓
Researcher Debate (bull vs bear)
    ↓ [max_debate_rounds iterations]
    ↓
Trader Decision
    ↓
Risk Management Assessment
    ↓
Portfolio Manager Approval
    ↓
Validation Gates (validation_gates.py) - NEW
    ↓ [data freshness, multi-source, earnings proximity]
    ↓
Decision + Four Gate Validation
    ↓ [stores LLM tracking data]
    ↓ [optional RAG storage]
    ↓
Database/Results Storage
```

### Configuration System

All configuration lives in `tradingagents/default_config.py`:

```python
DEFAULT_CONFIG = {
    # LLM settings
    "llm_provider": "ollama",  # openai, anthropic, google, ollama
    "deep_think_llm": "llama3.3",
    "quick_think_llm": "llama3.1",
    "backend_url": "http://localhost:11434/v1",

    # Data vendors (category-level)
    "data_vendors": {
        "core_stock_apis": "yfinance",
        "technical_indicators": "yfinance",
        "fundamental_data": "yfinance",  # or alpha_vantage
        "news_data": "alpha_vantage",
    },

    # Validation gates
    "validation": {
        "enable_price_staleness_check": True,
        "require_multi_source_validation": True,
        "check_earnings_proximity": True,
        # ... more gates
    },

    # Debate rounds
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
}
```

Override in your code:
```python
from tradingagents.default_config import DEFAULT_CONFIG
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "gpt-4o"
ta = TradingAgentsGraph(config=config)
```

## Key Design Patterns

### 1. Vendor Abstraction
The framework uses an abstract data interface (`dataflows/interface.py`) to support multiple data sources. To add a new vendor:
- Implement functions in `dataflows/your_vendor.py`
- Update `dataflows/interface.py` routing logic
- Configure via `DEFAULT_CONFIG["data_vendors"]`

### 2. Agent Tools
Agents access data via centralized tool functions in `agents/utils/agent_utils.py`:
- `get_stock_data()`, `get_indicators()`, `get_fundamentals()`, `get_news()`
- These route to the configured vendor via `dataflows/interface.py`
- **Use `route_to_vendor_with_cache()` for automatic caching** (10x faster repeat analyses)
- Never call vendor-specific functions directly from agents

### 3. State Management
LangGraph uses typed state objects:
- `AgentState` - Main workflow state
- `InvestDebateState` - Researcher debate state
- `RiskDebateState` - Risk management discussion state

### 4. Database Access
Always use connection pooling:
```python
from tradingagents.database import get_db_connection
db = get_db_connection()  # Singleton pattern
ticker_ops = TickerOperations(db)

# Use helper methods when available
ticker_id = ticker_ops.get_or_create_ticker(
    symbol="AAPL",
    company_name="Apple Inc.",
    sector="Technology"
)
```

### 5. Price Caching
Use cached data fetching for better performance:
```python
from tradingagents.dataflows.interface import route_to_vendor_with_cache

# Automatic cache check and store
data = route_to_vendor_with_cache("get_stock_data", "AAPL", start_date, end_date)
# First call: fetches from API and caches
# Subsequent calls: instant cache hit (<0.1s vs 2-5s)
```

### 6. Data Validation
Validate data quality before analysis:
```python
from tradingagents.utils.data_validator import DataValidator

validator = DataValidator(config=DEFAULT_CONFIG)
results = validator.validate_all(ticker="AAPL", data_dict={
    "stock_data": csv_string,
    "prices": {"yfinance": 150.25, "alpha_vantage": 150.30},
    "fundamentals": {...},
    "current_price": 150.25,
    "volume": 50000000
})
summary = validator.get_validation_summary(results)
```

### 7. Validation Gates
Run validation gates before trading decisions:
```python
from tradingagents.decision.validation_gates import ValidationGateOrchestrator

orchestrator = ValidationGateOrchestrator(config=DEFAULT_CONFIG)
results = orchestrator.validate_all("AAPL", {
    "data_timestamp": datetime.now(),
    "prices": {"yfinance": 150.25, "alpha_vantage": 150.30},
    "earnings_date": date(2024, 11, 25),
    "analysis_date": date.today()
})
overall = orchestrator.get_overall_result(results)
```

### 8. Async/Streaming in Bot
Eddie bot uses async throughout:
- `chainlit_app.py` - All handlers are async
- Streaming responses with `cl.Message().stream_token()`
- Timeout handling with `asyncio.wait_for()`

## Important Conventions

### Data Fetching
- **Default sources**: yfinance (price/technical), Alpha Vantage (fundamentals/news)
- **Caching**: 
  - **Price caching**: Automatic database caching via `price_cache` table (NEW)
    - Realtime data: 5 minutes expiration
    - Recent EOD data: 24 hours expiration
    - Historical data: Never expires
  - **File caching**: Data cached in `tradingagents/dataflows/data_cache/` (legacy)
- **Date format**: Always use `YYYY-MM-DD` strings
- **Ticker format**: Uppercase (e.g., "AAPL", "NVDA")
- **Performance**: Use `route_to_vendor_with_cache()` for 10x faster repeat analyses

### Environment Variables
Required:
- `OPENAI_API_KEY` - For OpenAI models
- `ALPHA_VANTAGE_API_KEY` - For fundamental/news data

Optional:
- `GOOGLE_API_KEY` - For Gemini models
- `ANTHROPIC_API_KEY` - For Claude models
- `TRADINGAGENTS_RESULTS_DIR` - Custom results directory
- See `.env.example` for notification/portfolio settings

### Logging
```python
import logging
logger = logging.getLogger(__name__)
logger.info("✓ Success message")
logger.warning("⚠ Warning message")
logger.error("✗ Error message")
```

### Database Schema
Key tables:
- `tickers` - Stock metadata
- `analyses` - Historical analysis results (includes `llm_prompts`, `llm_responses`, `llm_metadata` JSONB columns)
- `price_cache` - Cached stock price data (NEW - reduces API calls by 80%)
- `portfolio_positions` - Current holdings
- `transactions` - Trade history
- `embeddings` - RAG vector storage
- `scan_results` - Screener output

**Database Migrations:**
- `012_add_price_cache.sql` - Creates `price_cache` table with indexes
- `013_add_llm_tracking.sql` - Adds LLM tracking columns to `analyses` table

## Testing & Validation

### Running Tests
```bash
# Quick validation
python test.py

# Comprehensive test suite
python test_improvements.py
python test_core_improvements.py
python test_natural_language.py

# Validate specific fixes
python validate_high_priority_fixes.py

# Test caching implementation
python test_caching_implementation.py

# Validate system data flow
python validate_system_data_flow.py
python validate_data_accuracy.py
python validate_agents.py
python validate_screener.py
```

### Common Issues

**1. Ollama not running**
```bash
ollama list  # Check if running
ollama pull llama3.3  # Download model
```

**2. Database connection errors**
```bash
# Check PostgreSQL status
brew services list | grep postgresql

# Restart if needed
brew services restart postgresql@14

# Verify connection
psql -d investment_intelligence -c "SELECT 1;"
```

**3. Alpha Vantage rate limits**
- Free tier: 25 requests/day
- TradingAgents users: 60 requests/minute (no daily limit)
- Switch to yfinance: `config["data_vendors"]["fundamental_data"] = "yfinance"`

**4. Async timeout errors in bot**
- Default timeout: 120 seconds for analysis
- Adjust in `bot/chainlit_app.py`: `asyncio.wait_for(task, timeout=X)`

## Important Notes

### Data Quality
- **DataValidator**: Comprehensive validation layer (`tradingagents/utils/data_validator.py`)
  - Validates stock data completeness and freshness
  - Cross-validates prices across multiple sources
  - Checks price reasonableness and volume thresholds
- **Validation Gates**: Systematic quality checks (`tradingagents/decision/validation_gates.py`)
  - Data Freshness Gate: Ensures data is recent enough
  - Multi-Source Validation Gate: Cross-validates prices (2% threshold)
  - Earnings Proximity Gate: Warns about earnings volatility periods
- The framework includes multi-source validation (`validation.require_multi_source_validation`)
- Earnings proximity warnings help avoid volatile periods
- Data staleness checks ensure fresh information
- **Vendor Metadata Tracking**: Track which vendor provided data and when fallbacks occurred

### LLM Costs
- Framework makes **many** API calls (analyst team + debate rounds)
- For testing: Use `o4-mini` or Ollama models
- For production: Consider `gpt-4o` or Claude for deep thinking

### Performance
- **Price Caching**: Automatic database caching provides 10x faster repeat analyses
  - First analysis: 2-5 seconds (fetch + cache)
  - Subsequent analyses: <0.1 seconds (cache hit)
  - API call reduction: 80% fewer calls for repeated tickers
- Fast mode: Skip RAG lookups, reduce debate rounds
- Sector-first screening: Analyze top sectors only
- Database caching: Reduces redundant data fetches
- **Cache cleanup**: Automated via `scripts/cleanup_price_cache.sh` (cron-ready)

### Security
- Never commit `.env` file
- Use app passwords for Gmail notifications
- Rotate API keys regularly

## Recent Updates (2025-11-17)

### Major Features Added

1. **Price Caching System** ✅
   - Automatic database caching of stock prices
   - 10x faster repeat analyses
   - 80% reduction in API calls
   - See `CACHING_IMPLEMENTATION_COMPLETE.md` for details

2. **LLM Tracking** ✅
   - Full audit trail of all LLM prompts and responses
   - Tracks tokens, costs, and duration per agent
   - Stored in `analyses.llm_prompts`, `llm_responses`, `llm_metadata` columns

3. **Data Validation Layer** ✅
   - `DataValidator` class for comprehensive data quality checks
   - Validates freshness, consistency, reasonableness
   - See `tradingagents/utils/data_validator.py`

4. **Validation Gates System** ✅
   - Systematic data quality gates before trading decisions
   - Data freshness, multi-source validation, earnings proximity checks
   - See `tradingagents/decision/validation_gates.py`

5. **Vendor Metadata Tracking** ✅
   - Track which vendor provided data
   - Monitor fallback occurrences
   - Audit trail for data sources

6. **Database Improvements** ✅
   - Added `get_or_create_ticker()` helper method
   - Fixed connection pool statistics handling
   - Enhanced error handling

### Performance Improvements
- **10x faster** repeat analyses (price caching)
- **80% fewer** API calls for repeated tickers
- **Sub-second** response times for cached data
- **Full LLM audit trail** for debugging and optimization

## Documentation References

For detailed feature guides, see:
- `README.md` - Overview and installation
- `QUICK_START.md` - Getting started quickly
- `BOT_GUIDE.md` - Eddie chatbot usage
- `SCREENER_GUIDE.md` - Understanding screener metrics
- `INTERACTIVE_SHELL_GUIDE.md` - Interactive menu system
- `EVALUATION_AND_DATABASE_ACCESS.md` - Database usage
- `CACHING_IMPLEMENTATION_COMPLETE.md` - Price caching details
- `FIXES_IMPLEMENTED_SUMMARY.md` - Recent fixes and improvements
