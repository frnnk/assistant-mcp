"""
FastMCP server, aggregating all resources, tools, and prompts. 
"""

import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context
from mcp.types import ElicitRequestURLParams, TextContent
from mcp.shared.exceptions import UrlElicitationRequiredError
from fastmcp.tools.tool import ToolResult
from mcp_tools.google.calendar import GoogleCalendarToolApp
from auth.providers.provider_registry import get_provider
from auth.oauth_gate import elicitation_mapping, callback_state
from utils.errors import MethodNotFoundError, OAuthRequiredError
from starlette.requests import Request
from starlette.responses import PlainTextResponse, RedirectResponse

load_dotenv()
SERVER_HOST = os.getenv('SERVER_HOST')
SERVER_PORT = os.getenv('SERVER_PORT')

mcp = FastMCP(name="Assistant-MCP", port=SERVER_PORT)
google_provider = get_provider('google')
calendar_tools = GoogleCalendarToolApp(provider=google_provider)

@mcp.custom_route("/auth/connect/{elicitation_id}", methods=['GET'])
async def auth_connect(request: Request) -> PlainTextResponse:
    elicitation_id = request.path_params['elicitation_id']
    elicitation_body = elicitation_mapping[elicitation_id]

    provider = get_provider(provider_name=elicitation_body['provider_name'])
    provider_state = provider.generate_auth_url(
        scopes=elicitation_body['scopes'],
        elicitation_id=elicitation_id,
        host=SERVER_HOST,
        port=SERVER_PORT
    )
    callback_state[elicitation_id] = provider_state
   
    return RedirectResponse(url=provider_state['auth_url'])


@mcp.custom_route("/auth/callback/{elicitation_id}", methods=['GET'])
async def auth_callback(request: Request) -> PlainTextResponse:
    elicitation_id = request.path_params['elicitation_id']
    provider_state = callback_state[elicitation_id]
    uri = str(request.url)

    provider = get_provider(provider_name=provider_state['provider'])
    provider.finish_auth(provider_state=provider_state, uri=uri)

    return PlainTextResponse("You may close this tab.")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def list_calendars(ctx: Context):
    """List all calendars in the user's Google Calendar"""
    try:
        result = calendar_tools.run_method(
            'list_calendars',
            ctx=ctx
        )
        return result
    except OAuthRequiredError as e:
        raise UrlElicitationRequiredError(
            elicitations=[
                ElicitRequestURLParams(
                    mode='url',
                    elicitationId=e.elicitation_id,
                    url=f"http://{SERVER_HOST}:{SERVER_PORT}/auth/connect/{e.elicitation_id}",
                    message="Authorization is required to access your Google Calendar."
                )
            ]
        )
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
    mcp.run(
        transport="streamable-http"
    )


if __name__ == "__main__":
    main()
