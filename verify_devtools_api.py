# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

import requests
import json
import sys

BASE_URL = "http://localhost:8005"

def test_devtools_api():
    print("Starting DevTools Verification...")
    
    # 1. Test Execute Tool
    print("\n--- Testing Execute Tool (get_stock_summary) ---")
    try:
        payload = {
            "tool_name": "get_stock_summary",
            "args": {"ticker": "AAPL"}
        }
        response = requests.post(f"{BASE_URL}/debug/execute_tool", params={"tool_name": "get_stock_summary"}, json={"ticker": "AAPL"})
        
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                print("✅ Tool execution successful")
                print(f"Result preview: {data['result'][:100]}...")
            else:
                print(f"❌ Tool execution failed: {data.get('error')}")
        else:
            print(f"❌ Failed to execute tool: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Exception: {e}")

    # 2. Test RAG Search
    print("\n--- Testing RAG Search ---")
    try:
        response = requests.post(f"{BASE_URL}/debug/rag_search", params={"query": "test query"})
        
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                print("✅ RAG search successful")
                print(f"Results: {len(data['results'])}")
            else:
                print(f"❌ RAG search failed")
        else:
            print(f"❌ Failed to search RAG: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")

    # 3. Test Analyze Sector (Fix Verification)
    print("\n--- Testing Analyze Sector (Fix Verification) ---")
    try:
        response = requests.post(f"{BASE_URL}/debug/execute_tool", params={"tool_name": "analyze_sector"}, json={"sector_name": "Technology"})
        
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                print("✅ Analyze Sector execution successful")
                print(f"Result preview: {data['result'][:100]}...")
            else:
                print(f"❌ Analyze Sector execution failed: {data.get('error')}")
        else:
            print(f"❌ Failed to execute Analyze Sector: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")

    # 4. Test Analyze Stock (Fix Verification)
    print("\n--- Testing Analyze Stock (Fix Verification) ---")
    try:
        # Use a mock ticker or a real one if available, but keep it simple
        response = requests.post(f"{BASE_URL}/debug/execute_tool", params={"tool_name": "analyze_stock"}, json={"ticker": "AAPL", "portfolio_value": 100000})
        
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                print("✅ Analyze Stock execution successful")
                print(f"Result preview: {data['result'][:100]}...")
            else:
                print(f"❌ Analyze Stock execution failed: {data.get('error')}")
        else:
            print(f"❌ Failed to execute Analyze Stock: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")

    print("\nVerification Complete.")

if __name__ == "__main__":
    test_devtools_api()
