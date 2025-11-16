-- Migration: Add Dividend Tracking
-- Phase 6: Portfolio CLI & Dividend Tracking
-- Date: 2025-11-16

-- ============================================================================
-- Dividend Payments
-- ============================================================================

CREATE TABLE IF NOT EXISTS dividend_payments (
    dividend_id SERIAL PRIMARY KEY,
    ticker_id INTEGER REFERENCES tickers(ticker_id) NOT NULL,
    
    -- Dividend details
    ex_dividend_date DATE NOT NULL,
    payment_date DATE NOT NULL,
    record_date DATE,
    dividend_per_share DECIMAL(10, 4) NOT NULL,
    
    -- Dividend type
    dividend_type VARCHAR(20) DEFAULT 'REGULAR', -- REGULAR, SPECIAL, RETURN_OF_CAPITAL
    
    -- Status tracking
    status VARCHAR(20) DEFAULT 'ANNOUNCED', -- ANNOUNCED, PENDING, PAID
    
    -- Amount received (if holding tracked)
    shares_held DECIMAL(15, 4),
    total_amount DECIMAL(15, 2),
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure unique dividend per ex-date
    CONSTRAINT unique_dividend_per_ticker_date UNIQUE(ticker_id, ex_dividend_date)
);

COMMENT ON TABLE dividend_payments IS 'Dividend payment tracking for holdings';
COMMENT ON COLUMN dividend_payments.ex_dividend_date IS 'Must own stock by this date to receive dividend';
COMMENT ON COLUMN dividend_payments.payment_date IS 'Date dividend will be/was paid';
COMMENT ON COLUMN dividend_payments.dividend_type IS 'REGULAR, SPECIAL, or RETURN_OF_CAPITAL';
COMMENT ON COLUMN dividend_payments.status IS 'ANNOUNCED, PENDING, or PAID';

-- ============================================================================
-- Dividend History (for holdings)
-- ============================================================================

CREATE TABLE IF NOT EXISTS dividend_history (
    history_id SERIAL PRIMARY KEY,
    holding_id INTEGER REFERENCES portfolio_holdings(holding_id),
    dividend_id INTEGER REFERENCES dividend_payments(dividend_id),
    
    -- Payment details
    shares_held DECIMAL(15, 4) NOT NULL,
    dividend_per_share DECIMAL(10, 4) NOT NULL,
    total_amount DECIMAL(15, 2) NOT NULL,
    
    -- Dates
    ex_dividend_date DATE NOT NULL,
    payment_date DATE NOT NULL,
    received_date DATE,
    
    -- Tax tracking
    qualified_dividend BOOLEAN DEFAULT true,
    tax_withheld DECIMAL(10, 2) DEFAULT 0,
    
    -- Status
    status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, RECEIVED
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT positive_dividend CHECK (dividend_per_share > 0),
    CONSTRAINT positive_total CHECK (total_amount > 0)
);

COMMENT ON TABLE dividend_history IS 'Historical dividend payments received on holdings';
COMMENT ON COLUMN dividend_history.qualified_dividend IS 'Whether dividend qualifies for preferential tax rate';

-- ============================================================================
-- Indexes
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_dividend_payments_ticker ON dividend_payments(ticker_id);
CREATE INDEX IF NOT EXISTS idx_dividend_payments_payment_date ON dividend_payments(payment_date);
CREATE INDEX IF NOT EXISTS idx_dividend_payments_status ON dividend_payments(status);
CREATE INDEX IF NOT EXISTS idx_dividend_payments_ex_date ON dividend_payments(ex_dividend_date);

CREATE INDEX IF NOT EXISTS idx_dividend_history_holding ON dividend_history(holding_id);
CREATE INDEX IF NOT EXISTS idx_dividend_history_dividend ON dividend_history(dividend_id);
CREATE INDEX IF NOT EXISTS idx_dividend_history_payment_date ON dividend_history(payment_date);
CREATE INDEX IF NOT EXISTS idx_dividend_history_status ON dividend_history(status);

-- ============================================================================
-- Update performance_snapshots to track dividends
-- ============================================================================

-- Add dividend tracking columns if they don't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'performance_snapshots' 
        AND column_name = 'dividend_income_ytd'
    ) THEN
        ALTER TABLE performance_snapshots 
        ADD COLUMN dividend_income_ytd DECIMAL(15, 2) DEFAULT 0;
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'performance_snapshots' 
        AND column_name = 'dividend_income_mtd'
    ) THEN
        ALTER TABLE performance_snapshots 
        ADD COLUMN dividend_income_mtd DECIMAL(15, 2) DEFAULT 0;
    END IF;
END $$;

COMMENT ON COLUMN performance_snapshots.dividend_income_ytd IS 'Total dividends received year-to-date';
COMMENT ON COLUMN performance_snapshots.dividend_income_mtd IS 'Total dividends received month-to-date';

-- ============================================================================
-- End of migration
-- ============================================================================
