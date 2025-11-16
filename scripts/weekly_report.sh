#!/bin/bash
#
# Weekly Performance Report Script - Phase 6 & 7
#
# This script generates a comprehensive weekly report including:
# - Performance metrics and win rates
# - Top/worst performers
# - Active alerts and opportunities
# - Weekly market summary
#
# Add to crontab to run every Sunday at 9 AM:
# 0 9 * * 0 cd /path/to/TradingAgents && ./scripts/weekly_report.sh | mail -s "AI Trading Performance Report" your@email.com

set -e  # Exit on error

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

echo "=================================================================="
echo "📊 WEEKLY TRADING REPORT - $(date '+%B %d, %Y')"
echo "=================================================================="
echo

# Section 1: Performance Report
echo "📈 PERFORMANCE METRICS"
echo "=================================================================="
PYTHONPATH="$PROJECT_DIR" .venv/bin/python -m tradingagents.evaluate report --period 90
echo

# Section 2: Current Alerts
echo
echo "🚨 ACTIVE ALERTS"
echo "=================================================================="
PYTHONPATH="$PROJECT_DIR" .venv/bin/python -m tradingagents.insights alerts || echo "No active alerts"
echo

# Section 3: Weekly Digest
echo
echo "📰 WEEKLY SUMMARY"
echo "=================================================================="
PYTHONPATH="$PROJECT_DIR" .venv/bin/python -m tradingagents.insights digest || echo "Run screener for fresh data"
echo

echo "=================================================================="
echo "✅ Weekly Report Complete"
echo "=================================================================="
