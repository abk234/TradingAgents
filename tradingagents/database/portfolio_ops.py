# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Portfolio Operations Module - Phase 5

Database operations for portfolio tracking:
- Portfolio configuration (risk tolerance, position limits)
- Position recommendations (sizing, timing, entry/exit)
- Holdings management (track positions)
- Trade execution (record buy/sell)
- Performance tracking (snapshots, returns, benchmarks)
"""

from typing import List, Dict, Any, Optional
from datetime import date, datetime
from decimal import Decimal
import logging

from .connection import DatabaseConnection

logger = logging.getLogger(__name__)


class PortfolioOperations:
    """Operations for portfolio tracking and management (Phase 5)."""

    def __init__(self, db: DatabaseConnection):
        """
        Initialize portfolio operations.

        Args:
            db: DatabaseConnection instance
        """
        self.db = db

    # ========================================================================
    # PORTFOLIO CONFIGURATION
    # ========================================================================

    def create_config(
        self,
        portfolio_value: Decimal,
        max_position_pct: Decimal = Decimal('10.0'),
        risk_tolerance: str = 'moderate',
        cash_reserve_pct: Decimal = Decimal('20.0'),
        sector_limits: Dict[str, float] = None,
        notes: str = None
    ) -> int:
        """
        Create a new portfolio configuration.

        Args:
            portfolio_value: Total portfolio value in USD
            max_position_pct: Maximum position size as % of portfolio (default 10%)
            risk_tolerance: 'conservative', 'moderate', or 'aggressive'
            cash_reserve_pct: Minimum cash reserve as % of portfolio (default 20%)
            sector_limits: Optional sector exposure limits as JSON
            notes: Optional notes

        Returns:
            config_id
        """
        # Deactivate any existing active configs
        self.db.execute_query(
            "UPDATE portfolio_config SET is_active = false WHERE is_active = true",
            fetch=False
        )

        query = """
            INSERT INTO portfolio_config (
                portfolio_value, max_position_pct, risk_tolerance,
                cash_reserve_pct, sector_limits, notes, is_active
            )
            VALUES (%s, %s, %s, %s, %s::jsonb, %s, true)
            RETURNING config_id
        """

        import json
        sector_limits_json = json.dumps(sector_limits) if sector_limits else None

        result = self.db.execute_query(
            query,
            (portfolio_value, max_position_pct, risk_tolerance,
             cash_reserve_pct, sector_limits_json, notes),
            fetch_one=True
        )
        config_id = result[0]
        logger.info(f"Created portfolio config {config_id}: ${portfolio_value:,.2f}, {risk_tolerance} risk")
        return config_id

    def get_active_config(self) -> Optional[Dict[str, Any]]:
        """Get the currently active portfolio configuration."""
        query = "SELECT * FROM portfolio_config WHERE is_active = true ORDER BY created_at DESC LIMIT 1"
        return self.db.execute_dict_query(query, fetch_one=True)

    def update_config(
        self,
        config_id: int,
        portfolio_value: Decimal = None,
        max_position_pct: Decimal = None,
        risk_tolerance: str = None,
        cash_reserve_pct: Decimal = None,
        sector_limits: Dict[str, float] = None,
        notes: str = None
    ):
        """Update portfolio configuration."""
        updates = []
        params = []

        if portfolio_value is not None:
            updates.append("portfolio_value = %s")
            params.append(portfolio_value)
        if max_position_pct is not None:
            updates.append("max_position_pct = %s")
            params.append(max_position_pct)
        if risk_tolerance is not None:
            updates.append("risk_tolerance = %s")
            params.append(risk_tolerance)
        if cash_reserve_pct is not None:
            updates.append("cash_reserve_pct = %s")
            params.append(cash_reserve_pct)
        if sector_limits is not None:
            import json
            updates.append("sector_limits = %s::jsonb")
            params.append(json.dumps(sector_limits))
        if notes is not None:
            updates.append("notes = %s")
            params.append(notes)

        if not updates:
            return

        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(config_id)

        query = f"""
            UPDATE portfolio_config
            SET {', '.join(updates)}
            WHERE config_id = %s
        """
        self.db.execute_query(query, tuple(params), fetch=False)
        logger.info(f"Updated portfolio config {config_id}")

    # ========================================================================
    # POSITION RECOMMENDATIONS
    # ========================================================================

    def store_position_recommendation(
        self,
        analysis_id: int,
        ticker_id: int,
        recommended_shares: int,
        recommended_amount: Decimal,
        position_size_pct: Decimal,
        entry_price: Decimal,
        target_price: Decimal = None,
        stop_loss: Decimal = None,
        expected_return_pct: Decimal = None,
        expected_timeframe_days: int = None,
        risk_reward_ratio: Decimal = None,
        timing_recommendation: str = 'BUY_NOW',
        ideal_entry_min: Decimal = None,
        ideal_entry_max: Decimal = None,
        timing_reasoning: str = None,
        sizing_reasoning: str = None
    ) -> int:
        """
        Store a position sizing recommendation.

        Args:
            analysis_id: Reference to analysis that generated this
            ticker_id: Stock ticker ID
            recommended_shares: Number of shares to buy
            recommended_amount: Dollar amount to invest
            position_size_pct: Position size as % of portfolio
            entry_price: Current/recommended entry price
            target_price: Price target
            stop_loss: Stop loss price
            expected_return_pct: Expected return percentage
            expected_timeframe_days: Expected holding period
            risk_reward_ratio: Risk/reward ratio
            timing_recommendation: 'BUY_NOW', 'WAIT_FOR_DIP', 'WAIT_FOR_BREAKOUT', 'WAIT'
            ideal_entry_min: Ideal entry price minimum
            ideal_entry_max: Ideal entry price maximum
            timing_reasoning: Explanation of timing
            sizing_reasoning: Explanation of position sizing

        Returns:
            recommendation_id
        """
        query = """
            INSERT INTO position_recommendations (
                analysis_id, ticker_id, recommended_shares, recommended_amount,
                position_size_pct, entry_price, target_price, stop_loss,
                expected_return_pct, expected_timeframe_days, risk_reward_ratio,
                timing_recommendation, ideal_entry_min, ideal_entry_max,
                timing_reasoning, sizing_reasoning
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING recommendation_id
        """

        result = self.db.execute_query(
            query,
            (
                analysis_id, ticker_id, recommended_shares, recommended_amount,
                position_size_pct, entry_price, target_price, stop_loss,
                expected_return_pct, expected_timeframe_days, risk_reward_ratio,
                timing_recommendation, ideal_entry_min, ideal_entry_max,
                timing_reasoning, sizing_reasoning
            ),
            fetch_one=True
        )

        recommendation_id = result[0]
        logger.info(f"Stored position recommendation {recommendation_id}: {recommended_shares} shares @ ${entry_price}")
        return recommendation_id

    def get_recent_recommendations(
        self,
        ticker_id: int = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent position recommendations."""
        if ticker_id:
            query = """
                SELECT pr.*, t.symbol, t.company_name, a.analyzed_at
                FROM position_recommendations pr
                JOIN tickers t ON pr.ticker_id = t.ticker_id
                JOIN analyses a ON pr.analysis_id = a.analysis_id
                WHERE pr.ticker_id = %s
                ORDER BY pr.created_at DESC
                LIMIT %s
            """
            params = (ticker_id, limit)
        else:
            query = """
                SELECT pr.*, t.symbol, t.company_name, a.analyzed_at
                FROM position_recommendations pr
                JOIN tickers t ON pr.ticker_id = t.ticker_id
                JOIN analyses a ON pr.analysis_id = a.analysis_id
                ORDER BY pr.created_at DESC
                LIMIT %s
            """
            params = (limit,)

        return self.db.execute_dict_query(query, params)

    # ========================================================================
    # PORTFOLIO HOLDINGS
    # ========================================================================

    def add_holding(
        self,
        ticker_id: int,
        shares: Decimal,
        avg_cost_basis: Decimal,
        acquisition_date: date,
        notes: str = None,
        related_analysis_id: int = None
    ) -> int:
        """
        Add a new holding or update existing one.

        Args:
            ticker_id: Stock ticker ID
            shares: Number of shares
            avg_cost_basis: Average cost per share
            acquisition_date: Date of acquisition
            notes: Optional notes
            related_analysis_id: Reference to analysis that recommended this

        Returns:
            holding_id
        """
        total_cost = shares * avg_cost_basis

        # Check if holding already exists
        existing = self.db.execute_dict_query(
            "SELECT * FROM portfolio_holdings WHERE ticker_id = %s AND is_open = true",
            (ticker_id,),
            fetch_one=True
        )

        if existing:
            # Update existing holding - calculate new average cost
            old_shares = Decimal(str(existing['shares']))
            old_total = Decimal(str(existing['total_cost']))
            new_shares = old_shares + shares
            new_total_cost = old_total + total_cost
            new_avg_cost = new_total_cost / new_shares

            query = """
                UPDATE portfolio_holdings
                SET shares = %s,
                    avg_cost_basis = %s,
                    total_cost = %s,
                    last_updated = CURRENT_TIMESTAMP
                WHERE holding_id = %s
                RETURNING holding_id
            """
            result = self.db.execute_query(
                query,
                (new_shares, new_avg_cost, new_total_cost, existing['holding_id']),
                fetch_one=True
            )
            holding_id = result[0]
            logger.info(f"Updated holding {holding_id}: {new_shares} shares @ ${new_avg_cost:.2f}")
        else:
            # Create new holding
            query = """
                INSERT INTO portfolio_holdings (
                    ticker_id, shares, avg_cost_basis, total_cost,
                    acquisition_date, notes, related_analysis_id, is_open
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, true)
                RETURNING holding_id
            """
            result = self.db.execute_query(
                query,
                (ticker_id, shares, avg_cost_basis, total_cost,
                 acquisition_date, notes, related_analysis_id),
                fetch_one=True
            )
            holding_id = result[0]
            logger.info(f"Added holding {holding_id}: {shares} shares @ ${avg_cost_basis:.2f}")

        return holding_id

    def get_open_holdings(self) -> List[Dict[str, Any]]:
        """Get all open holdings."""
        query = """
            SELECT h.*, t.symbol, t.company_name
            FROM portfolio_holdings h
            JOIN tickers t ON h.ticker_id = t.ticker_id
            WHERE h.is_open = true
            ORDER BY h.total_cost DESC
        """
        return self.db.execute_dict_query(query)

    def get_holding(self, ticker_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific open holding."""
        query = """
            SELECT h.*, t.symbol, t.company_name
            FROM portfolio_holdings h
            JOIN tickers t ON h.ticker_id = t.ticker_id
            WHERE h.ticker_id = %s AND h.is_open = true
        """
        return self.db.execute_dict_query(query, (ticker_id,), fetch_one=True)

    def close_holding(
        self,
        ticker_id: int,
        shares_to_close: Decimal = None
    ) -> int:
        """
        Close a holding (full or partial).

        Args:
            ticker_id: Stock ticker ID
            shares_to_close: Number of shares to close (None = close all)

        Returns:
            holding_id
        """
        holding = self.get_holding(ticker_id)
        if not holding:
            raise ValueError(f"No open holding found for ticker_id {ticker_id}")

        current_shares = Decimal(str(holding['shares']))

        if shares_to_close is None or shares_to_close >= current_shares:
            # Close entire position
            query = """
                UPDATE portfolio_holdings
                SET is_open = false,
                    closed_date = CURRENT_DATE,
                    last_updated = CURRENT_TIMESTAMP
                WHERE holding_id = %s
                RETURNING holding_id
            """
            result = self.db.execute_query(query, (holding['holding_id'],), fetch_one=True)
            logger.info(f"Closed holding {holding['holding_id']}: all {current_shares} shares")
        else:
            # Partial close - reduce shares
            remaining_shares = current_shares - shares_to_close
            avg_cost = Decimal(str(holding['avg_cost_basis']))
            new_total_cost = remaining_shares * avg_cost

            query = """
                UPDATE portfolio_holdings
                SET shares = %s,
                    total_cost = %s,
                    last_updated = CURRENT_TIMESTAMP
                WHERE holding_id = %s
                RETURNING holding_id
            """
            result = self.db.execute_query(
                query,
                (remaining_shares, new_total_cost, holding['holding_id']),
                fetch_one=True
            )
            logger.info(f"Reduced holding {holding['holding_id']}: {shares_to_close} shares sold, {remaining_shares} remaining")

        return result[0]

    # ========================================================================
    # TRADE EXECUTIONS
    # ========================================================================

    def log_trade(
        self,
        ticker_id: int,
        trade_type: str,
        shares: Decimal,
        price: Decimal,
        fees: Decimal = Decimal('0'),
        execution_date: datetime = None,
        execution_method: str = 'MARKET',
        related_analysis_id: int = None,
        related_recommendation_id: int = None,
        notes: str = None
    ) -> int:
        """
        Log a trade execution.

        Args:
            ticker_id: Stock ticker ID
            trade_type: 'BUY' or 'SELL'
            shares: Number of shares
            price: Execution price per share
            fees: Trading fees/commissions
            execution_date: Execution timestamp (default: now)
            execution_method: 'MARKET', 'LIMIT', 'STOP'
            related_analysis_id: Analysis that led to this trade
            related_recommendation_id: Recommendation that led to this trade
            notes: Optional notes

        Returns:
            execution_id
        """
        if execution_date is None:
            execution_date = datetime.now()

        total_value = shares * price

        # Get holding_id if exists
        holding = self.get_holding(ticker_id)
        holding_id = holding['holding_id'] if holding else None

        query = """
            INSERT INTO trade_executions (
                ticker_id, trade_type, shares, price, total_value, fees,
                execution_date, execution_method, related_analysis_id,
                related_recommendation_id, holding_id, notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING execution_id
        """

        result = self.db.execute_query(
            query,
            (
                ticker_id, trade_type, shares, price, total_value, fees,
                execution_date, execution_method, related_analysis_id,
                related_recommendation_id, holding_id, notes
            ),
            fetch_one=True
        )

        execution_id = result[0]
        logger.info(f"Logged {trade_type} trade {execution_id}: {shares} shares @ ${price:.2f}")

        # Update holdings
        if trade_type == 'BUY':
            self.add_holding(
                ticker_id=ticker_id,
                shares=shares,
                avg_cost_basis=price,
                acquisition_date=execution_date.date(),
                related_analysis_id=related_analysis_id
            )
        elif trade_type == 'SELL':
            self.close_holding(ticker_id, shares)

        return execution_id

    def get_trade_history(
        self,
        ticker_id: int = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get trade execution history."""
        if ticker_id:
            query = """
                SELECT te.*, t.symbol, t.company_name
                FROM trade_executions te
                JOIN tickers t ON te.ticker_id = t.ticker_id
                WHERE te.ticker_id = %s
                ORDER BY te.execution_date DESC
                LIMIT %s
            """
            params = (ticker_id, limit)
        else:
            query = """
                SELECT te.*, t.symbol, t.company_name
                FROM trade_executions te
                JOIN tickers t ON te.ticker_id = t.ticker_id
                ORDER BY te.execution_date DESC
                LIMIT %s
            """
            params = (limit,)

        return self.db.execute_dict_query(query, params)

    # ========================================================================
    # PERFORMANCE SNAPSHOTS
    # ========================================================================

    def create_snapshot(
        self,
        snapshot_date: date = None,
        total_value: Decimal = None,
        cash_balance: Decimal = None,
        invested_value: Decimal = None,
        total_cost_basis: Decimal = None,
        unrealized_gains: Decimal = None,
        unrealized_gains_pct: Decimal = None,
        realized_gains_ytd: Decimal = None,
        dividend_income_ytd: Decimal = None,
        portfolio_return_pct: Decimal = None,
        sp500_return_pct: Decimal = None,
        alpha: Decimal = None,
        beta: Decimal = None,
        sharpe_ratio: Decimal = None,
        max_drawdown_pct: Decimal = None
    ) -> int:
        """
        Create a performance snapshot.

        Args:
            snapshot_date: Date of snapshot (default: today)
            total_value: Total portfolio value
            cash_balance: Cash on hand
            invested_value: Value of positions
            total_cost_basis: Total cost basis of positions
            unrealized_gains: Unrealized gains/losses
            unrealized_gains_pct: Unrealized gains as percentage
            realized_gains_ytd: Realized gains year-to-date
            dividend_income_ytd: Dividend income year-to-date
            portfolio_return_pct: Portfolio return percentage
            sp500_return_pct: S&P 500 return for comparison
            alpha: Excess return vs S&P 500
            beta: Portfolio beta
            sharpe_ratio: Sharpe ratio
            max_drawdown_pct: Maximum drawdown percentage

        Returns:
            snapshot_id
        """
        if snapshot_date is None:
            snapshot_date = date.today()

        query = """
            INSERT INTO performance_snapshots (
                snapshot_date, total_value, cash_balance, invested_value,
                total_cost_basis, unrealized_gains, unrealized_gains_pct,
                realized_gains_ytd, dividend_income_ytd, portfolio_return_pct,
                sp500_return_pct, alpha, beta, sharpe_ratio, max_drawdown_pct
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (snapshot_date) DO UPDATE
            SET total_value = EXCLUDED.total_value,
                cash_balance = EXCLUDED.cash_balance,
                invested_value = EXCLUDED.invested_value,
                total_cost_basis = EXCLUDED.total_cost_basis,
                unrealized_gains = EXCLUDED.unrealized_gains,
                unrealized_gains_pct = EXCLUDED.unrealized_gains_pct,
                realized_gains_ytd = EXCLUDED.realized_gains_ytd,
                dividend_income_ytd = EXCLUDED.dividend_income_ytd,
                portfolio_return_pct = EXCLUDED.portfolio_return_pct,
                sp500_return_pct = EXCLUDED.sp500_return_pct,
                alpha = EXCLUDED.alpha,
                beta = EXCLUDED.beta,
                sharpe_ratio = EXCLUDED.sharpe_ratio,
                max_drawdown_pct = EXCLUDED.max_drawdown_pct
            RETURNING snapshot_id
        """

        result = self.db.execute_query(
            query,
            (
                snapshot_date, total_value, cash_balance, invested_value,
                total_cost_basis, unrealized_gains, unrealized_gains_pct,
                realized_gains_ytd, dividend_income_ytd, portfolio_return_pct,
                sp500_return_pct, alpha, beta, sharpe_ratio, max_drawdown_pct
            ),
            fetch_one=True
        )

        snapshot_id = result[0]
        logger.info(f"Created performance snapshot {snapshot_id} for {snapshot_date}")
        return snapshot_id

    def get_snapshots(
        self,
        start_date: date = None,
        end_date: date = None,
        limit: int = 30
    ) -> List[Dict[str, Any]]:
        """Get performance snapshots."""
        if start_date and end_date:
            query = """
                SELECT * FROM performance_snapshots
                WHERE snapshot_date BETWEEN %s AND %s
                ORDER BY snapshot_date DESC
            """
            params = (start_date, end_date)
        elif start_date:
            query = """
                SELECT * FROM performance_snapshots
                WHERE snapshot_date >= %s
                ORDER BY snapshot_date DESC
                LIMIT %s
            """
            params = (start_date, limit)
        else:
            query = """
                SELECT * FROM performance_snapshots
                ORDER BY snapshot_date DESC
                LIMIT %s
            """
            params = (limit,)

        return self.db.execute_dict_query(query, params)

    def get_latest_snapshot(self) -> Optional[Dict[str, Any]]:
        """Get the most recent performance snapshot."""
        query = """
            SELECT * FROM performance_snapshots
            ORDER BY snapshot_date DESC
            LIMIT 1
        """
        return self.db.execute_dict_query(query, fetch_one=True)

    # ========================================================================
    # DIVIDEND TRACKING
    # ========================================================================

    def record_dividend_payment(
        self,
        ticker_id: int,
        ex_dividend_date: date,
        payment_date: date,
        dividend_per_share: Decimal,
        dividend_type: str = 'REGULAR',
        record_date: date = None,
        notes: str = None
    ) -> int:
        """
        Record a dividend payment announcement.

        Args:
            ticker_id: Stock ticker ID
            ex_dividend_date: Ex-dividend date (must own by this date)
            payment_date: Payment date
            dividend_per_share: Dividend amount per share
            dividend_type: REGULAR, SPECIAL, or RETURN_OF_CAPITAL
            record_date: Record date (optional)
            notes: Optional notes

        Returns:
            dividend_id
        """
        query = """
            INSERT INTO dividend_payments (
                ticker_id, ex_dividend_date, payment_date, dividend_per_share,
                dividend_type, record_date, status, notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, 'ANNOUNCED', %s)
            ON CONFLICT (ticker_id, ex_dividend_date) DO UPDATE
            SET payment_date = EXCLUDED.payment_date,
                dividend_per_share = EXCLUDED.dividend_per_share,
                dividend_type = EXCLUDED.dividend_type,
                record_date = EXCLUDED.record_date,
                notes = EXCLUDED.notes,
                updated_at = CURRENT_TIMESTAMP
            RETURNING dividend_id
        """

        result = self.db.execute_query(
            query,
            (ticker_id, ex_dividend_date, payment_date, dividend_per_share,
             dividend_type, record_date, notes),
            fetch_one=True
        )

        dividend_id = result[0]
        logger.info(f"Recorded dividend {dividend_id}: ${dividend_per_share} per share on {payment_date}")
        return dividend_id

    def track_dividend_for_holding(
        self,
        holding_id: int,
        dividend_id: int,
        qualified_dividend: bool = True
    ) -> int:
        """
        Track a dividend payment for a specific holding.

        Args:
            holding_id: Holding ID
            dividend_id: Dividend payment ID
            qualified_dividend: Whether dividend qualifies for tax benefits

        Returns:
            history_id
        """
        # Get holding details
        holding = self.db.execute_dict_query(
            "SELECT * FROM portfolio_holdings WHERE holding_id = %s",
            (holding_id,),
            fetch_one=True
        )

        if not holding:
            raise ValueError(f"Holding {holding_id} not found")

        # Get dividend details
        dividend = self.db.execute_dict_query(
            "SELECT * FROM dividend_payments WHERE dividend_id = %s",
            (dividend_id,),
            fetch_one=True
        )

        if not dividend:
            raise ValueError(f"Dividend {dividend_id} not found")

        shares_held = Decimal(str(holding['shares']))
        dividend_per_share = Decimal(str(dividend['dividend_per_share']))
        total_amount = shares_held * dividend_per_share

        query = """
            INSERT INTO dividend_history (
                holding_id, dividend_id, shares_held, dividend_per_share,
                total_amount, ex_dividend_date, payment_date,
                qualified_dividend, status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'PENDING')
            RETURNING history_id
        """

        result = self.db.execute_query(
            query,
            (holding_id, dividend_id, shares_held, dividend_per_share,
             total_amount, dividend['ex_dividend_date'], dividend['payment_date'],
             qualified_dividend),
            fetch_one=True
        )

        history_id = result[0]
        logger.info(f"Tracked dividend for holding {holding_id}: ${total_amount:.2f}")
        return history_id

    def mark_dividend_received(
        self,
        history_id: int,
        received_date: date = None,
        tax_withheld: Decimal = Decimal('0')
    ):
        """
        Mark a dividend as received.

        Args:
            history_id: Dividend history ID
            received_date: Date received (default: today)
            tax_withheld: Tax withheld amount
        """
        if received_date is None:
            received_date = date.today()

        query = """
            UPDATE dividend_history
            SET status = 'RECEIVED',
                received_date = %s,
                tax_withheld = %s
            WHERE history_id = %s
        """
        self.db.execute_query(query, (received_date, tax_withheld, history_id), fetch=False)
        logger.info(f"Marked dividend {history_id} as received")

    def get_upcoming_dividends(
        self,
        days_ahead: int = 30
    ) -> List[Dict[str, Any]]:
        """Get upcoming dividend payments."""
        query = """
            SELECT dp.*, t.symbol, t.company_name,
                   h.holding_id, h.shares,
                   (h.shares * dp.dividend_per_share) as expected_amount
            FROM dividend_payments dp
            JOIN tickers t ON dp.ticker_id = t.ticker_id
            LEFT JOIN portfolio_holdings h ON dp.ticker_id = h.ticker_id AND h.is_open = true
            WHERE dp.payment_date >= CURRENT_DATE
              AND dp.payment_date <= CURRENT_DATE + INTERVAL '%s days'
              AND dp.status IN ('ANNOUNCED', 'PENDING')
            ORDER BY dp.payment_date
        """
        return self.db.execute_dict_query(query, (days_ahead,))

    def get_dividend_history(
        self,
        ticker_id: int = None,
        start_date: date = None,
        end_date: date = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get dividend payment history."""
        conditions = []
        params = []

        if ticker_id:
            conditions.append("h.ticker_id = %s")
            params.append(ticker_id)

        if start_date:
            conditions.append("dh.payment_date >= %s")
            params.append(start_date)

        if end_date:
            conditions.append("dh.payment_date <= %s")
            params.append(end_date)

        where_clause = " AND " + " AND ".join(conditions) if conditions else ""

        query = f"""
            SELECT dh.*, t.symbol, t.company_name, h.shares
            FROM dividend_history dh
            JOIN portfolio_holdings h ON dh.holding_id = h.holding_id
            JOIN tickers t ON h.ticker_id = t.ticker_id
            WHERE 1=1 {where_clause}
            ORDER BY dh.payment_date DESC
            LIMIT %s
        """

        params.append(limit)
        return self.db.execute_dict_query(query, tuple(params))

    def get_dividend_income_summary(
        self,
        year: int = None
    ) -> Dict[str, Any]:
        """
        Get dividend income summary for a year.

        Args:
            year: Year to summarize (default: current year)

        Returns:
            Summary with total income, qualified income, taxes, etc.
        """
        if year is None:
            from datetime import datetime
            year = datetime.now().year

        query = """
            SELECT
                COUNT(*) as payment_count,
                SUM(total_amount) as total_income,
                SUM(CASE WHEN qualified_dividend THEN total_amount ELSE 0 END) as qualified_income,
                SUM(CASE WHEN NOT qualified_dividend THEN total_amount ELSE 0 END) as ordinary_income,
                SUM(tax_withheld) as total_tax_withheld
            FROM dividend_history
            WHERE EXTRACT(YEAR FROM payment_date) = %s
              AND status = 'RECEIVED'
        """

        result = self.db.execute_dict_query(query, (year,), fetch_one=True)

        # Get by ticker breakdown
        by_ticker_query = """
            SELECT
                t.symbol,
                t.company_name,
                COUNT(*) as payment_count,
                SUM(dh.total_amount) as total_income
            FROM dividend_history dh
            JOIN portfolio_holdings h ON dh.holding_id = h.holding_id
            JOIN tickers t ON h.ticker_id = t.ticker_id
            WHERE EXTRACT(YEAR FROM dh.payment_date) = %s
              AND dh.status = 'RECEIVED'
            GROUP BY t.ticker_id, t.symbol, t.company_name
            ORDER BY total_income DESC
        """

        by_ticker = self.db.execute_dict_query(by_ticker_query, (year,))

        return {
            'year': year,
            'total_income': result.get('total_income') or Decimal('0'),
            'qualified_income': result.get('qualified_income') or Decimal('0'),
            'ordinary_income': result.get('ordinary_income') or Decimal('0'),
            'total_tax_withheld': result.get('total_tax_withheld') or Decimal('0'),
            'payment_count': result.get('payment_count') or 0,
            'by_ticker': by_ticker
        }

    # ========================================================================
    # PORTFOLIO MANAGEMENT (CLI compatibility methods)
    # ========================================================================

    def get_portfolio(self, portfolio_id: int) -> Optional[Dict[str, Any]]:
        """Get portfolio summary (for CLI compatibility)."""
        query = "SELECT * FROM portfolios WHERE portfolio_id = %s"
        return self.db.execute_dict_query(query, (portfolio_id,), fetch_one=True)

    def get_positions(self, portfolio_id: int) -> List[Dict[str, Any]]:
        """Get current positions for a portfolio (for CLI compatibility)."""
        # Check if current_price column exists by querying information_schema
        # If it doesn't exist, use fallback query without current_price
        check_column_query = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'portfolio_holdings' AND column_name = 'current_price'
        """
        has_current_price = self.db.execute_dict_query(check_column_query, (), fetch_one=True)
        
        if has_current_price:
            # Use query with current_price (migration 005 schema)
            query = """
                SELECT
                    pp.*,
                    t.symbol,
                    t.company_name,
                    pp.current_price,
                    (pp.shares * COALESCE(pp.current_price, pp.avg_cost_basis)) as current_value,
                    ((pp.shares * COALESCE(pp.current_price, pp.avg_cost_basis)) - (pp.shares * pp.avg_cost_basis)) as unrealized_gain_loss,
                    (((pp.shares * COALESCE(pp.current_price, pp.avg_cost_basis)) - (pp.shares * pp.avg_cost_basis)) / (pp.shares * pp.avg_cost_basis) * 100) as unrealized_gain_loss_pct
                FROM portfolio_holdings pp
                JOIN tickers t ON pp.ticker_id = t.ticker_id
                WHERE pp.is_open = true
                ORDER BY (pp.shares * COALESCE(pp.current_price, pp.avg_cost_basis)) DESC
            """
        else:
            # Fallback: use avg_cost_basis as current_price (migration 001 schema)
            query = """
                SELECT
                    pp.*,
                    t.symbol,
                    t.company_name,
                    pp.avg_cost_basis as current_price,
                    (pp.shares * pp.avg_cost_basis) as current_value,
                    0 as unrealized_gain_loss,
                    0 as unrealized_gain_loss_pct
                FROM portfolio_holdings pp
                JOIN tickers t ON pp.ticker_id = t.ticker_id
                WHERE pp.is_open = true
                ORDER BY (pp.shares * pp.avg_cost_basis) DESC
            """
        
        return self.db.execute_dict_query(query, ())

    def record_transaction(
        self,
        portfolio_id: int,
        ticker_id: int,
        transaction_type: str,
        transaction_date: date,
        shares: Decimal,
        price_per_share: Decimal,
        fees: Decimal = Decimal('0'),
        notes: str = None
    ) -> int:
        """Record a buy/sell transaction (for CLI compatibility)."""
        total_value = shares * price_per_share

        query = """
            INSERT INTO portfolio_transactions (
                portfolio_id, ticker_id, transaction_type, transaction_date,
                shares, price_per_share, total_value, fees, notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING transaction_id
        """

        result = self.db.execute_query(
            query,
            (portfolio_id, ticker_id, transaction_type, transaction_date,
             shares, price_per_share, total_value, fees, notes),
            fetch_one=True
        )

        transaction_id = result[0]
        logger.info(f"Recorded {transaction_type} transaction {transaction_id}: {shares} shares @ ${price_per_share}")

        # Update portfolio positions
        self._update_portfolio_position(portfolio_id, ticker_id, transaction_type, shares, price_per_share, transaction_date)

        # Update portfolio totals
        self._update_portfolio_totals(portfolio_id)

        return transaction_id

    def _update_portfolio_position(
        self,
        portfolio_id: int,
        ticker_id: int,
        transaction_type: str,
        shares: Decimal,
        price: Decimal,
        transaction_date: date
    ):
        """Update or create portfolio position after a transaction."""
        # Get existing position
        existing = self.db.execute_dict_query(
            """SELECT * FROM portfolio_holdings
               WHERE ticker_id = %s AND is_open = true""",
            (ticker_id,),
            fetch_one=True
        )

        if transaction_type == 'BUY':
            if existing:
                # Update existing position
                old_shares = Decimal(str(existing['shares']))
                old_avg_cost = Decimal(str(existing['avg_cost_basis']))

                new_shares = old_shares + shares
                new_avg_cost = ((old_shares * old_avg_cost) + (shares * price)) / new_shares

                self.db.execute_query(
                    """UPDATE portfolio_holdings
                       SET shares = %s, avg_cost_basis = %s, current_price = %s, updated_at = CURRENT_TIMESTAMP
                       WHERE holding_id = %s""",
                    (new_shares, new_avg_cost, price, existing['holding_id']),
                    fetch=False
                )
            else:
                # Create new position
                self.db.execute_query(
                    """INSERT INTO portfolio_holdings
                       (ticker_id, shares, avg_cost_basis, current_price, acquisition_date, is_open)
                       VALUES (%s, %s, %s, %s, %s, true)""",
                    (ticker_id, shares, price, price, transaction_date),
                    fetch=False
                )

        elif transaction_type == 'SELL':
            if existing:
                old_shares = Decimal(str(existing['shares']))
                remaining_shares = old_shares - shares

                if remaining_shares > 0:
                    # Partial sell
                    self.db.execute_query(
                        """UPDATE portfolio_holdings
                           SET shares = %s, current_price = %s, updated_at = CURRENT_TIMESTAMP
                           WHERE holding_id = %s""",
                        (remaining_shares, price, existing['holding_id']),
                        fetch=False
                    )
                else:
                    # Full sell - close position
                    self.db.execute_query(
                        """UPDATE portfolio_holdings
                           SET is_open = false, closed_date = %s, current_price = %s, updated_at = CURRENT_TIMESTAMP
                           WHERE holding_id = %s""",
                        (transaction_date, price, existing['holding_id']),
                        fetch=False
                    )

    def _update_portfolio_totals(self, portfolio_id: int):
        """Recalculate portfolio total value and cash."""
        # Get all open positions
        positions = self.get_positions(portfolio_id)

        # Calculate total position value
        total_positions_value = sum(
            Decimal(str(p.get('current_value', 0) or 0)) for p in positions
        )

        # Get portfolio to get cash
        portfolio = self.get_portfolio(portfolio_id)
        if portfolio:
            cash = Decimal(str(portfolio.get('current_cash', 0) or 0))
            total_value = cash + total_positions_value

            # Update portfolio
            self.db.execute_query(
                """UPDATE portfolios
                   SET total_value = %s, updated_at = CURRENT_TIMESTAMP
                   WHERE portfolio_id = %s""",
                (total_value, portfolio_id),
                fetch=False
            )

    def create_snapshot(self, portfolio_id: int, snapshot_date: date = None):
        """Create a performance snapshot for a portfolio (for CLI compatibility)."""
        if snapshot_date is None:
            snapshot_date = date.today()

        portfolio = self.get_portfolio(portfolio_id)
        if not portfolio:
            raise ValueError(f"Portfolio {portfolio_id} not found")

        positions = self.get_positions(portfolio_id)

        total_value = Decimal(str(portfolio.get('total_value', 0) or 0))
        initial_cash = Decimal(str(portfolio.get('initial_cash', 0) or 0))
        current_cash = Decimal(str(portfolio.get('current_cash', 0) or 0))

        # Calculate metrics
        positions_value = sum(Decimal(str(p.get('current_value', 0) or 0)) for p in positions)
        total_gain_loss = total_value - initial_cash
        total_gain_loss_pct = (total_gain_loss / initial_cash * 100) if initial_cash > 0 else Decimal('0')

        # Get previous snapshot for day change
        prev_snapshot = self.db.execute_dict_query(
            """SELECT * FROM portfolio_snapshots
               WHERE portfolio_id = %s AND snapshot_date < %s
               ORDER BY snapshot_date DESC LIMIT 1""",
            (portfolio_id, snapshot_date),
            fetch_one=True
        )

        day_change = Decimal('0')
        if prev_snapshot:
            prev_value = Decimal(str(prev_snapshot.get('total_value', 0) or 0))
            day_change = total_value - prev_value

        # Insert or update snapshot
        query = """
            INSERT INTO portfolio_snapshots (
                portfolio_id, snapshot_date, total_value, cash_balance,
                positions_value, total_gain_loss, total_gain_loss_pct, day_change
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (portfolio_id, snapshot_date)
            DO UPDATE SET
                total_value = EXCLUDED.total_value,
                cash_balance = EXCLUDED.cash_balance,
                positions_value = EXCLUDED.positions_value,
                total_gain_loss = EXCLUDED.total_gain_loss,
                total_gain_loss_pct = EXCLUDED.total_gain_loss_pct,
                day_change = EXCLUDED.day_change,
                updated_at = CURRENT_TIMESTAMP
            RETURNING snapshot_id
        """

        result = self.db.execute_query(
            query,
            (portfolio_id, snapshot_date, total_value, current_cash,
             positions_value, total_gain_loss, total_gain_loss_pct, day_change),
            fetch_one=True
        )

        snapshot_id = result[0]
        logger.info(f"Created snapshot {snapshot_id} for portfolio {portfolio_id} on {snapshot_date}")
        return snapshot_id

    def get_performance_history(self, portfolio_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get performance history for a portfolio (for CLI compatibility)."""
        query = """
            SELECT * FROM portfolio_snapshots
            WHERE portfolio_id = %s
            ORDER BY snapshot_date DESC
            LIMIT %s
        """
        return self.db.execute_dict_query(query, (portfolio_id, days))

    def get_upcoming_dividends(self, portfolio_id: int, days: int = 90) -> List[Dict[str, Any]]:
        """Get upcoming dividends for portfolio positions (for CLI compatibility)."""
        # This is a simplified version - would need dividend data in the database
        query = """
            SELECT
                t.symbol,
                pp.shares as shares_held,
                0.50 as dividend_per_share,
                (pp.shares * 0.50) as total_dividend,
                CURRENT_DATE + INTERVAL '30 days' as payment_date
            FROM portfolio_holdings pp
            JOIN tickers t ON pp.ticker_id = t.ticker_id
            WHERE pp.is_open = true
            ORDER BY t.symbol
            LIMIT 5
        """
        return self.db.execute_dict_query(query, (portfolio_id,))
