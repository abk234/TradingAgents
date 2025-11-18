#!/bin/bash
# Phase 2: Agent Analysis Workflow
# This script runs the full agent analysis (all agents) and shows how data flows

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

# Get ticker from command line or use default
TICKER=${1:-"AAPL"}

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  PHASE 2: AGENT ANALYSIS WORKFLOW${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "${YELLOW}Analyzing: ${TICKER}${NC}"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "-/bin" ]; then
    source -/bin/activate
fi

# Check if ticker exists in database
echo -e "${BLUE}[STEP 1] Verifying ticker in database...${NC}"
python3 << PYTHON_SCRIPT
from tradingagents.database import get_db_connection, TickerOperations

db = get_db_connection()
ticker_ops = TickerOperations(db)

ticker_info = ticker_ops.get_ticker(symbol="${TICKER}")
if ticker_info:
    print(f"  ✓ Ticker ${TICKER} found in database")
    print(f"    Company: {ticker_info.get('company_name', 'N/A')}")
    print(f"    Sector: {ticker_info.get('sector', 'N/A')}")
else:
    print(f"  ⚠ Ticker ${TICKER} not in database, adding it...")
    ticker_ops.add_ticker("${TICKER}")
    print(f"  ✓ Added ${TICKER} to database")

print("")
PYTHON_SCRIPT

# Check analysis history BEFORE
echo -e "${BLUE}[STEP 2] Checking analysis history BEFORE...${NC}"
python3 << PYTHON_SCRIPT
from tradingagents.database import get_db_connection, TickerOperations, AnalysisOperations

db = get_db_connection()
ticker_ops = TickerOperations(db)
analysis_ops = AnalysisOperations(db)

ticker_info = ticker_ops.get_ticker(symbol="${TICKER}")
if ticker_info:
    ticker_id = ticker_info['ticker_id']
    analyses = analysis_ops.get_analyses_for_ticker(ticker_id, limit=5)
    print(f"  ✓ Existing analyses for ${TICKER}: {len(analyses)}")
    if analyses:
        print(f"    Latest: {analyses[0].get('analysis_date')} - {analyses[0].get('final_decision', 'N/A')}")

print("")
PYTHON_SCRIPT

echo ""
echo -e "${BLUE}[STEP 3] Running full agent analysis...${NC}"
echo -e "${YELLOW}This will execute the following agents in sequence:${NC}"
echo ""
echo -e "${CYAN}  ANALYST TEAM (Parallel):${NC}"
echo "    • Market Analyst → Technical indicators, price action"
echo "    • Social Media Analyst → Sentiment analysis"
echo "    • News Analyst → Recent news and events"
echo "    • Fundamentals Analyst → Financial health"
echo ""
echo -e "${CYAN}  RESEARCH TEAM (Sequential Debate):${NC}"
echo "    • Bull Researcher → Bullish arguments"
echo "    • Bear Researcher → Bearish arguments"
echo "    • Research Manager → Investment decision"
echo ""
echo -e "${CYAN}  TRADING TEAM:${NC}"
echo "    • Trader Agent → Detailed trading plan"
echo ""
echo -e "${CYAN}  RISK MANAGEMENT TEAM (Sequential Debate):${NC}"
echo "    • Aggressive Analyst → High risk arguments"
echo "    • Conservative Analyst → Low risk arguments"
echo "    • Neutral Analyst → Balanced arguments"
echo "    • Portfolio Manager → Final APPROVE/REJECT decision"
echo ""
echo -e "${YELLOW}This may take 30-90 seconds...${NC}"
echo ""

# Run the analysis with verbose output
python3 -m tradingagents.analyze "${TICKER}" --verbose --plain-english --portfolio-value 100000

echo ""
echo -e "${BLUE}[STEP 4] Checking database state AFTER analysis...${NC}"
python3 << PYTHON_SCRIPT
from tradingagents.database import get_db_connection, TickerOperations, AnalysisOperations
from datetime import date

db = get_db_connection()
ticker_ops = TickerOperations(db)
analysis_ops = AnalysisOperations(db)

ticker_info = ticker_ops.get_ticker(symbol="${TICKER}")
if ticker_info:
    ticker_id = ticker_info['ticker_id']
    
    # Get latest analysis
    latest = analysis_ops.get_latest_analysis(ticker_id)
    
    if latest:
        print(f"\n  ✓ Analysis stored in database")
        print(f"    Analysis ID: {latest['analysis_id']}")
        print(f"    Date: {latest['analysis_date']}")
        print(f"    Decision: {latest.get('final_decision', 'N/A')}")
        print(f"    Confidence: {latest.get('confidence_score', 'N/A')}/100")
        
        if latest.get('executive_summary'):
            summary = latest['executive_summary'][:200]
            print(f"    Summary: {summary}...")
        
        # Check what's stored
        print(f"\n  Database table: analyses")
        print(f"  Columns stored:")
        print(f"    • analysis_id, ticker_id, analysis_date")
        print(f"    • final_decision, confidence_score")
        print(f"    • executive_summary, bull_case, bear_case")
        print(f"    • market_report, fundamentals_report (JSONB)")
        print(f"    • sentiment_report, news_report (JSONB)")
        print(f"    • embedding (vector for RAG)")
        
        # Count total analyses
        all_analyses = analysis_ops.get_analyses_for_ticker(ticker_id)
        print(f"\n  Total analyses for ${TICKER}: {len(all_analyses)}")
    else:
        print("  ⚠ No analysis found (may not have been stored)")

print("")
PYTHON_SCRIPT

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  PHASE 2 COMPLETE: Agent Analysis Done${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${CYAN}Next Steps:${NC}"
echo "  • Run: ./scripts/phase3_reports.sh ${TICKER}"
echo "  • Or: ./scripts/phase3_reports.sh"
echo ""

