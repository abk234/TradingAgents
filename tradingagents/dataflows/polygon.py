# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

import os
import requests
import pandas as pd
from datetime import datetime
from typing import Optional

def get_stock(ticker: str, start_date: str, end_date: str) -> str:
    """
    Get stock data from Polygon.io API.
    Returns CSV string in format: Date,Open,High,Low,Close,Adj Close,Volume
    """
    api_key = os.getenv("POLYGON_API_KEY")
    
    if not api_key:
        raise ValueError("Polygon API key not found. Please set POLYGON_API_KEY.")

    # Polygon uses YYYY-MM-DD format
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}"
    params = {
        "adjusted": "true",
        "sort": "asc",
        "limit": 50000,
        "apiKey": api_key
    }

    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        raise RuntimeError(f"Polygon API error: {response.text}")

    data = response.json()
    results = data.get("results", [])
    
    if not results:
        return "Date,Open,High,Low,Close,Adj Close,Volume\n"

    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    # Convert timestamp (ms) to date
    df['t'] = pd.to_datetime(df['t'], unit='ms').dt.date
    
    # Rename columns
    df = df.rename(columns={
        't': 'Date',
        'o': 'Open',
        'h': 'High',
        'l': 'Low',
        'c': 'Close',
        'v': 'Volume'
    })
    
    # Polygon provides adjusted data if requested, so Close is Adj Close
    df['Adj Close'] = df['Close']
    
    # Reorder columns
    df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]
    
    return df.to_csv(index=False)
