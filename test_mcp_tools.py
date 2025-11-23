#!/usr/bin/env python3
"""
Comprehensive test script for MCP tools.

Tests:
1. MCP server initialization
2. Tool registration
3. Tool listing
4. Tool schema validation
5. Tool execution with proper arguments
"""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tradingagents.mcp import MCPServer, convert_langchain_tool_to_mcp
from tradingagents.bot.conversational_agent import ConversationalAgent
from tradingagents.default_config import DEFAULT_CONFIG

def test_mcp_tools():
    """Test all MCP tools."""
    print("=" * 70)
    print("MCP Tools Comprehensive Test")
    print("=" * 70)
    
    # Initialize agent to get tools
    print("\n1. Initializing Conversational Agent...")
    try:
        agent = ConversationalAgent(config=DEFAULT_CONFIG)
        print("   ✅ Agent initialized")
    except Exception as e:
        print(f"   ❌ Failed to initialize agent: {e}")
        return False
    
    # Initialize MCP server
    print("\n2. Initializing MCP Server...")
    try:
        mcp_server = MCPServer()
        mcp_server.initialize()
        print("   ✅ MCP server initialized")
    except Exception as e:
        print(f"   ❌ Failed to initialize MCP server: {e}")
        return False
    
    # Register tools
    print("\n3. Registering tools with MCP server...")
    registered_tools = []
    failed_tools = []
    
    if agent and agent.trading_agent and hasattr(agent.trading_agent, 'tools'):
        tools = agent.trading_agent.tools
        print(f"   Found {len(tools)} tools to register")
        
        for tool in tools:
            try:
                mcp_tool = convert_langchain_tool_to_mcp(tool)
                mcp_server.register_tool(mcp_tool)
                registered_tools.append(tool.name)
                print(f"   ✅ Registered: {tool.name}")
            except Exception as e:
                failed_tools.append((tool.name, str(e)))
                print(f"   ❌ Failed to register {tool.name}: {e}")
    else:
        print("   ⚠️  No tools found in agent")
        return False
    
    print(f"\n   Summary: {len(registered_tools)} registered, {len(failed_tools)} failed")
    
    # List tools
    print("\n4. Listing registered MCP tools...")
    try:
        tools_list = mcp_server.list_tools()
        print(f"   ✅ Found {len(tools_list)} tools in MCP server")
    except Exception as e:
        print(f"   ❌ Failed to list tools: {e}")
        return False
    
    # Validate tool schemas
    print("\n5. Validating tool schemas...")
    schema_issues = []
    for tool_info in tools_list:
        tool_name = tool_info.get('name', 'unknown')
        input_schema = tool_info.get('inputSchema', {})
        
        # Check if schema has required structure
        if not isinstance(input_schema, dict):
            schema_issues.append((tool_name, "inputSchema is not a dict"))
            continue
        
        properties = input_schema.get('properties', {})
        required = input_schema.get('required', [])
        
        # Check if required fields are in properties
        missing_props = [r for r in required if r not in properties]
        if missing_props:
            schema_issues.append((tool_name, f"Required fields missing from properties: {missing_props}"))
        
        if not schema_issues:
            print(f"   ✅ {tool_name}: Schema valid")
        else:
            for issue in schema_issues:
                if issue[0] == tool_name:
                    print(f"   ⚠️  {tool_name}: {issue[1]}")
    
    if schema_issues:
        print(f"\n   ⚠️  Found {len(schema_issues)} schema issues")
    else:
        print("   ✅ All tool schemas are valid")
    
    # Test a few representative tools
    print("\n6. Testing tool execution with sample arguments...")
    
    test_cases = [
        {
            "name": "analyze_sector",
            "arguments": {"sector_name": "Technology"},
            "expected_success": True
        },
        {
            "name": "get_stock_info",
            "arguments": {"ticker": "AAPL"},
            "expected_success": True
        },
        {
            "name": "run_screener",
            "arguments": {"sector_analysis": True, "top_n": 5},
            "expected_success": True
        },
        {
            "name": "show_legend",
            "arguments": {},
            "expected_success": True
        },
        {
            "name": "get_portfolio_status",
            "arguments": {},
            "expected_success": True
        },
    ]
    
    execution_results = []
    for test_case in test_cases:
        tool_name = test_case["name"]
        arguments = test_case["arguments"]
        expected = test_case["expected_success"]
        
        if tool_name not in registered_tools:
            print(f"   ⚠️  {tool_name}: Not registered, skipping")
            continue
        
        print(f"\n   Testing: {tool_name}")
        print(f"   Arguments: {json.dumps(arguments, indent=2)}")
        
        try:
            # Test argument unwrapping (simulate frontend format)
            wrapped_args = {"arguments": arguments}
            result = mcp_server.call_tool(tool_name, wrapped_args)
            
            if result.get("isError", False):
                print(f"   ❌ {tool_name}: Tool returned error")
                execution_results.append((tool_name, False, result.get("content", [{}])[0].get("text", "Unknown error")))
            else:
                print(f"   ✅ {tool_name}: Execution successful")
                execution_results.append((tool_name, True, "Success"))
        except Exception as e:
            print(f"   ❌ {tool_name}: Exception: {e}")
            execution_results.append((tool_name, False, str(e)))
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Total tools registered: {len(registered_tools)}")
    print(f"Tools with schema issues: {len(schema_issues)}")
    print(f"Tools tested: {len(execution_results)}")
    
    successful_tests = sum(1 for _, success, _ in execution_results if success)
    print(f"Successful executions: {successful_tests}/{len(execution_results)}")
    
    if failed_tools:
        print(f"\n⚠️  Failed to register {len(failed_tools)} tools:")
        for tool_name, error in failed_tools:
            print(f"   - {tool_name}: {error}")
    
    if schema_issues:
        print(f"\n⚠️  Schema issues found:")
        for tool_name, issue in schema_issues:
            print(f"   - {tool_name}: {issue}")
    
    if execution_results:
        failed_executions = [(name, error) for name, success, error in execution_results if not success]
        if failed_executions:
            print(f"\n⚠️  Failed executions:")
            for tool_name, error in failed_executions:
                print(f"   - {tool_name}: {error}")
    
    # List all registered tools
    print("\n" + "=" * 70)
    print("All Registered MCP Tools")
    print("=" * 70)
    for i, tool_name in enumerate(sorted(registered_tools), 1):
        print(f"{i:3d}. {tool_name}")
    
    return len(failed_tools) == 0 and len(schema_issues) == 0 and successful_tests == len(execution_results)

if __name__ == "__main__":
    success = test_mcp_tools()
    sys.exit(0 if success else 1)

