# Verifying Langfuse Monitoring Capture

## 🔍 Current Status

The Langfuse dashboard shows "Instrument Your Application" as pending. This means we need to verify that traces are actually being captured.

---

## ✅ What's Configured

1. **Langfuse Client** ✅
   - Initialized with credentials
   - OpenTelemetry tracing enabled (`tracing_enabled=True`)
   - Has `_otel_tracer` attribute (OpenTelemetry integration)

2. **Environment Variables** ✅
   - `LANGFUSE_ENABLED=true`
   - `LANGFUSE_PUBLIC_KEY` set
   - `LANGFUSE_SECRET_KEY` set
   - `LANGFUSE_HOST=http://localhost:3000`

3. **Integration Code** ✅
   - Custom callback handler created
   - Integrated into `TradingAgentsGraph`

---

## 🧪 How to Verify

### Option 1: Run OpenTelemetry Test

```bash
cd /Users/lxupkzwjs/Developer/eval/TradingAgents
python3 test_langfuse_opentelemetry.py
```

This will:
- Create OpenTelemetry spans directly
- Create a Langfuse event
- Flush traces to Langfuse
- Show you what to look for in the dashboard

### Option 2: Run Analysis Test

```bash
python3 test_langfuse_monitoring.py
```

This will:
- Run a minimal stock analysis
- Use the callback handler
- Show you where to find traces

---

## 📊 What to Look For

### In Langfuse Dashboard (`http://localhost:3000`)

1. **Go to:** Traces (sidebar)
2. **Look for:**
   - `test_span` or `child_span` (from OpenTelemetry test)
   - `Test Event - Monitoring Verification` (from event test)
   - `Stock Analysis: AAPL` (from analysis test)

### In Langfuse Logs

```bash
cd /Users/lxupkzwjs/Developer/langfuse
docker compose logs langfuse-web --tail 50 | grep -i "trace\|span\|otel\|api"
```

Look for:
- POST requests to `/api/public/traces`
- OpenTelemetry span ingestion
- No authentication errors

---

## 🔧 If Traces Don't Appear

### Issue 1: OpenTelemetry Not Initialized

Langfuse v3 requires OpenTelemetry to be properly initialized. The client should do this automatically, but verify:

```python
from langfuse import Langfuse

langfuse = Langfuse(
    public_key="...",
    secret_key="...",
    host="http://localhost:3000",
    tracing_enabled=True  # This is key!
)
```

### Issue 2: Spans Not Being Exported

OpenTelemetry spans need to be exported to Langfuse. Check:

1. **Langfuse client has OTEL tracer:**
   ```python
   hasattr(langfuse_client, '_otel_tracer')  # Should be True
   ```

2. **Spans are being created:**
   ```python
   from opentelemetry import trace
   tracer = trace.get_tracer(__name__)
   with tracer.start_as_current_span("test"):
       pass
   ```

3. **Flush is called:**
   ```python
   langfuse.flush()  # Ensure traces are sent
   ```

### Issue 3: Callback Handler Not Working

Our custom callback handler may not be creating proper OpenTelemetry spans. We can:

1. **Use OpenTelemetry directly:**
   ```python
   from opentelemetry import trace
   
   tracer = trace.get_tracer(__name__)
   with tracer.start_as_current_span("analysis"):
       result = graph.propagate("AAPL", date.today())
   ```

2. **Or use Langfuse events:**
   ```python
   langfuse.create_event(
       name="Stock Analysis",
       input={"ticker": "AAPL"},
       output={"decision": result.get("final_decision")}
   )
   ```

---

## ✅ Expected Behavior

When working correctly:

1. **Traces appear in dashboard** within 5-10 seconds
2. **Logs show incoming requests** to Langfuse API
3. **No errors** in Langfuse web container logs
4. **Spans show execution details** when clicked

---

## 🎯 Next Steps

1. **Run the OpenTelemetry test:**
   ```bash
   python3 test_langfuse_opentelemetry.py
   ```

2. **Check the dashboard** - Do traces appear?

3. **If yes:** ✅ Monitoring is working! The "Instrument Your Application" badge should update.

4. **If no:** 
   - Check Langfuse logs
   - Verify API keys are correct
   - Ensure Langfuse server is running
   - Try creating spans manually

---

## 📝 Summary

**Status:** Integration code is ready, but we need to verify that:
- OpenTelemetry spans are being created
- Spans are being exported to Langfuse
- Langfuse is receiving and displaying traces

**Next:** Run the verification tests and check the dashboard!

