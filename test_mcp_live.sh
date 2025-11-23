#!/bin/bash
################################################################################
# Live MCP Tools Test Script
# 
# This script tests MCP tools via the running API server.
# Make sure ./start.sh is running first!
################################################################################

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

BASE_URL="http://localhost:8005"

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}  Testing MCP Tools via Live API${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Check if server is running
echo -e "${BLUE}Checking if server is running...${NC}"
if ! curl -s "${BASE_URL}/health" > /dev/null 2>&1 && ! curl -s "${BASE_URL}/docs" > /dev/null 2>&1; then
    echo -e "${RED}❌ Server is not running!${NC}"
    echo -e "${YELLOW}Please run: ./start.sh${NC}"
    echo -e "${YELLOW}Then wait for services to start and run this script again.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Server is running${NC}\n"

# Test 1: List tools
echo -e "${BLUE}1. Testing GET /mcp/tools...${NC}"
TOOLS_RESPONSE=$(curl -s "${BASE_URL}/mcp/tools" 2>&1)
if echo "$TOOLS_RESPONSE" | grep -q '"tools"'; then
    TOOL_COUNT=$(echo "$TOOLS_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('count', 0))" 2>/dev/null || echo "?")
    echo -e "${GREEN}   ✅ Success: Found ${TOOL_COUNT} tools${NC}"
else
    echo -e "${RED}   ❌ Failed to list tools${NC}"
    echo "$TOOLS_RESPONSE" | head -5
    exit 1
fi

# Test 2: Get capabilities
echo -e "\n${BLUE}2. Testing GET /mcp/capabilities...${NC}"
CAPS_RESPONSE=$(curl -s "${BASE_URL}/mcp/capabilities" 2>&1)
if echo "$CAPS_RESPONSE" | grep -q '"capabilities"'; then
    echo -e "${GREEN}   ✅ Success: Capabilities retrieved${NC}"
else
    echo -e "${YELLOW}   ⚠️  Unexpected response${NC}"
fi

# Test 3: Call show_legend (no args)
echo -e "\n${BLUE}3. Testing POST /mcp/tools/show_legend...${NC}"
LEGEND_RESPONSE=$(curl -s -X POST "${BASE_URL}/mcp/tools/show_legend" \
    -H "Content-Type: application/json" \
    -d '{"arguments": {}}' 2>&1)
if echo "$LEGEND_RESPONSE" | grep -q '"isError"'; then
    IS_ERROR=$(echo "$LEGEND_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('isError', True))" 2>/dev/null || echo "true")
    if [ "$IS_ERROR" = "False" ]; then
        echo -e "${GREEN}   ✅ Success: Tool executed${NC}"
    else
        echo -e "${YELLOW}   ⚠️  Tool returned error${NC}"
    fi
else
    echo -e "${RED}   ❌ Failed to execute tool${NC}"
    echo "$LEGEND_RESPONSE" | head -3
fi

# Test 4: Call analyze_sector (with args)
echo -e "\n${BLUE}4. Testing POST /mcp/tools/analyze_sector...${NC}"
SECTOR_RESPONSE=$(curl -s -X POST "${BASE_URL}/mcp/tools/analyze_sector" \
    -H "Content-Type: application/json" \
    -d '{"arguments": {"sector_name": "Technology"}}' 2>&1)
if echo "$SECTOR_RESPONSE" | grep -q '"isError"'; then
    IS_ERROR=$(echo "$SECTOR_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('isError', True))" 2>/dev/null || echo "true")
    if [ "$IS_ERROR" = "False" ]; then
        echo -e "${GREEN}   ✅ Success: Sector analysis completed${NC}"
    else
        ERROR_TEXT=$(echo "$SECTOR_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('content', [{}])[0].get('text', 'Unknown')[:100])" 2>/dev/null || echo "Unknown error")
        echo -e "${YELLOW}   ⚠️  Tool returned error: ${ERROR_TEXT}${NC}"
    fi
else
    echo -e "${RED}   ❌ Failed to execute tool${NC}"
    echo "$SECTOR_RESPONSE" | head -3
fi

# Test 5: List resources
echo -e "\n${BLUE}5. Testing GET /mcp/resources...${NC}"
RESOURCES_RESPONSE=$(curl -s "${BASE_URL}/mcp/resources" 2>&1)
if echo "$RESOURCES_RESPONSE" | grep -q '"resources"'; then
    RESOURCE_COUNT=$(echo "$RESOURCES_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('count', 0))" 2>/dev/null || echo "?")
    echo -e "${GREEN}   ✅ Success: Found ${RESOURCE_COUNT} resources${NC}"
else
    echo -e "${YELLOW}   ⚠️  Unexpected response${NC}"
fi

# Summary
echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}  Test Complete${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${GREEN}✅ MCP Tools are accessible via API${NC}"
echo -e "\n${BLUE}You can also test via:${NC}"
echo -e "   - Frontend UI: http://localhost:3005"
echo -e "   - API Docs: http://localhost:8005/docs"
echo -e "   - MCP Tools View: http://localhost:3005 (click 'MCP Tools' in sidebar)"

