# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

# Utility functions for TradingAgents

from .cli_formatter import (
    console,
    print_header,
    print_section,
    print_success,
    print_warning,
    print_error,
    print_info,
    format_recommendation,
    format_confidence,
    format_sector,
    format_money,
    format_percentage,
    print_screener_results,
    print_sector_analysis,
    print_analysis_summary,
    print_dividend_calendar,
    print_performance_metrics,
    create_progress_bar,
    print_markdown,
    print_code,
    print_rule,
    cprint,
)

from .screener_table_formatter import (
    print_screener_results_clean,
    print_screener_legend,
    print_screener_details,
)

from .help_text import (
    show_screener_legend,
    show_sector_recommendations,
    show_next_steps_menu,
    show_interpretation_tips,
    show_filtering_help,
    format_score_with_context,
)

from .recommendations import (
    display_next_steps,
    display_screener_quick_actions,
)

__all__ = [
    'console',
    'print_header',
    'print_section',
    'print_success',
    'print_warning',
    'print_error',
    'print_info',
    'format_recommendation',
    'format_confidence',
    'format_sector',
    'format_money',
    'format_percentage',
    'print_screener_results',
    'print_screener_results_clean',
    'print_screener_legend',
    'print_screener_details',
    'print_sector_analysis',
    'print_analysis_summary',
    'print_dividend_calendar',
    'print_performance_metrics',
    'create_progress_bar',
    'print_markdown',
    'print_code',
    'print_rule',
    'cprint',
    'show_screener_legend',
    'show_sector_recommendations',
    'show_next_steps_menu',
    'show_interpretation_tips',
    'show_filtering_help',
    'format_score_with_context',
    'display_next_steps',
    'display_screener_quick_actions',
]
