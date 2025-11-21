# Database Schema - Trading Metrics

**Version:** 1.0
**Last Updated:** 2025-11-21

---

## Overview

This document details the database schema for trading metrics stored in the `daily_scans` table. These metrics are calculated during each scan and stored permanently for historical analysis.

---

## Table: daily_scans

### Trading Metrics Columns

| Column Name | Type | Nullable | Description | Calculation Method |
|-------------|------|----------|-------------|-------------------|
| `target` | NUMERIC(10,2) | YES | Price target for profit-taking | min(resistance_level, bb_upper) |
| `stop_loss` | NUMERIC(10,2) | YES | Stop loss price for risk management | support_level * 0.98 OR entry_min * 0.95 |
| `gain_percent` | NUMERIC(6,2) | YES | Expected gain percentage | ((target - entry_min) / entry_min) * 100 |
| `risk_reward_ratio` | NUMERIC(6,2) | YES | Risk/Reward ratio | (target - entry_min) / (entry_min - stop_loss) |

### Complete Schema (Relevant Columns)

```sql
CREATE TABLE daily_scans (
    -- Primary Key
    scan_id SERIAL PRIMARY KEY,
    ticker_id INTEGER NOT NULL REFERENCES tickers(ticker_id),
    scan_date DATE NOT NULL,

    -- Basic Metrics
    price NUMERIC(10,2),
    volume BIGINT,
    priority_score INTEGER,
    priority_rank INTEGER,

    -- Entry Price Fields
    entry_price_min NUMERIC(10,2),      -- Most conservative entry point
    entry_price_max NUMERIC(10,2),      -- Upper bound of buy zone
    entry_timing VARCHAR(50),           -- BUY_NOW, ACCUMULATE, WAIT_FOR_PULLBACK
    entry_price_reasoning TEXT,         -- Why this entry price was chosen

    -- Technical Indicators (used in calculations)
    bb_upper NUMERIC(10,2),             -- Bollinger Band Upper
    bb_lower NUMERIC(10,2),             -- Bollinger Band Lower
    bb_middle NUMERIC(10,2),            -- Bollinger Band Middle
    support_level NUMERIC(10,2),        -- Support level below price
    resistance_level NUMERIC(10,2),     -- Resistance level above price

    -- NEW: Trading Metrics (Added 2025-11-21)
    target NUMERIC(10,2),               -- Price target
    stop_loss NUMERIC(10,2),            -- Stop loss price
    gain_percent NUMERIC(6,2),          -- Expected gain %
    risk_reward_ratio NUMERIC(6,2),     -- Risk/Reward ratio

    -- Other Fields
    technical_signals JSONB,            -- RSI, MACD, etc.
    recommendation VARCHAR(100),        -- BUY, SELL, HOLD, etc.
    pe_ratio NUMERIC(8,2),
    forward_pe NUMERIC(8,2),
    news_sentiment_score NUMERIC(5,2),

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    UNIQUE(ticker_id, scan_date)
);
```

---

## Column Details

### target

**Type:** NUMERIC(10,2)
**Range:** 0.01 to 99,999,999.99
**Nullable:** YES

**Description:**
Price target based on technical resistance levels. Represents the expected price where profit should be taken.

**Calculation:**
```sql
-- Primary: Use most conservative of resistance or BB upper
target = LEAST(resistance_level, bb_upper)

-- Fallback 1: If only one exists
target = COALESCE(resistance_level, bb_upper)

-- Fallback 2: If neither exists (rare)
target = entry_price_min * 1.05
```

**Business Rules:**
- Should be >= entry_price_min
- Typically 2-10% above entry price
- Conservative estimate (achievable target)

**Example Values:**
- AAPL: $272.01 (resistance level)
- MSFT: $493.00 (BB upper)
- NVDA: $186.44 (minimum of both)

**Indexes:**
```sql
CREATE INDEX idx_daily_scans_target
ON daily_scans(target)
WHERE target IS NOT NULL;
```

---

### stop_loss

**Type:** NUMERIC(10,2)
**Range:** 0.01 to 99,999,999.99
**Nullable:** YES

**Description:**
Stop loss price for risk management. The price at which traders should exit to limit losses.

**Calculation:**
```sql
-- Primary: 2% below support level
IF support_level IS NOT NULL THEN
    stop_loss = support_level * 0.98

-- Fallback: 5% below entry when no support exists
ELSE IF entry_price_min IS NOT NULL THEN
    stop_loss = entry_price_min * 0.95

-- No fallback: NULL (should never happen)
ELSE
    stop_loss = NULL
END IF
```

**Business Rules:**
- Must be < entry_price_min
- Typically 2-5% below entry price
- CRITICAL: Should never be NULL (risk management requirement)

**Example Values:**
- AAPL: $260.00 (2% below support $265.31)
- BAC: $49.15 (5% fallback, no support)
- WFC: $79.71 (5% fallback, no support)

**Indexes:**
```sql
CREATE INDEX idx_daily_scans_stop_loss
ON daily_scans(stop_loss)
WHERE stop_loss IS NOT NULL;
```

**Monitoring:**
```sql
-- Alert: Check for missing stop losses
SELECT COUNT(*) as missing_stops
FROM daily_scans
WHERE scan_date = CURRENT_DATE
  AND stop_loss IS NULL;

-- Expected: 0
```

---

### gain_percent

**Type:** NUMERIC(6,2)
**Range:** -99.99 to 999.99
**Nullable:** YES

**Description:**
Expected gain percentage from entry to target. Represents potential profit.

**Calculation:**
```sql
IF target IS NOT NULL AND entry_price_min IS NOT NULL AND entry_price_min > 0 THEN
    gain_percent = ((target - entry_price_min) / entry_price_min) * 100
ELSE
    gain_percent = NULL
END IF
```

**Business Rules:**
- Positive values expected (target > entry)
- Typical range: 0% to 20%
- Negative values indicate target < entry (unusual)
- Values > 50% warrant review (may be calculation error)

**Interpretation:**
| Range | Quality |
|-------|---------|
| 20%+ | Excellent |
| 10-20% | Good |
| 5-10% | Moderate |
| 0-5% | Marginal |
| Negative | Unusual - investigate |

**Example Values:**
- CAT: +4.66% (good opportunity)
- AAPL: +2.02% (moderate)
- BAC: +0.02% (marginal)
- WFC: -0.33% (unusual - target below entry)

**Indexes:**
```sql
CREATE INDEX idx_daily_scans_gain_percent
ON daily_scans(gain_percent DESC)
WHERE gain_percent IS NOT NULL;
```

**Query Examples:**
```sql
-- Find high-gain opportunities
SELECT ticker_id, symbol, entry_price_min, target, gain_percent
FROM daily_scans ds
JOIN tickers t USING (ticker_id)
WHERE scan_date = CURRENT_DATE
  AND gain_percent >= 5.0
ORDER BY gain_percent DESC
LIMIT 20;

-- Average gain by sector
SELECT t.sector,
       AVG(gain_percent) as avg_gain,
       COUNT(*) as opportunities
FROM daily_scans ds
JOIN tickers t USING (ticker_id)
WHERE scan_date = CURRENT_DATE
  AND gain_percent IS NOT NULL
GROUP BY t.sector
ORDER BY avg_gain DESC;
```

---

### risk_reward_ratio

**Type:** NUMERIC(6,2)
**Range:** -99.99 to 99.99
**Nullable:** YES

**Description:**
Risk/Reward ratio. Critical metric for professional traders. Measures potential reward vs. potential risk.

**Calculation:**
```sql
IF target IS NOT NULL
   AND entry_price_min IS NOT NULL
   AND stop_loss IS NOT NULL
   AND entry_price_min > stop_loss THEN

    risk = entry_price_min - stop_loss
    reward = target - entry_price_min

    IF risk > 0 THEN
        risk_reward_ratio = reward / risk
    ELSE
        risk_reward_ratio = NULL
    END IF
ELSE
    risk_reward_ratio = NULL
END IF
```

**Business Rules:**
- Values >= 2.0 are professional standard
- Values >= 3.0 are excellent opportunities
- Values < 1.0 indicate risk > reward (poor trades)
- Negative values indicate target < entry (skip)

**Interpretation:**
| Range | Quality | Action |
|-------|---------|--------|
| 3.0+ | Excellent | Professional grade - Strong BUY |
| 2.0-3.0 | Good | Acceptable for most traders |
| 1.5-2.0 | Fair | Consider carefully |
| 1.0-1.5 | Marginal | High risk, low reward |
| Below 1.0 | Poor | AVOID - Skip trade |

**Example Values:**
- CAT: 4.61 (excellent - risk $5.41 to make $24.92)
- NVDA: 1.40 (fair)
- AAPL: 0.81 (poor - risk > reward)
- BAC: 0.00 (very poor)

**Indexes:**
```sql
CREATE INDEX idx_daily_scans_rr_ratio
ON daily_scans(risk_reward_ratio DESC)
WHERE risk_reward_ratio IS NOT NULL;
```

**Query Examples:**
```sql
-- Find professional-grade opportunities (R/R >= 2.0)
SELECT ticker_id, symbol,
       entry_price_min, target, stop_loss,
       gain_percent, risk_reward_ratio,
       recommendation
FROM daily_scans ds
JOIN tickers t USING (ticker_id)
WHERE scan_date = CURRENT_DATE
  AND risk_reward_ratio >= 2.0
  AND recommendation LIKE '%BUY%'
ORDER BY risk_reward_ratio DESC
LIMIT 20;

-- Statistics by R/R tier
SELECT
    CASE
        WHEN risk_reward_ratio >= 3.0 THEN 'Excellent (3.0+)'
        WHEN risk_reward_ratio >= 2.0 THEN 'Good (2.0-3.0)'
        WHEN risk_reward_ratio >= 1.0 THEN 'Fair (1.0-2.0)'
        ELSE 'Poor (<1.0)'
    END as quality_tier,
    COUNT(*) as count,
    AVG(gain_percent) as avg_gain
FROM daily_scans
WHERE scan_date = CURRENT_DATE
  AND risk_reward_ratio IS NOT NULL
GROUP BY quality_tier
ORDER BY MIN(risk_reward_ratio) DESC;
```

---

## Migration Script

**File:** `database/migrations/001_add_trading_metrics.sql`

```sql
-- Migration: Add Target, Stop Loss, Gain%, and R/R Ratio columns to daily_scans
-- Date: 2025-11-21

-- Add new columns
ALTER TABLE daily_scans
ADD COLUMN IF NOT EXISTS target NUMERIC(10,2),
ADD COLUMN IF NOT EXISTS stop_loss NUMERIC(10,2),
ADD COLUMN IF NOT EXISTS gain_percent NUMERIC(6,2),
ADD COLUMN IF NOT EXISTS risk_reward_ratio NUMERIC(6,2);

-- Add indexes for filtering and sorting
CREATE INDEX IF NOT EXISTS idx_daily_scans_target
    ON daily_scans(target) WHERE target IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_daily_scans_gain_percent
    ON daily_scans(gain_percent DESC) WHERE gain_percent IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_daily_scans_rr_ratio
    ON daily_scans(risk_reward_ratio DESC) WHERE risk_reward_ratio IS NOT NULL;

-- Add comments for documentation
COMMENT ON COLUMN daily_scans.target IS
    'Price target calculated from resistance_level or bb_upper';

COMMENT ON COLUMN daily_scans.stop_loss IS
    'Stop loss price calculated as 2% below support_level or 5% below entry';

COMMENT ON COLUMN daily_scans.gain_percent IS
    'Expected gain percentage: (target - entry_min) / entry_min * 100';

COMMENT ON COLUMN daily_scans.risk_reward_ratio IS
    'Risk/Reward ratio: (target - entry_min) / (entry_min - stop_loss)';
```

---

## Data Quality Checks

### Required Checks

```sql
-- 1. Check for NULL stop losses (should be 0)
SELECT COUNT(*) as missing_stops
FROM daily_scans
WHERE scan_date = CURRENT_DATE
  AND stop_loss IS NULL;

-- 2. Check for invalid stop loss (stop >= entry)
SELECT COUNT(*) as invalid_stops
FROM daily_scans
WHERE scan_date = CURRENT_DATE
  AND stop_loss >= entry_price_min;

-- 3. Check for invalid target (target <= entry)
SELECT COUNT(*) as invalid_targets
FROM daily_scans
WHERE scan_date = CURRENT_DATE
  AND target <= entry_price_min;

-- 4. Check for negative gain_percent (unusual)
SELECT COUNT(*) as negative_gains,
       AVG(gain_percent) as avg_negative_gain
FROM daily_scans
WHERE scan_date = CURRENT_DATE
  AND gain_percent < 0;

-- 5. Check for R/R distribution
SELECT
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE risk_reward_ratio >= 2.0) as professional_grade,
    COUNT(*) FILTER (WHERE risk_reward_ratio >= 1.0 AND risk_reward_ratio < 2.0) as acceptable,
    COUNT(*) FILTER (WHERE risk_reward_ratio < 1.0) as poor,
    ROUND(AVG(risk_reward_ratio), 2) as avg_rr
FROM daily_scans
WHERE scan_date = CURRENT_DATE
  AND risk_reward_ratio IS NOT NULL;
```

### Automated Monitoring

```sql
-- Daily data quality report
CREATE OR REPLACE FUNCTION check_trading_metrics_quality(check_date DATE)
RETURNS TABLE (
    metric VARCHAR,
    status VARCHAR,
    count INTEGER,
    notes TEXT
) AS $$
BEGIN
    -- Missing stop losses
    RETURN QUERY
    SELECT 'Missing Stop Loss'::VARCHAR,
           CASE WHEN COUNT(*) = 0 THEN '✓ PASS' ELSE '✗ FAIL' END::VARCHAR,
           COUNT(*)::INTEGER,
           'All scans should have stop loss values'::TEXT
    FROM daily_scans
    WHERE scan_date = check_date AND stop_loss IS NULL;

    -- Invalid stop losses
    RETURN QUERY
    SELECT 'Invalid Stop Loss'::VARCHAR,
           CASE WHEN COUNT(*) = 0 THEN '✓ PASS' ELSE '✗ FAIL' END::VARCHAR,
           COUNT(*)::INTEGER,
           'Stop loss should be below entry price'::TEXT
    FROM daily_scans
    WHERE scan_date = check_date AND stop_loss >= entry_price_min;

    -- Professional grade opportunities
    RETURN QUERY
    SELECT 'Professional Grade (R/R >= 2.0)'::VARCHAR,
           CASE WHEN COUNT(*) >= 10 THEN '✓ PASS' ELSE '⚠ WARN' END::VARCHAR,
           COUNT(*)::INTEGER,
           'Should have at least 10 opportunities with R/R >= 2.0'::TEXT
    FROM daily_scans
    WHERE scan_date = check_date AND risk_reward_ratio >= 2.0;

END;
$$ LANGUAGE plpgsql;

-- Run daily check
SELECT * FROM check_trading_metrics_quality(CURRENT_DATE);
```

---

## Performance Considerations

### Index Strategy

**High-selectivity indexes:**
```sql
-- For filtering high-quality trades
CREATE INDEX idx_daily_scans_quality ON daily_scans(scan_date, risk_reward_ratio DESC)
WHERE risk_reward_ratio >= 2.0;

-- For finding high-gain opportunities
CREATE INDEX idx_daily_scans_high_gain ON daily_scans(scan_date, gain_percent DESC)
WHERE gain_percent >= 5.0;
```

**Partial indexes save space and improve performance:**
- Only index non-NULL values
- Only index high-quality trades (R/R >= 2.0)
- Compound indexes for common queries

### Query Optimization

**Good Query:**
```sql
-- Optimized: Uses index efficiently
SELECT * FROM daily_scans
WHERE scan_date = CURRENT_DATE
  AND risk_reward_ratio >= 2.0
ORDER BY risk_reward_ratio DESC
LIMIT 20;
```

**Bad Query:**
```sql
-- Not optimized: Function on indexed column
SELECT * FROM daily_scans
WHERE scan_date = CURRENT_DATE
  AND ROUND(risk_reward_ratio, 0) >= 2
ORDER BY risk_reward_ratio DESC;
```

---

## Backup & Recovery

### Backup Strategy

```bash
# Daily backup of trading metrics
pg_dump -h localhost -U postgres \
    -t daily_scans \
    --data-only \
    investment_intelligence \
    | gzip > backups/daily_scans_$(date +%Y%m%d).sql.gz

# Restore if needed
gunzip -c backups/daily_scans_20251121.sql.gz | \
    psql -h localhost -U postgres investment_intelligence
```

### Data Retention

```sql
-- Keep 90 days of scan history
DELETE FROM daily_scans
WHERE scan_date < CURRENT_DATE - INTERVAL '90 days';

-- Archive older data
INSERT INTO daily_scans_archive
SELECT * FROM daily_scans
WHERE scan_date < CURRENT_DATE - INTERVAL '90 days';
```

---

## API Integration

### Retrieving Trading Metrics

**Python Example:**
```python
from tradingagents.database.scan_ops import ScanOperations
from datetime import date

# Get today's scans with trading metrics
scan_ops = ScanOperations()
results = scan_ops.get_scan_results(scan_date=date.today())

# Filter for professional-grade trades
quality_trades = [
    r for r in results
    if r.get('risk_reward_ratio', 0) >= 2.0
]

# Sort by R/R ratio
quality_trades.sort(
    key=lambda x: x.get('risk_reward_ratio', 0),
    reverse=True
)

for trade in quality_trades[:10]:
    print(f"{trade['symbol']:6s} - "
          f"Entry: ${trade['entry_price_min']:.2f}, "
          f"Target: ${trade['target']:.2f}, "
          f"Stop: ${trade['stop_loss']:.2f}, "
          f"R/R: {trade['risk_reward_ratio']:.1f}")
```

**SQL Query:**
```sql
-- Get top 20 opportunities with all metrics
SELECT
    t.symbol,
    ds.entry_price_min,
    ds.target,
    ds.stop_loss,
    ds.gain_percent,
    ds.risk_reward_ratio,
    ds.recommendation,
    ts.rsi
FROM daily_scans ds
JOIN tickers t USING (ticker_id)
LEFT JOIN LATERAL (
    SELECT (technical_signals->>'rsi')::NUMERIC as rsi
) ts ON true
WHERE ds.scan_date = CURRENT_DATE
  AND ds.risk_reward_ratio >= 2.0
  AND ds.recommendation LIKE '%BUY%'
ORDER BY ds.risk_reward_ratio DESC
LIMIT 20;
```

---

## Version History

### Version 1.0 (2025-11-21)
- Added `target` column
- Added `stop_loss` column with fallback logic
- Added `gain_percent` column
- Added `risk_reward_ratio` column
- Created indexes for performance
- Added data quality checks
- Documented all calculations

### Future Enhancements
- Add `trailing_stop` for dynamic risk management
- Add `partial_exit_price` for scaled exits
- Add `confidence_score` for prediction confidence
- Historical accuracy tracking table
- Performance metrics over time

---

## References

- Main Documentation: `TRADING_METRICS_CALCULATION.md`
- Quick Reference: `TRADING_QUICK_REFERENCE.md`
- Migration Script: `database/migrations/001_add_trading_metrics.sql`
- Python Module: `tradingagents/database/scan_ops.py`

---

**Last Updated:** 2025-11-21
**Schema Version:** 1.0
**Maintained By:** Trading System Development Team
