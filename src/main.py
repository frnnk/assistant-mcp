"""
FastMCP server, aggregating all resources, tools, and prompts. 
"""

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.fastmcp.exceptions import ToolError
from mcp.types import CallToolResult, TextContent
from mcp_tools.google.calendar import GoogleCalendarToolApp
from auth.providers.provider_registry import get_provider
from utils.errors import MethodNotFoundError, OAuthRequiredError
from starlette.requests import Request
from starlette.responses import PlainTextResponse, RedirectResponse

mcp = FastMCP(name="Assistant-MCP")
local_google_provider = get_provider('google-local')
calendar_tools = GoogleCalendarToolApp(provider=local_google_provider)

@mcp.custom_route("/auth/connect/{elicitation_id}", methods=['GET'])
async def auth_connect(request: Request) -> PlainTextResponse:
    elicitation_id = request.path_params['elicitation_id']
    # get provider type from short-term elicitation memory
    return PlainTextResponse("filler")


@mcp.custom_route("/auth/callback", methods=['POST'])
async def auth_callback(request: Request) -> PlainTextResponse:
    return PlainTextResponse("filler")


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
