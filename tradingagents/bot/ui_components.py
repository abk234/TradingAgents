import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def create_stock_chart(ticker: str, period: str = "6mo") -> Optional[go.Figure]:
    """
    Create a candlestick chart for a given ticker.
    
    Args:
        ticker: Stock ticker symbol
        period: Data period (e.g., "1mo", "3mo", "6mo", "1y")
        
    Returns:
        Plotly Figure object or None if data fetch fails
    """
    try:
        # Fetch data
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        
        if hist.empty:
            return None
            
        # Create figure
        fig = go.Figure(data=[go.Candlestick(
            x=hist.index,
            open=hist['Open'],
            high=hist['High'],
            low=hist['Low'],
            close=hist['Close'],
            name=ticker
        )])
        
        # Add moving averages
        hist['MA20'] = hist['Close'].rolling(window=20).mean()
        hist['MA50'] = hist['Close'].rolling(window=50).mean()
        
        fig.add_trace(go.Scatter(
            x=hist.index, 
            y=hist['MA20'], 
            line=dict(color='orange', width=1),
            name='MA 20'
        ))
        
        fig.add_trace(go.Scatter(
            x=hist.index, 
            y=hist['MA50'], 
            line=dict(color='blue', width=1),
            name='MA 50'
        ))
        
        # Update layout
        fig.update_layout(
            title=f'{ticker} Stock Price ({period})',
            yaxis_title='Price (USD)',
            xaxis_title='Date',
            template='plotly_dark',
            height=500,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating chart for {ticker}: {e}")
        return None

def create_portfolio_chart(portfolio_history: list) -> Optional[go.Figure]:
    """
    Create a portfolio value chart.
    
    Args:
        portfolio_history: List of dicts with 'date' and 'value'
    """
    try:
        if not portfolio_history:
            return None
            
        df = pd.DataFrame(portfolio_history)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['value'],
            mode='lines+markers',
            name='Portfolio Value',
            line=dict(color='#00ff00', width=2)
        ))
        
        fig.update_layout(
            title='Portfolio Performance',
            yaxis_title='Value (USD)',
            xaxis_title='Date',
            template='plotly_dark',
            height=400
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating portfolio chart: {e}")
        return None
