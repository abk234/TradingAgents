# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Insights CLI - Phase 7

Command-line interface for daily digests, alerts, and notifications.
"""

import argparse
import logging
import sys
from datetime import datetime, date
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from tradingagents.insights.digest import MarketDigest
from tradingagents.insights.alerts import PriceAlertSystem
from tradingagents.insights.notifications import NotificationDelivery
from tradingagents.utils import display_next_steps

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def digest_command(args):
    """Generate and display daily market digest."""
    # Refresh data if requested
    if args.refresh:
        print("Refreshing underlying data...")
        from tradingagents.screener import DailyScreener
        screener = DailyScreener()
        screener.scan_all(update_prices=True, store_results=True)
        print("✓ Data refreshed\n")

    digest_gen = MarketDigest()

    target_date = date.today()
    if args.date:
        target_date = datetime.strptime(args.date, '%Y-%m-%d').date()

    digest = digest_gen.generate_digest(target_date)

    if args.output:
        # Save to file
        with open(args.output, 'w') as f:
            f.write(digest)
        print(f"Digest saved to {args.output}")
    else:
        # Print to terminal
        print(digest)
    
    # Display next steps and recommendations
    display_next_steps('digest')


def alerts_command(args):
    """Check and display price alerts."""
    # Refresh data if requested
    if args.refresh:
        print("Refreshing price data...")
        from tradingagents.screener import DailyScreener
        screener = DailyScreener()
        screener.scan_all(update_prices=True, store_results=True)
        print("✓ Price data refreshed\n")

    alert_system = PriceAlertSystem()

    alerts = alert_system.check_all_alerts()

    if not alerts:
        print("✅ No active alerts at this time.")
        return

    # Format and display alerts
    formatted = alert_system.format_alerts(alerts)
    print(formatted)

    if args.output:
        # Save to file
        with open(args.output, 'w') as f:
            f.write(formatted)
        print(f"\nAlerts saved to {args.output}")
    
    # Display next steps and recommendations
    display_next_steps('alerts')


def notify_command(args):
    """Send a test notification."""
    notifier = NotificationDelivery()

    channels = args.channels.split(',') if args.channels else ['terminal', 'log']

    results = notifier.send(
        message=args.message,
        title=args.title,
        priority=args.priority,
        channels=channels
    )

    print("\nNotification Results:")
    for channel, success in results.items():
        status = "✅ Success" if success else "❌ Failed"
        print(f"  {channel}: {status}")


def summary_command(args):
    """Generate quick summary."""
    digest_gen = MarketDigest()
    summary = digest_gen.generate_quick_summary()
    print(summary)


def morning_command(args):
    """Run full morning routine: digest + alerts."""
    print("=" * 80)
    print("🌅 MORNING MARKET BRIEFING")
    print("=" * 80)
    print()

    # Generate digest
    digest_gen = MarketDigest()
    digest = digest_gen.generate_digest()
    print(digest)
    print()

    # Check alerts
    alert_system = PriceAlertSystem()
    alerts = alert_system.check_all_alerts()

    if alerts:
        print("\n")
        formatted_alerts = alert_system.format_alerts(alerts)
        print(formatted_alerts)
    
    # Display next steps and recommendations
    display_next_steps('morning')


def main():
    """Main entry point for insights CLI."""
    parser = argparse.ArgumentParser(
        description="TradingAgents Insights - Daily digests, alerts, and notifications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Daily morning routine
  python -m tradingagents.insights morning

  # Generate daily digest
  python -m tradingagents.insights digest

  # Check price alerts
  python -m tradingagents.insights alerts

  # Quick summary
  python -m tradingagents.insights summary

  # Test notification
  python -m tradingagents.insights notify --message "Test alert" --title "Test"
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Digest command
    digest_parser = subparsers.add_parser('digest', help='Generate daily market digest')
    digest_parser.add_argument('--date', type=str, help='Date for digest (YYYY-MM-DD)')
    digest_parser.add_argument('--output', type=str, help='Save digest to file')
    digest_parser.add_argument(
        '--refresh',
        action='store_true',
        help='Refresh underlying data (scans, analyses) before generating digest'
    )

    # Alerts command
    alerts_parser = subparsers.add_parser('alerts', help='Check price alerts')
    alerts_parser.add_argument('--output', type=str, help='Save alerts to file')
    alerts_parser.add_argument(
        '--refresh',
        action='store_true',
        help='Refresh price data before checking alerts'
    )

    # Notify command
    notify_parser = subparsers.add_parser('notify', help='Send test notification')
    notify_parser.add_argument('--message', required=True, help='Notification message')
    notify_parser.add_argument('--title', help='Notification title')
    notify_parser.add_argument('--priority', default='MEDIUM',
                              choices=['URGENT', 'HIGH', 'MEDIUM', 'LOW'])
    notify_parser.add_argument('--channels', help='Comma-separated channels (terminal,log,email,webhook)')

    # Summary command
    summary_parser = subparsers.add_parser('summary', help='Generate quick summary')

    # Morning command
    morning_parser = subparsers.add_parser('morning', help='Full morning briefing (digest + alerts)')

    args = parser.parse_args()

    # Execute command
    if args.command == 'digest':
        digest_command(args)
    elif args.command == 'alerts':
        alerts_command(args)
    elif args.command == 'notify':
        notify_command(args)
    elif args.command == 'summary':
        summary_command(args)
    elif args.command == 'morning':
        morning_command(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
