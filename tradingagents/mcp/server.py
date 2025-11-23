# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
MCP Server Implementation

Implements the Model Context Protocol server for tool integration.
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class MCPToolType(str, Enum):
    """MCP Tool Types"""
    FUNCTION = "function"
    RESOURCE = "resource"


@dataclass
class MCPTool:
    """Represents an MCP tool definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Optional[Callable] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to MCP tool definition format"""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema
        }


@dataclass
class MCPResource:
    """Represents an MCP resource"""
    uri: str
    name: str
    description: str
    mime_type: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to MCP resource definition format"""
        result = {
            "uri": self.uri,
            "name": self.name,
            "description": self.description
        }
        if self.mime_type:
            result["mimeType"] = self.mime_type
        return result


class MCPServer:
    """
    MCP Server for Eddy
    
    Implements the Model Context Protocol to allow external tools
    to be integrated into the trading assistant.
    """
    
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self._initialized = False
    
    def initialize(self) -> Dict[str, Any]:
        """
        Initialize the MCP server.
        Returns server capabilities.
        """
        if self._initialized:
            return self.get_capabilities()
        
        self._initialized = True
        logger.info("MCP Server initialized")
        return self.get_capabilities()
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get server capabilities"""
        return {
            "protocolVersion": "2024-11-05",
            "serverInfo": {
                "name": "eddy-mcp-server",
                "version": "1.0.0"
            },
            "capabilities": {
                "tools": {
                    "listChanged": True
                },
                "resources": {
                    "subscribe": True,
                    "listChanged": True
                }
            }
        }
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all registered tools"""
        return [tool.to_dict() for tool in self.tools.values()]
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all registered resources"""
        return [resource.to_dict() for resource in self.resources.values()]
    
    def register_tool(self, tool: MCPTool) -> None:
        """Register a new tool"""
        if tool.handler is None:
            raise ValueError(f"Tool {tool.name} must have a handler")
        
        self.tools[tool.name] = tool
        logger.info(f"Registered MCP tool: {tool.name}")
    
    def register_resource(self, resource: MCPResource) -> None:
        """Register a new resource"""
        self.resources[resource.uri] = resource
        logger.info(f"Registered MCP resource: {resource.uri}")
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a registered tool with given arguments.
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found")
        
        tool = self.tools[name]
        if tool.handler is None:
            raise ValueError(f"Tool '{name}' has no handler")
        
        try:
            logger.info(f"Calling MCP tool: {name} with args: {arguments}")
            
            # Handle MCP protocol format where arguments might be wrapped in 'arguments' key
            # This can happen when the request body follows MCP protocol format
            if isinstance(arguments, dict):
                # Check if arguments are wrapped in an 'arguments' key (MCP protocol format)
                if 'arguments' in arguments and len(arguments) == 1:
                    actual_args = arguments['arguments']
                    if isinstance(actual_args, dict):
                        arguments = actual_args
                        logger.debug(f"Unwrapped arguments from MCP format: {arguments}")
                    else:
                        logger.warning(f"Arguments wrapped in 'arguments' key but value is not dict: {actual_args}")
                # Also handle case where arguments might be at root level but empty
                elif not arguments:
                    logger.warning(f"Empty arguments provided for tool {name}")
            
            result = tool.handler(**arguments)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result) if not isinstance(result, str) else result
                    }
                ],
                "isError": False
            }
        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}", exc_info=True)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    def read_resource(self, uri: str) -> Dict[str, Any]:
        """
        Read a resource by URI.
        
        Args:
            uri: Resource URI
            
        Returns:
            Resource content
        """
        if uri not in self.resources:
            raise ValueError(f"Resource '{uri}' not found")
        
        resource = self.resources[uri]
        return {
            "contents": [
                {
                    "uri": resource.uri,
                    "mimeType": resource.mime_type or "text/plain",
                    "text": f"Resource: {resource.name}\n{resource.description}"
                }
            ]
        }
    
    def unregister_tool(self, name: str) -> None:
        """Unregister a tool"""
        if name in self.tools:
            del self.tools[name]
            logger.info(f"Unregistered MCP tool: {name}")
    
    def unregister_resource(self, uri: str) -> None:
        """Unregister a resource"""
        if uri in self.resources:
            del self.resources[uri]
            logger.info(f"Unregistered MCP resource: {uri}")

