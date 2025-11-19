"""
CLI Entry Point for Strategy System

Usage:
    python -m tradingagents.strategies compare AAPL
    python -m tradingagents.strategies value AAPL
    python -m tradingagents.strategies list
"""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())

