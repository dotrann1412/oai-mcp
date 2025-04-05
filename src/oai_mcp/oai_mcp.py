import openai
import asyncio
from typing import List, Dict, Any
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import logging
import json
from .utils import convert_mcp_tools_to_openai_format, compare_toolname

logger = logging.getLogger(__name__)

async def get_chat_completion_with_mcp(
    messages: list[dict[str, str]], 
    client: openai.AsyncOpenAI, 
    model_id: str="gpt-4o-mini", 
    mcp_servers: List[StdioServerParameters]=[]
) -> openai.types.completion.Completion:

    if len(mcp_servers) == 0 or not isinstance(mcp_servers, list):
        if not isinstance(mcp_servers, list):
            logger.warning("mcp_servers is not a list, it's a %s", type(mcp_servers))

        return await client.chat.completions.create(
            model=model_id,
            messages=messages,
        )

    async with AsyncExitStack() as stack:
        sessions: List[ClientSession] = []

        for mcp_server in mcp_servers:
            connection = stdio_client(mcp_server)
            streams = await stack.enter_async_context(connection)
            sessions.append(await stack.enter_async_context(ClientSession(*streams)))

        await asyncio.gather(*[session.initialize() for session in sessions])
        tools = [
            await session.list_tools() 
            for session in sessions
        ]

        tools_mapping: Dict[str, ClientSession] = {}
        openai_compatible_tools: List[Dict[str, Any]] = []
        
        for i, tools in enumerate(tools):
            for tool in tools.tools:
                tools_mapping[tool.name] = sessions[i]
            openai_compatible_tools.extend(convert_mcp_tools_to_openai_format(tools.tools))
            
        async def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> str:

            for mcp_tool_name, mcp_session in tools_mapping.items():
                if compare_toolname(tool_name, mcp_tool_name):
                    res = await mcp_session.call_tool(tool_name, arguments)
                
                    if res.isError:
                        return (
                            f"Something went wrong while "
                            f"executing tool {tool_name} with {arguments}; Response: {res.content}"
                        )

                    return res.content

            return f"Tool {tool_name} not found"

        completion = await client.chat.completions.create(
            model=model_id,
            messages=messages,
            tools=openai_compatible_tools
        )
        
        messages.append(completion.choices[0].message.model_dump())
        
        while completion.choices[0].message.tool_calls is not None and len(completion.choices[0].message.tool_calls) > 0:
            for call in completion.choices[0].message.tool_calls:
                _id, _name = call.id, call.function.name
                _args = json.loads(call.function.arguments)
                
                result = await execute_tool(_name, _args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": _id,
                    "content": result
                })
                
            completion = await client.chat.completions.create(
                model=model_id,
                messages=messages,
                tools=openai_compatible_tools
            )

            messages.append(completion.choices[0].message.model_dump())

        return completion