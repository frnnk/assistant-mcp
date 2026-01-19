"""
FastMCP server, aggregating all resources, tools, and prompts. 
"""

import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP, Context
from mcp.types import TextContent
from fastmcp.tools.tool import ToolResult
from mcp_tools.google.calendar import GoogleCalendarToolApp
from auth.providers.provider_registry import get_provider
from auth.oauth_gate import elicitation_mapping, callback_state
from utils.decorators import mcp_oauth_handler
from starlette.requests import Request
from starlette.responses import PlainTextResponse, RedirectResponse

load_dotenv()
SERVER_HOST = os.getenv('SERVER_HOST')
SERVER_PORT = os.getenv('SERVER_PORT')
SERVER_ORIGIN_PROXY = os.getenv('SERVER_ORIGIN_PROXY')

mcp = FastMCP(name="Assistant-MCP", host=SERVER_HOST, port=SERVER_PORT)
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
        proxy_origin=SERVER_ORIGIN_PROXY
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
@mcp_oauth_handler("Authorization is required to access your Google Calendar.")
def list_calendars(ctx: Context):
    """
    List all calendars in the user's Google Calendar account.
    Returns calendar_id values needed for other calendar tools.
    """
    result = calendar_tools.run_method(
        'list_calendars',
        ctx=ctx
    )
    return result


@mcp.tool()
@mcp_oauth_handler("Authorization is required to access your Google Calendar.")
def list_events(
    ctx: Context,
    start_time: str,
    calendar_id: str = 'primary',
    duration_days: int = 7
):
    """
    List events from a specific calendar within a time range.

    Prerequisites:
        - calendar_id: Obtain from list_calendars first. Otherwise defaults to primary
        calendar

    Args:
        calendar_id: The calendar ID from list_calendars
        start_time: Start time in ISO format (e.g., '2026-01-06T00:00:00')
        duration_days: Number of days to look ahead (default: 7)

    Returns event_id values needed for update_event.
    """
    result = calendar_tools.run_method(
        'list_events',
        ctx=ctx,
        calendar_id=calendar_id,
        start_time=datetime.fromisoformat(start_time),
        duration=timedelta(days=duration_days)
    )
    return result


@mcp.tool()
@mcp_oauth_handler("Authorization is required to access your Google Calendar.")
def create_event(
    ctx: Context,
    start: str,
    name: str = None,
    calendar_id: str = 'primary',
    duration_minutes: int = 30,
    location: str = None,
    description: str = None
):
    """
    Create a new event in a specific calendar.

    Prerequisites:
        - calendar_id: Obtain from list_calendars first. Otherwise defaults to primary calendar.

    Args:
        calendar_id: The calendar ID from list_calendars
        start: Start time in ISO format (e.g., '2026-01-06T14:00:00')
        name: Event name/title (optional - agent should generate from context if not provided)
        duration_minutes: Event duration in minutes (default: 30)
        location: Optional event location
        description: Optional event description
    """
    result = calendar_tools.run_method(
        'create_event',
        ctx=ctx,
        calendar_id=calendar_id,
        name=name,
        start=datetime.fromisoformat(start),
        duration=timedelta(minutes=duration_minutes),
        location=location,
        description=description
    )
    return result


@mcp.tool()
@mcp_oauth_handler("Authorization is required to access your Google Calendar.")
def update_event(
    ctx: Context,
    calendar_id: str,
    event_id: str,
    start: str,
    name: str = None,
    duration_minutes: int = 30,
    location: str = None,
    description: str = None
):
    """
    Update an existing event in a specific calendar.

    Prerequisites:
        - calendar_id: Obtain from list_calendars first
        - event_id: Obtain from list_events first

    Args:
        calendar_id: The calendar ID from list_calendars
        event_id: The event ID from list_events
        start: Updated start time in ISO format (e.g., '2026-01-06T14:00:00')
        name: Updated event name/title (optional - keeps existing if not provided)
        duration_minutes: Updated event duration in minutes (default: 30)
        location: Updated event location
        description: Updated event description
    """
    result = calendar_tools.run_method(
        'update_event',
        ctx=ctx,
        calendar_id=calendar_id,
        event_id=event_id,
        name=name,
        start=datetime.fromisoformat(start),
        duration=timedelta(minutes=duration_minutes),
        location=location,
        description=description
    )
    return result


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
