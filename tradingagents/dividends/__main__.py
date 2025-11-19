"""
CLI interface for dividend tracking and analysis.

Usage:
    python -m tradingagents.dividends <command> [options]

Commands:
    backfill        Backfill dividend history from yfinance
    upcoming        Show upcoming dividend payments
    income          Show dividend income report
    high-yield      Show high-yield dividend stocks
    safety          Analyze dividend safety
    reinvest        Get dividend reinvestment suggestions
    update-cache    Update dividend yield cache
    update-calendar Update dividend calendar predictions
"""

import argparse
import sys
from datetime import datetime
import logging

from tradingagents.dividends import (
    DividendFetcher,
    DividendCalendar,
    DividendTracker,
    DividendMetrics
)
from tradingagents.utils import display_next_steps

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def cmd_backfill(args):
    """Backfill dividend history from yfinance."""
    fetcher = DividendFetcher()

    if args.symbol:
        # Backfill single symbol
        print(f"Fetching dividend history for {args.symbol}...")
        count = fetcher.fetch_and_store(args.symbol)
        print(f"✓ Stored {count} dividend records for {args.symbol}")

    else:
        # Backfill all tickers
        print(f"Backfilling dividend history for all tickers ({args.years} years)...")
        results = fetcher.backfill_all_tickers(
            years_back=args.years,
            active_only=not args.all
        )

        total = sum(results.values())
        with_dividends = sum(1 for count in results.values() if count > 0)

        print(f"\n{'='*60}")
        print(f"Backfill Complete!")
        print(f"{'='*60}")
        print(f"Total tickers processed: {len(results)}")
        print(f"Tickers with dividends:  {with_dividends}")
        print(f"Total dividend records:  {total}")
        print(f"{'='*60}")


def cmd_upcoming(args):
    """Show upcoming dividend payments."""
    # Refresh data if requested
    if args.refresh_data:
        print("Refreshing dividend data...")
        fetcher = DividendFetcher()
        if args.symbol:
            fetcher.fetch_and_store(args.symbol)
            fetcher.update_yield_cache(args.symbol)
        else:
            # Refresh for all tickers (this might take a while)
            print("This may take a few minutes...")
            from tradingagents.database import DatabaseConnection
            db = DatabaseConnection()
            query = "SELECT DISTINCT t.symbol FROM tickers t WHERE t.active = TRUE ORDER BY t.symbol"
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    symbols = [row[0] for row in cur.fetchall()]
            for symbol in symbols[:50]:  # Limit to first 50 to avoid timeout
                try:
                    fetcher.fetch_and_store(symbol)
                    fetcher.update_yield_cache(symbol)
                except:
                    pass
        print("✓ Dividend data refreshed\n")

    calendar = DividendCalendar()

    if args.symbol:
        # Show prediction for specific symbol
        prediction = calendar.predict_next_dividend(args.symbol)

        if prediction:
            print(f"\n📅 Next Dividend Prediction for {args.symbol}")
            print(f"{'='*60}")
            print(f"Ex-Date (est):     {prediction['expected_ex_date']}")
            print(f"Payment Date (est): {prediction['expected_payment_date']}")
            print(f"Amount (est):       ${prediction['expected_amount_per_share']:.4f}")
            print(f"Confidence:         {prediction['confidence']}")
            print(f"Based on:           {prediction['based_on_history']} historical dividends")
            print(f"{'='*60}")
        else:
            print(f"No dividend history found for {args.symbol}")

    else:
        # Show upcoming calendar
        output = calendar.format_calendar(
            days_ahead=args.days,
            min_yield=args.min_yield
        )
        print(output)
    
    # Display next steps and recommendations
    display_next_steps('dividends')


def cmd_income(args):
    """Show dividend income report."""
    tracker = DividendTracker()

    year = args.year if args.year else datetime.now().year

    if args.symbol:
        # Income for specific symbol
        summary = tracker.get_dividend_income_summary(year=year, symbol=args.symbol)

        print(f"\n💵 Dividend Income for {args.symbol} ({year})")
        print(f"{'='*60}")
        print(f"Payments Received: {summary['payment_count']}")
        print(f"Gross Income:      ${summary['total_gross_income']:.2f}")
        print(f"Tax Withheld:      ${summary['total_tax_withheld']:.2f}")
        print(f"Net Income:        ${summary['total_net_income']:.2f}")
        print(f"{'='*60}")

    else:
        # Full income report
        report = tracker.format_income_report(year=year)
        print(report)


def cmd_high_yield(args):
    """Show high-yield dividend stocks."""
    metrics = DividendMetrics()

    report = metrics.format_high_yield_report(
        min_yield=args.min_yield,
        limit=args.limit
    )
    print(report)


def cmd_safety(args):
    """Analyze dividend safety for a stock."""
    metrics = DividendMetrics()

    analysis = metrics.analyze_dividend_safety(args.symbol)

    if analysis:
        print(f"\n🔒 Dividend Safety Analysis: {args.symbol}")
        print(f"{'='*60}")
        print(f"Safety Score:      {analysis['safety_score']}/100")
        print(f"Safety Rating:     {analysis['safety_rating']}")
        print(f"Recommendation:    {analysis['recommendation']}")
        print(f"\nCurrent Metrics:")
        print(f"  Dividend Yield:     {analysis['dividend_yield_pct']:.2f}%")
        print(f"  Annual Dividend:    ${analysis['annual_dividend']:.2f}")
        print(f"  Consecutive Years:  {analysis['consecutive_years']}")

        if analysis['payout_ratio_pct']:
            print(f"  Payout Ratio:       {analysis['payout_ratio_pct']:.1f}%")
        if analysis['growth_3yr_pct']:
            print(f"  3yr Growth:         {analysis['growth_3yr_pct']:.1f}%")

        print(f"\nSafety Factors:")
        for factor in analysis['factors']:
            print(f"  {factor}")

        print(f"{'='*60}")
    else:
        print(f"No dividend data available for {args.symbol}")


def cmd_reinvest(args):
    """Get dividend reinvestment suggestions."""
    metrics = DividendMetrics()

    suggestions = metrics.suggest_dividend_reinvestment(
        available_cash=args.cash,
        min_yield=args.min_yield,
        prefer_growth=args.prefer_growth
    )

    if not suggestions:
        print("No suitable stocks found for reinvestment.")
        return

    print(f"\n💰 Dividend Reinvestment Suggestions")
    print(f"{'='*80}")
    print(f"Available Cash: ${args.cash:.2f}")
    print(f"Strategy: {'Dividend Growth' if args.prefer_growth else 'High Yield'}")
    print(f"{'='*80}\n")

    print(
        f"{'Rank':<6} {'Symbol':<8} {'Yield':<8} {'Price':<10} "
        f"{'Shares':<8} {'Amount':<12} {'Score':<8}"
    )
    print("-" * 80)

    for i, stock in enumerate(suggestions[:10], 1):
        if stock['affordable_shares'] == 0:
            continue

        print(
            f"#{i:<5} {stock['symbol']:<8} "
            f"{stock['dividend_yield_pct']:<7.2f}% "
            f"${stock['current_price']:<9.2f} "
            f"{stock['affordable_shares']:<8} "
            f"${stock['investment_amount']:<11.2f} "
            f"{stock['reinvestment_score']:<7.0f}"
        )

    print(f"\n{'='*80}")


def cmd_update_cache(args):
    """Update dividend yield cache."""
    fetcher = DividendFetcher()

    if args.symbol:
        # Update single symbol
        print(f"Updating dividend yield cache for {args.symbol}...")
        success = fetcher.update_yield_cache(args.symbol, cache_hours=args.cache_hours)

        if success:
            print(f"✓ Updated cache for {args.symbol}")
        else:
            print(f"✗ Failed to update cache for {args.symbol}")

    else:
        print("Updating dividend yield cache for all dividend-paying stocks...")
        print("This may take a few minutes...\n")

        # Get all tickers with dividend history
        from tradingagents.database import DatabaseConnection
        db = DatabaseConnection()

        query = """
            SELECT DISTINCT t.symbol
            FROM tickers t
            JOIN dividend_payments dp ON t.ticker_id = dp.ticker_id
            WHERE t.active = TRUE
            ORDER BY t.symbol
        """

        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                symbols = [row[0] for row in cur.fetchall()]

        success_count = 0
        for symbol in symbols:
            try:
                if fetcher.update_yield_cache(symbol, cache_hours=args.cache_hours):
                    print(f"✓ {symbol}")
                    success_count += 1
                else:
                    print(f"- {symbol} (no data)")
            except Exception as e:
                print(f"✗ {symbol} (error: {e})")

        print(f"\n{'='*60}")
        print(f"Cache update complete!")
        print(f"Successfully updated: {success_count}/{len(symbols)}")
        print(f"{'='*60}")


def cmd_update_calendar(args):
    """Update dividend calendar predictions."""
    calendar = DividendCalendar()

    print(f"Updating dividend calendar ({args.days} days ahead)...")
    count = calendar.update_calendar(days_ahead=args.days)

    print(f"✓ Updated calendar with {count} dividend predictions")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Dividend tracking and analysis CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Backfill command
    backfill_parser = subparsers.add_parser('backfill', help='Backfill dividend history')
    backfill_parser.add_argument('-s', '--symbol', type=str, help='Symbol to backfill (default: all)')
    backfill_parser.add_argument('-y', '--years', type=int, default=5, help='Years of history (default: 5)')
    backfill_parser.add_argument('-a', '--all', action='store_true', help='Include inactive tickers')

    # Upcoming command
    upcoming_parser = subparsers.add_parser('upcoming', help='Show upcoming dividends')
    upcoming_parser.add_argument('-s', '--symbol', type=str, help='Specific symbol')
    upcoming_parser.add_argument('-d', '--days', type=int, default=60, help='Days ahead (default: 60)')
    upcoming_parser.add_argument('-y', '--min-yield', type=float, help='Minimum yield filter')
    upcoming_parser.add_argument(
        '--refresh-data',
        action='store_true',
        help='Fetch fresh dividend data before showing upcoming dividends'
    )

    # Income command
    income_parser = subparsers.add_parser('income', help='Show dividend income report')
    income_parser.add_argument('-s', '--symbol', type=str, help='Specific symbol')
    income_parser.add_argument('-y', '--year', type=int, help='Year (default: current year)')

    # High-yield command
    high_yield_parser = subparsers.add_parser('high-yield', help='Show high-yield stocks')
    high_yield_parser.add_argument('-y', '--min-yield', type=float, default=3.0, help='Min yield %% (default: 3.0)')
    high_yield_parser.add_argument('-l', '--limit', type=int, default=20, help='Max results (default: 20)')

    # Safety command
    safety_parser = subparsers.add_parser('safety', help='Analyze dividend safety')
    safety_parser.add_argument('symbol', type=str, help='Stock symbol')

    # Reinvest command
    reinvest_parser = subparsers.add_parser('reinvest', help='Get reinvestment suggestions')
    reinvest_parser.add_argument('cash', type=float, help='Available cash for reinvestment')
    reinvest_parser.add_argument('-y', '--min-yield', type=float, default=2.0, help='Min yield %% (default: 2.0)')
    reinvest_parser.add_argument('-g', '--prefer-growth', action='store_true', help='Prefer dividend growth')

    # Update cache command
    update_cache_parser = subparsers.add_parser('update-cache', help='Update dividend yield cache')
    update_cache_parser.add_argument('-s', '--symbol', type=str, help='Specific symbol (default: all)')
    update_cache_parser.add_argument('-c', '--cache-hours', type=int, default=24, help='Cache validity hours')

    # Update calendar command
    update_calendar_parser = subparsers.add_parser('update-calendar', help='Update dividend calendar')
    update_calendar_parser.add_argument('-d', '--days', type=int, default=180, help='Days ahead (default: 180)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    commands = {
        'backfill': cmd_backfill,
        'upcoming': cmd_upcoming,
        'income': cmd_income,
        'high-yield': cmd_high_yield,
        'safety': cmd_safety,
        'reinvest': cmd_reinvest,
        'update-cache': cmd_update_cache,
        'update-calendar': cmd_update_calendar,
    }

    try:
        commands[args.command](args)
        return 0
    except Exception as e:
        logger.error(f"Error executing command: {e}", exc_info=True)
        print(f"\n✗ Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
