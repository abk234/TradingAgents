# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TradingAgents is a multi-agent LLM-powered financial trading framework that mirrors real-world trading firms. It uses specialized AI agents (Analysts, Researchers, Traders, Risk Managers) to collaboratively evaluate market conditions and inform trading decisions via LangGraph orchestration.

**Key Architecture Principle**: The system follows a 3-phase workflow:
1. **Screening Phase**: Scan tickers, calculate indicators, generate priority scores (stored in `daily_scans`)
2. **Analysis Phase**: Run 13+ specialized agents across 5 teams for deep analysis (stored in `analyses`)
3. **Decision Phase**: Apply Four-Gate validation framework with profitability enhancements

## Development Commands

### Environment Setup
```bash
# Create virtual environment
conda create -n tradingagents python=3.13
conda activate tradingagents

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys (OPENAI_API_KEY, ALPHA_VANTAGE_API_KEY)
```

### Running the System

**CLI Interface** (Interactive):
```bash
python -m cli.main
```

**Phase-by-Phase Testing** (Recommended for understanding data flow):
```bash
# Phase 1: Run screener to find opportunities
./scripts/phase1_screening.sh

# Phase 2: Run full agent analysis on a ticker
./scripts/phase2_agents.sh AAPL

# Phase 3: View stored analysis reports
./scripts/phase3_reports.sh AAPL

# Phase 4: Full end-to-end workflow
./scripts/phase4_full_workflow.sh
```

**Quick Commands**:
```bash
# Fast screener (no news, optimized)
./quick_run.sh screener-fast

# Analyze specific stock
./quick_run.sh analyze NVDA

# Morning briefing
./quick_run.sh morning

# Portfolio performance
./quick_run.sh portfolio
```

**Profit-Making Workflow**:
```bash
# Full profit optimization workflow
./make_profit.sh --portfolio-value 100000 --top 5

# Fast mode
./make_profit.sh --fast
```

**Package Usage** (Python):
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Create custom config
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "gpt-4o-mini"
config["quick_think_llm"] = "gpt-4o-mini"

# Initialize graph
ta = TradingAgentsGraph(debug=True, config=config, enable_rag=True)

# Run analysis (stores to database if store_analysis=True)
_, decision = ta.propagate("NVDA", "2024-05-10", store_analysis=True)
```

### Testing
```bash
# Run validation suite
python validate_system_data_flow.py

# Test profitability features
python test_profitability_features.py

# Test specific components
python test_eddie.py  # Natural language interface
python test_langfuse_monitoring.py  # Observability
```

### Database Operations
```bash
# Initialize database with watchlist
python scripts/init_database.py

# Check database state
./scripts/show_database_state.sh

# Backup database
./scripts/backup_database.sh
```

## Architecture Overview

### Multi-Agent System (LangGraph)

**Agent Teams** (orchestrated via `TradingAgentsGraph`):

1. **Analyst Team** (parallel execution):
   - `market_analyst.py`: Technical analysis (MACD, RSI, moving averages)
   - `social_media_analyst.py`: Sentiment from Reddit, social platforms
   - `news_analyst.py`: Global news and macroeconomic events
   - `fundamentals_analyst.py`: Financial statements, metrics

2. **Research Team** (sequential debate):
   - `bull_researcher.py`: Identifies upside potential
   - `bear_researcher.py`: Identifies risks and downside
   - `research_manager.py`: Synthesizes debate into recommendation

3. **Trader Agent**:
   - `trader.py`: Makes trading decisions (BUY/SELL/HOLD/WAIT) based on all inputs

4. **Risk Management Team** (sequential debate):
   - `aggressive_debator.py`: High-risk, high-reward perspective
   - `conservative_debator.py`: Risk-averse perspective
   - `neutral_debator.py`: Balanced perspective
   - `risk_manager.py` (Portfolio Manager): Final decision approval

### Core Modules

**`tradingagents/graph/`** - LangGraph orchestration:
- `trading_graph.py`: Main graph setup, agent coordination, RAG integration
- `propagation.py`: State initialization and propagation logic
- `conditional_logic.py`: Graph routing decisions
- `setup.py`: Graph construction and node wiring
- `signal_processing.py`: Signal extraction from agent outputs

**`tradingagents/decision/`** - Four-Gate validation framework:
- `four_gate.py`: 4-gate system (Trend, Value, Timing, Risk)
- `validation_gates.py`: Gate-specific validation logic
- `market_regime.py`: Bull/bear/volatility regime detection
- `sector_rotation.py`: Sector strength analysis

**`tradingagents/rag/`** - Historical context retrieval:
- `embeddings.py`: Generate embeddings for analyses
- `context_retriever.py`: Query ChromaDB for similar past analyses
- `prompt_formatter.py`: Format RAG context into prompts

**`tradingagents/database/`** - PostgreSQL operations:
- `connection.py`: Database connection management
- `ticker_ops.py`: Watchlist CRUD operations
- `scan_ops.py`: Daily screener results
- `analysis_ops.py`: Agent analysis storage/retrieval
- `portfolio_ops.py`: Portfolio tracking
- `rag_ops.py`: Vector embeddings storage

**`tradingagents/screener/`** - Opportunity identification:
- `screener.py`: Main screening logic
- `indicators.py`: Technical indicator calculation
- `scorer.py`: Priority score generation
- `sector_analyzer.py`: Sector-based screening

**`tradingagents/dataflows/`** - Data vendor abstraction:
- `config.py`: Vendor routing logic
- `yfinance.py`, `alpha_vantage.py`: Data source implementations
- Tool categories: `core_stock_apis`, `technical_indicators`, `fundamental_data`, `news_data`

### Configuration System

**`tradingagents/default_config.py`**:
- LLM provider selection: `openai`, `google` (Gemini), `anthropic` (Claude), `ollama`
- Data vendor routing (category-level and tool-level)
- Validation settings (price staleness, multi-source validation, earnings proximity)
- Profitability features (regime detection, sector rotation, correlation checks)

**Key config patterns**:
```python
config["llm_provider"] = "ollama"  # or "openai", "google", "anthropic"
config["deep_think_llm"] = "llama3.3"  # Complex reasoning
config["quick_think_llm"] = "llama3.1"  # Fast operations

# Data vendor routing (category-level)
config["data_vendors"] = {
    "core_stock_apis": "yfinance",
    "fundamental_data": "alpha_vantage",
    "news_data": "skip",  # Skip to avoid OpenAI fallback
}

# Override specific tools (tool-level)
config["tool_vendors"] = {
    "get_news": "skip",
}

# Profitability features (enabled by default)
config["enable_profitability_features"] = True
config["enable_regime_detection"] = True
config["enable_sector_rotation"] = True
```

### Database Schema

**Key Tables**:
- `tickers`: Watchlist management (symbol, sector, industry, priority_tier)
- `daily_scans`: Screener results (priority_score, technical_signals JSONB, triggered_alerts)
- `analyses`: Agent outputs (final_decision, confidence_score, reports as JSONB, embeddings vector)
- `daily_prices`: Historical OHLCV + indicators (ma_20, ma_50, rsi_14)
- `portfolio_positions`: Active holdings
- `portfolio_transactions`: Trade history

**Important**: The database is the system's memory. Always check `analyses` table for historical context before running new analyses.

### LLM Provider Support

**Supported Providers** (via LangChain):
- **OpenAI**: `gpt-4o`, `gpt-4o-mini`, `o3-mini`, `o4-mini`
- **Google Gemini**: `gemini-2.0-flash-lite`, `gemini-2.0-flash`, `gemini-2.5-flash`
- **Anthropic Claude**: `claude-3-5-haiku-latest`, `claude-3-5-sonnet-latest`
- **Ollama** (local): `llama3.1`, `llama3.3`, `mistral`, `qwen2.5`

**Provider Selection Pattern** (in `trading_graph.py:108-155`):
```python
if config["llm_provider"] == "ollama":
    llm = ChatOpenAI(base_url=config["backend_url"], model_name=model)
elif config["llm_provider"] == "openai":
    llm = ChatOpenAI(model_name=model)
elif config["llm_provider"] == "google":
    llm = ChatGoogleGenerativeAI(model=model)
elif config["llm_provider"] == "anthropic":
    llm = ChatAnthropic(model=model)
```

### Data Vendor Abstraction

**Tool Routing** (in `agents/utils/agent_utils.py`):
- Uses `TOOL_TO_CATEGORY` mapping to determine vendor
- Falls back to category-level vendor if tool-level not specified
- Each tool checks `config["tool_vendors"]` then `config["data_vendors"]`

**Adding New Vendor**:
1. Create vendor implementation in `tradingagents/dataflows/`
2. Register in `dataflows/config.py:VENDOR_REGISTRY`
3. Update tool vendor logic in `agents/utils/agent_utils.py`

### Profitability Enhancements

When `enable_profitability_features=True` (default):
- **Market Regime Detection**: Identifies bull/bear/high-volatility periods
- **Sector Rotation**: Tracks sector strength and rotation patterns
- **Correlation Analysis**: Checks portfolio correlation for diversification
- **Four-Gate Framework**: Validates decisions against Trend/Value/Timing/Risk gates

**Access in code**:
```python
from tradingagents.decision import FourGateFramework

gates = FourGateFramework(config)
result = gates.evaluate(ticker, analysis_data, portfolio_context)
```

## Observability & Monitoring

**Langfuse Integration** (optional):
```python
# Enable in config
ta = TradingAgentsGraph(config=config, enable_langfuse=True)

# Or via environment
export LANGFUSE_ENABLED=true
```

**Monitoring module**: `tradingagents/monitoring/langfuse_integration.py`

## Common Patterns

### Running Analysis with RAG
```python
ta = TradingAgentsGraph(enable_rag=True, config=config)
_, decision = ta.propagate("AAPL", "2024-05-10", store_analysis=True)
# RAG automatically retrieves similar past analyses and injects into agent prompts
```

### Custom Analyst Selection
```python
ta = TradingAgentsGraph(
    selected_analysts=["market", "fundamentals"],  # Skip social, news
    config=config
)
```

### Debugging Agent Flow
```python
ta = TradingAgentsGraph(debug=True, config=config)
# Enables verbose logging of agent decisions and state transitions
```

### Accessing Database
```python
from tradingagents.database import get_db_connection

db = get_db_connection()
results = db.execute_dict_query("SELECT * FROM analyses WHERE ticker_id = 1")
```

## Critical Implementation Notes

1. **Agent State Management**: All agent state flows through `AgentState` TypedDict (defined in `agents/utils/agent_states.py`). Never modify state structure without updating all agents.

2. **Debate Rounds**: Research and Risk teams use debate rounds (`max_debate_rounds`, `max_risk_discuss_rounds`). Each round accumulates in `debate_state.history`.

3. **Tool Binding**: Each agent has tools bound via `llm.bind_tools()`. Tools are defined in `agents/utils/*_tools.py`.

4. **Graph Recursion**: Default recursion limit is 100 (`max_recur_limit`). Increase if graph doesn't complete.

5. **Data Caching**: Alpha Vantage responses cached in `dataflows/data_cache/`. Clear with `scripts/cleanup_price_cache.sh`.

6. **Earnings Proximity Warnings**: When `check_earnings_proximity=True`, system warns about analyses near earnings dates (±7 days by default).

7. **Multi-Source Validation**: When `require_multi_source_validation=True`, prices cross-validated between yfinance and Alpha Vantage. Alerts if discrepancy > 2%.

## File Organization Principles

- **Agents**: One file per agent in `tradingagents/agents/{analysts,researchers,risk_mgmt,trader}/`
- **Tools**: Grouped by category in `tradingagents/agents/utils/*_tools.py`
- **Database ops**: Grouped by table in `tradingagents/database/*_ops.py`
- **Scripts**: User-facing scripts in `scripts/`, internal utilities in `tradingagents/`
- **Tests**: Root-level for integration tests, module-level for unit tests

## Known Gotchas

- **Ollama + News**: When using Ollama, set `news_data: "skip"` to avoid OpenAI fallback
- **PostgreSQL Required**: Database operations will fail without PostgreSQL running
- **API Rate Limits**: Alpha Vantage free tier is 25 requests/day. TradingAgents users get 60/min.
- **Debate Rounds = API Calls**: Each debate round is 2-3 LLM calls. Set to 1 for testing.
- **Store Analysis Flag**: Use `store_analysis=True` in `propagate()` to save to database for RAG
- **Virtual Environment**: Always activate venv before running scripts (many scripts auto-activate)

## Phase-by-Phase Workflow Scripts

The `scripts/phase*.sh` scripts are the best way to understand system data flow:
- **phase1_screening.sh**: See how screener populates `daily_scans` table
- **phase2_agents.sh**: See how agents populate `analyses` table
- **phase3_reports.sh**: See how to query and display stored data
- **phase4_full_workflow.sh**: See complete end-to-end execution

When modifying core logic, run these scripts to verify data flow integrity.
