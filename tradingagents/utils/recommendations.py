# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Next Steps & Recommendations Helper

Provides a consistent format for displaying actionable next steps and recommendations
across all TradingAgents commands, similar to the indexes command format.

USAGE:
    from tradingagents.utils import display_next_steps
    
    # At the end of your command function:
    display_next_steps('command_name', context={'key': 'value'})

FORMAT:
    All commands should follow this structure:
    1. Main analysis/results output
    2. Next Steps & Recommendations section (this module)
    3. Commands to execute these recommendations
    4. Full guide reference

DOCUMENTATION:
    See docs/COMMAND_OUTPUT_FORMAT.md for complete implementation guide
    See docs/STRATEGY_RECOMMENDATIONS_COMMANDS.md for command reference

ADDING NEW COMMANDS:
    1. Add recommendations in _get_command_recommendations()
    2. Add command references in _display_command_references()
    3. Call display_next_steps() at end of your command function
"""

from .cli_formatter import CLIFormatter
from .screener_command_generator import (
    generate_commands_from_results,
    generate_commands_for_command,
    format_command_description
)
from .interactive_menu import show_command_menu, execute_commands
from typing import List, Dict, Any, Optional


def display_next_steps(
    command_name: str,
    recommendations: list = None,
    context: dict = None,
    results: List[Dict[str, Any]] = None,
    show_quick_actions: bool = True,
    interactive: bool = False
):
    """
    Display actionable next steps and recommendations in a consistent format.
    
    Args:
        command_name: Name of the command (e.g., 'screener', 'analyze', 'portfolio')
        recommendations: List of recommendation strings (optional)
        context: Additional context dict (optional, e.g., {'ticker': 'AAPL', 'sector': 'Technology'})
        results: Optional results list for commands that return data
        show_quick_actions: If True, show auto-generated quick action commands
        interactive: If True, show interactive menu for command selection
    """
    formatter = CLIFormatter()
    
    print(f"\n{formatter.BOLD}{formatter.BLUE}═══ NEXT STEPS & RECOMMENDATIONS ═══{formatter.NC}\n")
    
    # Get command-specific recommendations
    cmd_recs = _get_command_recommendations(command_name, context)
    
    # Merge with provided recommendations
    all_recommendations = (recommendations or []) + cmd_recs
    
    # Display recommendations
    if all_recommendations:
        for i, rec in enumerate(all_recommendations, 1):
            print(f"  {i}. {rec}")
        print()
    
    # Generate and display auto-generated quick actions (if enabled)
    if show_quick_actions:
        try:
            auto_commands = generate_commands_for_command(
                command_name=command_name,
                context=context or {},
                results=results or []
            )
            
            if auto_commands:
                display_quick_actions(
                    auto_commands,
                    format_type='section',
                    interactive=interactive
                )
        except Exception as e:
            # If auto-generation fails, fall back to static commands
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Auto-command generation failed: {e}")
    
    # Display static command references (fallback/backup)
    _display_command_references(command_name, context)
    
    # Display full guide reference
    print(f"{formatter.CYAN}📖 Full Guide:{formatter.NC} See docs/STRATEGY_RECOMMENDATIONS_COMMANDS.md for complete command reference")
    print()


def display_quick_actions(
    commands: Dict[str, List[str]],
    format_type: str = 'section',
    interactive: bool = False
) -> None:
    """
    Display auto-generated quick action commands.
    
    Args:
        commands: Dictionary mapping category names to lists of commands
        format_type: Output format - 'inline', 'section', or 'all'
        interactive: If True, show interactive menu for command selection
    """
    if not commands:
        return
    
    formatter = CLIFormatter()
    
    # Display based on format type
    if format_type in ['inline', 'all']:
        _format_inline_commands(commands, formatter)
    
    if format_type in ['section', 'all']:
        _format_section_commands(commands, formatter)
    
    # Interactive menu (if requested)
    if interactive:
        selected = show_command_menu(commands)
        if selected:
            execute_commands(selected)


def _get_command_recommendations(command_name: str, context: dict = None) -> list:
    """Get command-specific recommendations."""
    context = context or {}
    ticker = context.get('ticker', 'TICKER')
    
    recommendations_map = {
        'screener': [
            "Review top opportunities and their priority scores",
            "Check sector analysis to identify leading sectors",
            "Use 'analyze TICKER' for deep dive on top picks",
            "Monitor indicators for entry timing",
            "Set up price alerts for stocks of interest"
        ],
        'analyze': [
            f"Review technical indicators for {ticker}",
            "Check entry price recommendations and timing",
            "Consider position sizing based on confidence score",
            "Set stop-loss levels at recommended support levels",
            "Monitor for confirmation signals before entry"
        ],
        'portfolio': [
            "Review current positions and allocation",
            "Check performance metrics vs benchmarks",
            "Identify rebalancing opportunities",
            "Review upcoming dividends and income",
            "Consider tax implications of any changes"
        ],
        'performance': [
            "Compare performance to S&P 500 benchmark",
            "Identify best and worst performing positions",
            "Review win rate and average returns",
            "Consider adjusting strategy based on results",
            "Document lessons learned from trades"
        ],
        'dividends': [
            "Review upcoming dividend dates",
            "Check dividend yield and safety metrics",
            "Consider dividend reinvestment strategies",
            "Plan for tax implications of dividend income",
            "Monitor dividend sustainability"
        ],
        'evaluate': [
            "Review overall system performance",
            "Identify strengths and weaknesses",
            "Compare to market benchmarks",
            "Adjust strategy based on evaluation results",
            "Document improvements for next period"
        ],
        'digest': [
            "Review market summary and key events",
            "Check sector performance and rotation",
            "Identify market regime (bull/bear/neutral)",
            "Adjust strategy based on market conditions",
            "Monitor for breaking news and events"
        ],
        'morning': [
            "Review comprehensive market briefing",
            "Check overnight news and events",
            "Review portfolio positions and alerts",
            "Plan trading activities for the day",
            "Set up monitoring for key positions"
        ],
        'alerts': [
            "Review triggered price alerts",
            "Check if alerts match current analysis",
            "Take action on high-priority alerts",
            "Update or remove outdated alerts",
            "Set new alerts based on current analysis"
        ],
        'top': [
            "Review top opportunities and their scores",
            "Deep dive into top picks with 'analyze TICKER'",
            "Check indicators for entry timing",
            "Compare opportunities across sectors",
            "Set up monitoring for top picks"
        ],
        'stats': [
            "Review performance statistics",
            "Compare to previous periods",
            "Identify trends and patterns",
            "Adjust strategy based on statistics",
            "Set goals for next period"
        ],
        'indicators': [
            "Review all technical indicators",
            "Look for confirmation signals across indicators",
            "Check for divergences and patterns",
            "Identify support and resistance levels",
            "Use indicators to time entries and exits"
        ],
    }
    
    return recommendations_map.get(command_name, [
        "Review the analysis results",
        "Take appropriate action based on findings",
        "Monitor for changes and updates",
        "Document decisions and reasoning"
    ])


def _display_command_references(command_name: str, context: dict = None):
    """Display relevant commands to execute next steps."""
    formatter = CLIFormatter()
    context = context or {}
    ticker = context.get('ticker', 'TICKER')
    
    print(f"{formatter.CYAN}Commands to Execute These Recommendations:{formatter.NC}\n")
    
    command_map = {
        'screener': [
            ("For Deep Analysis:", [
                f"./quick_run.sh analyze {ticker}",
                "./quick_run.sh top",
                "./quick_run.sh indicators TICKER"
            ]),
            ("For Market Context:", [
                "./quick_run.sh indexes",
                "./quick_run.sh digest",
                "./quick_run.sh morning"
            ]),
            ("For Portfolio Actions:", [
                "./quick_run.sh portfolio",
                "./quick_run.sh performance",
                "./quick_run.sh alerts"
            ])
        ],
        'analyze': [
            ("For Entry Timing:", [
                f"./quick_run.sh indicators {ticker}",
                "./quick_run.sh indexes",
                "./quick_run.sh top"
            ]),
            ("For Portfolio Integration:", [
                "./quick_run.sh portfolio",
                "./quick_run.sh performance",
                "./quick_run.sh evaluate"
            ]),
            ("For Monitoring:", [
                f"./quick_run.sh alerts",
                "./quick_run.sh digest",
                "./quick_run.sh morning"
            ])
        ],
        'portfolio': [
            ("For Performance Review:", [
                "./quick_run.sh performance",
                "./quick_run.sh evaluate",
                "./quick_run.sh stats"
            ]),
            ("For Income Planning:", [
                "./quick_run.sh dividends",
                "./quick_run.sh analyze TICKER"
            ]),
            ("For Market Context:", [
                "./quick_run.sh indexes",
                "./quick_run.sh digest",
                "./quick_run.sh morning"
            ])
        ],
        'performance': [
            ("For Detailed Analysis:", [
                "./quick_run.sh evaluate",
                "./quick_run.sh stats",
                "./quick_run.sh portfolio"
            ]),
            ("For Strategy Adjustment:", [
                "./quick_run.sh screener",
                "./quick_run.sh top",
                "./quick_run.sh analyze TICKER"
            ]),
            ("For Market Context:", [
                "./quick_run.sh indexes",
                "./quick_run.sh digest"
            ])
        ],
        'dividends': [
            ("For Income Strategy:", [
                "./quick_run.sh portfolio",
                "./quick_run.sh performance",
                "./quick_run.sh analyze TICKER"
            ]),
            ("For Dividend Analysis:", [
                "./quick_run.sh screener",
                "./quick_run.sh top"
            ]),
            ("For Portfolio Review:", [
                "./quick_run.sh portfolio",
                "./quick_run.sh evaluate"
            ])
        ],
        'evaluate': [
            ("For Strategy Improvement:", [
                "./quick_run.sh screener",
                "./quick_run.sh top",
                "./quick_run.sh analyze TICKER"
            ]),
            ("For Performance Tracking:", [
                "./quick_run.sh performance",
                "./quick_run.sh stats",
                "./quick_run.sh portfolio"
            ]),
            ("For Market Analysis:", [
                "./quick_run.sh indexes",
                "./quick_run.sh digest",
                "./quick_run.sh morning"
            ])
        ],
        'digest': [
            ("For Market Analysis:", [
                "./quick_run.sh indexes",
                "./quick_run.sh screener",
                "./quick_run.sh top"
            ]),
            ("For Deep Dives:", [
                "./quick_run.sh analyze TICKER",
                "./quick_run.sh indicators TICKER"
            ]),
            ("For Portfolio Review:", [
                "./quick_run.sh portfolio",
                "./quick_run.sh performance"
            ])
        ],
        'morning': [
            ("For Trading Actions:", [
                "./quick_run.sh screener",
                "./quick_run.sh top",
                "./quick_run.sh analyze TICKER"
            ]),
            ("For Portfolio Management:", [
                "./quick_run.sh portfolio",
                "./quick_run.sh alerts",
                "./quick_run.sh dividends"
            ]),
            ("For Market Monitoring:", [
                "./quick_run.sh indexes",
                "./quick_run.sh digest"
            ])
        ],
        'alerts': [
            ("For Alert Analysis:", [
                "./quick_run.sh analyze TICKER",
                "./quick_run.sh indicators TICKER",
                "./quick_run.sh top"
            ]),
            ("For Market Context:", [
                "./quick_run.sh indexes",
                "./quick_run.sh digest",
                "./quick_run.sh screener"
            ]),
            ("For Portfolio Actions:", [
                "./quick_run.sh portfolio",
                "./quick_run.sh performance"
            ])
        ],
        'top': [
            ("For Deep Analysis:", [
                "./quick_run.sh analyze TICKER",
                "./quick_run.sh indicators TICKER"
            ]),
            ("For Market Context:", [
                "./quick_run.sh indexes",
                "./quick_run.sh screener",
                "./quick_run.sh digest"
            ]),
            ("For Portfolio Integration:", [
                "./quick_run.sh portfolio",
                "./quick_run.sh alerts"
            ])
        ],
        'stats': [
            ("For Detailed Performance:", [
                "./quick_run.sh performance",
                "./quick_run.sh evaluate",
                "./quick_run.sh portfolio"
            ]),
            ("For Strategy Analysis:", [
                "./quick_run.sh screener",
                "./quick_run.sh top",
                "./quick_run.sh analyze TICKER"
            ]),
            ("For Market Context:", [
                "./quick_run.sh indexes",
                "./quick_run.sh digest"
            ])
        ],
        'indicators': [
            ("For Entry Timing:", [
                "./quick_run.sh analyze TICKER",
                "./quick_run.sh top",
                "./quick_run.sh screener"
            ]),
            ("For Market Context:", [
                "./quick_run.sh indexes",
                "./quick_run.sh digest"
            ]),
            ("For Portfolio Actions:", [
                "./quick_run.sh portfolio",
                "./quick_run.sh alerts"
            ])
        ],
    }
    
    command_groups = command_map.get(command_name, [
        ("For Further Analysis:", [
            "./quick_run.sh screener",
            "./quick_run.sh analyze TICKER",
            "./quick_run.sh top"
        ]),
        ("For Market Context:", [
            "./quick_run.sh indexes",
            "./quick_run.sh digest",
            "./quick_run.sh morning"
        ]),
        ("For Portfolio Review:", [
            "./quick_run.sh portfolio",
            "./quick_run.sh performance",
            "./quick_run.sh evaluate"
        ])
    ])
    
    for category, commands in command_groups:
        print(f"{formatter.YELLOW}{category}{formatter.NC}")
        for cmd in commands:
            print(f"  {formatter.WHITE}{cmd}{formatter.NC}")
        print()


def display_screener_quick_actions(
    results: List[Dict[str, Any]],
    format_type: str = 'all',
    interactive: bool = False
) -> None:
    """
    Display auto-generated quick action commands based on screener results.
    
    Args:
        results: List of screener result dictionaries
        format_type: Output format - 'inline', 'section', 'all', or 'none'
        interactive: If True, show interactive menu for command selection
    """
    if not results:
        return
    
    # Generate commands from results
    commands = generate_commands_from_results(results)
    
    if not commands:
        return
    
    display_quick_actions(commands, format_type=format_type, interactive=interactive)


def _format_inline_commands(commands: Dict[str, List[str]], formatter: CLIFormatter) -> None:
    """
    Format commands as inline list (easy to copy/paste).
    
    Args:
        commands: Dictionary mapping category names to lists of commands
        formatter: CLIFormatter instance
    """
    print()
    print(f"{formatter.CYAN}💡 Quick Actions - Copy & Paste:{formatter.NC}")
    print()
    
    cmd_number = 1
    for category, cmd_list in commands.items():
        desc = format_command_description(category)
        for cmd in cmd_list:
            # Remove comments for cleaner display
            cmd_clean = cmd.split('#')[0].strip()
            print(f"  [{formatter.YELLOW}{cmd_number}{formatter.NC}] {formatter.WHITE}{desc}:{formatter.NC} {formatter.WHITE}{cmd_clean}{formatter.NC}")
            cmd_number += 1
    
    print()


def _format_section_commands(commands: Dict[str, List[str]], formatter: CLIFormatter) -> None:
    """
    Format commands in a separate section with categories.
    
    Args:
        commands: Dictionary mapping category names to lists of commands
        formatter: CLIFormatter instance
    """
    print()
    print(f"{formatter.BOLD}{formatter.BLUE}{'═' * 55}{formatter.NC}")
    print(f"{formatter.BOLD}{formatter.BLUE}🚀 QUICK ACTIONS - Based on Screener Results{formatter.NC}")
    print(f"{formatter.BOLD}{formatter.BLUE}{'═' * 55}{formatter.NC}")
    print()
    
    # Category emojis
    category_emojis = {
        'buy_signals': '📊',
        'dividend_focus': '💰',
        'top_n': '🏆',
        'sector_based': '🏭',
        'custom_filters': '🔍'
    }
    
    for category, cmd_list in commands.items():
        desc = format_command_description(category)
        emoji = category_emojis.get(category, '•')
        
        # Count stocks in category (approximate from commands)
        count_str = ""
        if cmd_list:
            # Try to extract ticker count from first command
            first_cmd = cmd_list[0]
            if 'analyze' in first_cmd or 'indicators' in first_cmd:
                tickers = first_cmd.split()[2:] if len(first_cmd.split()) > 2 else []
                # Filter out flags
                tickers = [t for t in tickers if not t.startswith('--')]
                if tickers:
                    count_str = f" ({len(tickers)} stocks)"
        
        print(f"{emoji} {formatter.BOLD}{desc}{count_str}:{formatter.NC}")
        for cmd in cmd_list:
            # Remove comments for cleaner display
            cmd_clean = cmd.split('#')[0].strip()
            print(f"  {formatter.WHITE}{cmd_clean}{formatter.NC}")
        print()
    
    print(f"{formatter.CYAN}💡 Tip: Copy any command above to execute it, or use --interactive for menu{formatter.NC}")
    print()

