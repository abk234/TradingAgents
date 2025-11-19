#!/bin/bash
# Helper script to show current database state
# Useful for understanding what data is stored

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

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "-/bin" ]; then
    source -/bin/activate
fi

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  DATABASE STATE OVERVIEW${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

python3 << 'PYTHON_SCRIPT'
from tradingagents.database import get_db_connection, TickerOperations, ScanOperations, AnalysisOperations
from datetime import date

db = get_db_connection()
ticker_ops = TickerOperations(db)
scan_ops = ScanOperations(db)
analysis_ops = AnalysisOperations(db)

print("=" * 60)
print("DATABASE TABLES STATUS")
print("=" * 60)

# Tickers
active_tickers = ticker_ops.get_all_tickers(active_only=True)
print(f"\n📊 TICKERS TABLE")
print(f"   Active tickers: {len(active_tickers)}")
if active_tickers:
    print(f"   Sample: {', '.join([t['symbol'] for t in active_tickers[:5]])}")

# Daily Scans
with db.get_cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM daily_scans")
    scan_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT MAX(scan_date) FROM daily_scans")
    latest_scan_date = cursor.fetchone()[0]
    
    print(f"\n🔍 DAILY_SCANS TABLE")
    print(f"   Total scan results: {scan_count}")
    if latest_scan_date:
        print(f"   Latest scan date: {latest_scan_date}")
        
        # Get top 3 from latest scan
        today = date.today()
        top_opportunities = scan_ops.get_top_opportunities(scan_date=today, limit=3)
        if top_opportunities:
            print(f"   Top 3 opportunities:")
            for i, opp in enumerate(top_opportunities, 1):
                print(f"     {i}. {opp['symbol']} - Score: {opp['priority_score']}")

# Analyses
with db.get_cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM analyses")
    analysis_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT MAX(analysis_date) FROM analyses")
    latest_analysis_date = cursor.fetchone()[0]
    
    print(f"\n🤖 ANALYSES TABLE")
    print(f"   Total analyses: {analysis_count}")
    if latest_analysis_date:
        print(f"   Latest analysis date: {latest_analysis_date}")
        
        # Decision breakdown
        cursor.execute("""
            SELECT final_decision, COUNT(*) as count
            FROM analyses
            WHERE final_decision IS NOT NULL
            GROUP BY final_decision
            ORDER BY count DESC
        """)
        decisions = cursor.fetchall()
        if decisions:
            print(f"   Decision breakdown:")
            for decision, count in decisions:
                print(f"     • {decision}: {count}")
        
        # Recent analyses
        cursor.execute("""
            SELECT t.symbol, a.analysis_date, a.final_decision, a.confidence_score
            FROM analyses a
            JOIN tickers t ON a.ticker_id = t.ticker_id
            ORDER BY a.analysis_date DESC
            LIMIT 5
        """)
        recent = cursor.fetchall()
        if recent:
            print(f"   Recent analyses:")
            for symbol, a_date, decision, confidence in recent:
                print(f"     • {symbol} ({a_date}): {decision} (confidence: {confidence})")

# Prices
with db.get_cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM daily_prices")
    price_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT MAX(price_date) FROM daily_prices")
    latest_price_date = cursor.fetchone()[0]
    
    print(f"\n💰 DAILY_PRICES TABLE")
    print(f"   Total price records: {price_count}")
    if latest_price_date:
        print(f"   Latest price date: {latest_price_date}")

print("\n" + "=" * 60)
print("WORKFLOW STATUS")
print("=" * 60)

# Check if workflow is complete
has_scans = scan_count > 0
has_analyses = analysis_count > 0

print(f"\n✓ Screening Phase: {'Complete' if has_scans else 'Not Run'}")
print(f"✓ Analysis Phase: {'Complete' if has_analyses else 'Not Run'}")

if has_scans and has_analyses:
    print(f"\n✅ Full workflow has been executed!")
    print(f"   You can now query the database for insights.")
elif has_scans:
    print(f"\n⚠️  Screening complete, but no analyses yet.")
    print(f"   Run: ./scripts/phase2_agents.sh [TICKER]")
else:
    print(f"\n⚠️  No data found. Run Phase 1 first:")
    print(f"   Run: ./scripts/phase1_screening.sh")

print("")
PYTHON_SCRIPT

