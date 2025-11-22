#!/bin/bash

################################################################################
# Test All Strategies Sequentially
#
# Usage: ./test_all_strategies.sh [TICKER]
# Default: AAPL
################################################################################

TICKER=${1:-AAPL}

echo "========================================"
echo "Testing All Strategies for $TICKER"
echo "========================================"
echo ""

STRATEGIES=("value" "growth" "dividend" "momentum" "contrarian" "quantitative" "sector_rotation" "market_structure")

for strategy in "${STRATEGIES[@]}"; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Testing: $strategy"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    python -m tradingagents.strategies run "$strategy" "$TICKER"
    echo ""
    echo ""
done

echo "========================================"
echo "All strategies tested!"
echo "========================================"

