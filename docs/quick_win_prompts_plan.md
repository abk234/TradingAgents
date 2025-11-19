# Quick Win Prompts for Eddie AI

Implement a predefined prompt system focused on profit-making opportunities. Eddie's goal is to help traders identify actionable stock opportunities with clear justification using the multi-agent backend.

## Proposed Changes

### Frontend Components

#### [NEW] [PromptCategories.tsx](file:///Users/lxupkzwjs/Developer/eval/TradingAgents/web-app/components/PromptCategories.tsx)

Create a new component to organize and display categorized prompts. The component will render collapsible sections for four categories:

- **Quick Wins**: Immediate profit opportunities
- **Deep Analysis**: Detailed stock evaluation
- **Risk Management**: Risk assessment tools
- **Market Intelligence**: Market context and trends

Each category will display prompt buttons with icons and clear labels. Prompts will be configured with metadata including category, icon, and color scheme.

#### [MODIFY] [ChatInterface.tsx](file:///Users/lxupkzwjs/Developer/eval/TradingAgents/web-app/components/ChatInterface.tsx)

Update the chat interface to:
- Replace the current `SUGGESTED_PROMPTS` (lines 20-25) with a comprehensive categorized prompt system
- Add a persistent prompt panel that can be toggled via a button in the header
- Keep the initial welcome prompts but make them category-focused
- Integrate the new `PromptCategories` component
- Add visual feedback when prompts are clicked (loading state per category)

### Prompt Configuration

#### [NEW] [prompts.config.ts](file:///Users/lxupkzwjs/Developer/eval/TradingAgents/web-app/lib/prompts.config.ts)

Create a centralized configuration file defining all prompts with metadata:

```typescript
type PromptConfig = {
  id: string
  category: 'quick_wins' | 'analysis' | 'risk' | 'market'
  label: string
  prompt: string
  icon: string
  description: string
}
```

Prompts will include:

**Quick Wins:**
- "Show me top 3 stocks to buy TODAY"
- "What stocks are breaking out right now?"
- "Find me undervalued stocks ready to move"

**Deep Analysis:**
- "Analyze [TICKER] - should I buy?"
- "What are the bullish and bearish cases for [TICKER]?"
- "Show me the technical setup for [TICKER]"

**Risk Management:**
- "What's the risk on [TICKER]?"
- "Should I exit [TICKER]?"
- "Calculate position size for [TICKER] with $X portfolio"

**Market Intelligence:**
- "What's moving the market today?"
- "What sectors are hot right now?"
- "Show me stocks with positive news catalysts"

---

### Backend Optimizations

#### [MODIFY] [main.py](file:///Users/lxupkzwjs/Developer/eval/TradingAgents/tradingagents/api/main.py)

Add optional prompt metadata to the chat endpoint:
- Accept a `prompt_type` field in `ChatRequest` to identify predefined prompts
- Log prompt types for analytics
- Enable future optimizations for known prompt patterns

#### [MODIFY] [models.py](file:///Users/lxupkzwjs/Developer/eval/TradingAgents/tradingagents/api/models.py)

Extend `ChatRequest` model to include optional fields:
- `prompt_type: Optional[str]` - Category identifier
- `prompt_id: Optional[str]` - Specific prompt identifier

This allows the backend to optimize responses for known prompt patterns in the future.

---

### UI/UX Enhancements

#### [NEW] [Button.tsx variant](file:///Users/lxupkzwjs/Developer/eval/TradingAgents/web-app/components/ui/button.tsx)

Add a new `prompt` button variant with category-specific styling:
- Gradient backgrounds per category
- Hover effects with scale animations
- Icon + text layout

## Verification Plan

### Manual UI Testing

Since this is primarily a UI enhancement, verification will be manual:

1. **Start the application**:
   ```bash
   # Terminal 1: Backend
   cd /Users/lxupkzwjs/Developer/eval/TradingAgents
   python -m tradingagents.api.main
   
   # Terminal 2: Frontend
   cd /Users/lxupkzwjs/Developer/eval/TradingAgents/web-app
   npm run dev
   ```

2. **Test initial load**:
   - Navigate to `http://localhost:3005`
   - Verify categorized prompts are visible on welcome screen
   - Confirm prompts are organized by category with proper styling

3. **Test Quick Win prompts**:
   - Click "Show me top 3 stocks to buy TODAY"
   - Verify Eddie coordinates all agents (check console logs)
   - Confirm response includes stock symbols, prices, justifications, indicators
   - Validate response structure is clear and actionable

4. **Test Deep Analysis prompts**:
   - Click "Analyze AAPL - should I buy?"
   - Verify multi-agent analysis runs
   - Confirm bullish/bearish cases are presented
   - Check that technical, fundamental, sentiment data are included

5. **Test Risk Management prompts**:
   - Click "What's the risk on TSLA?"
   - Verify risk assessment is provided
   - Confirm risk score and downside analysis are clear

6. **Test Market Intelligence prompts**:
   - Click "What's moving the market today?"
   - Verify news and sentiment analysis
   - Confirm market drivers are identified

7. **Test prompt panel persistence**:
   - Send several messages
   - Click toggle button to show/hide prompt panel
   - Verify panel state persists between interactions

8. **Test responsive design**:
   - Resize browser to mobile width
   - Verify prompts stack vertically
   - Confirm all buttons remain clickable

9. **Test feedback system**:
   - After receiving response from a prompt
   - Click thumbs up/down
   - Verify feedback is sent to backend (check logs)

### Browser Console Validation

- No console errors during any interactions
- Verify API calls include `prompt_type` when using predefined prompts
- Check network tab for proper request/response structure

### Backend Logging

- Verify backend logs show prompt type for predefined prompts
- Confirm all agent coordination happens as expected
- Check Langfuse traces capture prompt metadata
