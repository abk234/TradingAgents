-- Phase 4: Portfolio Management Tables
-- Migration: 004_portfolio_management.sql
-- Description: Add tables for tracking portfolios, positions, transactions, dividends, and alerts

-- ============================================================================
-- PORTFOLIOS TABLE
-- ============================================================================
-- Stores different portfolios (users can have multiple portfolios)
CREATE TABLE IF NOT EXISTS portfolios (
    portfolio_id SERIAL PRIMARY KEY,
    portfolio_name VARCHAR(100) NOT NULL,
    description TEXT,
    initial_cash DECIMAL(15, 2) NOT NULL DEFAULT 0,
    current_cash DECIMAL(15, 2) NOT NULL DEFAULT 0,
    total_value DECIMAL(15, 2) DEFAULT 0, -- Cash + positions value
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Index for active portfolios
CREATE INDEX IF NOT EXISTS idx_portfolios_active ON portfolios(is_active);

-- ============================================================================
-- POSITIONS TABLE
-- ============================================================================
-- Stores current stock holdings in each portfolio
CREATE TABLE IF NOT EXISTS positions (
    position_id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(portfolio_id) ON DELETE CASCADE,
    ticker_id INTEGER NOT NULL REFERENCES tickers(ticker_id) ON DELETE RESTRICT,

    -- Position details
    shares DECIMAL(15, 6) NOT NULL DEFAULT 0,
    average_cost DECIMAL(15, 4) NOT NULL, -- Average price paid per share
    total_cost DECIMAL(15, 2) NOT NULL, -- Total amount invested

    -- Current values (updated daily)
    current_price DECIMAL(15, 4),
    current_value DECIMAL(15, 2), -- shares * current_price
    unrealized_gain_loss DECIMAL(15, 2), -- current_value - total_cost
    unrealized_gain_loss_pct DECIMAL(8, 4), -- (current_value - total_cost) / total_cost * 100

    -- Metadata
    first_purchase_date DATE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,

    UNIQUE(portfolio_id, ticker_id)
);

-- Indexes for positions
CREATE INDEX IF NOT EXISTS idx_positions_portfolio ON positions(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_positions_ticker ON positions(ticker_id);
CREATE INDEX IF NOT EXISTS idx_positions_active ON positions(portfolio_id, is_active);

-- ============================================================================
-- TRANSACTIONS TABLE
-- ============================================================================
-- Stores all buy/sell transactions
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(portfolio_id) ON DELETE CASCADE,
    ticker_id INTEGER NOT NULL REFERENCES tickers(ticker_id) ON DELETE RESTRICT,

    -- Transaction details
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('BUY', 'SELL', 'DIVIDEND')),
    transaction_date DATE NOT NULL,
    shares DECIMAL(15, 6) NOT NULL,
    price_per_share DECIMAL(15, 4) NOT NULL,
    total_amount DECIMAL(15, 2) NOT NULL, -- shares * price_per_share

    -- Fees and commissions
    commission DECIMAL(10, 2) DEFAULT 0,
    fees DECIMAL(10, 2) DEFAULT 0,

    -- For sells: realized gain/loss
    realized_gain_loss DECIMAL(15, 2),

    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for transactions
CREATE INDEX IF NOT EXISTS idx_transactions_portfolio ON transactions(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_transactions_ticker ON transactions(ticker_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type);

-- ============================================================================
-- DIVIDENDS TABLE
-- ============================================================================
-- Tracks dividend payments (past and expected)
CREATE TABLE IF NOT EXISTS dividends (
    dividend_id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(portfolio_id) ON DELETE CASCADE,
    ticker_id INTEGER NOT NULL REFERENCES tickers(ticker_id) ON DELETE RESTRICT,

    -- Dividend details
    ex_dividend_date DATE NOT NULL,
    payment_date DATE,
    dividend_per_share DECIMAL(10, 4) NOT NULL,
    shares_held DECIMAL(15, 6) NOT NULL,
    total_dividend DECIMAL(15, 2) NOT NULL, -- shares_held * dividend_per_share

    -- Status
    status VARCHAR(20) DEFAULT 'EXPECTED' CHECK (status IN ('EXPECTED', 'RECEIVED')),

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    received_at TIMESTAMP
);

-- Indexes for dividends
CREATE INDEX IF NOT EXISTS idx_dividends_portfolio ON dividends(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_dividends_ticker ON dividends(ticker_id);
CREATE INDEX IF NOT EXISTS idx_dividends_payment_date ON dividends(payment_date);
CREATE INDEX IF NOT EXISTS idx_dividends_status ON dividends(status);

-- ============================================================================
-- PRICE ALERTS TABLE
-- ============================================================================
-- Stop loss and target price alerts
CREATE TABLE IF NOT EXISTS price_alerts (
    alert_id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(portfolio_id) ON DELETE CASCADE,
    ticker_id INTEGER NOT NULL REFERENCES tickers(ticker_id) ON DELETE RESTRICT,

    -- Alert details
    alert_type VARCHAR(20) NOT NULL CHECK (alert_type IN ('STOP_LOSS', 'TARGET_PRICE', 'TRAILING_STOP')),
    trigger_price DECIMAL(15, 4) NOT NULL,
    current_price DECIMAL(15, 4), -- Updated daily

    -- For trailing stops
    trailing_pct DECIMAL(5, 2), -- Percentage below highest price
    highest_price DECIMAL(15, 4), -- Track highest price for trailing stops

    -- Status
    is_active BOOLEAN DEFAULT true,
    triggered_at TIMESTAMP,

    -- Notification
    notification_sent BOOLEAN DEFAULT false,

    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for price alerts
CREATE INDEX IF NOT EXISTS idx_alerts_portfolio ON price_alerts(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_alerts_ticker ON price_alerts(ticker_id);
CREATE INDEX IF NOT EXISTS idx_alerts_active ON price_alerts(is_active);
CREATE INDEX IF NOT EXISTS idx_alerts_type ON price_alerts(alert_type);

-- ============================================================================
-- PORTFOLIO SNAPSHOTS TABLE
-- ============================================================================
-- Daily snapshots of portfolio performance
CREATE TABLE IF NOT EXISTS portfolio_snapshots (
    snapshot_id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(portfolio_id) ON DELETE CASCADE,

    -- Snapshot details
    snapshot_date DATE NOT NULL,

    -- Values
    cash_balance DECIMAL(15, 2) NOT NULL,
    positions_value DECIMAL(15, 2) NOT NULL,
    total_value DECIMAL(15, 2) NOT NULL, -- cash + positions

    -- Performance metrics
    total_gain_loss DECIMAL(15, 2), -- total_value - initial_cash
    total_gain_loss_pct DECIMAL(8, 4), -- (total_value - initial_cash) / initial_cash * 100
    day_change DECIMAL(15, 2), -- Change from previous day
    day_change_pct DECIMAL(8, 4),

    -- Holdings count
    num_positions INTEGER,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(portfolio_id, snapshot_date)
);

-- Indexes for portfolio snapshots
CREATE INDEX IF NOT EXISTS idx_snapshots_portfolio ON portfolio_snapshots(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_snapshots_date ON portfolio_snapshots(snapshot_date DESC);

-- ============================================================================
-- REBALANCING SUGGESTIONS TABLE
-- ============================================================================
-- Stores automated rebalancing recommendations
CREATE TABLE IF NOT EXISTS rebalancing_suggestions (
    suggestion_id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(portfolio_id) ON DELETE CASCADE,

    -- Suggestion details
    suggestion_date DATE NOT NULL,

    -- Analysis
    current_allocation JSONB, -- Current percentage allocation
    target_allocation JSONB, -- Recommended allocation
    suggested_trades JSONB, -- List of buy/sell actions

    -- Reasoning
    reason TEXT,
    confidence_score INTEGER, -- 0-100

    -- Status
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'ACCEPTED', 'REJECTED', 'EXPIRED')),

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP
);

-- Indexes for rebalancing suggestions
CREATE INDEX IF NOT EXISTS idx_rebalancing_portfolio ON rebalancing_suggestions(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_rebalancing_date ON rebalancing_suggestions(suggestion_date DESC);
CREATE INDEX IF NOT EXISTS idx_rebalancing_status ON rebalancing_suggestions(status);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to update portfolio total value
CREATE OR REPLACE FUNCTION update_portfolio_value(p_portfolio_id INTEGER)
RETURNS VOID AS $$
DECLARE
    v_positions_value DECIMAL(15, 2);
    v_cash DECIMAL(15, 2);
BEGIN
    -- Calculate total positions value
    SELECT COALESCE(SUM(current_value), 0)
    INTO v_positions_value
    FROM positions
    WHERE portfolio_id = p_portfolio_id AND is_active = true;

    -- Get current cash
    SELECT current_cash
    INTO v_cash
    FROM portfolios
    WHERE portfolio_id = p_portfolio_id;

    -- Update portfolio
    UPDATE portfolios
    SET total_value = v_cash + v_positions_value,
        updated_at = CURRENT_TIMESTAMP
    WHERE portfolio_id = p_portfolio_id;
END;
$$ LANGUAGE plpgsql;

-- Function to update position values
CREATE OR REPLACE FUNCTION update_position_values(p_position_id INTEGER, p_current_price DECIMAL(15, 4))
RETURNS VOID AS $$
BEGIN
    UPDATE positions
    SET current_price = p_current_price,
        current_value = shares * p_current_price,
        unrealized_gain_loss = (shares * p_current_price) - total_cost,
        unrealized_gain_loss_pct = CASE
            WHEN total_cost > 0 THEN ((shares * p_current_price - total_cost) / total_cost) * 100
            ELSE 0
        END,
        last_updated = CURRENT_TIMESTAMP
    WHERE position_id = p_position_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Trigger to update portfolio value when positions change
CREATE OR REPLACE FUNCTION trigger_update_portfolio_value()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM update_portfolio_value(NEW.portfolio_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER positions_update_portfolio
AFTER INSERT OR UPDATE ON positions
FOR EACH ROW
EXECUTE FUNCTION trigger_update_portfolio_value();

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Create default portfolio (optional - user can create their own)
INSERT INTO portfolios (portfolio_name, description, initial_cash, current_cash)
VALUES ('Main Portfolio', 'Primary investment portfolio', 100000.00, 100000.00)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

COMMENT ON TABLE portfolios IS 'User portfolios with cash and total value tracking';
COMMENT ON TABLE positions IS 'Current stock holdings with unrealized gains/losses';
COMMENT ON TABLE transactions IS 'All buy/sell/dividend transactions';
COMMENT ON TABLE dividends IS 'Dividend payments tracking (expected and received)';
COMMENT ON TABLE price_alerts IS 'Stop loss and target price alerts';
COMMENT ON TABLE portfolio_snapshots IS 'Daily portfolio performance snapshots';
COMMENT ON TABLE rebalancing_suggestions IS 'Automated portfolio rebalancing recommendations';
