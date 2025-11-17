# Troubleshooting Eddie - Not Responding

## 🔍 Issue: Eddie Not Responding to Queries

**Symptoms:**
- User sends queries but Eddie doesn't respond
- "Task manually stopped" message appears
- White circle/cursor indicating waiting state
- No error messages shown

---

## 🔧 Quick Fixes

### 1. **Check Ollama Connection**
```bash
# Test if Ollama is responding
curl http://localhost:11434/api/tags

# If not responding, restart Ollama:
ollama serve
```

### 2. **Check Application Logs**
```bash
# View recent logs
tail -f logs/*.log

# Or check application output
ps aux | grep chainlit
```

### 3. **Restart the Application**
```bash
# Kill existing processes
./start_eddie.sh

# Or manually:
lsof -ti:8000 | xargs kill -9
pkill -f "chainlit run"
./trading_bot.sh
```

### 4. **Check Database Connection**
If queries require database access, ensure PostgreSQL is running:
```bash
# Check if PostgreSQL is running
pg_isready

# If not, start it:
brew services start postgresql  # macOS
# or
sudo systemctl start postgresql  # Linux
```

---

## 🐛 Common Issues

### Issue 1: LLM Timeout
**Symptom:** Queries hang indefinitely
**Fix:** Increase timeout in `tradingagents/bot/agent.py`:
```python
self.llm = ChatOpenAI(
    model=model_name,
    base_url=base_url,
    api_key="ollama",
    temperature=temperature,
    timeout=300  # Increase from 120 to 300 seconds
)
```

### Issue 2: Tool Execution Hanging
**Symptom:** Tools take too long or hang
**Fix:** Some tools may require database. Check:
- Database connection is working
- Required data exists in database
- No network issues

### Issue 3: Ollama Model Not Loaded
**Symptom:** Ollama running but model not available
**Fix:**
```bash
# Check available models
ollama list

# Pull model if missing
ollama pull llama3.3
```

### Issue 4: Database Connection Issues
**Symptom:** Tools that require database hang
**Fix:**
- Check PostgreSQL is running
- Verify database credentials
- Check connection pool limits

---

## 🔍 Diagnostic Steps

### Step 1: Check System Status
```bash
# Check all components
echo "=== System Status ==="
echo "Ollama: $(curl -s http://localhost:11434/api/tags > /dev/null && echo 'Running' || echo 'Not Running')"
echo "Application: $(curl -s http://localhost:8000 > /dev/null && echo 'Running' || echo 'Not Running')"
echo "Port 8000: $(lsof -ti:8000 && echo 'In Use' || echo 'Free')"
```

### Step 2: Test Simple Query
Try a simple query that doesn't require database:
- "Hello"
- "What can you do?"
- "Explain priority score"

### Step 3: Check Browser Console
Open browser developer tools (F12) and check:
- Network tab for failed requests
- Console for JavaScript errors
- Any error messages

### Step 4: Enable Debug Mode
Modify `tradingagents/bot/chainlit_app.py`:
```python
agent = TradingAgent(
    model_name="llama3.3",
    base_url="http://localhost:11434/v1",
    temperature=0.7,
    debug=True  # Enable debug logging
)
```

---

## 🚀 Quick Restart Procedure

1. **Kill all processes:**
   ```bash
   ./start_eddie.sh
   ```

2. **Verify clean state:**
   ```bash
   lsof -ti:8000  # Should return nothing
   ```

3. **Start fresh:**
   ```bash
   ./trading_bot.sh
   ```

4. **Wait for startup:**
   - Look for "✓ Agent ready" message
   - Check http://localhost:8000 loads

5. **Test with simple query:**
   - "Hello" or "What can you do?"

---

## 📝 What to Check

### ✅ Pre-flight Checklist:
- [ ] Ollama is running (`ollama serve`)
- [ ] llama3.3 model is available (`ollama list`)
- [ ] Port 8000 is free
- [ ] No other chainlit processes running
- [ ] Database is accessible (if using database features)
- [ ] Browser console shows no errors

### ✅ When Querying:
- [ ] Start with simple queries first
- [ ] Check if response starts streaming
- [ ] Wait at least 30-60 seconds for complex queries
- [ ] Check browser network tab for activity

---

## 🆘 If Still Not Working

1. **Check Application Logs:**
   ```bash
   tail -f logs/*.log
   ```

2. **Test Ollama Directly:**
   ```bash
   curl http://localhost:11434/api/generate -d '{
     "model": "llama3.3",
     "prompt": "Hello",
     "stream": false
   }'
   ```

3. **Test Agent Directly:**
   ```python
   from tradingagents.bot.agent import TradingAgent
   agent = TradingAgent(debug=True)
   response = agent.chat("Hello")
   print(response)
   ```

4. **Check for Error Messages:**
   - Browser console (F12)
   - Terminal where app is running
   - Log files in `logs/` directory

---

## 💡 Expected Behavior

### Normal Response Flow:
1. User sends query
2. Eddie shows "thinking" indicator
3. Response starts streaming (word by word)
4. Complete response appears
5. Ready for next query

### If Hanging:
- Check if Ollama is processing (CPU usage)
- Check if tools are executing
- Check database connections
- Look for timeout errors

---

## 🔗 Related Files

- `tradingagents/bot/agent.py` - Agent implementation
- `tradingagents/bot/chainlit_app.py` - Web interface
- `tradingagents/bot/tools.py` - Tool definitions
- `trading_bot.sh` - Startup script

---

**Need more help?** Check the logs and error messages for specific issues.

