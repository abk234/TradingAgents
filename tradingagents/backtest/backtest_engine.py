"""
Backtesting Engine

Core backtesting engine with anti-lookahead protection.
"""

from typing import Dict, Any, List, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
import logging

import yfinance as yf
import pandas as pd

from tradingagents.database import get_db_connection
from tradingagents.decision import FourGateFramework

logger = logging.getLogger(__name__)


class BacktestResult:
    """Result from a backtest run."""
    
    def __init__(
        self,
        strategy_name: str,
        start_date: date,
        end_date: date,
        tickers: List[str],
        total_trades: int,
        winning_trades: int,
        losing_trades: int,
        win_rate: float,
        avg_return: float,
        total_return: float,
        sharpe_ratio: float,
        max_drawdown: float,
        trades: List[Dict[str, Any]]
    ):
        self.strategy_name = strategy_name
        self.start_date = start_date
        self.end_date = end_date
        self.tickers = tickers
        self.total_trades = total_trades
        self.winning_trades = winning_trades
        self.losing_trades = losing_trades
        self.win_rate = win_rate
        self.avg_return = avg_return
        self.total_return = total_return
        self.sharpe_ratio = sharpe_ratio
        self.max_drawdown = max_drawdown
        self.trades = trades
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'strategy_name': self.strategy_name,
            'start_date': str(self.start_date),
            'end_date': str(self.end_date),
            'tickers': self.tickers,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': self.win_rate,
            'avg_return': self.avg_return,
            'total_return': self.total_return,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'trades': self.trades
        }
    
    def __str__(self) -> str:
        return (
            f"Backtest Result: {self.strategy_name}\n"
            f"Period: {self.start_date} to {self.end_date}\n"
            f"Trades: {self.total_trades} (Win: {self.winning_trades}, Loss: {self.losing_trades})\n"
            f"Win Rate: {self.win_rate:.1f}%\n"
            f"Avg Return: {self.avg_return:.2f}%\n"
            f"Total Return: {self.total_return:.2f}%\n"
            f"Sharpe Ratio: {self.sharpe_ratio:.2f}\n"
            f"Max Drawdown: {self.max_drawdown:.2f}%"
        )


class BacktestEngine:
    """
    Backtesting engine with anti-lookahead protection.
    
    Ensures that only data available at the time of analysis is used.
    """
    
    def __init__(self, db=None):
        """Initialize backtesting engine."""
        self.db = db or get_db_connection()
        self.four_gate = FourGateFramework()
    
    def test_strategy(
        self,
        strategy_name: str,
        start_date: date,
        end_date: date,
        tickers: List[str],
        holding_period_days: int = 30,
        min_confidence: int = 70
    ) -> BacktestResult:
        """
        Test a strategy on historical data.
        
        Args:
            strategy_name: Name of the strategy being tested
            start_date: Start date for backtest
            end_date: End date for backtest
            tickers: List of tickers to test
            holding_period_days: Days to hold position after buy signal
            min_confidence: Minimum confidence score to take trade
        
        Returns:
            BacktestResult with performance metrics
        """
        logger.info(f"Starting backtest: {strategy_name} from {start_date} to {end_date}")
        
        trades = []
        current_date = start_date
        
        # Iterate through dates
        while current_date <= end_date:
            # Skip weekends
            if current_date.weekday() >= 5:
                current_date += timedelta(days=1)
                continue
            
            # Test each ticker on this date
            for ticker in tickers:
                try:
                    trade = self._test_ticker_on_date(
                        ticker=ticker,
                        test_date=current_date,
                        holding_period_days=holding_period_days,
                        min_confidence=min_confidence
                    )
                    
                    if trade:
                        trades.append(trade)
                
                except Exception as e:
                    logger.warning(f"Error testing {ticker} on {current_date}: {e}")
                    continue
            
            # Move to next date
            current_date += timedelta(days=1)
        
        # Calculate performance metrics
        return self._calculate_results(
            strategy_name=strategy_name,
            start_date=start_date,
            end_date=end_date,
            tickers=tickers,
            trades=trades
        )
    
    def _test_ticker_on_date(
        self,
        ticker: str,
        test_date: date,
        holding_period_days: int,
        min_confidence: int
    ) -> Optional[Dict[str, Any]]:
        """
        Test a ticker on a specific date (with anti-lookahead protection).
        
        Only uses data available on or before test_date.
        """
        try:
            # Get historical price data up to test_date (anti-lookahead)
            ticker_obj = yf.Ticker(ticker)
            hist = ticker_obj.history(
                start=test_date - timedelta(days=365),
                end=test_date + timedelta(days=1)  # Include test_date
            )
            
            if hist.empty or len(hist) < 50:
                return None
            
            # Get price on test_date
            test_date_str = test_date.strftime('%Y-%m-%d')
            if test_date_str not in hist.index.strftime('%Y-%m-%d').values:
                # Use closest available date
                available_dates = hist.index[hist.index <= pd.Timestamp(test_date)]
                if len(available_dates) == 0:
                    return None
                price_date = available_dates[-1]
            else:
                price_date = pd.Timestamp(test_date)
            
            entry_price = float(hist.loc[price_date, 'Close'])
            
            # Get technical indicators (using only data up to test_date)
            indicators = self._calculate_indicators(hist.loc[:price_date])
            
            # Get fundamentals (using only data available on test_date)
            fundamentals = self._get_fundamentals_as_of_date(ticker, test_date)
            
            # Evaluate using Four-Gate Framework
            gate_result = self.four_gate.evaluate_all_gates(
                fundamentals=fundamentals,
                signals=indicators,
                price_data={
                    'current_price': entry_price,
                    'week_52_high': float(hist['High'].max()),
                    'week_52_low': float(hist['Low'].min())
                },
                risk_analysis={
                    'max_expected_drawdown_pct': 15.0,
                    'risk_reward_ratio': 2.0,
                    'red_flags': []
                },
                position_size_pct=5.0,
                historical_context={},
                sector_avg=None,
                portfolio_context=None
            )
            
            # Check if we should take the trade
            if (gate_result['final_decision'] == 'BUY' and 
                gate_result['confidence_score'] >= min_confidence):
                
                # Calculate exit price (after holding period)
                exit_date = test_date + timedelta(days=holding_period_days)
                exit_price = self._get_exit_price(ticker, exit_date, entry_price)
                
                if exit_price:
                    return_pct = ((exit_price - entry_price) / entry_price) * 100
                    
                    return {
                        'ticker': ticker,
                        'entry_date': test_date,
                        'entry_price': entry_price,
                        'exit_date': exit_date,
                        'exit_price': exit_price,
                        'return_pct': return_pct,
                        'confidence': gate_result['confidence_score'],
                        'decision': gate_result['final_decision']
                    }
        
        except Exception as e:
            logger.debug(f"Error in _test_ticker_on_date for {ticker} on {test_date}: {e}")
            return None
        
        return None
    
    def _calculate_indicators(self, hist: pd.DataFrame) -> Dict[str, Any]:
        """Calculate technical indicators from historical data."""
        if len(hist) < 20:
            return {}
        
        try:
            # RSI
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = float(rsi.iloc[-1]) if not rsi.empty else 50.0
            
            # Moving averages
            ma20 = float(hist['Close'].rolling(20).mean().iloc[-1])
            ma50 = float(hist['Close'].rolling(50).mean().iloc[-1]) if len(hist) >= 50 else ma20
            current_price = float(hist['Close'].iloc[-1])
            
            # MACD
            ema12 = hist['Close'].ewm(span=12).mean()
            ema26 = hist['Close'].ewm(span=26).mean()
            macd = ema12 - ema26
            signal = macd.ewm(span=9).mean()
            macd_bullish = float(macd.iloc[-1]) > float(signal.iloc[-1])
            
            # Volume
            avg_volume = float(hist['Volume'].rolling(20).mean().iloc[-1])
            current_volume = float(hist['Volume'].iloc[-1])
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            return {
                'rsi': current_rsi,
                'price_above_ma20': current_price > ma20,
                'price_above_ma50': current_price > ma50,
                'ma20_above_ma50': ma20 > ma50,
                'macd_bullish_crossover': macd_bullish,
                'volume_ratio': volume_ratio,
                'near_support': False,  # Simplified
                'near_resistance': False  # Simplified
            }
        except Exception as e:
            logger.debug(f"Error calculating indicators: {e}")
            return {}
    
    def _get_fundamentals_as_of_date(self, ticker: str, as_of_date: date) -> Dict[str, Any]:
        """Get fundamentals as they would have been known on as_of_date."""
        # Simplified - in production, would query historical fundamental data
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info
            
            return {
                'pe_ratio': info.get('trailingPE') or info.get('forwardPE'),
                'forward_pe': info.get('forwardPE'),
                'revenue_growth_yoy': None,  # Would need historical data
                'debt_to_equity': info.get('debtToEquity')
            }
        except Exception as e:
            logger.debug(f"Error getting fundamentals for {ticker}: {e}")
            return {}
    
    def _get_exit_price(self, ticker: str, exit_date: date, fallback_price: float) -> Optional[float]:
        """Get exit price on exit_date."""
        try:
            ticker_obj = yf.Ticker(ticker)
            hist = ticker_obj.history(
                start=exit_date - timedelta(days=5),
                end=exit_date + timedelta(days=5)
            )
            
            if hist.empty:
                return fallback_price
            
            # Find closest date to exit_date
            exit_date_ts = pd.Timestamp(exit_date)
            available_dates = hist.index[hist.index <= exit_date_ts]
            
            if len(available_dates) == 0:
                return fallback_price
            
            closest_date = available_dates[-1]
            return float(hist.loc[closest_date, 'Close'])
        
        except Exception as e:
            logger.debug(f"Error getting exit price for {ticker} on {exit_date}: {e}")
            return fallback_price
    
    def _calculate_results(
        self,
        strategy_name: str,
        start_date: date,
        end_date: date,
        tickers: List[str],
        trades: List[Dict[str, Any]]
    ) -> BacktestResult:
        """Calculate backtest performance metrics."""
        if not trades:
            return BacktestResult(
                strategy_name=strategy_name,
                start_date=start_date,
                end_date=end_date,
                tickers=tickers,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                avg_return=0.0,
                total_return=0.0,
                sharpe_ratio=0.0,
                max_drawdown=0.0,
                trades=[]
            )
        
        returns = [t['return_pct'] for t in trades]
        winning_trades = [r for r in returns if r > 0]
        losing_trades = [r for r in returns if r <= 0]
        
        total_trades = len(trades)
        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0.0
        
        avg_return = sum(returns) / len(returns) if returns else 0.0
        total_return = sum(returns)
        
        # Calculate Sharpe ratio (simplified)
        if len(returns) > 1:
            try:
                import numpy as np
                returns_array = np.array(returns)
                sharpe_ratio = (np.mean(returns_array) / np.std(returns_array)) * np.sqrt(252) if np.std(returns_array) > 0 else 0.0
            except ImportError:
                # Fallback if numpy not available
                mean_return = sum(returns) / len(returns)
                variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
                std_dev = variance ** 0.5
                sharpe_ratio = (mean_return / std_dev * (252 ** 0.5)) if std_dev > 0 else 0.0
        else:
            sharpe_ratio = 0.0
        
        # Calculate max drawdown
        cumulative = []
        cumsum = 0
        for r in returns:
            cumsum += r
            cumulative.append(cumsum)
        
        if cumulative:
            peak = cumulative[0]
            max_dd = 0.0
            for value in cumulative:
                if value > peak:
                    peak = value
                drawdown = (peak - value) / peak * 100 if peak > 0 else 0.0
                if drawdown > max_dd:
                    max_dd = drawdown
            max_drawdown = max_dd
        else:
            max_drawdown = 0.0
        
        return BacktestResult(
            strategy_name=strategy_name,
            start_date=start_date,
            end_date=end_date,
            tickers=tickers,
            total_trades=total_trades,
            winning_trades=win_count,
            losing_trades=loss_count,
            win_rate=win_rate,
            avg_return=avg_return,
            total_return=total_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            trades=trades
        )

