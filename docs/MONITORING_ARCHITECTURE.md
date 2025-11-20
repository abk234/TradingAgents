# Monitoring Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER ACCESS                                  │
│                                                                       │
│    Browser → http://localhost:3000 (Grafana Dashboards)            │
│              http://localhost:9090 (Prometheus Queries)              │
│              http://localhost:9093 (AlertManager)                    │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      VISUALIZATION LAYER                             │
│                                                                       │
│  ┌───────────────────┐           ┌──────────────────┐              │
│  │   GRAFANA :3000   │           │  AlertManager    │              │
│  │                   │◄──────────│     :9093        │              │
│  │  • Dashboards     │           │                  │              │
│  │  • Queries        │           │  • Routing       │              │
│  │  • Alerts         │           │  • Grouping      │              │
│  └────────┬──────────┘           │  • Silencing     │              │
│           │                       └──────────────────┘              │
│           │ Queries                                                 │
└───────────┼─────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DATA STORAGE LAYER                              │
│                                                                       │
│  ┌────────────────────┐          ┌──────────────────┐              │
│  │  PROMETHEUS :9090  │          │   LOKI :3100     │              │
│  │                    │          │                  │              │
│  │  • Time-series DB  │          │  • Log storage   │              │
│  │  • 30-day retention│          │  • Indexing      │              │
│  │  • Alert rules     │          │  • Compression   │              │
│  └─────────┬──────────┘          └────────┬─────────┘              │
│            │                               │                         │
│            │ Scrapes                       │ Receives                │
└────────────┼───────────────────────────────┼─────────────────────────┘
             │                               │
             ▼                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    COLLECTION LAYER                                  │
│                                                                       │
│  Metrics Exporters:                  Log Collectors:                │
│  ┌──────────────┐                   ┌──────────────┐               │
│  │ Node Exporter│                   │  Promtail    │               │
│  │   :9100      │                   │              │               │
│  └──────────────┘                   └──────────────┘               │
│                                                                       │
│  ┌──────────────┐                                                   │
│  │ Postgres     │                                                   │
│  │ Exporter     │                                                   │
│  │   :9187      │                                                   │
│  └──────────────┘                                                   │
│                                                                       │
│  ┌──────────────┐                                                   │
│  │ Redis        │                                                   │
│  │ Exporter     │                                                   │
│  │   :9121      │                                                   │
│  └──────────────┘                                                   │
│                                                                       │
│  ┌──────────────┐                                                   │
│  │  cAdvisor    │                                                   │
│  │   :8080      │                                                   │
│  └──────────────┘                                                   │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                                │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │         Trading Agents API (:8005)                            │ │
│  │                                                               │ │
│  │  /metrics endpoint                                            │ │
│  │  ├─ tradingagents_chat_requests_total                        │ │
│  │  ├─ tradingagents_agent_processing_seconds                   │ │
│  │  ├─ tradingagents_user_feedback_total                        │ │
│  │  ├─ tradingagents_llm_calls_total                            │ │
│  │  ├─ tradingagents_db_queries_total                           │ │
│  │  └─ ... (40+ custom metrics)                                 │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                    │                                 │
│                                    │ Uses                            │
│                                    ▼                                 │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  TradingMetrics Class (tradingagents/monitoring/metrics.py)  │ │
│  │                                                               │ │
│  │  • Custom business metrics                                   │ │
│  │  • Prometheus instrumentation                                │ │
│  │  • Context managers for timing                               │ │
│  └───────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                              │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ PostgreSQL   │  │    Redis     │  │   System     │             │
│  │   :5432      │  │    :6379     │  │  Resources   │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Metrics Flow
```
Application Code
    │
    ├─► track_chat_request()
    │       │
    │       └─► Counter.inc()
    │               │
    │               └─► Prometheus Client Library
    │                       │
    │                       └─► /metrics endpoint
    │                               │
    └───────────────────────────────┤
                                    │
                                    ▼
                            Prometheus Scraper
                            (every 15 seconds)
                                    │
                                    └─► Time-Series Database
                                            │
                                            └─► Grafana Queries
                                                    │
                                                    └─► Dashboard Visualization
```

### Logs Flow
```
Application Logs
    │
    └─► /app/logs/*.log
            │
            └─► Promtail
                    │
                    ├─► Parse & Label
                    │
                    └─► Ship to Loki
                            │
                            └─► Log Storage
                                    │
                                    └─► Grafana Queries
                                            │
                                            └─► Log Explorer
```

### Alerts Flow
```
Prometheus
    │
    ├─► Evaluate Alert Rules (every 15s)
    │       │
    │       └─► Condition Met?
    │               │
    │               └─► YES → Fire Alert
    │                           │
    │                           └─► AlertManager
    │                                   │
    │                                   ├─► Group by severity
    │                                   ├─► Deduplicate
    │                                   └─► Route to receivers
    │                                           │
    │                                           ├─► Slack
    │                                           ├─► Email
    │                                           ├─► PagerDuty
    │                                           └─► Webhook
```

## Component Responsibilities

### Prometheus
**Role:** Metrics collection and storage
- Scrapes `/metrics` endpoints
- Evaluates alert rules
- Stores time-series data
- Provides PromQL query interface

**Metrics Collected:**
- API performance (latency, throughput, errors)
- Business metrics (signals, analyses, feedback)
- LLM usage (tokens, costs, latency)
- System resources (CPU, memory, disk)
- Database performance (queries, connections)
- Cache performance (hits, misses)

### Grafana
**Role:** Visualization and dashboards
- Queries Prometheus & Loki
- Renders dashboards
- Displays alerts
- User management

**Dashboard Panels:**
- Status indicators (gauges)
- Time-series graphs
- Bar charts
- Heatmaps
- Tables

### Loki
**Role:** Log aggregation
- Receives logs from Promtail
- Indexes logs efficiently
- Stores compressed logs
- Provides LogQL query interface

### AlertManager
**Role:** Alert routing and management
- Receives alerts from Prometheus
- Groups related alerts
- Deduplicates identical alerts
- Routes to notification channels
- Manages silences

### Exporters
**Node Exporter:**
- CPU usage
- Memory usage
- Disk I/O
- Network traffic
- System load

**PostgreSQL Exporter:**
- Active connections
- Query execution time
- Cache hit ratio
- Table statistics
- Lock waits

**Redis Exporter:**
- Memory usage
- Key count
- Hit/miss ratio
- Evictions
- Replication lag

**cAdvisor:**
- Container CPU usage
- Container memory usage
- Network I/O per container
- Disk I/O per container

## Network Architecture

```
┌─────────────────────────────────────────────┐
│         Docker Network: monitoring          │
│                                             │
│  ┌─────────────┐      ┌──────────────┐    │
│  │ Prometheus  │──────│   Grafana    │    │
│  │   :9090     │      │    :3000     │    │
│  └──────┬──────┘      └──────┬───────┘    │
│         │                    │             │
│         │                    │             │
│         ├────────────────────┼──────────┐  │
│         │                    │          │  │
│    ┌────▼─────┐         ┌───▼────┐  ┌──▼──┐
│    │  Loki    │         │AlertMgr│  │     │
│    │  :3100   │         │ :9093  │  │Exprt│
│    └────▲─────┘         └────────┘  └─────┘
│         │                                   │
│    ┌────┴─────┐                            │
│    │Promtail  │                            │
│    └──────────┘                            │
│                                             │
└─────────────────────────────────────────────┘
                   │
                   │ host.docker.internal
                   │
                   ▼
┌─────────────────────────────────────────────┐
│              Host Machine                    │
│                                             │
│  Trading Agents API :8005                   │
│  PostgreSQL :5432                           │
│  Redis :6379                                │
└─────────────────────────────────────────────┘
```

## Metric Types

### Counters (Always Increasing)
```python
tradingagents_chat_requests_total        # Total requests
tradingagents_chat_success_total         # Total successes
tradingagents_llm_tokens_total           # Total tokens consumed
```

**Use Case:** Count events that only go up

### Gauges (Can Go Up or Down)
```python
tradingagents_active_conversations       # Current active chats
tradingagents_feedback_score_average     # Current average score
tradingagents_unique_tickers_analyzed    # Current unique count
```

**Use Case:** Track current state or level

### Histograms (Distribution)
```python
tradingagents_agent_processing_seconds   # Processing time distribution
tradingagents_llm_latency_seconds        # LLM API latency distribution
tradingagents_db_query_duration_seconds  # Query duration distribution
```

**Use Case:** Track distributions and percentiles (p50, p95, p99)

## Query Patterns

### Rate Queries (Events per Second)
```promql
rate(tradingagents_chat_requests_total[5m])
```

### Percentage Calculations
```promql
(rate(tradingagents_chat_failures_total[5m]) /
 rate(tradingagents_chat_requests_total[5m])) * 100
```

### Percentile Queries
```promql
histogram_quantile(0.95,
  rate(tradingagents_agent_processing_seconds_bucket[5m])
)
```

### Aggregations
```promql
sum by (ticker) (tradingagents_analysis_requests_total)
topk(10, sum by (ticker) (tradingagents_analysis_requests_total))
```

## Storage Architecture

### Prometheus Storage
```
/prometheus/
├── chunks/          # Compressed time-series data
├── wal/             # Write-ahead log
└── snapshots/       # Checkpoints
```

**Retention:** 30 days (configurable)
**Compression:** ~10:1 ratio

### Loki Storage
```
/loki/
├── chunks/          # Log chunks
├── boltdb-shipper/  # Index files
└── compactor/       # Compacted logs
```

**Retention:** Based on disk space
**Compression:** ~20:1 ratio

### Grafana Storage
```
/var/lib/grafana/
├── dashboards/      # Dashboard JSON files
├── grafana.db       # SQLite database
└── plugins/         # Grafana plugins
```

## Security Considerations

### Access Control
- Grafana: Username/password authentication
- Prometheus: No auth by default (add reverse proxy)
- AlertManager: No auth by default (add reverse proxy)

### Network Security
```yaml
# Recommended: Use internal network
networks:
  monitoring:
    internal: true  # Prevent external access
```

### Secret Management
```yaml
# Use environment variables for secrets
environment:
  - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
  - SLACK_WEBHOOK=${SLACK_WEBHOOK}
```

### TLS/HTTPS
For production, add reverse proxy:
```
Internet → Nginx (TLS) → Grafana
                       → Prometheus
                       → AlertManager
```

## Scalability Considerations

### High Cardinality Metrics
Avoid labels with many values:
```python
# BAD: user_id has thousands of values
metric.labels(user_id=user_id).inc()

# GOOD: Use aggregated labels
metric.labels(user_type="premium").inc()
```

### Metric Retention
Adjust based on disk space:
```yaml
command:
  - '--storage.tsdb.retention.time=15d'  # Reduce from 30d
  - '--storage.tsdb.retention.size=50GB' # Add size limit
```

### Federation
For multiple instances:
```yaml
# Prometheus config
- job_name: 'federate'
  scrape_interval: 15s
  honor_labels: true
  metrics_path: '/federate'
  params:
    'match[]':
      - '{job="tradingagents-api"}'
  static_configs:
    - targets:
      - 'prometheus-instance-1:9090'
      - 'prometheus-instance-2:9090'
```

## Troubleshooting Architecture

### Common Issues

**Metrics not appearing:**
1. Check Prometheus targets: http://localhost:9090/targets
2. Verify API exposing metrics: curl http://localhost:8005/metrics
3. Check Prometheus logs: docker logs tradingagents_prometheus

**High memory usage:**
1. Reduce metric cardinality (fewer unique label combinations)
2. Decrease retention period
3. Increase scrape interval

**Slow queries:**
1. Add recording rules for complex queries
2. Use shorter time ranges
3. Optimize PromQL queries

## Best Practices

1. **Label Consistency** - Use same label names across metrics
2. **Metric Naming** - Follow `namespace_subsystem_unit_suffix` pattern
3. **Cardinality Control** - Limit unique label combinations to <10,000
4. **Rate vs Counter** - Always use `rate()` for counters in queries
5. **Recording Rules** - Pre-compute expensive queries
6. **Dashboard Organization** - Group related metrics together
7. **Alert Tuning** - Adjust thresholds based on baseline data
