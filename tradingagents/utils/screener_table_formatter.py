"""
Screener Table Formatter - Clean, Beautiful Tables

Provides clean, scannable table formatting for screener results,
matching the style of the dividend income screener.
"""

from typing import List, Dict, Any, Optional
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()


def format_price(price: float) -> str:
    """Format price with currency."""
    if price is None or price == 0:
        return "N/A"
    return f"${price:,.2f}"


def format_volume(volume: float) -> str:
    """Format volume with commas and abbreviations (M for millions, K for thousands)."""
    if volume is None or volume == 0:
        return "[dim]--[/dim]"
    
    volume = float(volume)
    
    if volume >= 1_000_000:
        # Format as millions (e.g., 1.2M)
        vol_m = volume / 1_000_000
        return f"{vol_m:.1f}M"
    elif volume >= 1_000:
        # Format as thousands (e.g., 1.2K)
        vol_k = volume / 1_000
        return f"{vol_k:.1f}K"
    else:
        # Format with commas for smaller numbers
        return f"{volume:,.0f}"


def format_score(score: int) -> str:
    """Format score with color."""
    if score is None:
        return "[dim]N/A[/dim]"

    if score >= 80:
        return f"[bold green]{score}[/bold green]"
    elif score >= 70:
        return f"[green]{score}[/green]"
    elif score >= 60:
        return f"[cyan]{score}[/cyan]"
    elif score >= 50:
        return f"[yellow]{score}[/yellow]"
    else:
        return f"[dim]{score}[/dim]"


def format_recommendation_clean(rec: str) -> str:
    """Format recommendation with color and emoji (compact version)."""
    rec_upper = rec.upper()

    if "STRONG BUY" in rec_upper or "STRONG_BUY" in rec_upper:
        return "[bold green]🟢🟢S-BUY[/bold green]"
    elif "BUY DIP" in rec_upper:
        return "[bold bright_green]✅BUY-DIP[/bold bright_green]"
    elif "BUY" in rec_upper:
        return "[green]🟢BUY[/green]"
    elif "ACCUMULATION" in rec_upper:
        return "[cyan]🔵ACCUM[/cyan]"
    elif "NEUTRAL" in rec_upper or "HOLD" in rec_upper:
        return "[dim]⚪HOLD[/dim]"
    elif "WAIT" in rec_upper:
        return "[yellow]🟡WAIT[/yellow]"
    elif "SELL RALLY" in rec_upper:
        return "[red]🔴S-RALLY[/red]"
    elif "STRONG SELL" in rec_upper or "STRONG_SELL" in rec_upper:
        return "[bold red]🔴🔴S-SELL[/bold red]"
    elif "SELL" in rec_upper:
        return "[red]🔴SELL[/red]"
    else:
        return f"[dim]{rec[:8]}[/dim]"


def format_rsi(rsi: float) -> str:
    """Format RSI with color."""
    if rsi is None:
        return "N/A"

    if rsi < 30:
        return f"[bold green]{rsi:.0f}[/bold green]"
    elif rsi < 40:
        return f"[green]{rsi:.0f}[/green]"
    elif rsi > 70:
        return f"[bold red]{rsi:.0f}[/bold red]"
    elif rsi > 60:
        return f"[red]{rsi:.0f}[/red]"
    else:
        return f"[dim]{rsi:.0f}[/dim]"


def format_gain_percentage(gain_pct: float) -> str:
    """Format gain percentage with color."""
    if gain_pct is None or gain_pct == 0:
        return "[dim]--[/dim]"

    if gain_pct >= 20:
        return f"[bold green]+{gain_pct:.1f}%[/bold green]"
    elif gain_pct >= 10:
        return f"[green]+{gain_pct:.1f}%[/green]"
    elif gain_pct >= 5:
        return f"[cyan]+{gain_pct:.1f}%[/cyan]"
    elif gain_pct > 0:
        return f"[yellow]+{gain_pct:.1f}%[/yellow]"
    else:
        return f"[red]{gain_pct:.1f}%[/red]"


def format_entry_status(current_price: float, entry_min: float, entry_max: float) -> str:
    """Format entry status indicator (compact version)."""
    if not current_price or not entry_min or not entry_max:
        return "[dim]--[/dim]"

    # Convert to float to handle Decimal types from database
    current_price = float(current_price)
    entry_min = float(entry_min)
    entry_max = float(entry_max)

    # Calculate percentage below entry_min
    if current_price < entry_min:
        pct_below = ((entry_min - current_price) / entry_min) * 100
        if pct_below <= 2:
            # Within 2% below min entry - slightly opportunistic
            return "[cyan]~BELOW[/cyan]"
        else:
            # More than 2% below - possible breakdown
            return "[yellow]⚠️LOW[/yellow]"
    elif entry_min <= current_price <= entry_max:
        # In the optimal buy zone - best entry point
        return "[bold green]✅ZONE[/bold green]"
    elif current_price <= entry_max * 1.02:
        # Slightly above zone (within 2%)
        return "[cyan]~NEAR[/cyan]"
    elif current_price <= entry_max * 1.05:
        # 2-5% above zone
        return "[yellow]⏸HIGH[/yellow]"
    else:
        # More than 5% above zone
        return "[red]🛑WAIT[/red]"


def get_recommendation_rank(recommendation: str) -> int:
    """
    Assign ranking to recommendations so BUYs appear first.
    Lower number = higher priority in display.
    """
    rec_upper = (recommendation or "").upper()
    if "STRONG BUY" in rec_upper or "STRONG_BUY" in rec_upper:
        return 1  # Highest priority
    elif "BUY DIP" in rec_upper:
        return 2
    elif "BUY" in rec_upper:
        return 3
    elif "ACCUMULATION" in rec_upper or "ACCUMULATE" in rec_upper:
        return 4
    elif "NEUTRAL" in rec_upper or "HOLD" in rec_upper:
        return 5
    elif "WAIT" in rec_upper:
        return 6
    elif "SELL RALLY" in rec_upper:
        return 7
    elif "SELL" in rec_upper and "STRONG" not in rec_upper:
        return 8
    elif "STRONG SELL" in rec_upper or "STRONG_SELL" in rec_upper:
        return 9
    else:
        return 10  # Unknown recommendations last


def print_screener_results_clean(
    results: List[Dict[str, Any]],
    limit: Optional[int] = 20,
    show_summary: bool = True
):
    """
    Print screener results in clean, scannable table format.

    Matches the style of the dividend income screener.

    Args:
        results: List of screener result dictionaries
        limit: Maximum number of results to display
        show_summary: Whether to show summary statistics
    """
    if not results:
        console.print("[yellow]No screening results available.[/yellow]")
        return

    # Sort by recommendation strength first (BUY recommendations at top), then by priority score
    results.sort(
        key=lambda x: (
            get_recommendation_rank(x.get('recommendation', x.get('_recommendation', ''))),
            -x.get('priority_score', 0)  # Negative for descending order
        )
    )

    # Limit results
    if limit:
        results = results[:limit]

    # Create main table
    table = Table(
        title="📊 Daily Screener Results - Top Investment Opportunities",
        title_style="bold cyan",
        show_header=True,
        header_style="bold white on blue",
        border_style="blue",
        show_lines=False
    )

    # Define columns - trading-focused layout
    table.add_column("#", style="dim", width=2, justify="right")
    table.add_column("Symbol", style="bold cyan", width=6)
    table.add_column("Action", justify="left", width=10)
    table.add_column("Price", justify="right", width=8)
    table.add_column("Volume", justify="right", width=8)
    table.add_column("Entry", justify="right", width=7)
    table.add_column("Target", justify="right", width=7)
    table.add_column("Stop", justify="right", width=7)
    table.add_column("Gain%", justify="right", width=6)
    table.add_column("R/R", justify="right", width=5)
    table.add_column("RSI", justify="center", width=3)

    # Process and add rows
    for idx, result in enumerate(results, 1):
        # Extract data
        symbol = result.get('symbol', 'N/A')
        company_name = result.get('company_name', result.get('name', 'N/A'))[:22]
        current_price = result.get('current_price') or result.get('price', 0)
        current_volume = result.get('current_volume') or result.get('volume', 0)
        priority_score = result.get('priority_score', 0)

        # Get technical signals
        technical_signals = result.get('technical_signals')
        if isinstance(technical_signals, str):
            try:
                technical_signals = json.loads(technical_signals)
            except:
                technical_signals = {}

        # Get RSI
        rsi = technical_signals.get('rsi') if isinstance(technical_signals, dict) else None

        # Get recommendation (from pre-calculated or generate)
        recommendation = result.get('_recommendation')
        if not recommendation:
            # Generate simple recommendation
            if rsi and rsi < 30:
                recommendation = "BUY"
            elif rsi and rsi > 70:
                recommendation = "SELL"
            else:
                recommendation = "HOLD"

        # Get entry/target prices and trading metrics
        entry_min = result.get('entry_price_min')
        entry_max = result.get('entry_price_max')
        target_price = result.get('target')  # New field from database
        stop_loss = result.get('stop_loss')  # New field from database
        gain_pct = result.get('gain_percent')  # Pre-calculated from database
        risk_reward_ratio = result.get('risk_reward_ratio')  # Pre-calculated from database

        # Use entry_min as the main entry price (most conservative entry point)
        entry_price = entry_min

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

        # Format row data - trading-focused columns
        table.add_row(
            str(idx),
            symbol,
            format_recommendation_clean(recommendation),
            format_price(current_price),
            format_volume(current_volume),
            format_price(entry_price) if entry_price else "[dim]--[/dim]",
            format_price(target_price) if target_price else "[dim]--[/dim]",
            format_price(stop_loss) if stop_loss else "[dim]--[/dim]",
            format_gain_percentage(gain_pct) if gain_pct else "[dim]--[/dim]",
            rr_formatted,
            format_rsi(rsi)
        )

    console.print()
    console.print(table)
    console.print()

    # Show summary statistics
    if show_summary and results:
        # Calculate stats
        avg_score = sum(r.get('priority_score', 0) for r in results) / len(results)

        # Count recommendations
        buy_count = sum(1 for r in results if 'BUY' in (r.get('_recommendation', '') or '').upper())

        # Calculate average potential gain
        gains = []
        for r in results:
            entry_min = r.get('entry_price_min')
            entry_max = r.get('entry_price_max')
            target = r.get('target_price') or r.get('_target_price')

            if entry_min and entry_max and target:
                entry_mid = (float(entry_min) + float(entry_max)) / 2
                gain = ((float(target) - entry_mid) / entry_mid) * 100
                gains.append(gain)

        avg_gain = sum(gains) / len(gains) if gains else 0

        summary = Text()
        summary.append("\n📊 Summary Statistics\n", style="bold cyan")
        summary.append(f"  • Total Opportunities: ", style="white")
        summary.append(f"{len(results)}\n", style="bold white")
        summary.append(f"  • Average Priority Score: ", style="white")
        summary.append(f"{avg_score:.1f}/100\n", style="bold cyan")
        summary.append(f"  • Buy Signals: ", style="white")
        summary.append(f"{buy_count}\n", style="bold green")
        if avg_gain > 0:
            summary.append(f"  • Average Potential Gain: ", style="white")
            summary.append(f"+{avg_gain:.1f}%\n", style="bold green")
        summary.append(f"  • Highest Score: ", style="white")
        summary.append(f"{results[0]['symbol']} ({results[0].get('priority_score', 0)})\n", style="bold cyan")

        console.print(Panel(summary, border_style="blue"))
        console.print()


def print_screener_details(results: List[Dict[str, Any]], top_n: int = 5):
    """
    Print detailed breakdown for top N screener results.

    Shows complete information including company names, target prices,
    entry ranges, and technical indicators.

    Args:
        results: List of screener result dictionaries
        top_n: Number of top results to show details for (default: 5)
    """
    if not results:
        return

    console.print("\n[bold cyan]📋 Detailed Analysis - Top Stocks[/bold cyan]\n")

    for idx, result in enumerate(results[:top_n], 1):
        symbol = result.get('symbol', 'N/A')
        company_name = result.get('company_name', result.get('name', 'N/A'))
        current_price = result.get('current_price') or result.get('price', 0)
        priority_score = result.get('priority_score', 0)

        # Get technical signals
        technical_signals = result.get('technical_signals')
        if isinstance(technical_signals, str):
            try:
                technical_signals = json.loads(technical_signals)
            except:
                technical_signals = {}

        # Extract technical data
        rsi = technical_signals.get('rsi') if isinstance(technical_signals, dict) else None
        macd = technical_signals.get('macd') if isinstance(technical_signals, dict) else None
        signal = technical_signals.get('signal') if isinstance(technical_signals, dict) else None

        # Get entry/target prices
        entry_min = result.get('entry_price_min')
        entry_max = result.get('entry_price_max')
        target_price = result.get('target_price') or result.get('_target_price')

        # Get recommendation
        recommendation = result.get('_recommendation', 'HOLD')

        # Create detail table
        detail_table = Table(
            title=f"#{idx} {symbol} - {company_name}",
            title_style="bold cyan",
            show_header=False,
            border_style="blue",
            width=80
        )

        detail_table.add_column("Metric", style="white", width=25)
        detail_table.add_column("Value", style="cyan", width=25)
        detail_table.add_column("Info", style="dim", width=25)

        # Priority Score
        detail_table.add_row(
            "Priority Score",
            format_score(priority_score),
            "Overall ranking score"
        )

        # Pricing Information
        detail_table.add_section()
        detail_table.add_row(
            "Current Price",
            format_price(current_price),
            ""
        )
        detail_table.add_row(
            "Entry Range",
            f"{format_price(entry_min)} - {format_price(entry_max)}" if entry_min and entry_max else "[dim]N/A[/dim]",
            "Optimal buy zone"
        )
        detail_table.add_row(
            "  └─ Min Entry",
            format_price(entry_min) if entry_min else "[dim]N/A[/dim]",
            "[bold green]← Lowest entry price[/bold green]"
        )
        detail_table.add_row(
            "  └─ Max Entry",
            format_price(entry_max) if entry_max else "[dim]N/A[/dim]",
            "Upper bound of zone"
        )
        detail_table.add_row(
            "Target Price",
            format_price(target_price) if target_price else "[dim]N/A[/dim]",
            "Technical price target"
        )

        # Calculate gains
        if entry_min and target_price:
            gain_from_min = ((float(target_price) - float(entry_min)) / float(entry_min)) * 100
            detail_table.add_row(
                "Potential Gain",
                format_gain_percentage(gain_from_min),
                "From min entry to target"
            )

        # Technical Indicators
        detail_table.add_section()
        detail_table.add_row(
            "Recommendation",
            format_recommendation_clean(recommendation),
            ""
        )
        detail_table.add_row(
            "RSI",
            format_rsi(rsi) if rsi else "[dim]N/A[/dim]",
            "<30 oversold, >70 overbought"
        )
        if macd is not None and signal is not None:
            macd_diff = macd - signal
            macd_status = "[green]Bullish[/green]" if macd_diff > 0 else "[red]Bearish[/red]"
            detail_table.add_row(
                "MACD Signal",
                macd_status,
                f"Diff: {macd_diff:.2f}"
            )

        # Entry Status
        if entry_min and entry_max:
            status = format_entry_status(current_price, entry_min, entry_max)
            detail_table.add_row(
                "Entry Status",
                status,
                format_entry_status(current_price, entry_min, entry_max)
            )

        console.print(detail_table)
        console.print()


def print_screener_legend():
    """Print legend explaining the columns."""
    legend = Text()
    legend.append("\n📖 Column Legend\n", style="bold cyan")
    legend.append("  • ", style="white")
    legend.append("Action", style="bold")
    legend.append(": Trading recommendation (BUY, SELL, HOLD, WAIT)\n", style="white")
    legend.append("  • ", style="white")
    legend.append("Entry", style="bold")
    legend.append(": Recommended entry price (most conservative buy point)\n", style="white")
    legend.append("  • ", style="white")
    legend.append("Target", style="bold")
    legend.append(": Price target based on resistance levels\n", style="white")
    legend.append("  • ", style="white")
    legend.append("Stop", style="bold")
    legend.append(": Stop loss price (2% below support)\n", style="white")
    legend.append("  • ", style="white")
    legend.append("Gain%", style="bold")
    legend.append(": Expected gain from entry to target\n", style="white")
    legend.append("  • ", style="white")
    legend.append("R/R", style="bold")
    legend.append(": Risk/Reward ratio (", style="white")
    legend.append(">3.0 excellent", style="bold green")
    legend.append(", ", style="white")
    legend.append(">2.0 good", style="green")
    legend.append(", ", style="white")
    legend.append("<1.0 poor", style="red")
    legend.append(")\n", style="white")
    legend.append("  • ", style="white")
    legend.append("RSI", style="bold")
    legend.append(": Relative Strength Index (", style="white")
    legend.append("<30 oversold", style="green")
    legend.append(", ", style="white")
    legend.append(">70 overbought", style="red")
    legend.append(")\n", style="white")

    console.print(Panel(legend, title="[bold]Understanding the Results[/bold]", border_style="cyan"))
    console.print()
