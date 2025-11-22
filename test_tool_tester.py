#!/usr/bin/env python3
"""
Comprehensive test script for Tool Tester verification.
Tests all 9 tools available in the Tool Tester UI.
"""

import requests
import json
import sys
from typing import Dict, Any, Tuple

BASE_URL = "http://localhost:8005"

# Tool definitions matching DevToolsView.tsx
TOOLS = [
    {
        "name": "run_screener",
        "args": {"sector_analysis": True, "top_n": 5},
        "description": "Run stock screener with sector analysis"
    },
    {
        "name": "get_top_stocks",
        "args": {"limit": 5},
        "description": "Get top performing stocks"
    },
    {
        "name": "analyze_sector",
        "args": {"sector_name": "Technology"},
        "description": "Analyze a specific sector"
    },
    {
        "name": "search_stocks",
        "args": {"sector": "Technology", "min_score": 50},
        "description": "Search stocks by sector and score"
    },
    {
        "name": "analyze_stock",
        "args": {"ticker": "AAPL", "portfolio_value": 100000},
        "description": "Analyze a specific stock"
    },
    {
        "name": "get_stock_summary",
        "args": {"ticker": "MSFT"},
        "description": "Get stock summary"
    },
    {
        "name": "get_stock_info",
        "args": {"ticker": "NVDA"},
        "description": "Get stock information"
    },
    {
        "name": "explain_metric",
        "args": {"metric_name": "RSI"},
        "description": "Explain a trading metric"
    },
    {
        "name": "show_legend",
        "args": {},
        "description": "Show trading legend"
    }
]


def test_tool(tool_name: str, args: Dict[str, Any], api_key: str = None) -> Tuple[bool, str, Any]:
    """
    Test a single tool execution.
    
    Returns:
        (success: bool, message: str, result: Any)
    """
    try:
        headers = {
            "Content-Type": "application/json"
        }
        if api_key:
            headers["X-API-Key"] = api_key
        
        response = requests.post(
            f"{BASE_URL}/debug/execute_tool",
            params={"tool_name": tool_name},
            json=args,
            headers=headers,
            timeout=60  # Increased timeout for tools that may take longer
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                result = data.get("result", "")
                # Check if result indicates an error (tools may return error strings)
                if isinstance(result, str):
                    if result.startswith("Error") or "connection error" in result.lower():
                        return False, f"Tool returned error: {result[:200]}", result
                return True, "Tool executed successfully", result
            else:
                error = data.get("error", "Unknown error")
                return False, f"Tool execution failed: {error}", None
        elif response.status_code == 401:
            return False, "Unauthorized - API key may be required", None
        elif response.status_code == 503:
            return False, "Service unavailable - Agent not initialized", None
        elif response.status_code == 404:
            return False, f"Tool '{tool_name}' not found", None
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}", None
            
    except requests.exceptions.ConnectionError:
        return False, "Connection error - Backend may not be running", None
    except requests.exceptions.Timeout:
        return False, "Request timeout - Tool took too long to execute", None
    except Exception as e:
        return False, f"Exception: {str(e)}", None


def test_all_tools(api_key: str = None) -> Dict[str, Any]:
    """
    Test all tools in the Tool Tester.
    
    Returns:
        Dictionary with test results
    """
    print("=" * 80)
    print("Tool Tester Verification")
    print("=" * 80)
    print(f"Testing {len(TOOLS)} tools against {BASE_URL}")
    print()
    
    results = {
        "total": len(TOOLS),
        "passed": 0,
        "failed": 0,
        "tools": {}
    }
    
    for i, tool_config in enumerate(TOOLS, 1):
        tool_name = tool_config["name"]
        args = tool_config["args"]
        description = tool_config["description"]
        
        print(f"[{i}/{len(TOOLS)}] Testing: {tool_name}")
        print(f"  Description: {description}")
        print(f"  Arguments: {json.dumps(args, indent=2)}")
        
        success, message, result = test_tool(tool_name, args, api_key)
        
        if success:
            print(f"  ✅ {message}")
            results["passed"] += 1
            results["tools"][tool_name] = {
                "status": "passed",
                "message": message,
                "result_preview": str(result)[:200] if result else None
            }
        else:
            print(f"  ❌ {message}")
            results["failed"] += 1
            results["tools"][tool_name] = {
                "status": "failed",
                "message": message,
                "error": str(result) if result else None
            }
        
        print()
    
    # Summary
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Total tools tested: {results['total']}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"Success rate: {(results['passed'] / results['total'] * 100):.1f}%")
    print()
    
    # Failed tools details
    if results["failed"] > 0:
        print("Failed Tools:")
        print("-" * 80)
        for tool_name, tool_result in results["tools"].items():
            if tool_result["status"] == "failed":
                print(f"  ❌ {tool_name}: {tool_result['message']}")
        print()
    
    return results


def check_backend_health() -> bool:
    """Check if backend is running and accessible."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def main():
    """Main entry point."""
    # Check backend health first
    print("Checking backend health...")
    if not check_backend_health():
        print(f"❌ Backend at {BASE_URL} is not accessible")
        print("   Please ensure the backend is running on port 8005")
        sys.exit(1)
    print(f"✅ Backend is running at {BASE_URL}")
    print()
    
    # Try to get API key from environment or command line
    api_key = None
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        # Try to read from common locations (for testing)
        import os
        api_key = os.environ.get("API_KEY")
        # Also try the documented key from AUTHENTICATION_SETUP.md
        if not api_key:
            api_key = "Uo8m722b5pkY4s8ixSqm3SkIGXcVR55JkjUm4cNaUlg"
    
    if api_key:
        print(f"Using API key: {api_key[:10]}...")
        print()
    else:
        print("⚠️  No API key provided - testing without authentication")
        print("   (Backend may require API key if API_KEY env var is set)")
        print()
    
    results = test_all_tools(api_key)
    
    # Exit with appropriate code
    if results["failed"] == 0:
        print("✅ All tools are functioning correctly!")
        sys.exit(0)
    else:
        print(f"⚠️  {results['failed']} tool(s) failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

