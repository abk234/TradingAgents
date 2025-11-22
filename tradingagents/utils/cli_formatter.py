# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
CLI Formatting Utilities using Rich library
Beautiful, colorful terminal output for TradingAgents
"""

from typing import List, Dict, Any, Optional
import re
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
            # Check RSI before giving BUY signal
            if rsi and rsi > 70:
                return "[yellow]⏳ WAIT (Below VAL, RSI >70)[/yellow]"
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
    # Check for conflicting signals (BB_UPPER_TOUCH should downgrade)
    if rsi_oversold and macd_bullish and volume_spike:
        if bb_upper:  # Conflicting signal - at resistance
            return "[green]BUY[/green]"  # Downgrade from STRONG BUY
        return "[bold bright_green]STRONG BUY[/bold bright_green]"

    # STRONG BUY: RSI oversold + MACD bullish
    if rsi_oversold and macd_bullish:
        if bb_upper:  # Conflicting signal
            return "[green]BUY[/green]"  # Downgrade from STRONG BUY
        return "[bold green]STRONG BUY[/bold green]"

    # STRONG BUY: RSI oversold + BB lower touch
    if rsi_oversold and bb_lower:
        return "[bold green]STRONG BUY[/bold green]"

    # BUY: RSI oversold alone (stronger signal if extremely oversold)
    if rsi_oversold:
        if rsi and rsi < 20:
            # Extremely oversold - check for conflicting signals
            if bb_upper:  # Very rare but possible
                return "[green]BUY[/green]"  # Downgrade due to resistance
            return "[bold green]STRONG BUY[/bold green]"
        # Regular oversold - check for conflicting signals
        if bb_upper:  # RSI oversold but at upper band - contradictory
            return "[yellow]WAIT[/yellow]"  # Wait for signal clarity
        return "[green]BUY[/green]"

    # BUY: MACD bullish + RSI neutral/low
    if macd_bullish and rsi and rsi < 50:
        return "[green]BUY[/green]"

    # BUY: MACD bullish + volume spike
    if macd_bullish and volume_spike:
        return "[green]BUY[/green]"

    # WAIT: BB upper touch with neutral/high RSI (prevent false positives)
    # This prevents stocks at resistance from getting BUY signals
    if bb_upper and rsi and rsi > 50:
        return "[yellow]WAIT[/yellow]"

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
    Calculate T1 (first technical resistance) profit target price.

    Uses technical levels in priority order:
    1. VAH (Value Area High) - institutional resistance
    2. BB Upper (Bollinger Band Upper) - volatility resistance
    3. R1 (Pivot Resistance 1) - floor trader resistance
    4. Fallback: entry_price * 1.05 (minimum 5% target)

    Args:
        entry_price: Recommended entry price (use midpoint if range)
        current_price: Current stock price
        rsi: RSI indicator value
        signals: List of technical signals
        technical_signals: Technical analysis signals dict
        priority_score: Priority/confidence score (unused in T1 method)
        dividend_yield: Annual dividend yield percentage (unused in T1 method)
        profit_timeline: Profit timeline string (unused in T1 method)

    Returns formatted target price string.
    """
    if entry_price <= 0 or current_price <= 0:
        return "[dim]N/A[/dim]"

    # Parse entry price if it's a range (e.g., "$100.00-$105.00")
    if isinstance(entry_price, str):
        # Extract numbers from string
        prices = re.findall(r'\d+\.?\d*', entry_price)
        if prices:
            entry_price = float(prices[0])  # Use first price
        else:
            entry_price = current_price

    # Use midpoint of entry range if we have a range
    entry_base = entry_price

    # Extract technical levels from technical_signals
    target_price = None
    target_source = None

    if technical_signals and isinstance(technical_signals, dict):
        # Priority 1: VAH (Value Area High) - institutional resistance
        vp_vah = technical_signals.get('vp_vah')
        if vp_vah and float(vp_vah) > current_price:
            target_price = float(vp_vah)
            target_source = "VAH"

        # Priority 2: BB Upper (Bollinger Band Upper) - volatility resistance
        if not target_price:
            bb_upper = technical_signals.get('bb_upper')
            if bb_upper and float(bb_upper) > current_price:
                target_price = float(bb_upper)
                target_source = "BB Upper"

        # Priority 3: R1 (Pivot Resistance 1) - floor trader resistance
        if not target_price:
            pivot_r1 = technical_signals.get('pivot_r1')
            if pivot_r1 and float(pivot_r1) > current_price:
                target_price = float(pivot_r1)
                target_source = "R1"

    # Fallback: If no technical resistance found, use minimum 5% gain
    if not target_price:
        target_price = entry_base * 1.05
        target_source = "Min 5%"

    # Ensure target is above entry price (safety check)
    if target_price < entry_base:
        target_price = entry_base * 1.05
        target_source = "Min 5%"

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
    Calculate expected profit timeline based on multi-timeframe alignment and technical signals.

    Aligns with detailed report timeline calculation using:
    1. Multi-timeframe (MTF) alignment for trend-based timelines
    2. BB Squeeze detection for breakout setups (wait for direction)
    3. Divergence detection for reversal timelines
    4. Signal quality score for swing trade opportunities

    Returns formatted timeline string (e.g., "2-4 weeks", "5-15 days").
    """
    # Priority 1: Check for divergence signals - critical risk/opportunity indicator
    if signals:
        if 'BEARISH_RSI_DIVERGENCE' in signals or 'BEARISH_MACD_DIVERGENCE' in signals:
            # Bearish divergence - reversal pending, wait for confirmation
            return "[yellow]⚠️ Wait (divergence)[/yellow]"

        if 'BULLISH_RSI_DIVERGENCE' in signals or 'BULLISH_MACD_DIVERGENCE' in signals:
            # Bullish divergence - reversal setup
            return "[green]1-3 weeks (reversal)[/green]"

    # Priority 2: Check for BB Squeeze - wait for breakout direction
    if signals and 'BB_SQUEEZE' in signals:
        bb_squeeze = technical_signals.get('bb_squeeze_detected', False) if technical_signals else False
        squeeze_strength = technical_signals.get('bb_squeeze_strength', 0) if technical_signals else 0

        if bb_squeeze and squeeze_strength > 0.7:
            # High strength squeeze - breakout imminent, but direction unknown
            return "[yellow]⏸️ Wait (breakout pending)[/yellow]"
        elif bb_squeeze:
            # Moderate squeeze
            return "[yellow]1-2 weeks (squeeze setup)[/yellow]"

    # Priority 3: Check for multi-timeframe alignment (most accurate timing indicator)
    if technical_signals and isinstance(technical_signals, dict):
        mtf_alignment = technical_signals.get('mtf_alignment', '')

        if 'PERFECT' in mtf_alignment or 'STRONG' in mtf_alignment:
            # Strong trend alignment across all timeframes
            return "[green]2-4 weeks[/green]"

        elif 'SHORT_TERM' in mtf_alignment:
            # Only short-term momentum, not sustainable
            return "[yellow]5-15 days[/yellow]"

        elif mtf_alignment == 'RANGE_BOUND':
            # Range trading - continuous until breakout
            return "[dim]Continuous (range)[/dim]"

    # Priority 4: Use priority score as proxy for signal quality
    confidence = priority_score or 50.0

    if confidence >= 70:
        # High-quality setup with good signal score
        return "[green]1-3 weeks[/green]"
    elif confidence >= 50:
        # Moderate setup
        return "[yellow]5-10 days[/yellow]"
    else:
        # Lower quality setup
        return "[dim]5-10 days[/dim]"


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


def _calculate_opportunity_score(stock: Dict[str, Any]) -> float:
    """
    Calculate Opportunity Score - composite metric for best trading opportunities.
    
    Combines:
    - Gain potential (40% weight)
    - Entry status (25% weight)
    - RSI oversold bonus (20% weight)
    - Recommendation strength (15% weight)
    
    Returns score from 0-100 (higher = better opportunity)
    """
    score = 0.0
    
    # Extract gain percentage
    entry_price_min = stock.get('entry_price_min')
    entry_price_max = stock.get('entry_price_max')
    current_price = stock.get('current_price') or stock.get('price', 0)
    target_price = stock.get('_target_price') or stock.get('target_price') or stock.get('profit_target')
    
    gain_percent = 0.0
    if entry_price_min and entry_price_max and current_price:
        entry_mid = (float(entry_price_min) + float(entry_price_max)) / 2
        if target_price:
            gain_percent = ((float(target_price) - entry_mid) / entry_mid) * 100
        else:
            # Estimate 10% gain if no target
            gain_percent = 10.0
    
    # Gain potential (weight: 40%)
    score += min(gain_percent * 4, 40)  # Max 40 points for 10%+ gain
    
    # Entry status (weight: 25%)
    entry_status = stock.get('_entry_status', 'UNKNOWN')
    if entry_status == 'BELOW':
        score += 25  # Best - below entry zone
    elif entry_status == 'OK':
        score += 20  # Good - in entry zone
    elif entry_status == 'ABOVE':
        score += 5   # Poor - above entry
    else:
        score += 10  # Unknown - neutral
    
    # RSI oversold bonus (weight: 20%)
    technical_signals = stock.get('technical_signals', {})
    if isinstance(technical_signals, str):
        import json
        try:
            technical_signals = json.loads(technical_signals)
        except:
            technical_signals = {}
    
    rsi = technical_signals.get('rsi') if isinstance(technical_signals, dict) else None
    if rsi:
        rsi_value = float(rsi)
        if rsi_value < 30:
            score += 20  # Oversold - excellent entry
        elif rsi_value < 40:
            score += 15  # Approaching oversold
        elif rsi_value < 50:
            score += 10  # Neutral-bearish
        elif rsi_value < 60:
            score += 5   # Neutral-bullish
        # Overbought (>70) gets 0 points
    
    # Recommendation bonus (weight: 15%)
    recommendation = stock.get('_recommendation', '')
    rec_upper = recommendation.upper()
    if 'STRONG BUY' in rec_upper or 'BUY' in rec_upper and 'BELOW' in rec_upper:
        score += 15
    elif 'BUY' in rec_upper:
        score += 12
    elif 'NEUTRAL' in rec_upper:
        score += 7
    elif 'WAIT' in rec_upper:
        score += 3
    # SELL gets 0 points
    
    return min(score, 100)  # Cap at 100


def _format_signal_icons(signals: List[str]) -> str:
    """
    Format signals with icons for better visual scanning.
    
    Returns abbreviated signal string with icons.
    """
    if not signals:
        return "[dim]-[/dim]"
    
    icon_map = {
        'RSI_OVERSOLD': '🟢RSI',
        'RSI_OVERBOUGHT': '🔴RSI',
        'MACD_BULLISH': '📈MACD',
        'MACD_BEARISH': '📉MACD',
        'BB_SQUEEZE': '🔥SQZ',
        'BB_LOWER': '📉BB',
        'BB_UPPER': '📈BB',
        'DIVERGENCE': '⚠️DIV',
        'VOLUME_SPIKE': '⚡VOL',
        'MOMENTUM': '📊MOM',
    }
    
    formatted_signals = []
    for signal in signals[:3]:  # Show first 3 signals
        # Try to match signal name
        signal_upper = signal.upper()
        icon = None
        for key, icon_str in icon_map.items():
            if key in signal_upper:
                icon = icon_str
                break
        
        if icon:
            formatted_signals.append(icon)
        else:
            # Abbreviate long signal names
            abbrev = signal[:8].replace('_', '')
            formatted_signals.append(abbrev)
    
    result = ' '.join(formatted_signals)
    if len(signals) > 3:
        result += f" +{len(signals)-3}"
    
    return result


def _format_gain_percent(gain_percent: float) -> str:
    """
    Format gain percentage with color coding and visual indicators.
    
    Returns formatted string with emoji indicators.
    """
    if gain_percent >= 7:
        return f"🟢🟢 [bright_green]{gain_percent:.1f}%[/bright_green]"  # Excellent
    elif gain_percent >= 5:
        return f"🟢 [green]{gain_percent:.1f}%[/green]"  # Good
    elif gain_percent >= 3:
        return f"🟡 [yellow]{gain_percent:.1f}%[/yellow]"  # Moderate
    elif gain_percent >= 1:
        return f"🟠 [dim]{gain_percent:.1f}%[/dim]"  # Low
    else:
        return f"⚪ [dim]{gain_percent:.1f}%[/dim]"  # Minimal


def _format_entry_with_status(entry_price_min: Optional[float], entry_price_max: Optional[float], 
                              current_price: float, entry_status: str) -> str:
    """
    Format entry price with status icon in a single column.
    
    Returns formatted string like: "⬇️ $82.40" or "✅ $90.87"
    """
    if not entry_price_min or not entry_price_max:
        return "[dim]N/A[/dim]"
    
    entry_min_float = float(entry_price_min)
    entry_max_float = float(entry_price_max)
    
    # Determine status icon
    if current_price < entry_min_float:
        # Below entry (BEST - buy opportunity!)
        icon = "⬇️"
        color = "green"
        price_str = f"${entry_min_float:.2f}"
    elif entry_min_float <= current_price <= entry_max_float:
        # In entry zone (GOOD)
        icon = "✅"
        color = "green"
        price_str = f"${current_price:.2f}"
    elif current_price > entry_max_float:
        # Above entry (WAIT for pullback)
        icon = "⬆️"
        color = "yellow"
        price_str = f"${entry_max_float:.2f}"
    else:
        icon = "⚠️"
        color = "yellow"
        price_str = f"${current_price:.2f}"
    
    return f"{icon} [{color}]{price_str}[/{color}]"


def print_screener_results(results: List[Dict[str, Any]], limit: Optional[int] = None, show_buy_only: bool = False, 
                          sort_by: str = "gain", show_full_detail: bool = False):
    """
    Print screener results as a beautiful table with improved layout.
    
    Args:
        results: List of screener result dictionaries
        limit: Maximum number of results to display
        show_buy_only: If True, only show BUY recommendations
        sort_by: Sort mode - "gain" (default), "opportunity", "rsi", "priority"
        show_full_detail: If True, show both Quick Action and Full Detail tables
    """
    # Use terminal width with padding
    from rich.console import Console as RichConsole
    import shutil
    try:
        terminal_width = shutil.get_terminal_size().columns
    except (OSError, AttributeError):
        # Fallback if terminal size cannot be determined
        terminal_width = 200
    
    # Use full width but ensure minimum readability
    # Condensed table needs less width - 10 columns instead of 17
    console_width = max(terminal_width - 4, 180)  # Reduced from 230 since we have fewer columns
    wide_console = RichConsole(width=console_width, force_terminal=True)

    # Determine table title based on sort mode
    sort_title_map = {
        "gain": "Sorted by Gain%",
        "opportunity": "Sorted by Opportunity Score",
        "rsi": "Sorted by RSI (Oversold first)",
        "priority": "Sorted by Priority Score"
    }
    sort_title = sort_title_map.get(sort_by, "Sorted by Gain%")
    
    # Create condensed table (10 columns instead of 17)
    table = Table(
        title=f"📊 Screener Results - {sort_title}" + (" - BUY Recommendations" if show_buy_only else ""),
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        expand=True,
        show_lines=True,
        padding=(1, 1),  # Slightly reduced padding for more compact display
        row_styles=["", "dim"]
    )

    # Condensed column layout (10 columns)
    table.add_column("Rank", justify="center", style="dim", width=6, no_wrap=True)
    table.add_column("Symbol", justify="left", style="bold", width=8, no_wrap=True)
    table.add_column("Name", justify="left", width=24, overflow="fold")
    table.add_column("Sector", justify="left", width=16, overflow="fold")
    table.add_column("RSI", justify="center", style="dim", width=7, no_wrap=True)
    table.add_column("Signals", justify="left", width=20, overflow="fold")
    table.add_column("Rec", justify="center", style="bold", width=20, overflow="fold")
    table.add_column("Entry", justify="center", style="green", width=14, no_wrap=True)  # Merged Entry + Status
    table.add_column("Target", justify="center", style="bright_green", width=11, no_wrap=True)
    table.add_column("Gain%", justify="center", style="bright_green", width=10, no_wrap=True)  # Prominent position

    # Calculate recommendations for all results and sort by priority score
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

        priority_score = result.get('priority_score', 0) or 0
        
        # Pre-calculate gain percentage for sorting (if entry/target prices available)
        entry_price_min = result.get('entry_price_min')
        entry_price_max = result.get('entry_price_max')
        current_price = result.get('current_price') or result.get('price', 0)
        
        # Try to extract target price from profit_target if available
        target_price = result.get('target_price') or result.get('profit_target')
        if not target_price:
            # Try to calculate target price from technical signals
            profit_target_str = result.get('profit_target_str')
            if profit_target_str:
                # re is already imported at module level
                profit_target_clean = re.sub(r'\[.*?\]', '', str(profit_target_str))
                if profit_target_clean != "N/A":
                    target_prices = re.findall(r'\d+\.?\d*', profit_target_clean)
                    if target_prices:
                        target_price = float(target_prices[0])
        
        gain_pct_for_sort = 0.0
        if entry_price_min and entry_price_max and current_price:
            entry_mid = (float(entry_price_min) + float(entry_price_max)) / 2
            if target_price:
                gain_pct_for_sort = ((float(target_price) - entry_mid) / entry_mid) * 100
            else:
                # Estimate target as 10% gain (conservative estimate for sorting)
                estimated_target = entry_mid * 1.10
                if estimated_target > entry_mid:
                    gain_pct_for_sort = ((estimated_target - entry_mid) / entry_mid) * 100
        
        # Store target_price for later use
        result['_target_price'] = target_price
        
        # Check entry status for sorting priority
        entry_status_for_sort = 'UNKNOWN'
        if entry_price_min and entry_price_max and current_price:
            entry_min_float = float(entry_price_min)
            entry_max_float = float(entry_price_max)
            if current_price < entry_min_float:
                entry_status_for_sort = 'BELOW'  # Best - below entry zone
            elif entry_min_float <= current_price <= entry_max_float:
                entry_status_for_sort = 'OK'  # Good - in entry zone
            else:
                entry_status_for_sort = 'ABOVE'  # Poor - above entry

        # Calculate opportunity score
        result['_recommendation'] = recommendation
        result['_rec_score'] = rec_score
        result['_priority_score'] = priority_score
        result['_gain_pct'] = gain_pct_for_sort
        result['_entry_status'] = entry_status_for_sort
        result['_opportunity_score'] = _calculate_opportunity_score(result)
        results_with_recommendations.append(result)

    # Improved sorting based on sort_by parameter
    if sort_by == "gain":
        # Sort by Gain% (default - most useful for traders)
        results_with_recommendations.sort(key=lambda x: x['_gain_pct'], reverse=True)
    elif sort_by == "opportunity":
        # Sort by Opportunity Score (composite metric)
        results_with_recommendations.sort(key=lambda x: x['_opportunity_score'], reverse=True)
    elif sort_by == "rsi":
        # Sort by RSI (oversold first - best buy opportunities)
        def rsi_sort_key(x):
            technical_signals = x.get('technical_signals', {})
            if isinstance(technical_signals, str):
                import json
                try:
                    technical_signals = json.loads(technical_signals)
                except:
                    technical_signals = {}
            rsi = technical_signals.get('rsi') if isinstance(technical_signals, dict) else None
            return float(rsi) if rsi else 999  # Put N/A RSI at end
        results_with_recommendations.sort(key=rsi_sort_key, reverse=False)  # Lower RSI first
    elif sort_by == "priority":
        # Sort by Priority Score (original behavior)
        results_with_recommendations.sort(key=lambda x: x['_priority_score'], reverse=True)
    else:
        # Default to gain
        results_with_recommendations.sort(key=lambda x: x['_gain_pct'], reverse=True)
    
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
        name = result.get('name', 'N/A')  # No truncation - Rich will wrap if needed
        sector = format_sector(result.get('sector', 'Unknown'))
        # Remove emoji from sector for cleaner display if needed
        sector_clean = sector.replace('💻', '').replace('🏥', '').replace('🏭', '').replace('🏦', '').replace('💡', '').replace('💰', '').replace('⛏️', '').replace('🚗', '').replace('🏠', '').strip()
        # No truncation - Rich will wrap if needed
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

        # Format signals with icons - check both 'signals' and 'triggered_alerts'
        signals = result.get('triggered_alerts', result.get('signals', []))
        signal_list = signals if isinstance(signals, list) else []
        signal_str = _format_signal_icons(signal_list)

        # Use pre-calculated recommendation if available, otherwise generate
        recommendation = result.get('_recommendation') or _generate_recommendation(rsi_value, signal_list, technical_signals)
        # No truncation - Rich will wrap if needed

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

            # Round to integers for display
            entry_min_rounded = round(entry_min_float)
            entry_max_rounded = round(entry_max_float)

            # Show range only if there's a meaningful difference after rounding
            if entry_min_rounded != entry_max_rounded:
                # Compact format: $101.64-$109.00 -> $101-$109
                entry_price_str = f"[green]${entry_min_rounded}[/green]-[green]${entry_max_rounded}[/green]"
            else:
                # Same rounded value, show single price
                entry_price_str = f"[green]${entry_min_rounded}[/green]"
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

        # Format entry price with status icon (merged column)
        entry_status_str = result.get('_entry_status', 'UNKNOWN')
        entry_with_status = _format_entry_with_status(
            float(entry_price_min) if entry_price_min else None,
            float(entry_price_max) if entry_price_max else None,
            float(current_price) if current_price else 0,
            entry_status_str
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
        
        # Calculate profit percentage (gain from entry to target) with improved formatting
        profit_pct_str = "[dim]N/A[/dim]"
        if entry_price_numeric > 0 and target_price_numeric:
            if target_price_numeric > entry_price_numeric:
                profit_pct = ((target_price_numeric - entry_price_numeric) / entry_price_numeric) * 100
                profit_pct_str = _format_gain_percent(profit_pct)
            else:
                profit_pct_str = "[red]N/A[/red]"
        elif entry_price_numeric > 0:
            # Estimate gain if no target available
            estimated_gain = 10.0  # Conservative estimate
            profit_pct_str = _format_gain_percent(estimated_gain)
        
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

                # Extract volatility (ATR%) from technical signals for position sizing
                volatility_decimal = None
                if isinstance(technical_signals, dict):
                    atr_pct = technical_signals.get('atr_pct')
                    if atr_pct:
                        # Annualize ATR% (multiply by sqrt(252 trading days))
                        volatility_decimal = Decimal(str(float(atr_pct) * 15.87))  # sqrt(252) ≈ 15.87

                position_result = sizer.calculate_position_size(
                    confidence=confidence,
                    current_price=Decimal(str(entry_price_numeric)),
                    volatility=volatility_decimal,
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
        
        # Use condensed table format (10 columns)
        table.add_row(
            rank, 
            symbol, 
            name, 
            sector, 
            rsi_str, 
            signal_str, 
            recommendation, 
            entry_with_status,  # Merged Entry + Status
            profit_target_str, 
            profit_pct_str  # Gain% in prominent last position
        )

    wide_console.print(table)
    
    # Add legend for entry status icons
    console.print("\n[dim]💡 Legend:[/dim]")
    console.print("[dim]  Entry Status: ⬇️ Below Entry (Best!) | ✅ In Entry Zone | ⬆️ Above Entry (Wait) | ⚠️ Caution[/dim]")
    console.print("[dim]  Gain%: 🟢🟢 Excellent (7%+) | 🟢 Good (5-7%) | 🟡 Moderate (3-5%) | 🟠 Low (1-3%)[/dim]")
    console.print("[dim]  Signals: 🟢RSI Oversold | 📈MACD Bullish | 🔥SQZ BB Squeeze | ⚠️DIV Divergence[/dim]")

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
