#!/usr/bin/env python3
"""
Test script to verify API Key authentication implementation.
"""
import requests
import os
import sys

API_BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8005")
API_KEY = "Uo8m722b5pkY4s8ixSqm3SkIGXcVR55JkjUm4cNaUlg"

def test_health_endpoint():
    """Health endpoint should be accessible without auth."""
    print("Testing /health endpoint (no auth required)...")
    response = requests.get(f"{API_BASE_URL}/health")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print("✓ /health endpoint accessible without auth")

def test_chat_without_key():
    """Chat endpoint should reject requests without API key."""
    print("\nTesting /chat endpoint without API key...")
    response = requests.post(
        f"{API_BASE_URL}/chat",
        json={
            "message": "Hello",
            "conversation_history": [],
            "conversation_id": "test"
        }
    )
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    print("✓ /chat endpoint correctly rejects requests without API key")

def test_chat_with_invalid_key():
    """Chat endpoint should reject requests with invalid API key."""
    print("\nTesting /chat endpoint with invalid API key...")
    response = requests.post(
        f"{API_BASE_URL}/chat",
        headers={"X-API-Key": "invalid-key"},
        json={
            "message": "Hello",
            "conversation_history": [],
            "conversation_id": "test"
        }
    )
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    print("✓ /chat endpoint correctly rejects requests with invalid API key")

def test_chat_with_valid_key():
    """Chat endpoint should accept requests with valid API key."""
    print("\nTesting /chat endpoint with valid API key...")
    response = requests.post(
        f"{API_BASE_URL}/chat",
        headers={"X-API-Key": API_KEY},
        json={
            "message": "Hello",
            "conversation_history": [],
            "conversation_id": "test"
        }
    )
    # Should get 200 or 503 (if agent not initialized), but not 401
    assert response.status_code in [200, 503], f"Expected 200 or 503, got {response.status_code}"
    print(f"✓ /chat endpoint accepts valid API key (status: {response.status_code})")

def test_state_endpoint():
    """State endpoint should require authentication."""
    print("\nTesting /state endpoint without API key...")
    response = requests.get(f"{API_BASE_URL}/state")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    print("✓ /state endpoint requires authentication")
    
    print("\nTesting /state endpoint with valid API key...")
    response = requests.get(
        f"{API_BASE_URL}/state",
        headers={"X-API-Key": API_KEY}
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print("✓ /state endpoint accepts valid API key")

def main():
    print("=" * 60)
    print("API Key Authentication Verification Tests")
    print("=" * 60)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"API Key: {API_KEY[:20]}...")
    print("=" * 60)
    
    try:
        test_health_endpoint()
        test_chat_without_key()
        test_chat_with_invalid_key()
        test_chat_with_valid_key()
        test_state_endpoint()
        
        print("\n" + "=" * 60)
        print("✓ All authentication tests passed!")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except requests.exceptions.ConnectionError:
        print(f"\n✗ Could not connect to {API_BASE_URL}")
        print("Make sure the backend server is running.")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
