#!/bin/bash

################################################################################
# API Key Validation Script
# Checks if all required API keys are configured
################################################################################

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  🔑 API Key Configuration Check${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

ERRORS=0
WARNINGS=0

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo -e "${YELLOW}   Creating from .env.example...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}   ✅ .env created. Please edit it with your API keys.${NC}\n"
    else
        echo -e "${RED}   ❌ .env.example also not found!${NC}\n"
        exit 1
    fi
fi

# Load .env
if [ -f ".env" ]; then
    source .env
fi

# Check OpenAI API Key (Required)
echo -e "${BLUE}Checking OpenAI API Key (Required)...${NC}"
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}❌ OPENAI_API_KEY is not set${NC}"
    ERRORS=$((ERRORS + 1))
elif [ "$OPENAI_API_KEY" = "your-openai-api-key-here" ]; then
    echo -e "${RED}❌ OPENAI_API_KEY is still the placeholder value${NC}"
    echo -e "${YELLOW}   Get your key from: https://platform.openai.com/api-keys${NC}"
    ERRORS=$((ERRORS + 1))
elif [[ ! "$OPENAI_API_KEY" =~ ^sk- ]]; then
    echo -e "${YELLOW}⚠️  OPENAI_API_KEY doesn't start with 'sk-' (might be invalid)${NC}"
    WARNINGS=$((WARNINGS + 1))
else
    # Test the API key
    echo -e "${BLUE}   Testing API key...${NC}"
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: Bearer $OPENAI_API_KEY" \
        https://api.openai.com/v1/models \
        --max-time 10)

    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✅ OPENAI_API_KEY is valid and working${NC}"
    elif [ "$HTTP_CODE" = "401" ]; then
        echo -e "${RED}❌ OPENAI_API_KEY is invalid (401 Unauthorized)${NC}"
        ERRORS=$((ERRORS + 1))
    elif [ "$HTTP_CODE" = "000" ]; then
        echo -e "${YELLOW}⚠️  Cannot connect to OpenAI API (network issue)${NC}"
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "${YELLOW}⚠️  Unexpected response code: $HTTP_CODE${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
fi

# Check Alpha Vantage API Key (Required for default config)
echo -e "\n${BLUE}Checking Alpha Vantage API Key...${NC}"
if [ -z "$ALPHA_VANTAGE_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  ALPHA_VANTAGE_API_KEY is not set${NC}"
    echo -e "${YELLOW}   Get your free key from: https://www.alphavantage.co/support/#api-key${NC}"
    WARNINGS=$((WARNINGS + 1))
elif [ "$ALPHA_VANTAGE_API_KEY" = "your-alpha-vantage-api-key-here" ]; then
    echo -e "${YELLOW}⚠️  ALPHA_VANTAGE_API_KEY is still the placeholder value${NC}"
    echo -e "${YELLOW}   Get your free key from: https://www.alphavantage.co/support/#api-key${NC}"
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}✅ ALPHA_VANTAGE_API_KEY is configured${NC}"
fi

# Check Optional API Keys
echo -e "\n${BLUE}Checking Optional API Keys...${NC}"

# Anthropic (Claude)
if [ -n "$ANTHROPIC_API_KEY" ] && [ "$ANTHROPIC_API_KEY" != "your-anthropic-api-key-here" ]; then
    echo -e "${GREEN}✅ ANTHROPIC_API_KEY is configured (optional)${NC}"
else
    echo -e "${BLUE}ℹ️  ANTHROPIC_API_KEY not configured (optional)${NC}"
fi

# Google (Gemini)
if [ -n "$GOOGLE_API_KEY" ] && [ "$GOOGLE_API_KEY" != "your-google-api-key-here" ]; then
    echo -e "${GREEN}✅ GOOGLE_API_KEY is configured (optional)${NC}"
else
    echo -e "${BLUE}ℹ️  GOOGLE_API_KEY not configured (optional)${NC}"
fi

# Summary
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  📊 Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}❌ Critical Errors: $ERRORS${NC}"
    echo -e "${RED}   The application will NOT work until these are fixed.${NC}\n"

    echo -e "${YELLOW}🔧 How to fix:${NC}"
    echo -e "   1. Open .env file: ${BLUE}nano .env${NC}"
    echo -e "   2. Replace placeholder values with real API keys"
    echo -e "   3. Save and run this script again\n"

    echo -e "${YELLOW}📚 Where to get API keys:${NC}"
    echo -e "   OpenAI:        https://platform.openai.com/api-keys"
    echo -e "   Alpha Vantage: https://www.alphavantage.co/support/#api-key"
    echo ""
    exit 1
fi

if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Warnings: $WARNINGS${NC}"
    echo -e "${YELLOW}   The application may work with limited functionality.${NC}\n"
else
    echo -e "${GREEN}✅ All required API keys are configured!${NC}\n"
fi

echo -e "${GREEN}🚀 You can now start the application with: ${BLUE}./start.sh${NC}\n"
exit 0
