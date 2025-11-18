"""
Pre-cache Stock Prices for Eddie

Populates price_cache table with recent price data for all active tickers.
This ensures Eddie can make prompt decisions without waiting for API calls.
"""

import logging
from datetime import date, timedelta
from tradingagents.database import get_db_connection, TickerOperations
from tradingagents.dataflows.interface import route_to_vendor_with_cache

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def precache_prices(days_back: int = 90, max_tickers: int = None):
    """
    Pre-cache prices for all active tickers.
    
    Args:
        days_back: Number of days of historical data to cache
        max_tickers: Maximum number of tickers to process (None for all)
    """
    db = get_db_connection()
    ticker_ops = TickerOperations(db)
    
    # Get active tickers
    active_tickers = ticker_ops.get_all_tickers(active_only=True)
    
    if max_tickers:
        active_tickers = active_tickers[:max_tickers]
    
    logger.info(f"Found {len(active_tickers)} active tickers to cache")
    
    # Date range
    start_date = (date.today() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    end_date = date.today().strftime('%Y-%m-%d')
    
    logger.info(f"Caching prices from {start_date} to {end_date}")
    
    # Cache prices for each ticker
    cached_count = 0
    failed_count = 0
    
    for i, ticker in enumerate(active_tickers, 1):
        symbol = ticker['symbol']
        
        try:
            logger.info(f"[{i}/{len(active_tickers)}] Caching {symbol}...")
            route_to_vendor_with_cache('get_stock_data', symbol, start_date, end_date)
            cached_count += 1
            
        except Exception as e:
            logger.warning(f"Failed to cache {symbol}: {e}")
            failed_count += 1
            continue
    
    logger.info("="*60)
    logger.info(f"✅ Caching complete!")
    logger.info(f"   Successfully cached: {cached_count} tickers")
    logger.info(f"   Failed: {failed_count} tickers")
    logger.info("="*60)


if __name__ == "__main__":
    import sys
    
    days_back = int(sys.argv[1]) if len(sys.argv) > 1 else 90
    max_tickers = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    precache_prices(days_back=days_back, max_tickers=max_tickers)

