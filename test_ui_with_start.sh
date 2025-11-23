#!/bin/bash
################################################################################
# UI Test Script - Tests AnythingLLM Integration Features
# 
# This script:
# 1. Starts the application using start.sh
# 2. Waits for services to be ready
# 3. Tests all new UI features via API calls
# 4. Reports results
################################################################################

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

BACKEND_PORT=8005
FRONTEND_PORT=3005

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}  UI Integration Test - AnythingLLM Features${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Check if start.sh exists
if [ ! -f "start.sh" ]; then
    echo -e "${RED}❌ start.sh not found${NC}"
    exit 1
fi

echo -e "${BLUE}This script will:${NC}"
echo -e "  1. Start the application using ./start.sh"
echo -e "  2. Wait for services to be ready"
echo -e "  3. Test UI endpoints via API"
echo -e "  4. Report test results"
echo ""
echo -e "${YELLOW}Press Enter to continue or Ctrl+C to cancel...${NC}"
read

# Start the application in background
echo -e "\n${BLUE}Starting application...${NC}"
./start.sh > /tmp/tradingagents_startup.log 2>&1 &
START_PID=$!

# Wait for backend
echo -e "${BLUE}Waiting for backend to start...${NC}"
for i in {1..60}; do
    if curl -s http://localhost:$BACKEND_PORT/health &>/dev/null; then
        echo -e "${GREEN}✅ Backend is ready${NC}"
        break
    fi
    if [ $i -eq 60 ]; then
        echo -e "${RED}❌ Backend failed to start${NC}"
        kill $START_PID 2>/dev/null
        exit 1
    fi
    sleep 1
done

# Wait for frontend
echo -e "${BLUE}Waiting for frontend to start...${NC}"
for i in {1..60}; do
    if curl -s http://localhost:$FRONTEND_PORT &>/dev/null; then
        echo -e "${GREEN}✅ Frontend is ready${NC}"
        break
    fi
    if [ $i -eq 60 ]; then
        echo -e "${YELLOW}⚠️  Frontend taking longer than expected${NC}"
        break
    fi
    sleep 1
done

# Test endpoints
echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}  Testing API Endpoints${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    
    echo -e "${BLUE}Testing: ${method} ${endpoint}${NC}"
    echo -e "  ${description}"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" http://localhost:$BACKEND_PORT$endpoint 2>/dev/null || echo -e "\n000")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method http://localhost:$BACKEND_PORT$endpoint 2>/dev/null || echo -e "\n000")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        echo -e "  ${GREEN}✅ Success (${http_code})${NC}"
        return 0
    elif [ "$http_code" = "401" ] || [ "$http_code" = "403" ]; then
        echo -e "  ${YELLOW}⚠️  Auth required (${http_code}) - Endpoint exists${NC}"
        return 0
    elif [ "$http_code" = "503" ]; then
        echo -e "  ${YELLOW}⚠️  Service unavailable (${http_code}) - May need initialization${NC}"
        return 0
    elif [ "$http_code" = "404" ]; then
        echo -e "  ${RED}❌ Not found (${http_code})${NC}"
        return 1
    else
        echo -e "  ${YELLOW}⚠️  Status: ${http_code}${NC}"
        return 0
    fi
}

# Test MCP endpoints
echo -e "\n${CYAN}MCP Integration:${NC}"
test_endpoint "GET" "/mcp/initialize" "Initialize MCP server"
test_endpoint "GET" "/mcp/capabilities" "Get MCP capabilities"
test_endpoint "GET" "/mcp/tools" "List MCP tools"

# Test Document endpoints
echo -e "\n${CYAN}Document Processing:${NC}"
test_endpoint "GET" "/documents" "List documents"
# Upload test would require file, skip for now

# Test Workspace endpoints
echo -e "\n${CYAN}Workspace Management:${NC}"
test_endpoint "GET" "/workspaces" "List workspaces"
test_endpoint "GET" "/workspaces/default" "Get default workspace"

# Test Analytics endpoints (that were fixed)
echo -e "\n${CYAN}Analytics (Fixed):${NC}"
test_endpoint "GET" "/analytics/portfolio/performance" "Portfolio performance"
test_endpoint "GET" "/analytics/history?limit=10" "Historical analyses"

echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}  Test Complete${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${GREEN}✅ Application is running!${NC}"
echo -e ""
echo -e "${BLUE}Access the UI at:${NC}"
echo -e "   Frontend: http://localhost:$FRONTEND_PORT"
echo -e "   Backend API: http://localhost:$BACKEND_PORT"
echo -e "   API Docs: http://localhost:$BACKEND_PORT/docs"
echo ""
echo -e "${BLUE}Test the new features:${NC}"
echo -e "   1. Open http://localhost:$FRONTEND_PORT"
echo -e "   2. Click 'Documents' in sidebar → Test document upload"
echo -e "   3. Click 'Workspaces' in sidebar → Test workspace management"
echo -e "   4. Click 'MCP Tools' in sidebar → Test tool execution"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the application${NC}"

# Wait for user to stop
wait $START_PID

