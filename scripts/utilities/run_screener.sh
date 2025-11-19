#!/bin/bash
#
# Quick Screener Runner - Wrapper to run screener with proper environment
#

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Run screener with all arguments passed through
PYTHONPATH="$SCRIPT_DIR" python -m tradingagents.screener "$@"
