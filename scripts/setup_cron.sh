#!/bin/bash
# Investment Intelligence System - Cron Setup Script
#
# This script helps set up automated daily screening
#
# Usage:
#   ./scripts/setup_cron.sh

echo "======================================================================="
echo "Investment Intelligence System - Cron Automation Setup"
echo "======================================================================="
echo ""

# Get project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="$PROJECT_DIR/venv/bin/python"

# Verify Python and project exist
if [ ! -f "$PYTHON_BIN" ]; then
    echo "Error: Python virtual environment not found at $PYTHON_BIN"
    echo "Please run from the project root directory"
    exit 1
fi

# Cron job command
CRON_COMMAND="0 7 * * 1-5 cd $PROJECT_DIR && $PYTHON_BIN -m tradingagents.screener run >> $HOME/iis_screener.log 2>&1"

echo "This will set up a daily screener to run:"
echo "  - Every weekday (Monday-Friday)"
echo "  - At 7:00 AM (before market open)"
echo "  - Logs to: $HOME/iis_screener.log"
echo ""
echo "Cron command:"
echo "  $CRON_COMMAND"
echo ""

read -p "Do you want to add this cron job? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup cancelled"
    exit 0
fi

# Add to crontab
(crontab -l 2>/dev/null | grep -v "tradingagents.screener"; echo "$CRON_COMMAND") | crontab -

if [ $? -eq 0 ]; then
    echo "✓ Cron job added successfully"
    echo ""
    echo "To view your cron jobs:"
    echo "  crontab -l"
    echo ""
    echo "To remove this job:"
    echo "  crontab -e"
    echo "  (then delete the line containing 'tradingagents.screener')"
    echo ""
    echo "To test manually:"
    echo "  cd $PROJECT_DIR"
    echo "  venv/bin/python -m tradingagents.screener run"
else
    echo "✗ Failed to add cron job"
    exit 1
fi

echo ""
echo "======================================================================="
echo "Setup Complete!"
echo "======================================================================="
