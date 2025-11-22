# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

import requests
import json
import time
import sys
from datetime import datetime

API_URL = "http://localhost:8006"

def test_chat_and_feedback():
    print("1. Testing Chat Endpoint...")
    chat_payload = {
        "message": "What is the price of AAPL?",
        "conversation_history": [],
        "conversation_id": f"test_session_{int(time.time())}"
    }
    
    try:
        response = requests.post(f"{API_URL}/chat", json=chat_payload)
        response.raise_for_status()
        data = response.json()
        print(f"✓ Chat response received: {data['response'][:50]}...")
        
        interaction_id = data.get("metadata", {}).get("interaction_id")
        if not interaction_id:
            print("⚠ No interaction_id returned in metadata (Feedback storage might fail)")
        else:
            print(f"✓ Interaction ID received: {interaction_id}")
            
        # Test Feedback
        print("\n2. Testing Feedback Endpoint...")
        if interaction_id:
            feedback_payload = {
                "conversation_id": chat_payload["conversation_id"],
                "message_id": str(interaction_id),
                "rating": 5,
                "comment": "Great response!",
                "correction": None
            }
            
            fb_response = requests.post(f"{API_URL}/feedback", json=feedback_payload)
            fb_response.raise_for_status()
            print(f"✓ Feedback response: {fb_response.json()}")
        else:
            print("⚠ Skipping feedback test due to missing interaction_id")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to API at {API_URL}. Is it running?")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_chat_and_feedback()
