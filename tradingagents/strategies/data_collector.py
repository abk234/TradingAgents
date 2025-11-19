"""
Strategy Data Collector

Collects all data needed for strategy evaluation.
Reuses existing data fetching infrastructure to ensure consistency.
"""

from typing import Dict, Any, Optional
import logging
import json
from datetime import date, timedelta

from tradingagents.dataflows.interface import route_to_vendor
from tradingagents.dataflows.config import get_config
from tradingagents.dividends.dividend_metrics import DividendMetrics
from tradingagents.database import get_db_connection

logger = logging.getLogger(__name__)


class StrategyDataCollector:
    """
    Collects all data needed for strategy evaluation.
    
    Reuses existing data fetching functions to ensure:
    - Consistency with current system
    - No code duplication
    - Same data sources and formats
    """
    
    def __init__(self, config: Dict[str, Any] = None, use_database_first: bool = True):
        """
        Initialize data collector.
        
        Args:
            config: Configuration dictionary (optional)
            use_database_first: If True, use database data (daily_scans) first, then fall back to API
        """
        self.config = config or get_config()
        self.dividend_metrics = DividendMetrics()
        self.use_database_first = use_database_first
        self.db_conn = get_db_connection() if use_database_first else None
    
    def collect_all_data(
        self,
        ticker: str,
        analysis_date: str = None
    ) -> Dict[str, Any]:
        """
        Collect all data types needed for strategies.
        
        Args:
            ticker: Stock symbol (e.g., "AAPL")
            analysis_date: Analysis date in YYYY-MM-DD format (defaults to today)
        
        Returns:
            Dictionary with all data:
            {
                "market_data": {...},
                "fundamental_data": {...},
                "technical_data": {...},
                "news_data": {...},
                "dividend_data": {...},
            }
        """
        if analysis_date is None:
            analysis_date = date.today().strftime("%Y-%m-%d")
        
        logger.info(f"Collecting data for {ticker} as of {analysis_date}")
        
        try:
            # Parse analysis date
            analysis_date_obj = date.fromisoformat(analysis_date)
            
            # Calculate date range for historical data
            end_date = analysis_date_obj
            start_date = end_date - timedelta(days=252)  # ~1 year
            
            # Try database first if enabled, then fall back to API
            if self.use_database_first:
                # Try to get data from daily_scans (fast, consistent with screener)
                db_data = self._collect_from_database(ticker, analysis_date_obj)
                if db_data:
                    logger.info(f"Using database data for {ticker} from daily_scans")
                    market_data = db_data.get('market_data', {})
                    fundamental_data = db_data.get('fundamental_data', {})
                    technical_data = db_data.get('technical_data', {})
                    
                    # Fill in any missing data from API
                    if not market_data.get('current_price'):
                        logger.debug(f"Filling missing market data for {ticker} from API")
                        api_market = self._collect_market_data(ticker, start_date, end_date)
                        market_data.update(api_market)
                    
                    if not fundamental_data.get('pe_ratio'):
                        logger.debug(f"Filling missing fundamental data for {ticker} from API")
                        api_fundamental = self._collect_fundamental_data(ticker)
                        fundamental_data.update(api_fundamental)
                    
                    if not technical_data.get('rsi'):
                        logger.debug(f"Filling missing technical data for {ticker} from API")
                        api_technical = self._collect_technical_data(ticker, start_date, end_date)
                        technical_data.update(api_technical)
                else:
                    # No database data, use API
                    logger.info(f"No database data found for {ticker}, using API")
                    market_data = self._collect_market_data(ticker, start_date, end_date)
                    fundamental_data = self._collect_fundamental_data(ticker)
                    technical_data = self._collect_technical_data(ticker, start_date, end_date)
            else:
                # Use API only
                market_data = self._collect_market_data(ticker, start_date, end_date)
                fundamental_data = self._collect_fundamental_data(ticker)
                technical_data = self._collect_technical_data(ticker, start_date, end_date)
            
            # Collect news data
            news_data = self._collect_news_data(ticker)
            
            # Collect dividend data
            dividend_data = self._collect_dividend_data(ticker)
            
            return {
                "market_data": market_data,
                "fundamental_data": fundamental_data,
                "technical_data": technical_data,
                "news_data": news_data,
                "dividend_data": dividend_data,
                "analysis_date": analysis_date,
                "ticker": ticker,
            }
        
        except Exception as e:
            logger.error(f"Error collecting data for {ticker}: {e}")
            raise
    
    def _collect_market_data(
        self,
        ticker: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Collect market data (price, volume, etc.)."""
        try:
            # Get stock data using route_to_vendor directly
            stock_data_str = route_to_vendor(
                "get_stock_data",
                ticker,
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )
            
            # Parse stock data (assuming it returns formatted string or dict)
            # This may need adjustment based on actual return format
            market_data = {
                "ticker": ticker,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "raw_data": stock_data_str,
            }
            
            # Get fundamentals for current price, market cap, etc.
            fundamentals_str = route_to_vendor(
                "get_fundamentals",
                ticker,
                end_date.strftime("%Y-%m-%d")
            )
            
            # Try to extract key metrics from fundamentals
            # Note: This is a simplified extraction - may need enhancement
            if isinstance(fundamentals_str, dict):
                market_data.update({
                    "current_price": fundamentals_str.get("Current Price") or fundamentals_str.get("current_price"),
                    "market_cap": fundamentals_str.get("Market Cap") or fundamentals_str.get("market_cap"),
                    "volume": fundamentals_str.get("Volume") or fundamentals_str.get("volume"),
                })
            
            return market_data
        
        except Exception as e:
            logger.warning(f"Error collecting market data for {ticker}: {e}")
            return {"ticker": ticker, "error": str(e)}
    
    def _collect_fundamental_data(self, ticker: str) -> Dict[str, Any]:
        """Collect fundamental data (P/E, revenue, etc.)."""
        try:
            # Get fundamentals using route_to_vendor directly
            from datetime import date
            curr_date = date.today().strftime("%Y-%m-%d")
            fundamentals = route_to_vendor("get_fundamentals", ticker, curr_date)
            
            # If it's a string, try to parse it
            # If it's already a dict, use it directly
            if isinstance(fundamentals, str):
                # Try to extract key metrics from string
                # This is a simplified approach - may need enhancement
                fundamental_data = {
                    "raw": fundamentals,
                    "ticker": ticker,
                }
            else:
                fundamental_data = fundamentals if isinstance(fundamentals, dict) else {"raw": str(fundamentals)}
            
            # Get balance sheet, cash flow, income statement
            try:
                balance_sheet = route_to_vendor("get_balance_sheet", ticker)
                cashflow = route_to_vendor("get_cashflow", ticker)
                income_statement = route_to_vendor("get_income_statement", ticker)
                
                fundamental_data.update({
                    "balance_sheet": balance_sheet,
                    "cashflow": cashflow,
                    "income_statement": income_statement,
                })
            except Exception as e:
                logger.warning(f"Error collecting financial statements for {ticker}: {e}")
            
            return fundamental_data
        
        except Exception as e:
            logger.warning(f"Error collecting fundamental data for {ticker}: {e}")
            return {"ticker": ticker, "error": str(e)}
    
    def _collect_technical_data(
        self,
        ticker: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Collect technical data (RSI, MACD, etc.)."""
        try:
            # Get indicators using route_to_vendor directly
            # Note: get_indicators expects indicator name, curr_date, and lookback_days
            # We'll get multiple indicators
            lookback_days = (end_date - start_date).days
            
            indicators_data = {}
            # Use correct indicator names supported by the system
            indicator_names = ["rsi", "macd", "boll", "close_50_sma", "close_10_ema"]
            
            for indicator in indicator_names:
                try:
                    indicator_result = route_to_vendor(
                        "get_indicators",
                        ticker,
                        indicator,
                        end_date.strftime("%Y-%m-%d"),
                        lookback_days
                    )
                    indicators_data[indicator] = indicator_result
                except Exception as e:
                    logger.debug(f"Error getting {indicator} for {ticker}: {e}")
            
            technical_data = {
                "ticker": ticker,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "indicators": indicators_data,
            }
            
            return technical_data
        
        except Exception as e:
            logger.warning(f"Error collecting technical data for {ticker}: {e}")
            return {"ticker": ticker, "error": str(e)}
    
    def _collect_news_data(self, ticker: str) -> Dict[str, Any]:
        """Collect news data."""
        try:
            # Get news using route_to_vendor directly
            news = route_to_vendor("get_news", ticker)
            
            news_data = {
                "ticker": ticker,
                "raw": news,
            }
            
            return news_data
        
        except Exception as e:
            logger.warning(f"Error collecting news data for {ticker}: {e}")
            return {"ticker": ticker, "error": str(e)}
    
    def _collect_dividend_data(self, ticker: str) -> Dict[str, Any]:
        """Collect dividend data."""
        try:
            # Use existing dividend metrics
            dividend_safety = self.dividend_metrics.analyze_dividend_safety(ticker)
            
            dividend_data = {
                "ticker": ticker,
                "safety_analysis": dividend_safety,
            }
            
            return dividend_data
        
        except Exception as e:
            logger.warning(f"Error collecting dividend data for {ticker}: {e}")
            return {"ticker": ticker, "error": str(e)}
    
    def _collect_from_database(
        self,
        ticker: str,
        analysis_date: date
    ) -> Optional[Dict[str, Any]]:
        """
        Collect data from database (daily_scans table) - fast and consistent with screener.
        
        Args:
            ticker: Stock symbol
            analysis_date: Analysis date
            
        Returns:
            Dictionary with market_data, fundamental_data, technical_data, or None if not found
        """
        if not self.db_conn:
            return None
        
        try:
            with self.db_conn.get_connection() as conn:
                with conn.cursor() as cur:
                    # Get latest scan result for this ticker
                    query = """
                    SELECT 
                        sr.price,
                        sr.volume,
                        sr.technical_signals,
                        sr.pe_ratio,
                        sr.forward_pe,
                        sr.market_cap,
                        sr.enterprise_value,
                        sr.enterprise_to_ebitda,
                        sr.priority_score
                    FROM daily_scans sr
                    JOIN tickers t ON sr.ticker_id = t.ticker_id
                    WHERE t.symbol = %s
                      AND sr.scan_date = %s
                    ORDER BY sr.scan_date DESC
                    LIMIT 1
                    """
                    
                    cur.execute(query, (ticker, analysis_date))
                    result = cur.fetchone()
                    
                    if not result:
                        return None
                    
                    # Parse technical signals JSON
                    technical_signals_json = result[2]
                    if isinstance(technical_signals_json, str):
                        technical_signals = json.loads(technical_signals_json)
                    else:
                        technical_signals = technical_signals_json or {}
                    
                    # Build market data
                    market_data = {
                        "ticker": ticker,
                        "current_price": float(result[0]) if result[0] else None,
                        "volume": int(result[1]) if result[1] else None,
                        "market_cap": int(result[6]) if result[6] else None,
                    }
                    
                    # Build fundamental data
                    fundamental_data = {
                        "ticker": ticker,
                        "pe_ratio": float(result[3]) if result[3] else None,
                        "Trailing P/E": float(result[3]) if result[3] else None,
                        "forward_pe": float(result[4]) if result[4] else None,
                        "market_cap": int(result[6]) if result[6] else None,
                        "enterprise_value": int(result[7]) if result[7] else None,
                        "enterprise_to_ebitda": float(result[8]) if result[8] else None,
                    }
                    
                    # Build technical data (extract from technical_signals JSON)
                    technical_data = {
                        "ticker": ticker,
                        "rsi": technical_signals.get('rsi'),
                        "RSI": technical_signals.get('rsi'),
                        "macd": technical_signals.get('macd'),
                        "MACD": technical_signals.get('macd'),
                        "macd_signal": technical_signals.get('macd_signal'),
                        "MACD_Signal": technical_signals.get('macd_signal'),
                        "ma_20": technical_signals.get('ma_20') or technical_signals.get('ma20'),
                        "MA_20": technical_signals.get('ma_20') or technical_signals.get('ma20'),
                        "ma_50": technical_signals.get('ma_50') or technical_signals.get('ma50'),
                        "MA_50": technical_signals.get('ma_50') or technical_signals.get('ma50'),
                        "volume_ratio": technical_signals.get('volume_ratio', 1.0),
                        "bb_upper": technical_signals.get('bb_upper'),
                        "bb_lower": technical_signals.get('bb_lower'),
                        "bb_middle": technical_signals.get('bb_middle'),
                    }
                    
                    # Log data completeness
                    completeness = {
                        "market": "✓" if market_data.get('current_price') else "✗",
                        "fundamental": "✓" if fundamental_data.get('pe_ratio') else "✗",
                        "technical": "✓" if technical_data.get('rsi') else "✗",
                    }
                    logger.debug(f"Database data completeness for {ticker}: {completeness}")
                    
                    return {
                        "market_data": market_data,
                        "fundamental_data": fundamental_data,
                        "technical_data": technical_data,
                    }
        
        except Exception as e:
            logger.warning(f"Error collecting from database for {ticker}: {e}")
            return None

