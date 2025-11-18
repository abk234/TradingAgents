#!/bin/bash
# Phase 3: Database Reports and Queries
# This script shows how to query and display data from the database

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

# Optional ticker filter
TICKER=${1:-""}

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  PHASE 3: DATABASE REPORTS${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "-/bin" ]; then
    source -/bin/activate
fi

# Report 1: Screener Results
echo -e "${BLUE}[REPORT 1] Latest Screener Results${NC}"
python3 << 'PYTHON_SCRIPT'
from tradingagents.database import get_db_connection, ScanOperations
from datetime import date

db = get_db_connection()
scan_ops = ScanOperations(db)

today = date.today()
results = scan_ops.get_top_opportunities(scan_date=today, limit=10)

if results:
    print(f"\n  Top 10 Opportunities (from daily_scans table):")
    print(f"  {'Rank':<6} {'Symbol':<8} {'Score':<8} {'Price':<12} {'Alerts'}")
    print(f"  {'-'*60}")
    for result in results:
        rank = result.get('priority_rank', 'N/A')
        symbol = result.get('symbol', 'N/A')
        score = result.get('priority_score', 0)
        price = result.get('price', 0)
        alerts = result.get('triggered_alerts', [])
        alert_str = ', '.join(alerts[:2]) if alerts else 'None'
        print(f"  {rank:<6} {symbol:<8} {score:<8} ${price:<11.2f} {alert_str}")
else:
    print("  ⚠ No screener results found. Run Phase 1 first.")

print("")
PYTHON_SCRIPT

# Report 2: Analysis History
echo -e "${BLUE}[REPORT 2] Analysis History${NC}"
python3 << PYTHON_SCRIPT
from tradingagents.database import get_db_connection, TickerOperations, AnalysisOperations
from datetime import date

db = get_db_connection()
ticker_ops = TickerOperations(db)
analysis_ops = AnalysisOperations(db)

# Query recent analyses
with db.get_cursor() as cursor:
    if "${TICKER}":
        # Get analyses for specific ticker
        ticker_info = ticker_ops.get_ticker(symbol="${TICKER}")
        if ticker_info:
            ticker_id = ticker_info['ticker_id']
            analyses = analysis_ops.get_analyses_for_ticker(ticker_id, limit=10)
            
            if analyses:
                print(f"\n  Recent Analyses for ${TICKER}:")
                print(f"  {'Date':<12} {'Decision':<10} {'Confidence':<12} {'Summary'}")
                print(f"  {'-'*80}")
                for a in analyses:
                    date_str = str(a.get('analysis_date', ''))[:10]
                    decision = a.get('final_decision', 'N/A')
                    confidence = a.get('confidence_score', 'N/A')
                    summary = (a.get('executive_summary', '') or '')[:50]
                    print(f"  {date_str:<12} {decision:<10} {confidence:<12} {summary}")
            else:
                print(f"  ⚠ No analyses found for ${TICKER}")
        else:
            print(f"  ⚠ Ticker ${TICKER} not found")
    else:
        # Get all recent analyses
        query = """
            SELECT 
                t.symbol,
                a.analysis_date,
                a.final_decision,
                a.confidence_score,
                LEFT(a.executive_summary, 50) as summary
            FROM analyses a
            JOIN tickers t ON a.ticker_id = t.ticker_id
            ORDER BY a.analysis_date DESC
            LIMIT 10
        """
        analyses = db.execute_dict_query(query)
        
        if analyses:
            print(f"\n  Recent Analyses (all tickers):")
            print(f"  {'Symbol':<8} {'Date':<12} {'Decision':<10} {'Confidence':<12} {'Summary'}")
            print(f"  {'-'*90}")
            for a in analyses:
                symbol = a.get('symbol', 'N/A')
                date_str = str(a.get('analysis_date', ''))[:10]
                decision = a.get('final_decision', 'N/A')
                confidence = a.get('confidence_score', 'N/A')
                summary = (a.get('summary', '') or '')[:40]
                print(f"  {symbol:<8} {date_str:<12} {decision:<10} {confidence:<12} {summary}")
        else:
            print("  ⚠ No analyses found. Run Phase 2 first.")

print("")
PYTHON_SCRIPT

# Report 3: Database Statistics
echo -e "${BLUE}[REPORT 3] Database Statistics${NC}"
python3 << 'PYTHON_SCRIPT'
from tradingagents.database import get_db_connection, TickerOperations

db = get_db_connection()
ticker_ops = TickerOperations(db)

# Count tickers
active_tickers = ticker_ops.get_all_tickers(active_only=True)
print(f"\n  Database Statistics:")
print(f"    • Active tickers: {len(active_tickers)}")

# Count scans
with db.get_cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM daily_scans")
    scan_count = cursor.fetchone()[0]
    print(f"    • Total scan results: {scan_count}")
    
    cursor.execute("SELECT COUNT(DISTINCT scan_date) FROM daily_scans")
    scan_dates = cursor.fetchone()[0]
    print(f"    • Unique scan dates: {scan_dates}")
    
    cursor.execute("SELECT COUNT(*) FROM analyses")
    analysis_count = cursor.fetchone()[0]
    print(f"    • Total analyses: {analysis_count}")
    
    cursor.execute("SELECT COUNT(*) FROM analyses WHERE embedding IS NOT NULL")
    rag_count = cursor.fetchone()[0]
    print(f"    • Analyses with RAG embeddings: {rag_count}")
    
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
        print(f"\n    Decision Breakdown:")
        for decision, count in decisions:
            print(f"      • {decision}: {count}")

print("")
PYTHON_SCRIPT

# Report 4: Show full analysis details if ticker specified
if [ -n "$TICKER" ]; then
    echo -e "${BLUE}[REPORT 4] Full Analysis Details for ${TICKER}${NC}"
    python3 << PYTHON_SCRIPT
from tradingagents.database import get_db_connection, TickerOperations, AnalysisOperations
import json

db = get_db_connection()
ticker_ops = TickerOperations(db)
analysis_ops = AnalysisOperations(db)

ticker_info = ticker_ops.get_ticker(symbol="${TICKER}")
if ticker_info:
    ticker_id = ticker_info['ticker_id']
    latest = analysis_ops.get_latest_analysis(ticker_id)
    
    if latest:
        print(f"\n  Full Analysis Details:")
        print(f"    Analysis ID: {latest['analysis_id']}")
        print(f"    Ticker: ${TICKER}")
        print(f"    Date: {latest['analysis_date']}")
        print(f"    Decision: {latest.get('final_decision', 'N/A')}")
        print(f"    Confidence: {latest.get('confidence_score', 'N/A')}/100")
        
        if latest.get('bull_case'):
            bull = latest['bull_case'][:200] if len(latest['bull_case']) > 200 else latest['bull_case']
            print(f"\n    Bull Case:")
            print(f"      {bull}...")
        
        if latest.get('bear_case'):
            bear = latest['bear_case'][:200] if len(latest['bear_case']) > 200 else latest['bear_case']
            print(f"\n    Bear Case:")
            print(f"      {bear}...")
        
        if latest.get('key_catalysts'):
            print(f"\n    Key Catalysts:")
            for catalyst in latest['key_catalysts'][:3]:
                print(f"      • {catalyst}")
        
        if latest.get('risk_factors'):
            print(f"\n    Risk Factors:")
            for risk in latest['risk_factors'][:3]:
                print(f"      • {risk}")
    else:
        print(f"  ⚠ No analysis found for ${TICKER}")

print("")
PYTHON_SCRIPT
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  PHASE 3 COMPLETE: Reports Generated${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${CYAN}Summary:${NC}"
echo "  • Screener results stored in 'daily_scans' table"
echo "  • Analysis results stored in 'analyses' table"
echo "  • All data is queryable via Python or SQL"
echo ""

