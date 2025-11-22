#!/bin/bash

################################################################################
# TradingAgents Integration Validation Script
# 
# This script validates that frontend, backend, and middleware are properly
# integrated and working together.
################################################################################

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Configuration
BACKEND_URL="${BACKEND_URL:-http://localhost:8005}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3005}"
VENV_PATH="${VENV_PATH:-venv}"

print_header() {
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}→${NC} $1"
}

# Check if services are running
check_backend() {
    print_info "Checking backend..."
    if curl -s "${BACKEND_URL}/health" > /dev/null 2>&1; then
        print_success "Backend is running"
        return 0
    else
        print_error "Backend is not running. Please start it with: ./start.sh or python -m tradingagents.api.main"
        return 1
    fi
}

check_frontend() {
    print_info "Checking frontend..."
    if curl -s "${FRONTEND_URL}" > /dev/null 2>&1; then
        print_success "Frontend is running"
        return 0
    else
        print_error "Frontend is not running. Please start it with: cd web-app && npm run dev -- -p 3005"
        return 1
    fi
}

# Run integration tests
run_integration_tests() {
    print_header "Running Integration Tests"
    
    if [ -d "$VENV_PATH" ]; then
        PYTHON="$VENV_PATH/bin/python"
    else
        PYTHON="python3"
    fi
    
    print_info "Running test_integration.py..."
    if $PYTHON test_integration.py; then
        print_success "Integration tests passed"
        return 0
    else
        print_error "Integration tests failed"
        return 1
    fi
}

# Run E2E tests
run_e2e_tests() {
    print_header "Running End-to-End Tests"
    
    if [ -d "$VENV_PATH" ]; then
        PYTHON="$VENV_PATH/bin/python"
    else
        PYTHON="python3"
    fi
    
    print_info "Running test_e2e.py..."
    if $PYTHON test_e2e.py; then
        print_success "E2E tests passed"
        return 0
    else
        print_error "E2E tests failed"
        return 1
    fi
}

# Check system health
check_system_health() {
    print_header "Checking System Health"
    
    if [ -d "$VENV_PATH" ]; then
        PYTHON="$VENV_PATH/bin/python"
    else
        PYTHON="python3"
    fi
    
    print_info "Running monitor_system.py..."
    $PYTHON monitor_system.py
}

# Analyze logs
analyze_logs() {
    print_header "Analyzing Logs"
    
    if [ -d "$VENV_PATH" ]; then
        PYTHON="$VENV_PATH/bin/python"
    else
        PYTHON="python3"
    fi
    
    print_info "Running analyze_logs.py..."
    $PYTHON analyze_logs.py
}

# Main execution
main() {
    print_header "TradingAgents Integration Validation"
    
    echo -e "${BLUE}Configuration:${NC}"
    echo "   Backend URL: ${BACKEND_URL}"
    echo "   Frontend URL: ${FRONTEND_URL}"
    echo ""
    
    # Check services
    BACKEND_OK=false
    FRONTEND_OK=false
    
    if check_backend; then
        BACKEND_OK=true
    fi
    
    if check_frontend; then
        FRONTEND_OK=true
    fi
    
    if [ "$BACKEND_OK" = false ] || [ "$FRONTEND_OK" = false ]; then
        echo -e "\n${YELLOW}⚠️  Some services are not running.${NC}"
        echo "Please start the services before running validation."
        exit 1
    fi
    
    # Run tests
    INTEGRATION_OK=true
    E2E_OK=true
    
    if ! run_integration_tests; then
        INTEGRATION_OK=false
    fi
    
    if ! run_e2e_tests; then
        E2E_OK=false
    fi
    
    # System health and logs
    check_system_health
    analyze_logs
    
    # Final summary
    print_header "Validation Summary"
    
    if [ "$INTEGRATION_OK" = true ] && [ "$E2E_OK" = true ]; then
        print_success "All validation tests passed!"
        echo ""
        echo -e "${GREEN}✓ Integration tests: PASSED${NC}"
        echo -e "${GREEN}✓ E2E tests: PASSED${NC}"
        echo ""
        echo -e "${BLUE}Your TradingAgents system is properly integrated and working!${NC}"
        exit 0
    else
        print_error "Some validation tests failed"
        echo ""
        [ "$INTEGRATION_OK" = false ] && echo -e "${RED}✗ Integration tests: FAILED${NC}"
        [ "$E2E_OK" = false ] && echo -e "${RED}✗ E2E tests: FAILED${NC}"
        echo ""
        echo -e "${YELLOW}Please review the errors above and fix any issues.${NC}"
        exit 1
    fi
}

# Parse arguments
case "${1:-}" in
    --integration-only)
        check_backend && check_frontend && run_integration_tests
        ;;
    --e2e-only)
        check_backend && check_frontend && run_e2e_tests
        ;;
    --health-only)
        check_system_health
        ;;
    --logs-only)
        analyze_logs
        ;;
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --integration-only  Run only integration tests"
        echo "  --e2e-only          Run only E2E tests"
        echo "  --health-only       Check system health only"
        echo "  --logs-only         Analyze logs only"
        echo "  --help, -h          Show this help message"
        echo ""
        echo "Default: Run all validation checks"
        exit 0
        ;;
    *)
        main
        ;;
esac

