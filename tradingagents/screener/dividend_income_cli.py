# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Dividend Income CLI

Command-line interface for dividend income screener.
"""

import argparse
import sys
import logging
from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .dividend_income import DividendIncomeScreener
from tradingagents.database import get_db_connection
from tradingagents.utils.screener_table_formatter import (
    format_recommendation_clean,
    format_price,
    format_gain_percentage,
    format_rsi
)
import json

logger = logging.getLogger(__name__)
console = Console()


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format float as percentage with color."""
    if value is None:
        return "N/A"

    formatted = f"{value * 100:.{decimals}f}%"

    if value >= 0.05:  # 5%+
        return f"[bold green]{formatted}[/bold green]"
    elif value >= 0.03:  # 3-5%
        return f"[green]{formatted}[/green]"
    elif value >= 0.02:  # 2-3%
        return f"[yellow]{formatted}[/yellow]"
    else:
        return f"[dim]{formatted}[/dim]"


def format_score(score: int, category: str) -> str:
    """Format score with color based on category."""
    if category == "EXCELLENT":
        return f"[bold green]{score}[/bold green]"
    elif category == "VERY GOOD":
        return f"[green]{score}[/green]"
    elif category == "GOOD":
        return f"[cyan]{score}[/cyan]"
    elif category == "FAIR":
        return f"[yellow]{score}[/yellow]"
    else:
        return f"[red]{score}[/red]"


def format_currency(value: float) -> str:
    """Format value as currency."""
    if value is None:
        return "N/A"
    return f"${value:,.2f}"


def format_years(years: int) -> str:
    """Format consecutive years with color."""
    if years >= 25:
        return f"[bold green]{years}[/bold green]"
    elif years >= 10:
        return f"[green]{years}[/green]"
    elif years >= 5:
        return f"[cyan]{years}[/cyan]"
    else:
        return f"[yellow]{years}[/yellow]"


def display_results(results: List[Dict[str, Any]], show_details: bool = False):
    """
    Display dividend income screening results in a formatted table.

    Args:
        results: List of screening results
        show_details: Whether to show detailed breakdown
    """
    if not results:
        console.print("[yellow]No dividend income opportunities found.[/yellow]")
        return

    # Main results table
    table = Table(
        title="💰 Dividend Income Opportunities - Top Stocks for Living Off Dividends",
        title_style="bold cyan",
        show_header=True,
        header_style="bold white on blue",
        border_style="blue"
    )

    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Symbol", style="bold cyan", width=8)
    table.add_column("Company", style="white", width=25, overflow="fold")
    table.add_column("Score", justify="center", width=10)
    table.add_column("Action", justify="left", width=10)
    table.add_column("Entry", justify="right", width=7)
    table.add_column("Target", justify="right", width=7)
    table.add_column("Stop", justify="right", width=7)
    table.add_column("Gain%", justify="right", width=6)
    table.add_column("R/R", justify="right", width=5)
    table.add_column("RSI", justify="center", width=3)
    table.add_column("Yield", justify="right", width=10)
    table.add_column("Price", justify="right", width=10)
    table.add_column("Annual Div", justify="right", width=10)
    table.add_column("Years", justify="center", width=8)
    table.add_column("Income/10K", justify="right", width=12)

    for idx, result in enumerate(results, 1):
        # Get technical signals and RSI
        technical_signals = result.get('technical_signals')
        if isinstance(technical_signals, str):
            try:
                technical_signals = json.loads(technical_signals)
            except:
                technical_signals = {}
        
        rsi = technical_signals.get('rsi') if isinstance(technical_signals, dict) else None
        
        # Get recommendation (from pre-calculated or generate from RSI)
        recommendation = result.get('_recommendation')
        if not recommendation:
            # Generate simple recommendation based on RSI
            if rsi and rsi < 30:
                recommendation = "BUY"
            elif rsi and rsi > 70:
                recommendation = "SELL"
            else:
                recommendation = "HOLD"
        
        # Get entry/target prices and trading metrics
        entry_min = result.get('entry_price_min')
        target_price = result.get('target')
        stop_loss = result.get('stop_loss')
        gain_pct = result.get('gain_percent')
        risk_reward_ratio = result.get('risk_reward_ratio')
        
        # Format R/R Ratio
        rr_formatted = "[dim]--[/dim]"
        if risk_reward_ratio is not None:
            rr_val = float(risk_reward_ratio)
            if rr_val >= 3.0:
                rr_formatted = f"[bold green]{rr_val:.1f}[/bold green]"
            elif rr_val >= 2.0:
                rr_formatted = f"[green]{rr_val:.1f}[/green]"
            elif rr_val >= 1.5:
                rr_formatted = f"[cyan]{rr_val:.1f}[/cyan]"
            elif rr_val >= 1.0:
                rr_formatted = f"[yellow]{rr_val:.1f}[/yellow]"
            else:
                rr_formatted = f"[red]{rr_val:.1f}[/red]"
        
        table.add_row(
            str(idx),
            result['symbol'],
            result.get('company_name', 'N/A')[:25],
            format_score(result['income_score'], result['category']),
            format_recommendation_clean(recommendation),
            format_price(entry_min) if entry_min else "[dim]--[/dim]",
            format_price(target_price) if target_price else "[dim]--[/dim]",
            format_price(stop_loss) if stop_loss else "[dim]--[/dim]",
            format_gain_percentage(gain_pct) if gain_pct else "[dim]--[/dim]",
            rr_formatted,
            format_rsi(rsi),
            format_percentage(result['dividend_yield']),
            format_currency(result['current_price']),
            format_currency(result['annual_dividend']),
            format_years(result['consecutive_years']),
            f"[green]{format_currency(result['annual_income_per_10k'])}[/green]"
        )

    console.print()
    console.print(table)
    console.print()

    # Summary statistics
    avg_yield = sum(r['dividend_yield'] for r in results) / len(results)
    avg_score = sum(r['income_score'] for r in results) / len(results)
    total_10k_income = sum(r['annual_income_per_10k'] for r in results[:10]) / 10  # Average of top 10

    summary = Text()
    summary.append("\n📊 Summary Statistics\n", style="bold cyan")
    summary.append(f"  • Average Yield: ", style="white")
    summary.append(f"{avg_yield * 100:.2f}%\n", style="bold green")
    summary.append(f"  • Average Income Score: ", style="white")
    summary.append(f"{avg_score:.1f}/100\n", style="bold cyan")
    summary.append(f"  • Avg Income (Top 10) per $10K: ", style="white")
    summary.append(f"${total_10k_income:.2f}/year\n", style="bold green")
    summary.append(f"  • Total Opportunities: ", style="white")
    summary.append(f"{len(results)}\n", style="bold white")

    console.print(Panel(summary, border_style="blue"))

    # Show detailed breakdown if requested
    if show_details and results:
        console.print("\n[bold cyan]📋 Detailed Analysis - Top 5 Stocks[/bold cyan]\n")

        for idx, result in enumerate(results[:5], 1):
            detail_table = Table(
                title=f"#{idx} {result['symbol']} - {result.get('company_name', 'N/A')}",
                title_style="bold cyan",
                show_header=False,
                border_style="blue",
                width=100
            )

            detail_table.add_column("Metric", style="white", width=30)
            detail_table.add_column("Value", style="cyan", width=20)
            detail_table.add_column("Score", style="green", width=15, justify="right")

            # Income score breakdown
            detail_table.add_row(
                "Income Score",
                f"{result['income_score']}/100",
                f"[bold green]{result['category']}[/bold green]"
            )
            detail_table.add_row(
                "  ├─ Yield Score (30%)",
                f"{result['yield_score']}/30",
                format_percentage(result['dividend_yield'])
            )
            detail_table.add_row(
                "  ├─ Safety Score (25%)",
                f"{result['safety_score']}/25",
                f"{result['payout_ratio'] * 100:.1f}%" if result['payout_ratio'] else "N/A"
            )
            detail_table.add_row(
                "  ├─ Consistency Score (20%)",
                f"{result['consistency_score']}/20",
                format_years(result['consecutive_years'])
            )
            detail_table.add_row(
                "  ├─ Growth Score (15%)",
                f"{result['growth_score']}/15",
                format_percentage(result['dividend_growth_3yr'] or result['dividend_growth_1yr'] or 0)
            )
            detail_table.add_row(
                "  └─ Stability Score (10%)",
                f"{result['stability_score']}/10",
                f"{result['volatility'] * 100:.1f}%" if result.get('volatility') else "N/A"
            )

            # Key metrics
            detail_table.add_section()
            detail_table.add_row(
                "Annual Dividend",
                format_currency(result['annual_dividend']),
                result.get('payout_frequency', 'N/A')
            )
            detail_table.add_row(
                "Payout Ratio",
                f"{result['payout_ratio'] * 100:.1f}%" if result['payout_ratio'] else "N/A",
                "✓ Safe" if result['payout_ratio'] and result['payout_ratio'] < 0.7 else "⚠ Watch"
            )
            detail_table.add_row(
                "P/E Ratio",
                f"{result['pe_ratio']:.1f}" if result['pe_ratio'] else "N/A",
                ""
            )

            # Income potential
            detail_table.add_section()
            detail_table.add_row(
                "[bold]Income per $10,000[/bold]",
                f"[bold green]{format_currency(result['annual_income_per_10k'])}/year[/bold green]",
                ""
            )
            detail_table.add_row(
                "[bold]Income per $100,000[/bold]",
                f"[bold green]{format_currency(result['annual_income_per_10k'] * 10)}/year[/bold green]",
                ""
            )

            console.print(detail_table)

            # Reasons and warnings
            if result.get('reasons'):
                reasons_text = Text("\n  ✓ ", style="green")
                reasons_text.append("\n  ✓ ".join(result['reasons'][:5]), style="white")
                console.print(reasons_text)

            if result.get('warnings'):
                warnings_text = Text("\n  ⚠ ", style="yellow")
                warnings_text.append("\n  ⚠ ".join(result['warnings'][:3]), style="yellow")
                console.print(warnings_text)

            console.print()

    # Investment scenario
    console.print("\n[bold cyan]💡 Investment Scenario Examples[/bold cyan]\n")

    if results:
        top_stock = results[0]

        scenario_table = Table(
            title=f"What if you invest in {top_stock['symbol']}?",
            title_style="bold cyan",
            show_header=True,
            header_style="bold white on blue",
            border_style="blue"
        )

        scenario_table.add_column("Investment Amount", style="white", width=25)
        scenario_table.add_column("Shares", justify="right", width=15)
        scenario_table.add_column("Annual Income", justify="right", width=20, style="bold green")
        scenario_table.add_column("Monthly Income", justify="right", width=20, style="green")

        amounts = [10000, 25000, 50000, 100000, 250000, 500000]
        for amount in amounts:
            shares = amount / top_stock['current_price'] if top_stock['current_price'] > 0 else 0
            annual_income = shares * top_stock['annual_dividend']
            monthly_income = annual_income / 12

            scenario_table.add_row(
                format_currency(amount),
                f"{shares:.0f}",
                format_currency(annual_income),
                format_currency(monthly_income)
            )

        console.print(scenario_table)
        console.print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Screen for dividend income stocks suitable for living off dividends"
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Number of top results to show (default: 20)"
    )
    parser.add_argument(
        "--min-yield",
        type=float,
        default=0.025,
        help="Minimum dividend yield as decimal (default: 0.025 for 2.5%%)"
    )
    parser.add_argument(
        "--min-years",
        type=int,
        default=3,
        help="Minimum consecutive years paying dividends (default: 3)"
    )
    parser.add_argument(
        "--details",
        action="store_true",
        help="Show detailed breakdown for top 5 stocks"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Minimal output"
    )

    args = parser.parse_args()

    # Configure logging
    if args.quiet:
        logging.basicConfig(level=logging.WARNING)
    else:
        logging.basicConfig(
            level=logging.INFO,
            format='%(message)s'
        )

    try:
        # Initialize screener
        db = get_db_connection()
        screener = DividendIncomeScreener(db)

        # Run scan
        results = screener.scan_all_for_income(
            min_yield=args.min_yield,
            min_consecutive_years=args.min_years,
            top_n=args.top
        )

        # Display results
        if not args.quiet:
            display_results(results, show_details=args.details)

        return 0

    except KeyboardInterrupt:
        console.print("\n[yellow]Scan interrupted by user[/yellow]")
        return 130
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        logger.exception("Unexpected error")
        return 1


if __name__ == "__main__":
    sys.exit(main())
