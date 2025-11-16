# Product Requirements Document: Investment Intelligence System

**Version:** 1.0
**Date:** 2025-11-15
**Status:** Draft
**Owner:** TradingAgents Team

---

## Executive Summary

The Investment Intelligence System (IIS) is an enhancement to the existing TradingAgents framework that transforms it from a single-ticker analysis tool into a comprehensive, intelligent investment platform for long-term investors. The system will enable efficient monitoring of 10-20 stocks across multiple sectors, provide data-driven buy/sell signals, and leverage historical analysis through RAG (Retrieval-Augmented Generation) to improve decision quality over time.

### Key Objectives
- Automate daily screening of 10-20 watchlist tickers
- Provide deep analysis for high-priority opportunities
- Store and learn from historical analyses
- Answer the critical question: "Is NOW the right time to buy?"
- Operate entirely on local infrastructure using Ollama models

---

## Problem Statement

### Current Limitations
1. **Single-Ticker Focus**: TradingAgents can only analyze one company at a time
2. **No Historical Memory**: Each analysis is independent, no learning from past decisions
3. **No Screening Capability**: Cannot efficiently evaluate multiple opportunities
4. **Time Intensive**: Deep analysis of 10+ tickers would take 10+ hours daily
5. **No Buy Timing Optimization**: Lacks framework to determine optimal entry points
6. **No Performance Tracking**: Cannot validate which strategies/patterns work

### User Pain Points
- "I want to monitor 20 stocks but can't spend all day analyzing each one"
- "Did we analyze this stock before? What was our conclusion?"
- "We saw similar market conditions last year - what happened then?"
- "Is this a good entry price or should I wait?"
- "Which of my watchlist stocks deserves attention today?"

---

## User Personas

### Primary Persona: Long-Term Investor
- **Goal**: Build a portfolio of 10-20 quality stocks over 1-3 years
- **Investment Horizon**: 6-24 months per position
- **Decision Style**: Data-driven, patient, seeks value
- **Time Available**: 30-60 minutes daily for market analysis
- **Technical Skill**: Comfortable with Python, CLI tools, local setup
- **Risk Profile**: Moderate, seeks 15-25% annual returns

---

## Goals and Success Criteria

### Business Goals
1. Enable monitoring of 10-20 tickers with <1 hour daily time investment
2. Achieve >70% success rate on buy signals (positive returns at 6 months)
3. Reduce analysis time per ticker from 60 min to 10 min (screener mode)
4. Build institutional memory that improves decision quality over time
5. Provide clear, actionable buy/wait/pass signals with confidence scores

### User Goals
1. Know which stocks deserve attention each day
2. Make informed buy decisions with historical context
3. Avoid repeating past mistakes
4. Track portfolio performance against original thesis
5. Understand what patterns lead to successful investments

### Technical Goals
1. Fully local operation (no cloud dependencies)
2. Leverage existing Ollama models efficiently
3. Sub-second query response for RAG lookups
4. Scalable database design (support 100+ tickers in future)
5. <2 hour runtime for daily workflow (screener + deep analysis)

---

## Feature Requirements

### 1. Three-Tier Analysis System

#### Tier 1: Daily Screener (MUST HAVE)
**Description**: Lightweight automated scan of all watchlist tickers

**Functional Requirements**:
- FR1.1: Scan all watchlist tickers (10-20) every morning
- FR1.2: Calculate priority score (0-100) based on:
  - Price/volume changes vs moving averages (20/50/200 day)
  - Technical indicators: RSI, MACD, Bollinger Bands
  - Support/resistance levels
  - News sentiment snapshot
  - Fundamental metric changes (P/E, growth rates)
- FR1.3: Rank tickers by priority score
- FR1.4: Generate daily report with top 5 opportunities
- FR1.5: Store daily scan results in database
- FR1.6: Flag specific alerts (e.g., "RSI oversold + volume spike")

**Performance Requirements**:
- PR1.1: Complete scan of 20 tickers in <15 minutes
- PR1.2: Use llama3.1 (8B) model for speed
- PR1.3: Minimal data fetching (incremental updates)

**Acceptance Criteria**:
- Can run unattended via cron job
- Produces consistent, actionable priority rankings
- Stores results in PostgreSQL for trend analysis

---

#### Tier 2: Deep Analysis with RAG (MUST HAVE)
**Description**: Comprehensive analysis of high-priority tickers with historical context

**Functional Requirements**:
- FR2.1: Run existing TradingAgents multi-agent system
- FR2.2: Retrieve relevant historical context from database:
  - Previous analyses of same ticker
  - Similar market conditions across all tickers
  - Similar technical setups that led to buy signals
  - Performance data from similar past situations
- FR2.3: Inject historical context into agent prompts
- FR2.4: Generate final decision: BUY / WAIT / PASS
- FR2.5: Calculate confidence score (0-100)
- FR2.6: Provide position sizing recommendation
- FR2.7: Identify key catalysts and risk factors
- FR2.8: Store full analysis + embeddings in database

**RAG Requirements**:
- FR2.9: Semantic search for similar historical analyses
- FR2.10: Pattern matching: "Show times this pattern succeeded/failed"
- FR2.11: Sector comparison: "How does this compare to peers?"
- FR2.12: Temporal analysis: "Is this better entry than last time?"

**Performance Requirements**:
- PR2.1: Complete deep analysis in 30-45 minutes per ticker
- PR2.2: Use llama3.3 (70B) for quality
- PR2.3: RAG queries return results in <1 second

**Acceptance Criteria**:
- Produces actionable buy/wait/pass decision with clear reasoning
- Historical context measurably improves decision quality
- All analysis stored for future reference

---

#### Tier 3: Portfolio Monitoring (SHOULD HAVE)
**Description**: Weekly review of existing positions

**Functional Requirements**:
- FR3.1: Re-analyze all held positions weekly
- FR3.2: Compare current state to entry thesis
- FR3.3: Check stop-loss levels and risk parameters
- FR3.4: Generate HOLD / TRIM / ADD recommendations
- FR3.5: Track performance vs expected returns
- FR3.6: Identify rebalancing opportunities

**Performance Requirements**:
- PR3.1: Complete portfolio review (10 positions) in 30 minutes

**Acceptance Criteria**:
- Alerts when thesis no longer valid
- Tracks portfolio-level metrics
- Suggests rebalancing actions

---

### 2. PostgreSQL + pgvector Database (MUST HAVE)

#### Core Database Schema

**Functional Requirements**:
- FR4.1: Store all ticker metadata (sector, industry, etc.)
- FR4.2: Store daily price/volume data
- FR4.3: Store screening results with timestamps
- FR4.4: Store full analysis outputs as JSON + embeddings
- FR4.5: Store buy/sell signals with reasoning
- FR4.6: Track portfolio actions (buys, sells, holds)
- FR4.7: Track performance metrics over time
- FR4.8: Support vector similarity search (pgvector)

**Database Tables** (detailed schema below):
- `tickers`: Watchlist management
- `daily_prices`: OHLCV historical data
- `daily_scans`: Screening results
- `analyses`: Deep analysis history
- `buy_signals`: Buy/sell signal history
- `portfolio_actions`: Actual trades/decisions
- `performance_tracking`: Return tracking and learning

**Performance Requirements**:
- PR4.1: Support 20 active tickers, 10,000+ historical records
- PR4.2: Query response time <100ms for structured queries
- PR4.3: Vector similarity search <1 second for top 10 results
- PR4.4: Database size <2GB per year of operation

**Acceptance Criteria**:
- All analyses persisted durably
- Fast retrieval for RAG queries
- Supports complex joins and aggregations
- Automated backups configured

---

### 3. Buy Decision Framework (MUST HAVE)

#### Four-Gate Decision System

**Gate 1: Fundamental Value**
- FR5.1: Calculate valuation metrics vs sector
- FR5.2: Assess growth trajectory (revenue, earnings)
- FR5.3: Evaluate balance sheet strength
- FR5.4: Compare to historical averages in DB
- FR5.5: Must pass threshold to proceed

**Gate 2: Technical Entry**
- FR5.6: Confirm not buying at 52-week highs (min 5% pullback)
- FR5.7: Verify support levels holding
- FR5.8: Check volume confirmation
- FR5.9: RAG query: Success rate of similar setups >60%
- FR5.10: Must pass threshold to proceed

**Gate 3: Risk Assessment**
- FR5.11: Risk agents evaluate downside scenarios
- FR5.12: Calculate max expected drawdown
- FR5.13: Verify position sizing appropriate for portfolio
- FR5.14: Compare risk profile to historical similar positions
- FR5.15: Must pass threshold to proceed

**Gate 4: Timing Quality**
- FR5.16: RAG query: "Is this the best entry we've seen?"
- FR5.17: Evaluate opportunity cost of waiting
- FR5.18: Assess catalyst timeline
- FR5.19: Generate timing score (optimization, not blocker)

**Output Requirements**:
- FR5.20: Final decision: BUY / WAIT / PASS
- FR5.21: Confidence score: 0-100
- FR5.22: Entry price target
- FR5.23: Position size recommendation (% of portfolio)
- FR5.24: Expected return and timeline
- FR5.25: Stop-loss level
- FR5.26: Key catalysts identified
- FR5.27: Historical pattern match (similarity score)

**Acceptance Criteria**:
- Clear, explainable decision logic
- All four gates documented in output
- Historical context influences decision
- Conservative by default (false negatives ok, false positives not)

---

### 4. RAG-Enhanced Context Retrieval (MUST HAVE)

**Functional Requirements**:
- FR6.1: Generate embeddings for all analyses using nomic-embed-text
- FR6.2: Semantic search: "Find similar market conditions"
- FR6.3: Pattern search: "Find all times RSI <30 led to buy signal"
- FR6.4: Performance search: "Find buy signals that returned >25%"
- FR6.5: Ticker-specific search: "All previous NVDA analyses"
- FR6.6: Cross-ticker search: "Similar setups in other stocks"
- FR6.7: Temporal search: "Comparing current entry to historical entries"
- FR6.8: Inject top 5 relevant contexts into agent prompts

**Context Types to Retrieve**:
- Previous analyses of same ticker
- Similar technical patterns across all tickers
- Similar fundamental profiles
- Similar market conditions (macro environment)
- Successful buy signals with similar characteristics
- Failed signals to avoid repeating mistakes

**Performance Requirements**:
- PR6.1: Embedding generation <2 seconds per analysis
- PR6.2: Similarity search <1 second for top 10 results
- PR6.3: Support cosine similarity threshold filtering

**Acceptance Criteria**:
- Relevant historical context retrieved >90% of the time
- Context measurably improves decision quality
- No false matches (similarity threshold tuned properly)

---

### 5. Watchlist Management (SHOULD HAVE)

**Functional Requirements**:
- FR7.1: Add/remove tickers from watchlist
- FR7.2: Categorize by sector/industry
- FR7.3: Tag tickers (e.g., "high-growth", "value", "dividend")
- FR7.4: Set custom alerts per ticker
- FR7.5: View watchlist performance summary
- FR7.6: Import watchlist from CSV

**Acceptance Criteria**:
- Simple CLI commands to manage watchlist
- Changes persist in database
- Can organize 20+ tickers efficiently

---

### 6. Performance Tracking & Learning (SHOULD HAVE)

**Functional Requirements**:
- FR8.1: Track returns at 30/90/180 day intervals
- FR8.2: Compare actual returns vs expected returns
- FR8.3: Validate if entry thesis played out
- FR8.4: Extract "lessons learned" from outcomes
- FR8.5: Calculate success rate by pattern type
- FR8.6: Identify which agent reasoning correlates with success
- FR8.7: Store learnings as embeddings for future RAG retrieval

**Metrics to Track**:
- Overall win rate (% of buy signals with positive returns)
- Average return by holding period
- Max drawdown experienced vs predicted
- Signal confidence correlation with outcomes
- Pattern success rates
- Agent accuracy (bull vs bear vs risk manager)

**Acceptance Criteria**:
- Performance data automatically collected
- Can query: "Show me all tech buys and their outcomes"
- System learns from mistakes (RAG retrieves failed patterns)

---

### 7. Operational Workflows (MUST HAVE)

#### Daily Morning Routine (Automated)
```
Workflow: Daily Screener
Trigger: Cron job at 7:00 AM (before market open)
Steps:
  1. Fetch overnight price/volume data for watchlist
  2. Run lightweight screener (Tier 1)
  3. Calculate priority scores
  4. Store results in database
  5. Generate report: top 5 opportunities
  6. Send notification (optional: email/Slack)
Duration: <15 minutes
Output: Priority report for user review
```

#### Deep Analysis (Manual Trigger)
```
Workflow: Deep Ticker Analysis
Trigger: User command (e.g., `analyze NVDA`)
Steps:
  1. Fetch fresh data for ticker
  2. Retrieve historical context via RAG
  3. Run full TradingAgents system (Tier 2)
  4. Apply four-gate buy decision framework
  5. Generate comprehensive report
  6. Store analysis + embeddings in database
Duration: 30-45 minutes per ticker
Output: BUY/WAIT/PASS decision with full reasoning
```

#### Weekly Portfolio Review
```
Workflow: Portfolio Health Check
Trigger: Manual or scheduled (Sunday evening)
Steps:
  1. Re-scan all held positions
  2. Compare current state to entry thesis
  3. Check stop-loss levels
  4. Identify thesis violations
  5. Generate HOLD/TRIM/ADD recommendations
Duration: 30 minutes for 10 positions
Output: Portfolio action items
```

#### Monthly Learning Review
```
Workflow: System Performance Review
Trigger: Manual (first Sunday of month)
Steps:
  1. Calculate performance metrics for past month
  2. Review all buy signals and outcomes
  3. Identify successful patterns
  4. Identify failed patterns
  5. Update screening thresholds if needed
  6. Store learnings in database
Duration: 1 hour
Output: Performance report + system improvements
```

---

## Technical Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Investment Intelligence System            │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│  Daily Screener  │      │  Deep Analyzer   │      │Portfolio Monitor │
│   (Tier 1)       │      │   (Tier 2)       │      │   (Tier 3)       │
│                  │      │                  │      │                  │
│ llama3.1 (8B)    │      │ llama3.3 (70B)   │      │ llama3.1 (8B)    │
│ Fast & Efficient │      │ Quality Analysis │      │ Quick Review     │
└────────┬─────────┘      └────────┬─────────┘      └────────┬─────────┘
         │                         │                         │
         └─────────────────────────┼─────────────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   RAG Context Retriever     │
                    │                             │
                    │  • Semantic Search          │
                    │  • Pattern Matching         │
                    │  • Historical Context       │
                    │  • Performance Lookup       │
                    │                             │
                    │  nomic-embed-text           │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │  PostgreSQL + pgvector      │
                    │                             │
                    │  • Structured Data (SQL)    │
                    │  • Vector Embeddings        │
                    │  • Time-Series Data         │
                    │  • Performance Metrics      │
                    └──────────────┬──────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         │                         │                         │
┌────────▼─────────┐    ┌─────────▼────────┐    ┌──────────▼────────┐
│  Data Sources    │    │  TradingAgents   │    │  User Interface   │
│                  │    │  Framework       │    │                   │
│ • yfinance       │    │  (Existing)      │    │ • CLI             │
│ • Alpha Vantage  │    │                  │    │ • Reports         │
│ • News APIs      │    │ • Market Agent   │    │ • Notifications   │
└──────────────────┘    │ • Bull Agent     │    └───────────────────┘
                        │ • Bear Agent     │
                        │ • Risk Manager   │
                        │ • etc.           │
                        └──────────────────┘
```

### Technology Stack

**Core Technologies**:
- **Python 3.10+**: Main programming language
- **PostgreSQL 14+**: Primary database
- **pgvector Extension**: Vector similarity search
- **Ollama**: Local LLM inference
  - llama3.1 (8B): Screener & quick tasks
  - llama3.3 (70B): Deep analysis
  - nomic-embed-text: Embeddings generation
- **LangChain**: LLM orchestration (existing)
- **LangGraph**: Multi-agent framework (existing)

**Data Sources** (existing):
- yfinance: Stock prices, volume, technical indicators
- Alpha Vantage: Fundamentals, news
- Local cache: Historical data

**Development Tools**:
- Git: Version control
- pytest: Testing
- SQLAlchemy: Database ORM (optional)
- psycopg2/psycopg3: PostgreSQL driver

---

## Database Schema

### Detailed Table Definitions

#### 1. `tickers` - Watchlist Management
```sql
CREATE TABLE tickers (
    ticker_id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    company_name VARCHAR(255),
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,

    -- Watchlist management
    active BOOLEAN DEFAULT true,
    added_date DATE NOT NULL,
    removed_date DATE,
    priority_tier INTEGER DEFAULT 1, -- 1=high, 2=medium, 3=low

    -- Categorization
    tags TEXT[], -- e.g., ['high-growth', 'AI', 'dividend']
    notes TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tickers_symbol ON tickers(symbol);
CREATE INDEX idx_tickers_active ON tickers(active);
CREATE INDEX idx_tickers_sector ON tickers(sector);
```

#### 2. `daily_prices` - OHLCV Historical Data
```sql
CREATE TABLE daily_prices (
    price_id BIGSERIAL PRIMARY KEY,
    ticker_id INTEGER REFERENCES tickers(ticker_id),
    price_date DATE NOT NULL,

    -- Price data
    open DECIMAL(10,2),
    high DECIMAL(10,2),
    low DECIMAL(10,2),
    close DECIMAL(10,2),
    volume BIGINT,

    -- Calculated fields
    ma_20 DECIMAL(10,2),
    ma_50 DECIMAL(10,2),
    ma_200 DECIMAL(10,2),
    rsi_14 DECIMAL(5,2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(ticker_id, price_date)
);

CREATE INDEX idx_prices_ticker_date ON daily_prices(ticker_id, price_date DESC);
CREATE INDEX idx_prices_date ON daily_prices(price_date DESC);
```

#### 3. `daily_scans` - Screening Results
```sql
CREATE TABLE daily_scans (
    scan_id BIGSERIAL PRIMARY KEY,
    ticker_id INTEGER REFERENCES tickers(ticker_id),
    scan_date DATE NOT NULL,

    -- Current metrics
    price DECIMAL(10,2),
    volume BIGINT,

    -- Priority scoring
    priority_score INTEGER, -- 0-100
    priority_rank INTEGER, -- 1=highest priority

    -- Technical signals (JSON)
    technical_signals JSONB, -- {rsi: 28, macd: {...}, bollinger: {...}}

    -- Alerts triggered (array)
    triggered_alerts TEXT[], -- ['RSI_OVERSOLD', 'VOLUME_SPIKE']

    -- Fundamental snapshot
    pe_ratio DECIMAL(6,2),
    forward_pe DECIMAL(6,2),
    peg_ratio DECIMAL(6,3),

    -- Sentiment
    news_sentiment_score DECIMAL(3,2), -- -1 to 1

    -- Metadata
    scan_duration_seconds INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(ticker_id, scan_date)
);

CREATE INDEX idx_scans_date ON daily_scans(scan_date DESC);
CREATE INDEX idx_scans_priority ON daily_scans(scan_date, priority_rank);
CREATE INDEX idx_scans_ticker ON daily_scans(ticker_id, scan_date DESC);
```

#### 4. `analyses` - Deep Analysis History
```sql
CREATE TABLE analyses (
    analysis_id BIGSERIAL PRIMARY KEY,
    ticker_id INTEGER REFERENCES tickers(ticker_id),
    analysis_date TIMESTAMP NOT NULL,

    -- Market context
    price_at_analysis DECIMAL(10,2),
    volume_at_analysis BIGINT,
    market_cap_at_analysis BIGINT,

    -- Analysis output
    full_report JSONB, -- Complete agent outputs
    executive_summary TEXT,

    -- Decision
    final_decision VARCHAR(10), -- 'BUY', 'WAIT', 'PASS'
    confidence_score INTEGER, -- 0-100

    -- Four-gate results
    fundamental_gate_passed BOOLEAN,
    technical_gate_passed BOOLEAN,
    risk_gate_passed BOOLEAN,
    timing_score INTEGER, -- 0-100

    -- Key insights
    key_catalysts TEXT[],
    risk_factors TEXT[],
    bull_case TEXT,
    bear_case TEXT,

    -- Recommendations (if BUY)
    entry_price_target DECIMAL(10,2),
    stop_loss_price DECIMAL(10,2),
    position_size_pct DECIMAL(5,2), -- % of portfolio
    expected_return_pct DECIMAL(6,2),
    expected_holding_period_days INTEGER,

    -- Agent outputs (detailed)
    market_report JSONB,
    fundamentals_report JSONB,
    sentiment_report JSONB,
    news_report JSONB,
    debate_history JSONB,

    -- Vector embedding for RAG
    embedding vector(768), -- nomic-embed-text dimension

    -- Metadata
    analysis_duration_seconds INTEGER,
    llm_model_used VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_analyses_ticker ON analyses(ticker_id, analysis_date DESC);
CREATE INDEX idx_analyses_date ON analyses(analysis_date DESC);
CREATE INDEX idx_analyses_decision ON analyses(final_decision);
CREATE INDEX idx_analyses_embedding ON analyses USING ivfflat (embedding vector_cosine_ops);
```

#### 5. `buy_signals` - Buy/Sell Signal History
```sql
CREATE TABLE buy_signals (
    signal_id BIGSERIAL PRIMARY KEY,
    analysis_id BIGINT REFERENCES analyses(analysis_id),
    ticker_id INTEGER REFERENCES tickers(ticker_id),

    signal_date TIMESTAMP NOT NULL,
    signal_type VARCHAR(10), -- 'BUY', 'SELL', 'STRONG_BUY'

    -- Price context
    signal_price DECIMAL(10,2),
    stop_loss_price DECIMAL(10,2),
    target_price DECIMAL(10,2),

    -- Reasoning
    reasoning TEXT,
    pattern_matched VARCHAR(100), -- e.g., "OVERSOLD_BOUNCE", "BREAKOUT"
    historical_pattern_id BIGINT, -- Reference to similar past pattern
    pattern_similarity_score DECIMAL(4,3), -- 0-1

    -- Expectations
    expected_return_pct DECIMAL(6,2),
    expected_holding_days INTEGER,
    position_size_recommended_pct DECIMAL(5,2),

    -- Risk assessment
    risk_factors JSONB,
    max_expected_drawdown_pct DECIMAL(5,2),

    -- Signal quality
    confidence_score INTEGER, -- 0-100
    agent_consensus_score DECIMAL(4,3), -- % of agents agreeing

    -- Vector embedding for pattern matching
    embedding vector(768),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_signals_ticker ON buy_signals(ticker_id, signal_date DESC);
CREATE INDEX idx_signals_date ON buy_signals(signal_date DESC);
CREATE INDEX idx_signals_type ON buy_signals(signal_type);
CREATE INDEX idx_signals_embedding ON buy_signals USING ivfflat (embedding vector_cosine_ops);
```

#### 6. `portfolio_actions` - Actual Trades & Decisions
```sql
CREATE TABLE portfolio_actions (
    action_id BIGSERIAL PRIMARY KEY,
    ticker_id INTEGER REFERENCES tickers(ticker_id),
    signal_id BIGINT REFERENCES buy_signals(signal_id), -- If action based on signal

    action_date DATE NOT NULL,
    action_type VARCHAR(10), -- 'BUY', 'SELL', 'HOLD', 'TRIM', 'ADD'

    -- Trade details
    shares DECIMAL(10,2),
    price DECIMAL(10,2),
    total_value DECIMAL(12,2),
    commission DECIMAL(8,2),

    -- Portfolio context
    portfolio_value_before DECIMAL(12,2),
    position_size_pct DECIMAL(5,2), -- % of portfolio

    -- Decision reasoning
    reasoning TEXT,
    thesis TEXT, -- Investment thesis at entry

    -- Metadata
    is_paper_trade BOOLEAN DEFAULT false, -- For testing
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_actions_ticker ON portfolio_actions(ticker_id, action_date DESC);
CREATE INDEX idx_actions_date ON portfolio_actions(action_date DESC);
CREATE INDEX idx_actions_type ON portfolio_actions(action_type);
```

#### 7. `performance_tracking` - Returns & Learning
```sql
CREATE TABLE performance_tracking (
    tracking_id BIGSERIAL PRIMARY KEY,
    portfolio_action_id BIGINT REFERENCES portfolio_actions(action_id),
    ticker_id INTEGER REFERENCES tickers(ticker_id),
    signal_id BIGINT REFERENCES buy_signals(signal_id),

    -- Entry details
    entry_date DATE NOT NULL,
    entry_price DECIMAL(10,2),
    entry_thesis TEXT,

    -- Exit details (if closed)
    exit_date DATE,
    exit_price DECIMAL(10,2),
    exit_reason TEXT,

    -- Performance snapshots
    days_30_price DECIMAL(10,2),
    days_30_return_pct DECIMAL(6,2),
    days_90_price DECIMAL(10,2),
    days_90_return_pct DECIMAL(6,2),
    days_180_price DECIMAL(10,2),
    days_180_return_pct DECIMAL(6,2),

    -- Final performance (if exited)
    holding_period_days INTEGER,
    actual_return_pct DECIMAL(6,2),
    actual_return_dollars DECIMAL(10,2),
    max_drawdown_pct DECIMAL(5,2),

    -- Expectations vs Reality
    expected_return_pct DECIMAL(6,2),
    expected_holding_days INTEGER,
    beat_expectations BOOLEAN,
    return_variance DECIMAL(6,2), -- actual - expected

    -- Thesis validation
    thesis_validated BOOLEAN,
    catalysts_played_out BOOLEAN,
    unexpected_events TEXT[],

    -- Learnings
    what_went_right TEXT,
    what_went_wrong TEXT,
    lessons_learned TEXT,
    pattern_notes TEXT, -- Notes about the pattern for future

    -- Vector embedding for learning RAG
    embedding vector(768),

    -- Metadata
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_performance_ticker ON performance_tracking(ticker_id);
CREATE INDEX idx_performance_entry ON performance_tracking(entry_date DESC);
CREATE INDEX idx_performance_return ON performance_tracking(actual_return_pct DESC);
CREATE INDEX idx_performance_embedding ON performance_tracking USING ivfflat (embedding vector_cosine_ops);
```

#### 8. `system_config` - Configuration & Parameters
```sql
CREATE TABLE system_config (
    config_id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value JSONB,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Store things like:
-- screening_thresholds: {rsi_oversold: 30, volume_spike_pct: 50, ...}
-- buy_decision_gates: {fundamental_min_score: 70, technical_min_score: 65, ...}
-- position_sizing_rules: {max_single_position: 10, max_sector: 30, ...}
-- rag_parameters: {similarity_threshold: 0.7, max_context_items: 5, ...}
```

### Database Views (Useful Queries)

```sql
-- View: Recent high-priority opportunities
CREATE VIEW recent_opportunities AS
SELECT
    t.symbol,
    ds.scan_date,
    ds.priority_score,
    ds.price,
    ds.triggered_alerts,
    a.final_decision,
    a.confidence_score
FROM daily_scans ds
JOIN tickers t ON ds.ticker_id = t.ticker_id
LEFT JOIN analyses a ON ds.ticker_id = a.ticker_id
    AND DATE(a.analysis_date) = ds.scan_date
WHERE ds.scan_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY ds.scan_date DESC, ds.priority_rank;

-- View: Active portfolio with current performance
CREATE VIEW active_positions AS
SELECT
    t.symbol,
    pa.entry_date,
    pa.entry_price,
    pt.days_30_return_pct,
    pt.days_90_return_pct,
    pt.actual_return_pct,
    pt.thesis_validated,
    pa.thesis
FROM portfolio_actions pa
JOIN tickers t ON pa.ticker_id = t.ticker_id
LEFT JOIN performance_tracking pt ON pa.action_id = pt.portfolio_action_id
WHERE pa.action_type = 'BUY'
    AND NOT EXISTS (
        SELECT 1 FROM portfolio_actions pa2
        WHERE pa2.ticker_id = pa.ticker_id
        AND pa2.action_type = 'SELL'
        AND pa2.action_date > pa.action_date
    );

-- View: Pattern success rates
CREATE VIEW pattern_performance AS
SELECT
    bs.pattern_matched,
    COUNT(*) as total_signals,
    AVG(pt.actual_return_pct) as avg_return,
    AVG(pt.holding_period_days) as avg_holding_days,
    SUM(CASE WHEN pt.beat_expectations THEN 1 ELSE 0 END)::FLOAT / COUNT(*) as success_rate
FROM buy_signals bs
JOIN performance_tracking pt ON bs.signal_id = pt.signal_id
WHERE pt.exit_date IS NOT NULL
GROUP BY bs.pattern_matched
ORDER BY success_rate DESC;
```

---

## Implementation Plan

### Phase 1: Foundation (Week 1-2)
**Goal**: Set up core infrastructure

**Tasks**:
1. Install and configure PostgreSQL + pgvector
2. Create database schema (all tables)
3. Set up database backup automation
4. Create database connection module in Python
5. Build basic CRUD operations for tickers table
6. Import initial watchlist (10-20 tickers)
7. Backfill historical price data for watchlist

**Deliverables**:
- PostgreSQL database running locally
- All tables created with proper indexes
- Python DB interface module
- Watchlist loaded with historical data

**Acceptance Criteria**:
- Can add/remove tickers via Python
- Can query price history
- Database backup runs daily

---

### Phase 2: Daily Screener (Week 3)
**Goal**: Implement Tier 1 analysis

**Tasks**:
1. Build data fetching module (incremental updates)
2. Implement technical indicator calculations
3. Build priority scoring algorithm
4. Create daily_scans table insertion logic
5. Build screener CLI command
6. Generate daily report (text/markdown format)
7. Set up cron job for automation

**Deliverables**:
- `screener.py` module
- CLI: `python -m tradingagents.screener run`
- Daily report output
- Automated morning execution

**Acceptance Criteria**:
- Scans 20 tickers in <15 minutes
- Produces consistent priority rankings
- Results stored in database
- Can review past screening results

---

### Phase 3: RAG Integration (Week 4-5)
**Goal**: Enable historical context retrieval

**Tasks**:
1. Build embedding generation module (nomic-embed-text)
2. Backfill embeddings for any existing analyses
3. Build vector similarity search functions
4. Create context retrieval module:
   - Similar analyses finder
   - Pattern matcher
   - Performance lookup
5. Build context formatter (for LLM injection)
6. Test RAG queries on sample data

**Deliverables**:
- `rag.py` module
- Embedding generation pipeline
- Context retrieval functions
- Test suite for RAG queries

**Acceptance Criteria**:
- Can generate embeddings in <2 sec
- Similarity search returns results in <1 sec
- Relevant context retrieved >90% of time
- Can find similar historical situations

---

### Phase 4: Enhanced Deep Analysis (Week 6)
**Goal**: Integrate RAG with existing TradingAgents

**Tasks**:
1. Modify TradingAgentsGraph to accept historical context
2. Update agent prompts to utilize context
3. Build four-gate decision framework
4. Implement buy signal generation logic
5. Create analysis storage module (save to DB)
6. Build CLI for deep analysis: `python -m tradingagents.analyze NVDA`
7. Test end-to-end on multiple tickers

**Deliverables**:
- Enhanced `trading_graph.py`
- `decision_framework.py` module
- CLI for triggering deep analysis
- Analysis results stored in database

**Acceptance Criteria**:
- Deep analysis includes historical context
- Four-gate framework produces clear decisions
- All results stored with embeddings
- Can analyze ticker in 30-45 min

---

### Phase 5: Portfolio Tracking (Week 7)
**Goal**: Implement Tier 3 and performance tracking

**Tasks**:
1. Build portfolio management module
2. Create portfolio action logging (buys/sells)
3. Implement performance calculation (30/90/180 day)
4. Build weekly portfolio review workflow
5. Create performance reporting
6. Implement lessons learned capture

**Deliverables**:
- `portfolio.py` module
- CLI: `python -m tradingagents.portfolio review`
- Performance tracking automation
- Learning extraction logic

**Acceptance Criteria**:
- Can log portfolio actions
- Automatic performance tracking
- Weekly review generates actionable insights
- Learnings stored for RAG retrieval

---

### Phase 6: Testing & Refinement (Week 8-9)
**Goal**: Validate system with historical data

**Tasks**:
1. Backtest on historical data (2020-2024)
2. Validate buy signal accuracy
3. Tune screening thresholds
4. Tune decision gate parameters
5. Optimize RAG similarity thresholds
6. Performance testing (speed optimization)
7. Documentation

**Deliverables**:
- Backtest results report
- Tuned configuration parameters
- Performance benchmarks
- User documentation

**Acceptance Criteria**:
- System achieves >65% win rate on backtest
- Daily workflow completes in <2 hours
- All features documented
- No critical bugs

---

### Phase 7: Production Deployment (Week 10)
**Goal**: Deploy for daily use

**Tasks**:
1. Set up production database (separate from dev)
2. Configure automated backups
3. Set up monitoring/alerting
4. Create deployment scripts
5. Final user training
6. Begin paper trading period (30 days)

**Deliverables**:
- Production system running
- Automated daily workflows
- Monitoring dashboard
- Paper trading results

**Acceptance Criteria**:
- System runs unattended daily
- Zero data loss
- Paper trading validates signals
- User can operate independently

---

## Non-Functional Requirements

### Performance
- NFR1: Daily screener completes in <15 minutes for 20 tickers
- NFR2: Deep analysis completes in <45 minutes per ticker
- NFR3: RAG queries return in <1 second
- NFR4: Database queries <100ms for common operations
- NFR5: System handles 100+ tickers without degradation

### Reliability
- NFR6: 99.9% uptime for automated workflows
- NFR7: Automated daily database backups
- NFR8: Graceful handling of API failures (data sources)
- NFR9: Transaction safety for all database writes
- NFR10: Data validation prevents corruption

### Scalability
- NFR11: Database design supports 10,000+ analyses
- NFR12: Can expand to 100+ tickers without refactoring
- NFR13: Historical data retention: 5+ years
- NFR14: Embedding storage optimized for millions of vectors

### Security
- NFR15: Database credentials stored securely (.env)
- NFR16: Local-only operation (no data sent to cloud)
- NFR17: API keys encrypted at rest
- NFR18: Database access controls configured

### Maintainability
- NFR19: Modular code architecture
- NFR20: Comprehensive logging
- NFR21: Unit test coverage >80%
- NFR22: Clear documentation for all modules

### Usability
- NFR23: CLI commands intuitive and well-documented
- NFR24: Error messages clear and actionable
- NFR25: Reports human-readable and actionable
- NFR26: Configuration via simple YAML/JSON files

---

## Success Metrics

### Primary KPIs (Must Achieve)

**Investment Performance**:
- Win Rate: >70% of buy signals show positive returns at 6 months
- Average Return: >15% per position over 12 months
- Max Drawdown: <15% on any position
- Sharpe Ratio: >1.5 (risk-adjusted returns)

**Operational Efficiency**:
- Daily Time Investment: <1 hour for full workflow
- Analysis Speed: 20 tickers screened in <15 min
- Deep Analysis: <45 min per ticker
- False Positives: <20% (buy signals that lose money)

**System Quality**:
- RAG Relevance: >90% of retrieved context rated as relevant
- Decision Consistency: Same inputs produce same outputs
- Data Accuracy: 100% of analyses stored correctly
- Uptime: >99% for automated workflows

### Secondary KPIs (Nice to Have)

**Learning & Improvement**:
- Pattern Recognition: Success rate of identified patterns
- Agent Accuracy: Which agents' reasoning correlates with success
- Continuous Improvement: Win rate increases over time
- Thesis Validation: % of investment theses that play out

**User Satisfaction**:
- Confidence in Decisions: User trusts system recommendations
- Time Saved: vs manual analysis (estimate 80% reduction)
- Insight Quality: "Learned something new" from analysis

---

## Dependencies & Assumptions

### Dependencies

**External**:
- PostgreSQL 14+ available
- pgvector extension installed
- Ollama running locally with models:
  - llama3.1 (8B)
  - llama3.3 (70B)
  - nomic-embed-text
- Data API keys:
  - Alpha Vantage (free tier sufficient)
  - yfinance (no key needed)

**Internal**:
- Existing TradingAgents framework functional
- Python 3.10+ environment
- Sufficient disk space (50GB+ recommended)
- Adequate RAM (32GB+ for 70B model)

### Assumptions

**User Behavior**:
- User will review daily screener reports
- User will manually trigger deep analyses
- User will log portfolio actions (for tracking)
- User comfortable with CLI interface

**Market Data**:
- Free data sources provide sufficient quality
- Daily data updates are acceptable (no real-time needed)
- Historical data available for backtesting

**System**:
- Local Ollama models provide acceptable quality
- PostgreSQL can handle workload on single machine
- No need for distributed/cloud infrastructure
- 10-20 ticker scope sufficient (won't balloon to 1000s)

**Investment Horizon**:
- Long-term focus (6-24 month holds)
- Not for day trading or HFT
- Fundamental analysis more important than technical

---

## Risks & Mitigations

### Technical Risks

**Risk 1: Ollama Model Quality**
- **Impact**: Poor analysis quality, bad decisions
- **Likelihood**: Medium
- **Mitigation**:
  - Use largest models possible (70B for deep analysis)
  - Validate outputs against historical data
  - Allow manual override of decisions
  - Continuous monitoring of decision quality

**Risk 2: Database Performance**
- **Impact**: Slow queries, poor user experience
- **Likelihood**: Low
- **Mitigation**:
  - Proper indexing from start
  - Regular VACUUM and ANALYZE
  - Monitor query performance
  - Optimize slow queries proactively

**Risk 3: Data Source Reliability**
- **Impact**: Missing/stale data affects decisions
- **Likelihood**: Medium
- **Mitigation**:
  - Multiple data source fallbacks
  - Cache data locally
  - Alert on data fetch failures
  - Graceful degradation

**Risk 4: RAG Context Quality**
- **Impact**: Irrelevant context confuses LLM
- **Likelihood**: Medium
- **Mitigation**:
  - Tune similarity thresholds carefully
  - Validate context relevance on test data
  - Allow disabling RAG if needed
  - Monitor context quality metrics

### Business Risks

**Risk 5: False Confidence**
- **Impact**: Over-reliance on system leads to poor decisions
- **Likelihood**: Medium
- **Mitigation**:
  - Clearly communicate limitations
  - Show confidence scores honestly
  - Encourage user judgment
  - Paper trading period before real money

**Risk 6: Overfitting to Historical Data**
- **Impact**: Past patterns don't predict future
- **Likelihood**: High (inherent to backtesting)
- **Mitigation**:
  - Conservative thresholds
  - Diverse pattern recognition
  - Regular strategy review
  - Acknowledge market regime changes

**Risk 7: Data Privacy**
- **Impact**: Sensitive investment data leaked
- **Likelihood**: Low (local system)
- **Mitigation**:
  - Fully local operation
  - Secure database credentials
  - Encrypted backups
  - No cloud sync by default

---

## Open Questions

1. **Notification System**: Email/Slack for daily reports or CLI-only?
2. **Backtesting Scope**: How far back to backtest? Full 2020-2024 or sample periods?
3. **Paper Trading Duration**: 30 days, 90 days, or until X signals validated?
4. **Stop-Loss Automation**: Track recommended stop-losses or just advisory?
5. **Position Sizing**: Fixed rules or dynamic based on conviction?
6. **Sector Limits**: Hard caps on sector exposure or just guidance?
7. **Rebalancing Logic**: Automated suggestions or user-driven?
8. **Export Capabilities**: Need CSV/Excel export of reports?
9. **Visualization**: CLI-only or add simple charts (matplotlib)?
10. **Multi-user**: Design for single user or allow multiple portfolios?

---

## Appendix

### A. Example Workflows

#### Example 1: Monday Morning Routine
```bash
# 7:00 AM - Automated screener runs (cron)
# 7:15 AM - User wakes up, checks report

$ python -m tradingagents.screener report --latest

=== Daily Screener Report - 2025-11-18 ===
Analyzed 20 tickers in 12 minutes

TOP OPPORTUNITIES:
1. NVDA (Score: 87) - Oversold bounce setup, strong fundamentals
   Alerts: RSI_OVERSOLD, VOLUME_SPIKE, SUPPORT_HOLDING

2. MSFT (Score: 78) - Breakout pattern, earnings catalyst
   Alerts: BREAKOUT_20DMA, NEWS_POSITIVE

3. AMD (Score: 72) - Value opportunity, sector rotation
   Alerts: PE_BELOW_SECTOR, INSTITUTIONAL_BUYING

# User decides to analyze NVDA deeply
$ python -m tradingagents.analyze NVDA

[... 30 minutes of analysis ...]

=== DEEP ANALYSIS REPORT - NVDA ===
Decision: BUY
Confidence: 84/100

Historical Context:
- Similar setup seen 2023-08-15 (similarity: 0.89)
  → That signal returned +42% in 6 months
- Current price $850 vs our last analysis at $920 (-7.6%)
- Pattern: MACRO_PULLBACK_STRONG_FUNDAMENTALS (78% success rate)

Four-Gate Assessment:
✓ Fundamental Value: PASS (score: 88/100)
✓ Technical Entry: PASS (score: 76/100)
✓ Risk Assessment: PASS (max drawdown: 12%)
⚠ Timing Quality: GOOD (score: 81/100)

Recommendation:
Entry Price: $845-$855
Position Size: 8% of portfolio
Stop Loss: $765 (-10%)
Expected Return: +28% over 12 months
Key Catalyst: Blackwell GPU ramp Q1 2025

# User decides to buy
$ python -m tradingagents.portfolio buy NVDA --shares 100 --price 850

Position logged. Tracking started.
```

#### Example 2: Weekly Portfolio Review
```bash
$ python -m tradingagents.portfolio review

=== Portfolio Health Check - 2025-11-17 ===

Active Positions: 8

THESIS VIOLATIONS:
⚠ AAPL - Revenue growth slowing (expected: 8%, actual: 4%)
  → Recommendation: TRIM to 5% (currently 10%)

STOP-LOSS ALERTS:
❌ TSLA - Approaching stop-loss ($245 current, $240 stop)
  → Review immediately

OUTPERFORMERS:
✓ NVDA - Up 18% in 45 days (expected: 12%)
  → Thesis validated, HOLD

REBALANCING OPPORTUNITIES:
→ Tech sector now 45% (target: 35%)
  → Consider trimming AAPL, MSFT

# User takes action
$ python -m tradingagents.portfolio trim AAPL --to-pct 5

Position adjusted. Proceeds: $12,500
```

### B. RAG Query Examples

```python
# Example RAG queries the system will use

# 1. Find similar past analyses
query = "NVDA oversold on macro fears, fundamentals strong, AI growth intact"
results = rag.find_similar_analyses(query, limit=5)
# Returns: [
#   {analysis_id: 123, ticker: 'NVDA', date: '2023-08-15',
#    decision: 'BUY', outcome: '+42% in 180 days', similarity: 0.89},
#   ...
# ]

# 2. Pattern success rate lookup
pattern = "OVERSOLD_BOUNCE_STRONG_FUNDAMENTALS"
stats = rag.get_pattern_performance(pattern)
# Returns: {
#   total_signals: 24,
#   win_rate: 0.78,
#   avg_return: 0.23,
#   avg_holding_days: 145
# }

# 3. Historical ticker performance
history = rag.get_ticker_history('NVDA', limit=10)
# Returns all past analyses, decisions, outcomes for NVDA

# 4. Cross-ticker pattern matching
similar = rag.find_similar_setups(
    ticker='NVDA',
    current_metrics={'rsi': 28, 'pe': 52, 'growth': 45},
    exclude_same_ticker=True
)
# Returns similar setups in other stocks
```

### C. Configuration Example

```yaml
# config/investment_intelligence.yaml

# Screening Configuration
screening:
  priority_scoring:
    weights:
      technical: 0.35
      fundamental: 0.30
      sentiment: 0.20
      volume: 0.15

  technical_alerts:
    rsi_oversold: 30
    rsi_overbought: 70
    volume_spike_pct: 50
    macd_crossover: true
    support_bounce_pct: 2

  fundamental_thresholds:
    min_market_cap: 1000000000  # $1B
    max_pe_ratio: 100
    min_revenue_growth_yoy: -0.10  # -10%

# Buy Decision Gates
buy_decision:
  fundamental_gate:
    min_score: 70
    required_checks:
      - positive_earnings_growth
      - healthy_balance_sheet
      - sector_relative_value

  technical_gate:
    min_score: 65
    max_pct_from_high: 0.15  # Max 15% from 52-week high
    required_signals:
      - support_holding
      - volume_confirmation

  risk_gate:
    max_position_size: 0.10  # 10% of portfolio
    max_sector_exposure: 0.35  # 35% in any sector
    max_drawdown_acceptable: 0.15  # 15%
    min_risk_reward_ratio: 2.0

  timing_gate:
    min_timing_score: 60  # 0-100
    pattern_min_success_rate: 0.60  # 60%

# RAG Configuration
rag:
  embedding_model: "nomic-embed-text"
  similarity_threshold: 0.70  # Cosine similarity
  max_context_items: 5
  context_types:
    - similar_analyses
    - similar_patterns
    - ticker_history
    - sector_comparisons

# LLM Configuration
llms:
  screener_model: "llama3.1"  # 8B - fast
  deep_analysis_model: "llama3.3"  # 70B - quality
  embedding_model: "nomic-embed-text"
  temperature: 0.7
  max_tokens: 4096

# Data Sources
data_sources:
  primary_price_data: "yfinance"
  fundamentals: "alpha_vantage"
  news: "alpha_vantage"
  backup_sources:
    - "local_cache"

# Portfolio Rules
portfolio:
  max_positions: 20
  min_position_size: 0.03  # 3%
  max_position_size: 0.10  # 10%
  max_sector_exposure: 0.35  # 35%
  cash_reserve_pct: 0.10  # 10%
  rebalancing_threshold: 0.05  # 5% drift

# Automation
automation:
  daily_screener:
    enabled: true
    schedule: "0 7 * * 1-5"  # 7 AM weekdays

  portfolio_review:
    enabled: true
    schedule: "0 18 * * 0"  # 6 PM Sunday

  performance_tracking:
    enabled: true
    update_frequency: "daily"

# Notifications (future)
notifications:
  email:
    enabled: false
    address: "user@example.com"

  slack:
    enabled: false
    webhook_url: ""
```

---

## Approval & Sign-off

**Product Owner**: ___________________ Date: ___________

**Technical Lead**: ___________________ Date: ___________

**Stakeholder**: ___________________ Date: ___________

---

**Document History**:
- v1.0 (2025-11-15): Initial draft
- Future revisions will be tracked here

---

**Next Steps**:
1. Review and approve PRD
2. Set up development environment
3. Begin Phase 1 implementation
4. Schedule weekly progress reviews
