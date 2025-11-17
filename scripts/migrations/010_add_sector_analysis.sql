-- Migration 010: Add Sector Analysis Tables
-- Created: 2025-11-16
-- Purpose: Enable sector-based screening and rotation tracking

-- ========================================
-- Table: sector_scores
-- Track daily sector strength scores
-- ========================================
CREATE TABLE IF NOT EXISTS sector_scores (
    score_id SERIAL PRIMARY KEY,
    sector VARCHAR(100) NOT NULL,
    score_date DATE NOT NULL DEFAULT CURRENT_DATE,
    strength_score DECIMAL(5,2) CHECK (strength_score BETWEEN 0 AND 100),
    total_stocks INTEGER NOT NULL DEFAULT 0,
    active_stocks INTEGER NOT NULL DEFAULT 0,
    buy_signals INTEGER NOT NULL DEFAULT 0,
    wait_signals INTEGER NOT NULL DEFAULT 0,
    sell_signals INTEGER NOT NULL DEFAULT 0,
    avg_priority_score DECIMAL(5,2),
    avg_rsi DECIMAL(5,2),
    avg_volume_ratio DECIMAL(10,2),
    momentum VARCHAR(50), -- Strong, Moderate, Neutral, Weak
    trend_direction VARCHAR(20), -- Up, Down, Sideways
    relative_strength DECIMAL(10,2), -- vs S&P 500
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(sector, score_date)
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_sector_scores_date ON sector_scores(score_date DESC);
CREATE INDEX IF NOT EXISTS idx_sector_scores_sector ON sector_scores(sector);
CREATE INDEX IF NOT EXISTS idx_sector_scores_strength ON sector_scores(strength_score DESC);

-- ========================================
-- Table: sector_rotation
-- Track sector leadership changes over time
-- ========================================
CREATE TABLE IF NOT EXISTS sector_rotation (
    rotation_id SERIAL PRIMARY KEY,
    rotation_date DATE NOT NULL DEFAULT CURRENT_DATE,
    from_sector VARCHAR(100),
    to_sector VARCHAR(100),
    rotation_type VARCHAR(50), -- Leadership, Money_Flow, Momentum
    confidence_level VARCHAR(20), -- High, Medium, Low
    strength_change DECIMAL(10,2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(rotation_date, from_sector, to_sector, rotation_type)
);

-- Index for rotation tracking
CREATE INDEX IF NOT EXISTS idx_sector_rotation_date ON sector_rotation(rotation_date DESC);

-- ========================================
-- Table: sector_momentum
-- Track momentum indicators by sector
-- ========================================
CREATE TABLE IF NOT EXISTS sector_momentum (
    momentum_id SERIAL PRIMARY KEY,
    sector VARCHAR(100) NOT NULL,
    analysis_date DATE NOT NULL DEFAULT CURRENT_DATE,
    momentum_score DECIMAL(5,2) CHECK (momentum_score BETWEEN -100 AND 100),
    trend_strength DECIMAL(5,2) CHECK (trend_strength BETWEEN 0 AND 100),
    velocity DECIMAL(10,2), -- Rate of change
    acceleration DECIMAL(10,2), -- Change in rate of change
    support_level DECIMAL(10,2),
    resistance_level DECIMAL(10,2),
    breakout_probability DECIMAL(5,2) CHECK (breakout_probability BETWEEN 0 AND 100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(sector, analysis_date)
);

-- Index for momentum tracking
CREATE INDEX IF NOT EXISTS idx_sector_momentum_date ON sector_momentum(analysis_date DESC);
CREATE INDEX IF NOT EXISTS idx_sector_momentum_score ON sector_momentum(momentum_score DESC);

-- ========================================
-- Table: sector_correlations
-- Track correlation between sectors
-- ========================================
CREATE TABLE IF NOT EXISTS sector_correlations (
    correlation_id SERIAL PRIMARY KEY,
    sector_a VARCHAR(100) NOT NULL,
    sector_b VARCHAR(100) NOT NULL,
    correlation_date DATE NOT NULL DEFAULT CURRENT_DATE,
    correlation_coefficient DECIMAL(5,4) CHECK (correlation_coefficient BETWEEN -1 AND 1),
    period_days INTEGER NOT NULL DEFAULT 30,
    significance_level DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(sector_a, sector_b, correlation_date, period_days)
);

-- Index for correlation lookups
CREATE INDEX IF NOT EXISTS idx_sector_corr_date ON sector_correlations(correlation_date DESC);

-- ========================================
-- Table: sector_alerts
-- Track sector-level alerts and signals
-- ========================================
CREATE TABLE IF NOT EXISTS sector_alerts (
    alert_id SERIAL PRIMARY KEY,
    sector VARCHAR(100) NOT NULL,
    alert_type VARCHAR(100) NOT NULL, -- Breakout, Breakdown, Rotation, Divergence
    alert_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    severity VARCHAR(20) DEFAULT 'Medium', -- High, Medium, Low
    message TEXT NOT NULL,
    trigger_value DECIMAL(20,6),
    threshold_value DECIMAL(20,6),
    is_active BOOLEAN DEFAULT TRUE,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for alert tracking
CREATE INDEX IF NOT EXISTS idx_sector_alerts_date ON sector_alerts(alert_date DESC);
CREATE INDEX IF NOT EXISTS idx_sector_alerts_active ON sector_alerts(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_sector_alerts_sector ON sector_alerts(sector);

-- ========================================
-- View: sector_rankings
-- Current sector rankings by strength
-- ========================================
CREATE OR REPLACE VIEW sector_rankings AS
SELECT
    s.sector,
    s.strength_score,
    s.total_stocks,
    s.buy_signals,
    s.avg_priority_score,
    s.momentum,
    s.trend_direction,
    s.relative_strength,
    s.score_date,
    ROW_NUMBER() OVER (ORDER BY s.strength_score DESC) as rank,
    CASE
        WHEN ROW_NUMBER() OVER (ORDER BY s.strength_score DESC) <= 3 THEN 'Top'
        WHEN ROW_NUMBER() OVER (ORDER BY s.strength_score DESC) > (SELECT COUNT(DISTINCT sector) FROM sector_scores WHERE score_date = CURRENT_DATE) - 3 THEN 'Bottom'
        ELSE 'Middle'
    END as tier
FROM sector_scores s
WHERE s.score_date = CURRENT_DATE
ORDER BY s.strength_score DESC;

-- ========================================
-- View: sector_summary
-- Comprehensive sector overview
-- ========================================
CREATE OR REPLACE VIEW sector_summary AS
SELECT
    ss.sector,
    ss.strength_score,
    ss.total_stocks,
    ss.buy_signals,
    ss.wait_signals,
    ss.sell_signals,
    ss.avg_priority_score,
    ss.momentum,
    ss.trend_direction,
    sm.momentum_score,
    sm.velocity,
    sm.breakout_probability,
    (SELECT COUNT(*) FROM sector_alerts WHERE sector = ss.sector AND is_active = TRUE) as active_alerts,
    sr.rank,
    sr.tier
FROM sector_scores ss
LEFT JOIN sector_momentum sm ON ss.sector = sm.sector AND ss.score_date = sm.analysis_date
LEFT JOIN sector_rankings sr ON ss.sector = sr.sector
WHERE ss.score_date = CURRENT_DATE
ORDER BY ss.strength_score DESC;

-- ========================================
-- View: sector_rotation_trends
-- Recent sector rotation patterns
-- ========================================
CREATE OR REPLACE VIEW sector_rotation_trends AS
SELECT
    rotation_date,
    from_sector,
    to_sector,
    rotation_type,
    confidence_level,
    strength_change,
    notes,
    ROW_NUMBER() OVER (PARTITION BY rotation_date ORDER BY ABS(strength_change) DESC) as importance_rank
FROM sector_rotation
WHERE rotation_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY rotation_date DESC, ABS(strength_change) DESC;

-- ========================================
-- Function: update_sector_score
-- Calculate and update sector strength score
-- ========================================
CREATE OR REPLACE FUNCTION update_sector_score(
    p_sector VARCHAR(100),
    p_score_date DATE DEFAULT CURRENT_DATE
) RETURNS DECIMAL(5,2) AS $$
DECLARE
    v_strength_score DECIMAL(5,2);
    v_total_stocks INTEGER;
    v_buy_signals INTEGER;
    v_avg_priority DECIMAL(5,2);
BEGIN
    -- Count stocks and signals for this sector
    SELECT
        COUNT(*) FILTER (WHERE sr.scan_date = p_score_date),
        COUNT(*) FILTER (WHERE sr.scan_date = p_score_date AND sr.recommendation = 'BUY'),
        AVG(sr.priority_score) FILTER (WHERE sr.scan_date = p_score_date)
    INTO v_total_stocks, v_buy_signals, v_avg_priority
    FROM scan_results sr
    JOIN tickers t ON sr.ticker_id = t.ticker_id
    WHERE t.sector = p_sector AND t.active = TRUE;

    -- Calculate strength score (weighted average)
    v_strength_score := COALESCE(
        (v_buy_signals::DECIMAL / NULLIF(v_total_stocks, 0) * 40) + -- 40% weight on buy signal ratio
        (COALESCE(v_avg_priority, 0) * 0.6), -- 60% weight on avg priority
        0
    );

    -- Insert or update sector score
    INSERT INTO sector_scores (
        sector, score_date, strength_score, total_stocks, buy_signals, avg_priority_score
    ) VALUES (
        p_sector, p_score_date, v_strength_score, COALESCE(v_total_stocks, 0),
        COALESCE(v_buy_signals, 0), v_avg_priority
    )
    ON CONFLICT (sector, score_date)
    DO UPDATE SET
        strength_score = EXCLUDED.strength_score,
        total_stocks = EXCLUDED.total_stocks,
        buy_signals = EXCLUDED.buy_signals,
        avg_priority_score = EXCLUDED.avg_priority_score,
        updated_at = CURRENT_TIMESTAMP;

    RETURN v_strength_score;
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- Trigger: auto_update_sector_timestamp
-- ========================================
CREATE OR REPLACE FUNCTION update_sector_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_sector_scores_timestamp
    BEFORE UPDATE ON sector_scores
    FOR EACH ROW
    EXECUTE FUNCTION update_sector_timestamp();

-- ========================================
-- Initial Data: Sector List
-- ========================================
-- Create initial sector scores for all known sectors
INSERT INTO sector_scores (sector, score_date, strength_score, total_stocks)
VALUES
    ('Technology', CURRENT_DATE, 0, 0),
    ('Healthcare', CURRENT_DATE, 0, 0),
    ('Financial Services', CURRENT_DATE, 0, 0),
    ('Consumer Cyclical', CURRENT_DATE, 0, 0),
    ('Communication', CURRENT_DATE, 0, 0),
    ('Industrials', CURRENT_DATE, 0, 0),
    ('Consumer Defensive', CURRENT_DATE, 0, 0),
    ('Energy', CURRENT_DATE, 0, 0),
    ('Utilities', CURRENT_DATE, 0, 0),
    ('Real Estate', CURRENT_DATE, 0, 0),
    ('Basic Materials', CURRENT_DATE, 0, 0)
ON CONFLICT (sector, score_date) DO NOTHING;

-- ========================================
-- Comments for documentation
-- ========================================
COMMENT ON TABLE sector_scores IS 'Daily strength scores for each market sector';
COMMENT ON TABLE sector_rotation IS 'Track sector leadership rotation events';
COMMENT ON TABLE sector_momentum IS 'Momentum indicators by sector';
COMMENT ON TABLE sector_correlations IS 'Correlation coefficients between sectors';
COMMENT ON TABLE sector_alerts IS 'Sector-level alerts and signals';
COMMENT ON VIEW sector_rankings IS 'Current sector rankings by strength';
COMMENT ON VIEW sector_summary IS 'Comprehensive sector overview';
COMMENT ON VIEW sector_rotation_trends IS 'Recent sector rotation patterns';
COMMENT ON FUNCTION update_sector_score IS 'Calculate and update sector strength score';

-- ========================================
-- Permissions (if needed)
-- ========================================
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO app_user;

-- Migration complete
SELECT 'Migration 010: Sector Analysis Tables created successfully' as status;
