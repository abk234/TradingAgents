-- Migration: Add Portfolio Tracking Tables
-- Phase 5: Portfolio Tracking
-- Date: 2025-11-16

-- ============================================================================
-- Portfolio Configuration
-- ============================================================================

CREATE TABLE IF NOT EXISTS portfolio_config (
    config_id SERIAL PRIMARY KEY,
    portfolio_value DECIMAL(15, 2) NOT NULL,
    max_position_pct DECIMAL(5, 2) DEFAULT 10.0,
    risk_tolerance VARCHAR(20) DEFAULT 'moderate',
    cash_reserve_pct DECIMAL(5, 2) DEFAULT 20.0,
    sector_limits JSONB,
    notes TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE portfolio_config IS 'Portfolio configuration and risk parameters';
COMMENT ON COLUMN portfolio_config.portfolio_value IS 'Total portfolio value in USD';
COMMENT ON COLUMN portfolio_config.max_position_pct IS 'Maximum position size as % of portfolio';
COMMENT ON COLUMN portfolio_config.risk_tolerance IS 'conservative, moderate, or aggressive';
COMMENT ON COLUMN portfolio_config.cash_reserve_pct IS 'Minimum cash reserve as % of portfolio';

-- ============================================================================
-- Position Recommendations
-- ============================================================================

CREATE TABLE IF NOT EXISTS position_recommendations (
    recommendation_id SERIAL PRIMARY KEY,
    analysis_id BIGINT REFERENCES analyses(analysis_id) ON DELETE CASCADE,
    ticker_id INTEGER REFERENCES tickers(ticker_id),

    -- Position sizing
    recommended_shares INTEGER,
    recommended_amount DECIMAL(15, 2),
    position_size_pct DECIMAL(5, 2),

    -- Price targets
    entry_price DECIMAL(10, 2),
    target_price DECIMAL(10, 2),
    stop_loss DECIMAL(10, 2),

    -- Expected returns
    expected_return_pct DECIMAL(7, 2),
    expected_timeframe_days INTEGER,
    risk_reward_ratio DECIMAL(5, 2),

    -- Entry timing
    timing_recommendation VARCHAR(50), -- 'BUY_NOW', 'WAIT_FOR_DIP', 'WAIT_FOR_BREAKOUT', 'WAIT'
    ideal_entry_min DECIMAL(10, 2),
    ideal_entry_max DECIMAL(10, 2),
    timing_reasoning TEXT,

    -- General reasoning
    sizing_reasoning TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE position_recommendations IS 'Position sizing and entry timing recommendations';
COMMENT ON COLUMN position_recommendations.timing_recommendation IS 'BUY_NOW, WAIT_FOR_DIP, WAIT_FOR_BREAKOUT, or WAIT';

-- ============================================================================
-- Portfolio Holdings
-- ============================================================================

CREATE TABLE IF NOT EXISTS portfolio_holdings (
    holding_id SERIAL PRIMARY KEY,
    ticker_id INTEGER REFERENCES tickers(ticker_id) NOT NULL,

    -- Position details
    shares DECIMAL(15, 4) NOT NULL,
    avg_cost_basis DECIMAL(10, 2) NOT NULL,
    total_cost DECIMAL(15, 2) NOT NULL,

    -- Dates
    acquisition_date DATE NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Status
    is_open BOOLEAN DEFAULT true,
    closed_date DATE,

    -- Metadata
    notes TEXT,
    related_analysis_id BIGINT REFERENCES analyses(analysis_id),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT positive_shares CHECK (shares > 0),
    CONSTRAINT positive_cost_basis CHECK (avg_cost_basis > 0)
);

COMMENT ON TABLE portfolio_holdings IS 'Current and historical portfolio positions';

-- ============================================================================
-- Trade Executions
-- ============================================================================

CREATE TABLE IF NOT EXISTS trade_executions (
    execution_id SERIAL PRIMARY KEY,
    ticker_id INTEGER REFERENCES tickers(ticker_id) NOT NULL,

    -- Trade details
    trade_type VARCHAR(10) NOT NULL, -- 'BUY', 'SELL'
    shares DECIMAL(15, 4) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    total_value DECIMAL(15, 2) NOT NULL,
    fees DECIMAL(10, 2) DEFAULT 0,

    -- Execution details
    execution_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    execution_method VARCHAR(50), -- 'MARKET', 'LIMIT', 'STOP'

    -- Links
    related_analysis_id BIGINT REFERENCES analyses(analysis_id),
    related_recommendation_id INTEGER REFERENCES position_recommendations(recommendation_id),
    holding_id INTEGER REFERENCES portfolio_holdings(holding_id),

    -- Metadata
    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_trade_type CHECK (trade_type IN ('BUY', 'SELL')),
    CONSTRAINT positive_shares_trade CHECK (shares > 0),
    CONSTRAINT positive_price CHECK (price > 0)
);

COMMENT ON TABLE trade_executions IS 'Historical record of all trade executions';

-- ============================================================================
-- Performance Snapshots
-- ============================================================================

CREATE TABLE IF NOT EXISTS performance_snapshots (
    snapshot_id SERIAL PRIMARY KEY,
    snapshot_date DATE NOT NULL UNIQUE,

    -- Portfolio values
    total_value DECIMAL(15, 2) NOT NULL,
    cash_balance DECIMAL(15, 2) NOT NULL,
    invested_value DECIMAL(15, 2) NOT NULL,

    -- Gains/losses
    total_cost_basis DECIMAL(15, 2),
    unrealized_gains DECIMAL(15, 2),
    unrealized_gains_pct DECIMAL(7, 2),
    realized_gains_ytd DECIMAL(15, 2),

    -- Income
    dividend_income_ytd DECIMAL(15, 2) DEFAULT 0,

    -- Benchmarks
    portfolio_return_pct DECIMAL(7, 2),
    sp500_return_pct DECIMAL(7, 2),
    alpha DECIMAL(7, 2),

    -- Risk metrics
    beta DECIMAL(5, 2),
    sharpe_ratio DECIMAL(5, 2),
    max_drawdown_pct DECIMAL(7, 2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE performance_snapshots IS 'Daily portfolio performance snapshots';
COMMENT ON COLUMN performance_snapshots.alpha IS 'Excess return vs S&P 500';

-- ============================================================================
-- Indexes
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_portfolio_config_active ON portfolio_config(is_active) WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_position_recommendations_analysis ON position_recommendations(analysis_id);
CREATE INDEX IF NOT EXISTS idx_position_recommendations_ticker ON position_recommendations(ticker_id);

CREATE INDEX IF NOT EXISTS idx_portfolio_holdings_ticker ON portfolio_holdings(ticker_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_holdings_open ON portfolio_holdings(is_open) WHERE is_open = true;
CREATE INDEX IF NOT EXISTS idx_portfolio_holdings_acquisition ON portfolio_holdings(acquisition_date);

CREATE INDEX IF NOT EXISTS idx_trade_executions_ticker ON trade_executions(ticker_id);
CREATE INDEX IF NOT EXISTS idx_trade_executions_date ON trade_executions(execution_date);
CREATE INDEX IF NOT EXISTS idx_trade_executions_type ON trade_executions(trade_type);

CREATE INDEX IF NOT EXISTS idx_performance_snapshots_date ON performance_snapshots(snapshot_date);

-- ============================================================================
-- End of migration
-- ============================================================================
