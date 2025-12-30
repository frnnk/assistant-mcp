"""
Provides a class for interfacing with the Google Calendar API. Come with a set of helper methods.
Makes use of the Google OAuth token, found in auth.tokens.google_token
"""

import datetime
from googleapiclient.discovery import build
from auth.tokens.google_token import GoogleToken
from auth.providers.google_provider import LocalGoogleProvider, create_local_google_provider
from mcp_tools.auth_tool_app import OAuthToolApp

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GoogleCalendarToolApp(OAuthToolApp):
    def create_service(creds):
        service = build('calendar', 'v3', credentials=creds)
        return service

    def get_availability():
        pass

    def create_event():
        pass

    def update_event():
        pass

    def list_events():
        pass


def main():
    provider = create_local_google_provider(SCOPES)
    new_token = provider.get_access_token("s", SCOPES)
    print(new_token.creds.token_state) 
    # x = GoogleCalendarToolApp()
    pass
