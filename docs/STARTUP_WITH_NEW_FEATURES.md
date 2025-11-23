# Starting Application with AnythingLLM Features

## Quick Start

Use the existing startup script - it works with all new features:

```bash
./start.sh
```

## What the Script Does

The `start.sh` script:
1. ✅ Checks all dependencies (Python, Node.js, databases)
2. ✅ Verifies virtual environment and packages
3. ✅ Checks for database migrations (new tables)
4. ✅ Starts backend API on port 8005
5. ✅ Starts frontend UI on port 3005
6. ✅ Waits for services to be ready

## New Features Available

Once started, you'll have access to:

### 1. Documents View
- **Access:** Sidebar → "Documents"
- **URL:** http://localhost:3005 (then click Documents)
- **Features:** Upload PDF/HTML/TXT/DOCX, view insights, manage documents

### 2. Workspaces View
- **Access:** Sidebar → "Workspaces"
- **URL:** http://localhost:3005 (then click Workspaces)
- **Features:** Create workspaces, organize analyses, set defaults

### 3. MCP Tools View
- **Access:** Sidebar → "MCP Tools"
- **URL:** http://localhost:3005 (then click MCP Tools)
- **Features:** List tools, execute tools, view capabilities

## Database Migrations

Before using Documents and Workspaces features, run migrations:

```bash
# Connect to your database
psql -U your_user -d your_database

# Run migrations
\i database/migrations/002_add_documents_table.sql
\i database/migrations/003_add_workspaces_table.sql
```

The startup script will warn you if tables don't exist.

## Testing the UI

After running `./start.sh`:

1. **Open browser:** http://localhost:3005
2. **Test Documents:**
   - Click "Documents" in sidebar
   - Upload a test file
   - Verify it processes and appears in list

3. **Test Workspaces:**
   - Click "Workspaces" in sidebar
   - Create a new workspace
   - Verify it appears in grid

4. **Test MCP Tools:**
   - Click "MCP Tools" in sidebar
   - Select a tool
   - Execute with JSON arguments
   - Verify results

## Troubleshooting

### Backend won't start
- Check if port 8005 is in use: `lsof -i:8005`
- Check Python dependencies: `pip install -e .`
- Check logs in `/tmp/tradingagents_startup.log`

### Frontend won't start
- Check if port 3005 is in use: `lsof -i:3005`
- Check Node dependencies: `cd web-app && npm install`
- Check for build errors: `cd web-app && npm run build`

### Features not working
- Ensure database migrations are run
- Check API is responding: `curl http://localhost:8005/health`
- Check browser console for errors

## Alternative: Manual Testing Script

For automated testing:

```bash
./test_ui_with_start.sh
```

This will:
1. Start the application
2. Wait for services
3. Test all endpoints
4. Report results

---

**All new features are integrated and ready to use with `./start.sh`!**

