#!/bin/bash

# Start Monitoring Stack for Trading Agents
# This script starts Prometheus, Grafana, Loki, and all exporters

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "======================================"
echo "Starting Trading Agents Monitoring Stack"
echo "======================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found. Creating a default one..."
    cat > .env << 'EOF'
# PostgreSQL Configuration (for postgres_exporter)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=investment_intelligence
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
EOF
    echo "✅ Created .env file. Please update POSTGRES_PASSWORD before proceeding."
    echo ""
fi

# Stop any existing monitoring containers
echo "🧹 Cleaning up existing monitoring containers..."
docker compose -f docker-compose.monitoring.yml down 2>/dev/null || true
echo ""

# Start the monitoring stack
echo "🚀 Starting monitoring services..."
docker compose -f docker-compose.monitoring.yml up -d

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo ""
echo "📊 Service Status:"
echo "===================="

services=(
    "prometheus:9095"
    "grafana:3001"
    "loki:3100"
    "alertmanager:9093"
)

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if docker ps | grep -q "tradingagents_$name"; then
        echo "✅ $name is running on port $port"
    else
        echo "❌ $name failed to start"
    fi
done

echo ""
echo "======================================"
echo "✨ Monitoring Stack Started Successfully!"
echo "======================================"
echo ""
echo "Access the services:"
echo "  📈 Grafana:       http://localhost:3001 (admin/admin)"
echo "  🔍 Prometheus:    http://localhost:9095"
echo "  📋 Loki:          http://localhost:3100"
echo "  🚨 AlertManager:  http://localhost:9093"
echo ""
echo "Metrics endpoints:"
echo "  🎯 API Metrics:   http://localhost:8005/metrics"
echo "  📊 Node Exporter: http://localhost:9100/metrics"
echo "  🗄️  Postgres:      http://localhost:9187/metrics"
echo "  💾 Redis:         http://localhost:9121/metrics"
echo ""
echo "📚 View logs: docker compose -f docker-compose.monitoring.yml logs -f"
echo "🛑 Stop monitoring: docker compose -f docker-compose.monitoring.yml down"
echo ""
echo "⚠️  Note: Make sure your Trading Agents API is running on port 8005"
echo "   Start it with: uvicorn tradingagents.api.main:app --host 0.0.0.0 --port 8005"
echo ""
