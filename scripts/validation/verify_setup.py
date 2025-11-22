#!/usr/bin/env python3
# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Setup Verification Script

Checks that all components are properly configured and ready.
"""

import sys
import subprocess
from tradingagents.default_config import DEFAULT_CONFIG


def check_ollama():
    """Check if Ollama is running and has required models."""
    print("\n" + "="*70)
    print("CHECKING OLLAMA")
    print("="*70)

    try:
        # Check if Ollama is accessible
        result = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/tags"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            print("✗ Ollama not responding")
            print("  Solution: Make sure Ollama is running")
            print("  Command: ollama serve")
            return False

        # Parse models
        import json
        try:
            data = json.loads(result.stdout)
            models = [m['name'] for m in data.get('models', [])]

            # Check required models
            required = ['llama3.1', 'llama3.3', 'nomic-embed-text']
            missing = []

            for model in required:
                # Check if any version of the model exists
                found = any(model in m for m in models)
                if found:
                    print(f"✓ {model}")
                else:
                    print(f"✗ {model} - NOT FOUND")
                    missing.append(model)

            if missing:
                print(f"\nMissing models: {', '.join(missing)}")
                print("Solution:")
                for model in missing:
                    print(f"  ollama pull {model}")
                return False
            else:
                print("\n✓ All required Ollama models installed")
                return True

        except json.JSONDecodeError:
            print("✗ Failed to parse Ollama response")
            return False

    except FileNotFoundError:
        print("✗ curl not found (needed to check Ollama)")
        return False
    except subprocess.TimeoutExpired:
        print("✗ Ollama connection timeout")
        print("  Solution: Make sure Ollama is running")
        return False
    except Exception as e:
        print(f"✗ Error checking Ollama: {e}")
        return False


def check_postgresql():
    """Check if PostgreSQL is running and database exists."""
    print("\n" + "="*70)
    print("CHECKING POSTGRESQL")
    print("="*70)

    try:
        # Try to connect to database
        result = subprocess.run(
            ["psql", "investment_intelligence", "-c", "SELECT version();"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            print("✓ PostgreSQL is running")
            print("✓ Database 'investment_intelligence' exists")

            # Check tickers
            result = subprocess.run(
                ["psql", "investment_intelligence", "-t", "-c", "SELECT COUNT(*) FROM tickers;"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                count = result.stdout.strip()
                print(f"✓ Tickers in database: {count}")

            return True
        else:
            print("✗ PostgreSQL connection failed")
            print("  Solution:")
            print("    brew services start postgresql@14")
            return False

    except FileNotFoundError:
        print("✗ psql not found (PostgreSQL not installed?)")
        return False
    except subprocess.TimeoutExpired:
        print("✗ PostgreSQL connection timeout")
        return False
    except Exception as e:
        print(f"✗ Error checking PostgreSQL: {e}")
        return False


def check_configuration():
    """Check current configuration."""
    print("\n" + "="*70)
    print("CHECKING CONFIGURATION")
    print("="*70)

    config = DEFAULT_CONFIG

    print(f"LLM Provider: {config['llm_provider']}")
    print(f"Deep Think Model: {config['deep_think_llm']}")
    print(f"Quick Think Model: {config['quick_think_llm']}")
    print(f"Backend URL: {config['backend_url']}")

    # Check data vendors
    print("\nData Vendors:")
    for category, vendor in config['data_vendors'].items():
        print(f"  {category}: {vendor}")

    # Validate configuration
    if config['llm_provider'] == 'ollama':
        if config['backend_url'] != 'http://localhost:11434/v1':
            print("\n⚠ Warning: Ollama provider but backend_url is not Ollama")
            return False

    print("\n✓ Configuration looks good")
    return True


def check_python_packages():
    """Check if required Python packages are installed."""
    print("\n" + "="*70)
    print("CHECKING PYTHON PACKAGES")
    print("="*70)

    required = [
        'psycopg2',
        'langchain',
        'langchain_openai',
        'langchain_anthropic',
        'langchain_google_genai',
        'yfinance',
        'pandas',
        'numpy',
        'requests'
    ]

    missing = []
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package}")
            missing.append(package)

    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        print("Solution:")
        print(f"  pip install {' '.join(missing)}")
        return False
    else:
        print("\n✓ All required packages installed")
        return True


def main():
    """Run all checks."""
    print("\n" + "="*70)
    print("INVESTMENT INTELLIGENCE SYSTEM - SETUP VERIFICATION")
    print("="*70)

    results = {
        'Configuration': check_configuration(),
        'Python Packages': check_python_packages(),
        'PostgreSQL': check_postgresql(),
        'Ollama': check_ollama(),
    }

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    all_passed = True
    for component, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:8s} {component}")
        if not passed:
            all_passed = False

    print()

    if all_passed:
        print("🎉 All checks passed! Your system is ready.")
        print("\nNext steps:")
        print("  1. Run screener: python -m tradingagents.screener run")
        print("  2. Analyze ticker: python -m tradingagents.analyze AAPL")
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
