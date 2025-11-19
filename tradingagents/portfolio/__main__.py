"""
Portfolio Management CLI

Simple commands to manage your investment portfolio.

Usage:
    # View your portfolio
    python -m tradingagents.portfolio

    # Buy stock
    python -m tradingagents.portfolio buy AAPL 10 175.50

    # Sell stock
    python -m tradingagents.portfolio sell AAPL 5 180.00

    # View performance
    python -m tradingagents.portfolio performance

    # View upcoming dividends
    python -m tradingagents.portfolio dividends
"""

import argparse
import sys
import logging
from datetime import date, datetime
from decimal import Decimal
from typing import List, Dict, Any

from tradingagents.database import get_db_connection, TickerOperations, PortfolioOperations
from tradingagents.utils import display_next_steps

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def format_currency(value) -> str:
    """Format value as currency."""
    if value is None:
        return "$0.00"
    return f"${float(value):,.2f}"


def format_pct(value) -> str:
    """Format value as percentage."""
    if value is None:
        return "0.00%"
    return f"{float(value):+.2f}%"


def print_portfolio_summary(portfolio_ops: PortfolioOperations, portfolio_id: int):
    """Print portfolio summary with current positions."""
    portfolio = portfolio_ops.get_portfolio(portfolio_id)
    if not portfolio:
        print(f"Portfolio {portfolio_id} not found.")
        return

    positions = portfolio_ops.get_positions(portfolio_id)

    print("\n" + "="*80)
    print(f"PORTFOLIO: {portfolio['portfolio_name']}")
    print("="*80)

    # Summary
    total_value = float(portfolio.get('total_value', 0) or 0)
    cash = float(portfolio.get('current_cash', 0) or 0)
    initial_cash = float(portfolio.get('initial_cash', 0) or 0)

    positions_value = total_value - cash
    total_gain_loss = total_value - initial_cash
    total_return_pct = (total_gain_loss / initial_cash * 100) if initial_cash > 0 else 0

    print(f"\n💰 Total Value: {format_currency(total_value)}")
    print(f"   Cash: {format_currency(cash)}")
    print(f"   Positions: {format_currency(positions_value)}")
    print(f"\n📈 Total Return: {format_currency(total_gain_loss)} ({format_pct(total_return_pct)})")

    # Positions
    if positions:
        print(f"\n{'='*80}")
        print("CURRENT HOLDINGS")
        print(f"{'='*80}\n")

        print(f"{'Symbol':<8} {'Shares':>10} {'Avg Cost':>12} {'Current':>12} {'Value':>14} {'Gain/Loss':>14} {'Return':>10}")
        print("-"*80)

        for pos in positions:
            symbol = pos['symbol']
            shares = float(pos['shares'] or 0)
            avg_cost = float(pos['average_cost'] or 0)
            current = float(pos.get('current_price', 0) or 0)
            value = float(pos.get('current_value', 0) or 0)
            gain_loss = float(pos.get('unrealized_gain_loss', 0) or 0)
            return_pct = float(pos.get('unrealized_gain_loss_pct', 0) or 0)

            # Color code gain/loss
            if gain_loss > 0:
                gain_str = f"+{format_currency(gain_loss)[1:]}"  # Remove $ and add +
                return_str = format_pct(return_pct)
            elif gain_loss < 0:
                gain_str = format_currency(gain_loss)
                return_str = format_pct(return_pct)
            else:
                gain_str = format_currency(0)
                return_str = format_pct(0)

            print(f"{symbol:<8} {shares:>10.2f} {format_currency(avg_cost):>12} "
                  f"{format_currency(current):>12} {format_currency(value):>14} "
                  f"{gain_str:>14} {return_str:>10}")

    else:
        print("\nNo positions yet. Start by buying some stocks!")

    print("\n" + "="*80 + "\n")


def buy_stock(
    portfolio_ops: PortfolioOperations,
    ticker_ops: TickerOperations,
    portfolio_id: int,
    symbol: str,
    shares: float,
    price: float,
    transaction_date: date = None
):
    """Buy stock."""
    if transaction_date is None:
        transaction_date = date.today()

    # Get ticker info
    ticker = ticker_ops.get_ticker(symbol=symbol.upper())
    if not ticker:
        print(f"Error: Ticker '{symbol}' not found in database.")
        print("Run the screener first to add tickers.")
        return

    ticker_id = ticker['ticker_id']
    shares_dec = Decimal(str(shares))
    price_dec = Decimal(str(price))

    # Record transaction
    try:
        transaction_id = portfolio_ops.record_transaction(
            portfolio_id=portfolio_id,
            ticker_id=ticker_id,
            transaction_type='BUY',
            transaction_date=transaction_date,
            shares=shares_dec,
            price_per_share=price_dec
        )

        total_cost = shares * price
        print(f"\n✅ BUY ORDER EXECUTED")
        print(f"   Symbol: {symbol.upper()}")
        print(f"   Shares: {shares}")
        print(f"   Price: {format_currency(price)}/share")
        print(f"   Total Cost: {format_currency(total_cost)}")
        print(f"   Transaction ID: {transaction_id}")
        print(f"   Date: {transaction_date}\n")

    except Exception as e:
        print(f"\n❌ Error: {e}\n")


def sell_stock(
    portfolio_ops: PortfolioOperations,
    ticker_ops: TickerOperations,
    portfolio_id: int,
    symbol: str,
    shares: float,
    price: float,
    transaction_date: date = None
):
    """Sell stock."""
    if transaction_date is None:
        transaction_date = date.today()

    # Get ticker info
    ticker = ticker_ops.get_ticker(symbol=symbol.upper())
    if not ticker:
        print(f"Error: Ticker '{symbol}' not found.")
        return

    ticker_id = ticker['ticker_id']
    shares_dec = Decimal(str(shares))
    price_dec = Decimal(str(price))

    # Record transaction
    try:
        transaction_id = portfolio_ops.record_transaction(
            portfolio_id=portfolio_id,
            ticker_id=ticker_id,
            transaction_type='SELL',
            transaction_date=transaction_date,
            shares=shares_dec,
            price_per_share=price_dec
        )

        total_proceeds = shares * price
        print(f"\n✅ SELL ORDER EXECUTED")
        print(f"   Symbol: {symbol.upper()}")
        print(f"   Shares: {shares}")
        print(f"   Price: {format_currency(price)}/share")
        print(f"   Total Proceeds: {format_currency(total_proceeds)}")
        print(f"   Transaction ID: {transaction_id}")
        print(f"   Date: {transaction_date}\n")

    except Exception as e:
        print(f"\n❌ Error: {e}\n")


def show_performance(portfolio_ops: PortfolioOperations, portfolio_id: int, days: int = 30):
    """Show performance history."""
    history = portfolio_ops.get_performance_history(portfolio_id, days)

    if not history:
        print("\nNo performance history yet. Create a snapshot with:")
        print("  python -m tradingagents.portfolio snapshot\n")
        return

    print("\n" + "="*80)
    print(f"PERFORMANCE HISTORY (Last {days} days)")
    print("="*80 + "\n")

    print(f"{'Date':<12} {'Total Value':>14} {'Day Change':>14} {'Total Return':>14} {'Return %':>10}")
    print("-"*80)

    for snap in history:
        snap_date = snap['snapshot_date'].strftime('%Y-%m-%d')
        total_value = float(snap['total_value'] or 0)
        day_change = float(snap.get('day_change', 0) or 0)
        total_gl = float(snap.get('total_gain_loss', 0) or 0)
        total_gl_pct = float(snap.get('total_gain_loss_pct', 0) or 0)

        print(f"{snap_date:<12} {format_currency(total_value):>14} "
              f"{format_currency(day_change):>14} "
              f"{format_currency(total_gl):>14} {format_pct(total_gl_pct):>10}")

    print("\n" + "="*80 + "\n")


def show_dividends(portfolio_ops: PortfolioOperations, portfolio_id: int, days: int = 90):
    """Show upcoming dividends."""
    dividends = portfolio_ops.get_upcoming_dividends(portfolio_id, days)

    if not dividends:
        print("\nNo upcoming dividends in the next {} days.\n".format(days))
        return

    print("\n" + "="*80)
    print(f"UPCOMING DIVIDENDS (Next {days} days)")
    print("="*80 + "\n")

    print(f"{'Symbol':<8} {'Payment Date':<14} {'$/Share':>12} {'Shares':>10} {'Total':>14}")
    print("-"*80)

    total_expected = 0
    for div in dividends:
        symbol = div['symbol']
        payment_date = div['payment_date'].strftime('%Y-%m-%d')
        per_share = float(div['dividend_per_share'] or 0)
        shares = float(div['shares_held'] or 0)
        total = float(div['total_dividend'] or 0)
        total_expected += total

        print(f"{symbol:<8} {payment_date:<14} {format_currency(per_share):>12} "
              f"{shares:>10.2f} {format_currency(total):>14}")

    print("-"*80)
    print(f"{'TOTAL EXPECTED':<23} {format_currency(total_expected):>14}")
    print("\n" + "="*80 + "\n")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Portfolio Management - Track your investments',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # View portfolio (default)
    view_parser = subparsers.add_parser('view', help='View portfolio summary')
    view_parser.add_argument(
        '--refresh',
        action='store_true',
        help='Refresh portfolio positions and prices before displaying'
    )

    # Buy command
    buy_parser = subparsers.add_parser('buy', help='Buy stock')
    buy_parser.add_argument('symbol', help='Stock symbol (e.g., AAPL)')
    buy_parser.add_argument('shares', type=float, help='Number of shares')
    buy_parser.add_argument('price', type=float, help='Price per share')
    buy_parser.add_argument('--date', help='Transaction date (YYYY-MM-DD)')

    # Sell command
    sell_parser = subparsers.add_parser('sell', help='Sell stock')
    sell_parser.add_argument('symbol', help='Stock symbol')
    sell_parser.add_argument('shares', type=float, help='Number of shares')
    sell_parser.add_argument('price', type=float, help='Price per share')
    sell_parser.add_argument('--date', help='Transaction date (YYYY-MM-DD)')

    # Performance command
    perf_parser = subparsers.add_parser('performance', help='View performance history')
    perf_parser.add_argument('--days', type=int, default=30, help='Days of history (default: 30)')
    perf_parser.add_argument(
        '--refresh',
        action='store_true',
        help='Refresh portfolio prices before calculating performance'
    )

    # Dividends command
    div_parser = subparsers.add_parser('dividends', help='View upcoming dividends')
    div_parser.add_argument('--days', type=int, default=90, help='Days ahead (default: 90)')

    # Snapshot command
    subparsers.add_parser('snapshot', help='Create daily snapshot')

    # Portfolio ID (default to 1)
    parser.add_argument('--portfolio-id', type=int, default=1, help='Portfolio ID (default: 1)')

    args = parser.parse_args()

    # Initialize database connection
    db = get_db_connection()
    portfolio_ops = PortfolioOperations(db)
    ticker_ops = TickerOperations(db)

    # Default command
    if args.command is None or args.command == 'view':
        # Refresh if requested
        if hasattr(args, 'refresh') and args.refresh:
            print("Refreshing portfolio prices...")
            from tradingagents.screener.data_fetcher import DataFetcher
            data_fetcher = DataFetcher(db)
            positions = portfolio_ops.get_positions(args.portfolio_id)
            for pos in positions:
                ticker_id = pos.get('ticker_id')
                symbol = pos.get('symbol')
                if ticker_id and symbol:
                    data_fetcher.update_ticker_prices(ticker_id, symbol)
            # Update portfolio totals
            portfolio_ops._update_portfolio_totals(args.portfolio_id)
            print("✓ Portfolio refreshed\n")
        print_portfolio_summary(portfolio_ops, args.portfolio_id)
        display_next_steps('portfolio')

    elif args.command == 'buy':
        trans_date = datetime.strptime(args.date, '%Y-%m-%d').date() if args.date else date.today()
        buy_stock(portfolio_ops, ticker_ops, args.portfolio_id, args.symbol, args.shares, args.price, trans_date)
        print_portfolio_summary(portfolio_ops, args.portfolio_id)
        display_next_steps('portfolio')

    elif args.command == 'sell':
        trans_date = datetime.strptime(args.date, '%Y-%m-%d').date() if args.date else date.today()
        sell_stock(portfolio_ops, ticker_ops, args.portfolio_id, args.symbol, args.shares, args.price, trans_date)
        print_portfolio_summary(portfolio_ops, args.portfolio_id)
        display_next_steps('portfolio')

    elif args.command == 'performance':
        # Refresh if requested
        if args.refresh:
            print("Refreshing portfolio prices...")
            from tradingagents.screener.data_fetcher import DataFetcher
            data_fetcher = DataFetcher(db)
            positions = portfolio_ops.get_positions(args.portfolio_id)
            for pos in positions:
                ticker_id = pos.get('ticker_id')
                symbol = pos.get('symbol')
                if ticker_id and symbol:
                    data_fetcher.update_ticker_prices(ticker_id, symbol)
            # Update portfolio totals
            portfolio_ops._update_portfolio_totals(args.portfolio_id)
            print("✓ Portfolio refreshed\n")
        show_performance(portfolio_ops, args.portfolio_id, args.days)
        display_next_steps('performance')

    elif args.command == 'dividends':
        show_dividends(portfolio_ops, args.portfolio_id, args.days)

    elif args.command == 'snapshot':
        portfolio_ops.create_snapshot(args.portfolio_id)
        print("\n✅ Snapshot created successfully.\n")
        show_performance(portfolio_ops, args.portfolio_id, days=7)
        display_next_steps('performance')


if __name__ == '__main__':
    main()
