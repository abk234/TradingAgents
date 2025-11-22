# Quick Validation Guide

## One-Command Validation

```bash
# Run all validation checks
./validate_integration.sh
```

This will:
1. ✓ Check backend is running
2. ✓ Check frontend is running
3. ✓ Run integration tests
4. ✓ Run E2E tests
5. ✓ Check system health
6. ✓ Analyze logs

## Quick Health Check

```bash
# Single health check
python monitor_system.py

# Continuous monitoring (updates every 10s)
python monitor_system.py --continuous
```

## Quick Integration Test

```bash
# Test frontend-backend-middleware integration
python test_integration.py
```

## Quick E2E Test

```bash
# Test complete user workflows
python test_e2e.py
```

## Quick Log Analysis

```bash
# Analyze all logs
python analyze_logs.py
```

## Start Everything

```bash
# Start backend + frontend
./start.sh

# Then in another terminal, run validation
./validate_integration.sh
```

## Troubleshooting

### Services Not Running?

```bash
# Start backend
python -m tradingagents.api.main

# Start frontend (in another terminal)
cd web-app && npm run dev -- -p 3005
```

### Tests Failing?

1. Check services are running:
   ```bash
   curl http://localhost:8005/health
   curl http://localhost:3005
   ```

2. Check logs:
   ```bash
   python analyze_logs.py
   ```

3. Run health check:
   ```bash
   python monitor_system.py
   ```

## Environment Variables

```bash
# Custom URLs
export BACKEND_URL=http://localhost:8005
export FRONTEND_URL=http://localhost:3005
export API_KEY=your-key-here
```

