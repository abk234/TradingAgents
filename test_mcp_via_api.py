#!/usr/bin/env python3
"""
Test MCP tools via the running API server.
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8005"
TIMEOUT = 30

def wait_for_server(max_attempts=30):
    """Wait for the server to be ready."""
    print("Waiting for server to start...")
    for i in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code in [200, 401]:  # 401 is OK, means server is up
                print("✅ Server is ready!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        except Exception as e:
            print(f"   Attempt {i+1}/{max_attempts}: {e}")
        time.sleep(1)
    return False

def test_mcp_endpoints():
    """Test all MCP endpoints."""
    print("=" * 70)
    print("Testing MCP Tools via API")
    print("=" * 70)
    
    if not wait_for_server():
        print("❌ Server did not start in time")
        return False
    
    results = {}
    
    # Test 1: Initialize
    print("\n1. Testing GET /mcp/initialize...")
    try:
        response = requests.get(f"{BASE_URL}/mcp/initialize", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: Protocol version {data.get('protocolVersion', 'unknown')}")
            results['initialize'] = True
        else:
            print(f"   ⚠️  Status {response.status_code}: {response.text[:100]}")
            results['initialize'] = False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['initialize'] = False
    
    # Test 2: List tools
    print("\n2. Testing GET /mcp/tools...")
    try:
        response = requests.get(f"{BASE_URL}/mcp/tools", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            tool_count = data.get('count', 0)
            tools = data.get('tools', [])
            print(f"   ✅ Success: Found {tool_count} tools")
            if tools:
                print(f"   Sample tools: {', '.join([t.get('name', '?') for t in tools[:5]])}")
            results['list_tools'] = True
            results['tool_count'] = tool_count
            results['tools'] = tools
        else:
            print(f"   ⚠️  Status {response.status_code}: {response.text[:100]}")
            results['list_tools'] = False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['list_tools'] = False
    
    # Test 3: Get capabilities
    print("\n3. Testing GET /mcp/capabilities...")
    try:
        response = requests.get(f"{BASE_URL}/mcp/capabilities", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {len(data.get('capabilities', {}))} capabilities")
            results['capabilities'] = True
        else:
            print(f"   ⚠️  Status {response.status_code}: {response.text[:100]}")
            results['capabilities'] = False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['capabilities'] = False
    
    # Test 4: Call a tool (show_legend - no args needed)
    print("\n4. Testing POST /mcp/tools/show_legend...")
    try:
        response = requests.post(
            f"{BASE_URL}/mcp/tools/show_legend",
            json={"arguments": {}},
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            is_error = data.get('isError', False)
            if not is_error:
                print(f"   ✅ Success: Tool executed")
                results['call_tool'] = True
            else:
                print(f"   ⚠️  Tool returned error: {data.get('content', [{}])[0].get('text', 'Unknown')[:100]}")
                results['call_tool'] = False
        else:
            print(f"   ⚠️  Status {response.status_code}: {response.text[:200]}")
            results['call_tool'] = False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['call_tool'] = False
    
    # Test 5: Call a tool with arguments (analyze_sector)
    print("\n5. Testing POST /mcp/tools/analyze_sector...")
    try:
        response = requests.post(
            f"{BASE_URL}/mcp/tools/analyze_sector",
            json={"arguments": {"sector_name": "Technology"}},
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            is_error = data.get('isError', False)
            if not is_error:
                print(f"   ✅ Success: Sector analysis completed")
                results['call_tool_with_args'] = True
            else:
                error_text = data.get('content', [{}])[0].get('text', 'Unknown')[:200]
                print(f"   ⚠️  Tool returned error: {error_text}")
                results['call_tool_with_args'] = False
        else:
            print(f"   ⚠️  Status {response.status_code}: {response.text[:200]}")
            results['call_tool_with_args'] = False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['call_tool_with_args'] = False
    
    # Test 6: List resources
    print("\n6. Testing GET /mcp/resources...")
    try:
        response = requests.get(f"{BASE_URL}/mcp/resources", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            resource_count = data.get('count', 0)
            print(f"   ✅ Success: Found {resource_count} resources")
            results['list_resources'] = True
        else:
            print(f"   ⚠️  Status {response.status_code}: {response.text[:100]}")
            results['list_resources'] = False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['list_resources'] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if isinstance(v, bool) and v)
    total = sum(1 for v in results.values() if isinstance(v, bool))
    
    print(f"Tests passed: {passed}/{total}")
    if 'tool_count' in results:
        print(f"Tools available: {results['tool_count']}")
    
    print("\nDetailed Results:")
    for test_name, result in results.items():
        if isinstance(result, bool):
            status = "✅" if result else "❌"
            print(f"  {status} {test_name}")
    
    return passed == total

if __name__ == "__main__":
    success = test_mcp_endpoints()
    sys.exit(0 if success else 1)

