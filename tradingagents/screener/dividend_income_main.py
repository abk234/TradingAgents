# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Dividend Income Screener Main Entry Point

Run with: python -m tradingagents.screener.dividend_income
"""

from .dividend_income_cli import main

if __name__ == "__main__":
    exit(main())
