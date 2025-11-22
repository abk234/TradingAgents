#!/usr/bin/env python3
"""
Comprehensive test script for all Quick Action prompts in Eddie UI.

This script tests all 15 predefined prompts across 4 categories:
- Quick Wins (3 prompts)
- Deep Analysis (4 prompts - require ticker)
- Risk Management (3 prompts - require ticker)
- Market Intelligence (4 prompts)

Usage:
    python test_all_quick_actions.py
"""

import os
import sys
import json
import time
import requests
from typing import Dict, List, Tuple
from datetime import datetime

# Configuration
API_BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8005")
API_KEY = os.getenv("API_KEY", "")

# Test tickers to use
TEST_TICKERS = ["AAPL", "NVDA", "TSLA", "MSFT", "GOOGL"]

# All prompts from prompts.config.ts
PROMPTS = {
    "quick_wins": [
        {
            "id": "top-3-stocks",
            "label": "Top 3 Stocks to Buy Today",
            "prompt": "Show me the top 3 stocks to buy TODAY with clear justification, entry points, and confidence scores.",
            "requiresTicker": False
        },
        {
            "id": "breakout-stocks",
            "label": "Stocks Breaking Out Now",
            "prompt": "What stocks are breaking out right now? Show me momentum plays with technical breakout patterns and news catalysts.",
            "requiresTicker": False
        },
        {
            "id": "undervalued-ready",
            "label": "Undervalued Stocks Ready to Move",
            "prompt": "Find me undervalued stocks that are ready to move. Look for value plays with positive catalysts and reversal signals.",
            "requiresTicker": False
        }
    ],
    "analysis": [
        {
            "id": "analyze-ticker",
            "label": "Should I Buy This Stock?",
            "prompt": "Analyze {TICKER} - should I buy it? Provide a comprehensive multi-agent analysis with buy/hold/sell recommendation.",
            "requiresTicker": True
        },
        {
            "id": "bull-bear-case",
            "label": "Bullish vs Bearish Cases",
            "prompt": "What are the bullish and bearish cases for {TICKER}? Show me both sides with detailed reasoning and a confidence score.",
            "requiresTicker": True
        },
        {
            "id": "technical-setup",
            "label": "Technical Setup Analysis",
            "prompt": "Show me the technical setup for {TICKER}. Include chart patterns, key support/resistance levels, indicators, entry point, stop loss, and price targets.",
            "requiresTicker": True
        },
        {
            "id": "fundamental-deep-dive",
            "label": "Fundamental Deep Dive",
            "prompt": "Give me a fundamental analysis of {TICKER}. Cover financials, valuation metrics, growth prospects, and competitive position.",
            "requiresTicker": True
        }
    ],
    "risk": [
        {
            "id": "risk-assessment",
            "label": "What's the Risk?",
            "prompt": "What's the risk on {TICKER}? Provide a risk score, potential downside scenarios, and recommended position sizing.",
            "requiresTicker": True
        },
        {
            "id": "exit-signal",
            "label": "Should I Exit?",
            "prompt": "Should I exit {TICKER}? Re-analyze the stock and tell me if I should hold or sell with clear reasoning.",
            "requiresTicker": True
        },
        {
            "id": "stop-loss-target",
            "label": "Stop Loss & Price Targets",
            "prompt": "Calculate optimal stop loss and price targets for {TICKER} based on technical analysis and volatility.",
            "requiresTicker": True
        }
    ],
    "market": [
        {
            "id": "market-movers",
            "label": "What's Moving the Market?",
            "prompt": "What's moving the market today? Show me key market drivers, news events, and how they're affecting stocks.",
            "requiresTicker": False
        },
        {
            "id": "hot-sectors",
            "label": "Hot Sectors Right Now",
            "prompt": "What sectors are hot right now? Identify trending sectors with specific stock picks in each.",
            "requiresTicker": False
        },
        {
            "id": "news-catalysts",
            "label": "Stocks with Positive Catalysts",
            "prompt": "Show me stocks with positive news catalysts today that could drive price movement.",
            "requiresTicker": False
        },
        {
            "id": "earnings-this-week",
            "label": "Key Earnings This Week",
            "prompt": "What are the most important earnings reports this week and which stocks should I watch?",
            "requiresTicker": False
        }
    ]
}

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str, color: str = Colors.CYAN):
    """Print a formatted header"""
    print(f"\n{color}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{color}{Colors.BOLD}{text.center(80)}{Colors.END}")
    print(f"{color}{Colors.BOLD}{'='*80}{Colors.END}\n")

def print_test_result(prompt_id: str, label: str, success: bool, details: str = ""):
    """Print test result with formatting"""
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if success else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"  {status} [{prompt_id}] {label}")
    if details:
        print(f"      {Colors.YELLOW}{details}{Colors.END}")

def test_streaming_chat(prompt: str, prompt_type: str, prompt_id: str, ticker: str = None) -> Tuple[bool, str]:
    """
    Test a streaming chat request.
    Returns (success, error_message)
    """
    url = f"{API_BASE_URL}/chat/stream"
    
    headers = {
        "Content-Type": "application/json"
    }
    if API_KEY:
        headers["X-API-Key"] = API_KEY
    
    # Replace {TICKER} placeholder if needed
    final_prompt = prompt.replace("{TICKER}", ticker) if ticker else prompt
    
    request_body = {
        "message": final_prompt,
        "conversation_history": [],
        "conversation_id": f"test_{prompt_id}_{int(time.time())}",
        "prompt_type": prompt_type,
        "prompt_id": prompt_id
    }
    
    try:
        response = requests.post(url, json=request_body, headers=headers, stream=True, timeout=30)
        
        if response.status_code == 401:
            return False, "Authentication failed - check API_KEY"
        if response.status_code == 503:
            return False, "Service unavailable - agent not initialized"
        if response.status_code != 200:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
        
        # Read streaming response
        content_received = False
        error_received = False
        error_message = ""
        
        for line in response.iter_lines():
            if not line:
                continue
            
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                try:
                    data = json.loads(line_str[6:])
                    
                    if data.get('type') == 'error':
                        error_received = True
                        error_message = data.get('message', 'Unknown error')
                        break
                    elif data.get('type') == 'content':
                        content_received = True
                    elif data.get('type') == 'done':
                        content_received = True
                        break
                except json.JSONDecodeError:
                    continue
        
        if error_received:
            return False, f"Stream error: {error_message}"
        if not content_received:
            return False, "No content received in stream"
        
        return True, "Success"
        
    except requests.exceptions.Timeout:
        return False, "Request timeout"
    except requests.exceptions.ConnectionError:
        return False, "Connection error - is the server running?"
    except Exception as e:
        return False, f"Exception: {str(e)}"

def test_category(category_name: str, prompts: List[Dict], category_color: str) -> Dict:
    """Test all prompts in a category"""
    print_header(f"Testing {category_name.upper()} Category", category_color)
    
    results = {
        "total": len(prompts),
        "passed": 0,
        "failed": 0,
        "details": []
    }
    
    for prompt in prompts:
        ticker = None
        if prompt.get("requiresTicker"):
            ticker = TEST_TICKERS[0]  # Use first test ticker
        
        print(f"\n  Testing: {prompt['label']}")
        if ticker:
            print(f"    Using ticker: {ticker}")
        
        success, details = test_streaming_chat(
            prompt["prompt"],
            category_name,
            prompt["id"],
            ticker
        )
        
        if success:
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        results["details"].append({
            "id": prompt["id"],
            "label": prompt["label"],
            "success": success,
            "details": details
        })
        
        print_test_result(prompt["id"], prompt["label"], success, details)
        
        # Small delay between requests
        time.sleep(1)
    
    return results

def main():
    """Run all tests"""
    print_header("Eddie Quick Actions Comprehensive Test Suite", Colors.BOLD)
    print(f"{Colors.WHITE}API Base URL: {API_BASE_URL}{Colors.END}")
    print(f"{Colors.WHITE}API Key: {'Set' if API_KEY else 'Not Set (may fail auth)'}{Colors.END}")
    print(f"{Colors.WHITE}Test Tickers: {', '.join(TEST_TICKERS)}{Colors.END}\n")
    
    # Check if server is reachable
    try:
        health_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print(f"{Colors.GREEN}✓ Server is reachable{Colors.END}\n")
        else:
            print(f"{Colors.YELLOW}⚠ Server returned status {health_response.status_code}{Colors.END}\n")
    except Exception as e:
        print(f"{Colors.RED}✗ Cannot reach server: {e}{Colors.END}\n")
        print(f"{Colors.YELLOW}Make sure the backend is running on {API_BASE_URL}{Colors.END}\n")
        return 1
    
    all_results = {}
    total_passed = 0
    total_failed = 0
    
    # Test each category
    category_colors = {
        "quick_wins": Colors.GREEN,
        "analysis": Colors.BLUE,
        "risk": Colors.YELLOW,
        "market": Colors.MAGENTA
    }
    
    for category, prompts in PROMPTS.items():
        results = test_category(category, prompts, category_colors[category])
        all_results[category] = results
        total_passed += results["passed"]
        total_failed += results["failed"]
    
    # Print summary
    print_header("Test Summary", Colors.BOLD)
    
    for category, results in all_results.items():
        category_name = category.replace("_", " ").title()
        color = Colors.GREEN if results["failed"] == 0 else Colors.RED
        print(f"{color}{category_name}:{Colors.END} {results['passed']}/{results['total']} passed")
    
    print(f"\n{Colors.BOLD}Overall:{Colors.END} {total_passed}/{total_passed + total_failed} tests passed")
    
    if total_failed > 0:
        print(f"\n{Colors.RED}Failed Tests:{Colors.END}")
        for category, results in all_results.items():
            for detail in results["details"]:
                if not detail["success"]:
                    print(f"  - [{category}] {detail['label']}: {detail['details']}")
    
    # Save results to file
    results_file = f"quick_actions_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "api_url": API_BASE_URL,
            "results": all_results,
            "summary": {
                "total": total_passed + total_failed,
                "passed": total_passed,
                "failed": total_failed
            }
        }, f, indent=2)
    
    print(f"\n{Colors.CYAN}Results saved to: {results_file}{Colors.END}\n")
    
    return 0 if total_failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())

