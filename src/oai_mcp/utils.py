from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def sanitize_tool_name(name: str) -> str:
    """Sanitize tool name for OpenAI compatibility"""
    # Replace any characters that might cause issues
    return name.replace("-", "_").replace(" ", "_").lower()


def compare_toolname(openai_toolname: str, mcp_toolname: str) -> bool:
    return sanitize_tool_name(mcp_toolname) == openai_toolname


def convert_mcp_tools_to_openai_format(
    mcp_tools: List[Any]
) -> List[Dict[str, Any]]:
    """Convert MCP tool format to OpenAI tool format"""
    openai_tools = []
    
    False and logger.debug(f"Input mcp_tools type: {type(mcp_tools)}")
    False and logger.debug(f"Input mcp_tools: {mcp_tools}")
    
    # Extract tools from the response
    if hasattr(mcp_tools, 'tools'):
        tools_list = mcp_tools.tools
        False and logger.debug("Found ListToolsResult, extracting tools attribute")
    elif isinstance(mcp_tools, dict):
        tools_list = mcp_tools.get('tools', [])
        False and logger.debug("Found dict, extracting 'tools' key")
    else:
        tools_list = mcp_tools
        False and logger.debug("Using mcp_tools directly as list")
        
    False and logger.debug(f"Tools list type: {type(tools_list)}")
    False and logger.debug(f"Tools list: {tools_list}")
    
    # Process each tool in the list
    if isinstance(tools_list, list):
        False and logger.debug(f"Processing {len(tools_list)} tools")
        for tool in tools_list:
            False and logger.debug(f"Processing tool: {tool}, type: {type(tool)}")
            if hasattr(tool, 'name') and hasattr(tool, 'description'):
                openai_name = sanitize_tool_name(tool.name)
                False and logger.debug(f"Tool has required attributes. Name: {tool.name}")
                
                tool_schema = getattr(tool, 'inputSchema', {})
                (tool_schema.setdefault(k, v) for k, v in {
                    "type": "object",
                    "properties": {},
                    "required": []
                }.items()) 
                                
                openai_tool = {
                    "type": "function",
                    "function": {
                        "name": openai_name,
                        "description": tool.description,
                        "parameters": tool_schema
                    }
                }

                openai_tools.append(openai_tool)
                False and logger.debug(f"Converted tool {tool.name} to OpenAI format")
            else:
                False and logger.debug(
                    f"Tool missing required attributes: "
                    f"has name = {hasattr(tool, 'name')}, "
                    f"has description = {hasattr(tool, 'description')}"
                )
    else:
        False and logger.debug(f"Tools list is not a list, it's a {type(tools_list)}")
    
    return openai_tools