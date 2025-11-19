#!/bin/bash

# Eddie Quick Analysis Script
# Quickly analyze a stock with all validation checks
#
# Usage:
#   ./scripts/eddie_quick_analysis.sh AAPL [PORTFOLIO_VALUE]
#
# Example:
#   ./scripts/eddie_quick_analysis.sh AAPL 100000

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

TICKER="${1:-}"
PORTFOLIO_VALUE="${2:-100000}"

if [ -z "$TICKER" ]; then
    echo -e "${RED}❌ Please provide a ticker symbol${NC}"
    echo "Usage: $0 [TICKER] [PORTFOLIO_VALUE]"
    echo "Example: $0 AAPL 100000"
    exit 1
fi

echo -e "\n${BLUE}🔍 Quick Analysis Workflow for $TICKER${NC}"
echo "=========================================="
echo -e "Portfolio Value: \$$PORTFOLIO_VALUE\n"

# Generate conversation script
cat << EOF
# Eddie Conversation Script for $TICKER
# Generated: $(date)
# Portfolio Value: \$$PORTFOLIO_VALUE

## Step 1: Quick Checks (5-15 seconds each)
"What's the news on $TICKER?"
"Show me $TICKER's technicals"
"What's the sentiment on $TICKER?"
"$TICKER's fundamentals?"

## Step 2: Full Analysis (30-90 seconds)
"Should I buy $TICKER? Portfolio \$$PORTFOLIO_VALUE"

## Step 3: Validation (Critical!)
"Check earnings risk for $TICKER"
"Validate price sources for $TICKER"
"Check data quality for $TICKER"

## Step 4: Learning & Pattern Recognition
"What did you learn about $TICKER?"
"Have you seen this pattern before?"

## Step 5: Decision
Review all information above, then:
- If BUY: Execute trade in your broker
- If HOLD/WAIT: Monitor and wait for better entry
- If SELL: Exit position

## Trade Execution Checklist
- [ ] Got Eddie's recommendation
- [ ] Checked earnings risk (LOW)
- [ ] Validated price sources (>8/10)
- [ ] Checked data quality (>7/10)
- [ ] Reviewed track record
- [ ] Calculated position size
- [ ] Set stop loss
- [ ] Set target price
- [ ] Executed trade in broker

## Position Details (Fill in after analysis)
- Entry Price: \$___
- Stop Loss: \$___
- Target Price: \$___
- Position Size: ___% = \$$___
- Shares: ___
- Expected Return: ___%
- Hold Period: ___ days

EOF

echo -e "\n${GREEN}✅ Conversation script generated${NC}"
echo -e "${BLUE}Copy the questions above and ask Eddie in the web interface${NC}"
echo -e "${YELLOW}Eddie URL: http://localhost:8000${NC}\n"

