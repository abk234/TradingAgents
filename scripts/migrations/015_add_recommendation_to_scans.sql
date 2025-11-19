-- Migration 015: Add Recommendation Column to Daily Scans
-- Purpose: Store screener recommendations (BUY, STRONG BUY, HOLD, etc.) for sector analysis alignment
-- Date: 2025-11-17

-- ============================================================================
-- Add recommendation column to daily_scans table
-- ============================================================================

-- Add recommendation column (stores the actual recommendation string from screener)
ALTER TABLE daily_scans
ADD COLUMN IF NOT EXISTS recommendation VARCHAR(50);

-- Add index for faster sector analysis queries
CREATE INDEX IF NOT EXISTS idx_scans_recommendation 
ON daily_scans(scan_date, recommendation) 
WHERE recommendation IS NOT NULL;

-- Add comment explaining the column
COMMENT ON COLUMN daily_scans.recommendation IS 
'Stores the screener recommendation (BUY, STRONG BUY, HOLD, SELL, WAIT, etc.) based on technical signals. Used for sector analysis alignment.';

-- ============================================================================
-- Update existing records (optional - can be run separately)
-- ============================================================================

-- Note: This migration only adds the column. Existing records will have NULL.
-- To backfill existing records, you would need to:
-- 1. Re-run the screener, OR
-- 2. Create a separate backfill script that regenerates recommendations from technical_signals

