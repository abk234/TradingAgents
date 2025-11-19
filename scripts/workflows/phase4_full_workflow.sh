#!/bin/bash
# Phase 4: Full End-to-End Workflow
# This script runs all phases sequentially to demonstrate the complete workflow

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  FULL END-TO-END WORKFLOW${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "${YELLOW}This will run all phases sequentially:${NC}"
echo "  1. Phase 1: Screening"
echo "  2. Phase 2: Agent Analysis (on top screener result)"
echo "  3. Phase 3: Database Reports"
echo ""

read -p "Press Enter to continue or Ctrl+C to cancel..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "-/bin" ]; then
    source -/bin/activate
fi

# Phase 1: Screening
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  PHASE 1: SCREENING${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

bash "$SCRIPT_DIR/phase1_screening.sh"

# Get top ticker from screener
echo -e "${BLUE}Getting top opportunity from screener...${NC}"
TOP_TICKER=$(python3 << 'PYTHON_SCRIPT'
from tradingagents.database import get_db_connection, ScanOperations
from datetime import date

db = get_db_connection()
scan_ops = ScanOperations(db)

today = date.today()
results = scan_ops.get_top_opportunities(scan_date=today, limit=1)

if results:
    print(results[0].get('symbol', 'AAPL'))
else:
    print('AAPL')  # Fallback
PYTHON_SCRIPT
)

echo -e "${GREEN}Top opportunity: ${TOP_TICKER}${NC}"
echo ""

# Phase 2: Agent Analysis
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  PHASE 2: AGENT ANALYSIS${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

bash "$SCRIPT_DIR/phase2_agents.sh" "$TOP_TICKER"

# Phase 3: Reports
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  PHASE 3: DATABASE REPORTS${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

bash "$SCRIPT_DIR/phase3_reports.sh" "$TOP_TICKER"

# Final Summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  FULL WORKFLOW COMPLETE!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${CYAN}What happened:${NC}"
echo "  1. ✓ Screener scanned all tickers and stored results"
echo "  2. ✓ Agent analysis ran on ${TOP_TICKER} and stored results"
echo "  3. ✓ Reports generated from database"
echo ""
echo -e "${CYAN}Database Tables Populated:${NC}"
echo "  • daily_scans - Screener results with priority scores"
echo "  • analyses - Full agent analysis with decisions"
echo "  • tickers - Watchlist information"
echo ""
echo -e "${CYAN}Next Steps:${NC}"
echo "  • Query database directly: python3 -c \"from tradingagents.database import get_db_connection; db = get_db_connection(); print(db.execute_dict_query('SELECT * FROM analyses LIMIT 5'))\""
echo "  • Run individual phases: ./scripts/phase1_screening.sh"
echo "  • Analyze specific ticker: ./scripts/phase2_agents.sh AAPL"
echo ""

