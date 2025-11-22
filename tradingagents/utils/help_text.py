# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Help text and legends for TradingAgents output
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()


def show_screener_legend():
    """Display legend explaining screener metrics"""
    console.print("\n")

    # Create legend table
    table = Table(
        title="📖 Screener Metrics Guide",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )

    table.add_column("Metric", style="bold")
    table.add_column("Range", justify="center")
    table.add_column("Interpretation", style="dim")

    table.add_row(
        "Priority Score",
        "0-100",
        "🟢 >50: Strong buy candidate\n🟡 30-50: Worth investigating\n🔴 <30: Weak signal"
    )

    table.add_row(
        "Sector Strength",
        "0-100%",
        "🟢 >40%: Strong sector\n🟡 20-40%: Neutral\n🔴 <20%: Weak sector"
    )

    table.add_row(
        "Buy Signals",
        "Count",
        "Bullish technical signals detected:\n• MACD Bullish Cross\n• RSI Oversold\n• Volume Spike\n• Bollinger Band Touch"
    )

    table.add_row(
        "Momentum",
        "Category",
        "🔥 Strong: Uptrend + volume\n⚪ Neutral: Sideways\n📉 Weak: Downtrend"
    )

    table.add_row(
        "Change %",
        "Percentage",
        "🟢 Positive: Price up\n🔴 Negative: Price down"
    )

    console.print(table)

    # Add recommendation
    console.print("\n")
    rec_panel = Panel(
        "[bold cyan]💡 Recommended Strategy:[/bold cyan]\n\n"
        "1. [green]Start with sectors showing >30% strength[/green]\n"
        "2. [green]Focus on stocks with priority score >40[/green]\n"
        "3. [green]Look for stocks with buy signals[/green]\n"
        "4. [green]Check momentum is not 'Weak'[/green]\n"
        "5. [green]Analyze top 3-5 candidates with AI[/green]",
        title="Strategy",
        border_style="cyan"
    )
    console.print(rec_panel)


def show_sector_recommendations(sector_results):
    """Show actionable recommendations based on sector analysis"""
    console.print("\n")

    # Find top sectors
    top_sectors = [s for s in sector_results if s.get('strength_score', 0) > 30][:3]

    if not top_sectors:
        console.print("[yellow]⚠️  All sectors showing weak signals. Consider waiting for better opportunities.[/yellow]\n")
        return

    # Create recommendations panel
    recs = []
    recs.append("[bold cyan]🎯 Recommended Next Steps:[/bold cyan]\n")

    for i, sector in enumerate(top_sectors, 1):
        sector_name = sector['sector']
        strength = sector['strength_score']

        recs.append(
            f"{i}. [green]Analyze {sector_name}[/green] "
            f"(Strength: {strength:.1f}/100)"
        )

    recs.append("\n[bold]Quick Commands:[/bold]")
    recs.append("• [cyan]venv/bin/python -m tradingagents.screener top 10[/cyan] - View top stocks")

    if top_sectors:
        top_sector = top_sectors[0]['sector']
        recs.append(f"• [cyan]venv/bin/python -m tradingagents.analyze TICKER --plain-english[/cyan] - Deep dive")

    recs.append("• [cyan]./quick_run.sh analyze TICKER[/cyan] - Quick analysis")

    panel = Panel(
        "\n".join(recs),
        title="📊 Analysis Summary",
        border_style="green"
    )
    console.print(panel)


def show_next_steps_menu():
    """Show interactive next steps menu"""
    console.print("\n")

    menu = Panel(
        "[bold cyan]What would you like to do next?[/bold cyan]\n\n"
        "[green]1)[/green] View top 10 stocks across all sectors\n"
        "[green]2)[/green] Analyze stocks from a specific sector\n"
        "[green]3)[/green] Get AI recommendations for top picks\n"
        "[green]4)[/green] View detailed sector breakdown\n"
        "[green]5)[/green] Export results to file\n"
        "[green]6)[/green] Show metric explanations (legend)\n"
        "[yellow]0)[/yellow] Return to main menu",
        title="Next Steps",
        border_style="cyan"
    )
    console.print(menu)


def format_score_with_context(score: float, metric_type: str = "priority") -> str:
    """
    Format a score with color-coded context

    Args:
        score: The score value
        metric_type: Type of metric (priority, strength, momentum)

    Returns:
        Formatted string with color and interpretation
    """
    if metric_type == "priority":
        if score >= 50:
            return f"[bold green]{score:.0f}[/bold green] 🔥 Strong"
        elif score >= 40:
            return f"[green]{score:.0f}[/green] ✅ Good"
        elif score >= 30:
            return f"[yellow]{score:.0f}[/yellow] ⚠️  Fair"
        else:
            return f"[red]{score:.0f}[/red] ⛔ Weak"

    elif metric_type == "strength":
        if score >= 40:
            return f"[bold green]{score:.1f}%[/bold green] 💪"
        elif score >= 20:
            return f"[yellow]{score:.1f}%[/yellow] ➖"
        else:
            return f"[red]{score:.1f}%[/red] 📉"

    return f"{score:.1f}"


def show_interpretation_tips():
    """Show tips for interpreting results"""
    tips = Panel(
        "[bold cyan]💡 Interpretation Tips:[/bold cyan]\n\n"
        "🎯 [bold]Priority Score:[/bold]\n"
        "   Combines technical indicators (MACD, RSI, Bollinger Bands, Volume)\n"
        "   Higher score = more bullish technical signals\n\n"
        "📊 [bold]Sector Strength:[/bold]\n"
        "   Average performance of all stocks in that sector\n"
        "   Look for sectors >30% for best opportunities\n\n"
        "🚀 [bold]Buy Signals:[/bold]\n"
        "   Number of stocks showing specific bullish patterns\n"
        "   0 signals = No strong technicals currently\n\n"
        "💨 [bold]Momentum:[/bold]\n"
        "   Recent price trend and volume analysis\n"
        "   Prefer 'Strong' or 'Neutral' over 'Weak'\n\n"
        "[yellow]⚠️  Remember:[/yellow] These are technical signals only.\n"
        "Always do fundamental research before investing!",
        title="How to Read Results",
        border_style="blue"
    )
    console.print(tips)


def show_filtering_help():
    """Show help for filtering and sorting results"""
    help_text = Panel(
        "[bold cyan]🔍 Filtering Options:[/bold cyan]\n\n"
        "[green]By Sector:[/green]\n"
        "  --sector Healthcare    Filter to specific sector\n\n"
        "[green]By Score:[/green]\n"
        "  --min-score 40        Show only stocks with score ≥40\n\n"
        "[green]By Signals:[/green]\n"
        "  --with-signals        Show only stocks with buy signals\n\n"
        "[green]Top Results:[/green]\n"
        "  --top 10              Limit to top N results\n\n"
        "[yellow]Examples:[/yellow]\n"
        "  [dim]venv/bin/python -m tradingagents.screener run --top 5[/dim]\n"
        "  [dim]venv/bin/python -m tradingagents.screener run --min-score 40[/dim]",
        title="Filtering Guide",
        border_style="cyan"
    )
    console.print(help_text)
