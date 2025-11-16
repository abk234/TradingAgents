-- Migration 009: Add Portfolio Optimization Tables
-- Date: 2025-11-16
-- Purpose: Support sector rebalancing, tax-loss harvesting, and portfolio optimization

-- ============================================================================
-- SECTOR ALLOCATION TARGETS TABLE
-- ============================================================================
-- Stores target sector allocations for portfolio
CREATE TABLE IF NOT EXISTS sector_allocation_targets (
    target_id SERIAL PRIMARY KEY,
    sector VARCHAR(100) NOT NULL,
    target_allocation_pct DECIMAL(5, 2) NOT NULL,
    min_allocation_pct DECIMAL(5, 2),
    max_allocation_pct DECIMAL(5, 2),
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(sector),
    CHECK (target_allocation_pct >= 0 AND target_allocation_pct <= 100),
    CHECK (min_allocation_pct IS NULL OR (min_allocation_pct >= 0 AND min_allocation_pct <= target_allocation_pct)),
    CHECK (max_allocation_pct IS NULL OR (max_allocation_pct >= target_allocation_pct AND max_allocation_pct <= 100))
);

-- Index for sector allocation targets
CREATE INDEX idx_sector_targets_active ON sector_allocation_targets(is_active);

-- ============================================================================
-- REBALANCING RECOMMENDATIONS TABLE
-- ============================================================================
-- Stores portfolio rebalancing recommendations
CREATE TABLE IF NOT EXISTS rebalancing_recommendations (
    recommendation_id SERIAL PRIMARY KEY,
    recommendation_date DATE NOT NULL DEFAULT CURRENT_DATE,

    -- Current portfolio state
    total_portfolio_value DECIMAL(15, 2) NOT NULL,

    -- Rebalancing metadata
    rebalancing_type VARCHAR(50), -- SECTOR, ASSET_CLASS, TAX_LOSS, OPPORTUNISTIC
    trigger_reason TEXT,
    urgency_level VARCHAR(20), -- LOW, MEDIUM, HIGH, URGENT

    -- Recommendations summary
    total_trades_recommended INTEGER,
    total_sell_value DECIMAL(15, 2),
    total_buy_value DECIMAL(15, 2),
    estimated_cost DECIMAL(10, 2), -- Trading fees
    estimated_tax_impact DECIMAL(15, 2), -- Capital gains tax

    -- Execution tracking
    status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, APPROVED, EXECUTED, REJECTED
    executed_date DATE,
    execution_notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CHECK (total_portfolio_value > 0)
);

-- Indexes for rebalancing recommendations
CREATE INDEX idx_rebalancing_date ON rebalancing_recommendations(recommendation_date DESC);
CREATE INDEX idx_rebalancing_status ON rebalancing_recommendations(status);
CREATE INDEX idx_rebalancing_type ON rebalancing_recommendations(rebalancing_type);

-- ============================================================================
-- REBALANCING TRADES TABLE
-- ============================================================================
-- Individual trade recommendations for rebalancing
CREATE TABLE IF NOT EXISTS rebalancing_trades (
    trade_id SERIAL PRIMARY KEY,
    recommendation_id INTEGER NOT NULL REFERENCES rebalancing_recommendations(recommendation_id) ON DELETE CASCADE,
    ticker_id INTEGER NOT NULL REFERENCES tickers(ticker_id) ON DELETE CASCADE,

    -- Trade details
    action VARCHAR(10) NOT NULL, -- BUY, SELL, HOLD
    shares DECIMAL(15, 4),
    estimated_price DECIMAL(10, 2),
    estimated_value DECIMAL(15, 2),

    -- Reasoning
    current_allocation_pct DECIMAL(7, 4),
    target_allocation_pct DECIMAL(7, 4),
    allocation_delta_pct DECIMAL(7, 4),
    reason TEXT,

    -- Execution tracking
    executed BOOLEAN DEFAULT FALSE,
    execution_price DECIMAL(10, 2),
    execution_date TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CHECK (action IN ('BUY', 'SELL', 'HOLD'))
);

-- Indexes for rebalancing trades
CREATE INDEX idx_rebalancing_trades_recommendation ON rebalancing_trades(recommendation_id);
CREATE INDEX idx_rebalancing_trades_ticker ON rebalancing_trades(ticker_id);
CREATE INDEX idx_rebalancing_trades_action ON rebalancing_trades(action);

-- ============================================================================
-- TAX LOSS HARVESTING OPPORTUNITIES TABLE
-- ============================================================================
-- Tracks tax-loss harvesting opportunities
CREATE TABLE IF NOT EXISTS tax_loss_opportunities (
    opportunity_id SERIAL PRIMARY KEY,
    ticker_id INTEGER NOT NULL REFERENCES tickers(ticker_id) ON DELETE CASCADE,
    holding_id INTEGER REFERENCES portfolio_holdings(holding_id) ON DELETE SET NULL,

    -- Opportunity details
    opportunity_date DATE NOT NULL DEFAULT CURRENT_DATE,
    current_price DECIMAL(10, 2) NOT NULL,
    cost_basis DECIMAL(10, 2) NOT NULL,
    unrealized_loss DECIMAL(15, 2) NOT NULL,
    unrealized_loss_pct DECIMAL(7, 2) NOT NULL,

    -- Shares and values
    shares DECIMAL(15, 4) NOT NULL,
    current_value DECIMAL(15, 2) NOT NULL,
    original_value DECIMAL(15, 2) NOT NULL,

    -- Tax benefit
    estimated_tax_benefit DECIMAL(15, 2),
    tax_rate_assumption DECIMAL(5, 2),

    -- Replacement suggestion
    replacement_ticker_id INTEGER REFERENCES tickers(ticker_id) ON DELETE SET NULL,
    replacement_reason TEXT,
    wash_sale_risk BOOLEAN DEFAULT FALSE,
    wash_sale_safe_date DATE,

    -- Status tracking
    status VARCHAR(20) DEFAULT 'IDENTIFIED', -- IDENTIFIED, HARVESTED, REJECTED, EXPIRED
    harvested_date DATE,
    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CHECK (unrealized_loss < 0),
    CHECK (shares > 0)
);

-- Indexes for tax loss opportunities
CREATE INDEX idx_tax_loss_ticker ON tax_loss_opportunities(ticker_id);
CREATE INDEX idx_tax_loss_date ON tax_loss_opportunities(opportunity_date DESC);
CREATE INDEX idx_tax_loss_status ON tax_loss_opportunities(status);
CREATE INDEX idx_tax_loss_unrealized ON tax_loss_opportunities(unrealized_loss);

-- ============================================================================
-- PORTFOLIO RISK METRICS TABLE
-- ============================================================================
-- Stores calculated risk metrics for portfolio and individual positions
CREATE TABLE IF NOT EXISTS portfolio_risk_metrics (
    metric_id SERIAL PRIMARY KEY,
    calculation_date DATE NOT NULL DEFAULT CURRENT_DATE,
    ticker_id INTEGER REFERENCES tickers(ticker_id) ON DELETE CASCADE, -- NULL for portfolio-level metrics

    -- Time period
    period_days INTEGER NOT NULL, -- 30, 90, 252 (1 year), etc.

    -- Return metrics
    total_return_pct DECIMAL(10, 4),
    annualized_return_pct DECIMAL(10, 4),

    -- Risk metrics
    volatility_pct DECIMAL(10, 4), -- Standard deviation
    downside_volatility_pct DECIMAL(10, 4), -- For Sortino ratio

    -- Risk-adjusted returns
    sharpe_ratio DECIMAL(10, 4),
    sortino_ratio DECIMAL(10, 4),
    calmar_ratio DECIMAL(10, 4),

    -- Drawdown metrics
    max_drawdown_pct DECIMAL(10, 4),
    max_drawdown_duration_days INTEGER,
    current_drawdown_pct DECIMAL(10, 4),

    -- Market correlation (for individual stocks)
    beta DECIMAL(10, 6),
    alpha_pct DECIMAL(10, 4),
    correlation DECIMAL(10, 6),
    r_squared DECIMAL(10, 6),

    -- Value at Risk
    var_95_pct DECIMAL(10, 4), -- 95% VaR
    var_99_pct DECIMAL(10, 4), -- 99% VaR
    cvar_95_pct DECIMAL(10, 4), -- Conditional VaR (expected shortfall)

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(calculation_date, ticker_id, period_days)
);

-- Indexes for risk metrics
CREATE INDEX idx_risk_metrics_date ON portfolio_risk_metrics(calculation_date DESC);
CREATE INDEX idx_risk_metrics_ticker ON portfolio_risk_metrics(ticker_id);
CREATE INDEX idx_risk_metrics_period ON portfolio_risk_metrics(period_days);

-- ============================================================================
-- PORTFOLIO OPTIMIZATION RESULTS TABLE
-- ============================================================================
-- Stores results from portfolio optimization (MPT, etc.)
CREATE TABLE IF NOT EXISTS portfolio_optimization_results (
    optimization_id SERIAL PRIMARY KEY,
    optimization_date DATE NOT NULL DEFAULT CURRENT_DATE,

    -- Optimization parameters
    optimization_method VARCHAR(50), -- MEAN_VARIANCE, BLACK_LITTERMAN, RISK_PARITY, etc.
    objective VARCHAR(50), -- MAX_SHARPE, MIN_VARIANCE, MAX_RETURN, TARGET_RISK

    -- Constraints
    constraints JSONB, -- Store constraints as JSON

    -- Current portfolio
    current_portfolio JSONB, -- Current allocations
    current_expected_return DECIMAL(10, 4),
    current_volatility DECIMAL(10, 4),
    current_sharpe_ratio DECIMAL(10, 4),

    -- Optimized portfolio
    optimized_portfolio JSONB, -- Recommended allocations
    optimized_expected_return DECIMAL(10, 4),
    optimized_volatility DECIMAL(10, 4),
    optimized_sharpe_ratio DECIMAL(10, 4),

    -- Improvement metrics
    improvement_return_pct DECIMAL(10, 4),
    improvement_volatility_pct DECIMAL(10, 4),
    improvement_sharpe DECIMAL(10, 4),

    -- Execution
    status VARCHAR(20) DEFAULT 'PENDING',
    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for optimization results
CREATE INDEX idx_optimization_date ON portfolio_optimization_results(optimization_date DESC);
CREATE INDEX idx_optimization_method ON portfolio_optimization_results(optimization_method);
CREATE INDEX idx_optimization_status ON portfolio_optimization_results(status);

-- ============================================================================
-- VIEWS FOR EASY QUERYING
-- ============================================================================

-- View: Current Sector Allocations
CREATE OR REPLACE VIEW v_current_sector_allocations AS
SELECT
    t.sector,
    COUNT(*) as position_count,
    SUM(ph.shares * ph.avg_cost_basis) as total_value,
    (SUM(ph.shares * ph.avg_cost_basis) /
     NULLIF((SELECT SUM(shares * avg_cost_basis) FROM portfolio_holdings WHERE is_open = TRUE), 0) * 100
    ) as current_allocation_pct
FROM portfolio_holdings ph
JOIN tickers t ON ph.ticker_id = t.ticker_id
WHERE ph.is_open = TRUE
GROUP BY t.sector
ORDER BY total_value DESC;

-- View: Sector Rebalancing Needs
CREATE OR REPLACE VIEW v_sector_rebalancing_needs AS
SELECT
    COALESCE(csa.sector, sat.sector) as sector,
    sat.target_allocation_pct,
    COALESCE(csa.current_allocation_pct, 0) as current_allocation_pct,
    sat.target_allocation_pct - COALESCE(csa.current_allocation_pct, 0) as allocation_delta_pct,
    CASE
        WHEN ABS(sat.target_allocation_pct - COALESCE(csa.current_allocation_pct, 0)) > 5 THEN 'HIGH'
        WHEN ABS(sat.target_allocation_pct - COALESCE(csa.current_allocation_pct, 0)) > 2 THEN 'MEDIUM'
        ELSE 'LOW'
    END as rebalancing_priority
FROM sector_allocation_targets sat
FULL OUTER JOIN v_current_sector_allocations csa ON sat.sector = csa.sector
WHERE sat.is_active = TRUE OR csa.sector IS NOT NULL
ORDER BY ABS(sat.target_allocation_pct - COALESCE(csa.current_allocation_pct, 0)) DESC;

-- View: Active Tax Loss Opportunities
CREATE OR REPLACE VIEW v_active_tax_loss_opportunities AS
SELECT
    t.symbol,
    t.company_name,
    tlo.unrealized_loss,
    tlo.unrealized_loss_pct,
    tlo.estimated_tax_benefit,
    tlo.wash_sale_risk,
    tlo.wash_sale_safe_date,
    rt.symbol as replacement_symbol,
    tlo.opportunity_date,
    tlo.status
FROM tax_loss_opportunities tlo
JOIN tickers t ON tlo.ticker_id = t.ticker_id
LEFT JOIN tickers rt ON tlo.replacement_ticker_id = rt.ticker_id
WHERE tlo.status = 'IDENTIFIED'
ORDER BY tlo.unrealized_loss ASC;

-- View: Portfolio Risk Summary
CREATE OR REPLACE VIEW v_portfolio_risk_summary AS
SELECT
    calculation_date,
    period_days,
    annualized_return_pct,
    volatility_pct,
    sharpe_ratio,
    sortino_ratio,
    max_drawdown_pct,
    current_drawdown_pct,
    var_95_pct,
    cvar_95_pct
FROM portfolio_risk_metrics
WHERE ticker_id IS NULL  -- Portfolio-level only
ORDER BY calculation_date DESC, period_days DESC;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Trigger: Update sector_allocation_targets timestamp
CREATE OR REPLACE FUNCTION update_sector_targets_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_sector_targets_timestamp
    BEFORE UPDATE ON sector_allocation_targets
    FOR EACH ROW
    EXECUTE FUNCTION update_sector_targets_timestamp();

-- Trigger: Update rebalancing_recommendations timestamp
CREATE OR REPLACE FUNCTION update_rebalancing_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_rebalancing_timestamp
    BEFORE UPDATE ON rebalancing_recommendations
    FOR EACH ROW
    EXECUTE FUNCTION update_rebalancing_timestamp();

-- Trigger: Update tax_loss_opportunities timestamp
CREATE OR REPLACE FUNCTION update_tax_loss_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_tax_loss_timestamp
    BEFORE UPDATE ON tax_loss_opportunities
    FOR EACH ROW
    EXECUTE FUNCTION update_tax_loss_timestamp();

-- Trigger: Update portfolio_optimization_results timestamp
CREATE OR REPLACE FUNCTION update_optimization_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_optimization_timestamp
    BEFORE UPDATE ON portfolio_optimization_results
    FOR EACH ROW
    EXECUTE FUNCTION update_optimization_timestamp();

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE sector_allocation_targets IS 'Target sector allocations for portfolio rebalancing';
COMMENT ON TABLE rebalancing_recommendations IS 'Portfolio rebalancing recommendations and execution tracking';
COMMENT ON TABLE rebalancing_trades IS 'Individual trade recommendations for rebalancing';
COMMENT ON TABLE tax_loss_opportunities IS 'Tax-loss harvesting opportunities and wash sale tracking';
COMMENT ON TABLE portfolio_risk_metrics IS 'Risk metrics for portfolio and individual positions';
COMMENT ON TABLE portfolio_optimization_results IS 'Results from portfolio optimization algorithms';

COMMENT ON VIEW v_current_sector_allocations IS 'Current portfolio sector allocations';
COMMENT ON VIEW v_sector_rebalancing_needs IS 'Sector rebalancing priorities';
COMMENT ON VIEW v_active_tax_loss_opportunities IS 'Active tax-loss harvesting opportunities';
COMMENT ON VIEW v_portfolio_risk_summary IS 'Portfolio-level risk metrics summary';

-- ============================================================================
-- DEFAULT SECTOR TARGETS (Example - adjust as needed)
-- ============================================================================

INSERT INTO sector_allocation_targets (sector, target_allocation_pct, min_allocation_pct, max_allocation_pct) VALUES
    ('Technology', 30.0, 25.0, 35.0),
    ('Healthcare', 15.0, 10.0, 20.0),
    ('Financial Services', 15.0, 10.0, 20.0),
    ('Consumer Cyclical', 10.0, 5.0, 15.0),
    ('Consumer Defensive', 10.0, 5.0, 15.0),
    ('Industrials', 10.0, 5.0, 15.0),
    ('Energy', 5.0, 0.0, 10.0),
    ('Real Estate', 5.0, 0.0, 10.0)
ON CONFLICT (sector) DO NOTHING;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Verification query
SELECT
    'sector_allocation_targets' as table_name, COUNT(*) as row_count FROM sector_allocation_targets
UNION ALL
SELECT 'rebalancing_recommendations', COUNT(*) FROM rebalancing_recommendations
UNION ALL
SELECT 'rebalancing_trades', COUNT(*) FROM rebalancing_trades
UNION ALL
SELECT 'tax_loss_opportunities', COUNT(*) FROM tax_loss_opportunities
UNION ALL
SELECT 'portfolio_risk_metrics', COUNT(*) FROM portfolio_risk_metrics
UNION ALL
SELECT 'portfolio_optimization_results', COUNT(*) FROM portfolio_optimization_results;

COMMENT ON SCHEMA public IS 'Migration 009: Portfolio optimization tables created successfully';
