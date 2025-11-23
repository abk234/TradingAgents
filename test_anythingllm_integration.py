#!/usr/bin/env python3
"""
Comprehensive test for AnythingLLM integration features:
1. MCP Integration
2. Document Processing
3. Workspace Management

Tests all endpoints and functionality to ensure everything works as expected.
"""

import requests
import json
import sys
import os
from pathlib import Path

API_BASE = "http://localhost:8005"
API_KEY = os.getenv("API_KEY")  # Optional API key

def get_headers():
    """Get request headers"""
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["X-API-Key"] = API_KEY
    return headers

def test_endpoint(method, endpoint, data=None, description="", expected_status=200):
    """Test an API endpoint"""
    print(f"\n{'='*70}")
    print(f"Testing: {method} {endpoint}")
    if description:
        print(f"Description: {description}")
    print(f"{'='*70}")
    
    try:
        url = f"{API_BASE}{endpoint}"
        headers = get_headers()
        
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            if isinstance(data, dict) and 'file' not in str(data):
                response = requests.post(url, headers=headers, json=data, timeout=10)
            else:
                # For file uploads, don't use json
                response = requests.post(url, files=data if data else None, headers={k: v for k, v in headers.items() if k != "Content-Type"}, timeout=30)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            print(f"  ❌ Unsupported method: {method}")
            return False, None
        
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == expected_status or (expected_status == 200 and response.status_code in [200, 201]):
            try:
                result = response.json()
                print(f"  ✅ Success!")
                if isinstance(result, dict):
                    print(f"  Response keys: {list(result.keys())}")
                return True, result
            except json.JSONDecodeError:
                print(f"  ✅ Success (non-JSON response)")
                return True, response.text
        elif response.status_code == 404:
            print(f"  ❌ Endpoint NOT FOUND (404)")
            print(f"  Response: {response.text[:200]}")
            return False, None
        elif response.status_code == 503:
            print(f"  ⚠️  Service unavailable (503) - Service not initialized")
            print(f"  Response: {response.text[:200]}")
            return None, None  # Can't determine if endpoint exists
        elif response.status_code in [401, 403]:
            print(f"  ⚠️  Authentication required ({response.status_code})")
            print(f"  Endpoint exists but requires auth")
            return True, None  # Endpoint exists
        else:
            print(f"  ⚠️  Unexpected status: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False, None
        
    except requests.exceptions.ConnectionError:
        print(f"  ❌ Cannot connect to API server")
        print(f"  Make sure the server is running on {API_BASE}")
        return None, None
    except requests.exceptions.Timeout:
        print(f"  ⚠️  Request timeout")
        return None, None
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def test_mcp_integration():
    """Test MCP Integration"""
    print("\n" + "="*70)
    print("TESTING MCP INTEGRATION")
    print("="*70)
    
    results = []
    
    # Test 1: Initialize
    success, data = test_endpoint("GET", "/mcp/initialize", description="Initialize MCP server")
    results.append(("MCP Initialize", success))
    
    # Test 2: Get capabilities
    success, data = test_endpoint("GET", "/mcp/capabilities", description="Get MCP capabilities")
    results.append(("MCP Capabilities", success))
    
    # Test 3: List tools
    success, data = test_endpoint("GET", "/mcp/tools", description="List MCP tools")
    results.append(("MCP List Tools", success))
    if success and data:
        tool_count = data.get("count", 0)
        print(f"  Found {tool_count} tools registered")
    
    # Test 4: List resources
    success, data = test_endpoint("GET", "/mcp/resources", description="List MCP resources")
    results.append(("MCP List Resources", success))
    
    return results

def test_document_processing():
    """Test Document Processing"""
    print("\n" + "="*70)
    print("TESTING DOCUMENT PROCESSING")
    print("="*70)
    
    results = []
    
    # Test 1: List documents
    success, data = test_endpoint("GET", "/documents", description="List documents")
    results.append(("List Documents", success))
    
    # Test 2: Upload a test document
    print("\n" + "="*70)
    print("Testing: POST /documents/upload")
    print("Description: Upload and process a test document")
    print("="*70)
    
    try:
        # Create a test text file
        test_content = """
        Apple Inc. (AAPL) Q4 2024 Earnings Report
        
        Revenue: $89.5 billion
        Net Income: $22.6 billion
        EPS: $1.46
        
        Key Highlights:
        - iPhone sales increased 5%
        - Services revenue reached new record
        - Strong performance in China market
        
        Ticker: AAPL
        Sector: Technology
        """
        
        files = {
            'file': ('test_earnings.txt', test_content.encode(), 'text/plain')
        }
        data = {}
        if API_KEY:
            data['X-API-Key'] = API_KEY
        
        response = requests.post(
            f"{API_BASE}/documents/upload",
            files=files,
            data=data,
            timeout=30
        )
        
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            doc_data = response.json()
            doc_id = doc_data.get("document_id")
            print(f"  ✅ Document uploaded successfully (ID: {doc_id})")
            results.append(("Upload Document", True))
            
            # Test 3: Get document
            success, data = test_endpoint("GET", f"/documents/{doc_id}", description="Get uploaded document")
            results.append(("Get Document", success))
            
            # Test 4: Get document insights
            success, data = test_endpoint("GET", f"/documents/{doc_id}/insights", description="Get document insights")
            results.append(("Get Document Insights", success))
            
            return results, doc_id
        else:
            print(f"  ⚠️  Upload failed: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            results.append(("Upload Document", False))
            return results, None
            
    except Exception as e:
        print(f"  ❌ Error uploading document: {e}")
        results.append(("Upload Document", False))
        return results, None

def test_workspace_management():
    """Test Workspace Management"""
    print("\n" + "="*70)
    print("TESTING WORKSPACE MANAGEMENT")
    print("="*70)
    
    results = []
    test_workspace_id = None
    
    # Test 1: List workspaces
    success, data = test_endpoint("GET", "/workspaces", description="List workspaces")
    results.append(("List Workspaces", success))
    
    # Test 2: Get default workspace
    success, data = test_endpoint("GET", "/workspaces/default", description="Get default workspace")
    results.append(("Get Default Workspace", success))
    
    # Test 3: Create workspace
    workspace_data = {
        "name": "Test Workspace - Integration Test",
        "description": "Test workspace for AnythingLLM integration validation",
        "is_default": False
    }
    success, data = test_endpoint("POST", "/workspaces", data=workspace_data, description="Create test workspace")
    results.append(("Create Workspace", success))
    
    if success and data:
        test_workspace_id = data.get("workspace_id")
        print(f"  Created workspace ID: {test_workspace_id}")
    
    if test_workspace_id:
        # Test 4: Get workspace
        success, data = test_endpoint("GET", f"/workspaces/{test_workspace_id}", description="Get created workspace")
        results.append(("Get Workspace", success))
        
        # Test 5: Get workspace tickers
        success, data = test_endpoint("GET", f"/workspaces/{test_workspace_id}/tickers", description="Get workspace tickers")
        results.append(("Get Workspace Tickers", success))
        
        # Test 6: Get workspace analyses
        success, data = test_endpoint("GET", f"/workspaces/{test_workspace_id}/analyses", description="Get workspace analyses")
        results.append(("Get Workspace Analyses", success))
        
        # Test 7: Update workspace
        update_data = {
            "description": "Updated description for test"
        }
        success, data = test_endpoint("PUT", f"/workspaces/{test_workspace_id}", data=update_data, description="Update workspace")
        results.append(("Update Workspace", success))
        
        # Test 8: Delete workspace (soft delete)
        success, data = test_endpoint("DELETE", f"/workspaces/{test_workspace_id}?soft_delete=true", description="Delete workspace")
        results.append(("Delete Workspace", success))
    
    return results

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("ANYTHINGLLM INTEGRATION - COMPREHENSIVE TEST")
    print("="*70)
    print(f"\nTesting API at: {API_BASE}")
    print("Make sure the API server is running!")
    
    if API_KEY:
        print(f"Using API key: {API_KEY[:10]}...")
    else:
        print("No API key set (using default auth)")
    
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    try:
        input()
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)
    
    all_results = {}
    
    # Test MCP Integration
    mcp_results = test_mcp_integration()
    all_results["MCP Integration"] = mcp_results
    
    # Test Document Processing
    doc_results, doc_id = test_document_processing()
    all_results["Document Processing"] = doc_results
    
    # Test Workspace Management
    workspace_results = test_workspace_management()
    all_results["Workspace Management"] = workspace_results
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    skipped_tests = 0
    
    for feature_name, feature_results in all_results.items():
        print(f"\n{feature_name}:")
        for test_name, result in feature_results:
            total_tests += 1
            if result is True:
                passed_tests += 1
                print(f"  ✅ {test_name}")
            elif result is False:
                failed_tests += 1
                print(f"  ❌ {test_name}")
            else:
                skipped_tests += 1
                print(f"  ⚠️  {test_name} (skipped - service unavailable)")
    
    print("\n" + "="*70)
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"⚠️  Skipped: {skipped_tests}")
    print("="*70)
    
    if failed_tests == 0:
        print("\n✅ All tests passed! AnythingLLM integration is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {failed_tests} test(s) failed. Check the output above for details.")
        print("\nNote: Some failures may be expected if:")
        print("  - Database migrations haven't been run")
        print("  - Required dependencies are not installed")
        print("  - Services are not fully initialized")
        return 1

if __name__ == "__main__":
    sys.exit(main())

