# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

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

