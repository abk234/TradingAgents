-- Migration: Add Entry Price Tracking and Historical Indicator Storage
-- Purpose: Track calculated entry prices and technical indicators for trend analysis
-- Author: System
-- Date: 2025-11-18

-- ============================================================================
-- 1. Enhance daily_scans with entry price tracking
-- ============================================================================

-- Add entry price recommendation columns
ALTER TABLE daily_scans
ADD COLUMN IF NOT EXISTS entry_price_min DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS entry_price_max DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS entry_price_reasoning TEXT;

-- Add Bollinger Band values (critical for entry timing)
ALTER TABLE daily_scans
ADD COLUMN IF NOT EXISTS bb_upper DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS bb_lower DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS bb_middle DECIMAL(10,2);

-- Add support/resistance levels
ALTER TABLE daily_scans
ADD COLUMN IF NOT EXISTS support_level DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS resistance_level DECIMAL(10,2);

-- Add enterprise value metrics snapshot
ALTER TABLE daily_scans
ADD COLUMN IF NOT EXISTS enterprise_value BIGINT,
ADD COLUMN IF NOT EXISTS enterprise_to_ebitda DECIMAL(8,2),
ADD COLUMN IF NOT EXISTS market_cap BIGINT;

-- Add entry timing recommendation
ALTER TABLE daily_scans
ADD COLUMN IF NOT EXISTS entry_timing VARCHAR(20); -- 'BUY_NOW', 'WAIT_FOR_PULLBACK', 'ACCUMULATE', 'AVOID'

COMMENT ON COLUMN daily_scans.entry_price_min IS 'Calculated minimum recommended entry price based on technical analysis';
COMMENT ON COLUMN daily_scans.entry_price_max IS 'Calculated maximum recommended entry price based on technical analysis';
COMMENT ON COLUMN daily_scans.entry_price_reasoning IS 'Human-readable explanation of entry price calculation';
COMMENT ON COLUMN daily_scans.bb_lower IS 'Bollinger Band lower value at scan time';
COMMENT ON COLUMN daily_scans.bb_upper IS 'Bollinger Band upper value at scan time';
COMMENT ON COLUMN daily_scans.support_level IS 'Calculated support level from technical analysis';
COMMENT ON COLUMN daily_scans.entry_timing IS 'Entry timing recommendation (BUY_NOW, WAIT_FOR_PULLBACK, etc)';

-- ============================================================================
-- 2. Enhance daily_prices with technical indicators
-- ============================================================================

-- Add Bollinger Bands to daily_prices (for historical analysis)
ALTER TABLE daily_prices
ADD COLUMN IF NOT EXISTS bb_upper DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS bb_lower DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS bb_middle DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS bb_width DECIMAL(10,4); -- Volatility measure

-- Add MACD indicators
ALTER TABLE daily_prices
ADD COLUMN IF NOT EXISTS macd DECIMAL(10,4),
ADD COLUMN IF NOT EXISTS macd_signal DECIMAL(10,4),
ADD COLUMN IF NOT EXISTS macd_histogram DECIMAL(10,4);

-- Add volume indicators
ALTER TABLE daily_prices
ADD COLUMN IF NOT EXISTS volume_sma_20 BIGINT,
ADD COLUMN IF NOT EXISTS volume_ratio DECIMAL(6,4); -- Today's volume / 20-day avg

-- Add price change metrics
ALTER TABLE daily_prices
ADD COLUMN IF NOT EXISTS day_return DECIMAL(8,6),
ADD COLUMN IF NOT EXISTS week_return DECIMAL(8,6),
ADD COLUMN IF NOT EXISTS month_return DECIMAL(8,6);

-- Add support/resistance detection
ALTER TABLE daily_prices
ADD COLUMN IF NOT EXISTS is_support_level BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS is_resistance_level BOOLEAN DEFAULT FALSE;

COMMENT ON COLUMN daily_prices.bb_width IS 'Bollinger Band width as percentage - measures volatility';
COMMENT ON COLUMN daily_prices.volume_ratio IS 'Current volume divided by 20-day average volume';
COMMENT ON COLUMN daily_prices.is_support_level IS 'True if this price level has acted as support historically';

-- ============================================================================
-- 3. Create entry_price_outcomes table (track accuracy)
-- ============================================================================

CREATE TABLE IF NOT EXISTS entry_price_outcomes (
    outcome_id BIGSERIAL PRIMARY KEY,
    scan_id BIGINT REFERENCES daily_scans(scan_id) ON DELETE CASCADE,
    ticker_id INTEGER REFERENCES tickers(ticker_id) ON DELETE CASCADE,

    -- Recommendation details
    scan_date DATE NOT NULL,
    entry_price_min DECIMAL(10,2) NOT NULL,
    entry_price_max DECIMAL(10,2) NOT NULL,
    recommended_timing VARCHAR(20), -- 'BUY_NOW', 'WAIT_FOR_PULLBACK', etc

    -- Actual outcome
    outcome_status VARCHAR(30) NOT NULL, -- 'HIT_TARGET', 'MISSED_OPPORTUNITY', 'STILL_WAITING', 'STOPPED_OUT'
    actual_entry_price DECIMAL(10,2), -- Price actually achieved (if entered)
    entry_date DATE, -- Date when entry price was hit
    days_to_entry INTEGER, -- Days between recommendation and entry

    -- Performance tracking
    lowest_price_after DECIMAL(10,2), -- Lowest price reached after recommendation
    highest_price_after DECIMAL(10,2), -- Highest price reached after recommendation
    current_price DECIMAL(10,2), -- Most recent price

    -- Analysis
    entry_accuracy_pct DECIMAL(8,4), -- How close actual entry was to recommendation
    opportunity_score DECIMAL(6,2), -- 0-100, how good was this entry in retrospect

    -- Metadata
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Ensure one outcome per scan
    UNIQUE(scan_id)
);

CREATE INDEX IF NOT EXISTS idx_outcomes_ticker_date ON entry_price_outcomes(ticker_id, scan_date DESC);
CREATE INDEX IF NOT EXISTS idx_outcomes_status ON entry_price_outcomes(outcome_status);
CREATE INDEX IF NOT EXISTS idx_outcomes_entry_date ON entry_price_outcomes(entry_date DESC);

COMMENT ON TABLE entry_price_outcomes IS 'Tracks accuracy of entry price recommendations over time';
COMMENT ON COLUMN entry_price_outcomes.outcome_status IS 'HIT_TARGET=entered at recommended price, MISSED_OPPORTUNITY=price never reached target, STILL_WAITING=monitoring';
COMMENT ON COLUMN entry_price_outcomes.opportunity_score IS 'Retrospective score: 100=perfect entry at bottom, 0=worst possible entry';

-- ============================================================================
-- 4. Create entry_price_history view (for easy trend analysis)
-- ============================================================================

CREATE OR REPLACE VIEW entry_price_history AS
SELECT
    t.symbol,
    t.company_name,
    ds.scan_date,
    ds.price as current_price,
    ds.entry_price_min,
    ds.entry_price_max,
    ds.entry_timing,
    ds.priority_score,
    ds.technical_signals->>'rsi' as rsi,
    ds.bb_lower,
    ds.bb_upper,
    ds.support_level,
    epo.outcome_status,
    epo.actual_entry_price,
    epo.days_to_entry,
    epo.opportunity_score,
    -- Calculate potential savings
    CASE
        WHEN epo.actual_entry_price IS NOT NULL AND ds.price IS NOT NULL
        THEN ROUND(((ds.price - epo.actual_entry_price) / ds.price * 100)::numeric, 2)
        ELSE NULL
    END as entry_discount_pct
FROM daily_scans ds
JOIN tickers t ON t.ticker_id = ds.ticker_id
LEFT JOIN entry_price_outcomes epo ON epo.scan_id = ds.scan_id
WHERE ds.entry_price_min IS NOT NULL
ORDER BY ds.scan_date DESC, ds.priority_rank;

COMMENT ON VIEW entry_price_history IS 'Historical view of entry price recommendations and their outcomes';

-- ============================================================================
-- 5. Create function to auto-update entry price outcomes
-- ============================================================================

CREATE OR REPLACE FUNCTION update_entry_price_outcomes()
RETURNS void AS $$
DECLARE
    outcome_rec RECORD;
    current_low DECIMAL(10,2);
    current_high DECIMAL(10,2);
    latest_price DECIMAL(10,2);
BEGIN
    -- Update all STILL_WAITING outcomes
    FOR outcome_rec IN
        SELECT
            epo.outcome_id,
            epo.ticker_id,
            epo.scan_date,
            epo.entry_price_min,
            epo.entry_price_max,
            t.symbol
        FROM entry_price_outcomes epo
        JOIN tickers t ON t.ticker_id = epo.ticker_id
        WHERE epo.outcome_status = 'STILL_WAITING'
    LOOP
        -- Get price range since recommendation
        SELECT
            MIN(low) as min_low,
            MAX(high) as max_high,
            (SELECT close FROM daily_prices
             WHERE ticker_id = outcome_rec.ticker_id
             ORDER BY price_date DESC LIMIT 1) as latest
        INTO current_low, current_high, latest_price
        FROM daily_prices
        WHERE ticker_id = outcome_rec.ticker_id
            AND price_date >= outcome_rec.scan_date;

        -- Check if entry target was hit
        IF current_low IS NOT NULL AND current_low <= outcome_rec.entry_price_max THEN
            -- Target was hit!
            UPDATE entry_price_outcomes
            SET
                outcome_status = 'HIT_TARGET',
                actual_entry_price = LEAST(current_low, outcome_rec.entry_price_max),
                entry_date = (
                    SELECT price_date
                    FROM daily_prices
                    WHERE ticker_id = outcome_rec.ticker_id
                        AND price_date >= outcome_rec.scan_date
                        AND low <= outcome_rec.entry_price_max
                    ORDER BY price_date ASC
                    LIMIT 1
                ),
                days_to_entry = (
                    SELECT (price_date - outcome_rec.scan_date)::integer
                    FROM daily_prices
                    WHERE ticker_id = outcome_rec.ticker_id
                        AND price_date >= outcome_rec.scan_date
                        AND low <= outcome_rec.entry_price_max
                    ORDER BY price_date ASC
                    LIMIT 1
                ),
                lowest_price_after = current_low,
                highest_price_after = current_high,
                current_price = latest_price,
                last_updated = CURRENT_TIMESTAMP
            WHERE outcome_id = outcome_rec.outcome_id;
        ELSE
            -- Still waiting, just update price tracking
            UPDATE entry_price_outcomes
            SET
                lowest_price_after = current_low,
                highest_price_after = current_high,
                current_price = latest_price,
                last_updated = CURRENT_TIMESTAMP
            WHERE outcome_id = outcome_rec.outcome_id;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_entry_price_outcomes() IS 'Updates entry price outcome tracking based on actual price movements';

-- ============================================================================
-- 6. Create indexes for performance
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_daily_scans_entry_price ON daily_scans(entry_price_min, entry_price_max) WHERE entry_price_min IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_daily_scans_entry_timing ON daily_scans(entry_timing) WHERE entry_timing IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_daily_prices_indicators ON daily_prices(ticker_id, price_date) WHERE rsi_14 IS NOT NULL;

-- ============================================================================
-- Migration Complete
-- ============================================================================

-- Verify the changes
DO $$
BEGIN
    RAISE NOTICE 'Migration 014 completed successfully';
    RAISE NOTICE 'Added entry price tracking to daily_scans';
    RAISE NOTICE 'Enhanced daily_prices with technical indicators';
    RAISE NOTICE 'Created entry_price_outcomes table';
    RAISE NOTICE 'Created entry_price_history view';
    RAISE NOTICE 'Created update_entry_price_outcomes() function';
END $$;
