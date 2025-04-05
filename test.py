# just a simple demo

import oai_mcp
import asyncio
import openai 
from mcp import StdioServerParameters
import os

async def main():
    client = openai.AsyncOpenAI()
    
    os.makedirs("storage", exist_ok=True)
    mcp_servers = [
        # setup: pip install git+https://github.com/briandconnelly/mcp-server-ipinfo
        StdioServerParameters( 
            command="mcp-server-ipinfo",
        ),

        # setup: cd mcps/fsapi && pip install . && cd -
        StdioServerParameters( 
            command="mcp-fsapi",
            env={
                "DIRECTORY": "storage"
            }
        ),
    ]

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

if __name__ == "__main__":
    asyncio.run(main())