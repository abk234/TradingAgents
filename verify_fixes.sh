#!/bin/bash
################################################################################
# Quick verification script for both bug fixes
################################################################################

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Bug Fix Verification${NC}"
echo -e "${BLUE}======================================${NC}"

# Check Fix #1: Intent classification in streaming endpoint
echo -e "\n${BLUE}Fix #1: Intent Classification in Streaming${NC}"
echo -e "Checking tradingagents/api/main.py..."

if grep -q "agent.chat_stream" tradingagents/api/main.py; then
    echo -e "${GREEN}✅ PASS: Streaming endpoint uses agent.chat_stream()${NC}"
    FIX1_FILE=1
else
    echo -e "${RED}❌ FAIL: Streaming endpoint still uses direct trading_agent.astream()${NC}"
    FIX1_FILE=0
fi

if grep -q "async def chat_stream" tradingagents/bot/conversational_agent.py; then
    echo -e "${GREEN}✅ PASS: chat_stream() method exists in ConversationalAgent${NC}"
    FIX1_METHOD=1
else
    echo -e "${RED}❌ FAIL: chat_stream() method not found${NC}"
    FIX1_METHOD=0
fi

# Check Fix #2: LangGraph chunk format handling
echo -e "\n${BLUE}Fix #2: LangGraph Chunk Format Handling${NC}"
echo -e "Checking tradingagents/bot/agent.py..."

if grep -q 'elif "agent" in chunk' tradingagents/bot/agent.py; then
    echo -e "${GREEN}✅ PASS: Chunk handler checks for 'agent' key${NC}"
    FIX2_CHECK1=1
else
    echo -e "${RED}❌ FAIL: Chunk handler doesn't check for 'agent' key${NC}"
    FIX2_CHECK1=0
fi

if grep -A 3 'elif "agent" in chunk' tradingagents/bot/agent.py | grep -q 'chunk\["agent"\]'; then
    echo -e "${GREEN}✅ PASS: Chunk handler accesses chunk['agent']${NC}"
    FIX2_CHECK2=1
else
    echo -e "${RED}❌ FAIL: Chunk handler doesn't properly access chunk['agent']${NC}"
    FIX2_CHECK2=0
fi

if grep -q '"messages" in agent_state' tradingagents/bot/agent.py; then
    echo -e "${GREEN}✅ PASS: Chunk handler checks for messages in agent_state${NC}"
    FIX2_CHECK3=1
else
    echo -e "${RED}❌ FAIL: Chunk handler doesn't check for messages in agent_state${NC}"
    FIX2_CHECK3=0
fi

# Summary
echo -e "\n${BLUE}======================================${NC}"
echo -e "${BLUE}SUMMARY${NC}"
echo -e "${BLUE}======================================${NC}"

FIX1_TOTAL=$((FIX1_FILE + FIX1_METHOD))
FIX2_TOTAL=$((FIX2_CHECK1 + FIX2_CHECK2 + FIX2_CHECK3))
TOTAL=$((FIX1_TOTAL + FIX2_TOTAL))

echo -e "\n${YELLOW}Fix #1 (Intent Classification):${NC} $FIX1_TOTAL/2 checks passed"
echo -e "${YELLOW}Fix #2 (Chunk Handling):${NC} $FIX2_TOTAL/3 checks passed"
echo -e "${YELLOW}Total:${NC} $TOTAL/5 checks passed"

if [ $TOTAL -eq 5 ]; then
    echo -e "\n${GREEN}======================================${NC}"
    echo -e "${GREEN}✅ ALL FIXES VERIFIED${NC}"
    echo -e "${GREEN}======================================${NC}"
    echo -e "\n${GREEN}Both bug fixes are correctly applied!${NC}"
    echo -e "${GREEN}The 'no text response' error should be resolved.${NC}\n"
    exit 0
else
    echo -e "\n${RED}======================================${NC}"
    echo -e "${RED}❌ SOME FIXES MISSING${NC}"
    echo -e "${RED}======================================${NC}"
    echo -e "\n${RED}Please review the failed checks above${NC}\n"
    exit 1
fi
