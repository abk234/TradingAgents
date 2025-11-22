#!/usr/bin/env python3
# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Test script for the show_data_dashboard() tool.
Verifies that the dashboard generates correctly with real database data.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tradingagents.bot.tools import show_data_dashboard

def test_dashboard():
    """Test the data dashboard tool."""
    print("=" * 80)
    print("Testing show_data_dashboard() Tool")
    print("=" * 80)
    print()

    try:
        # Invoke the dashboard tool
        result = show_data_dashboard.invoke({})

        print(result)
        print()
        print("=" * 80)
        print("✅ Dashboard test PASSED!")
        print("=" * 80)

        return True

    except Exception as e:
        print()
        print("=" * 80)
        print(f"❌ Dashboard test FAILED: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_dashboard()
    sys.exit(0 if success else 1)
