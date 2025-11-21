# Eddie v2.0 Testing Guide

**Date:** November 2025  
**Status:** ✅ All Tests Passing

---

## Quick Test

Run the comprehensive test suite:

```bash
python3 test_eddie_v2.py
```

**Expected Result:** ✅ All 9 tests pass (100% success rate)

---

## Test Results Summary

### ✅ All Tests Passing (9/9)

1. **System Doctor** ✅
   - Data sanity checks
   - Indicator math audits (RSI, MACD)
   - System health assessment

2. **State Tracking** ✅
   - State changes (idle, listening, processing, speaking)
   - Confidence tracking (multi-factor)
   - Active tools tracking

3. **Cognitive Controller** ✅
   - Mode decision (empathetic, analyst, engineer)
   - Context-aware mode switching
   - Mode prompt generation

4. **Knowledge Graph** ✅
   - Node creation and retrieval
   - Query functionality
   - Relationship traversal

5. **Procedural Memory** ✅
   - Workflow management
   - Tool usage pattern tracking
   - Tool recommendations

6. **Voice TTS** ✅
   - Tone detection
   - TTS engine initialization (fallback available)

7. **Agent Integration** ✅
   - Cognitive controller integration
   - State tracker integration
   - Mode decision in agent flow

8. **Tools Availability** ✅
   - All 3 v2.0 tools available:
     - `run_system_doctor_check`
     - `synthesize_speech`
     - `research_from_web`
   - Total: 26 tools

9. **Web Crawling** ✅
   - Knowledge storage
   - Search functionality (may be rate-limited)

---

## How to Test Eddie Manually

### 1. Launch Eddie

```bash
# Option 1: Use launcher script
./trading_bot.sh

# Option 2: Direct Python
venv/bin/python -m tradingagents.bot

# Option 3: Chainlit
venv/bin/chainlit run tradingagents/bot/chainlit_app.py
```

**Eddie opens at:** `http://localhost:8000`

### 2. Prerequisites

Before testing, ensure:
- ✅ **Ollama** is running (`ollama serve`)
- ✅ **llama3.3** model downloaded (`ollama pull llama3.3`)
- ✅ **Database** has stock data
- ✅ **Dependencies** installed (`pip install -r requirements.txt`)

### 3. Test v2.0 Features

#### Test System Doctor

```
You: "Run a system health check for AAPL"
Eddie: [Uses run_system_doctor_check]
       "🏥 System Doctor Health Report..."
       "Overall Health: ✅ HEALTHY"
```

#### Test State Tracking

The state is automatically tracked. Check the `/state` API endpoint:

```bash
curl http://localhost:8005/state
```

Or watch Eddie's state change during conversations:
- **Listening**: When receiving input
- **Processing**: When analyzing
- **Speaking**: When generating response

#### Test Cognitive Modes

**Empathetic Mode:**
```
You: "I'm worried about my portfolio, the market crashed"
Eddie: [Switches to empathetic mode]
       "I understand your concern. Let me help..."
```

**Engineer Mode:**
```
You: "The system seems broken, there's an error"
Eddie: [Switches to engineer mode]
       "Let me run diagnostics..."
```

**Analyst Mode (default):**
```
You: "Analyze AAPL for me"
Eddie: [Uses analyst mode]
       "Based on my analysis..."
```

#### Test Voice TTS

```
You: "Can you say that out loud?"
Eddie: [Uses synthesize_speech]
       "✅ Speech synthesized successfully!"
```

Or use the API directly:
```bash
curl -X POST "http://localhost:8005/voice/synthesize" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, I am Eddie", "tone": "professional"}'
```

#### Test Web Crawling

```
You: "What are 0DTE options?"
Eddie: [Uses research_from_web]
       "🌐 Research Results for: 0DTE options..."
       "✅ Knowledge stored in my memory!"
```

---

## API Testing

### State Endpoint

```bash
# Get current state
curl http://localhost:8005/state

# Response:
{
  "state": "idle",
  "confidence": {
    "data_freshness": 0,
    "math_verification": 0,
    "ai_confidence": 0,
    "overall": 0
  },
  "current_ticker": null,
  "active_tools": [],
  "system_health": "HEALTHY"
}
```

### Voice Synthesis Endpoint

```bash
# Synthesize speech
curl -X POST "http://localhost:8005/voice/synthesize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I recommend buying AAPL",
    "tone": "professional",
    "return_base64": false
  }'

# Returns: WAV audio file
```

---

## Unit Testing Individual Components

### Test System Doctor

```python
from tradingagents.validation import SystemDoctor

doctor = SystemDoctor()
report = doctor.run_health_check("AAPL")
print(report.format_for_display())
```

### Test State Tracker

```python
from tradingagents.bot.state_tracker import get_state_tracker, EddieState

tracker = get_state_tracker()
tracker.set_state(EddieState.PROCESSING, "Analyzing...")
state = tracker.get_state_dict()
print(state)
```

### Test Cognitive Controller

```python
from tradingagents.cognitive import get_cognitive_controller

controller = get_cognitive_controller()
decision = controller.decide_mode(
    user_message="I'm worried about my portfolio",
    user_emotional_state="stressed"
)
print(f"Mode: {decision.mode.value}")
```

### Test Knowledge Graph

```python
from tradingagents.cognitive import get_knowledge_graph

kg = get_knowledge_graph()
results = kg.query("RSI")
for node in results:
    print(f"{node.label}: {node.properties.get('description')}")
```

### Test Procedural Memory

```python
from tradingagents.cognitive import get_procedural_memory

pm = get_procedural_memory()
workflow = pm.get_workflow("stock_analysis_full")
print(f"Workflow: {workflow.name} ({len(workflow.steps)} steps)")
```

### Test Voice TTS

```python
from tradingagents.voice import get_tts_engine, EmotionalTone

tts = get_tts_engine()
audio_bytes = tts.synthesize(
    "Hello, I am Eddie",
    tone=EmotionalTone.PROFESSIONAL,
    return_bytes=True
)
print(f"Generated {len(audio_bytes)} bytes")
```

### Test Web Crawling

```python
from tradingagents.research import get_autonomous_researcher
import asyncio

researcher = get_autonomous_researcher()
result = asyncio.run(researcher.learn_about("Death Cross"))
print(result["knowledge"]["summary"])
```

---

## Integration Testing

### Full Conversation Flow

```python
from tradingagents.bot.conversational_agent import ConversationalAgent
from tradingagents.default_config import DEFAULT_CONFIG

agent = ConversationalAgent(config=DEFAULT_CONFIG)

# Test conversation
response = await agent.chat(
    message="Run a system health check for AAPL",
    history=[],
    prompt_metadata=None
)

print(response)
```

---

## Troubleshooting

### Missing Dependencies

If tests fail with import errors:

```bash
pip install -r requirements.txt
pip install networkx  # For knowledge graph
pip install TTS pyttsx3  # For voice
pip install crawl4ai duckduckgo-search  # For web crawling
```

### Database Connection Issues

Ensure PostgreSQL is running and database is configured:

```bash
# Check database connection
python3 -c "from tradingagents.database import get_db_connection; print('✅ Connected')"
```

### Ollama Not Running

```bash
# Start Ollama
ollama serve

# Check if running
curl http://localhost:11434/api/tags
```

### Module Import Errors

If you see `ModuleNotFoundError`:

```bash
# Ensure you're in the project directory
cd /Users/lxupkzwjs/Developer/eval/TradingAgents

# Set PYTHONPATH
export PYTHONPATH=$(pwd)

# Run tests
python3 test_eddie_v2.py
```

---

## Expected Test Output

```
================================================================================
  EDDIE V2.0 COMPREHENSIVE TEST SUITE
================================================================================

✅ System Doctor: PASSED
✅ State Tracking: ALL TESTS PASSED
✅ Cognitive Controller: ALL TESTS PASSED
✅ Knowledge Graph: ALL TESTS PASSED
✅ Procedural Memory: ALL TESTS PASSED
✅ Voice TTS: TESTS PASSED
✅ Agent Integration: ALL TESTS PASSED
✅ Tools Availability: PASSED
✅ Web Crawling: TESTS PASSED

Total: 9/9 tests passed
Success Rate: 100.0%

🎉 ALL TESTS PASSED! Eddie v2.0 Phase 1 MVP is working correctly!
```

---

## Next Steps

After successful testing:

1. **Manual Testing**: Try Eddie in the web interface
2. **Feature Testing**: Test each v2.0 feature individually
3. **Integration Testing**: Test full conversation flows
4. **Performance Testing**: Monitor response times
5. **User Acceptance Testing**: Get feedback from users

---

**Last Updated:** November 2025

