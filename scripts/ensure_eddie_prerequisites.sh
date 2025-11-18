#!/bin/bash
# Ensure Eddie Prerequisites
# Populates database with required data for Eddie to make valid trading decisions

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "🔧 Ensuring Eddie Prerequisites..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 1. Check database connection
echo "1️⃣ Checking database connection..."
python -c "from tradingagents.database import get_db_connection; get_db_connection()" || {
    echo "❌ Database connection failed. Please check PostgreSQL is running."
    exit 1
}
echo "✅ Database connected"
echo ""

# 2. Populate price cache for active tickers
echo "2️⃣ Populating price cache for active tickers..."
python << 'PYTHON_SCRIPT'
from tradingagents.database import get_db_connection, TickerOperations
from tradingagents.dataflows.interface import route_to_vendor_with_cache
from datetime import date, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = get_db_connection()
ticker_ops = TickerOperations(db)

# Get active tickers
active_tickers = ticker_ops.get_all_tickers(active_only=True)
print(f"Found {len(active_tickers)} active tickers")

# Cache prices for each ticker (last 90 days)
start_date = (date.today() - timedelta(days=90)).strftime('%Y-%m-%d')
end_date = date.today().strftime('%Y-%m-%d')

cached_count = 0
for ticker in active_tickers[:20]:  # Limit to first 20 for speed
    symbol = ticker['symbol']
    try:
        print(f"  Caching prices for {symbol}...")
        route_to_vendor_with_cache('get_stock_data', symbol, start_date, end_date)
        cached_count += 1
    except Exception as e:
        print(f"  ⚠️  Failed to cache {symbol}: {e}")
        continue

print(f"✅ Cached prices for {cached_count} tickers")
PYTHON_SCRIPT

echo ""

# 3. Run daily screener if needed
echo "3️⃣ Checking daily scans..."
python << 'PYTHON_SCRIPT'
from tradingagents.database import get_db_connection
from datetime import date

db = get_db_connection()
with db.get_cursor() as cursor:
    cursor.execute("""
        SELECT MAX(scan_date) as latest_scan
        FROM daily_scans
    """)
    row = cursor.fetchone()
    latest_scan = row[0] if row else None

if latest_scan and (date.today() - latest_scan).days <= 1:
    print(f"✅ Recent scan found: {latest_scan}")
else:
    print("⚠️  No recent scan found. Run: python -m tradingagents.screener")
PYTHON_SCRIPT

echo ""

# 4. Validate prerequisites
echo "4️⃣ Validating prerequisites..."
python validate_eddie_prerequisites.py

echo ""
echo "🎉 Prerequisites check complete!"
echo ""
echo "Next steps:"
echo "  1. If price cache is still low, run: python scripts/precache_prices.py"
echo "  2. Test Eddie: Ask 'What data do you have?'"
echo "  3. Run analysis: Ask 'Should I buy AAPL?'"

