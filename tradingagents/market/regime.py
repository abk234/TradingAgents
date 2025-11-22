# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def detect_market_regime(ticker: str = "SPY") -> str:
    """
    Detect the current market regime based on a benchmark ticker (default SPY).
    
    Returns:
        "BULL", "BEAR", or "VOLATILE"
    """
    try:
        stock = yf.Ticker(ticker)
        # Get last 6 months of data
        hist = stock.history(period="6mo")
        
        if hist.empty:
            return "VOLATILE" # Default fallback
            
        # Calculate 50-day and 200-day SMA
        hist['SMA50'] = hist['Close'].rolling(window=50).mean()
        hist['SMA200'] = hist['Close'].rolling(window=200).mean()
        
        current_price = hist['Close'].iloc[-1]
        sma50 = hist['SMA50'].iloc[-1]
        sma200 = hist['SMA200'].iloc[-1]
        
        # Determine regime
        if current_price > sma50 and sma50 > sma200:
            return "BULL"
        elif current_price < sma50 and sma50 < sma200:
            return "BEAR"
        else:
            return "VOLATILE"
            
    except Exception as e:
        print(f"Error detecting market regime: {e}")
        return "VOLATILE"
