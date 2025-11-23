# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
MCP Tool Adapter

Converts existing LangChain tools and custom tools to MCP format.
"""

from typing import Dict, Any, Callable, Optional
import inspect
import logging
from langchain_core.tools import BaseTool

from .server import MCPTool

logger = logging.getLogger(__name__)


class ToolAdapter:
    """Adapter for converting tools to MCP format"""
    
    @staticmethod
    def get_json_schema_from_function(func: Callable) -> Dict[str, Any]:
        """
        Extract JSON schema from a function's signature and docstring.
        
        Args:
            func: Function to analyze
            
        Returns:
            JSON schema for the function
        """
        sig = inspect.signature(func)
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
                
            param_type = param.annotation
            param_default = param.default
            
            # Map Python types to JSON schema types
            type_mapping = {
                str: "string",
                int: "integer",
                float: "number",
                bool: "boolean",
                list: "array",
                dict: "object"
            }
            
            json_type = "string"  # default
            if param_type != inspect.Parameter.empty:
                if param_type in type_mapping:
                    json_type = type_mapping[param_type]
                elif hasattr(param_type, "__origin__"):
                    # Handle Optional, Union, etc.
                    origin = param_type.__origin__
                    if origin is list:
                        json_type = "array"
                    elif origin is dict:
                        json_type = "object"
            
            prop = {"type": json_type}
            
            # Add default if available
            if param_default != inspect.Parameter.empty:
                prop["default"] = param_default
            
            properties[param_name] = prop
            
            # Add to required if no default
            if param_default == inspect.Parameter.empty:
                required.append(param_name)
        
        schema = {
            "type": "object",
            "properties": properties
        }
        
        if required:
            schema["required"] = required
        
        return schema
    
    @staticmethod
    def get_description_from_docstring(func: Callable) -> str:
        """Extract description from function docstring"""
        if func.__doc__:
            # Get first line or paragraph
            doc = func.__doc__.strip()
            lines = doc.split('\n')
            return lines[0].strip()
        return f"Tool: {func.__name__}"


def convert_langchain_tool_to_mcp(tool: BaseTool) -> MCPTool:
    """
    Convert a LangChain tool to MCP format.
    
    Args:
        tool: LangChain BaseTool instance
        
    Returns:
        MCPTool instance
    """
    # Get tool description
    description = tool.description or f"Tool: {tool.name}"
    
    # Get input schema
    if hasattr(tool, 'args_schema') and tool.args_schema:
        # Use Pydantic model if available
        try:
            schema = tool.args_schema.schema()
            input_schema = schema
        except Exception as e:
            logger.warning(f"Could not extract schema from {tool.name}: {e}")
            input_schema = {"type": "object", "properties": {}}
    else:
        # Try to infer from function signature
        if hasattr(tool, 'func'):
            input_schema = ToolAdapter.get_json_schema_from_function(tool.func)
        else:
            input_schema = {"type": "object", "properties": {}}
    
    # Create handler wrapper
    def handler(**kwargs):
        """Wrapper to call LangChain tool"""
        try:
            result = tool.invoke(kwargs)
            return result
        except Exception as e:
            logger.error(f"Error invoking tool {tool.name}: {e}")
            raise
    
    return MCPTool(
        name=tool.name,
        description=description,
        input_schema=input_schema,
        handler=handler
    )


def convert_function_to_mcp(
    func: Callable,
    name: Optional[str] = None,
    description: Optional[str] = None
) -> MCPTool:
    """
    Convert a Python function to MCP format.
    
    Args:
        func: Python function
        name: Tool name (defaults to function name)
        description: Tool description (defaults to docstring)
        
    Returns:
        MCPTool instance
    """
    tool_name = name or func.__name__
    tool_description = description or ToolAdapter.get_description_from_docstring(func)
    input_schema = ToolAdapter.get_json_schema_from_function(func)
    
    return MCPTool(
        name=tool_name,
        description=tool_description,
        input_schema=input_schema,
        handler=func
    )

