#!/bin/bash
# Update dividend data daily
# Add to crontab: 0 18 * * * cd /path/to/TradingAgents && ./scripts/update_dividends.sh >> logs/dividends.log 2>&1

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "=================================================="
echo "Dividend Data Update - $(date)"
echo "=================================================="

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# 1. Backfill any new dividend history (last 30 days)
echo ""
echo "📊 Checking for new dividend payments..."
PYTHONPATH="$PROJECT_ROOT" python -m tradingagents.dividends backfill --years 1

# 2. Update dividend yield cache
echo ""
echo "💰 Updating dividend yield cache..."
PYTHONPATH="$PROJECT_ROOT" python -m tradingagents.dividends update-cache --cache-hours 24

# 3. Update dividend calendar predictions
echo ""
echo "📅 Updating dividend calendar..."
PYTHONPATH="$PROJECT_ROOT" python -m tradingagents.dividends update-calendar --days 180

echo ""
echo "=================================================="
echo "Dividend update complete! - $(date)"
echo "=================================================="
