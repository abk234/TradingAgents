# Testing MCP Tools with start.sh

## Quick Start

1. **Start the application:**
   ```bash
   ./start.sh
   ```
   
   When prompted about Redis warning, type `y` and press Enter to continue.

2. **Wait for services to start:**
   - Backend will be available at: http://localhost:8005
   - Frontend will be available at: http://localhost:3005
   - You'll see: "✨ TradingAgents is Running!"

3. **Test MCP tools:**
   
   **Option A: Using the test script (in another terminal):**
   ```bash
   ./test_mcp_live.sh
   ```
   
   **Option B: Using Python test:**
   ```bash
   python3 test_mcp_via_api.py
   ```
   
   **Option C: Via API directly:**
   ```bash
   # List all tools
   curl http://localhost:8005/mcp/tools
   
   # Call a tool
   curl -X POST http://localhost:8005/mcp/tools/show_legend \
     -H "Content-Type: application/json" \
     -d '{"arguments": {}}'
   
   # Call a tool with arguments
   curl -X POST http://localhost:8005/mcp/tools/analyze_sector \
     -H "Content-Type: application/json" \
     -d '{"arguments": {"sector_name": "Technology"}}'
   ```
   
   **Option D: Via Frontend UI:**
   1. Open http://localhost:3005
   2. Click "MCP Tools" in the sidebar
   3. Select a tool from the dropdown
   4. Enter arguments as JSON (e.g., `{"sector_name": "Technology"}`)
   5. Click "Execute Tool"

## Available Test Scripts

### 1. `test_mcp_live.sh`
Bash script that tests MCP endpoints via curl. Works best when server is already running.

**Usage:**
```bash
./test_mcp_live.sh
```

### 2. `test_mcp_via_api.py`
Python script that tests MCP endpoints with detailed output.

**Usage:**
```bash
python3 test_mcp_via_api.py
```

### 3. `test_mcp_tools.py`
Comprehensive test that initializes agent and tests tools directly (doesn't require running server).

**Usage:**
```bash
python3 test_mcp_tools.py
```

## Testing Individual Tools

### Tools with No Arguments
```bash
# show_legend
curl -X POST http://localhost:8005/mcp/tools/show_legend \
  -H "Content-Type: application/json" \
  -d '{"arguments": {}}'

# get_portfolio_status
curl -X POST http://localhost:8005/mcp/tools/get_portfolio_status \
  -H "Content-Type: application/json" \
  -d '{"arguments": {}}'

# show_data_dashboard
curl -X POST http://localhost:8005/mcp/tools/show_data_dashboard \
  -H "Content-Type: application/json" \
  -d '{"arguments": {}}'
```

### Tools with Arguments
```bash
# analyze_sector
curl -X POST http://localhost:8005/mcp/tools/analyze_sector \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"sector_name": "Technology"}}'

# get_stock_info
curl -X POST http://localhost:8005/mcp/tools/get_stock_info \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"ticker": "AAPL"}}'

# run_screener
curl -X POST http://localhost:8005/mcp/tools/run_screener \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"sector_analysis": true, "top_n": 10}}'

# analyze_stock
curl -X POST http://localhost:8005/mcp/tools/analyze_stock \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"ticker": "AAPL", "portfolio_value": 100000}}'
```

## Expected Results

### Successful Response
```json
{
  "content": [
    {
      "type": "text",
      "text": "...tool output..."
    }
  ],
  "isError": false
}
```

### Error Response
```json
{
  "content": [
    {
      "type": "text",
      "text": "Error: ...error message..."
    }
  ],
  "isError": true
}
```

## Troubleshooting

### Server Not Starting
- Check if ports 8005 and 3005 are available
- Check logs in `/tmp/tradingagents_startup.log`
- Ensure PostgreSQL is running
- Verify `.env` file exists and has required API keys

### Tools Not Found (404)
- Ensure agent initialized successfully
- Check backend logs for tool registration errors
- Verify MCP server initialized: `curl http://localhost:8005/mcp/initialize`

### Tool Execution Errors
- Check tool arguments match the schema
- Verify required arguments are provided
- Check backend logs for detailed error messages

### Authentication Errors (401)
- If `API_KEY` is set in `.env`, include it in requests:
  ```bash
  curl -H "X-API-Key: your-api-key" http://localhost:8005/mcp/tools
  ```

## All 27 Available Tools

1. `advanced_research`
2. `analyze_sector`
3. `analyze_stock`
4. `check_data_quality`
5. `check_earnings_risk`
6. `check_past_performance`
7. `explain_agents`
8. `explain_metric`
9. `find_similar_situations`
10. `get_portfolio_status`
11. `get_stock_info`
12. `get_stock_summary`
13. `get_top_stocks`
14. `quick_fundamentals_check`
15. `quick_news_check`
16. `quick_sentiment_check`
17. `quick_technical_check`
18. `research_from_web`
19. `run_screener`
20. `run_system_doctor_check`
21. `search_stocks`
22. `show_data_dashboard`
23. `show_legend`
24. `synthesize_speech`
25. `validate_news_multi_source`
26. `validate_price_sources`
27. `what_did_i_learn`

## Next Steps

After verifying tools work:
- Use tools in the frontend UI
- Integrate tools into your workflows
- Register custom tools via `/mcp/tools/register`
- Explore tool capabilities via API docs: http://localhost:8005/docs

