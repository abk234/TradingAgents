"""
Entry point for TradingAgents Bot

Run with: python -m tradingagents.bot
"""

import sys
import os
import subprocess
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Launch Eddie - the TradingAgents bot using Chainlit."""
    print("=" * 70)
    print("🤖 Eddie - AI Trading Expert")
    print("=" * 70)
    print()
    print("Starting Chainlit web interface...")
    print("The bot will open in your browser at http://localhost:8000")
    print()
    print("Requirements:")
    print("  ✓ Ollama running (http://localhost:11434)")
    print("  ✓ llama3.3 model available")
    print("  ✓ Database with stock data")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 70)
    print()

    # Get the path to chainlit_app.py
    bot_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(bot_dir, "chainlit_app.py")

    try:
        # Launch Chainlit
        subprocess.run(
            ["chainlit", "run", app_path, "-w"],
            check=True
        )
    except KeyboardInterrupt:
        print("\n\n✓ Bot stopped by user")
        return 0
    except FileNotFoundError:
        logger.error("Chainlit not found. Please install it:")
        logger.error("  pip install chainlit")
        return 1
    except subprocess.CalledProcessError as e:
        logger.error(f"Error starting Chainlit: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
