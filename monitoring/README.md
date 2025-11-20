# Monitoring Configuration Files

This directory contains configuration files for the Trading Agents monitoring stack.

## 📁 Directory Structure

```
monitoring/
├── prometheus/
│   ├── prometheus.yml      # Prometheus scrape configuration
│   └── alerts.yml          # Alert rules
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/    # Auto-configured datasources
│   │   └── dashboards/     # Dashboard provisioning
│   └── dashboards/
│       └── *.json          # Pre-built dashboards
├── loki/
│   └── loki-config.yml     # Loki log aggregation config
├── promtail/
│   └── promtail-config.yml # Log shipping configuration
└── alertmanager/
    └── alertmanager.yml    # Alert routing and notifications
```

## 🔧 Configuration Files

### Prometheus (`prometheus/prometheus.yml`)
- **Scrape intervals**: 15s default, 30s for exporters
- **Targets**: API, PostgreSQL, Redis, Node, cAdvisor
- **Retention**: 30 days
- **Alert rules**: Loaded from `alerts.yml`

**Key Settings:**
```yaml
global:
  scrape_interval: 15s      # How often to scrape metrics
  evaluation_interval: 15s   # How often to evaluate rules
```

### Alert Rules (`prometheus/alerts.yml`)
Pre-configured alerts for:
- API health and performance
- Database issues
- Cache performance
- System resources
- Business metrics (user satisfaction, costs)

**Severity Levels:**
- `critical`: Immediate action required (API down, DB down)
- `warning`: Investigate soon (high error rate, slow queries)
- `info`: Informational (low activity)

### Grafana Datasources (`grafana/provisioning/datasources/`)
Auto-configured connections to:
- **Prometheus** (primary, default datasource)
- **Loki** (logs)

### Grafana Dashboards (`grafana/dashboards/`)
Pre-built dashboards:
- `trading-agents-overview.json`: Main operational dashboard

**Dashboard Panels:**
1. API Status (gauge)
2. Chat Request Rate (timeseries)
3. Agent Processing Time (histogram)
4. User Satisfaction Score (gauge)
5. Trading Signals (bar chart)
6. LLM Token Usage (timeseries)
7. CPU/Memory/Disk (gauges)

### Loki (`loki/loki-config.yml`)
Log aggregation settings:
- **Port**: 3100
- **Storage**: Local filesystem
- **Schema**: v11 with BoltDB shipper
- **Retention**: Based on disk space

### Promtail (`promtail/promtail-config.yml`)
Log collection from:
- Application logs: `/app/logs/*.log`
- System logs: `/var/log/*.log`
- JSON structured logs: `/app/logs/*.json`

**Pipeline stages:**
- JSON parsing
- Label extraction (level, logger)
- Timestamp parsing

### AlertManager (`alertmanager/alertmanager.yml`)
Alert routing configuration:
- **Group by**: alertname, severity, component
- **Receivers**: default, critical, warning
- **Inhibit rules**: Critical alerts suppress warnings

**Add notification channels:**
```yaml
receivers:
  - name: 'critical'
    slack_configs:
      - api_url: 'YOUR_WEBHOOK'
        channel: '#alerts'
```

## 🔄 Updating Configuration

### Reload Prometheus Configuration
```bash
# Hot reload (no restart needed)
curl -X POST http://localhost:9090/-/reload

# Or restart the container
docker-compose -f docker-compose.monitoring.yml restart prometheus
```

### Update Grafana Dashboards
1. Edit JSON in `grafana/dashboards/`
2. Restart Grafana or wait for auto-reload (10s interval)

```bash
docker-compose -f docker-compose.monitoring.yml restart grafana
```

### Modify Alert Rules
1. Edit `prometheus/alerts.yml`
2. Reload Prometheus configuration (see above)
3. Check rules: http://localhost:9090/rules

### Change Alert Routing
1. Edit `alertmanager/alertmanager.yml`
2. Reload AlertManager:
```bash
curl -X POST http://localhost:9093/-/reload
# Or restart
docker-compose -f docker-compose.monitoring.yml restart alertmanager
```

## 📊 Adding Custom Metrics

### 1. Add Metric in Code
```python
from tradingagents.monitoring.metrics import get_metrics
metrics = get_metrics()

# Define new metric in metrics.py
self.my_metric = Counter('tradingagents_my_metric_total', 'Description')

# Use it
metrics.my_metric.inc()
```

### 2. Create Alert Rule
Add to `prometheus/alerts.yml`:
```yaml
- alert: MyMetricHigh
  expr: rate(tradingagents_my_metric_total[5m]) > 10
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "My metric is too high"
```

### 3. Add to Dashboard
Edit `grafana/dashboards/trading-agents-overview.json` or create new dashboard via UI.

## 🧪 Testing Configuration

### Validate Prometheus Config
```bash
docker exec tradingagents_prometheus \
  promtool check config /etc/prometheus/prometheus.yml
```

### Validate Alert Rules
```bash
docker exec tradingagents_prometheus \
  promtool check rules /etc/prometheus/alerts.yml
```

### Test AlertManager Config
```bash
docker exec tradingagents_alertmanager \
  amtool check-config /etc/alertmanager/alertmanager.yml
```

## 🔐 Security Notes

### Production Checklist
- [ ] Change Grafana admin password
- [ ] Enable authentication on Prometheus
- [ ] Use HTTPS/TLS for all services
- [ ] Restrict network access (firewall rules)
- [ ] Secure AlertManager webhook URLs
- [ ] Review and limit datasource permissions
- [ ] Enable audit logging

### Environment Variables
Never commit sensitive data. Use environment variables:
```yaml
# In docker-compose.monitoring.yml
environment:
  - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
  - SLACK_WEBHOOK=${SLACK_WEBHOOK}
```

## 📚 Resources

- [Prometheus Configuration](https://prometheus.io/docs/prometheus/latest/configuration/configuration/)
- [Grafana Provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/)
- [Loki Configuration](https://grafana.com/docs/loki/latest/configuration/)
- [AlertManager Configuration](https://prometheus.io/docs/alerting/latest/configuration/)

## 🆘 Common Issues

**Prometheus not scraping:**
- Check `prometheus.yml` syntax
- Verify target URLs are reachable
- Check Docker network connectivity

**Grafana dashboards not loading:**
- Verify provisioning path in `dashboards.yml`
- Check JSON syntax in dashboard files
- Review Grafana logs

**Alerts not firing:**
- Check alert expression in Prometheus UI
- Verify AlertManager is configured in Prometheus
- Check AlertManager routing rules

**Logs not appearing in Loki:**
- Verify Promtail can access log files
- Check Promtail configuration
- Review Promtail logs for errors
