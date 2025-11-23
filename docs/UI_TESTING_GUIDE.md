# UI Testing Guide - AnythingLLM Integration

## Quick Start

1. **Start API Server:**
   ```bash
   python -m tradingagents.api.main
   ```

2. **Start Frontend:**
   ```bash
   cd web-app
   npm run dev
   ```

3. **Open Browser:**
   ```
   http://localhost:3000
   ```

---

## Testing Checklist

### ✅ Documents View
- [ ] Navigate to "Documents" in sidebar
- [ ] Upload a test file (TXT, PDF, or HTML)
- [ ] Verify file appears in list
- [ ] Check document status
- [ ] View document details
- [ ] Search documents
- [ ] Delete a document

### ✅ Workspaces View
- [ ] Navigate to "Workspaces" in sidebar
- [ ] Create a new workspace
- [ ] Set workspace as default
- [ ] Search workspaces
- [ ] Delete a workspace

### ✅ MCP Tools View
- [ ] Navigate to "MCP Tools" in sidebar
- [ ] Verify server capabilities display
- [ ] Select a tool
- [ ] Enter JSON arguments
- [ ] Execute tool
- [ ] Verify results display

---

## Expected Results

All three views should:
- ✅ Load without errors
- ✅ Display data from API
- ✅ Handle errors gracefully
- ✅ Show loading states
- ✅ Provide user feedback

---

## Files Verified

✅ `web-app/components/DocumentsView.tsx` - Created
✅ `web-app/components/WorkspacesView.tsx` - Created
✅ `web-app/components/MCPToolsView.tsx` - Created
✅ `web-app/lib/api/client.ts` - Updated with new methods
✅ `web-app/components/Sidebar.tsx` - Updated with new menu items
✅ `web-app/app/page.tsx` - Updated with route handlers

**Build Status:** ✅ Frontend builds successfully

