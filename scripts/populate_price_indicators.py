#!/usr/bin/env python3
# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Populate Technical Indicators in daily_prices Table

This script calculates and stores technical indicators (MA, RSI, Bollinger Bands, MACD)
in the daily_prices table for all tickers. This enables:
- Faster queries (no need to recalculate on-the-fly)
- Historical indicator analysis
- Better entry price calculations

Usage:
    python scripts/populate_price_indicators.py
    python scripts/populate_price_indicators.py --ticker AAPL
    python scripts/populate_price_indicators.py --days 30
"""

import sys
import argparse
from datetime import date, timedelta
import pandas as pd

sys.path.insert(0, '/Users/lxupkzwjs/Developer/eval/TradingAgents')

from tradingagents.database import get_db_connection, TickerOperations
from tradingagents.screener.indicators import TechnicalIndicators
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

console = Console()


def calculate_and_store_indicators(
    ticker_id: int,
    symbol: str,
    db,
    days: int = 365
):
    """Calculate and store indicators for a ticker."""

    # Fetch price data
    query = """
        SELECT price_date, open, high, low, close, volume
        FROM daily_prices
        WHERE ticker_id = %s
            AND price_date >= %s
        ORDER BY price_date ASC
    """

    start_date = date.today() - timedelta(days=days)
    price_data = db.execute_dict_query(query, (ticker_id, start_date))

    if not price_data or len(price_data) < 50:
        return 0

    # Convert to DataFrame
    df = pd.DataFrame(price_data)
    df.set_index('price_date', inplace=True)

    # Calculate indicators
    indicators = TechnicalIndicators()
    df = indicators.calculate_all_indicators(df)

    # Update database with indicators
    updated = 0
    for idx, row in df.iterrows():
        try:
            update_query = """
                UPDATE daily_prices
                SET ma_20 = %s,
                    ma_50 = %s,
                    ma_200 = %s,
                    rsi_14 = %s,
                    bb_upper = %s,
                    bb_lower = %s,
                    bb_middle = %s,
                    macd = %s,
                    macd_signal = %s,
                    macd_histogram = %s,
                    volume_ratio = %s
                WHERE ticker_id = %s AND price_date = %s
            """

            # Extract indicator values (handle NaN)
            ma_20 = float(row.get('ma_20')) if pd.notna(row.get('ma_20')) else None
            ma_50 = float(row.get('ma_50')) if pd.notna(row.get('ma_50')) else None
            ma_200 = float(row.get('ma_200')) if pd.notna(row.get('ma_200')) else None
            rsi_14 = float(row.get('rsi_14')) if pd.notna(row.get('rsi_14')) else None
            bb_upper = float(row.get('bb_upper')) if pd.notna(row.get('bb_upper')) else None
            bb_lower = float(row.get('bb_lower')) if pd.notna(row.get('bb_lower')) else None
            bb_middle = float(row.get('bb_middle')) if pd.notna(row.get('bb_middle')) else None
            macd = float(row.get('macd')) if pd.notna(row.get('macd')) else None
            macd_signal = float(row.get('macd_signal')) if pd.notna(row.get('macd_signal')) else None
            macd_histogram = float(row.get('macd_histogram')) if pd.notna(row.get('macd_histogram')) else None
            volume_ratio = float(row.get('volume_ratio')) if pd.notna(row.get('volume_ratio')) else None

            db.execute_query(
                update_query,
                (
                    ma_20, ma_50, ma_200, rsi_14,
                    bb_upper, bb_lower, bb_middle,
                    macd, macd_signal, macd_histogram,
                    volume_ratio,
                    ticker_id, idx
                ),
                fetch=False
            )
            updated += 1
        except Exception as e:
            console.print(f"[red]Error updating {symbol} on {idx}: {e}[/red]")
            continue

    return updated


def main():
    parser = argparse.ArgumentParser(
        description="Populate technical indicators in daily_prices table"
    )
    parser.add_argument(
        '--ticker',
        type=str,
        help='Specific ticker symbol to update (e.g., AAPL)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=365,
        help='Number of days of history to process (default: 365)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Process all tickers (default if no --ticker specified)'
    )

    args = parser.parse_args()

    console.print("\n[bold cyan]Populating Technical Indicators in daily_prices[/bold cyan]\n")

    db = get_db_connection()
    ticker_ops = TickerOperations(db)

    # Determine which tickers to process
    if args.ticker:
        ticker = ticker_ops.get_ticker(symbol=args.ticker)
        if not ticker:
            console.print(f"[red]Ticker {args.ticker} not found[/red]")
            return
        tickers = [ticker]
    else:
        tickers = ticker_ops.get_all_tickers(active_only=True)

    console.print(f"Processing {len(tickers)} ticker(s) with {args.days} days of history\n")

    # Process tickers with progress bar
    total_updated = 0
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Calculating indicators...", total=len(tickers))

        for ticker in tickers:
            symbol = ticker['symbol']
            ticker_id = ticker['ticker_id']

            progress.update(task, description=f"Processing {symbol}...")

            try:
                updated = calculate_and_store_indicators(
                    ticker_id, symbol, db, days=args.days
                )
                total_updated += updated

                if updated > 0:
                    console.print(f"  ✓ {symbol:6s}: Updated {updated} records")
                else:
                    console.print(f"  ⊙ {symbol:6s}: No data or insufficient history")

            except Exception as e:
                console.print(f"  ✗ {symbol:6s}: Error - {e}")

            progress.advance(task)

    console.print(f"\n[bold green]✓ Complete![/bold green]")
    console.print(f"Total records updated: {total_updated}")
    console.print(f"Tickers processed: {len(tickers)}\n")

    # Verification
    console.print("[bold]Verification:[/bold]")
    verification_query = """
        SELECT
            COUNT(*) as total_prices,
            COUNT(ma_20) as with_ma_20,
            COUNT(ma_50) as with_ma_50,
            COUNT(rsi_14) as with_rsi,
            COUNT(bb_lower) as with_bb
        FROM daily_prices
        WHERE price_date >= %s
    """

    start_date = date.today() - timedelta(days=args.days)
    stats = db.execute_dict_query(verification_query, (start_date,), fetch_one=True)

    if stats:
        console.print(f"  Total price records: {stats['total_prices']}")
        console.print(f"  With MA 20: {stats['with_ma_20']} ({stats['with_ma_20']/stats['total_prices']*100:.1f}%)")
        console.print(f"  With MA 50: {stats['with_ma_50']} ({stats['with_ma_50']/stats['total_prices']*100:.1f}%)")
        console.print(f"  With RSI: {stats['with_rsi']} ({stats['with_rsi']/stats['total_prices']*100:.1f}%)")
        console.print(f"  With Bollinger Bands: {stats['with_bb']} ({stats['with_bb']/stats['total_prices']*100:.1f}%)")

    console.print()


if __name__ == '__main__':
    main()
