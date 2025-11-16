-- Migration: Add Portfolio Tracking Tables
-- Phase 5: Portfolio Management
-- Created: 2025-11-16

-- ============================================================================
-- 1. PORTFOLIO CONFIGURATION
-- ============================================================================
-- Stores user's portfolio settings and risk preferences
CREATE TABLE IF NOT EXISTS portfolio_config (
    config_id SERIAL PRIMARY KEY,
    portfolio_value DECIMAL(15, 2) NOT NULL,           -- Total portfolio value (e.g., $100,000)
    max_position_pct DECIMAL(5, 2) DEFAULT 10.00,      -- Max % per stock (e.g., 10%)
    risk_tolerance VARCHAR(20) DEFAULT 'moderate',      -- 'conservative', 'moderate', 'aggressive'
    cash_reserve_pct DECIMAL(5, 2) DEFAULT 10.00,      -- % to keep in cash (e.g., 10%)
    sector_limits JSONB,                                -- Optional sector allocation limits
    is_active BOOLEAN DEFAULT true,                     -- Only one config should be active
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_portfolio_value CHECK (portfolio_value > 0),
    CONSTRAINT valid_max_position CHECK (max_position_pct > 0 AND max_position_pct <= 100),
    CONSTRAINT valid_risk_tolerance CHECK (risk_tolerance IN ('conservative', 'moderate', 'aggressive')),
    CONSTRAINT valid_cash_reserve CHECK (cash_reserve_pct >= 0 AND cash_reserve_pct <= 100)
);

-- Ensure only one active config at a time
CREATE UNIQUE INDEX idx_active_portfolio_config ON portfolio_config(is_active) WHERE is_active = true;

CREATE INDEX idx_portfolio_config_created ON portfolio_config(created_at DESC);

-- ============================================================================
-- 2. PORTFOLIO HOLDINGS
-- ============================================================================
-- Tracks actual stock positions
CREATE TABLE IF NOT EXISTS portfolio_holdings (
    holding_id SERIAL PRIMARY KEY,
    ticker_id INTEGER NOT NULL REFERENCES tickers(ticker_id) ON DELETE CASCADE,
    shares DECIMAL(15, 4) NOT NULL,                     -- Number of shares owned
    avg_cost_basis DECIMAL(10, 2) NOT NULL,             -- Average purchase price per share
    acquisition_date DATE NOT NULL,                      -- Date of initial purchase
    current_price DECIMAL(10, 2),                       -- Latest price (updated daily)
    current_value DECIMAL(15, 2),                       -- shares * current_price
    unrealized_gain DECIMAL(15, 2),                     -- current_value - (shares * avg_cost_basis)
    unrealized_gain_pct DECIMAL(7, 2),                  -- Percentage gain/loss
    is_open BOOLEAN DEFAULT true,                       -- false when position is closed
    closed_date DATE,                                    -- Date position was fully closed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_shares CHECK (shares >= 0),
    CONSTRAINT valid_cost_basis CHECK (avg_cost_basis > 0),
    CONSTRAINT valid_current_price CHECK (current_price IS NULL OR current_price > 0)
);

CREATE INDEX idx_holdings_ticker ON portfolio_holdings(ticker_id);
CREATE INDEX idx_holdings_open ON portfolio_holdings(is_open) WHERE is_open = true;
CREATE INDEX idx_holdings_acquisition ON portfolio_holdings(acquisition_date DESC);

-- Unique constraint: Only one open position per ticker
CREATE UNIQUE INDEX idx_unique_open_holding ON portfolio_holdings(ticker_id) WHERE is_open = true;

-- ============================================================================
-- 3. TRADE EXECUTIONS
-- ============================================================================
-- Logs all buy/sell transactions
CREATE TABLE IF NOT EXISTS trade_executions (
    execution_id SERIAL PRIMARY KEY,
    ticker_id INTEGER NOT NULL REFERENCES tickers(ticker_id) ON DELETE CASCADE,
    trade_type VARCHAR(10) NOT NULL,                    -- 'BUY' or 'SELL'
    shares DECIMAL(15, 4) NOT NULL,                     -- Number of shares traded
    price DECIMAL(10, 2) NOT NULL,                      -- Execution price per share
    total_value DECIMAL(15, 2) NOT NULL,                -- shares * price (+ fees if tracked)
    fees DECIMAL(10, 2) DEFAULT 0.00,                   -- Trading fees/commissions
    execution_date TIMESTAMP NOT NULL,                  -- When the trade was executed
    related_analysis_id BIGINT REFERENCES analyses(analysis_id),  -- Links to the analysis that recommended it
    notes TEXT,                                          -- Optional notes about the trade
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_trade_type CHECK (trade_type IN ('BUY', 'SELL')),
    CONSTRAINT valid_shares CHECK (shares > 0),
    CONSTRAINT valid_price CHECK (price > 0),
    CONSTRAINT valid_total CHECK (total_value > 0),
    CONSTRAINT valid_fees CHECK (fees >= 0)
);

CREATE INDEX idx_executions_ticker ON trade_executions(ticker_id);
CREATE INDEX idx_executions_date ON trade_executions(execution_date DESC);
CREATE INDEX idx_executions_type ON trade_executions(trade_type);
CREATE INDEX idx_executions_analysis ON trade_executions(related_analysis_id);

-- ============================================================================
-- 4. POSITION RECOMMENDATIONS
-- ============================================================================
-- Stores AI-generated position sizing recommendations
CREATE TABLE IF NOT EXISTS position_recommendations (
    recommendation_id SERIAL PRIMARY KEY,
    analysis_id BIGINT NOT NULL REFERENCES analyses(analysis_id) ON DELETE CASCADE,
    ticker_id INTEGER NOT NULL REFERENCES tickers(ticker_id) ON DELETE CASCADE,
    recommendation_date DATE NOT NULL,

    -- Position sizing
    recommended_shares INTEGER,                          -- Number of shares to buy
    recommended_amount DECIMAL(15, 2),                   -- Dollar amount to invest
    position_size_pct DECIMAL(5, 2),                     -- % of portfolio (e.g., 5.0%)

    -- Price targets
    entry_price DECIMAL(10, 2),                          -- Recommended entry price
    target_price DECIMAL(10, 2),                         -- Price target for profit
    stop_loss DECIMAL(10, 2),                            -- Stop loss price

    -- Expected performance
    expected_return_pct DECIMAL(7, 2),                   -- Expected return %
    expected_timeframe VARCHAR(50),                      -- e.g., "3-6 months"
    risk_reward_ratio DECIMAL(5, 2),                     -- Risk/Reward ratio

    -- Timing
    timing_signal VARCHAR(20),                           -- 'BUY_NOW', 'WAIT_FOR_DIP', 'WAIT_FOR_BREAKOUT'
    timing_notes TEXT,                                   -- Explanation of timing recommendation

    -- Reasoning
    reasoning TEXT,                                      -- Why this position size?

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_position_pct CHECK (position_size_pct >= 0 AND position_size_pct <= 100),
    CONSTRAINT valid_entry_price CHECK (entry_price IS NULL OR entry_price > 0),
    CONSTRAINT valid_target_price CHECK (target_price IS NULL OR target_price > 0),
    CONSTRAINT valid_stop_loss CHECK (stop_loss IS NULL OR stop_loss > 0),
    CONSTRAINT valid_timing_signal CHECK (timing_signal IN ('BUY_NOW', 'WAIT_FOR_DIP', 'WAIT_FOR_BREAKOUT', 'WAIT'))
);

CREATE INDEX idx_recommendations_analysis ON position_recommendations(analysis_id);
CREATE INDEX idx_recommendations_ticker ON position_recommendations(ticker_id);
CREATE INDEX idx_recommendations_date ON position_recommendations(recommendation_date DESC);
CREATE INDEX idx_recommendations_timing ON position_recommendations(timing_signal);

-- ============================================================================
-- 5. PERFORMANCE SNAPSHOTS
-- ============================================================================
-- Daily snapshots of portfolio performance
CREATE TABLE IF NOT EXISTS performance_snapshots (
    snapshot_id SERIAL PRIMARY KEY,
    snapshot_date DATE NOT NULL UNIQUE,                  -- Date of snapshot

    -- Portfolio metrics
    total_value DECIMAL(15, 2) NOT NULL,                -- Total portfolio value
    cash_balance DECIMAL(15, 2) NOT NULL,               -- Available cash
    invested_value DECIMAL(15, 2) NOT NULL,             -- Total value in stocks

    -- Performance metrics
    unrealized_gains DECIMAL(15, 2),                    -- Total unrealized gains/losses
    unrealized_gains_pct DECIMAL(7, 2),                 -- % unrealized gains
    realized_gains_ytd DECIMAL(15, 2),                  -- Realized gains this year
    dividend_income_ytd DECIMAL(15, 2),                 -- Dividend income this year

    -- Benchmark comparison
    benchmark_value DECIMAL(15, 2),                     -- What $X would be worth in S&P 500
    benchmark_return_pct DECIMAL(7, 2),                 -- S&P 500 return %
    alpha DECIMAL(7, 2),                                -- Portfolio return - benchmark return

    -- Holdings summary
    num_positions INTEGER,                               -- Number of open positions
    top_holding_ticker VARCHAR(10),                      -- Ticker of largest position
    top_holding_pct DECIMAL(5, 2),                       -- % of portfolio in top holding

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_total_value CHECK (total_value >= 0),
    CONSTRAINT valid_cash CHECK (cash_balance >= 0),
    CONSTRAINT valid_invested CHECK (invested_value >= 0),
    CONSTRAINT valid_num_positions CHECK (num_positions >= 0)
);

CREATE INDEX idx_snapshots_date ON performance_snapshots(snapshot_date DESC);

-- ============================================================================
-- 6. SECTOR ALLOCATIONS (Optional, for rebalancing)
-- ============================================================================
-- Track sector exposure over time
CREATE TABLE IF NOT EXISTS sector_allocations (
    allocation_id SERIAL PRIMARY KEY,
    snapshot_date DATE NOT NULL,
    sector VARCHAR(50) NOT NULL,
    sector_value DECIMAL(15, 2) NOT NULL,               -- Total value in this sector
    sector_pct DECIMAL(5, 2) NOT NULL,                   -- % of portfolio
    num_holdings INTEGER NOT NULL,                       -- Number of stocks in sector
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_sector_value CHECK (sector_value >= 0),
    CONSTRAINT valid_sector_pct CHECK (sector_pct >= 0 AND sector_pct <= 100)
);

CREATE INDEX idx_sector_allocations_date ON sector_allocations(snapshot_date DESC);
CREATE INDEX idx_sector_allocations_sector ON sector_allocations(sector);

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update portfolio_config.updated_at on UPDATE
CREATE OR REPLACE FUNCTION update_portfolio_config_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_portfolio_config_updated
    BEFORE UPDATE ON portfolio_config
    FOR EACH ROW
    EXECUTE FUNCTION update_portfolio_config_timestamp();

-- Function to update portfolio_holdings.updated_at on UPDATE
CREATE OR REPLACE FUNCTION update_portfolio_holdings_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_portfolio_holdings_updated
    BEFORE UPDATE ON portfolio_holdings
    FOR EACH ROW
    EXECUTE FUNCTION update_portfolio_holdings_timestamp();

-- Function to automatically calculate derived fields in portfolio_holdings
CREATE OR REPLACE FUNCTION calculate_holding_metrics()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculate current_value if current_price is set
    IF NEW.current_price IS NOT NULL THEN
        NEW.current_value = NEW.shares * NEW.current_price;
        NEW.unrealized_gain = NEW.current_value - (NEW.shares * NEW.avg_cost_basis);
        NEW.unrealized_gain_pct = (NEW.unrealized_gain / (NEW.shares * NEW.avg_cost_basis)) * 100;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_calculate_holding_metrics
    BEFORE INSERT OR UPDATE ON portfolio_holdings
    FOR EACH ROW
    EXECUTE FUNCTION calculate_holding_metrics();

-- ============================================================================
-- SAMPLE DATA (for testing)
-- ============================================================================

-- Insert a default portfolio configuration (commented out - user will run init command)
-- INSERT INTO portfolio_config (portfolio_value, max_position_pct, risk_tolerance, cash_reserve_pct)
-- VALUES (100000.00, 10.00, 'moderate', 10.00);

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check that tables were created
-- SELECT table_name FROM information_schema.tables
-- WHERE table_schema = 'public'
-- AND table_name IN ('portfolio_config', 'portfolio_holdings', 'trade_executions', 'position_recommendations', 'performance_snapshots', 'sector_allocations')
-- ORDER BY table_name;

-- ============================================================================
-- ROLLBACK (if needed)
-- ============================================================================

-- DROP TABLE IF EXISTS sector_allocations CASCADE;
-- DROP TABLE IF EXISTS performance_snapshots CASCADE;
-- DROP TABLE IF EXISTS position_recommendations CASCADE;
-- DROP TABLE IF EXISTS trade_executions CASCADE;
-- DROP TABLE IF EXISTS portfolio_holdings CASCADE;
-- DROP TABLE IF EXISTS portfolio_config CASCADE;
-- DROP FUNCTION IF EXISTS update_portfolio_config_timestamp() CASCADE;
-- DROP FUNCTION IF EXISTS update_portfolio_holdings_timestamp() CASCADE;
-- DROP FUNCTION IF EXISTS calculate_holding_metrics() CASCADE;
