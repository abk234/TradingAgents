"""
Filesystem middleware for TradingAgents.

Provides standardized file operations for agents.
"""

from typing import List, Dict, Any, Optional
from langchain_core.tools import tool, BaseTool
from pathlib import Path
import json
import re
import logging

from .base import TradingMiddleware

logger = logging.getLogger(__name__)


@tool
def ls(directory: str) -> str:
    """
    List files in a directory (requires absolute path).
    
    Use this to:
    - Browse available files
    - Check what reports exist
    - Find configuration files
    
    Args:
        directory: Absolute path to directory (must start with /)
    
    Returns:
        Formatted list of files and directories
    """
    if not directory.startswith("/"):
        return f"❌ Error: Path must be absolute (start with /). Got: {directory}"
    
    path = Path(directory)
    
    if not path.exists():
        return f"❌ Error: Directory does not exist: {directory}"
    
    if not path.is_dir():
        return f"❌ Error: Path is not a directory: {directory}"
    
    items = []
    for item in sorted(path.iterdir()):
        try:
            if item.is_dir():
                item_type = "📁"
                size = ""
            else:
                item_type = "📄"
                size_bytes = item.stat().st_size
                if size_bytes < 1024:
                    size = f"({size_bytes} B)"
                elif size_bytes < 1024 * 1024:
                    size = f"({size_bytes / 1024:.1f} KB)"
                else:
                    size = f"({size_bytes / (1024 * 1024):.1f} MB)"
            
            items.append(f"{item_type} {item.name} {size}")
        except Exception as e:
            logger.warning(f"Error reading item {item}: {e}")
            items.append(f"❓ {item.name} (error reading)")
    
    if not items:
        return f"📁 Directory is empty: {directory}"
    
    header = f"📁 Contents of {directory}:\n"
    return header + "\n".join(items)


@tool
def read_file(file_path: str, offset: int = 0, limit: int = None) -> str:
    """
    Read content from a file with optional pagination.
    
    Use this to:
    - Read analysis reports
- Read configuration files
    - Read historical data
    
    Args:
        file_path: Absolute path to file (must start with /)
        offset: Line number to start reading from (0-indexed, default: 0)
        limit: Maximum number of lines to read (default: all)
    
    Returns:
        File content (or portion if paginated)
    """
    if not file_path.startswith("/"):
        return f"❌ Error: Path must be absolute (start with /). Got: {file_path}"
    
    path = Path(file_path)
    
    if not path.exists():
        return f"❌ Error: File does not exist: {file_path}"
    
    if not path.is_file():
        return f"❌ Error: Path is not a file: {file_path}"
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return f"❌ Error reading file: {e}"
    
    total_lines = len(lines)
    start = max(0, offset)
    end = start + limit if limit else total_lines
    selected_lines = lines[start:end]
    
    content = "".join(selected_lines)
    
    if total_lines > end:
        remaining = total_lines - end
        content += f"\n... ({remaining} more lines)"
    
    header = f"📄 File: {file_path} (lines {start+1}-{min(end, total_lines)} of {total_lines})\n"
    header += "=" * 60 + "\n"
    
    return header + content


@tool
def write_file(file_path: str, content: str, overwrite: bool = True) -> str:
    """
    Create or overwrite a file.
    
    Use this to:
    - Save analysis results
    - Export data
    - Create reports
    
    Args:
        file_path: Absolute path to file (must start with /)
        content: Content to write
        overwrite: Whether to overwrite existing file (default: True)
    
    Returns:
        Confirmation message
    """
    if not file_path.startswith("/"):
        return f"❌ Error: Path must be absolute (start with /). Got: {file_path}"
    
    path = Path(file_path)
    
    if path.exists() and not overwrite:
        return f"❌ Error: File exists and overwrite=False: {file_path}"
    
    try:
        # Create parent directories if needed
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        size = len(content)
        size_str = f"{size:,} characters"
        if size > 1024:
            size_str += f" ({size / 1024:.1f} KB)"
        
        return f"✅ Written {size_str} to {file_path}"
    except Exception as e:
        return f"❌ Error writing file: {e}"


@tool
def edit_file(file_path: str, old_string: str, new_string: str) -> str:
    """
    Perform exact string replacement in a file.
    
    Use this to:
    - Update configuration files
    - Modify reports
    - Fix errors in files
    
    Args:
        file_path: Absolute path to file (must start with /)
        old_string: Exact text to replace
        new_string: Replacement text
    
    Returns:
        Confirmation message
    """
    if not file_path.startswith("/"):
        return f"❌ Error: Path must be absolute (start with /). Got: {file_path}"
    
    path = Path(file_path)
    
    if not path.exists():
        return f"❌ Error: File does not exist: {file_path}"
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return f"❌ Error reading file: {e}"
    
    if old_string not in content:
        return f"❌ Error: '{old_string[:50]}...' not found in file"
    
    new_content = content.replace(old_string, new_string)
    
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return f"✅ Replaced text in {file_path}"
    except Exception as e:
        return f"❌ Error writing file: {e}"


@tool
def glob(pattern: str, root_dir: str = "/tmp/tradingagents") -> str:
    """
    Find files matching a pattern.
    
    Use this to:
    - Find all analysis reports
    - Search for specific file types
    - Locate configuration files
    
    Args:
        pattern: Glob pattern (e.g., "**/*.json", "reports/*.txt")
        root_dir: Root directory to search from (default: /tmp/tradingagents)
    
    Returns:
        List of matching file paths
    """
    root = Path(root_dir)
    
    if not root.exists():
        return f"❌ Error: Root directory does not exist: {root_dir}"
    
    try:
        matches = list(root.glob(pattern))
    except Exception as e:
        return f"❌ Error searching: {e}"
    
    if not matches:
        return f"📁 No files found matching pattern: {pattern}"
    
    # Sort and format
    matches = sorted(matches)
    result = f"📁 Found {len(matches)} file(s) matching '{pattern}':\n\n"
    result += "\n".join(str(m) for m in matches)
    
    return result


@tool
def grep(pattern: str, file_path: str, context_lines: int = 0) -> str:
    """
    Search for text pattern in a file.
    
    Use this to:
    - Find specific information in reports
    - Search for keywords
    - Extract relevant sections
    
    Args:
        pattern: Text pattern to search for (case-insensitive)
        file_path: Absolute path to file (must start with /)
        context_lines: Number of context lines to include (default: 0)
    
    Returns:
        Matching lines with context
    """
    if not file_path.startswith("/"):
        return f"❌ Error: Path must be absolute (start with /). Got: {file_path}"
    
    path = Path(file_path)
    
    if not path.exists():
        return f"❌ Error: File does not exist: {file_path}"
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return f"❌ Error reading file: {e}"
    
    matches = []
    pattern_lower = pattern.lower()
    
    for i, line in enumerate(lines):
        if pattern_lower in line.lower():
            start = max(0, i - context_lines)
            end = min(len(lines), i + context_lines + 1)
            context = "".join(lines[start:end])
            matches.append(f"Line {i+1}:\n{context}")
    
    if not matches:
        return f"📄 No matches found for '{pattern}' in {file_path}"
    
    result = f"📄 Found {len(matches)} match(es) for '{pattern}' in {file_path}:\n\n"
    result += "\n\n".join(matches)
    
    return result


class FilesystemMiddleware(TradingMiddleware):
    """
    Middleware providing standardized filesystem tools.
    
    Enables agents to read/write files, search, and manage data.
    """
    
    def __init__(self, root_dir: str = "/tmp/tradingagents"):
        """
        Initialize filesystem middleware.
        
        Args:
            root_dir: Root directory for file operations (default: /tmp/tradingagents)
        """
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized FilesystemMiddleware (root: {root_dir})")
    
    @property
    def tools(self) -> List[BaseTool]:
        """Tools provided by this middleware."""
        return [ls, read_file, write_file, edit_file, glob, grep]
    
    def modify_prompt(self, prompt: str, agent_type: str) -> str:
        """Add filesystem tool instructions to prompt."""
        fs_instructions = """
        
## Filesystem Tools

You have access to filesystem tools for managing files and data:
- `ls(directory)`: List files in a directory (requires absolute path starting with /)
- `read_file(file_path, offset=0, limit=None)`: Read file content with pagination
- `write_file(file_path, content, overwrite=True)`: Create or overwrite files
- `edit_file(file_path, old_string, new_string)`: Perform exact string replacements
- `glob(pattern, root_dir="/tmp/tradingagents")`: Find files matching a pattern
- `grep(pattern, file_path, context_lines=0)`: Search for text in files

**Important:**
- All file paths must be absolute (start with `/`)
- Default root directory: `/tmp/tradingagents`
- Use these tools to save large analysis results (context offloading)
- Use for reading configuration files or historical reports
- Use for exporting data for external tools

**Example Usage:**
- Save report: `write_file("/tmp/tradingagents/reports/NVDA_analysis.txt", report_content)`
- Read report: `read_file("/tmp/tradingagents/reports/NVDA_analysis.txt")`
- Find reports: `glob("**/*.txt", "/tmp/tradingagents/reports")`
- Search in file: `grep("BUY", "/tmp/tradingagents/reports/NVDA_analysis.txt")`
"""
        return prompt + fs_instructions
    
    def pre_process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """No pre-processing needed."""
        return state
    
    def post_process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optionally offload large content to files.
        
        Args:
            state: Current agent state
        
        Returns:
            State with potentially offloaded content
        """
        # Context offloading can be implemented here
        # For now, just return state as-is
        return state

