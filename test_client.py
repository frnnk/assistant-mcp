"""
Used to test the mcp server.
"""

import os
import asyncio
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.types import CallToolResult
from mcp.client.streamable_http import streamable_http_client
from mcp.shared.exceptions import UrlElicitationRequiredError, McpError
from datetime import datetime, timezone

load_dotenv()
SERVER_PORT = os.getenv('SERVER_PORT')
SERVER_URL = f"http://localhost:{SERVER_PORT}/mcp"

async def main():
    async with streamable_http_client(SERVER_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Tools:", [t.name for t in tools.tools])
            import json
            try:
                result = await session.call_tool("list_events", arguments={
                    'calendar_id': 'primary',
                    'start_time': datetime.now().isoformat()
                })
                print(result.content)
                print(result.structuredContent)

            except McpError as e:
                error = e.error
                if error.code == -32042:
                    print(error.message)
                    error_data = error.data
                    print(json.dumps(error_data, indent=4))
                
                else:
                    print("MCP error:", e.error)

if __name__ == "__main__":
    asyncio.run(main())
