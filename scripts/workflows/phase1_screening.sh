#!/bin/bash
# Phase 1: Screening Workflow
# This script runs the daily screener and shows how data is saved to the database

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  PHASE 1: SCREENING WORKFLOW${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "-/bin" ]; then
    source -/bin/activate
fi

# Check database state BEFORE screening
echo -e "${BLUE}[STEP 1] Checking database state BEFORE screening...${NC}"
python3 << 'PYTHON_SCRIPT'
from tradingagents.database import get_db_connection, TickerOperations, ScanOperations
from datetime import date

db = get_db_connection()
ticker_ops = TickerOperations(db)
scan_ops = ScanOperations(db)

# Count active tickers
active_tickers = ticker_ops.get_all_tickers(active_only=True)
print(f"  ✓ Active tickers in database: {len(active_tickers)}")

# Count scan results
with db.get_cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM daily_scans")
    scan_count = cursor.fetchone()[0]
    print(f"  ✓ Total scan results in database: {scan_count}")
    
    if scan_count > 0:
        cursor.execute("SELECT MAX(scan_date) FROM daily_scans")
        latest_scan = cursor.fetchone()[0]
        print(f"  ✓ Latest scan date: {latest_scan}")

print("")
PYTHON_SCRIPT

echo ""
echo -e "${BLUE}[STEP 2] Running daily screener...${NC}"
echo -e "${YELLOW}This will:${NC}"
echo "  • Fetch price data for all active tickers"
echo "  • Calculate technical indicators (RSI, MACD, Bollinger Bands)"
echo "  • Generate trading signals and alerts"
echo "  • Calculate priority scores (0-100)"
echo "  • Rank tickers by priority"
echo "  • Store results in 'daily_scans' table"
echo ""

# Run the screener
python3 -m tradingagents.screener run --top 10

echo ""
echo -e "${BLUE}[STEP 3] Checking database state AFTER screening...${NC}"
python3 << 'PYTHON_SCRIPT'
from tradingagents.database import get_db_connection, ScanOperations
from datetime import date

db = get_db_connection()
scan_ops = ScanOperations(db)

# Get latest scan results
today = date.today()
results = scan_ops.get_scan_results(scan_date=today)

if results:
    print(f"\n  ✓ Scan results stored for {len(results)} tickers")
    print(f"\n  Top 5 opportunities:")
    for i, result in enumerate(results[:5], 1):
        symbol = result['symbol']
        score = result['priority_score']
        rank = result['priority_rank']
        alerts = result.get('triggered_alerts', [])
        print(f"    {i}. {symbol:6s} - Score: {score:3d} - Rank: {rank:2d}")
        if alerts:
            print(f"       Alerts: {', '.join(alerts[:3])}")
    
    # Show database structure
    print(f"\n  Database table: daily_scans")
    print(f"  Columns stored:")
    print(f"    • ticker_id, scan_date")
    print(f"    • priority_score, priority_rank")
    print(f"    • price, volume, pe_ratio")
    print(f"    • technical_signals (JSONB)")
    print(f"    • triggered_alerts (ARRAY)")
else:
    print("  ⚠ No scan results found for today")

print("")
PYTHON_SCRIPT

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  PHASE 1 COMPLETE: Screening Done${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${CYAN}Next Steps:${NC}"
echo "  • Run: ./scripts/phase2_agents.sh [TICKER]"
echo "  • Or: ./scripts/phase2_agents.sh AAPL"
echo ""

