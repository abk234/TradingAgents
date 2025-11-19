#!/usr/bin/env python3
"""
Entry Price Trend Viewer

Shows how entry price recommendations have changed over time for specific tickers.
This helps identify:
- Entry price stability (are recommendations consistent?)
- Entry price accuracy (did prices reach recommended entry points?)
- Optimal entry windows (when was the best time to enter?)

Usage:
    python scripts/show_entry_price_trends.py AAPL
    python scripts/show_entry_price_trends.py --all --days 7
    python scripts/show_entry_price_trends.py NVDA TSLA --days 14
"""

import sys
import argparse
from datetime import date, timedelta
from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich import box

# Add parent directory to path
sys.path.insert(0, '/Users/lxupkzwjs/Developer/eval/TradingAgents')

from tradingagents.database import get_db_connection, TickerOperations
from tradingagents.database.scan_ops import ScanOperations


console = Console()


def format_price(price: float) -> str:
    """Format price with color."""
    if price is None:
        return "[dim]N/A[/dim]"
    return f"${price:.2f}"


def format_outcome(status: str) -> str:
    """Format outcome status with color."""
    if status is None:
        return "[dim]Not tracked[/dim]"

    colors = {
        'HIT_TARGET': 'green',
        'MISSED_OPPORTUNITY': 'yellow',
        'STILL_WAITING': 'cyan',
        'STOPPED_OUT': 'red'
    }
    color = colors.get(status, 'white')
    return f"[{color}]{status.replace('_', ' ')}[/{color}]"


def format_timing(timing: str) -> str:
    """Format entry timing with color."""
    if timing is None:
        return "[dim]N/A[/dim]"

    colors = {
        'BUY_NOW': 'bright_green',
        'ACCUMULATE': 'green',
        'WAIT_FOR_PULLBACK': 'yellow',
        'AVOID': 'red'
    }
    color = colors.get(timing, 'white')
    return f"[{color}]{timing.replace('_', ' ')}[/{color}]"


def show_ticker_trends(symbol: str, days: int = 30):
    """Show entry price trends for a specific ticker."""
    db = get_db_connection()
    ticker_ops = TickerOperations(db)

    # Get ticker_id
    ticker = ticker_ops.get_ticker(symbol=symbol)
    if not ticker:
        console.print(f"[red]Ticker {symbol} not found in database[/red]")
        return

    ticker_id = ticker['ticker_id']

    # Get entry price history
    query = """
        SELECT
            scan_date,
            current_price,
            entry_price_min,
            entry_price_max,
            entry_timing,
            entry_price_reasoning,
            priority_score,
            rsi,
            bb_lower,
            bb_upper,
            support_level,
            outcome_status,
            actual_entry_price,
            days_to_entry,
            entry_discount_pct,
            opportunity_score
        FROM entry_price_history
        WHERE symbol = %s
            AND scan_date >= %s
        ORDER BY scan_date DESC
    """

    start_date = date.today() - timedelta(days=days)
    results = db.execute_dict_query(query, (symbol, start_date))

    if not results:
        console.print(f"[yellow]No entry price data found for {symbol} in the last {days} days[/yellow]")
        console.print("[dim]Run the screener to generate entry price recommendations[/dim]")
        return

    # Create table
    table = Table(
        title=f"📊 Entry Price Trends - {symbol} ({ticker['company_name']})",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )

    table.add_column("Date", justify="center", style="dim")
    table.add_column("Current\nPrice", justify="right")
    table.add_column("Entry Price\nRange", justify="center", style="green")
    table.add_column("Entry\nTiming", justify="center")
    table.add_column("RSI", justify="center", style="dim")
    table.add_column("Priority", justify="center")
    table.add_column("Outcome", justify="center")
    table.add_column("Actual\nEntry", justify="right", style="bright_green")
    table.add_column("Days to\nEntry", justify="center", style="cyan")
    table.add_column("Discount\n%", justify="right", style="bright_green")

    for row in results:
        date_str = str(row['scan_date'])
        current_price = format_price(row['current_price'])

        # Entry price range
        if row['entry_price_min'] and row['entry_price_max']:
            entry_range = f"${row['entry_price_min']:.2f} - ${row['entry_price_max']:.2f}"
        else:
            entry_range = "[dim]N/A[/dim]"

        entry_timing = format_timing(row['entry_timing'])

        # RSI
        if row['rsi']:
            rsi_val = float(row['rsi'])
            if rsi_val < 30:
                rsi_str = f"[bright_green]{rsi_val:.1f}[/bright_green]"
            elif rsi_val > 70:
                rsi_str = f"[red]{rsi_val:.1f}[/red]"
            else:
                rsi_str = f"{rsi_val:.1f}"
        else:
            rsi_str = "[dim]N/A[/dim]"

        # Priority score
        priority = str(row['priority_score']) if row['priority_score'] else "[dim]N/A[/dim]"

        # Outcome
        outcome = format_outcome(row['outcome_status'])

        # Actual entry
        actual_entry = format_price(row['actual_entry_price'])

        # Days to entry
        days_to_entry = str(row['days_to_entry']) if row['days_to_entry'] else "[dim]-[/dim]"

        # Discount percentage
        if row['entry_discount_pct']:
            discount = float(row['entry_discount_pct'])
            if discount > 0:
                discount_str = f"[bright_green]+{discount:.1f}%[/bright_green]"
            else:
                discount_str = f"[red]{discount:.1f}%[/red]"
        else:
            discount_str = "[dim]N/A[/dim]"

        table.add_row(
            date_str, current_price, entry_range, entry_timing,
            rsi_str, priority, outcome, actual_entry,
            days_to_entry, discount_str
        )

    console.print()
    console.print(table)

    # Show reasoning for most recent recommendation
    if results and results[0]['entry_price_reasoning']:
        console.print()
        console.print(f"[bold]Most Recent Reasoning:[/bold]")
        console.print(f"[dim]{results[0]['entry_price_reasoning']}[/dim]")

    # Show summary statistics
    console.print()
    console.print("[bold]Summary Statistics:[/bold]")

    # Calculate stats
    total_recommendations = len(results)
    hit_targets = len([r for r in results if r['outcome_status'] == 'HIT_TARGET'])
    still_waiting = len([r for r in results if r['outcome_status'] == 'STILL_WAITING'])
    missed = len([r for r in results if r['outcome_status'] == 'MISSED_OPPORTUNITY'])

    console.print(f"  Total Recommendations: {total_recommendations}")
    console.print(f"  [green]Hit Target: {hit_targets}[/green]")
    console.print(f"  [cyan]Still Waiting: {still_waiting}[/cyan]")
    console.print(f"  [yellow]Missed: {missed}[/yellow]")

    if hit_targets > 0:
        avg_days = sum(r['days_to_entry'] for r in results if r['days_to_entry']) / hit_targets
        console.print(f"  Average Days to Entry: {avg_days:.1f}")

        avg_discount = sum(float(r['entry_discount_pct']) for r in results if r['entry_discount_pct']) / hit_targets
        console.print(f"  Average Entry Discount: {avg_discount:.1f}%")


def show_all_trends(days: int = 7, limit: int = 10):
    """Show entry price trends for top tickers."""
    db = get_db_connection()

    query = """
        SELECT
            symbol,
            company_name,
            scan_date,
            current_price,
            entry_price_min,
            entry_price_max,
            entry_timing,
            priority_score,
            outcome_status,
            actual_entry_price,
            days_to_entry
        FROM entry_price_history
        WHERE scan_date >= %s
        ORDER BY scan_date DESC, priority_score DESC
        LIMIT %s
    """

    start_date = date.today() - timedelta(days=days)
    results = db.execute_dict_query(query, (start_date, limit))

    if not results:
        console.print(f"[yellow]No entry price data found in the last {days} days[/yellow]")
        console.print("[dim]Run the screener to generate entry price recommendations[/dim]")
        return

    # Create table
    table = Table(
        title=f"📊 Recent Entry Price Recommendations (Last {days} days)",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )

    table.add_column("Symbol", justify="left", style="bold")
    table.add_column("Date", justify="center", style="dim")
    table.add_column("Current\nPrice", justify="right")
    table.add_column("Entry Price\nRange", justify="center", style="green")
    table.add_column("Entry\nTiming", justify="center")
    table.add_column("Priority", justify="center")
    table.add_column("Outcome", justify="center")

    for row in results:
        symbol = row['symbol']
        date_str = str(row['scan_date'])
        current_price = format_price(row['current_price'])

        # Entry price range
        if row['entry_price_min'] and row['entry_price_max']:
            entry_range = f"${row['entry_price_min']:.2f} - ${row['entry_price_max']:.2f}"
        else:
            entry_range = "[dim]N/A[/dim]"

        entry_timing = format_timing(row['entry_timing'])
        priority = str(row['priority_score']) if row['priority_score'] else "[dim]N/A[/dim]"
        outcome = format_outcome(row['outcome_status'])

        table.add_row(
            symbol, date_str, current_price, entry_range,
            entry_timing, priority, outcome
        )

    console.print()
    console.print(table)


def main():
    parser = argparse.ArgumentParser(
        description="View entry price recommendation trends and outcomes"
    )
    parser.add_argument(
        'symbols',
        nargs='*',
        help='Ticker symbols to analyze (e.g., AAPL NVDA)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Show trends for all tickers'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days to look back (default: 30)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=20,
        help='Maximum number of results when using --all (default: 20)'
    )

    args = parser.parse_args()

    if args.all:
        show_all_trends(days=args.days, limit=args.limit)
    elif args.symbols:
        for symbol in args.symbols:
            show_ticker_trends(symbol.upper(), days=args.days)
            console.print()
    else:
        console.print("[yellow]Please specify ticker symbols or use --all flag[/yellow]")
        console.print()
        console.print("Examples:")
        console.print("  python scripts/show_entry_price_trends.py AAPL")
        console.print("  python scripts/show_entry_price_trends.py NVDA TSLA --days 14")
        console.print("  python scripts/show_entry_price_trends.py --all --days 7")


if __name__ == '__main__':
    main()
