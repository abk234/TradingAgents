#!/bin/bash
#
# Daily Evaluation Script - Phase 6
#
# This script should be run daily (via cron) to:
# 1. Update recommendation outcomes with latest prices
# 2. Update S&P 500 benchmark data
# 3. Calculate alpha (excess returns)
#
# Add to crontab:
# 0 18 * * * cd /path/to/TradingAgents && ./scripts/daily_evaluation.sh >> logs/evaluation.log 2>&1

set -e  # Exit on error

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "=================================================="
echo "Daily Evaluation - $(date '+%Y-%m-%d %H:%M:%S')"
echo "=================================================="
echo

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Run the evaluation update
PYTHONPATH="$PROJECT_DIR" .venv/bin/python -m tradingagents.evaluate update --days 90

echo
echo "=================================================="
echo "Daily Evaluation Complete - $(date '+%Y-%m-%d %H:%M:%S')"
echo "=================================================="
