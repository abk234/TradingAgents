#!/usr/bin/env python3
"""
Daily Screener CLI

Command-line interface for the daily screening system.

Usage:
    python -m tradingagents.screener run          # Run daily screener
    python -m tradingagents.screener report       # Show latest report
    python -m tradingagents.screener top [N]      # Show top N opportunities
    python -m tradingagents.screener update       # Update price data only
"""

import sys
import argparse
from datetime import date
import logging

from .screener import DailyScreener

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def cmd_run(args):
    """Run the daily screener."""
    screener = DailyScreener()

    # Run scan
    results = screener.scan_all(
        update_prices=not args.no_update,
        store_results=not args.no_store
    )

    # Show report
    if results and not args.quiet:
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

    scan_date = date.fromisoformat(args.date) if args.date else None
    opportunities = screener.get_top_opportunities(limit=args.limit, scan_date=scan_date)

    if not opportunities:
        print("No opportunities found.")
        return 1

    print("="*70)
    print(f"TOP {len(opportunities)} OPPORTUNITIES")
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
        default=5,
        help='Number of top opportunities to show (default: 5)'
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
    top_parser.set_defaults(func=cmd_top)

    # Update command
    update_parser = subparsers.add_parser('update', help='Update price data')
    update_parser.add_argument(
        '--full',
        action='store_true',
        help='Full refresh (not incremental)'
    )
    update_parser.set_defaults(func=cmd_update)

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
