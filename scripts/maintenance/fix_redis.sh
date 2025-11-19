#!/bin/bash
#
# Fix Redis Authentication for TradingAgents
#
# Redis is currently requiring authentication. For local development,
# we'll disable authentication to simplify the setup.
#

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Fixing Redis Configuration for TradingAgents"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Backup existing config
CONFIG_FILE="/opt/homebrew/etc/redis.conf"
BACKUP_FILE="/opt/homebrew/etc/redis.conf.backup.$(date +%Y%m%d_%H%M%S)"

if [ -f "$CONFIG_FILE" ]; then
    echo "Backing up Redis config..."
    cp "$CONFIG_FILE" "$BACKUP_FILE"
    echo -e "${GREEN}✓ Backup created: $BACKUP_FILE${NC}"
else
    echo -e "${YELLOW}⚠ Config file not found, creating default${NC}"
fi

# Stop Redis
echo ""
echo "Stopping Redis..."
brew services stop redis
sleep 2

# Create new config without authentication
echo "Creating Redis config without authentication..."

cat > "$CONFIG_FILE" << 'EOF'
# Redis Configuration for TradingAgents
# Local development setup - No authentication required

# Bind to localhost only for security
bind 127.0.0.1

# Port
port 6379

# Disable protected mode for localhost connections
protected-mode no

# No authentication required (local development only)
# requirepass ""

# Save to disk (optional)
save 900 1
save 300 10
save 60 10000

# Database file
dbfilename dump.rdb
dir /opt/homebrew/var/db/redis/

# Logging
loglevel notice
logfile /opt/homebrew/var/log/redis.log

# Memory management
maxmemory 256mb
maxmemory-policy allkeys-lru

# Append only file
appendonly no
EOF

echo -e "${GREEN}✓ Config updated${NC}"

# Start Redis with new config
echo ""
echo "Starting Redis with new configuration..."
brew services start redis

# Wait for Redis to start
sleep 3

# Test connection (no auth needed now)
echo ""
echo "Testing Redis connection..."

if redis-cli ping > /dev/null 2>&1; then
    result=$(redis-cli ping)
    echo -e "${GREEN}✓ Redis ping: $result${NC}"

    # Test set/get
    redis-cli SET test:tradingagents "working" > /dev/null 2>&1
    value=$(redis-cli GET test:tradingagents)

    if [ "$value" = "working" ]; then
        echo -e "${GREEN}✓ Redis read/write: OK${NC}"
        redis-cli DEL test:tradingagents > /dev/null 2>&1

        # Show Redis info
        echo ""
        echo "Redis Info:"
        redis-cli INFO server | grep -E "redis_version|os|uptime_in_seconds" | head -3

        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo -e "${GREEN}✓ Redis is now operational!${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "TradingAgents can now use Redis for caching."
        echo "This will speed up repeated API calls."

        exit 0
    else
        echo -e "${RED}✗ Redis read/write failed${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Redis connection failed${NC}"
    echo ""
    echo "Debug info:"
    brew services list | grep redis
    echo ""
    echo "Try restarting manually:"
    echo "  brew services restart redis"
    exit 1
fi
