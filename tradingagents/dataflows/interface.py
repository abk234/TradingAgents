# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

from typing import Annotated, List, Dict
import logging

logger = logging.getLogger(__name__)

# Import from vendor-specific modules
from .local import get_YFin_data, get_finnhub_news, get_finnhub_company_insider_sentiment, get_finnhub_company_insider_transactions, get_simfin_balance_sheet, get_simfin_cashflow, get_simfin_income_statements, get_reddit_global_news, get_reddit_company_news
from .y_finance import get_YFin_data_online, get_stock_stats_indicators_window, get_balance_sheet as get_yfinance_balance_sheet, get_cashflow as get_yfinance_cashflow, get_income_statement as get_yfinance_income_statement, get_insider_transactions as get_yfinance_insider_transactions, get_fundamentals as get_yfinance_fundamentals
from .google import get_google_news
from .openai import get_stock_news_openai, get_global_news_openai, get_fundamentals_openai
from .alpha_vantage import (
    get_stock as get_alpha_vantage_stock,
    get_indicator as get_alpha_vantage_indicator,
    get_fundamentals as get_alpha_vantage_fundamentals,
    get_balance_sheet as get_alpha_vantage_balance_sheet,
    get_cashflow as get_alpha_vantage_cashflow,
    get_income_statement as get_alpha_vantage_income_statement,
    get_insider_transactions as get_alpha_vantage_insider_transactions,
    get_news as get_alpha_vantage_news,
    get_global_news as get_alpha_vantage_global_news
)
from .alpaca import get_stock as get_alpaca_stock
from .polygon import get_stock as get_polygon_stock
from .alpha_vantage_common import AlphaVantageRateLimitError

# Configuration and routing logic
from .config import get_config

# Tools organized by category
TOOLS_CATEGORIES = {
    "core_stock_apis": {
        "description": "OHLCV stock price data",
        "tools": [
            "get_stock_data"
        ]
    },
    "technical_indicators": {
        "description": "Technical analysis indicators",
        "tools": [
            "get_indicators"
        ]
    },
    "fundamental_data": {
        "description": "Company fundamentals",
        "tools": [
            "get_fundamentals",
            "get_balance_sheet",
            "get_cashflow",
            "get_income_statement"
        ]
    },
    "news_data": {
        "description": "News (public/insiders, original/processed)",
        "tools": [
            "get_news",
            "get_global_news",
            "get_insider_sentiment",
            "get_insider_transactions",
        ]
    }
}

VENDOR_LIST = [
    "local",
    "yfinance",
    "openai",
    "google",
    "alpaca",
    "polygon"
]

# Mapping of methods to their vendor-specific implementations
VENDOR_METHODS = {
    # core_stock_apis
    "get_stock_data": {
        "alpha_vantage": get_alpha_vantage_stock,
        "yfinance": get_YFin_data_online,
        "local": get_YFin_data,
        "alpaca": get_alpaca_stock,
        "polygon": get_polygon_stock,
    },
    # technical_indicators
    "get_indicators": {
        "alpha_vantage": get_alpha_vantage_indicator,
        "yfinance": get_stock_stats_indicators_window,
        "local": get_stock_stats_indicators_window
    },
    # fundamental_data
    "get_fundamentals": {
        "yfinance": get_yfinance_fundamentals,
        "alpha_vantage": get_alpha_vantage_fundamentals,
        "openai": get_fundamentals_openai,
    },
    "get_balance_sheet": {
        "alpha_vantage": get_alpha_vantage_balance_sheet,
        "yfinance": get_yfinance_balance_sheet,
        "local": get_simfin_balance_sheet,
    },
    "get_cashflow": {
        "alpha_vantage": get_alpha_vantage_cashflow,
        "yfinance": get_yfinance_cashflow,
        "local": get_simfin_cashflow,
    },
    "get_income_statement": {
        "alpha_vantage": get_alpha_vantage_income_statement,
        "yfinance": get_yfinance_income_statement,
        "local": get_simfin_income_statements,
    },
    # news_data
    "get_news": {
        "alpha_vantage": get_alpha_vantage_news,
        "openai": get_stock_news_openai,
        "google": get_google_news,
        "local": [get_finnhub_news, get_reddit_company_news, get_google_news],
    },
    "get_global_news": {
        "alpha_vantage": get_alpha_vantage_global_news,
        "openai": get_global_news_openai,
        "local": get_reddit_global_news
    },
    "get_insider_sentiment": {
        "local": get_finnhub_company_insider_sentiment
    },
    "get_insider_transactions": {
        "alpha_vantage": get_alpha_vantage_insider_transactions,
        "yfinance": get_yfinance_insider_transactions,
        "local": get_finnhub_company_insider_transactions,
    },
}

def get_category_for_method(method: str) -> str:
    """Get the category that contains the specified method."""
    for category, info in TOOLS_CATEGORIES.items():
        if method in info["tools"]:
            return category
    raise ValueError(f"Method '{method}' not found in any category")

def get_vendor(category: str, method: str = None) -> str:
    """Get the configured vendor for a data category or specific tool method.
    Tool-level configuration takes precedence over category-level.
    """
    config = get_config()

    # Check tool-level configuration first (if method provided)
    if method:
        tool_vendors = config.get("tool_vendors", {})
        if method in tool_vendors:
            return tool_vendors[method]

    # Fall back to category-level configuration
    return config.get("data_vendors", {}).get(category, "default")

def route_to_vendor(method: str, *args, **kwargs):
    """Route method calls to appropriate vendor implementation with fallback support."""
    category = get_category_for_method(method)
    vendor_config = get_vendor(category, method)
    config = get_config()

    # Handle "skip" vendor - return placeholder immediately for optional methods
    if vendor_config == "skip" or "skip" in vendor_config:
        optional_methods = [
            'get_news', 'get_global_news', 'get_insider_sentiment', 'get_insider_transactions',
            'get_fundamentals', 'get_balance_sheet', 'get_cashflow', 'get_income_statement'
        ]
        if method in optional_methods:
            print(f"INFO: Skipping '{method}' (vendor='skip' in config) - analysis will continue with available data")
            return f"Skipped: '{method}' disabled in fast mode configuration."
        else:
            raise ValueError(f"Cannot skip critical method '{method}'")

    # Handle comma-separated vendors
    primary_vendors = [v.strip() for v in vendor_config.split(',')]

    if method not in VENDOR_METHODS:
        raise ValueError(f"Method '{method}' not supported")

    # Get all available vendors for this method for fallback
    all_available_vendors = list(VENDOR_METHODS[method].keys())

    # If using Ollama, exclude OpenAI from fallbacks to avoid API key errors
    llm_provider = config.get("llm_provider", "").lower()
    if llm_provider == "ollama":
        # Remove OpenAI from fallback list when using Ollama
        all_available_vendors = [v for v in all_available_vendors if v != "openai"]
        logger.debug(f"Using Ollama - excluding OpenAI from fallbacks for {method}")

    # Create fallback vendor list: primary vendors first, then remaining vendors as fallbacks
    fallback_vendors = primary_vendors.copy()
    for vendor in all_available_vendors:
        if vendor not in fallback_vendors:
            fallback_vendors.append(vendor)

    # Debug: Print fallback ordering
    primary_str = " → ".join(primary_vendors)
    fallback_str = " → ".join(fallback_vendors)
    print(f"DEBUG: {method} - Primary: [{primary_str}] | Full fallback order: [{fallback_str}]")

    # Track results and execution state
    results = []
    vendor_attempt_count = 0
    any_primary_vendor_attempted = False
    successful_vendor = None

    for vendor in fallback_vendors:
        if vendor not in VENDOR_METHODS[method]:
            if vendor in primary_vendors:
                print(f"INFO: Vendor '{vendor}' not supported for method '{method}', falling back to next vendor")
            continue

        vendor_impl = VENDOR_METHODS[method][vendor]
        is_primary_vendor = vendor in primary_vendors
        vendor_attempt_count += 1

        # Track if we attempted any primary vendor
        if is_primary_vendor:
            any_primary_vendor_attempted = True

        # Debug: Print current attempt
        vendor_type = "PRIMARY" if is_primary_vendor else "FALLBACK"
        print(f"DEBUG: Attempting {vendor_type} vendor '{vendor}' for {method} (attempt #{vendor_attempt_count})")

        # Handle list of methods for a vendor
        if isinstance(vendor_impl, list):
            vendor_methods = [(impl, vendor) for impl in vendor_impl]
            print(f"DEBUG: Vendor '{vendor}' has multiple implementations: {len(vendor_methods)} functions")
        else:
            vendor_methods = [(vendor_impl, vendor)]

        # Run methods for this vendor
        vendor_results = []
        for impl_func, vendor_name in vendor_methods:
            try:
                print(f"DEBUG: Calling {impl_func.__name__} from vendor '{vendor_name}'...")
                result = impl_func(*args, **kwargs)
                vendor_results.append(result)
                print(f"SUCCESS: {impl_func.__name__} from vendor '{vendor_name}' completed successfully")
                    
            except AlphaVantageRateLimitError as e:
                if vendor == "alpha_vantage":
                    print(f"RATE_LIMIT: Alpha Vantage rate limit exceeded, falling back to next available vendor")
                    print(f"DEBUG: Rate limit details: {e}")
                # Continue to next vendor for fallback
                continue
            except Exception as e:
                # Log error but continue with other implementations
                print(f"FAILED: {impl_func.__name__} from vendor '{vendor_name}' failed: {e}")
                continue

        # Add this vendor's results
        if vendor_results:
            results.extend(vendor_results)
            successful_vendor = vendor
            result_summary = f"Got {len(vendor_results)} result(s)"
            print(f"SUCCESS: Vendor '{vendor}' succeeded - {result_summary}")
            
            # Stopping logic: Stop after first successful vendor for single-vendor configs
            # Multiple vendor configs (comma-separated) may want to collect from multiple sources
            if len(primary_vendors) == 1:
                print(f"DEBUG: Stopping after successful vendor '{vendor}' (single-vendor config)")
                break
        else:
            print(f"FAILED: Vendor '{vendor}' produced no results")

    # Final result summary
    if not results:
        print(f"FAILURE: All {vendor_attempt_count} vendor attempts failed for method '{method}'")

        # For news-related and fundamental methods, return a placeholder instead of failing
        # This allows analysis to continue with limited data
        optional_methods = [
            'get_news', 'get_global_news', 'get_insider_sentiment', 'get_insider_transactions',
            'get_fundamentals', 'get_balance_sheet', 'get_cashflow', 'get_income_statement'
        ]
        if method in optional_methods:
            print(f"INFO: Returning placeholder for optional method '{method}' - analysis will continue with limited data")
            return f"Data unavailable for '{method}'. All vendors require API keys or local data files that are not configured. Analysis will proceed using available technical and price data."

        # For other critical methods, still raise an error
        raise RuntimeError(f"All vendor implementations failed for method '{method}'")
    else:
        print(f"FINAL: Method '{method}' completed with {len(results)} result(s) from {vendor_attempt_count} vendor attempt(s)")

    # Return single result if only one, otherwise concatenate as string
    if len(results) == 1:
        return results[0]
    else:
        # Convert all results to strings and concatenate
        return '\n'.join(str(result) for result in results)


def route_to_vendor_with_metadata(method: str, *args, **kwargs):
    """
    Enhanced version of route_to_vendor that returns data with vendor metadata.

    Returns:
        Tuple of (data, metadata) where metadata includes:
        - vendor_used: Which vendor successfully provided the data
        - primary_vendor: Configured primary vendor
        - fallback_occurred: Whether fallback was used
        - failed_vendors: List of vendors that failed
        - timestamp: When data was fetched
    """
    from datetime import datetime

    category = get_category_for_method(method)
    vendor_config = get_vendor(category, method)

    metadata = {
        "method": method,
        "primary_vendor": vendor_config.split(',')[0].strip(),
        "timestamp": datetime.now().isoformat(),
        "vendor_used": None,
        "fallback_occurred": False,
        "failed_vendors": [],
        "attempts": 0
    }

    # Handle "skip" vendor
    if vendor_config == "skip" or "skip" in vendor_config:
        optional_methods = [
            'get_news', 'get_global_news', 'get_insider_sentiment', 'get_insider_transactions',
            'get_fundamentals', 'get_balance_sheet', 'get_cashflow', 'get_income_statement'
        ]
        if method in optional_methods:
            metadata["vendor_used"] = "skip"
            return (f"Skipped: '{method}' disabled in fast mode configuration.", metadata)

    primary_vendors = [v.strip() for v in vendor_config.split(',')]
    all_available_vendors = list(VENDOR_METHODS.get(method, {}).keys())

    fallback_vendors = primary_vendors.copy()
    for vendor in all_available_vendors:
        if vendor not in fallback_vendors:
            fallback_vendors.append(vendor)

    # Try each vendor
    for i, vendor in enumerate(fallback_vendors):
        if vendor not in VENDOR_METHODS.get(method, {}):
            if vendor in primary_vendors:
                metadata["failed_vendors"].append({"vendor": vendor, "reason": "not supported for method"})
            continue

        vendor_impl = VENDOR_METHODS[method][vendor]
        is_primary = vendor in primary_vendors
        metadata["attempts"] += 1

        if not is_primary:
            metadata["fallback_occurred"] = True

        # Handle list of methods
        vendor_methods = [(vendor_impl, vendor)] if not isinstance(vendor_impl, list) else [(impl, vendor) for impl in vendor_impl]

        for impl_func, vendor_name in vendor_methods:
            try:
                result = impl_func(*args, **kwargs)
                metadata["vendor_used"] = vendor_name
                return (result, metadata)

            except AlphaVantageRateLimitError as e:
                metadata["failed_vendors"].append({
                    "vendor": vendor_name,
                    "reason": "rate_limit",
                    "error": str(e)
                })
                continue

            except Exception as e:
                metadata["failed_vendors"].append({
                    "vendor": vendor_name,
                    "reason": "error",
                    "error": str(e)
                })
                continue

    # All vendors failed
    optional_methods = [
        'get_news', 'get_global_news', 'get_insider_sentiment', 'get_insider_transactions',
        'get_fundamentals', 'get_balance_sheet', 'get_cashflow', 'get_income_statement'
    ]

    if method in optional_methods:
        placeholder = f"Data unavailable for '{method}'. All vendors require API keys or local data files that are not configured."
        return (placeholder, metadata)

    raise RuntimeError(f"All vendor implementations failed for method '{method}'. Metadata: {metadata}")


def route_to_vendor_with_cache(method: str, *args, **kwargs):
    """
    Route method calls with caching support for stock price data.

    For get_stock_data:
        1. Check cache first
        2. If cache hit and not stale: return cached data
        3. If cache miss: fetch from vendor and cache result

    Returns:
        Same format as the original method (CSV string for get_stock_data, etc.)
    """
    # Only cache stock price data
    if method == "get_stock_data" and len(args) >= 3:
        ticker = args[0]
        start_date = args[1]
        end_date = args[2]

        # Convert string dates to date objects if needed
        from datetime import date as date_type
        if isinstance(start_date, str):
            from datetime import datetime
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if isinstance(end_date, str):
            from datetime import datetime
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        # Try cache first
        try:
            from tradingagents.database import get_db_connection
            from tradingagents.database.price_cache_ops import PriceCacheOperations

            db = get_db_connection()
            cache_ops = PriceCacheOperations(db)

            cached_prices = cache_ops.get_cached_prices(ticker, start_date, end_date)

            if cached_prices:
                logger.info(f"✓ Cache hit for {ticker} {start_date} to {end_date}")
                # Convert to CSV format (same as yfinance)
                return _prices_to_csv(cached_prices)
        except Exception as e:
            logger.warning(f"Cache lookup failed, fetching from vendor: {e}")

    # Cache miss or error - fetch from vendor
    data, metadata = route_to_vendor_with_metadata(method, *args, **kwargs)

    # Store in cache for future use (only for get_stock_data)
    if method == "get_stock_data" and data and len(args) >= 3:
        ticker = args[0]
        start_date = args[1]
        end_date = args[2]

        # Convert string dates to date objects if needed
        from datetime import date as date_type, datetime
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        try:
            from tradingagents.database import get_db_connection
            from tradingagents.database.price_cache_ops import PriceCacheOperations

            db = get_db_connection()
            cache_ops = PriceCacheOperations(db)

            prices = _csv_to_prices(data)
            is_realtime = end_date >= date_type.today()

            cache_ops.store_prices(
                ticker_symbol=ticker,
                prices=prices,
                data_source=metadata.get('vendor_used', 'unknown'),
                is_realtime=is_realtime
            )
            logger.info(f"✓ Cached {len(prices)} prices for {ticker}")
        except Exception as e:
            logger.warning(f"Failed to cache prices: {e}")

    return data


def _prices_to_csv(prices: List[Dict]) -> str:
    """Convert price dicts to CSV string (yfinance format)."""
    import io

    output = io.StringIO()
    output.write("Date,Open,High,Low,Close,Adj Close,Volume\n")

    for price in prices:
        date_str = price['date'].strftime('%Y-%m-%d') if hasattr(price['date'], 'strftime') else str(price['date'])
        open_val = price.get('open', '') if price.get('open') is not None else ''
        high_val = price.get('high', '') if price.get('high') is not None else ''
        low_val = price.get('low', '') if price.get('low') is not None else ''
        close_val = price.get('close', '') if price.get('close') is not None else ''
        adj_close_val = price.get('adj_close', '') if price.get('adj_close') is not None else ''
        volume_val = price.get('volume', '') if price.get('volume') is not None else ''

        output.write(f"{date_str},{open_val},{high_val},{low_val},{close_val},{adj_close_val},{volume_val}\n")

    return output.getvalue()


def _csv_to_prices(csv_data: str) -> List[Dict]:
    """Convert CSV string to price dicts."""
    import csv
    from io import StringIO
    from datetime import datetime

    prices = []
    reader = csv.DictReader(StringIO(csv_data))

    for row in reader:
        # Parse date
        date_val = row.get('Date', '')
        if date_val:
            try:
                date_obj = datetime.strptime(date_val, '%Y-%m-%d').date()
            except:
                date_obj = date_val

            prices.append({
                'date': date_obj,
                'open': float(row.get('Open')) if row.get('Open') and row['Open'] != '' else None,
                'high': float(row.get('High')) if row.get('High') and row['High'] != '' else None,
                'low': float(row.get('Low')) if row.get('Low') and row['Low'] != '' else None,
                'close': float(row.get('Close')) if row.get('Close') and row['Close'] != '' else None,
                'adj_close': float(row.get('Adj Close')) if row.get('Adj Close') and row['Adj Close'] != '' else None,
                'volume': int(float(row.get('Volume'))) if row.get('Volume') and row['Volume'] != '' else None
            })

    return prices