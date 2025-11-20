#!/bin/bash

# Stop Monitoring Stack for Trading Agents

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "======================================"
echo "Stopping Trading Agents Monitoring Stack"
echo "======================================"
echo ""

# Stop all monitoring containers
docker compose -f docker-compose.monitoring.yml down

echo ""
echo "✅ Monitoring stack stopped successfully!"
echo ""
echo "To remove all data volumes as well, run:"
echo "  docker compose -f docker-compose.monitoring.yml down -v"
echo ""
