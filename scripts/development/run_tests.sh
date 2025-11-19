#!/bin/bash
# Test runner script for TradingAgents

set -e

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "TradingAgents Test Suite"
echo "=========================================="
echo ""

# Set PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Test categories
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run tests
run_test() {
    local test_name=$1
    local test_path=$2
    
    echo -e "${YELLOW}Running: $test_name${NC}"
    if python -m pytest "$test_path" -v 2>/dev/null || python "$test_path" 2>/dev/null; then
        echo -e "${GREEN}✅ $test_name PASSED${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ $test_name FAILED${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
    echo ""
}

# Run strategy system tests
echo "=== Strategy System Tests ==="
if [ -f "$PROJECT_ROOT/tests/test_strategy_system.py" ]; then
    run_test "Strategy System" "$PROJECT_ROOT/tests/test_strategy_system.py"
fi

# Run unit tests
echo ""
echo "=== Unit Tests ==="
if [ -d "$PROJECT_ROOT/tests/strategies" ]; then
    for test_file in "$PROJECT_ROOT/tests/strategies"/test_*.py; do
        if [ -f "$test_file" ]; then
            test_name=$(basename "$test_file" .py)
            run_test "$test_name" "$test_file"
        fi
    done
fi

# Summary
echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "${RED}Failed: $TESTS_FAILED${NC}"
    exit 1
else
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
fi

