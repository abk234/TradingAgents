"""
Historical Replay

Replay past dates with only historical data (anti-lookahead protection).
"""

from typing import Dict, Any, Optional
from datetime import date, datetime
import logging

from tradingagents.database import get_db_connection

logger = logging.getLogger(__name__)


class HistoricalReplay:
    """
    Replay historical dates with anti-lookahead protection.
    
    Ensures that only data available on or before the replay date is used.
    """
    
    def __init__(self, db=None):
        """Initialize historical replay."""
        self.db = db or get_db_connection()
    
    def get_price_as_of_date(
        self,
        ticker: str,
        as_of_date: date
    ) -> Optional[float]:
        """
        Get price as it would have been known on as_of_date.
        
        Only uses data from database where date <= as_of_date.
        """
        query = """
            SELECT close
            FROM daily_prices dp
            JOIN tickers t ON dp.ticker_id = t.ticker_id
            WHERE t.symbol = %s
                AND dp.price_date <= %s
            ORDER BY dp.price_date DESC
            LIMIT 1
        """
        
        result = self.db.execute_query(query, (ticker, as_of_date), fetch_one=True)
        
        if result:
            return float(result[0])
        
        return None
    
    def get_indicators_as_of_date(
        self,
        ticker: str,
        as_of_date: date
    ) -> Optional[Dict[str, Any]]:
        """
        Get technical indicators as they would have been on as_of_date.
        
        Only uses data from database where date <= as_of_date.
        """
        query = """
            SELECT 
                rsi_14,
                ma_20,
                ma_50,
                ma_200,
                close,
                volume
            FROM daily_prices dp
            JOIN tickers t ON dp.ticker_id = t.ticker_id
            WHERE t.symbol = %s
                AND dp.price_date <= %s
            ORDER BY dp.price_date DESC
            LIMIT 1
        """
        
        result = self.db.execute_dict_query(query, (ticker, as_of_date), fetch_one=True)
        
        if result:
            return {
                'rsi': float(result['rsi_14']) if result['rsi_14'] else None,
                'ma20': float(result['ma_20']) if result['ma_20'] else None,
                'ma50': float(result['ma_50']) if result['ma_50'] else None,
                'ma200': float(result['ma_200']) if result['ma_200'] else None,
                'current_price': float(result['close']) if result['close'] else None,
                'volume': int(result['volume']) if result['volume'] else None
            }
        
        return None
    
    def get_analysis_as_of_date(
        self,
        ticker: str,
        as_of_date: date
    ) -> Optional[Dict[str, Any]]:
        """
        Get analysis as it would have been on as_of_date.
        
        Only returns analyses where analysis_date <= as_of_date.
        """
        query = """
            SELECT 
                a.analysis_id,
                a.analysis_date,
                a.final_decision,
                a.confidence_score,
                a.entry_price_target,
                a.stop_loss_price,
                a.expected_return_pct
            FROM analyses a
            JOIN tickers t ON a.ticker_id = t.ticker_id
            WHERE t.symbol = %s
                AND a.analysis_date <= %s
            ORDER BY a.analysis_date DESC
            LIMIT 1
        """
        
        result = self.db.execute_dict_query(query, (ticker, as_of_date), fetch_one=True)
        
        return result
    
    def validate_no_lookahead(
        self,
        ticker: str,
        analysis_date: date,
        data_date: date
    ) -> bool:
        """
        Validate that data_date is not after analysis_date (anti-lookahead check).
        
        Returns:
            True if valid (no lookahead), False if lookahead detected
        """
        if data_date > analysis_date:
            logger.warning(
                f"Lookahead detected for {ticker}: "
                f"data_date ({data_date}) > analysis_date ({analysis_date})"
            )
            return False
        
        return True

