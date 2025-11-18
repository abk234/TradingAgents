-- Migration: Add LLM prompt/response tracking to analyses table
-- Purpose: Store complete LLM interaction history for debugging, auditing, and optimization
-- Expected Impact: Full audit trail, better debugging, prompt optimization opportunities

-- Add columns to analyses table for LLM tracking
ALTER TABLE analyses ADD COLUMN IF NOT EXISTS llm_prompts JSONB;
ALTER TABLE analyses ADD COLUMN IF NOT EXISTS llm_responses JSONB;
ALTER TABLE analyses ADD COLUMN IF NOT EXISTS llm_metadata JSONB;

-- Indexes for querying LLM data (GIN indexes for JSONB)
CREATE INDEX IF NOT EXISTS idx_analyses_llm_prompts ON analyses USING gin(llm_prompts);
CREATE INDEX IF NOT EXISTS idx_analyses_llm_metadata ON analyses USING gin(llm_metadata);

-- Comments for documentation
COMMENT ON COLUMN analyses.llm_prompts IS 'All LLM prompts used in analysis (by agent name)';
COMMENT ON COLUMN analyses.llm_responses IS 'All LLM responses (by agent name)';
COMMENT ON COLUMN analyses.llm_metadata IS 'LLM usage metadata (model, tokens, cost, duration)';

-- Example data structure for llm_prompts:
-- {
--   "fundamentals_analyst": "Analyze the following fundamental data for AAPL...",
--   "technical_analyst": "Review the following technical indicators...",
--   "news_analyst": "Analyze the following news articles...",
--   "sentiment_analyst": "Evaluate market sentiment based on...",
--   "bull_researcher": "Argue in favor of buying this stock...",
--   "bear_researcher": "Argue against buying this stock...",
--   "trader": "Based on all the analysis, make a trading decision...",
--   "risk_manager": "Assess the risk of this position...",
--   "portfolio_manager": "Review this trading recommendation..."
-- }

-- Example data structure for llm_responses:
-- {
--   "fundamentals_analyst": {
--     "report": "Detailed fundamental analysis...",
--     "score": 75,
--     "recommendation": "NEUTRAL"
--   },
--   "technical_analyst": {
--     "report": "Technical analysis shows...",
--     "score": 82,
--     "signals": ["MACD bullish", "RSI oversold recovery"]
--   },
--   "trader": {
--     "action": "BUY",
--     "confidence": 0.85,
--     "reasoning": "Strong fundamentals and technical setup..."
--   }
-- }

-- Example data structure for llm_metadata:
-- {
--   "model": "gpt-4o",
--   "total_tokens": 15420,
--   "prompt_tokens": 8500,
--   "completion_tokens": 6920,
--   "estimated_cost_usd": 0.185,
--   "total_duration_seconds": 12.4,
--   "by_agent": {
--     "fundamentals_analyst": {
--       "tokens": 2500,
--       "duration_seconds": 2.1
--     },
--     "technical_analyst": {
--       "tokens": 2200,
--       "duration_seconds": 1.8
--     }
--   }
-- }
