# OpenAI LLM with MCP Integration

A Python package that enables OpenAI's Language Models to interact with Anthropic's Model Context Protocol (MCP) standard. This integration allows OpenAI models to use external tools and services through MCP servers.

## Features

- Seamless integration between OpenAI's chat completions and MCP servers
- Support for multiple MCP servers simultaneously
- Automatic tool conversion from Anthropic MCP format to OpenAI's toolcall format
- Asynchronous execution of tools and completions

## Installation

```bash
pip install git+https://github.com/dotrann1412/oai-mcp
```

## Quick Demo

Here's a simple example that demonstrates how to use the package with MCP servers:

```python
import oai_mcp
import asyncio
import openai 
from mcp import StdioServerParameters
import os

async def main():
    client = openai.AsyncOpenAI()
    
    # Create storage directory
    os.makedirs("storage", exist_ok=True)
    
    # Configure MCP servers
    mcp_servers = [
        # IP Info server
        StdioServerParameters( 
            command="mcp-server-ipinfo",
        ),
        
        # File System API server
        StdioServerParameters( 
            command="mcp-fsapi",
            env={
                "DIRECTORY": "storage"
            }
        ),
    ]

    # Get chat completion with MCP integration
    completion = await oai_mcp.get_chat_completion_with_mcp(
        messages=[
            {
                "role": "user",
                "content": "Inspect my current IP address and write the result to ip.txt"
            }
        ],
        client=client,
        mcp_servers=mcp_servers
    )

    print(completion.choices[0].message.content)
    # the file ip.txt should contains something!

if __name__ == "__main__":
    asyncio.run(main())
```

### Prerequisites for the Demo

1. Install the IP Info MCP server:
```bash
pip install git+https://github.com/briandconnelly/mcp-server-ipinfo
```

2. Install the File System API MCP server:
```bash
cd mcps/fsapi && pip install . && cd -
```

## License

This project is open source and available under the MIT License.
