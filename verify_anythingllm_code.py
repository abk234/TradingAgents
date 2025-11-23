#!/usr/bin/env python3
"""
Static code verification for AnythingLLM integration features.
Checks that all code is properly structured without requiring server to run.
"""

import ast
import sys
from pathlib import Path

def check_file_exists(filepath):
    """Check if a file exists"""
    path = Path(filepath)
    exists = path.exists()
    print(f"{'✅' if exists else '❌'} {filepath}")
    return exists

def check_imports(filepath, required_imports):
    """Check if file has required imports"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            tree = ast.parse(content)
        
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        missing = []
        for imp in required_imports:
            if not any(imp in i or i.endswith(imp.split('.')[-1]) for i in imports):
                missing.append(imp)
        
        if missing:
            print(f"  ⚠️  Missing imports: {missing}")
            return False
        return True
    except Exception as e:
        print(f"  ❌ Error checking imports: {e}")
        return False

def check_endpoint_exists(filepath, endpoint_path):
    """Check if endpoint exists in API file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Look for endpoint definition
        if f'"{endpoint_path}"' in content or f"'{endpoint_path}'" in content:
            return True
        return False
    except Exception as e:
        print(f"  ❌ Error checking endpoint: {e}")
        return False

def main():
    """Run all verification checks"""
    print("\n" + "="*70)
    print("ANYTHINGLLM INTEGRATION - CODE VERIFICATION")
    print("="*70)
    
    all_checks_passed = True
    
    # 1. Check MCP Integration Files
    print("\n" + "="*70)
    print("1. MCP INTEGRATION FILES")
    print("="*70)
    
    mcp_files = [
        "tradingagents/mcp/__init__.py",
        "tradingagents/mcp/server.py",
        "tradingagents/mcp/adapter.py",
    ]
    
    for filepath in mcp_files:
        if not check_file_exists(filepath):
            all_checks_passed = False
    
    # Check MCP endpoints in API
    print("\nChecking MCP endpoints in API:")
    mcp_endpoints = [
        "/mcp/initialize",
        "/mcp/capabilities",
        "/mcp/tools",
        "/mcp/resources",
        "/mcp/tools/{tool_name}",
        "/mcp/resources/{uri:path}",
        "/mcp/tools/register",
    ]
    
    for endpoint in mcp_endpoints:
        # Clean endpoint for search
        search_endpoint = endpoint.replace("{tool_name}", "").replace("{uri:path}", "")
        exists = check_endpoint_exists("tradingagents/api/main.py", search_endpoint)
        print(f"{'✅' if exists else '❌'} Endpoint: {endpoint}")
        if not exists:
            all_checks_passed = False
    
    # 2. Check Document Processing Files
    print("\n" + "="*70)
    print("2. DOCUMENT PROCESSING FILES")
    print("="*70)
    
    doc_files = [
        "tradingagents/documents/__init__.py",
        "tradingagents/documents/parser.py",
        "tradingagents/documents/extractor.py",
        "tradingagents/documents/processor.py",
        "tradingagents/database/document_ops.py",
        "database/migrations/002_add_documents_table.sql",
    ]
    
    for filepath in doc_files:
        if not check_file_exists(filepath):
            all_checks_passed = False
    
    # Check document endpoints
    print("\nChecking document endpoints in API:")
    doc_endpoints = [
        "/documents/upload",
        "/documents",
        "/documents/{document_id}",
        "/documents/{document_id}/insights",
    ]
    
    for endpoint in doc_endpoints:
        search_endpoint = endpoint.replace("{document_id}", "")
        exists = check_endpoint_exists("tradingagents/api/main.py", search_endpoint)
        print(f"{'✅' if exists else '❌'} Endpoint: {endpoint}")
        if not exists:
            all_checks_passed = False
    
    # 3. Check Workspace Management Files
    print("\n" + "="*70)
    print("3. WORKSPACE MANAGEMENT FILES")
    print("="*70)
    
    workspace_files = [
        "tradingagents/database/workspace_ops.py",
        "database/migrations/003_add_workspaces_table.sql",
    ]
    
    for filepath in workspace_files:
        if not check_file_exists(filepath):
            all_checks_passed = False
    
    # Check workspace endpoints
    print("\nChecking workspace endpoints in API:")
    workspace_endpoints = [
        "/workspaces",
        "/workspaces/default",
        "/workspaces/{workspace_id}",
        "/workspaces/{workspace_id}/tickers",
        "/workspaces/{workspace_id}/analyses",
    ]
    
    for endpoint in workspace_endpoints:
        search_endpoint = endpoint.replace("{workspace_id}", "").replace("/default", "")
        exists = check_endpoint_exists("tradingagents/api/main.py", search_endpoint)
        print(f"{'✅' if exists else '❌'} Endpoint: {endpoint}")
        if not exists:
            all_checks_passed = False
    
    # 4. Check API Integration
    print("\n" + "="*70)
    print("4. API INTEGRATION")
    print("="*70)
    
    print("\nChecking API main.py for feature initialization:")
    
    with open("tradingagents/api/main.py", 'r') as f:
        api_content = f.read()
    
    checks = [
        ("MCP server import", "from tradingagents.mcp import MCPServer"),
        ("MCP server initialization", "mcp_server = MCPServer()"),
        ("Document processor import", "from tradingagents.documents import DocumentProcessor"),
        ("Document processor initialization", "document_processor = DocumentProcessor()"),
        ("Workspace ops import", "from tradingagents.database.workspace_ops import WorkspaceOperations"),
        ("Workspace ops initialization", "workspace_ops = WorkspaceOperations()"),
    ]
    
    for check_name, check_string in checks:
        exists = check_string in api_content
        print(f"{'✅' if exists else '❌'} {check_name}")
        if not exists:
            all_checks_passed = False
    
    # 5. Check Documentation
    print("\n" + "="*70)
    print("5. DOCUMENTATION")
    print("="*70)
    
    doc_files = [
        "docs/ANYTHINGLLM_ANALYSIS.md",
        "docs/ANYTHINGLLM_IMPLEMENTATION_SUMMARY.md",
        "docs/ANYTHINGLLM_SETUP_GUIDE.md",
        "docs/ANYTHINGLLM_FEATURES_READY.md",
        "docs/MCP_INTEGRATION.md",
    ]
    
    for filepath in doc_files:
        check_file_exists(filepath)
    
    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    if all_checks_passed:
        print("\n✅ All code checks passed!")
        print("\nThe AnythingLLM integration code is properly structured.")
        print("\nTo test with a running server:")
        print("  1. Start the API server: python -m tradingagents.api.main")
        print("  2. Run: python test_anythingllm_integration.py")
        return 0
    else:
        print("\n⚠️  Some checks failed. Review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

