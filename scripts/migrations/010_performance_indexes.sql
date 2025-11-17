-- ============================================================================
-- Performance Optimization Indexes
-- Add composite indexes for common query patterns
-- ============================================================================

-- Composite index for recent analyses by ticker and decision
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analyses_ticker_decision_date 
    ON analyses(ticker_id, final_decision, analysis_date DESC)
    WHERE final_decision IS NOT NULL;

-- Composite index for daily scans by date and priority
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_daily_scans_date_priority 
    ON daily_scans(scan_date DESC, priority_score DESC, priority_rank)
    WHERE priority_score IS NOT NULL;

-- Composite index for performance tracking
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_performance_ticker_return 
    ON performance_tracking(ticker_id, actual_return_pct DESC, entry_date DESC)
    WHERE actual_return_pct IS NOT NULL;

-- Partial index for active tickers only
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tickers_active_high_priority 
    ON tickers(symbol, sector) 
    WHERE active = true AND priority_tier = 1;

-- Index for buy signals with high confidence
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_buy_signals_confident 
    ON buy_signals(ticker_id, signal_date DESC, confidence_score DESC)
    WHERE signal_type IN ('BUY', 'STRONG_BUY') AND confidence_score >= 70;

-- Index for recent portfolio actions
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_portfolio_actions_recent 
    ON portfolio_actions(action_date DESC, ticker_id, action_type);

-- Index for price data range queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_daily_prices_ticker_range 
    ON daily_prices(ticker_id, price_date DESC, close);

-- GIN index for JSONB columns (technical_signals in daily_scans)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_daily_scans_signals_gin 
    ON daily_scans USING gin(technical_signals);

-- GIN index for array columns (triggered_alerts)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_daily_scans_alerts_gin 
    ON daily_scans USING gin(triggered_alerts);

-- ============================================================================
-- Analyze tables to update statistics
-- ============================================================================
ANALYZE tickers;
ANALYZE daily_prices;
ANALYZE daily_scans;
ANALYZE analyses;
ANALYZE buy_signals;
ANALYZE portfolio_actions;
ANALYZE performance_tracking;

-- ============================================================================
-- Completion message
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE 'Performance indexes created successfully!';
    RAISE NOTICE 'Run EXPLAIN ANALYZE on your queries to verify index usage.';
END $$;

