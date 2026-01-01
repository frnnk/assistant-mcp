"""
FastMCP server, aggregating all resources, tools, and prompts. 
"""

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.fastmcp.exceptions import ToolError
from mcp.types import CallToolResult, TextContent
from mcp_tools.google.calendar import GoogleCalendarToolApp
from auth.providers.google_provider import LOCAL_GOOGLE_PROVIDER
from utils.errors import MethodNotFoundError, OAuthRequiredError

mcp = FastMCP(name="Assistant-MCP")
calendar_tools = GoogleCalendarToolApp(provider=LOCAL_GOOGLE_PROVIDER)

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def list_calendars(ctx: Context):
    try:
        result = calendar_tools.run_method(
            'list_calendars',
            ctx=ctx
        )
        return CallToolResult(
            content=TextContent('text', "List of user's Calendars"),
            structuredContent=result
        )
    except OAuthRequiredError as e:
        raise ToolError(f"OAuth credentials needed:\n{e.auth_url}")
    except Exception as e:
        raise



# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


def main():
    """
    Entrypoint for MCP server
    """
    mcp.run()


if __name__ == "__main__":
    main()
