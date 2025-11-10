#!/usr/bin/env python3
"""
TradingAgents Run Script

This script ensures all dependencies are installed and starts the TradingAgents application.
It handles:
- Virtual environment creation
- Dependency installation
- Environment variable setup
- Application startup
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_colored(message, color=Colors.RESET):
    """Print colored message."""
    print(f"{color}{message}{Colors.RESET}")

def print_step(step_num, message):
    """Print a step message."""
    print_colored(f"\n{'='*60}", Colors.CYAN)
    print_colored(f"Step {step_num}: {message}", Colors.BOLD + Colors.CYAN)
    print_colored(f"{'='*60}", Colors.CYAN)

def check_python_version():
    """Check if Python version is 3.10 or higher."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print_colored(f"❌ Python 3.10 or higher is required", Colors.RED)
        print_colored(f"   Current version: {version.major}.{version.minor}.{version.micro}", Colors.RED)
        return False
    print_colored(f"✅ Python version: {version.major}.{version.minor}.{version.micro}", Colors.GREEN)
    return True

def get_venv_python():
    """Get the path to the virtual environment Python."""
    if platform.system() == "Windows":
        return Path("..venv/Scripts/python.exe")
    else:
        return Path("..venv/bin/python")

def get_venv_pip():
    """Get the path to the virtual environment pip."""
    if platform.system() == "Windows":
        return Path(".venv/Scripts/pip")
    else:
        return Path(".venv/bin/pip")

def create_venv():
    """Create a virtual environment if it doesn't exist."""
    venv_path = Path("venv")
    venv_python = get_venv_python()
    
    if venv_path.exists() and venv_python.exists():
        print_colored("✅ Virtual environment already exists", Colors.GREEN)
        return True
    
    print_colored("Creating virtual environment...", Colors.YELLOW)
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print_colored("✅ Virtual environment created successfully", Colors.GREEN)
        return True
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ Failed to create virtual environment: {e}", Colors.RED)
        return False

def install_dependencies():
    """Install dependencies from requirements.txt."""
    venv_pip = get_venv_pip()
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print_colored("❌ requirements.txt not found", Colors.RED)
        return False
    
    print_colored("Installing dependencies from requirements.txt...", Colors.YELLOW)
    print_colored("This may take a few minutes...", Colors.YELLOW)
    
    try:
        # Install requirements
        result = subprocess.run(
            [str(venv_pip), "install", "-r", "requirements.txt"],
            check=True,
            capture_output=True,
            text=True
        )
        print_colored("✅ Dependencies installed successfully", Colors.GREEN)
        
        # Try to install watchfiles with compatibility flag if needed
        print_colored("Installing additional dependencies...", Colors.YELLOW)
        try:
            env = os.environ.copy()
            env["PYO3_USE_ABI3_FORWARD_COMPATIBILITY"] = "1"
            subprocess.run(
                [str(venv_pip), "install", "watchfiles"],
                check=True,
                capture_output=True,
                text=True,
                env=env
            )
        except subprocess.CalledProcessError:
            # watchfiles might already be installed or not needed
            pass
        
        # Install pydantic-settings if not already installed
        subprocess.run(
            [str(venv_pip), "install", "pydantic-settings"],
            check=False,
            capture_output=True
        )
        
        return True
    except subprocess.CalledProcessError as e:
        print_colored(f"⚠️  Some dependencies may have failed to install", Colors.YELLOW)
        print_colored(f"   Error: {e.stderr}", Colors.YELLOW)
        print_colored("   Continuing anyway...", Colors.YELLOW)
        return True  # Continue anyway

def check_env_file():
    """Check if .env file exists and has required keys."""
    env_file = Path(".env")
    if not env_file.exists():
        env_example = Path(".env.example")
        if env_example.exists():
            print_colored("⚠️  .env file not found", Colors.YELLOW)
            print_colored("   Copying .env.example to .env...", Colors.YELLOW)
            try:
                import shutil
                shutil.copy(env_example, env_file)
                print_colored("✅ .env file created from .env.example", Colors.GREEN)
                print_colored("   Please edit .env and add your API keys!", Colors.YELLOW)
            except Exception as e:
                print_colored(f"❌ Failed to create .env file: {e}", Colors.RED)
        else:
            print_colored("⚠️  .env file not found and .env.example doesn't exist", Colors.YELLOW)
        return False
    
    # Check if API keys are set (try to load dotenv, but don't fail if not installed)
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print_colored("⚠️  python-dotenv not installed yet, skipping env check", Colors.YELLOW)
        return False
    
    google_key = os.getenv("GOOGLE_API_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    
    has_keys = False
    if google_key and google_key != "your-google-api-key-here":
        print_colored("✅ GOOGLE_API_KEY is set", Colors.GREEN)
        has_keys = True
    elif openai_key and openai_key != "your-openai-api-key-here":
        print_colored("✅ OPENAI_API_KEY is set", Colors.GREEN)
        has_keys = True
    
    if alpha_vantage_key and alpha_vantage_key != "your-alpha-vantage-api-key-here":
        print_colored("✅ ALPHA_VANTAGE_API_KEY is set", Colors.GREEN)
    else:
        print_colored("⚠️  ALPHA_VANTAGE_API_KEY is not set", Colors.YELLOW)
        print_colored("   Get a free key from: https://www.alphavantage.co/support/#api-key", Colors.YELLOW)
    
    if not has_keys:
        print_colored("⚠️  No LLM API key found (GOOGLE_API_KEY or OPENAI_API_KEY)", Colors.YELLOW)
        print_colored("   Please add your API keys to .env file", Colors.YELLOW)
    
    return has_keys

def fix_chromadb_config():
    """Fix chromadb configuration to handle extra environment variables."""
    try:
        chromadb_config_path = Path(".venv/lib/python3.14/site-packages/chromadb/config.py")
        if not chromadb_config_path.exists():
            # Try to find it in different Python versions
            venv_lib = Path(".venv/lib")
            if venv_lib.exists():
                for python_dir in venv_lib.glob("python*"):
                    config_path = python_dir / "site-packages/chromadb/config.py"
                    if config_path.exists():
                        chromadb_config_path = config_path
                        break
        
        if chromadb_config_path.exists():
            # Read the config file
            with open(chromadb_config_path, 'r') as f:
                content = f.read()
            
            # Check if already patched
            if "from pydantic_settings import BaseSettings" in content:
                print_colored("✅ ChromaDB config already patched", Colors.GREEN)
                return True
            
            # Patch the import
            if "from pydantic import BaseSettings" in content:
                content = content.replace(
                    "from pydantic import BaseSettings",
                    "from pydantic_settings import BaseSettings"
                )
                with open(chromadb_config_path, 'w') as f:
                    f.write(content)
                print_colored("✅ ChromaDB config patched", Colors.GREEN)
                return True
    except Exception as e:
        print_colored(f"⚠️  Could not patch chromadb config: {e}", Colors.YELLOW)
        print_colored("   Continuing anyway...", Colors.YELLOW)
    
    return False

def set_chromadb_env_vars():
    """Set environment variables to prevent chromadb validation errors."""
    # Set chromadb-specific env vars to empty strings to avoid validation errors
    os.environ.setdefault("CHROMA_SERVER_HOST", "")
    os.environ.setdefault("CHROMA_SERVER_HTTP_PORT", "")
    os.environ.setdefault("CHROMA_SERVER_GRPC_PORT", "")
    os.environ.setdefault("CLICKHOUSE_HOST", "")
    os.environ.setdefault("CLICKHOUSE_PORT", "")
    
    # Remove API keys from environment before chromadb loads
    # (We'll reload them after chromadb is initialized)
    api_keys = {
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
        "ALPHA_VANTAGE_API_KEY": os.environ.get("ALPHA_VANTAGE_API_KEY"),
        "GOOGLE_API_KEY": os.environ.get("GOOGLE_API_KEY"),
    }
    
    # Temporarily remove them
    for key in list(api_keys.keys()):
        if api_keys[key]:
            os.environ.pop(key, None)
    
    return api_keys

def restore_api_keys(api_keys):
    """Restore API keys to environment."""
    for key, value in api_keys.items():
        if value:
            os.environ[key] = value

def run_application():
    """Run the TradingAgents CLI application (INTERACTIVE - prompts for user input)."""
    venv_python = get_venv_python()
    
    if not venv_python.exists():
        print_colored("❌ Virtual environment Python not found", Colors.RED)
        return False
    
    print_colored("\n🚀 Starting TradingAgents CLI (Interactive Mode)...", Colors.BOLD + Colors.GREEN)
    print_colored("="*60, Colors.CYAN)
    print_colored("The application will now prompt you for:", Colors.YELLOW)
    print_colored("  - Ticker symbol (e.g., AAPL, NVDA, SPY)", Colors.YELLOW)
    print_colored("  - Analysis date (YYYY-MM-DD format)", Colors.YELLOW)
    print_colored("  - Which analysts to use", Colors.YELLOW)
    print_colored("  - Research depth (Shallow/Medium/Deep)", Colors.YELLOW)
    print_colored("  - LLM provider (Google/OpenAI/Anthropic/Ollama)", Colors.YELLOW)
    print_colored("  - AI models to use", Colors.YELLOW)
    print_colored("", Colors.RESET)
    
    try:
        # Prepare environment for subprocess with chromadb defaults
        env = os.environ.copy()
        env.setdefault("CHROMA_SERVER_HOST", "localhost")
        env.setdefault("CHROMA_SERVER_HTTP_PORT", "8000")
        env.setdefault("CHROMA_SERVER_GRPC_PORT", "50051")
        env.setdefault("CLICKHOUSE_HOST", "localhost")
        env.setdefault("CLICKHOUSE_PORT", "8123")
        
        # Run the CLI - create a wrapper script that directly calls the interactive analysis function
        wrapper_script = """
import os
import sys

# Set chromadb environment variables before any imports
os.environ.setdefault("CHROMA_SERVER_HOST", "localhost")
os.environ.setdefault("CHROMA_SERVER_HTTP_PORT", "8000")
os.environ.setdefault("CHROMA_SERVER_GRPC_PORT", "50051")
os.environ.setdefault("CLICKHOUSE_HOST", "localhost")
os.environ.setdefault("CLICKHOUSE_PORT", "8123")

# Load .env file
from dotenv import load_dotenv
load_dotenv()

# Import and run the interactive analysis function
from cli.main import run_analysis
run_analysis()
"""
        
        wrapper_path = Path("_run_cli.py")
        with open(wrapper_path, "w") as f:
            f.write(wrapper_script)
        
        # Run the CLI through the wrapper (interactive mode)
        result = subprocess.run(
            [str(venv_python), str(wrapper_path)],
            env=env,
            cwd=Path(__file__).parent
        )
        
        # Clean up wrapper
        if wrapper_path.exists():
            wrapper_path.unlink()
        
        return result.returncode == 0
    except KeyboardInterrupt:
        print_colored("\n\n⚠️  Application interrupted by user", Colors.YELLOW)
        return True
    except Exception as e:
        print_colored(f"\n❌ Failed to start application: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to set up and run the application."""
    print_colored("""
    ╔══════════════════════════════════════════════════════════╗
    ║         TradingAgents Setup & Run Script                  ║
    ║         Multi-Agents LLM Financial Trading Framework      ║
    ╚══════════════════════════════════════════════════════════╝
    """, Colors.BOLD + Colors.CYAN)
    
    # Change to script directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    print_colored(f"Working directory: {script_dir}", Colors.BLUE)
    
    # Step 1: Check Python version
    print_step(1, "Checking Python Version")
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Create virtual environment
    print_step(2, "Setting Up Virtual Environment")
    if not create_venv():
        sys.exit(1)
    
    # Step 3: Install dependencies
    print_step(3, "Installing Dependencies")
    if not install_dependencies():
        print_colored("⚠️  Some dependencies failed to install, but continuing...", Colors.YELLOW)
    
    # Step 4: Install watchfiles with compatibility flag if needed
    print_step(4, "Installing Additional Dependencies")
    venv_pip = get_venv_pip()
    try:
        env = os.environ.copy()
        env["PYO3_USE_ABI3_FORWARD_COMPATIBILITY"] = "1"
        subprocess.run(
            [str(venv_pip), "install", "watchfiles"],
            check=False,
            capture_output=True,
            env=env
        )
        print_colored("✅ Additional dependencies installed", Colors.GREEN)
    except Exception:
        print_colored("⚠️  Some optional dependencies may not be installed", Colors.YELLOW)
    
    # Step 5: Check environment variables
    print_step(5, "Checking Environment Variables")
    check_env_file()
    
    # Step 6: Fix chromadb config
    print_step(6, "Fixing ChromaDB Configuration")
    fix_chromadb_config()
    
    # Step 7: Run the application
    print_step(7, "Starting Application")
    success = run_application()
    
    if success:
        print_colored("\n✅ Application completed successfully!", Colors.GREEN)
    else:
        print_colored("\n⚠️  Application exited with errors", Colors.YELLOW)
        print_colored("   Check the error messages above for details", Colors.YELLOW)
    
    return 0 if success else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_colored("\n\n⚠️  Setup interrupted by user", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        print_colored(f"\n❌ Unexpected error: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        sys.exit(1)
