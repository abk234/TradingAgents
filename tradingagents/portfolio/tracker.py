"""
Portfolio Tracker

High-level interface for portfolio tracking and management.
"""

from typing import List, Dict, Any
from decimal import Decimal
from datetime import date

from tradingagents.database import get_db_connection, PortfolioOperations, TickerOperations


class PortfolioTracker:
    """High-level portfolio tracker."""

    def __init__(self, portfolio_id: int = 1):
        """
        Initialize portfolio tracker.

        Args:
            portfolio_id: Portfolio ID to track (default: 1)
        """
        self.db = get_db_connection()
        self.portfolio_ops = PortfolioOperations(self.db)
        self.ticker_ops = TickerOperations(self.db)
        self.portfolio_id = portfolio_id

    def get_summary(self) -> Dict[str, Any]:
        """Get portfolio summary."""
        portfolio = self.portfolio_ops.get_portfolio(self.portfolio_id)
        positions = self.portfolio_ops.get_positions(self.portfolio_id)

        total_value = float(portfolio.get('total_value', 0) or 0)
        cash = float(portfolio.get('current_cash', 0) or 0)
        initial_cash = float(portfolio.get('initial_cash', 0) or 0)

        positions_value = total_value - cash
        total_return = total_value - initial_cash
        total_return_pct = (total_return / initial_cash * 100) if initial_cash > 0 else 0

        return {
            'portfolio_id': self.portfolio_id,
            'name': portfolio['portfolio_name'],
            'total_value': total_value,
            'cash': cash,
            'positions_value': positions_value,
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'num_positions': len(positions),
            'positions': positions
        }

    def buy(self, symbol: str, shares: float, price: float, transaction_date: date = None):
        """
        Buy stock.

        Args:
            symbol: Stock symbol
            shares: Number of shares
            price: Price per share
            transaction_date: Date of transaction (default: today)
        """
        ticker = self.ticker_ops.get_ticker(symbol=symbol.upper())
        if not ticker:
            raise ValueError(f"Ticker '{symbol}' not found in database")

        if transaction_date is None:
            transaction_date = date.today()

        return self.portfolio_ops.record_transaction(
            portfolio_id=self.portfolio_id,
            ticker_id=ticker['ticker_id'],
            transaction_type='BUY',
            transaction_date=transaction_date,
            shares=Decimal(str(shares)),
            price_per_share=Decimal(str(price))
        )

    def sell(self, symbol: str, shares: float, price: float, transaction_date: date = None):
        """
        Sell stock.

        Args:
            symbol: Stock symbol
            shares: Number of shares
            price: Price per share
            transaction_date: Date of transaction (default: today)
        """
        ticker = self.ticker_ops.get_ticker(symbol=symbol.upper())
        if not ticker:
            raise ValueError(f"Ticker '{symbol}' not found in database")

        if transaction_date is None:
            transaction_date = date.today()

        return self.portfolio_ops.record_transaction(
            portfolio_id=self.portfolio_id,
            ticker_id=ticker['ticker_id'],
            transaction_type='SELL',
            transaction_date=transaction_date,
            shares=Decimal(str(shares)),
            price_per_share=Decimal(str(price))
        )

    def update_prices(self):
        """Update all position prices from market data."""
        positions = self.portfolio_ops.get_positions(self.portfolio_id)

        for pos in positions:
            symbol = pos['symbol']
            # TODO: Fetch current price from market data
            # For now, positions are updated when transactions occur
            pass

    def create_snapshot(self, snapshot_date: date = None):
        """Create a daily performance snapshot."""
        return self.portfolio_ops.create_snapshot(self.portfolio_id, snapshot_date)

    def get_performance(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get performance history."""
        return self.portfolio_ops.get_performance_history(self.portfolio_id, days)

    def get_upcoming_dividends(self, days: int = 90) -> List[Dict[str, Any]]:
        """Get upcoming dividend payments."""
        return self.portfolio_ops.get_upcoming_dividends(self.portfolio_id, days)

    def close(self):
        """Close database connection."""
        # Connection pool handles this
        pass
