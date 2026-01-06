"""
Provides a class for interfacing with the Google Calendar API. Come with a set of helper methods.
Makes use of the Google OAuth token, found in auth.tokens.google_token
"""

import json
from typing import Optional, List, Dict, Any, Iterable, Literal
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from auth.tokens.auth_token import OAuthToken
from auth.providers.google_provider import create_local_google_provider
from utils.decorators import tool_retry_factory, tool_scope_factory
from mcp_tools.auth_tool_app import OAuthToolApp
from gcsa.google_calendar import GoogleCalendar
from gcsa.event import Event
from datetime import datetime, timedelta

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GoogleCalendarToolApp(OAuthToolApp):
    @tool_scope_factory(scopes=SCOPES)
    @tool_retry_factory(error_message="Google Calendar error (create_event)", retry_on=(HttpError,))
    def create_event(
        self, *,
        token: OAuthToken,
        ctx: Dict[str, Any], 
        calendar_id: str,
        name: str, 
        start: datetime, 
        duration: Optional[timedelta],
        location: Optional[str],
        description: Optional[str]
    ):
        """
        Docstring for create_event
        """
        creds = token.present_creds()
        gc = GoogleCalendar(credentials=creds, default_calendar=calendar_id)
        event = Event(
            summary=name,
            start=start,
            end=start + duration,
            location=location,
            description=description
        )
        event = gc.add_event(event=event)

        return {
            "event_details": str(event),
            "id": event.id
        }


    @tool_scope_factory(scopes=SCOPES)
    @tool_retry_factory(error_message="Google Calendar error (update_event)", retry_on=(HttpError,))
    def update_event(
        self, *,
        token: OAuthToken,
        ctx: Dict[str, Any], 
        calendar_id: str,
        event_id: str,
        name: str, 
        start: datetime, 
        duration: Optional[timedelta],
        location: Optional[str],
        description: Optional[str]
    ):
        creds = token.present_creds()
        gc = GoogleCalendar(credentials=creds, default_calendar=calendar_id)
        event = gc.get_event(event_id=event_id, calendar_id=calendar_id)
        
        event.summary=name
        event.start=start
        event.end=start + duration
        event.location=location
        event.description=description
        event = gc.update_event(event=event)

        return {
            "event_details": str(event),
            "id": event.id
        }


    @tool_scope_factory(scopes=SCOPES)
    @tool_retry_factory(error_message="Google Calendar error (list_calendars)", retry_on=(HttpError,))
    def list_calendars(self, *, token: OAuthToken, ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Lists calendars on the user's calendar list.
        """
        creds = token.present_creds()
        gc = GoogleCalendar(credentials=creds)

        calendar_list = []
        for calendar in gc.get_calendar_list():
            calendar_dict = {}
            calendar_dict['name'] = calendar.summary
            calendar_dict['desciption'] = calendar.description or 'n/a'
            calendar_dict['calender_id'] = calendar.calendar_id
            calendar_list.append(calendar_dict)
        
        return {
            'calendars': calendar_list
        }


    @tool_scope_factory(scopes=SCOPES)
    @tool_retry_factory(error_message="Google Calendar error (list_events)", retry_on=(HttpError,))
    def list_events(
        self, *, 
        token: OAuthToken, 
        ctx: Dict[str, Any], 
        calendar_id: str, 
        start_time: datetime,
        duration: timedelta
    ):
        creds = token.present_creds()
        gc = GoogleCalendar(credentials=creds, default_calendar=calendar_id)
        events = list(gc.get_events(
            start_time, start_time+duration, single_events=True, order_by='startTime')
        )
        
        events_list = []
        for event in events:
            event_dict = {}
            event_dict['name'] = event.summary
            event_dict['start'] = str(event.start)
            event_dict['end'] = str(event.end)
            event_dict['desciption'] = event.description or 'n/a'
            event_dict['event_id'] = event.event_id or 'n/a'
            events_list.append(event_dict)
        
        return events_list


def main():
    pass
