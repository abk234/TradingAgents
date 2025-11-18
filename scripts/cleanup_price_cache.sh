#!/bin/bash
# Cleanup stale price cache entries
# This script should be run periodically (e.g., hourly via cron)

set -e

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# Change to project directory
cd "$PROJECT_DIR"

# Set Python path
export PYTHONPATH="$PROJECT_DIR"

# Run cleanup
echo "$(date): Starting price cache cleanup..."

venv/bin/python << 'EOF'
from tradingagents.database import get_db_connection
from tradingagents.database.price_cache_ops import PriceCacheOperations
import logging
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    db = get_db_connection()
    cache_ops = PriceCacheOperations(db)

    # Run cleanup
    result = cache_ops.cleanup_stale_cache()
    logger.info(f"Cache cleanup complete: {result}")

    # Get stats
    stats = cache_ops.get_cache_stats()
    logger.info(f"Cache stats: {stats}")

    sys.exit(0)

except Exception as e:
    logger.error(f"Cache cleanup failed: {e}")
    sys.exit(1)
EOF

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "$(date): Cache cleanup completed successfully"
else
    echo "$(date): Cache cleanup failed with exit code $EXIT_CODE"
fi

exit $EXIT_CODE
