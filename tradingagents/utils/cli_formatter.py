"""
CLI Formatting Utilities using Rich library
Beautiful, colorful terminal output for TradingAgents
"""

from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich import box
from rich.text import Text
from rich.layout import Layout
from datetime import datetime

# Create console instance
console = Console()

# Color scheme for recommendations
RECOMMENDATION_COLORS = {
    "BUY": "green",
    "STRONG_BUY": "bright_green",
    "WAIT": "yellow",
    "HOLD": "yellow",
    "SELL": "red",
    "STRONG_SELL": "bright_red",
}

# Emoji mappings
RECOMMENDATION_EMOJI = {
    "BUY": "🟢",
    "STRONG_BUY": "🟢🟢",
    "WAIT": "🟡",
    "HOLD": "🟡",
    "SELL": "🔴",
    "STRONG_SELL": "🔴🔴",
}

SECTOR_EMOJI = {
    "Technology": "💻",
    "Healthcare": "🏥",
    "Financial Services": "🏦",
    "Consumer Cyclical": "🛒",
    "Communication": "📡",
    "Industrials": "🏭",
    "Consumer Defensive": "🍔",
    "Energy": "⚡",
    "Utilities": "💡",
    "Real Estate": "🏠",
    "Basic Materials": "⛏️",
}


def print_header(title: str, subtitle: Optional[str] = None):
    """Print a beautiful header"""
    console.print()
    if subtitle:
        header = f"[bold cyan]{title}[/bold cyan]\n[dim]{subtitle}[/dim]"
    else:
        header = f"[bold cyan]{title}[/bold cyan]"

    console.print(Panel(header, border_style="cyan", box=box.DOUBLE))
    console.print()


def print_section(title: str):
    """Print a section divider"""
    console.print(f"\n[bold]{title}[/bold]", style="cyan")
    console.print("─" * 80, style="dim")


def print_success(message: str):
    """Print success message"""
    console.print(f"✅ [green]{message}[/green]")


def print_warning(message: str):
    """Print warning message"""
    console.print(f"⚠️  [yellow]{message}[/yellow]")


def print_error(message: str):
    """Print error message"""
    console.print(f"❌ [red]{message}[/red]")


def print_info(message: str):
    """Print info message"""
    console.print(f"ℹ️  [blue]{message}[/blue]")


def format_recommendation(action: str) -> str:
    """Format recommendation with emoji and color"""
    emoji = RECOMMENDATION_EMOJI.get(action.upper(), "⚪")
    color = RECOMMENDATION_COLORS.get(action.upper(), "white")
    return f"{emoji} [{color}]{action}[/{color}]"


def format_confidence(confidence: float) -> str:
    """Format confidence score with color gradient"""
    if confidence >= 80:
        color = "bright_green"
        emoji = "🔥"
    elif confidence >= 70:
        color = "green"
        emoji = "✅"
    elif confidence >= 60:
        color = "yellow"
        emoji = "⚠️"
    else:
        color = "red"
        emoji = "⛔"

    return f"{emoji} [{color}]{confidence:.1f}%[/{color}]"


def format_sector(sector: str) -> str:
    """Format sector with emoji"""
    emoji = SECTOR_EMOJI.get(sector, "📊")
    return f"{emoji} {sector}"


def format_money(amount: float, colored: bool = True) -> str:
    """Format money with color based on positive/negative"""
    if colored:
        if amount > 0:
            return f"[green]+${amount:,.2f}[/green]"
        elif amount < 0:
            return f"[red]-${abs(amount):,.2f}[/red]"
        else:
            return f"${amount:,.2f}"
    else:
        if amount >= 0:
            return f"${amount:,.2f}"
        else:
            return f"-${abs(amount):,.2f}"


def format_percentage(pct: float, colored: bool = True) -> str:
    """Format percentage with color"""
    if colored:
        if pct > 0:
            return f"[green]+{pct:.2f}%[/green]"
        elif pct < 0:
            return f"[red]{pct:.2f}%[/red]"
        else:
            return f"{pct:.2f}%"
    else:
        if pct >= 0:
            return f"+{pct:.2f}%"
        else:
            return f"{pct:.2f}%"


def print_screener_results(results: List[Dict[str, Any]], limit: Optional[int] = None):
    """Print screener results as a beautiful table"""
    table = Table(
        title="📊 Screener Results",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )

    table.add_column("Rank", justify="center", style="dim")
    table.add_column("Symbol", justify="left", style="bold")
    table.add_column("Name", justify="left")
    table.add_column("Sector", justify="left")
    table.add_column("Priority", justify="center")
    table.add_column("Signals", justify="left")
    table.add_column("Price", justify="right")
    table.add_column("Change", justify="right")

    display_results = results[:limit] if limit else results

    for idx, result in enumerate(display_results, 1):
        # Medal emoji for top 3
        rank = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else str(idx)

        symbol = result.get('symbol', 'N/A')
        name = result.get('name', 'N/A')[:30]  # Truncate long names
        sector = format_sector(result.get('sector', 'Unknown'))
        priority = format_confidence(result.get('priority_score', 0))

        # Format signals - check both 'signals' and 'triggered_alerts'
        signals = result.get('triggered_alerts', result.get('signals', []))
        if signals:
            # Show first 3 signals for better visibility
            signal_str = ", ".join(signals[:3])
            if len(signals) > 3:
                signal_str += f" +{len(signals)-3} more"
        else:
            signal_str = "[dim]None[/dim]"

        price = f"${result.get('current_price', 0):,.2f}"
        change_pct = result.get('change_pct', 0)
        change = format_percentage(change_pct)

        table.add_row(rank, symbol, name, sector, priority, signal_str, price, change)

    console.print(table)

    if limit and len(results) > limit:
        console.print(f"\n[dim]... and {len(results) - limit} more results[/dim]")


def print_sector_analysis(sector_data: List[Dict[str, Any]]):
    """Print sector analysis with rankings"""
    print_header("🎯 Sector Analysis", f"Analyzed {len(sector_data)} sectors")

    table = Table(
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )

    table.add_column("Rank", justify="center", style="dim")
    table.add_column("Sector", justify="left")
    table.add_column("Strength", justify="center")
    table.add_column("Stocks", justify="center")
    table.add_column("Buy Signals", justify="center")
    table.add_column("Avg Priority", justify="center")
    table.add_column("Momentum", justify="left")

    for idx, sector in enumerate(sector_data, 1):
        # Medal emoji for top 3
        rank = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else str(idx)

        sector_name = format_sector(sector.get('sector', 'Unknown'))
        strength = format_confidence(sector.get('strength_score', 0))

        total_stocks = sector.get('total_stocks', 0)
        buy_signals = sector.get('buy_signals', 0)
        stocks_str = f"{buy_signals}/{total_stocks}"

        avg_priority = format_confidence(sector.get('avg_priority', 0))

        momentum = sector.get('momentum', 'Neutral')
        momentum_color = {
            'Strong': 'bright_green',
            'Moderate': 'green',
            'Neutral': 'yellow',
            'Weak': 'red'
        }.get(momentum, 'white')
        momentum_str = f"[{momentum_color}]{momentum}[/{momentum_color}]"

        table.add_row(rank, sector_name, strength, stocks_str, f"{buy_signals}", avg_priority, momentum_str)

    console.print(table)
    console.print()


def print_analysis_summary(analysis: Dict[str, Any]):
    """Print analysis summary in a beautiful panel"""
    symbol = analysis.get('symbol', 'N/A')
    recommendation = analysis.get('recommendation', 'N/A')
    confidence = analysis.get('confidence', 0)

    # Create summary content
    rec_formatted = format_recommendation(recommendation)
    conf_formatted = format_confidence(confidence)

    summary = f"""
[bold]{symbol}[/bold] - {analysis.get('company_name', 'N/A')}
Sector: {format_sector(analysis.get('sector', 'Unknown'))}

Recommendation: {rec_formatted}
Confidence: {conf_formatted}

Entry Timing: [bold]{analysis.get('entry_timing', 'N/A')}[/bold]
Investment Amount: {format_money(analysis.get('investment_amount', 0), colored=False)}
Shares: {analysis.get('shares', 0)} @ {format_money(analysis.get('current_price', 0), colored=False)}/share
    """.strip()

    # Panel color based on recommendation
    panel_color = RECOMMENDATION_COLORS.get(recommendation.upper(), "white")

    console.print(Panel(
        summary,
        title=f"[bold]Analysis Summary[/bold]",
        border_style=panel_color,
        box=box.DOUBLE,
        expand=False
    ))


def print_dividend_calendar(dividends: List[Dict[str, Any]]):
    """Print upcoming dividends calendar"""
    table = Table(
        title="📅 Upcoming Dividends",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )

    table.add_column("Symbol", justify="left", style="bold")
    table.add_column("Ex-Date", justify="center")
    table.add_column("Pay Date", justify="center")
    table.add_column("Amount", justify="right")
    table.add_column("Yield", justify="right")
    table.add_column("Confidence", justify="center")

    for div in dividends:
        symbol = div.get('symbol', 'N/A')
        ex_date = div.get('ex_date', 'N/A')
        pay_date = div.get('pay_date', 'N/A')
        amount = format_money(div.get('amount', 0), colored=False)
        yield_pct = format_percentage(div.get('yield', 0), colored=False)
        confidence = format_confidence(div.get('confidence', 0))

        table.add_row(symbol, str(ex_date), str(pay_date), amount, yield_pct, confidence)

    console.print(table)


def print_performance_metrics(metrics: Dict[str, Any]):
    """Print performance metrics"""
    print_header("📈 Performance Metrics", f"As of {datetime.now().strftime('%Y-%m-%d')}")

    table = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style="bold cyan",
        show_edge=False
    )

    table.add_column("Metric", justify="left", style="bold")
    table.add_column("Value", justify="right")
    table.add_column("Benchmark", justify="right")
    table.add_column("Alpha", justify="right")

    # Win Rate
    win_rate = metrics.get('win_rate', 0)
    table.add_row(
        "Win Rate",
        format_percentage(win_rate),
        "[dim]75% target[/dim]",
        ""
    )

    # Average Return
    avg_return = metrics.get('avg_return', 0)
    benchmark_return = metrics.get('benchmark_return', 0)
    alpha = avg_return - benchmark_return
    table.add_row(
        "Avg Return",
        format_percentage(avg_return),
        format_percentage(benchmark_return),
        format_percentage(alpha)
    )

    # Total Recommendations
    total_recs = metrics.get('total_recommendations', 0)
    winning_recs = int(total_recs * win_rate / 100)
    table.add_row(
        "Recommendations",
        f"{total_recs}",
        f"{winning_recs} wins",
        ""
    )

    console.print(table)
    console.print()


def create_progress_bar(description: str) -> Progress:
    """Create a beautiful progress bar"""
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        transient=True
    )


def print_markdown(content: str):
    """Print markdown content with rich formatting"""
    md = Markdown(content)
    console.print(md)


def print_code(code: str, language: str = "python"):
    """Print code with syntax highlighting"""
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    console.print(syntax)


def print_rule(title: str = ""):
    """Print a horizontal rule with optional title"""
    console.rule(f"[bold cyan]{title}[/bold cyan]" if title else "")


# Convenience function for quick colored prints
def cprint(text: str, color: str = "white", bold: bool = False, emoji: str = ""):
    """Quick colored print"""
    style = f"bold {color}" if bold else color
    output = f"{emoji} {text}" if emoji else text
    console.print(output, style=style)
