#!/usr/bin/env python3
# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Database Initialization Script

Initialize the Investment Intelligence System database with an initial watchlist.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tradingagents.database import TickerOperations
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Initial watchlist: Mix of sectors for diversification
INITIAL_WATCHLIST = [
    # Technology
    {
        'symbol': 'NVDA',
        'company_name': 'NVIDIA Corporation',
        'sector': 'Technology',
        'industry': 'Semiconductors',
        'priority_tier': 1,
        'tags': ['AI', 'high-growth', 'semiconductors']
    },
    {
        'symbol': 'MSFT',
        'company_name': 'Microsoft Corporation',
        'sector': 'Technology',
        'industry': 'Software',
        'priority_tier': 1,
        'tags': ['AI', 'cloud', 'large-cap']
    },
    {
        'symbol': 'AAPL',
        'company_name': 'Apple Inc.',
        'sector': 'Technology',
        'industry': 'Consumer Electronics',
        'priority_tier': 1,
        'tags': ['consumer', 'large-cap', 'dividend']
    },
    {
        'symbol': 'GOOGL',
        'company_name': 'Alphabet Inc.',
        'sector': 'Technology',
        'industry': 'Internet Services',
        'priority_tier': 1,
        'tags': ['AI', 'advertising', 'large-cap']
    },
    {
        'symbol': 'META',
        'company_name': 'Meta Platforms Inc.',
        'sector': 'Technology',
        'industry': 'Social Media',
        'priority_tier': 1,
        'tags': ['AI', 'advertising', 'metaverse']
    },
    {
        'symbol': 'AMD',
        'company_name': 'Advanced Micro Devices Inc.',
        'sector': 'Technology',
        'industry': 'Semiconductors',
        'priority_tier': 1,
        'tags': ['AI', 'semiconductors', 'gaming']
    },

    # Finance
    {
        'symbol': 'JPM',
        'company_name': 'JPMorgan Chase & Co.',
        'sector': 'Finance',
        'industry': 'Banking',
        'priority_tier': 2,
        'tags': ['banking', 'large-cap', 'dividend']
    },
    {
        'symbol': 'V',
        'company_name': 'Visa Inc.',
        'sector': 'Finance',
        'industry': 'Payment Processing',
        'priority_tier': 1,
        'tags': ['fintech', 'payments', 'large-cap']
    },

    # Healthcare
    {
        'symbol': 'UNH',
        'company_name': 'UnitedHealth Group Inc.',
        'sector': 'Healthcare',
        'industry': 'Healthcare Insurance',
        'priority_tier': 2,
        'tags': ['healthcare', 'large-cap']
    },
    {
        'symbol': 'LLY',
        'company_name': 'Eli Lilly and Company',
        'sector': 'Healthcare',
        'industry': 'Pharmaceuticals',
        'priority_tier': 1,
        'tags': ['healthcare', 'pharmaceuticals', 'biotech']
    },

    # Consumer
    {
        'symbol': 'AMZN',
        'company_name': 'Amazon.com Inc.',
        'sector': 'Consumer Cyclical',
        'industry': 'E-commerce',
        'priority_tier': 1,
        'tags': ['e-commerce', 'cloud', 'large-cap']
    },
    {
        'symbol': 'TSLA',
        'company_name': 'Tesla Inc.',
        'sector': 'Consumer Cyclical',
        'industry': 'Automotive',
        'priority_tier': 1,
        'tags': ['EV', 'automotive', 'high-growth']
    },
    {
        'symbol': 'HD',
        'company_name': 'The Home Depot Inc.',
        'sector': 'Consumer Cyclical',
        'industry': 'Home Improvement Retail',
        'priority_tier': 2,
        'tags': ['retail', 'dividend', 'large-cap']
    },

    # Industrial
    {
        'symbol': 'CAT',
        'company_name': 'Caterpillar Inc.',
        'sector': 'Industrial',
        'industry': 'Construction Equipment',
        'priority_tier': 2,
        'tags': ['industrial', 'construction', 'dividend']
    },

    # Energy
    {
        'symbol': 'XOM',
        'company_name': 'Exxon Mobil Corporation',
        'sector': 'Energy',
        'industry': 'Oil & Gas',
        'priority_tier': 2,
        'tags': ['energy', 'oil', 'dividend']
    },

    # Communication
    {
        'symbol': 'DIS',
        'company_name': 'The Walt Disney Company',
        'sector': 'Communication',
        'industry': 'Entertainment',
        'priority_tier': 2,
        'tags': ['entertainment', 'streaming', 'media']
    },
]


def main():
    """Initialize the database with the initial watchlist."""
    logger.info("="*70)
    logger.info("Investment Intelligence System - Database Initialization")
    logger.info("="*70)

    try:
        # Initialize ticker operations
        ticker_ops = TickerOperations()

        # Check if watchlist already has tickers
        existing = ticker_ops.get_all_tickers()

        if existing:
            logger.warning(f"Database already contains {len(existing)} tickers")
            response = input("Do you want to add the initial watchlist anyway? (y/n): ")
            if response.lower() != 'y':
                logger.info("Initialization cancelled")
                return

        # Add tickers
        logger.info(f"\nAdding {len(INITIAL_WATCHLIST)} tickers to watchlist...")

        added = 0
        skipped = 0

        for ticker_data in INITIAL_WATCHLIST:
            try:
                symbol = ticker_data['symbol']

                # Check if ticker already exists
                if ticker_ops.get_ticker(symbol=symbol):
                    logger.info(f"  ⊙ {symbol} - Already exists, skipping")
                    skipped += 1
                    continue

                ticker_id = ticker_ops.add_ticker(**ticker_data)
                logger.info(f"  ✓ {symbol} - Added (ID: {ticker_id})")
                added += 1

            except Exception as e:
                logger.error(f"  ✗ {ticker_data['symbol']} - Error: {e}")

        # Show summary
        logger.info("\n" + "="*70)
        logger.info("Initialization Summary")
        logger.info("="*70)
        logger.info(f"Tickers added: {added}")
        logger.info(f"Tickers skipped: {skipped}")

        # Get and display watchlist summary
        summary = ticker_ops.get_watchlist_summary()
        logger.info(f"\nTotal tickers in watchlist: {summary.get('active_tickers', 0)}")
        logger.info(f"High priority: {summary.get('high_priority', 0)}")
        logger.info(f"Medium priority: {summary.get('medium_priority', 0)}")
        logger.info(f"Sectors represented: {summary.get('sectors_count', 0)}")

        if summary.get('sectors'):
            logger.info("\nSector breakdown:")
            for sector_info in summary['sectors']:
                logger.info(f"  - {sector_info['sector']}: {sector_info['count']} tickers")

        logger.info("\n" + "="*70)
        logger.info("Database initialized successfully!")
        logger.info("="*70)

        # Display next steps
        logger.info("\nNext Steps:")
        logger.info("1. Backfill historical price data: python scripts/backfill_prices.py")
        logger.info("2. Run daily screener: python -m tradingagents.screener run")
        logger.info("3. Analyze a ticker: python -m tradingagents.analyze NVDA")

    except Exception as e:
        logger.error(f"\nError during initialization: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
