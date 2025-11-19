-- Migration: Add prompt metadata tracking to user_interactions table
-- Purpose: Track which predefined prompts are used for analytics and optimization
-- Expected Impact: Enable prompt usage analytics, performance tracking, and optimization

-- Add columns to user_interactions table for prompt tracking
ALTER TABLE user_interactions ADD COLUMN IF NOT EXISTS prompt_type TEXT;
ALTER TABLE user_interactions ADD COLUMN IF NOT EXISTS prompt_id TEXT;

-- Create indexes for prompt analytics queries
CREATE INDEX IF NOT EXISTS idx_interactions_prompt_type ON user_interactions(prompt_type);
CREATE INDEX IF NOT EXISTS idx_interactions_prompt_id ON user_interactions(prompt_id);
CREATE INDEX IF NOT EXISTS idx_interactions_prompt_feedback ON user_interactions(prompt_type, prompt_id, feedback_rating) 
    WHERE prompt_type IS NOT NULL AND feedback_rating IS NOT NULL;

-- Comments for documentation
COMMENT ON COLUMN user_interactions.prompt_type IS 'Category of predefined prompt: quick_wins, analysis, risk, market';
COMMENT ON COLUMN user_interactions.prompt_id IS 'Specific prompt identifier from prompts.config.ts';

-- Example usage:
-- prompt_type: 'quick_wins'
-- prompt_id: 'top-3-stocks'
-- This enables queries like:
-- - Most used prompts by category
-- - Average feedback rating per prompt
-- - Success rate of different prompt types

