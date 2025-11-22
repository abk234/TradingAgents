# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Trading Commands Module

Provides command-line tools for viewing trading metrics and setups.
"""

import sys
from typing import List, Dict, Any, Optional
from datetime import date
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from tradingagents.database.scan_ops import ScanOperations
from tradingagents.utils.screener_table_formatter import (
    format_price,
    format_gain_percentage,
    format_recommendation_clean,
    get_recommendation_rank
)

console = Console()


def show_professional_trades(min_rr: float = 2.0, limit: int = 20):
    """
    Show only professional-grade trades (R/R >= min_rr).

    Args:
        min_rr: Minimum R/R ratio (default: 2.0)
        limit: Maximum number of results
    """
    scan_ops = ScanOperations()
    results = scan_ops.get_scan_results(scan_date=date.today())

    # Add recommendation to results
    for result in results:
        result['_recommendation'] = result.get('recommendation', 'HOLD')

    # Filter by R/R ratio
    quality_trades = [
        r for r in results
        if r.get('risk_reward_ratio') and r.get('risk_reward_ratio') >= min_rr
    ]

    # Sort by recommendation first, then R/R ratio
    quality_trades.sort(
        key=lambda x: (
            get_recommendation_rank(x.get('recommendation', '')),
            -x.get('risk_reward_ratio', 0)
        )
    )

    # Limit results
    quality_trades = quality_trades[:limit]

    if not quality_trades:
        console.print(f"\n[yellow]No trades found with R/R >= {min_rr}[/yellow]\n")
        console.print("[dim]Try lowering the minimum R/R ratio or run a fresh scan.[/dim]\n")
        return

    # Create table
    title = f"🎯 Professional-Grade Trades (R/R >= {min_rr})"
    table = Table(
        title=title,
        title_style="bold cyan",
        show_header=True,
        header_style="bold white on blue",
        border_style="blue",
        show_lines=False
    )

    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Symbol", style="bold cyan", width=7)
    table.add_column("Action", justify="left", width=12)
    table.add_column("Entry", justify="right", width=9)
    table.add_column("Target", justify="right", width=9)
    table.add_column("Stop", justify="right", width=9)
    table.add_column("Gain%", justify="right", width=7)
    table.add_column("R/R", justify="right", width=6)
    table.add_column("RSI", justify="center", width=4)

    for idx, trade in enumerate(quality_trades, 1):
        # Extract data
        symbol = trade.get('symbol', 'N/A')
        recommendation = trade.get('recommendation', 'HOLD')
        entry = trade.get('entry_price_min')
        target = trade.get('target')
        stop = trade.get('stop_loss')
        gain_pct = trade.get('gain_percent')
        rr = trade.get('risk_reward_ratio')

        # Get RSI from technical_signals
        technical_signals = trade.get('technical_signals')
        if isinstance(technical_signals, str):
            import json
            try:
                technical_signals = json.loads(technical_signals)
            except:
                technical_signals = {}
        rsi = technical_signals.get('rsi') if isinstance(technical_signals, dict) else None

        # Format R/R with quality indicator
        rr_formatted = "[dim]--[/dim]"
        if rr is not None:
            rr_val = float(rr)
            if rr_val >= 3.0:
                rr_formatted = f"[bold green]{rr_val:.1f} ✨[/bold green]"
            elif rr_val >= 2.0:
                rr_formatted = f"[green]{rr_val:.1f}[/green]"
            else:
                rr_formatted = f"[cyan]{rr_val:.1f}[/cyan]"

        # Format RSI
        rsi_formatted = "[dim]--[/dim]"
        if rsi is not None:
            if rsi < 30:
                rsi_formatted = f"[bold green]{rsi:.0f}[/bold green]"
            elif rsi < 40:
                rsi_formatted = f"[green]{rsi:.0f}[/green]"
            else:
                rsi_formatted = f"[dim]{rsi:.0f}[/dim]"

        table.add_row(
            str(idx),
            symbol,
            format_recommendation_clean(recommendation),
            format_price(entry) if entry else "[dim]--[/dim]",
            format_price(target) if target else "[dim]--[/dim]",
            format_price(stop) if stop else "[dim]--[/dim]",
            format_gain_percentage(gain_pct) if gain_pct else "[dim]--[/dim]",
            rr_formatted,
            rsi_formatted
        )

    console.print()
    console.print(table)
    console.print()

    # Summary
    avg_rr = sum(t.get('risk_reward_ratio', 0) for t in quality_trades) / len(quality_trades)
    avg_gain = sum(t.get('gain_percent', 0) for t in quality_trades) / len(quality_trades)
    buy_count = sum(1 for t in quality_trades if 'BUY' in t.get('recommendation', '').upper())

    summary = Text()
    summary.append(f"\n📊 Summary\n", style="bold cyan")
    summary.append(f"  • Total Opportunities: ", style="white")
    summary.append(f"{len(quality_trades)}\n", style="bold white")
    summary.append(f"  • BUY Signals: ", style="white")
    summary.append(f"{buy_count}\n", style="bold green")
    summary.append(f"  • Average R/R: ", style="white")
    summary.append(f"{avg_rr:.2f}\n", style="bold cyan")
    summary.append(f"  • Average Gain: ", style="white")
    summary.append(f"+{avg_gain:.1f}%\n", style="bold green")

    console.print(Panel(summary, border_style="blue"))
    console.print()

    # Tip
    console.print("[dim]💡 Use './quick_run.sh analyze SYMBOL' for detailed analysis[/dim]\n")


def show_trade_setups(min_rr: float = 2.0, limit: int = 10, account_size: float = 10000, risk_pct: float = 1.0):
    """
    Show detailed trade setups with position sizing.

    Args:
        min_rr: Minimum R/R ratio
        limit: Maximum number of setups to show
        account_size: Account size for position sizing
        risk_pct: Risk percentage per trade (default: 1%)
    """
    scan_ops = ScanOperations()
    results = scan_ops.get_scan_results(scan_date=date.today())

    # Add recommendation
    for result in results:
        result['_recommendation'] = result.get('recommendation', 'HOLD')

    # Filter by R/R and BUY signals
    quality_trades = [
        r for r in results
        if r.get('risk_reward_ratio') and r.get('risk_reward_ratio') >= min_rr
        and 'BUY' in r.get('recommendation', '').upper()
    ]

    # Sort by R/R ratio
    quality_trades.sort(key=lambda x: -x.get('risk_reward_ratio', 0))
    quality_trades = quality_trades[:limit]

    if not quality_trades:
        console.print(f"\n[yellow]No BUY setups found with R/R >= {min_rr}[/yellow]\n")
        return

    console.print(f"\n[bold cyan]🎯 Detailed Trade Setups (R/R >= {min_rr})[/bold cyan]")
    console.print(f"[dim]Account: ${account_size:,.0f} | Risk per trade: {risk_pct}% = ${account_size * risk_pct / 100:,.0f}[/dim]\n")

    for idx, trade in enumerate(quality_trades, 1):
        symbol = trade.get('symbol', 'N/A')
        entry = float(trade.get('entry_price_min', 0) or 0)
        target = float(trade.get('target', 0) or 0)
        stop = float(trade.get('stop_loss', 0) or 0)
        gain_pct = float(trade.get('gain_percent', 0) or 0)
        rr = float(trade.get('risk_reward_ratio', 0) or 0)

        # Position sizing calculation
        risk_per_share = entry - stop if entry and stop else 0
        risk_amount = account_size * (risk_pct / 100)
        shares = int(risk_amount / risk_per_share) if risk_per_share > 0 else 0
        total_cost = shares * entry if entry else 0
        max_loss = shares * risk_per_share if risk_per_share > 0 else 0
        max_gain = shares * (target - entry) if target and entry else 0

        # Create setup table
        setup = Table(
            title=f"#{idx} {symbol}",
            title_style="bold cyan",
            show_header=False,
            border_style="blue",
            box=box.ROUNDED,
            width=80
        )

        setup.add_column("Field", style="white", width=20)
        setup.add_column("Value", style="cyan bold", width=25)
        setup.add_column("Info", style="dim", width=30)

        # Price levels
        setup.add_row("Entry Price", f"${entry:.2f}", "Recommended buy point")
        setup.add_row("Target Price", f"${target:.2f}", f"+{gain_pct:.1f}% gain")
        setup.add_row("Stop Loss", f"${stop:.2f}", f"Risk: ${risk_per_share:.2f}/share")

        setup.add_section()

        # Risk/Reward
        rr_quality = "✨ Excellent" if rr >= 3.0 else "✅ Good" if rr >= 2.0 else "Fair"
        setup.add_row("Risk/Reward", f"{rr:.2f}:1", rr_quality)

        setup.add_section()

        # Position sizing
        setup.add_row("Shares to Buy", f"{shares}", f"Based on {risk_pct}% risk")
        setup.add_row("Total Cost", f"${total_cost:,.0f}", f"{(total_cost/account_size*100):.1f}% of account")
        setup.add_row("Max Loss", f"${max_loss:,.0f}", f"{(max_loss/account_size*100):.1f}% of account")
        setup.add_row("Max Gain", f"${max_gain:,.0f}", f"{(max_gain/account_size*100):.1f}% of account")

        console.print(setup)
        console.print()


def calculate_position_size(symbol: str, account_size: float = 10000, risk_pct: float = 1.0):
    """
    Calculate position size for a specific ticker.

    Args:
        symbol: Stock ticker symbol
        account_size: Account size
        risk_pct: Risk percentage per trade
    """
    scan_ops = ScanOperations()
    results = scan_ops.get_scan_results(scan_date=date.today())

    # Find the ticker
    trade = next((r for r in results if r.get('symbol', '').upper() == symbol.upper()), None)

    if not trade:
        console.print(f"\n[red]Error: {symbol} not found in today's scan results[/red]\n")
        console.print("[dim]Run './quick_run.sh screener' first to scan stocks[/dim]\n")
        return

    entry = float(trade.get('entry_price_min', 0) or 0)
    target = float(trade.get('target', 0) or 0)
    stop = float(trade.get('stop_loss', 0) or 0)
    gain_pct = float(trade.get('gain_percent', 0) or 0)
    rr = float(trade.get('risk_reward_ratio', 0) or 0)

    if not entry or not stop:
        console.print(f"\n[red]Error: Missing entry or stop loss data for {symbol}[/red]\n")
        return

    # Calculate position size
    risk_per_share = entry - stop
    risk_amount = account_size * (risk_pct / 100)
    shares = int(risk_amount / risk_per_share)
    total_cost = shares * entry
    max_loss = shares * risk_per_share
    max_gain = shares * (target - entry) if target else 0

    # Display
    console.print(f"\n[bold cyan]Position Size Calculator: {symbol}[/bold cyan]\n")

    calc_table = Table(show_header=False, border_style="blue", box=box.ROUNDED)
    calc_table.add_column("Field", style="white", width=25)
    calc_table.add_column("Value", style="cyan bold", width=25)

    calc_table.add_row("Account Size", f"${account_size:,.0f}")
    calc_table.add_row("Risk per Trade", f"{risk_pct}% = ${risk_amount:,.0f}")

    calc_table.add_section()

    calc_table.add_row("Entry Price", f"${entry:.2f}")
    calc_table.add_row("Stop Loss", f"${stop:.2f}")
    calc_table.add_row("Target Price", f"${target:.2f}" if target else "N/A")

    calc_table.add_section()

    calc_table.add_row("Risk per Share", f"${risk_per_share:.2f}")
    calc_table.add_row("Reward per Share", f"${(target - entry):.2f}" if target else "N/A")
    calc_table.add_row("R/R Ratio", f"{rr:.2f}:1" if rr else "N/A")

    calc_table.add_section()

    calc_table.add_row("🎯 Shares to Buy", f"[bold]{shares}[/bold]")
    calc_table.add_row("Total Investment", f"${total_cost:,.0f} ({(total_cost/account_size*100):.1f}%)")
    calc_table.add_row("Maximum Loss", f"${max_loss:,.0f} ({(max_loss/account_size*100):.2f}%)")
    calc_table.add_row("Maximum Gain", f"${max_gain:,.0f} ({(max_gain/account_size*100):.1f}%)" if target else "N/A")

    console.print(calc_table)
    console.print()

    # Orders to place
    console.print("[bold yellow]📝 Orders to Place:[/bold yellow]")
    console.print(f"  1. Limit Buy: {shares} shares @ ${entry:.2f}")
    console.print(f"  2. Stop Loss: {shares} shares @ ${stop:.2f}")
    console.print(f"  3. Limit Sell: {shares} shares @ ${target:.2f}\n" if target else "")


def show_trade_summary():
    """Show summary of today's actionable trades."""
    scan_ops = ScanOperations()
    results = scan_ops.get_scan_results(scan_date=date.today())

    if not results:
        console.print("\n[yellow]No scan results for today. Run screener first.[/yellow]\n")
        return

    # Add recommendations
    for result in results:
        result['_recommendation'] = result.get('recommendation', 'HOLD')

    # Count by quality
    total = len(results)
    excellent = sum(1 for r in results if r.get('risk_reward_ratio') and r.get('risk_reward_ratio') >= 3.0)
    professional = sum(1 for r in results if r.get('risk_reward_ratio') and r.get('risk_reward_ratio') >= 2.0)
    fair = sum(1 for r in results if r.get('risk_reward_ratio') and 1.0 <= r.get('risk_reward_ratio') < 2.0)
    poor = sum(1 for r in results if r.get('risk_reward_ratio') and 0 < r.get('risk_reward_ratio') < 1.0)

    # Count by recommendation
    buys = sum(1 for r in results if 'BUY' in r.get('recommendation', '').upper())
    holds = sum(1 for r in results if 'HOLD' in r.get('recommendation', '').upper() or 'NEUTRAL' in r.get('recommendation', '').upper())
    waits = sum(1 for r in results if 'WAIT' in r.get('recommendation', '').upper())

    console.print(f"\n[bold cyan]📊 Today's Trade Summary[/bold cyan]")
    console.print(f"[dim]Scan Date: {date.today()}[/dim]\n")

    # Summary table
    summary = Table(show_header=True, header_style="bold white on blue", border_style="blue")
    summary.add_column("Category", style="white", width=30)
    summary.add_column("Count", justify="right", width=10)
    summary.add_column("Percentage", justify="right", width=15)

    summary.add_row("Total Stocks Scanned", str(total), "100%")
    summary.add_section()
    summary.add_row("[bold green]Excellent (R/R >= 3.0)", f"[bold green]{excellent}", f"[bold green]{(excellent/total*100):.1f}%")
    summary.add_row("[green]Professional (R/R >= 2.0)", f"[green]{professional}", f"[green]{(professional/total*100):.1f}%")
    summary.add_row("[cyan]Fair (R/R 1.0-2.0)", f"[cyan]{fair}", f"[cyan]{(fair/total*100):.1f}%")
    summary.add_row("[yellow]Poor (R/R < 1.0)", f"[yellow]{poor}", f"[yellow]{(poor/total*100):.1f}%")
    summary.add_section()
    summary.add_row("[bold]BUY Signals", f"[bold]{buys}", f"[bold]{(buys/total*100):.1f}%")
    summary.add_row("HOLD/NEUTRAL", str(holds), f"{(holds/total*100):.1f}%")
    summary.add_row("WAIT", str(waits), f"{(waits/total*100):.1f}%")

    console.print(summary)
    console.print()

    # Top opportunities
    quality_buys = [
        r for r in results
        if r.get('risk_reward_ratio') and r.get('risk_reward_ratio') >= 2.0
        and 'BUY' in r.get('recommendation', '').upper()
    ]
    quality_buys.sort(key=lambda x: -(x.get('risk_reward_ratio') or 0))

    if quality_buys:
        console.print(f"[bold yellow]🎯 Top {min(5, len(quality_buys))} Professional-Grade Opportunities:[/bold yellow]")
        for idx, trade in enumerate(quality_buys[:5], 1):
            symbol = trade.get('symbol', 'N/A')
            entry = trade.get('entry_price_min', 0)
            target = trade.get('target', 0)
            gain = trade.get('gain_percent', 0)
            rr = trade.get('risk_reward_ratio', 0)

            quality = "✨" if rr >= 3.0 else "✅"
            console.print(f"  {idx}. {quality} {symbol:6s} @ ${entry:7.2f} → ${target:7.2f} (+{gain:4.1f}%, R/R {rr:.1f})")
        console.print()

    console.print("[dim]💡 Use './quick_run.sh professional' to see all professional-grade trades[/dim]")
    console.print("[dim]💡 Use './quick_run.sh setups' for detailed trade setups with position sizing[/dim]\n")


def main():
    """Main entry point for trading commands."""
    import argparse

    parser = argparse.ArgumentParser(description='Trading Metrics Commands')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Professional command
    prof_parser = subparsers.add_parser('professional', help='Show professional-grade trades')
    prof_parser.add_argument('--min-rr', type=float, default=2.0, help='Minimum R/R ratio')
    prof_parser.add_argument('--limit', type=int, default=20, help='Maximum results')

    # Setups command
    setup_parser = subparsers.add_parser('setups', help='Show detailed trade setups')
    setup_parser.add_argument('--min-rr', type=float, default=2.0, help='Minimum R/R ratio')
    setup_parser.add_argument('--limit', type=int, default=10, help='Maximum setups')
    setup_parser.add_argument('--account', type=float, default=10000, help='Account size')
    setup_parser.add_argument('--risk', type=float, default=1.0, help='Risk percentage')

    # Position command
    pos_parser = subparsers.add_parser('position', help='Calculate position size')
    pos_parser.add_argument('symbol', help='Stock ticker symbol')
    pos_parser.add_argument('--account', type=float, default=10000, help='Account size')
    pos_parser.add_argument('--risk', type=float, default=1.0, help='Risk percentage')

    # Summary command
    subparsers.add_parser('summary', help='Show trade summary')

    args = parser.parse_args()

    if args.command == 'professional':
        show_professional_trades(min_rr=args.min_rr, limit=args.limit)
    elif args.command == 'setups':
        show_trade_setups(min_rr=args.min_rr, limit=args.limit,
                         account_size=args.account, risk_pct=args.risk)
    elif args.command == 'position':
        calculate_position_size(args.symbol, account_size=args.account, risk_pct=args.risk)
    elif args.command == 'summary':
        show_trade_summary()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
