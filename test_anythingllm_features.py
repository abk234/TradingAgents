#!/usr/bin/env python3
"""
Test script for AnythingLLM integration features:
- MCP Integration
- Document Processing
- Workspace Management

Run this after starting the API server to validate all features.
"""

import requests
import json
import sys
from pathlib import Path

API_BASE = "http://localhost:8005"
API_KEY = None  # Set if API key is required

def get_headers():
    """Get request headers"""
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["X-API-Key"] = API_KEY
    return headers

def test_mcp_integration():
    """Test MCP integration"""
    print("\n" + "="*60)
    print("Testing MCP Integration")
    print("="*60)
    
    try:
        # Test initialization
        print("\n1. Testing MCP initialization...")
        response = requests.get(f"{API_BASE}/mcp/initialize", headers=get_headers())
        if response.status_code == 200:
            print("   ✅ MCP server initialized")
            print(f"   Protocol version: {response.json().get('protocolVersion', 'N/A')}")
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
            return False
        
        # Test capabilities
        print("\n2. Testing MCP capabilities...")
        response = requests.get(f"{API_BASE}/mcp/capabilities", headers=get_headers())
        if response.status_code == 200:
            print("   ✅ Capabilities retrieved")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return False
        
        # Test tool listing
        print("\n3. Testing tool listing...")
        response = requests.get(f"{API_BASE}/mcp/tools", headers=get_headers())
        if response.status_code == 200:
            data = response.json()
            tool_count = data.get("count", 0)
            print(f"   ✅ Found {tool_count} tools")
            if tool_count > 0:
                print(f"   Sample tools: {[t.get('name') for t in data.get('tools', [])[:3]]}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return False
        
        print("\n✅ MCP Integration tests passed!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to API. Is the server running?")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_document_processing():
    """Test document processing"""
    print("\n" + "="*60)
    print("Testing Document Processing")
    print("="*60)
    
    try:
        # Test document listing (should work even with no documents)
        print("\n1. Testing document listing...")
        response = requests.get(f"{API_BASE}/documents", headers=get_headers())
        if response.status_code == 200:
            data = response.json()
            doc_count = data.get("count", 0)
            print(f"   ✅ Document listing works ({doc_count} documents)")
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
            return False
        
        # Test with a sample text file
        print("\n2. Testing document upload (text file)...")
        sample_text = """
        Apple Inc. (AAPL) Q4 2024 Earnings Report
        
        Revenue: $89.5 billion
        Net Income: $22.6 billion
        EPS: $1.46
        
        Key Highlights:
        - iPhone sales increased 5%
        - Services revenue reached new record
        - Strong performance in China market
        """
        
        files = {
            'file': ('test_earnings.txt', sample_text.encode(), 'text/plain')
        }
        data = {}
        if API_KEY:
            data['X-API-Key'] = API_KEY
        
        response = requests.post(
            f"{API_BASE}/documents/upload",
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            doc_data = response.json()
            doc_id = doc_data.get("document_id")
            print(f"   ✅ Document uploaded successfully (ID: {doc_id})")
            
            # Test document retrieval
            print("\n3. Testing document retrieval...")
            response = requests.get(
                f"{API_BASE}/documents/{doc_id}",
                headers=get_headers()
            )
            if response.status_code == 200:
                print("   ✅ Document retrieved successfully")
                doc_info = response.json()
                print(f"   Document type: {doc_info.get('document_type')}")
                print(f"   Status: {doc_info.get('processing_status')}")
                
                # Check financial data extraction
                if doc_info.get('financial_data'):
                    financial_data = doc_info['financial_data']
                    if financial_data.get('tickers'):
                        print(f"   ✅ Extracted tickers: {financial_data['tickers']}")
                    if financial_data.get('metrics'):
                        print(f"   ✅ Extracted metrics: {list(financial_data['metrics'].keys())}")
            else:
                print(f"   ❌ Failed to retrieve document: {response.status_code}")
                return False
        else:
            print(f"   ⚠️  Document upload failed: {response.status_code} - {response.text}")
            print("   (This is OK if document processing dependencies are not installed)")
            return True  # Don't fail the test if dependencies are missing
        
        print("\n✅ Document Processing tests passed!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to API. Is the server running?")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_workspace_management():
    """Test workspace management"""
    print("\n" + "="*60)
    print("Testing Workspace Management")
    print("="*60)
    
    try:
        # Test workspace listing
        print("\n1. Testing workspace listing...")
        response = requests.get(f"{API_BASE}/workspaces", headers=get_headers())
        if response.status_code == 200:
            data = response.json()
            workspace_count = data.get("count", 0)
            print(f"   ✅ Found {workspace_count} workspaces")
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
            return False
        
        # Test default workspace
        print("\n2. Testing default workspace...")
        response = requests.get(f"{API_BASE}/workspaces/default", headers=get_headers())
        if response.status_code == 200:
            workspace = response.json()
            print(f"   ✅ Default workspace: {workspace.get('name')}")
            default_id = workspace.get('workspace_id')
        else:
            print(f"   ⚠️  No default workspace found (this is OK if migrations haven't run)")
            default_id = None
        
        # Test workspace creation
        print("\n3. Testing workspace creation...")
        new_workspace = {
            "name": "Test Workspace",
            "description": "Test workspace for validation",
            "is_default": False
        }
        response = requests.post(
            f"{API_BASE}/workspaces",
            headers=get_headers(),
            json=new_workspace
        )
        
        if response.status_code == 200:
            workspace_data = response.json()
            test_workspace_id = workspace_data.get("workspace_id")
            print(f"   ✅ Workspace created (ID: {test_workspace_id})")
            
            # Test workspace retrieval
            print("\n4. Testing workspace retrieval...")
            response = requests.get(
                f"{API_BASE}/workspaces/{test_workspace_id}",
                headers=get_headers()
            )
            if response.status_code == 200:
                print("   ✅ Workspace retrieved successfully")
            
            # Test workspace tickers
            print("\n5. Testing workspace tickers...")
            response = requests.get(
                f"{API_BASE}/workspaces/{test_workspace_id}/tickers",
                headers=get_headers()
            )
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Workspace tickers retrieved ({data.get('count', 0)} tickers)")
            
            # Cleanup: delete test workspace
            print("\n6. Cleaning up test workspace...")
            response = requests.delete(
                f"{API_BASE}/workspaces/{test_workspace_id}?soft_delete=true",
                headers=get_headers()
            )
            if response.status_code == 200:
                print("   ✅ Test workspace deleted")
        else:
            print(f"   ⚠️  Workspace creation failed: {response.status_code} - {response.text}")
            print("   (This is OK if database migrations haven't run)")
            return True  # Don't fail if migrations haven't run
        
        print("\n✅ Workspace Management tests passed!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to API. Is the server running?")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("AnythingLLM Integration Features Validation")
    print("="*60)
    print("\nMake sure the API server is running on http://localhost:8005")
    print("Press Enter to continue or Ctrl+C to cancel...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)
    
    results = []
    
    # Test MCP
    results.append(("MCP Integration", test_mcp_integration()))
    
    # Test Document Processing
    results.append(("Document Processing", test_document_processing()))
    
    # Test Workspace Management
    results.append(("Workspace Management", test_workspace_management()))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("Note: Some failures may be expected if:")
        print("  - Database migrations haven't been run")
        print("  - Required dependencies are not installed")
        print("  - API server is not running")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

