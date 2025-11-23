# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Model Context Protocol (MCP) Integration

MCP is a protocol for integrating external tools and resources into AI applications.
This module provides MCP server support for Eddy, allowing third-party tools to be
integrated via the MCP standard.
"""

from .server import MCPServer, MCPTool, MCPResource
from .adapter import ToolAdapter, convert_langchain_tool_to_mcp

__all__ = [
    "MCPServer",
    "MCPTool",
    "MCPResource",
    "ToolAdapter",
    "convert_langchain_tool_to_mcp",
]

