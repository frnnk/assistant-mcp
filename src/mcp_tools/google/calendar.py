"""
Provides a class for interfacing with the Google Calendar API. Come with a set of helper methods.
Makes use of the Google OAuth token, found in auth.tokens.google_token
"""

import datetime
import json
from typing import List, Dict, Any, Iterable, Literal
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from auth.tokens.google_token import GoogleToken
from auth.providers.google_provider import create_local_google_provider
from utils.decorators import tool_retry_factory
from mcp_tools.auth_tool_app import OAuthToolApp
from gcsa.google_calendar import GoogleCalendar
from gcsa.event import Event

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GoogleCalendarToolApp(OAuthToolApp):
    def create_service(self, creds):
        service = build('calendar', 'v3', credentials=creds)
        return service

    def get_availability():
        """
        Get free times on a calendar
        """
        pass

    @tool_retry_factory(error_message="Google Calendar error (create_event)", retry_on=(HttpError,))
    def create_event(name: str, start: datetime, end: datetime):

        pass

    def update_event():
        pass

    @tool_retry_factory(error_message="Google Calendar error (list_calendars)", retry_on=(HttpError,))
    def list_calendars(self) -> List[Dict[str, Any]]:
        """
        Lists calendars on the user's calendar list.
        """
        auth_token = self.get_auth_token("localtest")
        creds = auth_token.present_creds()

        gc = GoogleCalendar(credentials=creds)
        calendar_list = []
        for calendar in gc.get_calendar_list():
            calendar_dict = {}
            calendar_dict['name'] = calendar.summary
            calendar_dict['desciption'] = calendar.description or 'n/a'
            calendar_dict['calender_id'] = calendar.calendar_id
            calendar_list.append(calendar_dict)
        
        return calendar_list

    def list_events(self, calendar_id, max_events=20):
        auth_token = self.get_auth_token("localtest")
        creds = auth_token.present_creds()

        try:
            count = 0
            gc = GoogleCalendar(credentials=creds, default_calendar=calendar_id)
            events_list = []
            for event in gc:
                if count > max_events:
                    break

                event_dict = {}
                event_dict['name'] = event.summary
                event_dict['start'] = str(event.start)
                event_dict['end'] = str(event.end)
                event_dict['desciption'] = event.description or 'n/a'
                event_dict['event_id'] = event.event_id or 'n/a'
                events_list.append(event_dict)
                count += 1
            
            return events_list
        except Exception as e:
            raise RuntimeError(f"Google Calendar API error (list_events): {e}") from e


def main():
    provider = create_local_google_provider(SCOPES)
    cal = GoogleCalendarToolApp(provider=provider, scopes=SCOPES)
    x = cal.list_calendars()
    # x = cal.list_events(calendar_id="en.usa#holiday@group.v.calendar.google.com")
    print(json.dumps(x, indent=4))
    pass
