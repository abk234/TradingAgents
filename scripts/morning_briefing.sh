#!/bin/bash
#
# Morning Briefing Script - Enhanced with Sector Analysis
#
# This script provides a comprehensive morning market update:
# 1. Sector analysis across all 11 market sectors
# 2. Top stock opportunities from strongest sectors
# 3. Daily market digest and alerts
# 4. Email/Slack notifications (if configured)
#
# Run this every morning to get your market briefing!
#
# Add to crontab:
# 0 7 * * 1-5 cd /path/to/TradingAgents && ./scripts/morning_briefing.sh >> logs/briefing.log 2>&1
#
# Options:
#   --sector-first   Use sector-first workflow (analyze sectors, then top stocks)
#   --with-analysis  Include AI analysis of top stocks (slower but comprehensive)
#   --fast          Fast mode (skip news, optimized for speed)

set -e

# Parse arguments
SECTOR_FIRST=false
WITH_ANALYSIS=false
FAST_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --sector-first)
            SECTOR_FIRST=true
            shift
            ;;
        --with-analysis)
            WITH_ANALYSIS=true
            shift
            ;;
        --fast)
            FAST_MODE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--sector-first] [--with-analysis] [--fast]"
            exit 1
            ;;
    esac
done

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "=================================================="
echo "🌅 Morning Market Briefing - $(date '+%Y-%m-%d %H:%M:%S')"
echo "=================================================="
echo

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Build screener command based on options
SCREENER_CMD="PYTHONPATH=$PROJECT_DIR .venv/bin/python -m tradingagents.screener run"

# Add sector analysis flags
if [ "$SECTOR_FIRST" = true ]; then
    echo "📊 Running sector-first analysis..."
    SCREENER_CMD="$SCREENER_CMD --sector-analysis --sector-first --top-sectors 2 --stocks-per-sector 3"
else
    echo "📊 Running standard screener with sector analysis..."
    SCREENER_CMD="$SCREENER_CMD --sector-analysis"
fi

# Add AI analysis flag if requested
if [ "$WITH_ANALYSIS" = true ]; then
    echo "🤖 AI analysis enabled"
    SCREENER_CMD="$SCREENER_CMD --with-analysis --analysis-limit 5 --portfolio-value 100000"

    # Add fast mode if specified
    if [ "$FAST_MODE" = true ]; then
        echo "⚡ Fast mode enabled"
        SCREENER_CMD="$SCREENER_CMD --fast --no-rag"
    fi
fi

echo
echo "Running: $SCREENER_CMD"
echo
echo "--------------------------------------------------"

# Run screener with sector analysis
eval $SCREENER_CMD

echo
echo "--------------------------------------------------"
echo

# Run insights module for digest and alerts
echo "📰 Generating market digest and alerts..."
echo
PYTHONPATH="$PROJECT_DIR" .venv/bin/python -m tradingagents.insights morning

echo
echo "=================================================="
echo "✅ Briefing Complete"
echo "=================================================="
echo

# Print summary
if [ "$SECTOR_FIRST" = true ]; then
    echo "✓ Sector analysis: Complete (sector-first mode)"
else
    echo "✓ Sector analysis: Complete (standard mode)"
fi

if [ "$WITH_ANALYSIS" = true ]; then
    echo "✓ AI analysis: Complete"
else
    echo "ℹ️  AI analysis: Skipped (add --with-analysis to enable)"
fi

echo "✓ Market digest: Complete"
echo "✓ Alerts: Checked"
echo

echo "💡 Next steps:"
echo "   - Check your email for the briefing report (if configured)"
echo "   - Review top sector opportunities above"
if [ "$WITH_ANALYSIS" = false ]; then
    echo "   - Run with --with-analysis for AI recommendations"
fi
echo

echo "📧 Email notifications: $([ -n "$EMAIL_ENABLED" ] && echo "Enabled" || echo "Disabled (set EMAIL_ENABLED=true in .env)")"
echo "💬 Slack notifications: $([ -n "$SLACK_ENABLED" ] && echo "Enabled" || echo "Disabled (set SLACK_ENABLED=true in .env)")"
echo
