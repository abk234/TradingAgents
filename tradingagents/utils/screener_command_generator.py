# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Command Generator

Automatically generates context-aware follow-up commands based on command results.
Eliminates the need to manually copy tickers or data from output.
Supports all quick_run.sh commands.
"""

from typing import List, Dict, Any, Optional, Union
import json


def generate_commands_from_results(results: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Generate all command categories from screener results.
    
    Args:
        results: List of screener result dictionaries
        
    Returns:
        Dictionary mapping category names to lists of commands
    """
    if not results:
        return {}
    
    commands = {}
    
    # Generate commands for each category
    commands['buy_signals'] = get_buy_signal_commands(results)
    commands['dividend_focus'] = get_dividend_commands(results)
    commands['top_n'] = get_top_n_commands(results)
    commands['sector_based'] = get_sector_commands(results)
    commands['custom_filters'] = get_custom_filter_commands(results)
    
    # Remove empty categories
    commands = {k: v for k, v in commands.items() if v}
    
    return commands


def get_buy_signal_commands(results: List[Dict[str, Any]]) -> List[str]:
    """
    Generate commands for BUY and STRONG BUY recommendations.
    
    Args:
        results: List of screener results
        
    Returns:
        List of command strings
    """
    commands = []
    
    # Filter for BUY and STRONG BUY recommendations
    buy_stocks = []
    for result in results:
        recommendation = result.get('recommendation', '') or result.get('_recommendation', '')
        if recommendation:
            rec_upper = recommendation.upper()
            if 'STRONG BUY' in rec_upper or 'STRONG_BUY' in rec_upper or 'BUY' in rec_upper:
                # Exclude WAIT, SELL, HOLD, etc.
                if 'WAIT' not in rec_upper and 'SELL' not in rec_upper and 'HOLD' not in rec_upper:
                    symbol = result.get('symbol', '')
                    if symbol:
                        buy_stocks.append(symbol)
    
    if not buy_stocks:
        return []
    
    # Limit to reasonable number of tickers per command
    max_tickers = 10
    buy_stocks_limited = buy_stocks[:max_tickers]
    
    # Generate commands
    if len(buy_stocks_limited) > 0:
        tickers_str = ' '.join(buy_stocks_limited)
        commands.append(f"./quick_run.sh analyze {tickers_str}")
        commands.append(f"./quick_run.sh indicators {tickers_str}")
        
        # Position sizing for top buy signal
        if len(buy_stocks_limited) >= 1:
            commands.append(f"./quick_run.sh position {buy_stocks_limited[0]} --account 10000 --risk 1.0")
    
    return commands


def get_dividend_commands(results: List[Dict[str, Any]]) -> List[str]:
    """
    Generate commands for dividend-focused analysis.
    
    Args:
        results: List of screener results
        
    Returns:
        List of command strings
    """
    commands = []
    
    # Find stocks with dividend yield information
    dividend_stocks = []
    for result in results:
        # Check for dividend yield in various possible fields
        # dividend_yield_pct is stored as percentage (e.g., 2.5 for 2.5%)
        dividend_yield = (
            result.get('dividend_yield_pct') or
            result.get('dividend_yield') or
            result.get('yield')
        )
        
        symbol = result.get('symbol', '')
        if symbol and dividend_yield is not None:
            try:
                # Convert to float
                if isinstance(dividend_yield, str):
                    # Remove % if present
                    dividend_yield = float(dividend_yield.replace('%', '').strip())
                elif isinstance(dividend_yield, (int, float)):
                    dividend_yield = float(dividend_yield)
                else:
                    continue
                
                # dividend_yield_pct is already a percentage (2.5 = 2.5%)
                # Only include stocks with meaningful yield (> 1%)
                if dividend_yield > 1.0:
                    dividend_stocks.append((symbol, dividend_yield))
            except (ValueError, TypeError):
                continue
    
    if not dividend_stocks:
        # Still suggest dividend income screener
        commands.append("./quick_run.sh dividend-income --top 10")
        return commands
    
    # Sort by yield (highest first)
    dividend_stocks.sort(key=lambda x: x[1], reverse=True)
    
    # Generate commands
    commands.append("./quick_run.sh dividend-income --top 10")
    
    # Analyze top dividend stocks (limit to 5)
    top_dividend_tickers = [s[0] for s in dividend_stocks[:5]]
    if top_dividend_tickers:
        tickers_str = ' '.join(top_dividend_tickers)
        commands.append(f"./quick_run.sh analyze {tickers_str}")
    
    return commands


def get_top_n_commands(results: List[Dict[str, Any]], n: int = 5) -> List[str]:
    """
    Generate commands for top N opportunities.
    
    Args:
        results: List of screener results
        n: Number of top stocks to include (default: 5)
        
    Returns:
        List of command strings
    """
    commands = []
    
    if not results:
        return []
    
    # Sort by priority score (already sorted, but ensure)
    sorted_results = sorted(results, key=lambda x: x.get('priority_score', 0), reverse=True)
    
    # Get top N symbols
    top_symbols = []
    for result in sorted_results[:n]:
        symbol = result.get('symbol', '')
        if symbol:
            top_symbols.append(symbol)
    
    if not top_symbols:
        return []
    
    tickers_str = ' '.join(top_symbols)
    
    # Generate commands
    commands.append(f"./quick_run.sh analyze {tickers_str}")
    commands.append(f"./quick_run.sh indicators {tickers_str}")
    
    # Strategy comparison for top stocks
    if len(top_symbols) >= 2:
        commands.append(f"./quick_run.sh strategy-multi {tickers_str}")
    
    return commands


def get_sector_commands(results: List[Dict[str, Any]]) -> List[str]:
    """
    Generate commands for sector-based analysis.
    
    Args:
        results: List of screener results
        
    Returns:
        List of command strings
    """
    commands = []
    
    if not results:
        return []
    
    # Group by sector
    sector_groups = {}
    for result in results:
        sector = result.get('sector', '') or result.get('sector_name', '')
        symbol = result.get('symbol', '')
        
        if sector and symbol:
            if sector not in sector_groups:
                sector_groups[sector] = []
            sector_groups[sector].append(symbol)
    
    if not sector_groups:
        return []
    
    # Find top sector (most stocks with BUY signals)
    top_sector = None
    top_sector_count = 0
    
    for sector, symbols in sector_groups.items():
        # Count BUY signals in this sector
        buy_count = 0
        for result in results:
            if result.get('symbol') in symbols:
                recommendation = result.get('recommendation', '') or result.get('_recommendation', '')
                if recommendation:
                    rec_upper = recommendation.upper()
                    if 'BUY' in rec_upper and 'SELL' not in rec_upper:
                        buy_count += 1
        
        if buy_count > top_sector_count:
            top_sector_count = buy_count
            top_sector = sector
    
    # Generate commands for top sector
    if top_sector and top_sector in sector_groups:
        sector_symbols = sector_groups[top_sector][:10]  # Limit to 10
        if sector_symbols:
            tickers_str = ' '.join(sector_symbols)
            commands.append(f"./quick_run.sh analyze {tickers_str}")
            commands.append(f"./quick_run.sh strategy-multi {tickers_str}")
    
    return commands


def get_custom_filter_commands(results: List[Dict[str, Any]]) -> List[str]:
    """
    Generate commands for custom filters (RSI, volume, etc.).
    
    Args:
        results: List of screener results
        
    Returns:
        List of command strings
    """
    commands = []
    
    if not results:
        return []
    
    # Extract RSI from technical signals
    oversold_stocks = []  # RSI < 30
    overbought_stocks = []  # RSI > 70
    high_volume_stocks = []  # Volume ratio > 1.5
    
    for result in results:
        symbol = result.get('symbol', '')
        if not symbol:
            continue
        
        # Get RSI
        rsi = None
        technical_signals = result.get('technical_signals', {})
        if isinstance(technical_signals, str):
            try:
                technical_signals = json.loads(technical_signals)
            except (json.JSONDecodeError, TypeError):
                technical_signals = {}
        
        if isinstance(technical_signals, dict):
            rsi = technical_signals.get('rsi')
            volume_ratio = technical_signals.get('volume_ratio', 1.0)
            
            if rsi is not None:
                try:
                    rsi = float(rsi)
                    if rsi < 30:
                        oversold_stocks.append(symbol)
                    elif rsi > 70:
                        overbought_stocks.append(symbol)
                except (ValueError, TypeError):
                    pass
            
            # High volume filter
            if volume_ratio and isinstance(volume_ratio, (int, float)):
                if float(volume_ratio) > 1.5:
                    high_volume_stocks.append(symbol)
    
    # Generate commands for oversold stocks
    if oversold_stocks:
        oversold_limited = oversold_stocks[:5]
        tickers_str = ' '.join(oversold_limited)
        commands.append(f"./quick_run.sh analyze {tickers_str}  # Oversold (RSI < 30)")
    
    # Generate commands for high volume stocks
    if high_volume_stocks:
        high_vol_limited = high_volume_stocks[:5]
        tickers_str = ' '.join(high_vol_limited)
        commands.append(f"./quick_run.sh analyze {tickers_str}  # High Volume")
    
    return commands


def generate_commands_for_command(
    command_name: str,
    context: Dict[str, Any] = None,
    results: List[Dict[str, Any]] = None
) -> Dict[str, List[str]]:
    """
    Generate commands for any command type based on context and results.
    
    Args:
        command_name: Name of the command (e.g., 'portfolio', 'analyze', 'dividends')
        context: Context dictionary with command-specific data
        results: Optional results list (for commands that return lists)
        
    Returns:
        Dictionary mapping category names to lists of commands
    """
    context = context or {}
    results = results or []
    
    commands = {}
    
    # Route to appropriate generator based on command type
    if command_name == 'screener' or command_name == 'top':
        commands = generate_commands_from_results(results)
    elif command_name == 'portfolio':
        commands = generate_portfolio_commands(context, results)
    elif command_name == 'analyze':
        commands = generate_analyze_commands(context)
    elif command_name == 'dividends':
        commands = generate_dividends_commands(context, results)
    elif command_name == 'performance':
        commands = generate_performance_commands(context)
    elif command_name == 'indicators':
        commands = generate_indicators_commands(context)
    elif command_name == 'alerts':
        commands = generate_alerts_commands(context, results)
    elif command_name == 'indexes':
        commands = generate_indexes_commands(context)
    elif command_name == 'strategies' or command_name == 'strategy-compare':
        commands = generate_strategy_commands(context)
    elif command_name == 'dividend-income':
        commands = generate_dividend_income_commands(results)
    else:
        # Generic commands for other command types
        commands = generate_generic_commands(command_name, context)
    
    # Remove empty categories
    commands = {k: v for k, v in commands.items() if v}
    
    return commands


def generate_portfolio_commands(
    context: Dict[str, Any],
    results: List[Dict[str, Any]] = None
) -> Dict[str, List[str]]:
    """
    Generate commands based on portfolio data.
    
    Args:
        context: Context with portfolio information
        results: Optional portfolio positions/results
        
    Returns:
        Dictionary of command categories to commands
    """
    commands = {}
    
    # Extract tickers from portfolio positions
    tickers = []
    if results:
        for result in results:
            symbol = result.get('symbol') or result.get('ticker')
            if symbol:
                tickers.append(symbol)
    elif context.get('tickers'):
        tickers = context['tickers']
    elif context.get('positions'):
        for pos in context['positions']:
            symbol = pos.get('symbol') or pos.get('ticker')
            if symbol:
                tickers.append(symbol)
    
    if tickers:
        tickers_limited = tickers[:10]  # Limit to 10
        tickers_str = ' '.join(tickers_limited)
        
        commands['portfolio_analysis'] = [
            f"./quick_run.sh analyze {tickers_str}",
            f"./quick_run.sh indicators {tickers_str}",
        ]
        
        commands['portfolio_strategies'] = [
            f"./quick_run.sh strategy-multi {tickers_str}",
        ]
    
    # Always suggest performance and evaluation
    commands['performance_review'] = [
        "./quick_run.sh performance",
        "./quick_run.sh evaluate",
        "./quick_run.sh stats"
    ]
    
    commands['dividend_planning'] = [
        "./quick_run.sh dividends",
        "./quick_run.sh dividend-income --top 10"
    ]
    
    return commands


def generate_analyze_commands(context: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Generate commands based on analyze command results.
    
    Args:
        context: Context with ticker and analysis information
        
    Returns:
        Dictionary of command categories to commands
    """
    commands = {}
    ticker = context.get('ticker', '').upper()
    
    if not ticker:
        return commands
    
    commands['technical_analysis'] = [
        f"./quick_run.sh indicators {ticker}",
        f"./quick_run.sh top 10",
    ]
    
    commands['strategy_comparison'] = [
        f"./quick_run.sh strategies {ticker}",
        f"./quick_run.sh strategy-compare {ticker}",
    ]
    
    commands['portfolio_integration'] = [
        "./quick_run.sh portfolio",
        f"./quick_run.sh position {ticker} --account 10000 --risk 1.0",
    ]
    
    commands['market_context'] = [
        "./quick_run.sh indexes",
        "./quick_run.sh screener",
    ]
    
    return commands


def generate_dividends_commands(
    context: Dict[str, Any],
    results: List[Dict[str, Any]] = None
) -> Dict[str, List[str]]:
    """
    Generate commands based on dividends command results.
    
    Args:
        context: Context with dividend information
        results: List of upcoming dividends
        
    Returns:
        Dictionary of command categories to commands
    """
    commands = {}
    
    # Extract tickers with upcoming dividends
    tickers = []
    if results:
        for result in results:
            symbol = result.get('symbol') or result.get('ticker')
            if symbol:
                tickers.append(symbol)
    elif context.get('tickers'):
        tickers = context['tickers']
    
    if tickers:
        tickers_limited = tickers[:10]
        tickers_str = ' '.join(tickers_limited)
        
        commands['dividend_analysis'] = [
            f"./quick_run.sh analyze {tickers_str}",
            "./quick_run.sh dividend-income --top 10",
        ]
    
    commands['portfolio_review'] = [
        "./quick_run.sh portfolio",
        "./quick_run.sh performance",
    ]
    
    return commands


def generate_performance_commands(context: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Generate commands based on performance command results.
    
    Args:
        context: Context with performance information
        
    Returns:
        Dictionary of command categories to commands
    """
    commands = {}
    
    commands['detailed_analysis'] = [
        "./quick_run.sh evaluate",
        "./quick_run.sh stats",
        "./quick_run.sh portfolio",
    ]
    
    commands['strategy_adjustment'] = [
        "./quick_run.sh screener",
        "./quick_run.sh top 10",
    ]
    
    commands['market_context'] = [
        "./quick_run.sh indexes",
        "./quick_run.sh digest",
    ]
    
    return commands


def generate_indicators_commands(context: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Generate commands based on indicators command results.
    
    Args:
        context: Context with ticker(s) information
        
    Returns:
        Dictionary of command categories to commands
    """
    commands = {}
    
    tickers = context.get('tickers', [])
    if isinstance(tickers, str):
        tickers = [tickers]
    
    ticker = context.get('ticker', '')
    if ticker and ticker not in tickers:
        tickers.append(ticker)
    
    if tickers:
        tickers_limited = tickers[:10]
        tickers_str = ' '.join(tickers_limited)
        
        commands['deep_analysis'] = [
            f"./quick_run.sh analyze {tickers_str}",
        ]
    
    commands['market_context'] = [
        "./quick_run.sh indexes",
        "./quick_run.sh screener",
    ]
    
    return commands


def generate_alerts_commands(
    context: Dict[str, Any],
    results: List[Dict[str, Any]] = None
) -> Dict[str, List[str]]:
    """
    Generate commands based on alerts command results.
    
    Args:
        context: Context with alert information
        results: List of triggered alerts
        
    Returns:
        Dictionary of command categories to commands
    """
    commands = {}
    
    # Extract tickers from alerts
    tickers = []
    if results:
        for result in results:
            symbol = result.get('symbol') or result.get('ticker')
            if symbol:
                tickers.append(symbol)
    elif context.get('tickers'):
        tickers = context['tickers']
    
    if tickers:
        tickers_limited = tickers[:10]
        tickers_str = ' '.join(tickers_limited)
        
        commands['alert_analysis'] = [
            f"./quick_run.sh analyze {tickers_str}",
            f"./quick_run.sh indicators {tickers_str}",
        ]
    
    commands['market_context'] = [
        "./quick_run.sh indexes",
        "./quick_run.sh screener",
    ]
    
    return commands


def generate_indexes_commands(context: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Generate commands based on indexes command results.
    
    Args:
        context: Context with market regime and sector information
        
    Returns:
        Dictionary of command categories to commands
    """
    commands = {}
    
    commands['market_analysis'] = [
        "./quick_run.sh screener",
        "./quick_run.sh top 10",
        "./quick_run.sh digest",
    ]
    
    commands['sector_focus'] = [
        "./quick_run.sh screener --sector-analysis",
    ]
    
    return commands


def generate_strategy_commands(context: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Generate commands based on strategy command results.
    
    Args:
        context: Context with ticker and strategy information
        
    Returns:
        Dictionary of command categories to commands
    """
    commands = {}
    ticker = context.get('ticker', '').upper()
    
    if ticker:
        commands['technical_analysis'] = [
            f"./quick_run.sh analyze {ticker}",
            f"./quick_run.sh indicators {ticker}",
        ]
        
        commands['portfolio_integration'] = [
            f"./quick_run.sh position {ticker} --account 10000 --risk 1.0",
            "./quick_run.sh portfolio",
        ]
    
    commands['market_context'] = [
        "./quick_run.sh indexes",
        "./quick_run.sh screener",
    ]
    
    return commands


def generate_dividend_income_commands(results: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Generate commands based on dividend income screener results.
    
    Args:
        results: List of dividend income opportunities
        
    Returns:
        Dictionary of command categories to commands
    """
    commands = {}
    
    if not results:
        return commands
    
    # Extract top dividend stocks
    tickers = []
    for result in results[:10]:  # Top 10
        symbol = result.get('symbol', '')
        if symbol:
            tickers.append(symbol)
    
    if tickers:
        tickers_str = ' '.join(tickers)
        
        commands['dividend_analysis'] = [
            f"./quick_run.sh analyze {tickers_str}",
        ]
    
    commands['portfolio_integration'] = [
        "./quick_run.sh portfolio",
        "./quick_run.sh dividends",
    ]
    
    return commands


def generate_generic_commands(
    command_name: str,
    context: Dict[str, Any]
) -> Dict[str, List[str]]:
    """
    Generate generic commands for commands without specific generators.
    
    Args:
        command_name: Name of the command
        context: Context dictionary
        
    Returns:
        Dictionary of command categories to commands
    """
    commands = {}
    
    # Generic follow-up commands
    commands['market_analysis'] = [
        "./quick_run.sh screener",
        "./quick_run.sh top 10",
    ]
    
    commands['portfolio_review'] = [
        "./quick_run.sh portfolio",
        "./quick_run.sh performance",
    ]
    
    return commands


def format_command_description(category: str, count: int = None) -> str:
    """
    Format a description for a command category.
    
    Args:
        category: Category name
        count: Number of stocks in category (optional)
        
    Returns:
        Formatted description string
    """
    descriptions = {
        'buy_signals': 'BUY Signals',
        'dividend_focus': 'Dividend Focus',
        'top_n': 'Top Opportunities',
        'sector_based': 'Sector Analysis',
        'custom_filters': 'Custom Filters',
        'portfolio_analysis': 'Portfolio Analysis',
        'portfolio_strategies': 'Strategy Comparison',
        'performance_review': 'Performance Review',
        'dividend_planning': 'Dividend Planning',
        'technical_analysis': 'Technical Analysis',
        'strategy_comparison': 'Strategy Comparison',
        'portfolio_integration': 'Portfolio Integration',
        'market_context': 'Market Context',
        'dividend_analysis': 'Dividend Analysis',
        'portfolio_review': 'Portfolio Review',
        'detailed_analysis': 'Detailed Analysis',
        'strategy_adjustment': 'Strategy Adjustment',
        'deep_analysis': 'Deep Analysis',
        'alert_analysis': 'Alert Analysis',
        'market_analysis': 'Market Analysis',
        'sector_focus': 'Sector Focus',
    }
    
    desc = descriptions.get(category, category.replace('_', ' ').title())
    
    if count is not None:
        return f"{desc} ({count} stocks)"
    
    return desc

