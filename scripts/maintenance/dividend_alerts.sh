#!/bin/bash
# Check for upcoming dividend payments
# Add to crontab: 0 9 * * 1 cd /path/to/TradingAgents && ./scripts/dividend_alerts.sh | mail -s "Weekly Dividend Alert" your@email.com

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

echo "=================================================="
echo "💵 WEEKLY DIVIDEND ALERT"
echo "$(date)"
echo "=================================================="
echo ""

# Show upcoming dividends (next 30 days)
echo "📅 UPCOMING DIVIDENDS (Next 30 Days)"
echo "=================================================="
PYTHONPATH="$PROJECT_ROOT" python -m tradingagents.dividends upcoming --days 30

echo ""
echo ""

# Show high-yield opportunities
echo "🌟 HIGH-YIELD OPPORTUNITIES"
echo "=================================================="
PYTHONPATH="$PROJECT_ROOT" python -m tradingagents.dividends high-yield --min-yield 4.0 --limit 10

echo ""
echo "=================================================="
echo "Generated: $(date)"
echo "=================================================="
