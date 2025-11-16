-- Migration: Add Recommendation Outcome Tracking
-- Phase 6: Performance Tracking & Learning
-- Created: 2025-11-16

-- ============================================================================
-- RECOMMENDATION OUTCOMES
-- ============================================================================
-- Track what happened to stocks after we recommended them
-- This enables learning, validation, and continuous improvement

CREATE TABLE IF NOT EXISTS recommendation_outcomes (
    outcome_id SERIAL PRIMARY KEY,
    analysis_id BIGINT NOT NULL REFERENCES analyses(analysis_id) ON DELETE CASCADE,
    ticker_id INTEGER NOT NULL REFERENCES tickers(ticker_id) ON DELETE CASCADE,

    -- When the recommendation was made
    recommendation_date DATE NOT NULL,
    analyzed_at TIMESTAMP NOT NULL,

    -- What we recommended
    decision VARCHAR(10) NOT NULL,  -- 'BUY', 'WAIT', 'SELL', 'HOLD'
    confidence INTEGER NOT NULL,     -- 0-100
    recommended_entry_price DECIMAL(10, 2) NOT NULL,
    recommended_position_size_pct DECIMAL(5, 2),
    recommended_position_amount DECIMAL(15, 2),

    -- Price targets and stops (if provided)
    target_price DECIMAL(10, 2),
    stop_loss_price DECIMAL(10, 2),

    -- What actually happened - prices at various intervals
    price_after_1day DECIMAL(10, 2),
    price_after_3days DECIMAL(10, 2),
    price_after_7days DECIMAL(10, 2),
    price_after_14days DECIMAL(10, 2),
    price_after_30days DECIMAL(10, 2),
    price_after_60days DECIMAL(10, 2),
    price_after_90days DECIMAL(10, 2),

    -- Returns at various intervals
    return_1day_pct DECIMAL(7, 2),
    return_3days_pct DECIMAL(7, 2),
    return_7days_pct DECIMAL(7, 2),
    return_14days_pct DECIMAL(7, 2),
    return_30days_pct DECIMAL(7, 2),
    return_60days_pct DECIMAL(7, 2),
    return_90days_pct DECIMAL(7, 2),

    -- Peak and trough (best/worst performance)
    peak_price DECIMAL(10, 2),       -- Highest price reached
    peak_date DATE,                   -- When it peaked
    peak_return_pct DECIMAL(7, 2),   -- Return at peak
    trough_price DECIMAL(10, 2),     -- Lowest price reached
    trough_date DATE,                 -- When it hit bottom
    trough_return_pct DECIMAL(7, 2), -- Return at trough (negative)

    -- Outcome evaluation
    was_correct BOOLEAN,              -- Did price move in predicted direction?
    outcome_quality VARCHAR(20),      -- 'EXCELLENT', 'GOOD', 'NEUTRAL', 'POOR', 'FAILED'
    hit_target BOOLEAN,               -- Did it reach target price?
    hit_stop_loss BOOLEAN,            -- Did it hit stop loss?

    -- Benchmark comparison
    sp500_return_1day_pct DECIMAL(7, 2),
    sp500_return_7days_pct DECIMAL(7, 2),
    sp500_return_30days_pct DECIMAL(7, 2),
    sp500_return_90days_pct DECIMAL(7, 2),
    alpha_30days_pct DECIMAL(7, 2),   -- Excess return vs S&P 500
    alpha_90days_pct DECIMAL(7, 2),

    -- Metadata
    last_evaluated_at TIMESTAMP,      -- Last time we updated prices
    evaluation_status VARCHAR(20) DEFAULT 'PENDING',  -- 'PENDING', 'TRACKING', 'COMPLETED'
    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_decision CHECK (decision IN ('BUY', 'WAIT', 'SELL', 'HOLD')),
    CONSTRAINT valid_confidence CHECK (confidence >= 0 AND confidence <= 100),
    CONSTRAINT valid_quality CHECK (outcome_quality IN ('EXCELLENT', 'GOOD', 'NEUTRAL', 'POOR', 'FAILED') OR outcome_quality IS NULL)
);

-- Indexes for performance
CREATE INDEX idx_outcomes_analysis ON recommendation_outcomes(analysis_id);
CREATE INDEX idx_outcomes_ticker ON recommendation_outcomes(ticker_id);
CREATE INDEX idx_outcomes_date ON recommendation_outcomes(recommendation_date DESC);
CREATE INDEX idx_outcomes_decision ON recommendation_outcomes(decision);
CREATE INDEX idx_outcomes_quality ON recommendation_outcomes(outcome_quality);
CREATE INDEX idx_outcomes_status ON recommendation_outcomes(evaluation_status);
CREATE INDEX idx_outcomes_was_correct ON recommendation_outcomes(was_correct) WHERE was_correct IS NOT NULL;

-- Composite indexes for common queries
CREATE INDEX idx_outcomes_decision_confidence ON recommendation_outcomes(decision, confidence DESC);
CREATE INDEX idx_outcomes_ticker_date ON recommendation_outcomes(ticker_id, recommendation_date DESC);

-- ============================================================================
-- SIGNAL PERFORMANCE TRACKING
-- ============================================================================
-- Track which technical signals lead to best outcomes

CREATE TABLE IF NOT EXISTS signal_performance (
    signal_perf_id SERIAL PRIMARY KEY,
    signal_type VARCHAR(50) NOT NULL,   -- 'RSI_OVERSOLD', 'BB_LOWER_TOUCH', etc.
    ticker_id INTEGER REFERENCES tickers(ticker_id),

    -- Performance metrics
    total_occurrences INTEGER DEFAULT 0,
    successful_predictions INTEGER DEFAULT 0,
    failed_predictions INTEGER DEFAULT 0,
    win_rate_pct DECIMAL(5, 2),

    -- Return statistics
    avg_return_7days_pct DECIMAL(7, 2),
    avg_return_30days_pct DECIMAL(7, 2),
    best_return_pct DECIMAL(7, 2),
    worst_return_pct DECIMAL(7, 2),

    -- Confidence correlation
    avg_confidence_when_successful DECIMAL(5, 2),
    avg_confidence_when_failed DECIMAL(5, 2),

    -- Time period
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_signal_perf_type ON signal_performance(signal_type);
CREATE INDEX idx_signal_perf_ticker ON signal_performance(ticker_id);
CREATE INDEX idx_signal_perf_winrate ON signal_performance(win_rate_pct DESC NULLS LAST);

-- ============================================================================
-- BENCHMARK DATA (S&P 500)
-- ============================================================================
-- Store S&P 500 (SPY) prices for benchmark comparison

CREATE TABLE IF NOT EXISTS benchmark_prices (
    benchmark_id SERIAL PRIMARY KEY,
    benchmark_symbol VARCHAR(10) NOT NULL,  -- 'SPY', 'QQQ', etc.
    price_date DATE NOT NULL,
    close_price DECIMAL(10, 2) NOT NULL,
    open_price DECIMAL(10, 2),
    high_price DECIMAL(10, 2),
    low_price DECIMAL(10, 2),
    volume BIGINT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (benchmark_symbol, price_date)
);

CREATE INDEX idx_benchmark_symbol_date ON benchmark_prices(benchmark_symbol, price_date DESC);

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update recommendation_outcomes.updated_at on UPDATE
CREATE OR REPLACE FUNCTION update_recommendation_outcomes_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_outcomes_updated
    BEFORE UPDATE ON recommendation_outcomes
    FOR EACH ROW
    EXECUTE FUNCTION update_recommendation_outcomes_timestamp();

-- Function to automatically determine outcome quality
CREATE OR REPLACE FUNCTION calculate_outcome_quality()
RETURNS TRIGGER AS $$
BEGIN
    -- Only calculate if we have 30-day return
    IF NEW.return_30days_pct IS NOT NULL THEN
        -- For BUY recommendations
        IF NEW.decision = 'BUY' THEN
            IF NEW.return_30days_pct >= 15 THEN
                NEW.outcome_quality = 'EXCELLENT';
                NEW.was_correct = true;
            ELSIF NEW.return_30days_pct >= 8 THEN
                NEW.outcome_quality = 'GOOD';
                NEW.was_correct = true;
            ELSIF NEW.return_30days_pct >= 0 THEN
                NEW.outcome_quality = 'NEUTRAL';
                NEW.was_correct = true;
            ELSIF NEW.return_30days_pct >= -5 THEN
                NEW.outcome_quality = 'POOR';
                NEW.was_correct = false;
            ELSE
                NEW.outcome_quality = 'FAILED';
                NEW.was_correct = false;
            END IF;

        -- For WAIT/SELL recommendations (opposite logic)
        ELSIF NEW.decision IN ('WAIT', 'SELL') THEN
            IF NEW.return_30days_pct <= -10 THEN
                NEW.outcome_quality = 'EXCELLENT';
                NEW.was_correct = true;
            ELSIF NEW.return_30days_pct <= 0 THEN
                NEW.outcome_quality = 'GOOD';
                NEW.was_correct = true;
            ELSIF NEW.return_30days_pct <= 5 THEN
                NEW.outcome_quality = 'NEUTRAL';
                NEW.was_correct = true;
            ELSIF NEW.return_30days_pct <= 10 THEN
                NEW.outcome_quality = 'POOR';
                NEW.was_correct = false;
            ELSE
                NEW.outcome_quality = 'FAILED';
                NEW.was_correct = false;
            END IF;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_calculate_outcome_quality
    BEFORE INSERT OR UPDATE ON recommendation_outcomes
    FOR EACH ROW
    EXECUTE FUNCTION calculate_outcome_quality();

-- ============================================================================
-- HELPER VIEWS
-- ============================================================================

-- View: Recent recommendation performance
CREATE OR REPLACE VIEW v_recent_recommendation_performance AS
SELECT
    ro.*,
    t.symbol,
    t.company_name,
    a.analyzed_at,
    CASE
        WHEN ro.return_30days_pct IS NOT NULL THEN
            CASE
                WHEN ro.decision = 'BUY' AND ro.return_30days_pct > 0 THEN '✓ WIN'
                WHEN ro.decision = 'BUY' AND ro.return_30days_pct <= 0 THEN '✗ LOSS'
                ELSE 'N/A'
            END
        ELSE 'PENDING'
    END as result_label
FROM recommendation_outcomes ro
JOIN tickers t ON ro.ticker_id = t.ticker_id
JOIN analyses a ON ro.analysis_id = a.analysis_id
ORDER BY ro.recommendation_date DESC;

-- View: Win rate by confidence level
CREATE OR REPLACE VIEW v_winrate_by_confidence AS
SELECT
    CASE
        WHEN confidence >= 90 THEN '90-100'
        WHEN confidence >= 80 THEN '80-89'
        WHEN confidence >= 70 THEN '70-79'
        WHEN confidence >= 60 THEN '60-69'
        ELSE '0-59'
    END as confidence_range,
    COUNT(*) as total_recs,
    COUNT(CASE WHEN was_correct THEN 1 END) as wins,
    COUNT(CASE WHEN was_correct = false THEN 1 END) as losses,
    ROUND(100.0 * COUNT(CASE WHEN was_correct THEN 1 END) / NULLIF(COUNT(*), 0), 1) as win_rate_pct,
    ROUND(AVG(return_30days_pct), 2) as avg_return_30days
FROM recommendation_outcomes
WHERE return_30days_pct IS NOT NULL
GROUP BY confidence_range
ORDER BY confidence_range DESC;

-- ============================================================================
-- SAMPLE QUERIES (commented out)
-- ============================================================================

-- Get overall win rate
-- SELECT
--     COUNT(*) as total_recommendations,
--     COUNT(CASE WHEN was_correct THEN 1 END) as wins,
--     ROUND(100.0 * COUNT(CASE WHEN was_correct THEN 1 END) / NULLIF(COUNT(*), 0), 1) as win_rate_pct,
--     ROUND(AVG(return_30days_pct), 2) as avg_return_30days
-- FROM recommendation_outcomes
-- WHERE return_30days_pct IS NOT NULL;

-- Get top performers
-- SELECT
--     t.symbol,
--     ro.confidence,
--     ro.recommendation_date,
--     ro.recommended_entry_price,
--     ro.price_after_30days,
--     ro.return_30days_pct
-- FROM recommendation_outcomes ro
-- JOIN tickers t ON ro.ticker_id = t.ticker_id
-- WHERE ro.decision = 'BUY'
-- AND ro.return_30days_pct IS NOT NULL
-- ORDER BY ro.return_30days_pct DESC
-- LIMIT 10;

-- ============================================================================
-- CLEANUP (if needed)
-- ============================================================================

-- DROP VIEW IF EXISTS v_recent_recommendation_performance CASCADE;
-- DROP VIEW IF EXISTS v_winrate_by_confidence CASCADE;
-- DROP TABLE IF EXISTS signal_performance CASCADE;
-- DROP TABLE IF EXISTS benchmark_prices CASCADE;
-- DROP TABLE IF EXISTS recommendation_outcomes CASCADE;
-- DROP FUNCTION IF EXISTS calculate_outcome_quality() CASCADE;
-- DROP FUNCTION IF EXISTS update_recommendation_outcomes_timestamp() CASCADE;
