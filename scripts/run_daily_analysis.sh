#!/bin/bash
#
# Daily Analysis Script
#
# This script runs the daily screener and analyzes top opportunities.
# It populates the database with analyses that Phase 6 can then track.
#
# Usage:
#   ./scripts/run_daily_analysis.sh
#
# For faster analysis (2-3 min for 3 stocks):
#   ./scripts/run_daily_analysis.sh --fast
#
# For deeper analysis (5-7 min for 3 stocks):
#   ./scripts/run_daily_analysis.sh --deep

set -e

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "=================================================="
echo "Daily Analysis - $(date '+%Y-%m-%d %H:%M:%S')"
echo "=================================================="
echo

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Default settings
ANALYSIS_LIMIT=3
PORTFOLIO_VALUE=100000
FAST_MODE=""
RAG_MODE=""

# Parse arguments
if [[ "$1" == "--fast" ]]; then
    FAST_MODE="--fast --no-rag"
    echo "🚀 Fast mode enabled (2-3 min)"
elif [[ "$1" == "--deep" ]]; then
    FAST_MODE=""
    RAG_MODE=""
    echo "🔬 Deep analysis mode (5-7 min)"
else
    # Default: Fast mode without RAG
    FAST_MODE="--fast --no-rag"
    echo "🚀 Fast mode enabled by default (2-3 min)"
fi

echo "Analyzing top $ANALYSIS_LIMIT stocks..."
echo "Portfolio value: \$$PORTFOLIO_VALUE"
echo

# Run screener with analysis
PYTHONPATH="$PROJECT_DIR" venv/bin/python -m tradingagents.screener run \
    --with-analysis \
    $FAST_MODE \
    --analysis-limit $ANALYSIS_LIMIT \
    --portfolio-value $PORTFOLIO_VALUE

echo
echo "=================================================="
echo "✅ Daily Analysis Complete"
echo "=================================================="
echo
echo "Next steps:"
echo "  1. Review recommendations above"
echo "  2. After 24 hours, run: ./scripts/evaluate.sh update"
echo "  3. After 30 days, check performance: ./scripts/evaluate.sh report"
