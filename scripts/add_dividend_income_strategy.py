#!/usr/bin/env python3
# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Add Dividend Income Strategy to Database

This script adds the "Dividend Income" strategy to the trading_strategies table.
This strategy is designed for investors who want to live off dividend income.
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tradingagents.database import get_db_connection


def add_dividend_income_strategy():
    """Add the Dividend Income strategy to the database."""

    db = get_db_connection()

    # Strategy configuration
    strategy_name = "Dividend Income"
    strategy_description = """
    Dividend Income strategy for living off dividends.

    This strategy identifies stocks with high, sustainable dividend yields suitable
    for generating passive income. Perfect for retirees or investors seeking
    regular income from their portfolio.

    Key Focus Areas:
    - High dividend yield (4%+ preferred, 3%+ minimum)
    - Dividend safety (payout ratio < 80%)
    - Dividend consistency (5+ years of consecutive payments)
    - Dividend growth (to keep up with inflation)
    - Financial stability (profitable, manageable debt)
    - Price stability (lower volatility to preserve capital)

    Scoring System (0-100):
    - Yield Score (30%): Based on dividend yield
    - Safety Score (25%): Based on payout ratio and financial health
    - Consistency Score (20%): Based on consecutive years paying dividends
    - Growth Score (15%): Based on dividend growth rate
    - Stability Score (10%): Based on price volatility

    Ideal For:
    - Retirement income
    - Passive income generation
    - Conservative investors
    - Long-term buy-and-hold investors
    """.strip()

    indicator_combination = {
        "dividend_yield": True,
        "payout_ratio": True,
        "consecutive_years_paid": True,
        "dividend_growth": True,
        "price_volatility": True,
        "pe_ratio": True,
        "debt_to_equity": True,
    }

    gate_thresholds = {
        "min_dividend_yield": 0.025,  # 2.5% minimum
        "preferred_dividend_yield": 0.04,  # 4% preferred
        "max_payout_ratio": 0.80,  # 80% maximum
        "min_consecutive_years": 3,
        "preferred_consecutive_years": 10,
        "min_income_score": 60,  # Minimum score to recommend
    }

    # Check if strategy already exists
    check_query = """
        SELECT strategy_id, strategy_version
        FROM trading_strategies
        WHERE strategy_name = %s
        ORDER BY strategy_version DESC
        LIMIT 1
    """

    existing = db.execute_dict_query(check_query, (strategy_name,))

    if existing:
        print(f"Strategy '{strategy_name}' already exists (ID: {existing[0]['strategy_id']}, Version: {existing[0]['strategy_version']})")
        print("Updating strategy...")

        update_query = """
            UPDATE trading_strategies
            SET
                strategy_description = %s,
                indicator_combination = %s,
                gate_thresholds = %s,
                holding_period_days = %s,
                updated_at = CURRENT_TIMESTAMP,
                last_backtest_date = NULL  -- Needs new backtest after update
            WHERE strategy_name = %s
                AND strategy_version = %s
            RETURNING strategy_id
        """

        result = db.execute_dict_query(
            update_query,
            (
                strategy_description,
                json.dumps(indicator_combination),
                json.dumps(gate_thresholds),
                1825,  # 5 years holding period
                strategy_name,
                existing[0]['strategy_version']
            )
        )

        if result:
            print(f"✓ Strategy updated successfully (ID: {result[0]['strategy_id']})")
        else:
            print("✗ Failed to update strategy")
            return False

    else:
        print(f"Adding new strategy: '{strategy_name}'")

        insert_query = """
            INSERT INTO trading_strategies (
                strategy_name,
                strategy_description,
                strategy_version,
                indicator_combination,
                gate_thresholds,
                sector_focus,
                min_confidence,
                holding_period_days,
                is_active,
                is_validated
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING strategy_id
        """

        # No specific sector focus for dividend income - can be any sector
        sector_focus = None

        result = db.execute_dict_query(
            insert_query,
            (
                strategy_name,
                strategy_description,
                1,  # Version 1
                json.dumps(indicator_combination),
                json.dumps(gate_thresholds),
                sector_focus,
                60,  # Minimum confidence score
                1825,  # 5 years holding period (365 * 5)
                True,  # is_active
                False  # is_validated - needs backtesting
            )
        )

        if result:
            strategy_id = result[0]['strategy_id']
            print(f"✓ Strategy added successfully (ID: {strategy_id})")

            # Add initial metadata
            print("\nStrategy Details:")
            print(f"  Name: {strategy_name}")
            print(f"  Version: 1")
            print(f"  Min Dividend Yield: {gate_thresholds['min_dividend_yield'] * 100:.1f}%")
            print(f"  Preferred Dividend Yield: {gate_thresholds['preferred_dividend_yield'] * 100:.1f}%")
            print(f"  Min Consecutive Years: {gate_thresholds['min_consecutive_years']}")
            print(f"  Min Income Score: {gate_thresholds['min_income_score']}")
            print(f"  Holding Period: 5+ years")
            print(f"  Status: Active (needs backtesting)")
        else:
            print("✗ Failed to add strategy")
            return False

    print("\n✓ Dividend Income strategy is now available in the database!")
    print("\nYou can use it by running:")
    print("  ./quick_run.sh dividend-income")
    print("  ./quick_run.sh dividend-income --details")
    print("  ./quick_run.sh dividend-income --top 10")

    return True


if __name__ == "__main__":
    try:
        success = add_dividend_income_strategy()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
