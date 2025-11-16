-- Investment Intelligence System Database Schema
-- PostgreSQL 14+ with pgvector extension
-- Version: 1.0
-- Date: 2025-11-15

-- Ensure vector extension is enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- 1. TICKERS TABLE - Watchlist Management
-- ============================================================================
CREATE TABLE IF NOT EXISTS tickers (
    ticker_id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    company_name VARCHAR(255),
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,

    -- Watchlist management
    active BOOLEAN DEFAULT true,
    added_date DATE NOT NULL DEFAULT CURRENT_DATE,
    removed_date DATE,
    priority_tier INTEGER DEFAULT 1, -- 1=high, 2=medium, 3=low

    -- Categorization
    tags TEXT[], -- e.g., ['high-growth', 'AI', 'dividend']
    notes TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tickers_symbol ON tickers(symbol);
CREATE INDEX IF NOT EXISTS idx_tickers_active ON tickers(active);
CREATE INDEX IF NOT EXISTS idx_tickers_sector ON tickers(sector);

-- ============================================================================
-- 2. DAILY_PRICES TABLE - OHLCV Historical Data
-- ============================================================================
CREATE TABLE IF NOT EXISTS daily_prices (
    price_id BIGSERIAL PRIMARY KEY,
    ticker_id INTEGER REFERENCES tickers(ticker_id) ON DELETE CASCADE,
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

CREATE INDEX IF NOT EXISTS idx_prices_ticker_date ON daily_prices(ticker_id, price_date DESC);
CREATE INDEX IF NOT EXISTS idx_prices_date ON daily_prices(price_date DESC);

-- ============================================================================
-- 3. DAILY_SCANS TABLE - Screening Results
-- ============================================================================
CREATE TABLE IF NOT EXISTS daily_scans (
    scan_id BIGSERIAL PRIMARY KEY,
    ticker_id INTEGER REFERENCES tickers(ticker_id) ON DELETE CASCADE,
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

CREATE INDEX IF NOT EXISTS idx_scans_date ON daily_scans(scan_date DESC);
CREATE INDEX IF NOT EXISTS idx_scans_priority ON daily_scans(scan_date, priority_rank);
CREATE INDEX IF NOT EXISTS idx_scans_ticker ON daily_scans(ticker_id, scan_date DESC);

-- ============================================================================
-- 4. ANALYSES TABLE - Deep Analysis History
-- ============================================================================
CREATE TABLE IF NOT EXISTS analyses (
    analysis_id BIGSERIAL PRIMARY KEY,
    ticker_id INTEGER REFERENCES tickers(ticker_id) ON DELETE CASCADE,
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

CREATE INDEX IF NOT EXISTS idx_analyses_ticker ON analyses(ticker_id, analysis_date DESC);
CREATE INDEX IF NOT EXISTS idx_analyses_date ON analyses(analysis_date DESC);
CREATE INDEX IF NOT EXISTS idx_analyses_decision ON analyses(final_decision);

-- Vector index for similarity search (using IVFFlat - faster for smaller datasets)
CREATE INDEX IF NOT EXISTS idx_analyses_embedding ON analyses
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- ============================================================================
-- 5. BUY_SIGNALS TABLE - Buy/Sell Signal History
-- ============================================================================
CREATE TABLE IF NOT EXISTS buy_signals (
    signal_id BIGSERIAL PRIMARY KEY,
    analysis_id BIGINT REFERENCES analyses(analysis_id) ON DELETE CASCADE,
    ticker_id INTEGER REFERENCES tickers(ticker_id) ON DELETE CASCADE,

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

CREATE INDEX IF NOT EXISTS idx_signals_ticker ON buy_signals(ticker_id, signal_date DESC);
CREATE INDEX IF NOT EXISTS idx_signals_date ON buy_signals(signal_date DESC);
CREATE INDEX IF NOT EXISTS idx_signals_type ON buy_signals(signal_type);

CREATE INDEX IF NOT EXISTS idx_signals_embedding ON buy_signals
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- ============================================================================
-- 6. PORTFOLIO_ACTIONS TABLE - Actual Trades & Decisions
-- ============================================================================
CREATE TABLE IF NOT EXISTS portfolio_actions (
    action_id BIGSERIAL PRIMARY KEY,
    ticker_id INTEGER REFERENCES tickers(ticker_id) ON DELETE CASCADE,
    signal_id BIGINT REFERENCES buy_signals(signal_id) ON DELETE SET NULL, -- If action based on signal

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

CREATE INDEX IF NOT EXISTS idx_actions_ticker ON portfolio_actions(ticker_id, action_date DESC);
CREATE INDEX IF NOT EXISTS idx_actions_date ON portfolio_actions(action_date DESC);
CREATE INDEX IF NOT EXISTS idx_actions_type ON portfolio_actions(action_type);

-- ============================================================================
-- 7. PERFORMANCE_TRACKING TABLE - Returns & Learning
-- ============================================================================
CREATE TABLE IF NOT EXISTS performance_tracking (
    tracking_id BIGSERIAL PRIMARY KEY,
    portfolio_action_id BIGINT REFERENCES portfolio_actions(action_id) ON DELETE CASCADE,
    ticker_id INTEGER REFERENCES tickers(ticker_id) ON DELETE CASCADE,
    signal_id BIGINT REFERENCES buy_signals(signal_id) ON DELETE SET NULL,

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

CREATE INDEX IF NOT EXISTS idx_performance_ticker ON performance_tracking(ticker_id);
CREATE INDEX IF NOT EXISTS idx_performance_entry ON performance_tracking(entry_date DESC);
CREATE INDEX IF NOT EXISTS idx_performance_return ON performance_tracking(actual_return_pct DESC);

CREATE INDEX IF NOT EXISTS idx_performance_embedding ON performance_tracking
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- ============================================================================
-- 8. SYSTEM_CONFIG TABLE - Configuration & Parameters
-- ============================================================================
CREATE TABLE IF NOT EXISTS system_config (
    config_id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value JSONB,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default configuration
INSERT INTO system_config (config_key, config_value, description) VALUES
    ('screening_thresholds',
     '{"rsi_oversold": 30, "rsi_overbought": 70, "volume_spike_pct": 50, "macd_crossover": true, "support_bounce_pct": 2}',
     'Technical indicator thresholds for daily screener'),
    ('buy_decision_gates',
     '{"fundamental_min_score": 70, "technical_min_score": 65, "risk_min_score": 70, "timing_min_score": 60}',
     'Minimum scores required for each decision gate'),
    ('position_sizing_rules',
     '{"max_single_position": 0.10, "max_sector": 0.35, "cash_reserve": 0.10}',
     'Portfolio allocation rules'),
    ('rag_parameters',
     '{"similarity_threshold": 0.70, "max_context_items": 5, "min_match_count": 2}',
     'RAG retrieval configuration')
ON CONFLICT (config_key) DO NOTHING;

-- ============================================================================
-- VIEWS - Useful Queries
-- ============================================================================

-- View: Recent high-priority opportunities
CREATE OR REPLACE VIEW recent_opportunities AS
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
CREATE OR REPLACE VIEW active_positions AS
SELECT
    t.symbol,
    pa.action_date as entry_date,
    pa.price as entry_price,
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
    )
ORDER BY pa.action_date DESC;

-- View: Pattern success rates
CREATE OR REPLACE VIEW pattern_performance AS
SELECT
    bs.pattern_matched,
    COUNT(*) as total_signals,
    AVG(pt.actual_return_pct) as avg_return,
    AVG(pt.holding_period_days) as avg_holding_days,
    SUM(CASE WHEN pt.beat_expectations THEN 1 ELSE 0 END)::FLOAT / NULLIF(COUNT(*), 0) as success_rate
FROM buy_signals bs
JOIN performance_tracking pt ON bs.signal_id = pt.signal_id
WHERE pt.exit_date IS NOT NULL
GROUP BY bs.pattern_matched
ORDER BY success_rate DESC;

-- ============================================================================
-- FUNCTIONS - Update Timestamp Trigger
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tickers table
DROP TRIGGER IF EXISTS update_tickers_updated_at ON tickers;
CREATE TRIGGER update_tickers_updated_at
    BEFORE UPDATE ON tickers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- COMMENTS - Documentation
-- ============================================================================

COMMENT ON TABLE tickers IS 'Watchlist of stocks to monitor and analyze';
COMMENT ON TABLE daily_prices IS 'Historical OHLCV price data with calculated indicators';
COMMENT ON TABLE daily_scans IS 'Results from daily lightweight screening';
COMMENT ON TABLE analyses IS 'Deep analysis results from full TradingAgents system';
COMMENT ON TABLE buy_signals IS 'Buy/sell signals generated from analyses';
COMMENT ON TABLE portfolio_actions IS 'Actual portfolio trades and decisions';
COMMENT ON TABLE performance_tracking IS 'Performance tracking and learning outcomes';
COMMENT ON TABLE system_config IS 'System configuration and parameters';

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE 'Investment Intelligence System database schema created successfully!';
    RAISE NOTICE 'PostgreSQL version: %', version();
    RAISE NOTICE 'Vector extension enabled: %', (SELECT extversion FROM pg_extension WHERE extname = 'vector');
END $$;
