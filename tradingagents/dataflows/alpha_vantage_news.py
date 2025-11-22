# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

from .alpha_vantage_common import _make_api_request, format_datetime_for_api
from datetime import datetime, timedelta

def get_news(ticker, start_date, end_date) -> dict[str, str] | str:
    """Returns live and historical market news & sentiment data from premier news outlets worldwide.

    Covers stocks, cryptocurrencies, forex, and topics like fiscal policy, mergers & acquisitions, IPOs.

    Args:
        ticker: Stock symbol for news articles.
        start_date: Start date for news search.
        end_date: End date for news search.

    Returns:
        Dictionary containing news sentiment data or JSON string.
    """

    params = {
        "tickers": ticker,
        "time_from": format_datetime_for_api(start_date),
        "time_to": format_datetime_for_api(end_date),
        "sort": "LATEST",
        "limit": "50",
    }
    
    return _make_api_request("NEWS_SENTIMENT", params)

def get_insider_transactions(symbol: str) -> dict[str, str] | str:
    """Returns latest and historical insider transactions by key stakeholders.

    Covers transactions by founders, executives, board members, etc.

    Args:
        symbol: Ticker symbol. Example: "IBM".

    Returns:
        Dictionary containing insider transaction data or JSON string.
    """

    params = {
        "symbol": symbol,
    }

    return _make_api_request("INSIDER_TRANSACTIONS", params)

def get_global_news(curr_date: str, look_back_days: int = 7, limit: int = 5) -> dict[str, str] | str:
    """Returns global market news & sentiment data without a specific ticker.

    Covers general market news, macroeconomic events, and broad market trends.

    Args:
        curr_date: Current date in yyyy-mm-dd format.
        look_back_days: Number of days to look back (default 7).
        limit: Maximum number of articles to return (default 5).

    Returns:
        Dictionary containing global news sentiment data or JSON string.
    """

    # Calculate start date by going back the specified number of days
    end_date = datetime.strptime(curr_date, "%Y-%m-%d")
    start_date = end_date - timedelta(days=look_back_days)

    params = {
        # No ticker specified for global news
        "time_from": format_datetime_for_api(start_date.strftime("%Y-%m-%d")),
        "time_to": format_datetime_for_api(curr_date),
        "sort": "LATEST",
        "limit": str(limit),
    }

    return _make_api_request("NEWS_SENTIMENT", params)