#!/bin/bash
#
# Morning Briefing Script - Phase 7
#
# This script provides a comprehensive morning market update:
# 1. Daily market digest
# 2. Price alerts
# 3. Top opportunities
#
# Run this every morning to get your market briefing!
#
# Add to crontab:
# 0 7 * * 1-5 cd /path/to/TradingAgents && ./scripts/morning_briefing.sh >> logs/briefing.log 2>&1

set -e

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

# Run morning briefing
PYTHONPATH="$PROJECT_DIR" .venv/bin/python -m tradingagents.insights morning

echo
echo "=================================================="
echo "✅ Briefing Complete"
echo "=================================================="
echo
echo "💡 TIP: Run './scripts/run_daily_analysis.sh' for fresh AI analysis!"
