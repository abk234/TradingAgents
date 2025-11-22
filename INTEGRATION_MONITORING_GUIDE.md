# TradingAgents Integration & Monitoring Guide

This guide explains how to validate, monitor, and analyze your TradingAgents system to ensure frontend, backend, and middleware are properly integrated and working.

## Quick Start

### 1. Start the System

First, ensure both backend and frontend are running:

```bash
# Option 1: Use the comprehensive startup script
./start.sh

# Option 2: Start manually
# Terminal 1 - Backend
python -m tradingagents.api.main

# Terminal 2 - Frontend
cd web-app
npm run dev -- -p 3005
```

### 2. Run Integration Validation

```bash
# Run all validation checks
./validate_integration.sh

# Or run specific checks
./validate_integration.sh --integration-only  # Only integration tests
./validate_integration.sh --e2e-only          # Only E2E tests
./validate_integration.sh --health-only       # Only health check
./validate_integration.sh --logs-only         # Only log analysis
```

## Tools Overview

### 1. Integration Tests (`test_integration.py`)

Tests basic connectivity and API endpoints between frontend, backend, and middleware.

**What it tests:**
- Backend health endpoint
- Backend API endpoints (chat, analyze, state)
- Frontend connectivity
- WebSocket connections
- CORS configuration
- Middleware integration
- API authentication

**Usage:**
```bash
python test_integration.py

# Or with custom URLs
BACKEND_URL=http://localhost:8005 FRONTEND_URL=http://localhost:3005 python test_integration.py
```

**Output:**
- ✓ Green checkmarks for passed tests
- ✗ Red X for failed tests
- ⚠ Yellow warnings for non-critical issues

### 2. End-to-End Tests (`test_e2e.py`)

Tests complete user workflows from frontend to backend to middleware.

**What it tests:**
- Complete chat workflow (initial message + follow-up)
- Complete analysis workflow
- State tracking across requests
- Frontend-backend integration
- Middleware activity during requests

**Usage:**
```bash
python test_e2e.py

# Or with custom URLs
BACKEND_URL=http://localhost:8005 FRONTEND_URL=http://localhost:3005 python test_e2e.py
```

**Note:** E2E tests may take longer as they perform actual operations (chat, analysis).

### 3. System Health Monitor (`monitor_system.py`)

Continuously monitors system health and provides real-time status.

**What it monitors:**
- Backend health and agent initialization status
- Frontend accessibility
- Backend metrics endpoint
- Backend API availability
- System resources (CPU, memory, disk)

**Usage:**
```bash
# Single check
python monitor_system.py

# Continuous monitoring (updates every 10 seconds)
python monitor_system.py --continuous

# Custom interval (e.g., every 5 seconds)
python monitor_system.py --continuous --interval 5

# Export status to JSON
python monitor_system.py --export health_status.json
```

**Output:**
- Real-time status dashboard
- Color-coded health indicators:
  - ✓ Green: Healthy
  - ⚠ Yellow: Degraded
  - ✗ Red: Down

### 4. Log Analyzer (`analyze_logs.py`)

Analyzes logs from backend, frontend, and middleware to identify issues and patterns.

**What it analyzes:**
- Error patterns and frequency
- API call statistics
- Middleware events and token usage
- Log levels distribution
- Response times

**Usage:**
```bash
# Analyze logs in default directory (./logs)
python analyze_logs.py

# Analyze logs in custom directory
python analyze_logs.py --dir /path/to/logs

# Export results to JSON
python analyze_logs.py --output analysis_results.json
```

**Output:**
- Summary statistics
- Top error patterns
- Most used API endpoints
- Middleware token usage
- Performance metrics

### 5. Comprehensive Validation Script (`validate_integration.sh`)

Runs all validation checks in sequence.

**Usage:**
```bash
# Run all checks
./validate_integration.sh

# Run specific checks
./validate_integration.sh --integration-only
./validate_integration.sh --e2e-only
./validate_integration.sh --health-only
./validate_integration.sh --logs-only
```

## Monitoring Workflow

### Daily Monitoring

1. **Start the system:**
   ```bash
   ./start.sh
   ```

2. **Run health check:**
   ```bash
   python monitor_system.py
   ```

3. **Check logs for issues:**
   ```bash
   python analyze_logs.py
   ```

### Before Deployment

1. **Run full validation:**
   ```bash
   ./validate_integration.sh
   ```

2. **Verify all tests pass:**
   - Integration tests: ✓
   - E2E tests: ✓
   - System health: ✓

3. **Export health status:**
   ```bash
   python monitor_system.py --export pre_deployment_health.json
   ```

### Troubleshooting

#### Backend Not Responding

1. Check if backend is running:
   ```bash
   curl http://localhost:8005/health
   ```

2. Check backend logs:
   ```bash
   tail -f backend.log
   # or
   tail -f logs/*.log
   ```

3. Restart backend:
   ```bash
   python -m tradingagents.api.main
   ```

#### Frontend Not Responding

1. Check if frontend is running:
   ```bash
   curl http://localhost:3005
   ```

2. Check frontend logs:
   ```bash
   tail -f web-app/frontend.log
   ```

3. Restart frontend:
   ```bash
   cd web-app
   npm run dev -- -p 3005
   ```

#### Integration Issues

1. Run integration tests:
   ```bash
   python test_integration.py
   ```

2. Check CORS configuration:
   - Verify backend CORS allows frontend origin
   - Check browser console for CORS errors

3. Check API authentication:
   - Verify API_KEY is set in `.env`
   - Check that frontend includes `X-API-Key` header

#### Middleware Not Working

1. Check middleware metrics:
   ```bash
   curl http://localhost:8005/metrics | grep tradingagents
   ```

2. Check middleware logs:
   ```bash
   python analyze_logs.py | grep -i middleware
   ```

3. Verify middleware is enabled in configuration

## Environment Variables

You can customize the monitoring tools with environment variables:

```bash
# Backend URL
export BACKEND_URL=http://localhost:8005

# Frontend URL
export FRONTEND_URL=http://localhost:3005

# API Key (if authentication is enabled)
export API_KEY=your-api-key-here

# Monitoring interval (for continuous monitoring)
export CHECK_INTERVAL=10  # seconds
```

## Integration with Monitoring Stack

If you're using the Prometheus/Grafana monitoring stack:

1. **Prometheus** automatically scrapes metrics from `/metrics` endpoint
2. **Grafana** dashboards show real-time system health
3. **Loki** aggregates logs for analysis

See `monitoring/README.md` for more details.

## Continuous Monitoring

For production, set up continuous monitoring:

```bash
# Run health monitor in background
nohup python monitor_system.py --continuous --interval 30 > monitor.log 2>&1 &

# Or use systemd service (create service file)
```

## Best Practices

1. **Run validation before deployment:** Always run `./validate_integration.sh` before deploying changes

2. **Monitor regularly:** Set up automated health checks (cron job or systemd timer)

3. **Analyze logs daily:** Review logs for errors and patterns

4. **Export status reports:** Keep health status exports for historical analysis

5. **Set up alerts:** Configure alerts for critical failures (see `monitoring/README.md`)

## Troubleshooting Common Issues

### Issue: "Backend not initialized"

**Solution:**
- Check that OpenAI API key is set in `.env`
- Verify backend logs for initialization errors
- Ensure all dependencies are installed

### Issue: "CORS errors in browser"

**Solution:**
- Verify backend CORS configuration in `tradingagents/api/main.py`
- Check that frontend URL matches allowed origins
- Ensure backend is running and accessible

### Issue: "API authentication failing"

**Solution:**
- Check that `API_KEY` is set in `.env` (backend)
- Verify frontend includes `X-API-Key` header
- Check browser localStorage for API key

### Issue: "Middleware not tracking tokens"

**Solution:**
- Verify middleware is enabled in configuration
- Check middleware logs for errors
- Ensure middleware is properly initialized

## Next Steps

1. Set up automated monitoring (cron jobs or systemd timers)
2. Configure alerts for critical failures
3. Set up log rotation to manage log file sizes
4. Integrate with external monitoring services (if needed)

## Support

For issues or questions:
- Check logs: `python analyze_logs.py`
- Run diagnostics: `./validate_integration.sh`
- Review documentation in `docs/` directory

