# Quick Actions UI Testing Guide

This guide provides step-by-step instructions for testing all 15 Quick Action prompts in the Eddie UI.

## Prerequisites

1. **Backend Server Running**: Ensure the backend is running on `http://127.0.0.1:8005`
2. **API Key Set**: Make sure your API key is configured in localStorage (check DevTools → Application → Local Storage)
3. **Frontend Running**: Start the Next.js frontend with `npm run dev` (or your preferred command)

## Test Categories

### 1. Quick Wins (3 prompts) - No ticker required

#### Test 1.1: Top 3 Stocks to Buy Today
1. Open the chat interface
2. Click the bookmark icon to show the Quick Actions panel (if not visible)
3. Expand the **Quick Wins** category (should be expanded by default)
4. Click **"Top 3 Stocks to Buy Today"**
5. **Expected**: 
   - Button shows loading spinner
   - Chat shows "Coordinating agents..." message
   - Response includes top 3 stock recommendations with justifications, entry points, and confidence scores

#### Test 1.2: Stocks Breaking Out Now
1. In the **Quick Wins** category
2. Click **"Stocks Breaking Out Now"**
3. **Expected**:
   - Response identifies momentum plays with technical breakout patterns
   - Includes news catalysts
   - Shows actionable trading opportunities

#### Test 1.3: Undervalued Stocks Ready to Move
1. In the **Quick Wins** category
2. Click **"Undervalued Stocks Ready to Move"**
3. **Expected**:
   - Response finds undervalued stocks
   - Includes value plays with positive catalysts
   - Shows reversal signals

---

### 2. Deep Analysis (4 prompts) - Ticker required

#### Test 2.1: Should I Buy This Stock?
1. Expand the **Deep Analysis** category
2. Enter a ticker (e.g., "AAPL") in the input field
3. Click **"Should I Buy This Stock?"**
4. **Expected**:
   - Ticker input clears after submission
   - Comprehensive multi-agent analysis
   - Clear buy/hold/sell recommendation

#### Test 2.2: Bullish vs Bearish Cases
1. In **Deep Analysis** category
2. Enter a ticker (e.g., "NVDA")
3. Click **"Bullish vs Bearish Cases"**
4. **Expected**:
   - Response shows both bullish and bearish perspectives
   - Includes detailed reasoning for each side
   - Provides confidence scores

#### Test 2.3: Technical Setup Analysis
1. In **Deep Analysis** category
2. Enter a ticker (e.g., "TSLA")
3. Click **"Technical Setup Analysis"**
4. **Expected**:
   - Shows chart patterns
   - Includes key support/resistance levels
   - Provides indicators, entry point, stop loss, and price targets

#### Test 2.4: Fundamental Deep Dive
1. In **Deep Analysis** category
2. Enter a ticker (e.g., "MSFT")
3. Click **"Fundamental Deep Dive"**
4. **Expected**:
   - Covers financials and valuation metrics
   - Analyzes growth prospects
   - Evaluates competitive position

---

### 3. Risk Management (3 prompts) - Ticker required

#### Test 3.1: What's the Risk?
1. Expand the **Risk Management** category
2. Enter a ticker (e.g., "GOOGL")
3. Click **"What's the Risk?"**
4. **Expected**:
   - Provides risk score
   - Shows potential downside scenarios
   - Recommends position sizing

#### Test 3.2: Should I Exit?
1. In **Risk Management** category
2. Enter a ticker (e.g., "AAPL")
3. Click **"Should I Exit?"**
4. **Expected**:
   - Re-analyzes the stock
   - Provides clear hold or sell recommendation
   - Includes reasoning

#### Test 3.3: Stop Loss & Price Targets
1. In **Risk Management** category
2. Enter a ticker (e.g., "NVDA")
3. Click **"Stop Loss & Price Targets"**
4. **Expected**:
   - Calculates optimal stop loss
   - Provides price targets
   - Based on technical analysis and volatility

---

### 4. Market Intelligence (4 prompts) - No ticker required

#### Test 4.1: What's Moving the Market?
1. Expand the **Market Intelligence** category
2. Click **"What's Moving the Market?"**
3. **Expected**:
   - Shows key market drivers
   - Includes news events
   - Explains how they're affecting stocks

#### Test 4.2: Hot Sectors Right Now
1. In **Market Intelligence** category
2. Click **"Hot Sectors Right Now"**
3. **Expected**:
   - Identifies trending sectors
   - Provides specific stock picks in each sector

#### Test 4.3: Stocks with Positive Catalysts
1. In **Market Intelligence** category
2. Click **"Stocks with Positive Catalysts"**
3. **Expected**:
   - Shows stocks with positive news catalysts
   - Explains potential price movement drivers

#### Test 4.4: Key Earnings This Week
1. In **Market Intelligence** category
2. Click **"Key Earnings This Week"**
3. **Expected**:
   - Lists important earnings reports
   - Identifies stocks to watch

---

## UI Component Testing

### Category Expansion/Collapse
- [ ] Click each category header to expand/collapse
- [ ] Verify chevron icon changes (up/down)
- [ ] Verify smooth animation

### Ticker Input Fields
- [ ] Verify input appears for prompts requiring ticker
- [ ] Test entering ticker and pressing Enter
- [ ] Verify ticker input clears after submission
- [ ] Test clicking prompt without ticker (should focus input)

### Loading States
- [ ] Verify loading spinner appears on clicked prompt
- [ ] Verify "Processing..." text replaces description
- [ ] Verify button is disabled during loading
- [ ] Verify other prompts remain clickable (unless global loading)

### Visual Feedback
- [ ] Verify category colors match:
  - Quick Wins: Green gradient
  - Deep Analysis: Blue gradient
  - Risk Management: Amber/Orange gradient
  - Market Intelligence: Purple gradient
- [ ] Verify icons display correctly for each prompt
- [ ] Verify hover effects on prompt buttons

### Error Handling
- [ ] Test with invalid API key (should show auth error)
- [ ] Test with backend offline (should show connection error)
- [ ] Verify error messages are user-friendly

---

## Automated Testing

Run the automated test script:

```bash
# Set environment variables
export API_URL=http://127.0.0.1:8005
export API_KEY=your_api_key_here

# Run tests
python test_all_quick_actions.py
```

The script will:
- Test all 15 prompts programmatically
- Verify API responses
- Generate a test report JSON file
- Show colored output in terminal

---

## Common Issues & Solutions

### Issue: "Authentication failed"
**Solution**: Check that API key is set in localStorage and matches backend configuration

### Issue: "Service unavailable"
**Solution**: Ensure backend server is running and agent is initialized

### Issue: No response received
**Solution**: 
- Check browser console for errors
- Verify network tab shows successful requests
- Check backend logs for errors

### Issue: Ticker input not working
**Solution**: 
- Verify input field is visible for ticker-required prompts
- Check that Enter key triggers submission
- Verify ticker is being inserted into prompt correctly

---

## Test Checklist

- [ ] All 3 Quick Wins prompts work
- [ ] All 4 Deep Analysis prompts work (with tickers)
- [ ] All 3 Risk Management prompts work (with tickers)
- [ ] All 4 Market Intelligence prompts work
- [ ] Category expand/collapse works
- [ ] Ticker inputs work correctly
- [ ] Loading states display properly
- [ ] Error handling works
- [ ] Visual feedback is correct
- [ ] No console errors
- [ ] No TypeScript errors

---

## Notes

- Each prompt sends metadata (`prompt_type` and `prompt_id`) to the backend
- The backend can use this metadata for prompt-specific optimizations
- All prompts use the streaming chat endpoint (`/chat/stream`)
- Responses are displayed in real-time as they stream in

