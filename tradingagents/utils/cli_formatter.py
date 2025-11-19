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
    # Ensure confidence is a float and handle edge cases
    try:
        confidence = float(confidence) if confidence is not None else 0.0
    except (ValueError, TypeError):
        confidence = 0.0
    
    # Clamp to valid range
    confidence = max(0.0, min(100.0, confidence))
    
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


def _generate_recommendation(rsi: Optional[float], signals: List[str], technical_signals: Optional[Dict]) -> str:
    """
    Generate trading recommendation using Phase 2-3 Pattern Recognition.

    Returns color-coded recommendation string.
    """
    if not technical_signals or not isinstance(technical_signals, dict):
        # Fallback to basic RSI if no signals
        if rsi is None:
            return "[dim]N/A[/dim]"
        if rsi < 30:
            return "[green]BUY[/green]"
        elif rsi > 70:
            return "[red]SELL[/red]"
        else:
            return "[dim]HOLD[/dim]"

    # Check for Phase 3 Multi-Timeframe Analysis (highest priority)
    mtf_signal = technical_signals.get('mtf_signal')
    mtf_confidence = technical_signals.get('mtf_confidence', 0)

    if mtf_signal and mtf_confidence > 0.8:
        # If RSI is extremely overbought (>80), modify BUY signals to indicate pullback needed
        if rsi and rsi > 80:
            if mtf_signal == 'STRONG_BUY':
                return "[yellow]⏳ WAIT (RSI >80)[/yellow]"
            elif mtf_signal == 'BUY_THE_DIP':
                return "[bold bright_green]✅ BUY DIP[/bold bright_green]"
            elif mtf_signal == 'BUY':
                return "[yellow]⏳ WAIT (RSI >80)[/yellow]"
        elif rsi and rsi > 70:
            # RSI overbought but not extreme - still show BUY DIP if applicable
            if mtf_signal == 'BUY_THE_DIP':
                return "[bold bright_green]✅ BUY DIP[/bold bright_green]"
            elif mtf_signal == 'STRONG_BUY':
                return "[yellow]⏳ WAIT (RSI >70)[/yellow]"
            elif mtf_signal == 'BUY':
                return "[yellow]⏳ WAIT (RSI >70)[/yellow]"
        
        # Normal multi-timeframe signals (RSI not overbought or extreme)
        if mtf_signal == 'STRONG_BUY':
            return "[bold bright_green]⚡ STRONG BUY[/bold bright_green]"
        elif mtf_signal == 'BUY_THE_DIP':
            return "[bold bright_green]✅ BUY DIP[/bold bright_green]"
        elif mtf_signal == 'BUY':
            return "[bold green]BUY[/bold green]"
        elif mtf_signal == 'STRONG_SELL':
            return "[bold bright_red]⚡ STRONG SELL[/bold bright_red]"
        elif mtf_signal == 'SELL_THE_RALLY':
            return "[bold bright_red]❌ SELL RALLY[/bold bright_red]"

    # Check for Phase 3 Institutional Activity
    of_signal = technical_signals.get('of_signal')
    if of_signal:
        # If RSI extremely overbought, modify BUY signals
        if rsi and rsi > 80:
            if of_signal in ['BULLISH_ACCUMULATION', 'STRONG_BUYING']:
                return "[yellow]⏳ WAIT (RSI >80)[/yellow]"
            elif of_signal == 'BEARISH_DISTRIBUTION':
                return "[bold bright_red]📉 DISTRIBUTION[/bold bright_red]"
            elif of_signal == 'STRONG_SELLING':
                return "[bold red]STRONG SELL[/bold red]"
        elif rsi and rsi > 70:
            # RSI overbought - be cautious with BUY signals
            if of_signal == 'STRONG_BUYING':
                return "[yellow]⏳ WAIT (RSI >70)[/yellow]"
            elif of_signal == 'BULLISH_ACCUMULATION':
                return "[yellow]⏳ WAIT (RSI >70)[/yellow]"
        
        # Normal institutional signals
        if of_signal == 'BULLISH_ACCUMULATION':
            return "[bold bright_green]📈 ACCUMULATION[/bold bright_green]"
        elif of_signal == 'BEARISH_DISTRIBUTION':
            return "[bold bright_red]📉 DISTRIBUTION[/bold bright_red]"
        elif of_signal == 'STRONG_BUYING':
            return "[bold green]STRONG BUY[/bold green]"
        elif of_signal == 'STRONG_SELLING':
            return "[bold red]STRONG SELL[/bold red]"

    # Check for Phase 3 Volume Profile position
    vp_position = technical_signals.get('vp_profile_position')
    vp_poc = technical_signals.get('vp_poc')
    if vp_position and vp_poc:
        if vp_position == 'BELOW_VALUE_AREA':
            return "[bold green]💎 BUY (Below VAL)[/bold green]"
        elif vp_position == 'ABOVE_VALUE_AREA':
            return "[bold red]SELL (Above VAH)[/bold red]"

    # Check for Phase 2 RSI Divergence
    bullish_div = technical_signals.get('rsi_bullish_divergence', False)
    bearish_div = technical_signals.get('rsi_bearish_divergence', False)
    div_strength = technical_signals.get('rsi_divergence_strength', 0)

    if bullish_div and div_strength > 0.7:
        return "[bold green]🔄 REVERSAL (Bullish Div)[/bold green]"
    elif bearish_div and div_strength > 0.7:
        return "[bold red]🔄 REVERSAL (Bearish Div)[/bold red]"

    # Check for Phase 2 BB Squeeze
    bb_squeeze = technical_signals.get('bb_squeeze_detected', False)
    bb_strength = technical_signals.get('bb_squeeze_strength', 0)

    if bb_squeeze and bb_strength > 0.7:
        return "[yellow]💥 BREAKOUT IMMINENT[/yellow]"

    # Fall back to Phase 1-2 basic signals
    macd_bullish = technical_signals.get('macd_bullish_crossover', False)
    macd_bearish = technical_signals.get('macd_bearish_crossover', False)
    volume_ratio = technical_signals.get('volume_ratio', 1.0)

    # Check for MACD in signal list
    if 'MACD_BULLISH_CROSS' in signals:
        macd_bullish = True
    if 'MACD_BEARISH_CROSS' in signals:
        macd_bearish = True

    # Check for other signals
    rsi_oversold = 'RSI_OVERSOLD' in signals or (rsi and rsi < 30)
    rsi_overbought = 'RSI_OVERBOUGHT' in signals or (rsi and rsi > 70)
    volume_spike = 'VOLUME_SPIKE' in signals or volume_ratio > 1.5
    bb_lower = 'BB_LOWER_TOUCH' in signals or technical_signals.get('near_bb_lower', False)
    bb_upper = 'BB_UPPER_TOUCH' in signals or technical_signals.get('near_bb_upper', False)

    # STRONG BUY: RSI oversold + MACD bullish + volume spike
    if rsi_oversold and macd_bullish and volume_spike:
        return "[bold bright_green]STRONG BUY[/bold bright_green]"

    # STRONG BUY: RSI oversold + MACD bullish
    if rsi_oversold and macd_bullish:
        return "[bold green]STRONG BUY[/bold green]"

    # STRONG BUY: RSI oversold + BB lower touch
    if rsi_oversold and bb_lower:
        return "[bold green]STRONG BUY[/bold green]"

    # BUY: RSI oversold alone (stronger signal if extremely oversold)
    if rsi_oversold:
        if rsi and rsi < 20:
            return "[bold green]STRONG BUY[/bold green]"  # Extremely oversold
        return "[green]BUY[/green]"

    # BUY: MACD bullish + RSI neutral/low
    if macd_bullish and rsi and rsi < 50:
        return "[green]BUY[/green]"

    # BUY: MACD bullish + volume spike
    if macd_bullish and volume_spike:
        return "[green]BUY[/green]"

    # STRONG SELL: RSI overbought + MACD bearish
    if rsi_overbought and macd_bearish:
        return "[bold red]STRONG SELL[/bold red]"

    # STRONG SELL: RSI overbought + BB upper touch
    if rsi_overbought and bb_upper:
        return "[bold red]STRONG SELL[/bold red]"

    # SELL: RSI overbought alone
    if rsi_overbought:
        return "[red]SELL[/red]"

    # SELL: MACD bearish + RSI high
    if macd_bearish and rsi and rsi > 50:
        return "[red]SELL[/red]"

    # WAIT: MACD bullish but RSI high (wait for pullback)
    if macd_bullish and rsi and rsi > 70:
        return "[yellow]WAIT[/yellow]"

    # WAIT: MACD bearish but RSI low (might bounce)
    if macd_bearish and rsi and rsi < 30:
        return "[yellow]WAIT[/yellow]"

    # NEUTRAL: MACD bullish or RSI in neutral range
    if macd_bullish or (rsi and rsi >= 30 and rsi <= 50):
        return "[dim]NEUTRAL[/dim]"

    # Default neutral
    return "[dim]HOLD[/dim]"


def _calculate_profit_target_price(
    entry_price: float,
    current_price: float,
    rsi: Optional[float],
    signals: List[str],
    technical_signals: Optional[Dict],
    priority_score: Optional[float] = None,
    dividend_yield: Optional[float] = None,
    profit_timeline: Optional[str] = None
) -> str:
    """
    Calculate forecasted profit target price based on entry price, timeline, and expected returns.
    
    Args:
        entry_price: Recommended entry price (use midpoint if range)
        current_price: Current stock price
        rsi: RSI indicator value
        signals: List of technical signals
        technical_signals: Technical analysis signals dict
        priority_score: Priority/confidence score
        dividend_yield: Annual dividend yield percentage
        profit_timeline: Profit timeline string (e.g., "3-6 months")
    
    Returns formatted target price string.
    """
    if entry_price <= 0 or current_price <= 0:
        return "[dim]N/A[/dim]"
    
    # Parse entry price if it's a range (e.g., "$100.00-$105.00")
    if isinstance(entry_price, str):
        # Extract numbers from string
        import re
        prices = re.findall(r'\d+\.?\d*', entry_price)
        if prices:
            entry_price = float(prices[0])  # Use first price
        else:
            entry_price = current_price
    
    # Use midpoint of entry range if we have a range
    entry_base = entry_price
    
    # Calculate expected return percentage based on priority score and signals
    confidence = priority_score or 50.0
    
    # Base expected return on confidence level
    if confidence >= 80:
        base_return_pct = 20.0  # 20% for very high confidence
    elif confidence >= 70:
        base_return_pct = 15.0  # 15% for high confidence
    elif confidence >= 60:
        base_return_pct = 12.0  # 12% for moderate-high confidence
    elif confidence >= 50:
        base_return_pct = 10.0  # 10% for moderate confidence
    else:
        base_return_pct = 8.0   # 8% for lower confidence
    
    # Adjust based on RSI
    if rsi is not None:
        if rsi < 30:  # Oversold - higher upside potential
            base_return_pct += 5.0
        elif rsi > 70:  # Overbought - lower upside potential
            base_return_pct -= 3.0
    
    # Adjust based on strong buy signals
    strong_buy_signals = ['MACD_BULLISH_CROSS', 'GOLDEN_CROSS', 'RSI_OVERSOLD', 'BREAKOUT_UP']
    has_strong_signal = any(sig in signals for sig in strong_buy_signals) if signals else False
    if has_strong_signal:
        base_return_pct += 3.0
    
    # Adjust based on profit timeline (shorter = more aggressive)
    if profit_timeline:
        if '1-3' in profit_timeline or '2-4' in profit_timeline:
            # Short timeline - more aggressive target
            base_return_pct += 2.0
        elif '9-18' in profit_timeline or '18' in profit_timeline:
            # Long timeline - more conservative
            base_return_pct -= 2.0
    
    # Check for resistance levels in technical signals
    resistance_level = None
    if technical_signals and isinstance(technical_signals, dict):
        bb_upper = technical_signals.get('bb_upper')
        ma_200 = technical_signals.get('ma_200') or technical_signals.get('ma200')
        
        # Use resistance level if available
        if bb_upper:
            resistance_level = float(bb_upper)
        elif ma_200:
            resistance_level = float(ma_200)
    
    # Calculate target price
    target_price = entry_base * (1 + base_return_pct / 100)
    
    # Add dividend contribution (prorated based on timeline)
    dividend_contribution = 0.0
    if dividend_yield and dividend_yield > 0:
        # Estimate timeline in months
        timeline_months = 6  # Default to 6 months
        if profit_timeline:
            if '1-3' in profit_timeline:
                timeline_months = 2
            elif '3-6' in profit_timeline:
                timeline_months = 4.5
            elif '6-9' in profit_timeline:
                timeline_months = 7.5
            elif '6-12' in profit_timeline:
                timeline_months = 9
            elif '9-18' in profit_timeline:
                timeline_months = 13.5
        
        # Prorate dividend yield
        dividend_contribution = (dividend_yield / 100) * (timeline_months / 12)
        target_price = target_price * (1 + dividend_contribution)
    
    # Cap target price at resistance level if it's reasonable
    if resistance_level and resistance_level > entry_base:
        # If target exceeds resistance significantly, cap it
        if target_price > resistance_level * 1.1:
            target_price = resistance_level * 1.05  # 5% above resistance
        elif target_price < resistance_level * 0.95:
            # If target is below resistance, use resistance as minimum
            target_price = max(target_price, resistance_level * 0.98)
    
    # Ensure target is above entry price
    target_price = max(target_price, entry_base * 1.05)  # At least 5% gain
    
    # Format and return
    return f"[green]${target_price:.2f}[/green]"


def _calculate_profit_timeline(
    rsi: Optional[float],
    signals: List[str],
    technical_signals: Optional[Dict],
    priority_score: Optional[float] = None,
    dividend_yield: Optional[float] = None
) -> str:
    """
    Calculate expected profit timeline based on technical indicators and confidence.
    
    Uses RSI, signals, priority score, and historical patterns to estimate
    when profits might be realized.
    
    Returns formatted timeline string (e.g., "3-6 months", "6-12 months").
    """
    # Base timeline on priority score and RSI
    confidence = priority_score or 50.0
    
    # Strong buy signals accelerate timeline
    strong_buy_signals = ['MACD_BULLISH_CROSS', 'GOLDEN_CROSS', 'RSI_OVERSOLD', 'BREAKOUT_UP']
    has_strong_signal = any(sig in signals for sig in strong_buy_signals) if signals else False
    
    # RSI-based adjustments
    if rsi is not None:
        if rsi < 30:  # Oversold - quick recovery expected
            if confidence >= 70:
                return "[green]1-3 months[/green]"
            elif confidence >= 60:
                return "[green]3-6 months[/green]"
            else:
                return "[yellow]6-9 months[/yellow]"
        elif rsi > 70:  # Overbought - may take longer
            if has_strong_signal:
                return "[yellow]6-12 months[/yellow]"
            else:
                return "[dim]9-18 months[/dim]"
    
    # Confidence-based timeline
    if confidence >= 80:
        if has_strong_signal:
            return "[green]2-4 months[/green]"
        else:
            return "[green]3-6 months[/green]"
    elif confidence >= 70:
        if has_strong_signal:
            return "[green]3-6 months[/green]"
        else:
            return "[yellow]6-9 months[/yellow]"
    elif confidence >= 60:
        return "[yellow]6-12 months[/yellow]"
    else:
        return "[dim]9-18 months[/dim]"


def _calculate_entry_price(
    current_price: float, 
    rsi: Optional[float], 
    technical_signals: Optional[Dict],
    symbol: Optional[str] = None,
    enterprise_value: Optional[float] = None,
    enterprise_to_ebitda: Optional[float] = None,
    market_cap: Optional[float] = None
) -> str:
    """
    Calculate recommended entry price based on historical analysis, forecasting, and enterprise value.
    
    Uses support levels, moving averages, RSI, Bollinger Bands, historical patterns,
    and enterprise value metrics to determine optimal entry price range.
    
    Args:
        current_price: Current stock price
        rsi: RSI indicator value
        technical_signals: Technical analysis signals dict
        symbol: Stock symbol (for fetching enterprise data if needed)
        enterprise_value: Enterprise value (if available)
        enterprise_to_ebitda: Enterprise value to EBITDA ratio (if available)
        market_cap: Market capitalization (if available)
    
    Returns formatted entry price string with enterprise value considerations.
    """
    if current_price is None or current_price <= 0:
        return "[dim]N/A[/dim]"
    
    from decimal import Decimal
    from tradingagents.portfolio.position_sizer import PositionSizer
    
    # Extract support/resistance from technical signals
    support_level = None
    ma_50 = None
    ma_200 = None
    bb_lower = None
    bb_upper = None
    
    if technical_signals and isinstance(technical_signals, dict):
        # Try to get support level (Bollinger Band lower is a good proxy)
        bb_lower = technical_signals.get('bb_lower')
        bb_upper = technical_signals.get('bb_upper')
        if bb_lower:
            support_level = float(bb_lower)
        
        # Get moving averages if available
        ma_50_val = technical_signals.get('ma_50') or technical_signals.get('ma50')
        ma_200_val = technical_signals.get('ma_200') or technical_signals.get('ma200')
        
        if ma_50_val:
            ma_50 = Decimal(str(ma_50_val))
        if ma_200_val:
            ma_200 = Decimal(str(ma_200_val))
    
    # Enterprise value analysis for entry timing
    ev_adjustment = 0.0  # Percentage adjustment based on EV metrics
    ev_reasoning = []
    
    if enterprise_value and market_cap:
        # Calculate EV/Market Cap ratio
        ev_to_mcap = enterprise_value / market_cap if market_cap > 0 else None
        if ev_to_mcap:
            # If EV < Market Cap, company may be undervalued (good entry)
            # If EV > Market Cap, company has significant debt (be cautious)
            if ev_to_mcap < 0.9:
                ev_adjustment = -0.02  # Slightly lower entry (2% discount) - undervalued
                ev_reasoning.append("EV < Market Cap suggests undervaluation")
            elif ev_to_mcap > 1.2:
                ev_adjustment = 0.03  # Wait for better entry (3% higher) - high debt
                ev_reasoning.append("High EV/Market Cap suggests significant debt")
    
    if enterprise_to_ebitda:
        # EV/EBITDA analysis
        # Lower EV/EBITDA = better value (typically < 10 is good, < 5 is excellent)
        if enterprise_to_ebitda < 5:
            ev_adjustment = min(ev_adjustment - 0.03, -0.05)  # Excellent value, lower entry target
            ev_reasoning.append(f"Excellent EV/EBITDA ({enterprise_to_ebitda:.1f})")
        elif enterprise_to_ebitda < 10:
            ev_adjustment = min(ev_adjustment - 0.01, -0.02)  # Good value
            ev_reasoning.append(f"Good EV/EBITDA ({enterprise_to_ebitda:.1f})")
        elif enterprise_to_ebitda > 20:
            ev_adjustment = max(ev_adjustment + 0.02, 0.03)  # Expensive, wait for better entry
            ev_reasoning.append(f"High EV/EBITDA ({enterprise_to_ebitda:.1f}) - wait for better entry")
    
    # Use PositionSizer to calculate entry timing
    sizer = PositionSizer(
        portfolio_value=Decimal('100000'),
        max_position_pct=Decimal('5.0'),
        risk_tolerance='moderate'
    )
    
    rsi_decimal = Decimal(str(rsi)) if rsi else None
    support_decimal = Decimal(str(support_level)) if support_level else None
    
    timing_result = sizer.calculate_entry_timing(
        current_price=Decimal(str(current_price)),
        support_level=support_decimal,
        moving_avg_50=ma_50,
        moving_avg_200=ma_200,
        rsi=rsi_decimal
    )
    
    ideal_min = timing_result.get('ideal_entry_min')
    ideal_max = timing_result.get('ideal_entry_max')
    
    if ideal_min and ideal_max:
        ideal_min_float = float(ideal_min)
        ideal_max_float = float(ideal_max)
        
        # Apply enterprise value adjustments
        if ev_adjustment != 0:
            ideal_min_float = ideal_min_float * (1 + ev_adjustment)
            ideal_max_float = ideal_max_float * (1 + ev_adjustment)
        
        # Enhanced forecasting: use Bollinger Bands for better price targets
        if bb_lower and bb_upper:
            bb_mid = (float(bb_lower) + float(bb_upper)) / 2
            # If current price is below mid-band, suggest buying near lower band
            if current_price < bb_mid:
                ideal_min_float = min(ideal_min_float, float(bb_lower) * 1.01)  # Slightly above lower band
                ideal_max_float = min(ideal_max_float, bb_mid)  # Up to mid-band
        
        # Show range if there's a meaningful range (>1% difference)
        if abs(ideal_max_float - ideal_min_float) / ideal_min_float > 0.01:
            return f"[green]${ideal_min_float:.2f}[/green]-[green]${ideal_max_float:.2f}[/green]"
        else:
            # Single price target
            return f"[green]${ideal_min_float:.2f}[/green]"
    else:
        # Fallback: calculate based on RSI and current price with forecasting
        entry_base = current_price
        
        # Apply enterprise value adjustments to base price
        if ev_adjustment != 0:
            entry_base = entry_base * (1 + ev_adjustment)
        
        if rsi and rsi < 30:
            # Oversold - buy at current or slightly below (good entry)
            # Forecast: expect bounce, so buy slightly below current
            entry = entry_base * 0.98
            return f"[green]${entry:.2f}[/green]"
        elif rsi and rsi > 70:
            # Overbought - wait for pullback (8-10% below)
            entry = entry_base * 0.92
            return f"[yellow]${entry:.2f}[/yellow]"
        else:
            # Neutral - buy within 2% of current
            entry_min = entry_base * 0.98
            entry_max = entry_base * 1.02
            return f"[dim]${entry_min:.2f}[/dim]-[dim]${entry_max:.2f}[/dim]"


def print_screener_results(results: List[Dict[str, Any]], limit: Optional[int] = None, show_buy_only: bool = False):
    """Print screener results as a beautiful table"""
    # Use terminal width with padding
    from rich.console import Console as RichConsole
    import shutil
    terminal_width = shutil.get_terminal_size().columns
    # Use full width but ensure minimum readability
    console_width = max(terminal_width - 4, 160)  # Leave some margin
    wide_console = RichConsole(width=console_width, force_terminal=True)

    table = Table(
        title="📊 Screener Results" + (" - BUY Recommendations" if show_buy_only else ""),
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        expand=True,  # Expand to use available width
        show_lines=False,  # Remove lines for cleaner look
        padding=(0, 1)  # Minimal padding
    )

    # Add columns with width constraints to prevent overlap
    table.add_column("Rank", justify="center", style="dim", width=5, no_wrap=True)
    table.add_column("Symbol", justify="left", style="bold", width=6, no_wrap=True)
    table.add_column("Name", justify="left", width=18, overflow="ellipsis")
    table.add_column("Sector", justify="left", width=12, overflow="ellipsis")
    table.add_column("Priority", justify="center", width=8, no_wrap=True)
    table.add_column("RSI", justify="center", style="dim", width=5, no_wrap=True)
    table.add_column("Signals", justify="left", width=20, overflow="ellipsis")
    table.add_column("Rec", justify="center", style="bold", width=12, overflow="ellipsis")  # Shortened header
    table.add_column("Div%", justify="center", style="dim", width=6, no_wrap=True)  # Shortened header
    table.add_column("Entry", justify="center", style="green", width=12, no_wrap=True)  # Shortened header
    table.add_column("Target", justify="center", style="bright_green", width=10, no_wrap=True)  # Shortened header
    table.add_column("Gain%", justify="center", style="bright_green", width=7, no_wrap=True)  # Shortened header
    table.add_column("Pos%", justify="center", style="cyan", width=5, no_wrap=True)  # Shortened header
    table.add_column("Timeline", justify="center", style="cyan", width=10, no_wrap=True)  # Shortened header
    table.add_column("Price", justify="right", width=10, no_wrap=True)
    table.add_column("Change", justify="right", width=8, no_wrap=True)

    # Calculate recommendations for all results and sort by recommendation strength
    results_with_recommendations = []
    for result in results:
        technical_signals = result.get('technical_signals')
        if isinstance(technical_signals, str):
            import json
            try:
                technical_signals = json.loads(technical_signals)
            except:
                technical_signals = {}
        
        rsi = technical_signals.get('rsi') if isinstance(technical_signals, dict) else None
        signals = result.get('triggered_alerts', result.get('signals', []))
        signal_list = signals if isinstance(signals, list) else []
        
        recommendation = _generate_recommendation(rsi, signal_list, technical_signals)
        
        # Calculate recommendation score for sorting (higher = better)
        rec_score = 0
        rec_upper = recommendation.upper()
        if 'STRONG BUY' in rec_upper:
            rec_score = 100
        elif 'BUY' in rec_upper:
            rec_score = 80
        elif 'NEUTRAL' in rec_upper:
            rec_score = 50
        elif 'WAIT' in rec_upper:
            rec_score = 30
        elif 'SELL' in rec_upper:
            rec_score = 10
        elif 'STRONG SELL' in rec_upper:
            rec_score = 0
        
        # Add priority score to recommendation score for better sorting
        priority_score = result.get('priority_score', 0) or 0
        combined_score = rec_score + (priority_score * 0.1)  # Weight priority score
        
        result['_recommendation'] = recommendation
        result['_rec_score'] = combined_score
        results_with_recommendations.append(result)
    
    # Sort by recommendation strength (BUY first), then by priority score
    results_with_recommendations.sort(key=lambda x: x['_rec_score'], reverse=True)
    
    # Filter for BUY recommendations if requested
    if show_buy_only:
        filtered_results = [
            r for r in results_with_recommendations
            if 'BUY' in r['_recommendation'].upper()
        ]
        display_results = filtered_results[:limit] if limit else filtered_results
    else:
        display_results = results_with_recommendations[:limit] if limit else results_with_recommendations

    for idx, result in enumerate(display_results, 1):
        # Medal emoji for top 3
        rank = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else str(idx)

        symbol = result.get('symbol', 'N/A')
        name = result.get('name', 'N/A')[:18]  # Truncate long names to fit column
        sector = format_sector(result.get('sector', 'Unknown'))
        # Remove emoji from sector for cleaner display if needed
        sector_clean = sector.replace('💻', '').replace('🏥', '').replace('🏭', '').replace('🏦', '').replace('💡', '').replace('💰', '').replace('⛏️', '').replace('🚗', '').replace('🏠', '').strip()
        if len(sector_clean) > 12:
            sector_clean = sector_clean[:10] + '..'
        sector = sector_clean
        priority = format_confidence(result.get('priority_score', 0))

        # Extract RSI and signals from technical_signals JSONB
        rsi_str = "[dim]N/A[/dim]"
        rsi_value = None
        technical_signals = result.get('technical_signals')
        if technical_signals:
            # Handle both dict and JSON string
            if isinstance(technical_signals, str):
                import json
                try:
                    technical_signals = json.loads(technical_signals)
                except:
                    technical_signals = {}
            
            if isinstance(technical_signals, dict):
                rsi = technical_signals.get('rsi')
                if rsi is not None:
                    rsi_value = float(rsi)
                    # Color code RSI: oversold (<30) = green, overbought (>70) = red, else yellow
                    if rsi_value < 30:
                        rsi_str = f"[green]{rsi_value:.1f}[/green]"
                    elif rsi_value > 70:
                        rsi_str = f"[red]{rsi_value:.1f}[/red]"
                    else:
                        rsi_str = f"[yellow]{rsi_value:.1f}[/yellow]"

        # Format signals - check both 'signals' and 'triggered_alerts'
        signals = result.get('triggered_alerts', result.get('signals', []))
        signal_list = signals if isinstance(signals, list) else []
        if signal_list:
            # Show first 2 signals (more compact)
            signal_str = ", ".join(signal_list[:2])
            if len(signal_list) > 2:
                signal_str += f" +{len(signal_list)-2}"
            # Truncate if too long
            if len(signal_str) > 20:
                signal_str = signal_str[:17] + "..."
        else:
            signal_str = "[dim]-[/dim]"

        # Use pre-calculated recommendation if available, otherwise generate
        recommendation = result.get('_recommendation') or _generate_recommendation(rsi_value, signal_list, technical_signals)

        # Get current price first (needed for dividend yield calculation)
        current_price = result.get('current_price') or result.get('price', 0)

        # Get dividend yield - try multiple sources
        dividend_yield = result.get('dividend_yield_pct') or result.get('dividend_yield')
        
        # Convert to float if it's a string or Decimal
        if dividend_yield is not None:
            try:
                dividend_yield = float(dividend_yield)
            except (ValueError, TypeError):
                dividend_yield = None
        
        # If not in cache or is 0, try to calculate from dividend_payments table
        if (not dividend_yield or dividend_yield == 0) and current_price > 0:
            symbol = result.get('symbol')
            ticker_id = result.get('ticker_id')
            
            # Method 1: Try database dividend_payments table
            if ticker_id:
                try:
                    from tradingagents.database import get_db_connection
                    db = get_db_connection()
                    
                    # Get last 4 dividends (typically quarterly, so 4 = 1 year)
                    div_query = """
                        SELECT dividend_per_share
                        FROM dividend_payments
                        WHERE ticker_id = %s
                        AND ex_dividend_date >= CURRENT_DATE - INTERVAL '2 years'
                        ORDER BY ex_dividend_date DESC
                        LIMIT 4
                    """
                    with db.get_cursor() as cursor:
                        cursor.execute(div_query, (ticker_id,))
                        dividends = cursor.fetchall()
                    
                    if dividends and len(dividends) > 0:
                        # Calculate annual dividend (sum of last 4)
                        annual_div = sum(float(d[0]) for d in dividends)
                        if annual_div > 0:
                            # Calculate yield
                            dividend_yield = (annual_div / current_price) * 100
                except Exception as e:
                    # Log but continue to try yfinance
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.debug(f"Could not get dividend from database for {symbol}: {e}")
            
            # Method 2: Try yfinance directly as fallback
            if (not dividend_yield or dividend_yield == 0) and symbol:
                try:
                    import yfinance as yf
                    ticker = yf.Ticker(symbol)
                    
                    # Try to get dividend yield from info
                    info = ticker.info
                    if info:
                        # Check multiple possible fields
                        div_yield = info.get('dividendYield') or info.get('yield') or info.get('trailingAnnualDividendYield')
                        if div_yield:
                            dividend_yield = float(div_yield) * 100  # Convert to percentage
                    
                    # If still no yield, try calculating from dividends
                    if (not dividend_yield or dividend_yield == 0):
                        dividends = ticker.dividends
                        if dividends is not None and len(dividends) > 0:
                            # Get last 4 dividends (last year typically)
                            recent_dividends = dividends.tail(4)
                            if len(recent_dividends) > 0:
                                annual_div = float(recent_dividends.sum())
                                if annual_div > 0 and current_price > 0:
                                    dividend_yield = (annual_div / current_price) * 100
                except Exception as e:
                    # Silently fail - dividend data may not be available
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.debug(f"Could not get dividend from yfinance for {symbol}: {e}")
                    pass
        
        if dividend_yield and float(dividend_yield) > 0:
            div_yield_str = f"[green]{float(dividend_yield):.2f}%[/green]"
        else:
            div_yield_str = "[dim]N/A[/dim]"

        # Calculate entry price with enterprise value considerations
        # Try to get enterprise value data from result or fetch if needed
        enterprise_value = result.get('enterprise_value') or result.get('enterpriseValue')
        enterprise_to_ebitda = result.get('enterprise_to_ebitda') or result.get('enterpriseToEbitda') or result.get('ev_to_ebitda')
        market_cap = result.get('market_cap') or result.get('marketCap')
        
        # If enterprise data not in result, try to fetch from yfinance (lazy load)
        if (not enterprise_value or not enterprise_to_ebitda) and symbol:
            try:
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                info = ticker.info
                if info:
                    if not enterprise_value:
                        enterprise_value = info.get('enterpriseValue')
                    if not enterprise_to_ebitda:
                        enterprise_to_ebitda = info.get('enterpriseToEbitda') or info.get('evToEbitda')
                    if not market_cap:
                        market_cap = info.get('marketCap')
            except Exception:
                # Silently fail - enterprise data not critical for entry price
                pass
        
        # Use stored entry prices from scan results if available (more accurate)
        entry_price_min = result.get('entry_price_min')
        entry_price_max = result.get('entry_price_max')
        
        if entry_price_min and entry_price_max:
            # Use stored entry prices from EntryPriceCalculator
            entry_min_float = float(entry_price_min)
            entry_max_float = float(entry_price_max)
            # Show range if there's a meaningful range (>1% difference)
            if abs(entry_max_float - entry_min_float) / entry_min_float > 0.01:
                # Compact format: $101.64-$109.00 -> $101-109
                entry_price_str = f"[green]${entry_min_float:.0f}[/green]-[green]${entry_max_float:.0f}[/green]"
            else:
                entry_price_str = f"[green]${entry_min_float:.0f}[/green]"
        else:
            # Fallback to calculating entry price
            entry_price_str = _calculate_entry_price(
                float(current_price), 
                rsi_value, 
                technical_signals,
                symbol=symbol,
                enterprise_value=float(enterprise_value) if enterprise_value else None,
                enterprise_to_ebitda=float(enterprise_to_ebitda) if enterprise_to_ebitda else None,
                market_cap=float(market_cap) if market_cap else None
            )
        
        # Calculate profit timeline
        priority_score = result.get('priority_score', 0)
        profit_timeline_str = _calculate_profit_timeline(
            rsi_value,
            signal_list,
            technical_signals,
            priority_score=float(priority_score) if priority_score else None,
            dividend_yield=float(dividend_yield) if dividend_yield else None
        )
        
        # Extract numeric entry price for profit target calculation
        import re
        entry_price_numeric = current_price  # Default to current price
        
        # Prefer stored entry prices (more accurate)
        if entry_price_min and entry_price_max:
            entry_price_numeric = (float(entry_price_min) + float(entry_price_max)) / 2
        elif entry_price_str and entry_price_str != "[dim]N/A[/dim]":
            # Fallback: Extract all prices from string (handles "$100.00" or "$100.00-$105.00")
            prices = re.findall(r'\d+\.?\d*', entry_price_str)
            if prices:
                if len(prices) >= 2:
                    # Range: use midpoint
                    entry_price_numeric = (float(prices[0]) + float(prices[1])) / 2
                else:
                    # Single price
                    entry_price_numeric = float(prices[0])
        
        # Calculate profit target price
        profit_target_str = _calculate_profit_target_price(
            entry_price=entry_price_numeric,
            current_price=float(current_price),
            rsi=rsi_value,
            signals=signal_list,
            technical_signals=technical_signals,
            priority_score=float(priority_score) if priority_score else None,
            dividend_yield=float(dividend_yield) if dividend_yield else None,
            profit_timeline=profit_timeline_str
        )
        
        # Make profit target more compact (remove decimals for large numbers)
        import re
        profit_target_clean = re.sub(r'\[.*?\]', '', profit_target_str)
        if profit_target_clean != "N/A":
            target_num = float(re.findall(r'\d+\.?\d*', profit_target_clean)[0])
            if target_num >= 100:
                # Format as integer for large numbers
                profit_target_str = f"[green]${target_num:.0f}[/green]"
            # Otherwise keep original format
        
        # Extract target price numeric value for profit calculation
        target_price_numeric = None
        profit_target_clean = re.sub(r'\[.*?\]', '', profit_target_str)
        if profit_target_clean != "N/A":
            target_prices = re.findall(r'\d+\.?\d*', profit_target_clean)
            if target_prices:
                target_price_numeric = float(target_prices[0])
        
        # Calculate profit percentage (gain from entry to target)
        profit_pct_str = "[dim]N/A[/dim]"
        if entry_price_numeric > 0 and target_price_numeric:
            if target_price_numeric > entry_price_numeric:
                profit_pct = ((target_price_numeric - entry_price_numeric) / entry_price_numeric) * 100
                # Color code based on gain amount
                if profit_pct >= 20:
                    profit_pct_str = f"[bright_green]{profit_pct:.1f}%[/bright_green]"
                elif profit_pct >= 15:
                    profit_pct_str = f"[green]{profit_pct:.1f}%[/green]"
                elif profit_pct >= 10:
                    profit_pct_str = f"[yellow]{profit_pct:.1f}%[/yellow]"
                else:
                    profit_pct_str = f"[dim]{profit_pct:.1f}%[/dim]"
            else:
                profit_pct_str = "[red]N/A[/red]"
        
        # Calculate position size recommendation
        position_size_str = "[dim]N/A[/dim]"
        if entry_price_numeric > 0 and priority_score:
            try:
                from decimal import Decimal
                from tradingagents.portfolio.position_sizer import PositionSizer
                
                # Use default portfolio value of $100,000 for position sizing
                portfolio_value = Decimal('100000')
                sizer = PositionSizer(
                    portfolio_value=portfolio_value,
                    max_position_pct=Decimal('10.0'),  # Max 10% per position
                    risk_tolerance='moderate'
                )
                
                # Calculate position size based on priority score (confidence)
                confidence = int(priority_score)
                # dividend_yield is already a percentage (e.g., 2.5 for 2.5%), pass directly
                div_yield_decimal = Decimal(str(dividend_yield)) if dividend_yield else None
                position_result = sizer.calculate_position_size(
                    confidence=confidence,
                    current_price=Decimal(str(entry_price_numeric)),
                    target_price=Decimal(str(target_price_numeric)) if target_price_numeric else None,
                    annual_dividend_yield=div_yield_decimal
                )
                
                position_pct = float(position_result['position_size_pct'])
                position_amount = float(position_result['recommended_amount'])
                position_shares = position_result['recommended_shares']
                
                # Format position size: show percentage and dollar amount
                if position_pct >= 7.0:
                    color = "bright_green"
                elif position_pct >= 5.0:
                    color = "green"
                elif position_pct >= 3.0:
                    color = "yellow"
                else:
                    color = "dim"
                
                # Show percentage and shares in compact format
                position_size_str = f"[{color}]{position_pct:.1f}%[/{color}]"
                # Optionally show shares: f"[{color}]{position_pct:.1f}% ({position_shares}s)[/{color}]"
                
            except Exception as e:
                # Fallback: simple calculation based on priority score
                import logging
                logger = logging.getLogger(__name__)
                logger.debug(f"Could not calculate position size for {symbol}: {e}")
                
                # Simple fallback calculation
                if priority_score >= 80:
                    position_pct = 7.5
                elif priority_score >= 70:
                    position_pct = 5.0
                elif priority_score >= 60:
                    position_pct = 3.5
                elif priority_score >= 50:
                    position_pct = 2.5
                else:
                    position_pct = 1.5
                
                if position_pct >= 7.0:
                    color = "bright_green"
                elif position_pct >= 5.0:
                    color = "green"
                elif position_pct >= 3.0:
                    color = "yellow"
                else:
                    color = "dim"
                
                position_size_str = f"[{color}]{position_pct:.1f}%[/{color}]"

        # Format price more compactly
        if current_price >= 1000:
            price = f"${current_price:,.0f}"
        else:
            price = f"${current_price:.2f}"
        
        change_pct = result.get('change_pct', 0)
        change = format_percentage(change_pct)
        
        # Strip Rich markup from profit_timeline for compact display
        timeline_clean = re.sub(r'\[.*?\]', '', profit_timeline_str)
        if len(timeline_clean) > 10:
            timeline_clean = timeline_clean[:8] + '..'
        profit_timeline_str = timeline_clean

        table.add_row(rank, symbol, name, sector, priority, rsi_str, signal_str, recommendation, div_yield_str, entry_price_str, profit_target_str, profit_pct_str, position_size_str, profit_timeline_str, price, change)

    wide_console.print(table)

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


# CLIFormatter class for backward compatibility
# Provides ANSI color codes for legacy code
class CLIFormatter:
    """Simple formatter class for ANSI color codes (backward compatibility)."""
    
    # ANSI color codes
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color (reset)
