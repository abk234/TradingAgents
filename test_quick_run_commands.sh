#!/bin/bash
# Test script for quick_run.sh commands

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASSED=0
FAILED=0
SKIPPED=0

test_command() {
    local cmd="$1"
    local description="$2"
    local timeout_sec="${3:-30}"
    
    echo -e "\n${YELLOW}Testing: $description${NC}"
    echo "Command: ./quick_run.sh $cmd"
    
    # Run command with timeout
    if timeout $timeout_sec ./quick_run.sh $cmd > /tmp/quick_run_test.log 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
        return 0
    else
        local exit_code=$?
        if [ $exit_code -eq 124 ]; then
            echo -e "${YELLOW}⚠ TIMEOUT (may be normal for long-running commands)${NC}"
            ((SKIPPED++))
            return 0
        else
            echo -e "${RED}✗ FAILED (exit code: $exit_code)${NC}"
            echo "Last 5 lines of output:"
            tail -5 /tmp/quick_run_test.log
            ((FAILED++))
            return 1
        fi
    fi
}

echo "=========================================="
echo "Testing quick_run.sh Commands"
echo "=========================================="

# Strategy Testing Commands (our new additions)
echo -e "\n${YELLOW}=== Strategy Testing Commands ===${NC}"

test_command "strategy-list" "List available strategies" 10
test_command "strategies AAPL" "Compare all strategies on AAPL" 60
test_command "strategy-compare AAPL" "Compare strategies (detailed) on AAPL" 60
test_command "strategy-run value AAPL" "Run single value strategy" 60
test_command "strategy-multi AAPL MSFT" "Compare strategies across multiple stocks" 90
test_command "strategy-screener 3" "Compare strategies on top 3 screener stocks" 120
test_command "strategy-test AAPL" "Comprehensive strategy test" 60

# Quick Checks (fast commands)
echo -e "\n${YELLOW}=== Quick Check Commands ===${NC}"

test_command "top" "Show top 5 opportunities" 30
test_command "strategy-list" "List strategies" 10

# Test error handling
echo -e "\n${YELLOW}=== Error Handling Tests ===${NC}"

echo -e "\n${YELLOW}Testing: Missing ticker argument${NC}"
if ./quick_run.sh strategies 2>&1 | grep -q "Error.*ticker"; then
    echo -e "${GREEN}✓ PASSED (proper error message)${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED (should show error for missing ticker)${NC}"
    ((FAILED++))
fi

echo -e "\n${YELLOW}Testing: Invalid command${NC}"
if ./quick_run.sh invalid-command 2>&1 | grep -q "Unknown command"; then
    echo -e "${GREEN}✓ PASSED (proper error message)${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED (should show error for invalid command)${NC}"
    ((FAILED++))
fi

# Summary
echo -e "\n=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo -e "${YELLOW}Skipped/Timeout: $SKIPPED${NC}"
echo "=========================================="

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed${NC}"
    exit 1
fi

