# Phase-by-Phase Workflow Testing Scripts

This directory contains shell scripts to test the end-to-end workflow phase by phase, allowing you to understand how data flows through the system and gets stored in the database.

## Overview

The TradingAgents system has three main phases:

1. **Phase 1: Screening** - Scans all tickers, calculates technical indicators, generates priority scores
2. **Phase 2: Agent Analysis** - Runs full multi-agent analysis (13 agents across 5 teams)
3. **Phase 3: Database Reports** - Queries and displays data from the database

## Scripts

### `phase1_screening.sh`
**Purpose**: Run the daily screener and see how results are stored in the database.

**What it does**:
- Checks database state before screening
- Runs the daily screener (calculates indicators, scores, ranks tickers)
- Shows database state after screening
- Displays top opportunities stored in `daily_scans` table

**Usage**:
```bash
./scripts/phase1_screening.sh
```

**Output**:
- Shows how many tickers were scanned
- Displays priority scores and rankings
- Shows what data is stored in the `daily_scans` table

---

### `phase2_agents.sh [TICKER]`
**Purpose**: Run the full agent analysis workflow and see how results are stored.

**What it does**:
- Verifies ticker exists in database (adds if needed)
- Checks analysis history before running
- Runs full agent analysis:
  - **Analyst Team** (parallel): Market, Social, News, Fundamentals
  - **Research Team** (sequential): Bull Researcher, Bear Researcher, Research Manager
  - **Trading Team**: Trader Agent
  - **Risk Management Team** (sequential): Aggressive, Conservative, Neutral, Portfolio Manager
- Shows database state after analysis
- Displays what data is stored in `analyses` table

**Usage**:
```bash
# Analyze default ticker (AAPL)
./scripts/phase2_agents.sh

# Analyze specific ticker
./scripts/phase2_agents.sh NVDA
./scripts/phase2_agents.sh MSFT
```

**Output**:
- Shows each agent team executing
- Displays final decision and confidence score
- Shows what data is stored in the `analyses` table (including JSONB reports, embeddings, etc.)

---

### `phase3_reports.sh [TICKER]`
**Purpose**: Query and display data from the database.

**What it does**:
- Shows latest screener results (top opportunities)
- Displays analysis history (all tickers or specific ticker)
- Shows database statistics
- Displays full analysis details if ticker is specified

**Usage**:
```bash
# Show all reports
./scripts/phase3_reports.sh

# Show reports for specific ticker
./scripts/phase3_reports.sh AAPL
```

**Output**:
- Top opportunities from screener
- Recent analyses with decisions and confidence scores
- Database statistics (counts, breakdowns)
- Full analysis details (bull case, bear case, catalysts, risks)

---

### `phase4_full_workflow.sh`
**Purpose**: Run all phases sequentially to demonstrate the complete end-to-end workflow.

**What it does**:
1. Runs Phase 1 (Screening)
2. Gets top opportunity from screener
3. Runs Phase 2 (Agent Analysis) on top opportunity
4. Runs Phase 3 (Reports) for that ticker

**Usage**:
```bash
./scripts/phase4_full_workflow.sh
```

**Output**:
- Complete workflow execution
- Shows how screening feeds into analysis
- Demonstrates full data flow

---

### `show_database_state.sh`
**Purpose**: Quick overview of current database state.

**What it does**:
- Shows counts for all main tables
- Displays latest dates
- Shows top opportunities and recent analyses
- Indicates workflow completion status

**Usage**:
```bash
./scripts/show_database_state.sh
```

**Output**:
- Table status (tickers, scans, analyses, prices)
- Workflow completion status
- Recommendations for next steps

---

## Database Tables

### `daily_scans`
Stores screener results:
- `ticker_id`, `scan_date`
- `priority_score` (0-100), `priority_rank`
- `price`, `volume`, `pe_ratio`
- `technical_signals` (JSONB)
- `triggered_alerts` (ARRAY)

### `analyses`
Stores agent analysis results:
- `analysis_id`, `ticker_id`, `analysis_date`
- `final_decision` (BUY/SELL/HOLD/WAIT)
- `confidence_score` (0-100)
- `executive_summary`, `bull_case`, `bear_case`
- `market_report`, `fundamentals_report` (JSONB)
- `sentiment_report`, `news_report` (JSONB)
- `embedding` (vector for RAG)

### `tickers`
Watchlist management:
- `ticker_id`, `symbol`, `company_name`
- `sector`, `industry`
- `active`, `priority_tier`

### `daily_prices`
Historical price data:
- `price_id`, `ticker_id`, `price_date`
- `open`, `high`, `low`, `close`, `volume`
- `ma_20`, `ma_50`, `ma_200`, `rsi_14`

---

## Example Workflow

### Step 1: Run Screening
```bash
./scripts/phase1_screening.sh
```
**Result**: Database populated with scan results in `daily_scans` table.

### Step 2: Analyze Top Opportunity
```bash
# Get top ticker from screener, then analyze it
./scripts/phase2_agents.sh AAPL
```
**Result**: Full analysis stored in `analyses` table with all agent outputs.

### Step 3: View Reports
```bash
./scripts/phase3_reports.sh AAPL
```
**Result**: See all stored data, decisions, and insights.

### Or Run Everything at Once
```bash
./scripts/phase4_full_workflow.sh
```

---

## Understanding the Data Flow

1. **Screening Phase**:
   ```
   Tickers → Price Data → Technical Indicators → Priority Scores → daily_scans table
   ```

2. **Analysis Phase**:
   ```
   Ticker → Agent Teams → Final Decision → analyses table
   ```

3. **Reporting Phase**:
   ```
   Database Tables → Queries → Reports → Display
   ```

---

## Troubleshooting

### Scripts not executable
```bash
chmod +x scripts/*.sh
```

### Virtual environment not activated
The scripts automatically activate the virtual environment if it exists in:
- `venv/` (standard)
- `-/` (alternative)

### Database connection issues
Make sure PostgreSQL is running and configured in your `.env` file.

### No data in database
Run Phase 1 first to populate the screener results, then Phase 2 to populate analyses.

---

## Next Steps

After running these scripts, you can:

1. **Query database directly**:
   ```python
   from tradingagents.database import get_db_connection
   db = get_db_connection()
   results = db.execute_dict_query("SELECT * FROM analyses LIMIT 5")
   ```

2. **Use the CLI tools**:
   ```bash
   python -m tradingagents.screener top 10
   python -m tradingagents.analyze AAPL
   ```

3. **Explore the codebase**:
   - `tradingagents/screener/` - Screening logic
   - `tradingagents/analyze/` - Analysis logic
   - `tradingagents/database/` - Database operations
   - `tradingagents/graph/` - Agent graph orchestration

