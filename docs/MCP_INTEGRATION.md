# MCP (Model Context Protocol) Integration

## Overview

Eddy now supports the Model Context Protocol (MCP), allowing external tools and resources to be integrated into the trading assistant. This enables community-contributed tools and extensibility.

## MCP Server Endpoints

### Initialize
```
GET /mcp/initialize
```
Returns server capabilities and protocol version.

### List Tools
```
GET /mcp/tools
```
Returns all available MCP tools.

### List Resources
```
GET /mcp/resources
```
Returns all available MCP resources.

### Call Tool
```
POST /mcp/tools/{tool_name}
Body: { "arguments": {...} }
```
Calls an MCP tool with the provided arguments.

### Read Resource
```
GET /mcp/resources/{uri}
```
Reads an MCP resource by URI.

### Register Tool
```
POST /mcp/tools/register
Body: {
  "name": "tool_name",
  "description": "Tool description",
  "inputSchema": {...}
}
```
Registers a new MCP tool (for external tool registration).

## Usage Example

```python
from tradingagents.mcp import MCPServer, convert_langchain_tool_to_mcp

# Initialize MCP server
mcp_server = MCPServer()
mcp_server.initialize()

# Register existing LangChain tools
for tool in agent.tools:
    mcp_tool = convert_langchain_tool_to_mcp(tool)
    mcp_server.register_tool(mcp_tool)

# Call a tool
result = mcp_server.call_tool("run_screener", {"top_n": 10})
```

## Tool Registration

Existing LangChain tools are automatically registered with the MCP server on startup. External tools can be registered via the `/mcp/tools/register` endpoint.

## Protocol Version

Current MCP protocol version: `2024-11-05`

