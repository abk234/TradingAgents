#!/bin/bash
#
# Evaluation Wrapper Script
#
# This script provides easy access to the evaluation CLI without
# needing to set PYTHONPATH manually.
#
# Usage:
#   ./scripts/evaluate.sh backfill --days 90
#   ./scripts/evaluate.sh update
#   ./scripts/evaluate.sh report --period 90
#   ./scripts/evaluate.sh stats
#   ./scripts/evaluate.sh recent --limit 20

set -e

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Run the evaluation CLI with all arguments passed through
PYTHONPATH="$PROJECT_DIR" "$PROJECT_DIR/venv/bin/python" -m tradingagents.evaluate "$@"
