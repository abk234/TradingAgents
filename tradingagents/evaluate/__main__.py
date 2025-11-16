"""
Evaluation CLI - Phase 6

Command-line interface for tracking and analyzing recommendation outcomes.
"""

import argparse
import logging
import sys
from datetime import datetime

from tradingagents.evaluate.outcome_tracker import OutcomeTracker
from tradingagents.evaluate.performance import PerformanceAnalyzer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def backfill_command(args):
    """Backfill historical recommendations."""
    print("=" * 80)
    print("BACKFILLING HISTORICAL RECOMMENDATIONS")
    print("=" * 80)
    print()

    tracker = OutcomeTracker()

    # Create outcome records
    print(f"Looking for analyses from last {args.days} days...")
    created = tracker.backfill_historical_recommendations(days_back=args.days)
    print(f"✅ Created {created} outcome records")
    print()

    # Update with price data
    if created > 0:
        print("Updating outcomes with price data...")
        updated = tracker.update_outcomes(lookback_days=args.days)
        print(f"✅ Updated {updated} outcomes with price data")
        print()

        # Update S&P 500 benchmark
        print("Updating S&P 500 benchmark data...")
        spy_days = tracker.update_sp500_benchmark(days_back=args.days)
        print(f"✅ Updated {spy_days} days of S&P 500 data")
        print()

        # Calculate alpha
        print("Calculating alpha (excess return vs S&P 500)...")
        alpha_count = tracker.calculate_alpha()
        print(f"✅ Calculated alpha for {alpha_count} outcomes")
        print()

    print("=" * 80)
    print("✅ BACKFILL COMPLETE")
    print("=" * 80)


def update_command(args):
    """Update existing outcomes with latest price data."""
    print("=" * 80)
    print("UPDATING RECOMMENDATION OUTCOMES")
    print("=" * 80)
    print()

    tracker = OutcomeTracker()

    # Update outcomes
    print(f"Updating outcomes from last {args.days} days...")
    updated = tracker.update_outcomes(lookback_days=args.days)
    print(f"✅ Updated {updated} outcomes")
    print()

    # Update S&P 500
    print("Updating S&P 500 benchmark data...")
    spy_days = tracker.update_sp500_benchmark(days_back=args.days)
    print(f"✅ Updated {spy_days} days of S&P 500 data")
    print()

    # Calculate alpha
    print("Calculating alpha...")
    alpha_count = tracker.calculate_alpha()
    print(f"✅ Updated alpha for {alpha_count} outcomes")
    print()

    print("=" * 80)
    print("✅ UPDATE COMPLETE")
    print("=" * 80)


def report_command(args):
    """Generate performance report."""
    analyzer = PerformanceAnalyzer()
    report = analyzer.generate_report(days_back=args.period)
    print(report)


def recent_command(args):
    """Show recent outcomes."""
    analyzer = PerformanceAnalyzer()
    outcomes = analyzer.get_recent_outcomes(limit=args.limit)

    print("=" * 80)
    print(f"RECENT OUTCOMES (Last {args.limit})")
    print("=" * 80)
    print()

    if not outcomes:
        print("No outcomes found.")
        return

    print(f"{'Symbol':<8} {'Date':<12} {'Decision':<8} {'Conf':<6} {'1d':<8} {'7d':<8} {'30d':<8} {'Quality':<12} {'Status'}")
    print("-" * 80)

    for o in outcomes:
        symbol = o['symbol']
        date_str = o['recommendation_date'].strftime('%Y-%m-%d') if o['recommendation_date'] else 'N/A'
        decision = o['decision']
        conf = o['confidence']

        ret_1d = f"{o['return_1day_pct']:+.1f}%" if o.get('return_1day_pct') is not None else "N/A"
        ret_7d = f"{o['return_7days_pct']:+.1f}%" if o.get('return_7days_pct') is not None else "N/A"
        ret_30d = f"{o['return_30days_pct']:+.1f}%" if o.get('return_30days_pct') is not None else "N/A"

        quality = o.get('outcome_quality', 'N/A') or 'N/A'
        status = o.get('evaluation_status', 'PENDING')

        print(f"{symbol:<8} {date_str:<12} {decision:<8} {conf:<6} {ret_1d:<8} {ret_7d:<8} {ret_30d:<8} {quality:<12} {status}")

    print()


def stats_command(args):
    """Show quick statistics."""
    analyzer = PerformanceAnalyzer()
    stats = analyzer.get_overall_stats(days_back=args.period)

    print("=" * 80)
    print(f"QUICK STATS (Last {args.period} Days)")
    print("=" * 80)
    print()

    print(f"Total Recommendations: {stats.get('total_recommendations', 0)}")
    print(f"Evaluated (30+ days):  {stats.get('evaluated_recs', 0)}")
    print()

    if stats.get('evaluated_recs', 0) > 0:
        win_rate = stats.get('win_rate_pct', 0)
        avg_return = stats.get('avg_return_30days', 0)
        avg_sp500 = stats.get('avg_sp500_return_30days', 0)
        alpha = stats.get('avg_alpha_30days', 0)

        print(f"Win Rate:              {win_rate}%")
        print(f"Average Return:        {avg_return:+.2f}%")
        print()

        if avg_sp500 is not None:
            print(f"S&P 500 Return:        {avg_sp500:+.2f}%")
            print(f"Alpha:                 {alpha:+.2f}%")

            if alpha > 0:
                print(f"✅ Beating the market by {alpha:.2f}%!")
            else:
                print(f"⚠️  Underperforming by {abs(alpha):.2f}%")
    else:
        print("⏳ No recommendations old enough for evaluation yet")

    print()


def main():
    """Main entry point for evaluation CLI."""
    parser = argparse.ArgumentParser(
        description="Track and analyze recommendation outcomes (Phase 6)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # First time setup - backfill all historical recommendations
  python -m tradingagents.evaluate --backfill --days 90

  # Daily update - refresh outcome data
  python -m tradingagents.evaluate --update

  # Generate performance report
  python -m tradingagents.evaluate --report --period 90

  # Quick stats
  python -m tradingagents.evaluate --stats

  # View recent outcomes
  python -m tradingagents.evaluate --recent --limit 20
        """
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Backfill command
    backfill_parser = subparsers.add_parser('backfill', help='Backfill historical recommendations')
    backfill_parser.add_argument('--days', type=int, default=90,
                                help='How many days back to look (default: 90)')

    # Update command
    update_parser = subparsers.add_parser('update', help='Update existing outcomes')
    update_parser.add_argument('--days', type=int, default=90,
                              help='Update outcomes from last N days (default: 90)')

    # Report command
    report_parser = subparsers.add_parser('report', help='Generate performance report')
    report_parser.add_argument('--period', type=int, default=90,
                              help='Report period in days (default: 90)')

    # Recent command
    recent_parser = subparsers.add_parser('recent', help='Show recent outcomes')
    recent_parser.add_argument('--limit', type=int, default=20,
                              help='Number of outcomes to show (default: 20)')

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Quick statistics')
    stats_parser.add_argument('--period', type=int, default=90,
                             help='Period in days (default: 90)')

    # Also support legacy flags for backwards compatibility
    parser.add_argument('--backfill', action='store_true',
                       help='Backfill historical recommendations (use "backfill" command instead)')
    parser.add_argument('--update', action='store_true',
                       help='Update outcomes with latest prices (use "update" command instead)')
    parser.add_argument('--report', action='store_true',
                       help='Generate performance report (use "report" command instead)')
    parser.add_argument('--recent', action='store_true',
                       help='Show recent outcomes (use "recent" command instead)')
    parser.add_argument('--stats', action='store_true',
                       help='Show quick statistics (use "stats" command instead)')

    parser.add_argument('--days', type=int, default=90,
                       help='Days to look back (for --backfill, --update)')
    parser.add_argument('--period', type=int, default=90,
                       help='Report period in days (for --report, --stats)')
    parser.add_argument('--limit', type=int, default=20,
                       help='Number of items to show (for --recent)')

    args = parser.parse_args()

    # Handle subcommands
    if args.command == 'backfill':
        backfill_command(args)
    elif args.command == 'update':
        update_command(args)
    elif args.command == 'report':
        report_command(args)
    elif args.command == 'recent':
        recent_command(args)
    elif args.command == 'stats':
        stats_command(args)

    # Handle legacy flags
    elif args.backfill:
        backfill_command(args)
    elif args.update:
        update_command(args)
    elif args.report:
        report_command(args)
    elif args.recent:
        recent_command(args)
    elif args.stats:
        stats_command(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
