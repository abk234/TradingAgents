#!/usr/bin/env python3
"""
Quick verification script to check if TradingAgents is set up correctly.
Run this after installation to verify everything works.
"""

import sys
import os

def check_python_version():
    """Check if Python version is 3.10 or higher."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Python 3.10 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_imports():
    """Check if required packages can be imported."""
    required_packages = [
        "langchain_openai",
        "langchain_google_genai",  # For Gemini support
        "langgraph",
        "pandas",
        "yfinance",
        "rich",
        "questionary",
        "typer",
        "dotenv",
    ]
    
    failed = []
    for package in required_packages:
        try:
            if package == "dotenv":
                __import__("dotenv")
            else:
                __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is NOT installed")
            failed.append(package)
    
    if failed:
        print(f"\n⚠️  Missing packages: {', '.join(failed)}")
        print("   Run: pip install -r requirements.txt")
        return False
    return True

def check_api_keys():
    """Check if API keys are set."""
    openai_key = os.getenv("OPENAI_API_KEY")
    alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    
    # Also check .env file
    from pathlib import Path
    env_file = Path(".env")
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv()
        openai_key = openai_key or os.getenv("OPENAI_API_KEY")
        alpha_vantage_key = alpha_vantage_key or os.getenv("ALPHA_VANTAGE_API_KEY")
        google_key = google_key or os.getenv("GOOGLE_API_KEY")
    
    all_good = True
    
    if openai_key and openai_key != "your-openai-api-key-here":
        print("✅ OPENAI_API_KEY is set")
    else:
        print("❌ OPENAI_API_KEY is NOT set")
        print("   Set it with: export OPENAI_API_KEY=your-key")
        print("   Or add it to .env file")
        print("   Note: Required for OpenAI models, optional if using Gemini")
        all_good = False
    
    if alpha_vantage_key and alpha_vantage_key != "your-alpha-vantage-api-key-here":
        print("✅ ALPHA_VANTAGE_API_KEY is set")
    else:
        print("❌ ALPHA_VANTAGE_API_KEY is NOT set")
        print("   Set it with: export ALPHA_VANTAGE_API_KEY=your-key")
        print("   Or add it to .env file")
        all_good = False
    
    # Google API key is optional (only needed for Gemini)
    if google_key and google_key != "your-google-api-key-here":
        print("✅ GOOGLE_API_KEY is set (for Gemini models)")
    else:
        print("ℹ️  GOOGLE_API_KEY is NOT set (optional - only needed for Gemini)")
        print("   Get it from: https://aistudio.google.com/app/apikey")
        print("   Set it with: export GOOGLE_API_KEY=your-key")
        print("   Or add it to .env file")
    
    return all_good

def check_tradingagents_import():
    """Check if tradingagents package can be imported."""
    try:
        import tradingagents
        print("✅ tradingagents package can be imported")
        return True
    except ImportError as e:
        print(f"❌ Cannot import tradingagents: {e}")
        print("   Make sure you're in the project root directory")
        return False

def main():
    """Run all checks."""
    print("=" * 60)
    print("TradingAgents Setup Verification")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Package Imports", check_imports),
        ("TradingAgents Package", check_tradingagents_import),
        ("API Keys", check_api_keys),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n📋 Checking {name}...")
        result = check_func()
        results.append((name, result))
        print()
    
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All checks passed! You're ready to use TradingAgents.")
        print("\nNext steps:")
        print("  1. Run the CLI: python -m cli.main analyze")
        print("  2. Or run the example: python main.py")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\nFor help, see SETUP_GUIDE.md")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

