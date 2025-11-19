#!/bin/bash
#
# Quick Start Script for Eddie
# Kills any existing processes and starts fresh
#

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}Cleaning up any existing processes...${NC}"

# Kill any processes on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null

# Kill any chainlit or tradingagents processes
pkill -f "chainlit run" 2>/dev/null
pkill -f "tradingagents.bot" 2>/dev/null

sleep 2

# Check if port is free
if lsof -ti:8000 > /dev/null 2>&1; then
    echo -e "${RED}⚠️  Port 8000 still in use. Trying to free it...${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    sleep 2
fi

# Verify port is free
if lsof -ti:8000 > /dev/null 2>&1; then
    echo -e "${RED}❌ Could not free port 8000. Please manually kill the process.${NC}"
    echo "Run: lsof -ti:8000 | xargs kill -9"
    exit 1
fi

echo -e "${GREEN}✅ Port 8000 is free${NC}"
echo ""
echo -e "${YELLOW}Starting Eddie...${NC}"
echo ""

# Start the application
./trading_bot.sh

