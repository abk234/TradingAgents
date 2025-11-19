import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional

def get_stock(ticker: str, start_date: str, end_date: str) -> str:
    """
    Get stock data from Alpaca API.
    Returns CSV string in format: Date,Open,High,Low,Close,Adj Close,Volume
    """
    api_key = os.getenv("ALPACA_API_KEY")
    api_secret = os.getenv("ALPACA_SECRET_KEY")
    base_url = os.getenv("ALPACA_BASE_URL", "https://data.alpaca.markets/v2")
    
    if not api_key or not api_secret:
        raise ValueError("Alpaca API keys not found. Please set ALPACA_API_KEY and ALPACA_SECRET_KEY.")

    headers = {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": api_secret
    }

    # Convert dates to RFC3339 format
    start = datetime.strptime(start_date, "%Y-%m-%d").isoformat() + "Z"
    end = datetime.strptime(end_date, "%Y-%m-%d").isoformat() + "Z"
    
    url = f"{base_url}/stocks/{ticker}/bars"
    params = {
        "start": start,
        "end": end,
        "timeframe": "1Day",
        "limit": 10000
    }

    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        raise RuntimeError(f"Alpaca API error: {response.text}")

    data = response.json()
    bars = data.get("bars", [])
    
    if not bars:
        return "Date,Open,High,Low,Close,Adj Close,Volume\n"

    # Convert to DataFrame for easy CSV formatting
    df = pd.DataFrame(bars)
    df['t'] = pd.to_datetime(df['t']).dt.date
    
    # Rename columns to match expected format
    df = df.rename(columns={
        't': 'Date',
        'o': 'Open',
        'h': 'High',
        'l': 'Low',
        'c': 'Close',
        'v': 'Volume'
    })
    
    # Alpaca doesn't provide Adj Close in bars, use Close
    df['Adj Close'] = df['Close']
    
    # Reorder columns
    df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]
    
    return df.to_csv(index=False)
