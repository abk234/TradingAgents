#!/usr/bin/env python3
"""
Daily Screener CLI

Command-line interface for the daily screening system.

Usage:
    python -m tradingagents.screener run                    # Run daily screener
    python -m tradingagents.screener run --sector-analysis  # Run with sector analysis
    python -m tradingagents.screener report                 # Show latest report
    python -m tradingagents.screener top [N]                # Show top N opportunities
    python -m tradingagents.screener update                 # Update price data only
"""

import sys
import argparse
import os
from datetime import date
import logging

from .screener import DailyScreener
from .sector_analyzer import SectorAnalyzer
from tradingagents.database import DatabaseConnection
from tradingagents.utils import (
    print_header,
    print_section,
    print_screener_results,
    print_sector_analysis,
    print_success,
    print_warning,
    print_info,
    create_progress_bar,
    show_screener_legend,
    show_sector_recommendations,
    show_interpretation_tips,
    display_next_steps
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def cmd_run(args):
    """Run the daily screener."""
    screener = DailyScreener()

    # Check if rich formatting is enabled
    use_rich = os.getenv('ENABLE_RICH_OUTPUT', 'true').lower() == 'true'

    # Run scan
    results = screener.scan_all(
        update_prices=not args.no_update,
        store_results=not args.no_store
    )

    # Sector Analysis (if enabled)
    sector_results = None
    if args.sector_analysis and results:
        db_conn = DatabaseConnection()
        sector_analyzer = SectorAnalyzer(db_conn)

        if use_rich:
            print_section("Analyzing Sectors")
        else:
            print("\n" + "="*70)
            print("SECTOR ANALYSIS")
            print("="*70)

        # Analyze all sectors
        sector_results = sector_analyzer.analyze_all_sectors()

        if sector_results:
            if use_rich:
                print_sector_analysis(sector_results)
                # Show recommendations after sector analysis
                show_sector_recommendations(sector_results)
            else:
                # Traditional text output
                for i, sector in enumerate(sector_results[:5], 1):
                    emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                    print(f"{emoji} {sector['sector']:25s}: {sector['strength_score']:5.1f}/100")
                    print(f"   {sector['buy_signals']}/{sector['total_stocks']} buy signals, momentum: {sector['momentum']}")

            # If sector-first analysis, get stocks from top sectors
            if args.with_analysis and args.sector_first:
                top_n_sectors = args.top_sectors or 2
                stocks_per_sector = args.stocks_per_sector or 3

                if use_rich:
                    print_info(f"Focusing on top {top_n_sectors} sectors, {stocks_per_sector} stocks per sector")
                else:
                    print(f"\n🎯 Focusing on top {top_n_sectors} sectors ({stocks_per_sector} stocks each)")

                # Get stocks from top sectors
                sector_stocks = sector_analyzer.get_stocks_from_top_sectors(
                    top_n_sectors=top_n_sectors,
                    stocks_per_sector=stocks_per_sector
                )

                # Filter results to only include stocks from top sectors
                sector_symbols = {stock[0] for stock in sector_stocks}
                results = [r for r in results if r['symbol'] in sector_symbols]

                if use_rich:
                    print_success(f"Selected {len(results)} stocks from top sectors for analysis")
                else:
                    print(f"✅ Selected {len(results)} stocks from top sectors")

    # Show report
    if results and not args.quiet:
        if use_rich:
            # Use rich formatted output
            print_header("Daily Screener Results", f"{len(results)} stocks analyzed")
            # Check if user wants BUY recommendations only
            show_buy_only = getattr(args, 'buy_only', False)
            sort_by = getattr(args, 'sort_by', 'gain')
            print_screener_results(results, limit=args.top, show_buy_only=show_buy_only, sort_by=sort_by)
        else:
            # Use traditional text output
            print("\n")
            report = screener.generate_report(results, top_n=args.top)
            print(report)

        # Run AI analysis if requested
        if args.with_analysis:
            analysis_limit = args.analysis_limit or args.top

            print("\n" + "="*70)
            print("AI INVESTMENT RECOMMENDATIONS")
            print("="*70)
            print(f"Analyzing top {analysis_limit} stocks with AI...")
            print(f"Portfolio value: ${args.portfolio_value:,.0f}")
            print("="*70 + "\n")

            # Initialize analyzer
            try:
                from tradingagents.analyze import DeepAnalyzer
                from datetime import date

                # Choose configuration based on --fast flag
                if args.fast:
                    from tradingagents.fast_config import FAST_CONFIG
                    config = FAST_CONFIG
                    print("🚀 Fast mode enabled - skipping news, using optimized settings")
                else:
                    from tradingagents.default_config import DEFAULT_CONFIG
                    config = DEFAULT_CONFIG

                # Enable/disable RAG based on --no-rag flag
                enable_rag = not args.no_rag
                if args.no_rag:
                    print("⚡ RAG disabled for faster analysis")

                analyzer = DeepAnalyzer(
                    config=config,
                    enable_rag=enable_rag,
                    debug=False
                )

                # Analyze top N stocks
                for i, result in enumerate(results[:analysis_limit], 1):
                    symbol = result['symbol']
                    score = result['priority_score']

                    print(f"\n{'='*70}")
                    print(f"[{i}/{analysis_limit}] Analyzing {symbol} (Priority Score: {score})")
                    print("="*70 + "\n")

                    try:
                        # Run analysis
                        analysis_results = analyzer.analyze(
                            ticker=symbol,
                            analysis_date=date.today(),
                            store_results=not args.no_store
                        )

                        # Print results in plain English
                        analyzer.print_results(
                            analysis_results,
                            verbose=False,
                            plain_english=True,
                            portfolio_value=args.portfolio_value
                        )

                    except Exception as e:
                        logger.error(f"Error analyzing {symbol}: {e}")
                        print(f"⚠️  Failed to analyze {symbol}: {e}\n")
                        continue

                # Cleanup
                analyzer.close()

                print("\n" + "="*70)
                print("AI ANALYSIS COMPLETE")
                print("="*70 + "\n")

            except Exception as e:
                logger.error(f"Failed to initialize AI analyzer: {e}")
                print(f"\n⚠️  Could not run AI analysis: {e}\n")
                print("Tip: Make sure you have the analyze module properly configured.\n")

    # Display next steps and recommendations
    display_next_steps('screener', context={'results_count': len(results) if results else 0})

    return 0


def cmd_report(args):
    """Show the latest report."""
    screener = DailyScreener()

    scan_date = date.fromisoformat(args.date) if args.date else None
    report = screener.generate_report(scan_date=scan_date, top_n=args.top)

    print(report)
    return 0


def cmd_top(args):
    """Show top opportunities."""
    screener = DailyScreener()

    # Refresh scan if requested
    if args.refresh:
        print("Running fresh screener scan...")
        screener.scan_all(update_prices=True, store_results=True)
        print("✓ Scan complete\n")

    # Determine requested date
    requested_date = date.fromisoformat(args.date) if args.date else date.today()
    # Pass None to let get_top_opportunities use its fallback logic when no date specified
    scan_date_arg = date.fromisoformat(args.date) if args.date else None
    opportunities = screener.get_top_opportunities(limit=args.limit, scan_date=scan_date_arg)

    if not opportunities:
        # Check if there are any scans at all
        latest_scan_date = screener.scan_ops.get_latest_scan_date()
        if latest_scan_date:
            print(f"No opportunities found for the requested date ({requested_date}).")
            print(f"Latest scan date in database: {latest_scan_date}")
            if latest_scan_date != requested_date:
                print(f"\nTip: Use --date {latest_scan_date} to see opportunities from the latest scan")
            print(f"Or run a new scan with: python -m tradingagents.screener run")
        else:
            print("No opportunities found. No scans exist in the database.")
            print(f"\nTip: Run the screener first with: python -m tradingagents.screener run")
        return 1

    # Determine which scan date was actually used
    actual_scan_date = opportunities[0].get('scan_date') if opportunities else None
    
    print("="*70)
    print(f"TOP {len(opportunities)} OPPORTUNITIES")
    if actual_scan_date:
        if actual_scan_date != requested_date:
            print(f"(from scan date: {actual_scan_date} - fallback from requested {requested_date})")
        else:
            print(f"(from scan date: {actual_scan_date})")
    print("="*70)
    print()

    for i, opp in enumerate(opportunities, 1):
        symbol = opp.get('symbol', 'N/A')
        score = opp.get('priority_score', 0)
        price = opp.get('price', 0)
        alerts = opp.get('triggered_alerts', [])

        print(f"{i}. {symbol:6s} - Score: {score:3d} - Price: ${price:7.2f}")

        if alerts:
            print(f"   Alerts: {', '.join(alerts)}")

        print()

    # Display next steps and recommendations
    display_next_steps('top', context={'limit': args.limit})

    return 0


def cmd_update(args):
    """Update price data for all tickers."""
    from .data_fetcher import DataFetcher

    fetcher = DataFetcher()

    print("Updating price data for all tickers...")
    stats = fetcher.update_all_tickers(incremental=not args.full)

    print("\n" + "="*70)
    print("Price Update Complete")
    print("="*70)
    print(f"Successful: {stats['successful']}/{stats['total']}")
    print(f"Failed: {stats['failed']}")
    print(f"Records added: {stats['records_added']}")

    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Investment Intelligence System - Daily Screener',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Run command
    run_parser = subparsers.add_parser('run', help='Run daily screener')
    run_parser.add_argument(
        '--no-update',
        action='store_true',
        help='Skip price data update'
    )
    run_parser.add_argument(
        '--no-store',
        action='store_true',
        help='Do not store results in database'
    )
    run_parser.add_argument(
        '--top',
        type=int,
        default=20,
        help='Number of top opportunities to show (default: 20, use --buy-only to see top BUY recommendations)'
    )
    run_parser.add_argument(
        '--quiet',
        action='store_true',
        help='Do not print report'
    )
    run_parser.add_argument(
        '--with-analysis',
        action='store_true',
        help='Include AI investment recommendations (slower but more insightful)'
    )
    run_parser.add_argument(
        '--analysis-limit',
        type=int,
        help='Number of stocks to analyze (default: same as --top)'
    )
    run_parser.add_argument(
        '--portfolio-value',
        type=float,
        default=100000,
        help='Portfolio value for position sizing recommendations (default: 100000)'
    )
    run_parser.add_argument(
        '--fast',
        action='store_true',
        help='Fast mode: skips news, uses cached data, optimized for speed'
    )
    run_parser.add_argument(
        '--no-rag',
        action='store_true',
        help='Disable RAG (historical context) for faster analysis'
    )
    run_parser.add_argument(
        '--sector-analysis',
        action='store_true',
        help='Enable sector-based analysis (analyze all sectors, rank by strength)'
    )
    run_parser.add_argument(
        '--sector-first',
        action='store_true',
        help='Sector-first workflow: analyze sectors, then deep-dive top sectors only'
    )
    run_parser.add_argument(
        '--top-sectors',
        type=int,
        default=2,
        help='Number of top sectors to focus on (default: 2, use with --sector-first)'
    )
    run_parser.add_argument(
        '--stocks-per-sector',
        type=int,
        default=3,
        help='Stocks to analyze from each top sector (default: 3, use with --sector-first)'
    )
    run_parser.add_argument(
        '--buy-only',
        action='store_true',
        help='Show only BUY and STRONG BUY recommendations'
    )
    run_parser.add_argument(
        '--sort-by',
        choices=['gain', 'opportunity', 'rsi', 'priority'],
        default='gain',
        help='Sort results by: gain (default, highest profit potential), opportunity (composite score), rsi (oversold first), or priority (original score)'
    )
    run_parser.set_defaults(func=cmd_run)

    # Report command
    report_parser = subparsers.add_parser('report', help='Show latest report')
    report_parser.add_argument(
        '--date',
        help='Report date (YYYY-MM-DD, default: today)'
    )
    report_parser.add_argument(
        '--top',
        type=int,
        default=5,
        help='Number of top opportunities to show (default: 5)'
    )
    report_parser.set_defaults(func=cmd_report)

    # Top command
    top_parser = subparsers.add_parser('top', help='Show top opportunities')
    top_parser.add_argument(
        'limit',
        type=int,
        nargs='?',
        default=5,
        help='Number of opportunities to show (default: 5)'
    )
    top_parser.add_argument(
        '--date',
        help='Scan date (YYYY-MM-DD, default: today)'
    )
    top_parser.add_argument(
        '--refresh',
        action='store_true',
        help='Run fresh screener scan before showing top opportunities'
    )
    top_parser.set_defaults(func=cmd_top)

    # Update command
    update_parser = subparsers.add_parser('update', help='Update price data')
    update_parser.add_argument(
        '--full',
        action='store_true',
        help='Full refresh (not incremental)'
    )
    update_parser.set_defaults(func=cmd_update)

    # Legend command
    def cmd_legend(args):
        show_screener_legend()
        show_interpretation_tips()
        return 0

    legend_parser = subparsers.add_parser('legend', help='Show metrics legend and interpretation guide')
    legend_parser.set_defaults(func=cmd_legend)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
