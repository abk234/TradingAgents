# AnythingLLM Features Setup Guide

This guide will help you set up and use the new features integrated from AnythingLLM analysis.

## Prerequisites

1. **Database Migrations**
   - Run the new migration scripts to create required tables
   - Documents: `database/migrations/002_add_documents_table.sql`
   - Workspaces: `database/migrations/003_add_workspaces_table.sql`

2. **Python Dependencies** (for document processing)
   - `PyPDF2` - For PDF parsing (optional)
   - `beautifulsoup4` - For HTML parsing (optional)
   - `python-docx` - For DOCX parsing (optional)

   Install with:
   ```bash
   pip install PyPDF2 beautifulsoup4 python-docx
   ```

## Setup Steps

### 1. Run Database Migrations

```bash
# Connect to your PostgreSQL database
psql -U your_user -d your_database

# Run migrations
\i database/migrations/002_add_documents_table.sql
\i database/migrations/003_add_workspaces_table.sql
```

Or use your preferred database migration tool.

### 2. Start the API Server

```bash
# From project root
python -m tradingagents.api.main
```

The server will start on `http://localhost:8005`

### 3. Verify Installation

Run the validation script:

```bash
python test_anythingllm_features.py
```

This will test all three features:
- MCP Integration
- Document Processing
- Workspace Management

## Feature Usage

### MCP Integration

**List available tools:**
```bash
curl http://localhost:8005/mcp/tools
```

**Call a tool:**
```bash
curl -X POST http://localhost:8005/mcp/tools/run_screener \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"top_n": 10}}'
```

**Register external tool:**
```bash
curl -X POST http://localhost:8005/mcp/tools/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "custom_tool",
    "description": "Custom trading tool",
    "inputSchema": {
      "type": "object",
      "properties": {
        "symbol": {"type": "string"}
      }
    }
  }'
```

### Document Processing

**Upload a document:**
```bash
curl -X POST http://localhost:8005/documents/upload \
  -F "file=@earnings_report.pdf" \
  -F "ticker=AAPL"
```

**List documents:**
```bash
curl http://localhost:8005/documents?ticker=AAPL
```

**Get document details:**
```bash
curl http://localhost:8005/documents/1
```

**Get document insights:**
```bash
curl http://localhost:8005/documents/1/insights
```

### Workspace Management

**Create workspace:**
```bash
curl -X POST http://localhost:8005/workspaces \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Growth Portfolio",
    "description": "High-growth stocks workspace",
    "is_default": false
  }'
```

**List workspaces:**
```bash
curl http://localhost:8005/workspaces
```

**Get default workspace:**
```bash
curl http://localhost:8005/workspaces/default
```

**Get workspace tickers:**
```bash
curl http://localhost:8005/workspaces/1/tickers
```

**Get workspace analyses:**
```bash
curl http://localhost:8005/workspaces/1/analyses
```

## Integration with Existing Features

### Using Workspaces in Analysis

When creating analyses, you can now scope them to workspaces:

```python
from tradingagents.database.workspace_ops import WorkspaceOperations

workspace_ops = WorkspaceOperations()
workspace = workspace_ops.get_default_workspace()
workspace_id = workspace['workspace_id']

# Use workspace_id when creating analyses
```

### Using Document Insights

Document insights are automatically linked to analyses when documents are uploaded with a ticker:

```python
from tradingagents.database.document_ops import DocumentOperations

doc_ops = DocumentOperations()
insights = doc_ops.get_document_insights(analysis_id=123)
```

### Using MCP Tools

MCP tools are automatically registered from existing LangChain tools. You can also register custom tools:

```python
from tradingagents.mcp import MCPServer, convert_function_to_mcp

mcp_server = MCPServer()
mcp_server.initialize()

# Register a custom function
def my_custom_tool(symbol: str) -> str:
    """Custom trading tool"""
    return f"Analysis for {symbol}"

mcp_tool = convert_function_to_mcp(my_custom_tool)
mcp_server.register_tool(mcp_tool)
```

## Troubleshooting

### Document Processing Fails

- **Issue:** PDF parsing fails
- **Solution:** Install `PyPDF2`: `pip install PyPDF2`

- **Issue:** HTML parsing fails
- **Solution:** Install `beautifulsoup4`: `pip install beautifulsoup4`

- **Issue:** DOCX parsing fails
- **Solution:** Install `python-docx`: `pip install python-docx`

### Workspace Queries Return Empty

- **Issue:** No workspaces found
- **Solution:** Run migration `003_add_workspaces_table.sql` which creates a default workspace

### MCP Tools Not Available

- **Issue:** No tools listed
- **Solution:** Ensure the conversational agent is initialized. Tools are registered on server startup.

## Next Steps

1. **Frontend Integration:**
   - Add document upload UI
   - Add workspace selector
   - Display document insights in analysis views

2. **Advanced Features:**
   - Async document processing queue
   - Document chunking for large files
   - Workspace templates
   - Document versioning

3. **Performance:**
   - Add caching for document insights
   - Optimize workspace queries
   - Add pagination for large result sets

## API Documentation

Full API documentation is available at:
- Swagger UI: `http://localhost:8005/docs`
- ReDoc: `http://localhost:8005/redoc`

## Support

For issues or questions:
1. Check the implementation summary: `docs/ANYTHINGLLM_IMPLEMENTATION_SUMMARY.md`
2. Review the analysis document: `docs/ANYTHINGLLM_ANALYSIS.md`
3. Check API logs for detailed error messages

