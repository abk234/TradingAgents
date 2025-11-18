-- Migration: Add price caching table
-- Purpose: Cache stock price data to reduce API calls and improve performance
-- Expected Impact: 10x faster repeat analysis, 80% API call reduction

-- Create price_cache table
CREATE TABLE IF NOT EXISTS price_cache (
    cache_id SERIAL PRIMARY KEY,
    ticker_id INTEGER NOT NULL REFERENCES tickers(ticker_id) ON DELETE CASCADE,
    price_date DATE NOT NULL,

    -- OHLCV data
    open_price DECIMAL(12, 4),
    high_price DECIMAL(12, 4),
    low_price DECIMAL(12, 4),
    close_price DECIMAL(12, 4),
    adj_close_price DECIMAL(12, 4),
    volume BIGINT,

    -- Metadata
    data_source VARCHAR(50) NOT NULL,  -- 'yfinance', 'alpha_vantage', etc.
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_realtime BOOLEAN DEFAULT FALSE,  -- True if within market hours

    -- Constraints
    UNIQUE (ticker_id, price_date),
    CHECK (volume >= 0),
    CHECK (open_price >= 0),
    CHECK (high_price >= low_price)
);

-- Indexes for fast lookup
CREATE INDEX idx_price_cache_ticker_date ON price_cache(ticker_id, price_date);
CREATE INDEX idx_price_cache_fetched_at ON price_cache(fetched_at);
CREATE INDEX idx_price_cache_source ON price_cache(data_source);

-- Index for cleanup queries (partial index for efficiency)
CREATE INDEX idx_price_cache_realtime ON price_cache(is_realtime, fetched_at)
    WHERE is_realtime = TRUE;

-- Comments for documentation
COMMENT ON TABLE price_cache IS 'Cached stock price data to reduce API calls and improve performance';
COMMENT ON COLUMN price_cache.ticker_id IS 'Foreign key to tickers table';
COMMENT ON COLUMN price_cache.price_date IS 'Date of the price data';
COMMENT ON COLUMN price_cache.data_source IS 'Vendor that provided the data (yfinance, alpha_vantage, etc.)';
COMMENT ON COLUMN price_cache.fetched_at IS 'When the data was fetched and cached';
COMMENT ON COLUMN price_cache.is_realtime IS 'True if fetched during market hours - expires faster (5 min vs 24 hours)';
COMMENT ON COLUMN price_cache.adj_close_price IS 'Adjusted close price (for splits, dividends)';

-- Grant permissions (adjust as needed)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON price_cache TO tradingagents_app;
-- GRANT USAGE, SELECT ON SEQUENCE price_cache_cache_id_seq TO tradingagents_app;
