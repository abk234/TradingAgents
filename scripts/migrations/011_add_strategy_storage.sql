-- Migration 011: Add Trading Strategy Storage
-- Date: 2025-11-17
-- Purpose: Store trading strategies explicitly for learning and evolution

-- ============================================================================
-- TRADING STRATEGIES TABLE
-- ============================================================================
-- Stores trading strategies as reusable templates with performance tracking

CREATE TABLE IF NOT EXISTS trading_strategies (
    strategy_id SERIAL PRIMARY KEY,
    strategy_name VARCHAR(100) NOT NULL,
    strategy_description TEXT,
    strategy_version INTEGER DEFAULT 1,
    
    -- Strategy configuration
    indicator_combination JSONB,  -- Which indicators used (e.g., {"rsi": true, "macd": true})
    gate_thresholds JSONB,         -- Gate thresholds (e.g., {"fundamental_min": 70, "technical_min": 65})
    sector_focus TEXT[],           -- Preferred sectors (e.g., ["Technology", "Healthcare"])
    min_confidence INTEGER,        -- Minimum confidence to take trade
    holding_period_days INTEGER,   -- Expected holding period
    
    -- Performance metrics (from backtesting)
    backtest_results JSONB,       -- Win rate, avg return, sharpe ratio, max drawdown
    win_rate DECIMAL(5,2),        -- Win rate percentage
    avg_return_pct DECIMAL(6,2),   -- Average return percentage
    sharpe_ratio DECIMAL(5,2),    -- Sharpe ratio
    max_drawdown_pct DECIMAL(5,2), -- Maximum drawdown percentage
    total_trades INTEGER,          -- Total trades in backtest
    
    -- Strategy status
    is_active BOOLEAN DEFAULT TRUE,
    is_validated BOOLEAN DEFAULT FALSE,  -- Passed validation thresholds
    validation_date DATE,
    
    -- Evolution tracking
    parent_strategy_id INTEGER REFERENCES trading_strategies(strategy_id) ON DELETE SET NULL,
    improvement_notes TEXT,        -- What was improved in this version
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_backtest_date DATE,
    
    UNIQUE(strategy_name, strategy_version)
);

CREATE INDEX IF NOT EXISTS idx_strategies_name ON trading_strategies(strategy_name);
CREATE INDEX IF NOT EXISTS idx_strategies_active ON trading_strategies(is_active);
CREATE INDEX IF NOT EXISTS idx_strategies_validated ON trading_strategies(is_validated);
CREATE INDEX IF NOT EXISTS idx_strategies_win_rate ON trading_strategies(win_rate DESC);

-- ============================================================================
-- STRATEGY PERFORMANCE TRACKING
-- ============================================================================
-- Tracks how strategies perform in live trading

CREATE TABLE IF NOT EXISTS strategy_performance (
    performance_id BIGSERIAL PRIMARY KEY,
    strategy_id INTEGER NOT NULL REFERENCES trading_strategies(strategy_id) ON DELETE CASCADE,
    analysis_id BIGINT REFERENCES analyses(analysis_id) ON DELETE SET NULL,
    
    -- When strategy was applied
    applied_date DATE NOT NULL,
    ticker_id INTEGER REFERENCES tickers(ticker_id) ON DELETE CASCADE,
    
    -- Strategy decision
    strategy_decision VARCHAR(10),  -- 'BUY', 'WAIT', 'PASS'
    confidence_score INTEGER,      -- Confidence at time of application
    
    -- Outcome tracking
    entry_price DECIMAL(10,2),
    exit_price DECIMAL(10,2),
    return_pct DECIMAL(7,2),
    holding_days INTEGER,
    
    -- Performance comparison
    expected_return_pct DECIMAL(7,2),
    beat_expectations BOOLEAN,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_strategy_perf_strategy ON strategy_performance(strategy_id, applied_date DESC);
CREATE INDEX IF NOT EXISTS idx_strategy_perf_ticker ON strategy_performance(ticker_id);

-- ============================================================================
-- STRATEGY EVOLUTION TRACKING
-- ============================================================================
-- Tracks how strategies evolve over time

CREATE TABLE IF NOT EXISTS strategy_evolution (
    evolution_id SERIAL PRIMARY KEY,
    strategy_id INTEGER NOT NULL REFERENCES trading_strategies(strategy_id) ON DELETE CASCADE,
    
    -- Evolution details
    evolution_type VARCHAR(50),    -- 'THRESHOLD_ADJUSTMENT', 'INDICATOR_ADD', 'SECTOR_FOCUS_CHANGE'
    change_description TEXT,
    previous_value JSONB,
    new_value JSONB,
    
    -- Performance impact
    performance_before JSONB,      -- Metrics before change
    performance_after JSONB,       -- Metrics after change
    improvement_pct DECIMAL(5,2),  -- Improvement percentage
    
    -- Metadata
    evolved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    evolved_by VARCHAR(100) DEFAULT 'system'  -- 'system' or 'user'
);

CREATE INDEX IF NOT EXISTS idx_strategy_evolution_strategy ON strategy_evolution(strategy_id, evolved_at DESC);

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View: Top Performing Strategies
CREATE OR REPLACE VIEW v_top_strategies AS
SELECT 
    strategy_id,
    strategy_name,
    strategy_version,
    win_rate,
    avg_return_pct,
    sharpe_ratio,
    max_drawdown_pct,
    total_trades,
    is_active,
    is_validated,
    last_backtest_date
FROM trading_strategies
WHERE is_active = TRUE
    AND is_validated = TRUE
ORDER BY 
    (win_rate * 0.4 + avg_return_pct * 0.3 + sharpe_ratio * 10 * 0.3) DESC;

-- View: Strategy Performance Summary
CREATE OR REPLACE VIEW v_strategy_performance_summary AS
SELECT 
    s.strategy_id,
    s.strategy_name,
    s.strategy_version,
    COUNT(sp.performance_id) as live_trades,
    AVG(sp.return_pct) as avg_live_return,
    SUM(CASE WHEN sp.return_pct > 0 THEN 1 ELSE 0 END)::FLOAT / 
        NULLIF(COUNT(sp.performance_id), 0) * 100 as live_win_rate,
    s.win_rate as backtest_win_rate,
    s.avg_return_pct as backtest_avg_return
FROM trading_strategies s
LEFT JOIN strategy_performance sp ON s.strategy_id = sp.strategy_id
WHERE s.is_active = TRUE
GROUP BY s.strategy_id, s.strategy_name, s.strategy_version, 
         s.win_rate, s.avg_return_pct
ORDER BY live_win_rate DESC NULLS LAST;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function: Update strategy timestamp
CREATE OR REPLACE FUNCTION update_strategy_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_strategy_timestamp
    BEFORE UPDATE ON trading_strategies
    FOR EACH ROW
    EXECUTE FUNCTION update_strategy_timestamp();

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE trading_strategies IS 'Trading strategies stored as reusable templates';
COMMENT ON TABLE strategy_performance IS 'Live performance tracking for strategies';
COMMENT ON TABLE strategy_evolution IS 'Evolution history of strategies';

COMMENT ON VIEW v_top_strategies IS 'Top performing validated strategies';
COMMENT ON VIEW v_strategy_performance_summary IS 'Summary of strategy performance (backtest vs live)';

-- ============================================================================
-- DEFAULT STRATEGY (Four-Gate Framework)
-- ============================================================================

INSERT INTO trading_strategies (
    strategy_name,
    strategy_description,
    indicator_combination,
    gate_thresholds,
    min_confidence,
    holding_period_days,
    is_active,
    is_validated
) VALUES (
    'Four-Gate Framework',
    'Systematic four-gate buy decision framework with fundamental, technical, risk, and timing gates',
    '{"rsi": true, "macd": true, "moving_averages": true, "volume": true, "fundamentals": true}',
    '{"fundamental_min_score": 70, "technical_min_score": 65, "risk_min_score": 70, "timing_min_score": 60}',
    70,
    30,
    TRUE,
    FALSE  -- Needs backtesting to validate
) ON CONFLICT (strategy_name, strategy_version) DO NOTHING;

