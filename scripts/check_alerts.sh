#!/bin/bash
#
# Alert Checking Script - Phase 7
#
# Check for price alerts throughout the trading day.
# Run this periodically (every hour) during market hours.
#
# Add to crontab for hourly checks during market hours (9 AM - 4 PM ET):
# 0 9-16 * * 1-5 cd /path/to/TradingAgents && ./scripts/check_alerts.sh >> logs/alerts.log 2>&1

set -e

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Check for alerts
PYTHONPATH="$PROJECT_DIR" .venv/bin/python -m tradingagents.insights alerts
