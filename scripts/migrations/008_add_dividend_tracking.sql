-- Migration 008: Add Dividend Tracking Tables
-- Date: 2025-11-16
-- Purpose: Track dividend history, upcoming payments, and dividend income

-- ============================================================================
-- DIVIDEND HISTORY TABLE
-- ============================================================================
-- Stores historical dividend payments for stocks
CREATE TABLE IF NOT EXISTS dividend_history (
    dividend_id SERIAL PRIMARY KEY,
    ticker_id INTEGER NOT NULL REFERENCES tickers(ticker_id) ON DELETE CASCADE,

    -- Dividend dates
    ex_date DATE NOT NULL,
    record_date DATE,
    payment_date DATE,

    -- Dividend amounts
    amount_per_share DECIMAL(10, 4) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',

    -- Dividend type
    dividend_type VARCHAR(20) DEFAULT 'CASH',  -- CASH, STOCK, SPECIAL
    frequency VARCHAR(20),  -- QUARTERLY, MONTHLY, ANNUAL, SPECIAL

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    UNIQUE(ticker_id, ex_date),
    CHECK (amount_per_share >= 0)
);

-- Indexes for dividend history
CREATE INDEX idx_dividend_history_ticker ON dividend_history(ticker_id);
CREATE INDEX idx_dividend_history_ex_date ON dividend_history(ex_date);
CREATE INDEX idx_dividend_history_payment_date ON dividend_history(payment_date);
CREATE INDEX idx_dividend_history_ticker_ex_date ON dividend_history(ticker_id, ex_date DESC);

-- ============================================================================
-- DIVIDEND CALENDAR TABLE
-- ============================================================================
-- Stores upcoming dividend payments (forward-looking)
CREATE TABLE IF NOT EXISTS dividend_calendar (
    calendar_id SERIAL PRIMARY KEY,
    ticker_id INTEGER NOT NULL REFERENCES tickers(ticker_id) ON DELETE CASCADE,

    -- Expected dates
    expected_ex_date DATE,
    expected_payment_date DATE,

    -- Expected amounts (estimated from history)
    expected_amount_per_share DECIMAL(10, 4),

    -- Confirmation status
    is_confirmed BOOLEAN DEFAULT FALSE,
    announced_date DATE,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    UNIQUE(ticker_id, expected_ex_date)
);

-- Indexes for dividend calendar
CREATE INDEX idx_dividend_calendar_ticker ON dividend_calendar(ticker_id);
CREATE INDEX idx_dividend_calendar_ex_date ON dividend_calendar(expected_ex_date);
CREATE INDEX idx_dividend_calendar_upcoming ON dividend_calendar(expected_ex_date)
    WHERE expected_ex_date >= CURRENT_DATE;

-- ============================================================================
-- DIVIDEND INCOME TABLE
-- ============================================================================
-- Tracks actual dividend income received (links to portfolio holdings)
CREATE TABLE IF NOT EXISTS dividend_income (
    income_id SERIAL PRIMARY KEY,
    ticker_id INTEGER NOT NULL REFERENCES tickers(ticker_id) ON DELETE CASCADE,
    holding_id INTEGER REFERENCES portfolio_holdings(holding_id) ON DELETE SET NULL,

    -- Payment details
    payment_date DATE NOT NULL,
    ex_date DATE,

    -- Amount calculations
    shares_owned DECIMAL(15, 4) NOT NULL,
    amount_per_share DECIMAL(10, 4) NOT NULL,
    total_amount DECIMAL(15, 2) NOT NULL,

    -- Tax information
    tax_withheld DECIMAL(15, 2) DEFAULT 0,
    net_amount DECIMAL(15, 2) GENERATED ALWAYS AS (total_amount - tax_withheld) STORED,

    -- Reinvestment tracking
    reinvested BOOLEAN DEFAULT FALSE,
    reinvestment_ticker_id INTEGER REFERENCES tickers(ticker_id) ON DELETE SET NULL,
    reinvestment_shares DECIMAL(15, 4),

    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CHECK (shares_owned > 0),
    CHECK (amount_per_share >= 0),
    CHECK (total_amount >= 0),
    CHECK (tax_withheld >= 0)
);

-- Indexes for dividend income
CREATE INDEX idx_dividend_income_ticker ON dividend_income(ticker_id);
CREATE INDEX idx_dividend_income_payment_date ON dividend_income(payment_date);
CREATE INDEX idx_dividend_income_holding ON dividend_income(holding_id);
CREATE INDEX idx_dividend_income_year ON dividend_income(EXTRACT(YEAR FROM payment_date));

-- ============================================================================
-- DIVIDEND YIELD CACHE TABLE
-- ============================================================================
-- Caches current dividend yield calculations (updated periodically)
CREATE TABLE IF NOT EXISTS dividend_yield_cache (
    cache_id SERIAL PRIMARY KEY,
    ticker_id INTEGER NOT NULL REFERENCES tickers(ticker_id) ON DELETE CASCADE,

    -- Yield calculations
    current_price DECIMAL(10, 2),
    annual_dividend DECIMAL(10, 4),
    dividend_yield_pct DECIMAL(7, 4),

    -- Dividend metrics
    payout_frequency VARCHAR(20),
    last_dividend_amount DECIMAL(10, 4),
    last_ex_date DATE,

    -- Growth metrics
    dividend_growth_1yr_pct DECIMAL(7, 2),
    dividend_growth_3yr_pct DECIMAL(7, 2),
    dividend_growth_5yr_pct DECIMAL(7, 2),

    -- Reliability metrics
    consecutive_years_paid INTEGER,
    payout_ratio_pct DECIMAL(7, 2),

    -- Cache metadata
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMP,

    -- Constraints
    UNIQUE(ticker_id)
);

-- Index for dividend yield cache
CREATE INDEX idx_dividend_yield_cache_ticker ON dividend_yield_cache(ticker_id);
CREATE INDEX idx_dividend_yield_cache_yield ON dividend_yield_cache(dividend_yield_pct DESC);
CREATE INDEX idx_dividend_yield_cache_valid ON dividend_yield_cache(valid_until)
    WHERE valid_until > CURRENT_TIMESTAMP;

-- ============================================================================
-- VIEWS FOR EASY QUERYING
-- ============================================================================

-- View: Upcoming Dividends (next 90 days)
CREATE OR REPLACE VIEW v_upcoming_dividends AS
SELECT
    t.symbol,
    t.name,
    dc.expected_ex_date,
    dc.expected_payment_date,
    dc.expected_amount_per_share,
    dc.is_confirmed,
    dyc.dividend_yield_pct,
    dyc.payout_frequency,
    CASE
        WHEN dc.expected_ex_date <= CURRENT_DATE + INTERVAL '7 days' THEN 'THIS_WEEK'
        WHEN dc.expected_ex_date <= CURRENT_DATE + INTERVAL '30 days' THEN 'THIS_MONTH'
        WHEN dc.expected_ex_date <= CURRENT_DATE + INTERVAL '90 days' THEN 'NEXT_3_MONTHS'
        ELSE 'FUTURE'
    END as timeframe
FROM dividend_calendar dc
JOIN tickers t ON dc.ticker_id = t.ticker_id
LEFT JOIN dividend_yield_cache dyc ON dc.ticker_id = dyc.ticker_id
WHERE dc.expected_ex_date >= CURRENT_DATE
    AND dc.expected_ex_date <= CURRENT_DATE + INTERVAL '90 days'
ORDER BY dc.expected_ex_date ASC;

-- View: Dividend Income Summary by Year
CREATE OR REPLACE VIEW v_dividend_income_by_year AS
SELECT
    EXTRACT(YEAR FROM payment_date) as year,
    COUNT(*) as payment_count,
    SUM(total_amount) as total_gross_income,
    SUM(tax_withheld) as total_tax_withheld,
    SUM(net_amount) as total_net_income,
    COUNT(DISTINCT ticker_id) as unique_tickers,
    SUM(CASE WHEN reinvested THEN total_amount ELSE 0 END) as total_reinvested
FROM dividend_income
GROUP BY EXTRACT(YEAR FROM payment_date)
ORDER BY year DESC;

-- View: Dividend Income Summary by Ticker
CREATE OR REPLACE VIEW v_dividend_income_by_ticker AS
SELECT
    t.symbol,
    t.name,
    COUNT(*) as payment_count,
    SUM(di.total_amount) as total_income,
    AVG(di.amount_per_share) as avg_amount_per_share,
    MIN(di.payment_date) as first_payment,
    MAX(di.payment_date) as last_payment,
    dyc.dividend_yield_pct as current_yield,
    dyc.payout_frequency
FROM dividend_income di
JOIN tickers t ON di.ticker_id = t.ticker_id
LEFT JOIN dividend_yield_cache dyc ON di.ticker_id = dyc.ticker_id
GROUP BY t.symbol, t.name, dyc.dividend_yield_pct, dyc.payout_frequency
ORDER BY total_income DESC;

-- View: High Yield Dividend Stocks
CREATE OR REPLACE VIEW v_high_yield_stocks AS
SELECT
    t.symbol,
    t.name,
    dyc.dividend_yield_pct,
    dyc.annual_dividend,
    dyc.current_price,
    dyc.payout_frequency,
    dyc.dividend_growth_1yr_pct,
    dyc.dividend_growth_3yr_pct,
    dyc.consecutive_years_paid,
    dyc.payout_ratio_pct,
    CASE
        WHEN dyc.dividend_yield_pct >= 5.0 THEN 'HIGH'
        WHEN dyc.dividend_yield_pct >= 3.0 THEN 'MEDIUM'
        WHEN dyc.dividend_yield_pct >= 1.0 THEN 'LOW'
        ELSE 'MINIMAL'
    END as yield_category
FROM dividend_yield_cache dyc
JOIN tickers t ON dyc.ticker_id = t.ticker_id
WHERE dyc.dividend_yield_pct > 0
    AND dyc.valid_until > CURRENT_TIMESTAMP
ORDER BY dyc.dividend_yield_pct DESC;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Trigger: Update dividend_history updated_at timestamp
CREATE OR REPLACE FUNCTION update_dividend_history_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_dividend_history_timestamp
    BEFORE UPDATE ON dividend_history
    FOR EACH ROW
    EXECUTE FUNCTION update_dividend_history_timestamp();

-- Trigger: Update dividend_calendar updated_at timestamp
CREATE OR REPLACE FUNCTION update_dividend_calendar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_dividend_calendar_timestamp
    BEFORE UPDATE ON dividend_calendar
    FOR EACH ROW
    EXECUTE FUNCTION update_dividend_calendar_timestamp();

-- Trigger: Update dividend_income updated_at timestamp
CREATE OR REPLACE FUNCTION update_dividend_income_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_dividend_income_timestamp
    BEFORE UPDATE ON dividend_income
    FOR EACH ROW
    EXECUTE FUNCTION update_dividend_income_timestamp();

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE dividend_history IS 'Historical dividend payments for all tracked stocks';
COMMENT ON TABLE dividend_calendar IS 'Upcoming expected dividend payments';
COMMENT ON TABLE dividend_income IS 'Actual dividend income received by the portfolio';
COMMENT ON TABLE dividend_yield_cache IS 'Cached dividend yield calculations and metrics';

COMMENT ON VIEW v_upcoming_dividends IS 'Upcoming dividend payments in the next 90 days';
COMMENT ON VIEW v_dividend_income_by_year IS 'Dividend income summary aggregated by year';
COMMENT ON VIEW v_dividend_income_by_ticker IS 'Dividend income summary aggregated by ticker';
COMMENT ON VIEW v_high_yield_stocks IS 'Stocks ranked by dividend yield';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Grant permissions (adjust as needed)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT SELECT ON ALL VIEWS IN SCHEMA public TO your_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_app_user;

-- Verification query
SELECT
    'dividend_history' as table_name, COUNT(*) as row_count FROM dividend_history
UNION ALL
SELECT 'dividend_calendar', COUNT(*) FROM dividend_calendar
UNION ALL
SELECT 'dividend_income', COUNT(*) FROM dividend_income
UNION ALL
SELECT 'dividend_yield_cache', COUNT(*) FROM dividend_yield_cache;

COMMENT ON SCHEMA public IS 'Migration 008: Dividend tracking tables created successfully';
