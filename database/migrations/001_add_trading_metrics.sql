-- Migration: Add Target, Stop Loss, Gain%, and R/R Ratio columns to daily_scans
-- Date: 2025-11-21
-- Description: Adds columns for trader-focused metrics to the daily_scans table

-- Add new columns
ALTER TABLE daily_scans
ADD COLUMN IF NOT EXISTS target NUMERIC(10,2),
ADD COLUMN IF NOT EXISTS stop_loss NUMERIC(10,2),
ADD COLUMN IF NOT EXISTS gain_percent NUMERIC(6,2),
ADD COLUMN IF NOT EXISTS risk_reward_ratio NUMERIC(6,2);

-- Add indexes for filtering and sorting by these metrics
CREATE INDEX IF NOT EXISTS idx_daily_scans_target ON daily_scans(target) WHERE target IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_daily_scans_gain_percent ON daily_scans(gain_percent DESC) WHERE gain_percent IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_daily_scans_rr_ratio ON daily_scans(risk_reward_ratio DESC) WHERE risk_reward_ratio IS NOT NULL;

-- Add comments for documentation
COMMENT ON COLUMN daily_scans.target IS 'Price target calculated from resistance_level or bb_upper';
COMMENT ON COLUMN daily_scans.stop_loss IS 'Stop loss price calculated as 2% below support_level';
COMMENT ON COLUMN daily_scans.gain_percent IS 'Expected gain percentage: (target - entry_min) / entry_min * 100';
COMMENT ON COLUMN daily_scans.risk_reward_ratio IS 'Risk/Reward ratio: (target - entry_min) / (entry_min - stop_loss)';

-- Display success message
DO $$
BEGIN
    RAISE NOTICE 'Trading metrics columns added successfully to daily_scans table!';
END $$;
