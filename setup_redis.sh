#!/bin/bash
#
# Redis Setup Script for TradingAgents
#
# This script installs and configures Redis for optional caching.
# Redis is OPTIONAL - TradingAgents works fine without it, just slower for repeated queries.
#

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TradingAgents Redis Setup (Optional Caching)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}Note: Redis is OPTIONAL. TradingAgents works without it.${NC}"
echo "Redis provides faster repeated queries by caching API responses."
echo ""

# Check if Redis is already installed
if command -v redis-server &> /dev/null; then
    echo -e "${GREEN}✓ Redis is already installed${NC}"
    redis-server --version
else
    echo -e "${YELLOW}Redis not found. Installing...${NC}"

    # Check OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            echo "Installing Redis via Homebrew..."
            brew install redis
        else
            echo -e "${RED}✗ Homebrew not found. Please install Homebrew first:${NC}"
            echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            echo "Installing Redis via apt..."
            sudo apt-get update
            sudo apt-get install -y redis-server
        elif command -v yum &> /dev/null; then
            echo "Installing Redis via yum..."
            sudo yum install -y redis
        else
            echo -e "${RED}✗ Unsupported package manager${NC}"
            exit 1
        fi
    else
        echo -e "${RED}✗ Unsupported operating system: $OSTYPE${NC}"
        exit 1
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Starting Redis Server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if Redis is already running
if redis-cli ping &> /dev/null; then
    echo -e "${GREEN}✓ Redis is already running${NC}"
else
    echo "Starting Redis server..."

    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS with Homebrew
        brew services start redis
        echo -e "${GREEN}✓ Redis started via Homebrew services${NC}"
    else
        # Linux
        if command -v systemctl &> /dev/null; then
            sudo systemctl start redis
            sudo systemctl enable redis
            echo -e "${GREEN}✓ Redis started via systemctl${NC}"
        else
            # Start Redis in background
            redis-server --daemonize yes
            echo -e "${GREEN}✓ Redis started in background${NC}"
        fi
    fi

    # Wait for Redis to start
    sleep 2
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Testing Redis Connection"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test connection
if redis-cli ping &> /dev/null; then
    echo -e "${GREEN}✓ Redis connection successful${NC}"

    # Test set/get
    redis-cli SET test:tradingagents "operational" > /dev/null
    result=$(redis-cli GET test:tradingagents)

    if [ "$result" = "operational" ]; then
        echo -e "${GREEN}✓ Redis read/write working${NC}"
        redis-cli DEL test:tradingagents > /dev/null
    else
        echo -e "${RED}✗ Redis read/write test failed${NC}"
        exit 1
    fi

    # Show Redis info
    echo ""
    echo "Redis Info:"
    redis-cli INFO server | grep -E "redis_version|os|uptime_in_seconds"

else
    echo -e "${RED}✗ Redis connection failed${NC}"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✓ Redis Setup Complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Redis is now running and ready to cache TradingAgents queries."
echo ""
echo "Useful commands:"
echo "  Stop Redis:    brew services stop redis    (macOS)"
echo "                 sudo systemctl stop redis   (Linux)"
echo ""
echo "  Start Redis:   brew services start redis   (macOS)"
echo "                 sudo systemctl start redis  (Linux)"
echo ""
echo "  Redis CLI:     redis-cli"
echo "  Monitor cache: redis-cli MONITOR"
echo "  Flush cache:   redis-cli FLUSHALL"
echo ""
