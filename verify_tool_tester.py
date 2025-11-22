#!/usr/bin/env python3
"""
Comprehensive Tool Tester Verification Script

This script verifies:
1. Tool definitions match between frontend (DevToolsView.tsx) and backend (tools.py)
2. Backend connectivity and authentication
3. All 9 tools execute successfully
4. Generates a detailed verification report
"""

import sys
import os
import json
import re
from typing import Dict, List, Any, Tuple

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from tradingagents.bot.tools import get_all_tools
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False
    print("⚠️  Warning: Cannot import backend tools module")

# Tool definitions from DevToolsView.tsx
FRONTEND_TOOLS = [
    {"name": "run_screener", "defaultArgs": {"sector_analysis": True, "top_n": 5}},
    {"name": "get_top_stocks", "defaultArgs": {"limit": 5}},
    {"name": "analyze_sector", "defaultArgs": {"sector_name": "Technology"}},
    {"name": "search_stocks", "defaultArgs": {"sector": "Technology", "min_score": 50}},
    {"name": "analyze_stock", "defaultArgs": {"ticker": "AAPL", "portfolio_value": 100000}},
    {"name": "get_stock_summary", "defaultArgs": {"ticker": "MSFT"}},
    {"name": "get_stock_info", "defaultArgs": {"ticker": "NVDA"}},
    {"name": "explain_metric", "defaultArgs": {"metric_name": "RSI"}},
    {"name": "show_legend", "defaultArgs": {}}
]


def verify_tool_definitions() -> Dict[str, Any]:
    """Verify that frontend tools match backend tool definitions."""
    print("=" * 80)
    print("Step 1: Verifying Tool Definitions")
    print("=" * 80)
    
    results = {
        "total_frontend_tools": len(FRONTEND_TOOLS),
        "backend_tools_available": BACKEND_AVAILABLE,
        "matched_tools": [],
        "missing_tools": [],
        "status": "unknown"
    }
    
    if not BACKEND_AVAILABLE:
        print("❌ Cannot verify tool definitions - backend module not available")
        print("   This is expected if running outside the project environment")
        results["status"] = "skipped"
        return results
    
    try:
        backend_tools = get_all_tools()
        backend_tool_names = {tool.name for tool in backend_tools}
        
        print(f"Frontend tools: {len(FRONTEND_TOOLS)}")
        print(f"Backend tools: {len(backend_tools)}")
        print()
        
        for frontend_tool in FRONTEND_TOOLS:
            tool_name = frontend_tool["name"]
            if tool_name in backend_tool_names:
                print(f"✅ {tool_name} - Found in backend")
                results["matched_tools"].append(tool_name)
            else:
                print(f"❌ {tool_name} - NOT found in backend")
                results["missing_tools"].append(tool_name)
        
        if len(results["missing_tools"]) == 0:
            print()
            print("✅ All frontend tools are available in the backend!")
            results["status"] = "passed"
        else:
            print()
            print(f"⚠️  {len(results['missing_tools'])} tool(s) missing from backend")
            results["status"] = "failed"
            
    except Exception as e:
        print(f"❌ Error verifying tools: {e}")
        results["status"] = "error"
        results["error"] = str(e)
    
    print()
    return results


def check_backend_connectivity() -> Dict[str, Any]:
    """Check if backend API is accessible."""
    print("=" * 80)
    print("Step 2: Checking Backend Connectivity")
    print("=" * 80)
    
    results = {
        "backend_url": "http://localhost:8005",
        "health_endpoint_accessible": False,
        "status": "unknown"
    }
    
    try:
        import requests
        response = requests.get(f"{results['backend_url']}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Backend is running at {results['backend_url']}")
            results["health_endpoint_accessible"] = True
            results["status"] = "connected"
        else:
            print(f"⚠️  Backend responded with status {response.status_code}")
            results["status"] = "error"
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to backend at {results['backend_url']}")
        print("   Backend may not be running. Start it with:")
        print("   - ./start_fresh.sh")
        print("   - python -m uvicorn tradingagents.api.main:app --host 0.0.0.0 --port 8005")
        results["status"] = "disconnected"
    except ImportError:
        print("⚠️  'requests' library not available - skipping connectivity check")
        results["status"] = "skipped"
    except Exception as e:
        print(f"❌ Error checking connectivity: {e}")
        results["status"] = "error"
        results["error"] = str(e)
    
    print()
    return results


def test_tools_via_api(api_key: str = None) -> Dict[str, Any]:
    """Test all tools via the API endpoint."""
    print("=" * 80)
    print("Step 3: Testing Tools via API")
    print("=" * 80)
    
    results = {
        "total_tools": len(FRONTEND_TOOLS),
        "tested": 0,
        "passed": 0,
        "failed": 0,
        "tool_results": {}
    }
    
    try:
        import requests
    except ImportError:
        print("⚠️  'requests' library not available - skipping API tests")
        results["status"] = "skipped"
        return results
    
    BASE_URL = "http://localhost:8005"
    
    # Check if backend is accessible first
    try:
        requests.get(f"{BASE_URL}/health", timeout=5)
    except:
        print("❌ Backend not accessible - skipping API tests")
        print("   Please start the backend first")
        results["status"] = "backend_unavailable"
        return results
    
    if api_key:
        print(f"Using API key: {api_key[:10]}...")
    else:
        # Try default key from documentation
        api_key = "Uo8m722b5pkY4s8ixSqm3SkIGXcVR55JkjUm4cNaUlg"
        print(f"Using default API key from documentation")
    print()
    
    for i, tool_config in enumerate(FRONTEND_TOOLS, 1):
        tool_name = tool_config["name"]
        args = tool_config["defaultArgs"]
        
        print(f"[{i}/{len(FRONTEND_TOOLS)}] Testing: {tool_name}")
        
        try:
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": api_key
            }
            
            response = requests.post(
                f"{BASE_URL}/debug/execute_tool",
                params={"tool_name": tool_name},
                json=args,
                headers=headers,
                timeout=60
            )
            
            results["tested"] += 1
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    result = data.get("result", "")
                    # Check if result indicates an error
                    if isinstance(result, str) and (
                        result.startswith("Error") or 
                        "connection error" in result.lower() or
                        "timeout" in result.lower()
                    ):
                        print(f"  ⚠️  Tool executed but returned error: {result[:100]}...")
                        results["failed"] += 1
                        results["tool_results"][tool_name] = {
                            "status": "error_in_result",
                            "message": result[:200]
                        }
                    else:
                        print(f"  ✅ Success")
                        results["passed"] += 1
                        results["tool_results"][tool_name] = {
                            "status": "passed",
                            "result_preview": str(result)[:200]
                        }
                else:
                    error = data.get("error", "Unknown error")
                    print(f"  ❌ Failed: {error[:100]}")
                    results["failed"] += 1
                    results["tool_results"][tool_name] = {
                        "status": "failed",
                        "error": error
                    }
            elif response.status_code == 401:
                print(f"  ❌ Unauthorized - API key may be invalid")
                results["failed"] += 1
                results["tool_results"][tool_name] = {
                    "status": "unauthorized",
                    "error": "401 Unauthorized"
                }
            elif response.status_code == 404:
                print(f"  ❌ Tool not found")
                results["failed"] += 1
                results["tool_results"][tool_name] = {
                    "status": "not_found",
                    "error": "404 Not Found"
                }
            else:
                print(f"  ❌ HTTP {response.status_code}: {response.text[:100]}")
                results["failed"] += 1
                results["tool_results"][tool_name] = {
                    "status": "http_error",
                    "error": f"HTTP {response.status_code}"
                }
                
        except requests.exceptions.Timeout:
            print(f"  ⏱️  Timeout - Tool took too long to execute")
            results["failed"] += 1
            results["tool_results"][tool_name] = {
                "status": "timeout",
                "error": "Request timeout"
            }
        except Exception as e:
            print(f"  ❌ Exception: {str(e)[:100]}")
            results["failed"] += 1
            results["tool_results"][tool_name] = {
                "status": "exception",
                "error": str(e)
            }
        
        print()
    
    # Summary
    print("-" * 80)
    print(f"Tested: {results['tested']}/{results['total_tools']}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    if results['tested'] > 0:
        success_rate = (results['passed'] / results['tested'] * 100)
        print(f"Success rate: {success_rate:.1f}%")
    print()
    
    return results


def generate_report(definition_results: Dict, connectivity_results: Dict, api_results: Dict) -> str:
    """Generate a comprehensive verification report."""
    report = []
    report.append("=" * 80)
    report.append("Tool Tester Verification Report")
    report.append("=" * 80)
    report.append("")
    
    # Tool Definitions
    report.append("## Tool Definitions Verification")
    report.append(f"- Frontend tools: {definition_results['total_frontend_tools']}")
    if definition_results['status'] == 'passed':
        report.append(f"- ✅ All tools match backend definitions")
    elif definition_results['status'] == 'failed':
        report.append(f"- ❌ {len(definition_results['missing_tools'])} tool(s) missing")
    report.append("")
    
    # Connectivity
    report.append("## Backend Connectivity")
    if connectivity_results['status'] == 'connected':
        report.append(f"- ✅ Backend is accessible at {connectivity_results['backend_url']}")
    elif connectivity_results['status'] == 'disconnected':
        report.append(f"- ❌ Backend is not accessible")
        report.append(f"  Start backend with: ./start_fresh.sh")
    report.append("")
    
    # API Tests
    if api_results.get('tested', 0) > 0:
        report.append("## API Tool Execution Tests")
        report.append(f"- Total tools tested: {api_results['tested']}")
        report.append(f"- ✅ Passed: {api_results['passed']}")
        report.append(f"- ❌ Failed: {api_results['failed']}")
        if api_results['tested'] > 0:
            success_rate = (api_results['passed'] / api_results['tested'] * 100)
            report.append(f"- Success rate: {success_rate:.1f}%")
        report.append("")
        
        # Individual tool results
        report.append("### Individual Tool Results")
        for tool_name, tool_result in api_results.get('tool_results', {}).items():
            status = tool_result.get('status', 'unknown')
            if status == 'passed':
                report.append(f"- ✅ {tool_name}: Working")
            else:
                error = tool_result.get('error', tool_result.get('message', 'Unknown error'))
                report.append(f"- ❌ {tool_name}: {status} - {error[:100]}")
        report.append("")
    
    # Overall Status
    report.append("## Overall Status")
    all_passed = (
        definition_results.get('status') == 'passed' and
        connectivity_results.get('status') == 'connected' and
        api_results.get('passed', 0) == api_results.get('total_tools', 0)
    )
    
    if all_passed:
        report.append("✅ All Tool Tester components are functioning correctly!")
    else:
        report.append("⚠️  Some issues detected. See details above.")
    
    report.append("")
    report.append("=" * 80)
    
    return "\n".join(report)


def main():
    """Main entry point."""
    print("\n")
    print("Tool Tester Comprehensive Verification")
    print("=" * 80)
    print()
    
    # Step 1: Verify tool definitions
    definition_results = verify_tool_definitions()
    
    # Step 2: Check connectivity
    connectivity_results = check_backend_connectivity()
    
    # Step 3: Test tools via API (only if backend is accessible)
    api_results = {"tested": 0, "passed": 0, "failed": 0, "total_tools": len(FRONTEND_TOOLS)}
    if connectivity_results.get('status') == 'connected':
        # Try to get API key
        api_key = os.environ.get("API_KEY")
        if not api_key:
            api_key = "Uo8m722b5pkY4s8ixSqm3SkIGXcVR55JkjUm4cNaUlg"  # Default from docs
        
        api_results = test_tools_via_api(api_key)
    else:
        print("Skipping API tests - backend not accessible")
        print()
    
    # Generate and print report
    report = generate_report(definition_results, connectivity_results, api_results)
    print(report)
    
    # Save report to file
    report_file = "tool_tester_verification_report.txt"
    with open(report_file, "w") as f:
        f.write(report)
    print(f"\nReport saved to: {report_file}")
    
    # Exit code
    if (
        definition_results.get('status') == 'passed' and
        connectivity_results.get('status') == 'connected' and
        api_results.get('passed', 0) == api_results.get('total_tools', 0)
    ):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

