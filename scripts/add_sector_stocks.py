#!/usr/bin/env python3
"""
Bulk Stock Import Script
Add 110 stocks across all 11 market sectors for comprehensive sector analysis
"""

import sys
import os
import logging
from typing import List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents.database import DatabaseConnection
from tradingagents.screener.sector_models import SECTORS

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


# Comprehensive stock list by sector
SECTOR_STOCKS = {
    'Technology': [
        ('AAPL', 'Apple Inc.'),
        ('MSFT', 'Microsoft Corporation'),
        ('GOOGL', 'Alphabet Inc.'),
        ('NVDA', 'NVIDIA Corporation'),
        ('META', 'Meta Platforms Inc.'),
        ('AVGO', 'Broadcom Inc.'),
        ('ADBE', 'Adobe Inc.'),
        ('CRM', 'Salesforce Inc.'),
        ('ORCL', 'Oracle Corporation'),
        ('AMD', 'Advanced Micro Devices'),
    ],
    'Healthcare': [
        ('UNH', 'UnitedHealth Group'),
        ('JNJ', 'Johnson & Johnson'),
        ('LLY', 'Eli Lilly and Company'),
        ('ABBV', 'AbbVie Inc.'),
        ('MRK', 'Merck & Co.'),
        ('TMO', 'Thermo Fisher Scientific'),
        ('ABT', 'Abbott Laboratories'),
        ('DHR', 'Danaher Corporation'),
        ('PFE', 'Pfizer Inc.'),
        ('BMY', 'Bristol-Myers Squibb'),
    ],
    'Financial Services': [
        ('BRK.B', 'Berkshire Hathaway'),
        ('JPM', 'JPMorgan Chase & Co.'),
        ('V', 'Visa Inc.'),
        ('MA', 'Mastercard Inc.'),
        ('BAC', 'Bank of America'),
        ('WFC', 'Wells Fargo & Company'),
        ('GS', 'Goldman Sachs Group'),
        ('MS', 'Morgan Stanley'),
        ('SPGI', 'S&P Global Inc.'),
        ('AXP', 'American Express'),
    ],
    'Consumer Cyclical': [
        ('AMZN', 'Amazon.com Inc.'),
        ('TSLA', 'Tesla Inc.'),
        ('HD', 'Home Depot Inc.'),
        ('MCD', 'McDonald\'s Corporation'),
        ('NKE', 'Nike Inc.'),
        ('SBUX', 'Starbucks Corporation'),
        ('LOW', 'Lowe\'s Companies'),
        ('TGT', 'Target Corporation'),
        ('TJX', 'TJX Companies'),
        ('BKNG', 'Booking Holdings'),
    ],
    'Communication': [
        ('NFLX', 'Netflix Inc.'),
        ('DIS', 'Walt Disney Company'),
        ('CMCSA', 'Comcast Corporation'),
        ('VZ', 'Verizon Communications'),
        ('T', 'AT&T Inc.'),
        ('TMUS', 'T-Mobile US'),
        ('EA', 'Electronic Arts'),
        ('CHTR', 'Charter Communications'),
        ('TTWO', 'Take-Two Interactive'),
        ('PARA', 'Paramount Global'),
    ],
    'Industrials': [
        ('CAT', 'Caterpillar Inc.'),
        ('UPS', 'United Parcel Service'),
        ('HON', 'Honeywell International'),
        ('BA', 'Boeing Company'),
        ('RTX', 'RTX Corporation'),
        ('UNP', 'Union Pacific'),
        ('GE', 'General Electric'),
        ('MMM', '3M Company'),
        ('LMT', 'Lockheed Martin'),
        ('DE', 'Deere & Company'),
    ],
    'Consumer Defensive': [
        ('PG', 'Procter & Gamble'),
        ('KO', 'Coca-Cola Company'),
        ('PEP', 'PepsiCo Inc.'),
        ('WMT', 'Walmart Inc.'),
        ('COST', 'Costco Wholesale'),
        ('PM', 'Philip Morris International'),
        ('MO', 'Altria Group'),
        ('CL', 'Colgate-Palmolive'),
        ('MDLZ', 'Mondelez International'),
        ('KMB', 'Kimberly-Clark'),
    ],
    'Energy': [
        ('XOM', 'Exxon Mobil'),
        ('CVX', 'Chevron Corporation'),
        ('COP', 'ConocoPhillips'),
        ('SLB', 'Schlumberger'),
        ('EOG', 'EOG Resources'),
        ('MPC', 'Marathon Petroleum'),
        ('PSX', 'Phillips 66'),
        ('VLO', 'Valero Energy'),
        ('OXY', 'Occidental Petroleum'),
        ('HAL', 'Halliburton Company'),
    ],
    'Utilities': [
        ('NEE', 'NextEra Energy'),
        ('DUK', 'Duke Energy'),
        ('SO', 'Southern Company'),
        ('D', 'Dominion Energy'),
        ('AEP', 'American Electric Power'),
        ('EXC', 'Exelon Corporation'),
        ('SRE', 'Sempra Energy'),
        ('PEG', 'Public Service Enterprise'),
        ('XEL', 'Xcel Energy'),
        ('ED', 'Consolidated Edison'),
    ],
    'Real Estate': [
        ('AMT', 'American Tower'),
        ('PLD', 'Prologis Inc.'),
        ('CCI', 'Crown Castle'),
        ('EQIX', 'Equinix Inc.'),
        ('PSA', 'Public Storage'),
        ('WELL', 'Welltower Inc.'),
        ('SPG', 'Simon Property Group'),
        ('O', 'Realty Income'),
        ('DLR', 'Digital Realty Trust'),
        ('SBAC', 'SBA Communications'),
    ],
    'Basic Materials': [
        ('LIN', 'Linde plc'),
        ('APD', 'Air Products and Chemicals'),
        ('ECL', 'Ecolab Inc.'),
        ('SHW', 'Sherwin-Williams'),
        ('FCX', 'Freeport-McMoRan'),
        ('NEM', 'Newmont Corporation'),
        ('DOW', 'Dow Inc.'),
        ('DD', 'DuPont de Nemours'),
        ('NUE', 'Nucor Corporation'),
        ('VMC', 'Vulcan Materials'),
    ],
}


def add_stock(db_conn: DatabaseConnection, symbol: str, name: str, sector: str, dry_run: bool = False) -> bool:
    """
    Add a single stock to the database

    Args:
        db_conn: Database connection
        symbol: Stock symbol
        name: Company name
        sector: Sector name
        dry_run: If True, only print what would be added

    Returns:
        bool: True if successful or already exists
    """
    if dry_run:
        logger.info(f"[DRY RUN] Would add: {symbol} - {name} ({sector})")
        return True

    try:
        with db_conn.get_connection() as conn:
            with conn.cursor() as cur:
                # Check if stock already exists
                cur.execute("SELECT ticker_id FROM tickers WHERE symbol = %s", (symbol,))
                existing = cur.fetchone()

                if existing:
                    logger.info(f"✓ {symbol} already exists - skipping")
                    return True

                # Insert new ticker
                query = """
                INSERT INTO tickers (symbol, company_name, sector, active)
                VALUES (%s, %s, %s, TRUE)
                RETURNING ticker_id
                """
                cur.execute(query, (symbol, name, sector))
                ticker_id = cur.fetchone()[0]
                conn.commit()

                logger.info(f"✅ Added: {symbol} - {name} ({sector})")
                return True

    except Exception as e:
        logger.error(f"❌ Failed to add {symbol}: {e}")
        return False


def add_all_sector_stocks(dry_run: bool = False, interactive: bool = False) -> Tuple[int, int]:
    """
    Add all stocks from SECTOR_STOCKS to database

    Args:
        dry_run: If True, only print what would be added
        interactive: If True, ask for confirmation before adding each sector

    Returns:
        Tuple of (added_count, total_count)
    """
    db_conn = DatabaseConnection()
    added_count = 0
    total_count = 0

    logger.info("=" * 80)
    logger.info("BULK STOCK IMPORT - Adding 110 stocks across 11 sectors")
    logger.info("=" * 80)

    for sector, stocks in SECTOR_STOCKS.items():
        logger.info(f"\n📊 Sector: {sector} ({len(stocks)} stocks)")

        if interactive and not dry_run:
            response = input(f"  Add stocks from {sector}? (y/n): ").strip().lower()
            if response != 'y':
                logger.info(f"  Skipping {sector}")
                continue

        sector_added = 0
        for symbol, name in stocks:
            total_count += 1
            if add_stock(db_conn, symbol, name, sector, dry_run):
                sector_added += 1
                added_count += 1

        logger.info(f"  {sector}: {sector_added}/{len(stocks)} stocks processed")

    logger.info("\n" + "=" * 80)
    logger.info(f"SUMMARY: {added_count}/{total_count} stocks processed successfully")
    logger.info("=" * 80)

    return added_count, total_count


def verify_sector_coverage():
    """Verify that all sectors have stocks in the database"""
    db_conn = DatabaseConnection()

    logger.info("\n" + "=" * 80)
    logger.info("SECTOR COVERAGE VERIFICATION")
    logger.info("=" * 80)

    try:
        with db_conn.get_connection() as conn:
            with conn.cursor() as cur:
                query = """
                SELECT sector, COUNT(*) as stock_count
                FROM tickers
                WHERE active = TRUE AND sector IS NOT NULL
                GROUP BY sector
                ORDER BY sector
                """
                cur.execute(query)
                results = cur.fetchall()

                total_stocks = 0
                for sector, count in results:
                    emoji = SECTORS.get(sector, {}).get('emoji', '📊')
                    logger.info(f"{emoji} {sector:25s}: {count:3d} stocks")
                    total_stocks += count

                logger.info("-" * 80)
                logger.info(f"{'TOTAL':26s}: {total_stocks:3d} stocks across {len(results)} sectors")
                logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Error verifying sector coverage: {e}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Bulk import stocks across all market sectors'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be added without making changes'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Ask for confirmation before adding each sector'
    )
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Only verify sector coverage, don\'t add stocks'
    )

    args = parser.parse_args()

    if args.verify_only:
        verify_sector_coverage()
        return

    if args.dry_run:
        logger.info("🔍 DRY RUN MODE - No changes will be made\n")

    # Add all stocks
    added, total = add_all_sector_stocks(
        dry_run=args.dry_run,
        interactive=args.interactive
    )

    # Verify coverage
    if not args.dry_run:
        verify_sector_coverage()

    # Final summary
    logger.info("\n✅ Import complete!")
    logger.info(f"   Next steps:")
    logger.info(f"   1. Backfill price data: python -m tradingagents.dataflows.y_finance backfill --days 90")
    logger.info(f"   2. Run sector screener: python -m tradingagents.screener run --sector-analysis")


if __name__ == '__main__':
    main()
