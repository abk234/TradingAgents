#!/bin/bash
#
# Profit-Making Script for TradingAgents
#
# This script:
# 1. Validates the application is ready
# 2. Finds investment opportunities (screener)
# 3. Analyzes top stocks for profit potential
# 4. Provides actionable buy recommendations
# 5. Validates the strategy
#
# Usage:
#   ./make_profit.sh [--portfolio-value 100000] [--top 5] [--fast]
#

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default settings
PORTFOLIO_VALUE=${PORTFOLIO_VALUE:-100000}
TOP_N=${TOP_N:-5}
FAST_MODE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --portfolio-value)
            PORTFOLIO_VALUE="$2"
            shift 2
            ;;
        --top)
            TOP_N="$2"
            shift 2
            ;;
        --fast)
            FAST_MODE="--fast"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--portfolio-value 100000] [--top 5] [--fast]"
            exit 1
            ;;
    esac
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💰 TRADINGAGENTS PROFIT-MAKING WORKFLOW"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Portfolio Value: \$${PORTFOLIO_VALUE}"
echo "Analyzing Top: ${TOP_N} stocks"
echo "Mode: ${FAST_MODE:+Fast}${FAST_MODE:-Standard}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✓${NC} Virtual environment activated"
else
    echo -e "${RED}✗${NC} Virtual environment not found. Please create one first."
    exit 1
fi

# Step 1: Validate Prerequisites
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: Validating Prerequisites"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if python validate_eddie_prerequisites.py; then
    echo -e "${GREEN}✓${NC} Prerequisites validated"
else
    echo -e "${YELLOW}⚠${NC}  Some prerequisites missing. Continuing anyway..."
    echo "   Run 'python scripts/precache_prices.py' to improve performance"
fi

# Step 2: Run Screener to Find Opportunities
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: Finding Investment Opportunities (Screener)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Running daily screener to identify top opportunities..."
echo ""

if python -m tradingagents.screener run 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Screener completed"
else
    echo -e "${YELLOW}⚠${NC}  Screener had issues, but continuing..."
fi

echo ""
echo "Top ${TOP_N} Opportunities:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Get top stocks from screener
python << PYTHON_SCRIPT
import sys
sys.path.insert(0, '.')
from tradingagents.database import get_db_connection
from datetime import date

db = get_db_connection()
with db.get_cursor() as cursor:
    cursor.execute("""
        SELECT 
            t.symbol,
            t.company_name,
            ds.priority_score,
            ds.price,
            ds.triggered_alerts
        FROM daily_scans ds
        JOIN tickers t ON ds.ticker_id = t.ticker_id
        WHERE ds.scan_date = CURRENT_DATE
        ORDER BY ds.priority_rank
        LIMIT ${TOP_N}
    """)
    results = cursor.fetchall()
    
    if results:
        for i, (symbol, name, score, price, alerts) in enumerate(results, 1):
            alerts_str = ', '.join(alerts) if alerts else 'None'
            print(f"{i}. {symbol:6} | Score: {score:5.1f}/100 | Price: \${price:7.2f} | Alerts: {alerts_str}")
    else:
        print("No screener results found for today. Running screener...")
        print("(This may take 30-60 seconds)")
PYTHON_SCRIPT

# Step 3: Analyze Top Stocks for Profit
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: Analyzing Top Stocks for Profit Potential"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Running deep analysis on top ${TOP_N} opportunities..."
echo "This will take 2-5 minutes per stock (${TOP_N} stocks = ~${TOP_N}0-${TOP_N}0 minutes total)"
echo ""
echo -e "${BLUE}Analyzing now...${NC}"
echo ""

# Check if batch_analyze module exists
if python -c "import tradingagents.analyze.batch_analyze" 2>/dev/null; then
    # Use batch analyzer if available
    echo "Using batch analyzer..."
    python -m tradingagents.analyze.batch_analyze \
        --top ${TOP_N} \
        --plain-english \
        --portfolio-value ${PORTFOLIO_VALUE} \
        ${FAST_MODE} 2>&1 | tee /tmp/profit_analysis.log
else
    # Fallback: analyze individually
    echo "Using individual analysis..."
    
    # Get top tickers
    TOP_TICKERS=$(python << PYTHON_SCRIPT
import sys
sys.path.insert(0, '.')
from tradingagents.database import get_db_connection

db = get_db_connection()
with db.get_cursor() as cursor:
    cursor.execute("""
        SELECT t.symbol
        FROM daily_scans ds
        JOIN tickers t ON ds.ticker_id = t.ticker_id
        WHERE ds.scan_date = CURRENT_DATE
        ORDER BY ds.priority_rank
        LIMIT ${TOP_N}
    """)
    results = cursor.fetchall()
    print(' '.join([r[0] for r in results]))
PYTHON_SCRIPT
)
    
    for ticker in $TOP_TICKERS; do
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Analyzing: $ticker"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        python -m tradingagents.analyze "$ticker" \
            --plain-english \
            --portfolio-value ${PORTFOLIO_VALUE} \
            ${FAST_MODE} 2>&1 | tee -a /tmp/profit_analysis.log || {
            echo -e "${YELLOW}⚠${NC}  Analysis for $ticker had issues, continuing..."
        }
    done
fi

# Step 4: Extract Profit Recommendations
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: Profit Recommendations Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python << PYTHON_SCRIPT
import sys
sys.path.insert(0, '.')
from tradingagents.database import get_db_connection
from datetime import datetime, timedelta

db = get_db_connection()

# Get recent analyses with BUY recommendations
with db.get_cursor() as cursor:
    cursor.execute("""
        SELECT 
            t.symbol,
            a.final_decision,
            a.confidence_score,
            a.entry_price_target,
            a.stop_loss_price,
            a.expected_return_pct,
            a.position_size_pct,
            a.analysis_date
        FROM analyses a
        JOIN tickers t ON a.ticker_id = t.ticker_id
        WHERE a.analysis_date >= CURRENT_DATE - INTERVAL '1 day'
        AND a.final_decision = 'BUY'
        ORDER BY a.confidence_score DESC, a.analysis_date DESC
        LIMIT 10
    """)
    
    results = cursor.fetchall()
    
    if results:
        print("🎯 BUY RECOMMENDATIONS:")
        print("")
        
        total_investment = 0
        total_expected_profit = 0
        
        for symbol, decision, confidence, entry, stop, expected_return, position_pct, analysis_date in results:
            investment = ${PORTFOLIO_VALUE} * (position_pct / 100) if position_pct else 0
            expected_profit = investment * (expected_return / 100) if expected_return and investment else 0
            
            total_investment += investment
            total_expected_profit += expected_profit
            
            print(f"📈 {symbol}")
            print(f"   Decision: {decision} | Confidence: {confidence}/100")
            if entry:
                print(f"   Entry: \${entry:.2f} | Stop Loss: \${stop:.2f if stop else 'N/A'}")
            if expected_return:
                print(f"   Expected Return: {expected_return:.1f}%")
            if position_pct:
                print(f"   Position Size: {position_pct:.1f}% = \${investment:,.0f}")
                if expected_profit:
                    print(f"   Expected Profit: \${expected_profit:,.0f}")
            print("")
        
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"💰 TOTAL INVESTMENT: \${total_investment:,.0f}")
        print(f"📊 EXPECTED PROFIT: \${total_expected_profit:,.0f}")
        print(f"💵 REMAINING CASH: \${${PORTFOLIO_VALUE} - total_investment:,.0f}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    else:
        print("⚠️  No BUY recommendations found in recent analyses.")
        print("   This could mean:")
        print("   - Market conditions are not favorable")
        print("   - No stocks passed the four-gate framework")
        print("   - Analyses haven't been run yet")
        print("")
        print("   Try running: python -m tradingagents.analyze AAPL --plain-english")
PYTHON_SCRIPT

# Step 5: Validate Strategy
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 5: Strategy Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python << PYTHON_SCRIPT
import sys
sys.path.insert(0, '.')
from tradingagents.database import get_db_connection
from datetime import date, timedelta

db = get_db_connection()

# Validate strategy by checking:
# 1. Recent analyses exist
# 2. BUY signals have good confidence
# 3. Entry prices are reasonable
# 4. Stop losses are set

with db.get_cursor() as cursor:
    # Check recent analyses
    cursor.execute("""
        SELECT COUNT(*) 
        FROM analyses 
        WHERE analysis_date >= CURRENT_DATE - INTERVAL '7 days'
    """)
    recent_count = cursor.fetchone()[0]
    
    # Check BUY signals quality
    cursor.execute("""
        SELECT 
            COUNT(*) as total_buys,
            AVG(confidence_score) as avg_confidence,
            COUNT(*) FILTER (WHERE confidence_score >= 70) as high_confidence_buys,
            COUNT(*) FILTER (WHERE stop_loss_price IS NOT NULL) as with_stop_loss
        FROM analyses
        WHERE final_decision = 'BUY'
        AND analysis_date >= CURRENT_DATE - INTERVAL '7 days'
    """)
    
    buy_stats = cursor.fetchone()
    total_buys, avg_conf, high_conf_buys, with_stops = buy_stats
    
    print("📊 Strategy Validation Results:")
    print("")
    print(f"   Recent Analyses (7 days): {recent_count}")
    print(f"   BUY Signals: {total_buys or 0}")
    
    if total_buys and total_buys > 0:
        print(f"   Average Confidence: {avg_conf:.1f}/100")
        print(f"   High Confidence (≥70): {high_conf_buys}/{total_buys}")
        print(f"   With Stop Loss: {with_stops}/{total_buys}")
        print("")
        
        if avg_conf >= 70:
            print("   ✅ Strategy Quality: GOOD")
        elif avg_conf >= 60:
            print("   ⚠️  Strategy Quality: MODERATE")
        else:
            print("   ❌ Strategy Quality: NEEDS IMPROVEMENT")
        
        if with_stops == total_buys:
            print("   ✅ Risk Management: EXCELLENT (all positions have stop losses)")
        elif with_stops >= total_buys * 0.8:
            print("   ⚠️  Risk Management: GOOD (most positions have stop losses)")
        else:
            print("   ❌ Risk Management: NEEDS IMPROVEMENT (missing stop losses)")
    else:
        print("   ⚠️  No BUY signals found. Strategy validation cannot be completed.")
        print("   Run more analyses to validate strategy.")
PYTHON_SCRIPT

# Final Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ PROFIT-MAKING WORKFLOW COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Review the BUY recommendations above"
echo "2. Check entry prices and timing"
echo "3. Set stop losses for risk management"
echo "4. Execute trades at recommended entry prices"
echo "5. Monitor positions regularly"
echo ""
echo "📊 Track Performance:"
echo "   - Review portfolio: python -m tradingagents.portfolio"
echo "   - Check returns: python scripts/evaluate.sh report"
echo ""
echo "💡 Tips for Profit:"
echo "   - Buy at recommended entry prices (not higher)"
echo "   - Always set stop losses"
echo "   - Don't invest more than recommended position size"
echo "   - Diversify across multiple stocks"
echo "   - Be patient - returns take time"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

