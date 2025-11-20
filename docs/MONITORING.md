# Trading Agents Monitoring Stack

Complete monitoring solution for the Trading Agents application using Prometheus, Grafana, and Loki.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Trading Agents API                        │
│                    (FastAPI on :8005)                        │
│                  /metrics endpoint exposed                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
         ┌──────────────┴───────────────┐
         │                              │
    ┌────▼─────┐                  ┌────▼─────┐
    │Prometheus│                  │  Loki    │
    │  :9090   │                  │  :3100   │
    └────┬─────┘                  └────┬─────┘
         │                              │
         └───────────┬──────────────────┘
                     │
              ┌──────▼──────┐
              │   Grafana   │
              │    :3000    │
              └─────────────┘
```

## 📊 Components

### Core Services

1. **Prometheus** (`:9090`)
   - Time-series metrics database
   - Scrapes metrics from all exporters
   - Evaluates alerting rules
   - 30-day data retention

2. **Grafana** (`:3000`)
   - Visualization and dashboards
   - Query interface for Prometheus & Loki
   - Pre-configured dashboards included
   - Default credentials: `admin/admin`

3. **Loki** (`:3100`)
   - Log aggregation system
   - Integrates with Grafana
   - Efficient log storage

4. **AlertManager** (`:9093`)
   - Alert routing and management
   - Configurable notification channels
   - Alert grouping and deduplication

### Exporters

1. **Node Exporter** (`:9100`)
   - System metrics (CPU, memory, disk, network)

2. **PostgreSQL Exporter** (`:9187`)
   - Database connections, query performance
   - Table statistics, cache hit ratios

3. **Redis Exporter** (`:9121`)
   - Cache hit/miss rates
   - Memory usage, key counts

4. **cAdvisor** (`:8080`)
   - Container resource usage
   - Docker metrics

5. **Promtail**
   - Log shipping to Loki
   - Log parsing and labeling

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Trading Agents API running on port 8005
- PostgreSQL database running (for postgres_exporter)

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
# Or with uv
uv pip install prometheus-client prometheus-fastapi-instrumentator psutil
```

### 2. Configure Environment

Update `.env` file with your database credentials:

```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=investment_intelligence
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here
```

### 3. Start Monitoring Stack

```bash
./scripts/start-monitoring.sh
```

This will start:
- ✅ Prometheus
- ✅ Grafana
- ✅ Loki
- ✅ AlertManager
- ✅ All exporters

### 4. Verify Services

Check that all services are running:

```bash
docker-compose -f docker-compose.monitoring.yml ps
```

### 5. Access Dashboards

Open Grafana: http://localhost:3000
- Username: `admin`
- Password: `admin` (change on first login)

Navigate to **Dashboards → Trading Agents - Overview**

## 📈 Available Metrics

### API Metrics

```
tradingagents_chat_requests_total              # Total chat requests
tradingagents_chat_success_total               # Successful chats
tradingagents_chat_failures_total              # Failed chats
tradingagents_agent_processing_seconds         # Processing time histogram
tradingagents_user_feedback_total              # User feedback count
tradingagents_feedback_score_average           # Average satisfaction
```

### Trading Metrics

```
tradingagents_trading_signals_total            # Signals generated
tradingagents_analysis_requests_total          # Analysis requests
tradingagents_unique_tickers_analyzed          # Unique tickers
```

### LLM Metrics

```
tradingagents_llm_calls_total                  # API calls to LLM
tradingagents_llm_tokens_total                 # Token consumption
tradingagents_llm_cost_usd_total               # Estimated costs
tradingagents_llm_latency_seconds              # LLM API latency
```

### Database Metrics

```
tradingagents_db_queries_total                 # Database queries
tradingagents_db_query_duration_seconds        # Query execution time
```

### Cache Metrics

```
tradingagents_cache_hits_total                 # Cache hits
tradingagents_cache_misses_total               # Cache misses
```

## 🎯 Custom Metrics Usage

Add custom metrics to your code:

```python
from tradingagents.monitoring.metrics import get_metrics

metrics = get_metrics()

# Track a trading signal
metrics.track_trading_signal(signal_type="BUY", ticker="AAPL")

# Track an analysis request
metrics.track_analysis_request(ticker="TSLA", analysis_type="technical")

# Track LLM usage
metrics.track_llm_call(
    model="gpt-4",
    provider="openai",
    latency=2.5,
    input_tokens=150,
    output_tokens=300,
    cost=0.015
)

# Track database query
import time
start = time.time()
# ... your query ...
metrics.track_db_query(
    operation="SELECT",
    table="interactions",
    duration=time.time() - start
)
```

## 📊 Pre-built Dashboards

### Trading Agents Overview
- API health status
- Request rates and error rates
- Agent processing times (p50, p95, p99)
- User satisfaction score
- Trading signals generated
- LLM token usage
- System resources (CPU, Memory, Disk)

Access at: **Grafana → Dashboards → Trading Agents - Overview**

## 🚨 Alerts

Pre-configured alerts will trigger when:

### Critical Alerts
- ❌ API is down (>1 minute)
- ❌ PostgreSQL is down (>1 minute)
- ❌ Redis is down (>1 minute)

### Warning Alerts
- ⚠️ High error rate (>10% for 5 minutes)
- ⚠️ Slow response time (p95 >30s for 5 minutes)
- ⚠️ High database connections (>80 for 5 minutes)
- ⚠️ Low Redis hit rate (<70% for 10 minutes)
- ⚠️ High CPU usage (>80% for 5 minutes)
- ⚠️ High memory usage (>85% for 5 minutes)
- ⚠️ Low disk space (<15% for 5 minutes)
- ⚠️ Low user satisfaction (<3.0 for 1 hour)
- ⚠️ High LLM costs (>$10/hour)

### Configuring Alert Notifications

Edit `monitoring/alertmanager/alertmanager.yml` to add notification channels:

```yaml
receivers:
  - name: 'critical'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#alerts-critical'
    # Or email:
    email_configs:
      - to: 'alerts@example.com'
        from: 'alertmanager@example.com'
        smarthost: 'smtp.example.com:587'
```

## 🔍 Querying Metrics

### PromQL Examples

**Average response time (last 5 minutes):**
```promql
rate(tradingagents_agent_processing_seconds_sum[5m]) /
rate(tradingagents_agent_processing_seconds_count[5m])
```

**Error rate percentage:**
```promql
(rate(tradingagents_chat_failures_total[5m]) /
rate(tradingagents_chat_requests_total[5m])) * 100
```

**Cache hit ratio:**
```promql
rate(tradingagents_cache_hits_total[5m]) /
(rate(tradingagents_cache_hits_total[5m]) +
rate(tradingagents_cache_misses_total[5m]))
```

**Top tickers by analysis volume:**
```promql
topk(10, sum by (ticker) (
  increase(tradingagents_analysis_requests_total[1h])
))
```

## 📝 Viewing Logs

### Via Grafana
1. Go to **Explore** in Grafana
2. Select **Loki** datasource
3. Query logs:
   ```logql
   {job="tradingagents"} |= "error"
   ```

### Via Docker
```bash
# View all logs
docker-compose -f docker-compose.monitoring.yml logs -f

# View specific service
docker-compose -f docker-compose.monitoring.yml logs -f grafana
docker-compose -f docker-compose.monitoring.yml logs -f prometheus
```

## 🛠️ Troubleshooting

### Metrics Not Showing

1. **Check API is exposing metrics:**
   ```bash
   curl http://localhost:8005/metrics
   ```

2. **Check Prometheus is scraping:**
   - Go to Prometheus: http://localhost:9090/targets
   - All targets should show "UP"

3. **Check Prometheus config:**
   ```bash
   docker exec tradingagents_prometheus promtool check config /etc/prometheus/prometheus.yml
   ```

### Grafana Dashboard Empty

1. **Verify datasource connection:**
   - Grafana → Configuration → Data Sources → Prometheus
   - Click "Test" button

2. **Check if metrics exist:**
   - Go to Prometheus: http://localhost:9090/graph
   - Run query: `up{job="tradingagents-api"}`

### High Resource Usage

**Prometheus storage growing:**
- Default retention: 30 days
- Change in `docker-compose.monitoring.yml`:
  ```yaml
  command:
    - '--storage.tsdb.retention.time=15d'  # Reduce to 15 days
  ```

**Reduce scrape frequency:**
- Edit `monitoring/prometheus/prometheus.yml`
- Increase `scrape_interval` from `15s` to `30s` or `60s`

## 🧹 Maintenance

### Stop Monitoring
```bash
./scripts/stop-monitoring.sh
```

### Reset All Data
```bash
docker-compose -f docker-compose.monitoring.yml down -v
```

### Backup Grafana Dashboards
```bash
# Export dashboards via API
curl -X GET http://admin:admin@localhost:3000/api/dashboards/uid/trading-agents-overview \
  | jq '.dashboard' > backup-dashboard.json
```

### Update Prometheus Configuration
```bash
# After editing prometheus.yml
docker-compose -f docker-compose.monitoring.yml restart prometheus
```

## 📚 Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/)
- [PromQL Tutorial](https://prometheus.io/docs/prometheus/latest/querying/basics/)

## 🤝 Integration with Existing Tools

### Langfuse Integration

The application already uses Langfuse for LLM observability. The monitoring stack complements this:

- **Langfuse**: LLM-specific traces, prompt versioning, user feedback
- **Prometheus/Grafana**: Infrastructure, performance, system health, business metrics

### Database Integration

PostgreSQL metrics are automatically collected if the database is accessible. Make sure:
1. Database credentials are in `.env`
2. Database is running and accessible
3. postgres_exporter container can reach the database

### Redis Integration

Redis metrics are collected automatically. If Redis is running in Docker:
```yaml
# In docker-compose.yml, add to same network
networks:
  - monitoring
```

## 💡 Best Practices

1. **Set up alerts early** - Configure AlertManager notifications before production
2. **Monitor costs** - Track LLM token usage and costs closely
3. **Regular reviews** - Check dashboards weekly for trends
4. **Optimize queries** - Use metrics to identify slow database queries
5. **Capacity planning** - Monitor resource usage trends for scaling decisions
6. **User satisfaction** - Track feedback scores and investigate drops
7. **Custom metrics** - Add business-specific metrics as needed

## 🔐 Security Considerations

1. **Change default passwords** immediately in production
2. **Use authentication** for Prometheus and Grafana in production
3. **Restrict network access** to monitoring ports
4. **Encrypt connections** with TLS in production
5. **Secure sensitive data** in AlertManager notifications

## 📞 Support

For issues or questions:
- Check troubleshooting section above
- Review Prometheus/Grafana logs
- Open an issue in the project repository
