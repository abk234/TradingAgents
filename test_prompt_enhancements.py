#!/usr/bin/env python3
# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Test script for Quick Win Prompts enhancements.

Tests:
1. Database migration (columns exist)
2. Learning operations (prompt metadata storage)
3. Analytics endpoint (if API is running)
4. Component imports (frontend)
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_database_migration():
    """Test that database columns exist."""
    print("🔍 Testing database migration...")
    try:
        from tradingagents.database.learning_ops import LearningOperations
        
        learning_ops = LearningOperations()
        
        # Check if columns exist by trying to query them
        query = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'user_interactions' 
            AND column_name IN ('prompt_type', 'prompt_id')
        """
        result = learning_ops.db.execute_dict_query(query)
        
        columns_found = [row['column_name'] for row in result] if result else []
        
        if 'prompt_type' in columns_found and 'prompt_id' in columns_found:
            print("✅ Database columns exist: prompt_type, prompt_id")
            return True
        else:
            print(f"⚠️  Missing columns. Found: {columns_found}")
            print("   The app will auto-migrate on next startup.")
            return False
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

def test_learning_ops():
    """Test that learning_ops can store prompt metadata."""
    print("\n🔍 Testing learning operations...")
    try:
        from tradingagents.database.learning_ops import LearningOperations
        
        learning_ops = LearningOperations()
        
        # Test log_interaction with prompt metadata
        test_conv_id = "test_prompt_enhancements"
        interaction_id = learning_ops.log_interaction(
            conversation_id=test_conv_id,
            role="user",
            content="Test prompt message",
            prompt_type="quick_wins",
            prompt_id="top-3-stocks"
        )
        
        if interaction_id:
            print(f"✅ Successfully logged interaction with prompt metadata (ID: {interaction_id})")
            
            # Verify it was stored correctly
            query = """
                SELECT prompt_type, prompt_id 
                FROM user_interactions 
                WHERE interaction_id = %s
            """
            result = learning_ops.db.execute_dict_query(query, (interaction_id,))
            
            if result and result[0]['prompt_type'] == 'quick_wins':
                print("✅ Prompt metadata verified in database")
                return True
            else:
                print("⚠️  Prompt metadata not found in database")
                return False
        else:
            print("❌ Failed to log interaction")
            return False
            
    except Exception as e:
        print(f"❌ Error testing learning operations: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_analytics_method():
    """Test the analytics method."""
    print("\n🔍 Testing analytics method...")
    try:
        from tradingagents.database.learning_ops import LearningOperations
        
        learning_ops = LearningOperations()
        
        # Test get_prompt_analytics
        analytics = learning_ops.get_prompt_analytics(days=7)
        
        if isinstance(analytics, dict):
            required_keys = ['most_used_prompts', 'category_usage', 'period_days', 'total_prompt_interactions']
            if all(key in analytics for key in required_keys):
                print("✅ Analytics method works correctly")
                print(f"   Period: {analytics['period_days']} days")
                print(f"   Total interactions: {analytics['total_prompt_interactions']}")
                print(f"   Categories tracked: {len(analytics['category_usage'])}")
                print(f"   Prompts tracked: {len(analytics['most_used_prompts'])}")
                return True
            else:
                print(f"⚠️  Missing keys in analytics. Found: {list(analytics.keys())}")
                return False
        else:
            print("❌ Analytics method returned wrong type")
            return False
            
    except Exception as e:
        print(f"❌ Error testing analytics: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_models():
    """Test that API models include prompt fields."""
    print("\n🔍 Testing API models...")
    try:
        from tradingagents.api.models import ChatRequest
        
        # Check if ChatRequest has prompt fields
        request = ChatRequest(
            message="Test",
            prompt_type="quick_wins",
            prompt_id="test-prompt"
        )
        
        if hasattr(request, 'prompt_type') and hasattr(request, 'prompt_id'):
            if request.prompt_type == "quick_wins" and request.prompt_id == "test-prompt":
                print("✅ API models support prompt metadata")
                return True
            else:
                print("⚠️  Prompt fields not set correctly")
                return False
        else:
            print("❌ Prompt fields missing from ChatRequest")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API models: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_analytics_endpoint():
    """Test analytics endpoint (if API is running)."""
    print("\n🔍 Testing analytics endpoint...")
    try:
        import requests
        
        url = "http://127.0.0.1:8005/analytics/prompts?days=7"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Analytics endpoint is working")
            print(f"   Response keys: {list(data.keys())}")
            return True
        elif response.status_code == 503:
            print("⚠️  API is running but learning_ops not initialized")
            return False
        else:
            print(f"⚠️  API returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️  API is not running (this is OK if you haven't started it)")
        print("   Start API with: python -m tradingagents.api.main")
        return None  # Not a failure, just not running
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        return False

def test_frontend_imports():
    """Test that frontend components can be imported (TypeScript check)."""
    print("\n🔍 Testing frontend components...")
    try:
        # Check if TypeScript files exist
        frontend_path = project_root / "web-app"
        
        required_files = [
            "components/PromptCategories.tsx",
            "components/ChatInterface.tsx",
            "components/ui/button.tsx",
            "lib/prompts.config.ts"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = frontend_path / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"❌ Missing frontend files: {missing_files}")
            return False
        else:
            print("✅ All frontend component files exist")
            
            # Check if button.tsx has prompt variant
            button_file = frontend_path / "components/ui/button.tsx"
            if button_file.exists():
                content = button_file.read_text()
                if '"prompt"' in content and "categoryColor" in content:
                    print("✅ Button component has prompt variant")
                    return True
                else:
                    print("⚠️  Button component missing prompt variant")
                    return False
            return True
            
    except Exception as e:
        print(f"❌ Error checking frontend: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Quick Win Prompts Enhancements - Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test database migration
    results.append(("Database Migration", test_database_migration()))
    
    # Test learning operations
    results.append(("Learning Operations", test_learning_ops()))
    
    # Test analytics method
    results.append(("Analytics Method", test_analytics_method()))
    
    # Test API models
    results.append(("API Models", test_api_models()))
    
    # Test analytics endpoint (optional)
    endpoint_result = test_analytics_endpoint()
    if endpoint_result is not None:
        results.append(("Analytics Endpoint", endpoint_result))
    
    # Test frontend
    results.append(("Frontend Components", test_frontend_imports()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    skipped = sum(1 for _, result in results if result is None)
    
    for name, result in results:
        status = "✅ PASS" if result is True else "❌ FAIL" if result is False else "⚠️  SKIP"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

