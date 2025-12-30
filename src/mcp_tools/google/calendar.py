"""
Provides a class for interfacing with the Google Calendar API. Come with a set of helper methods.
Makes use of the Google OAuth token, found in auth.tokens.google_token
"""

import datetime
from typing import List, Dict, Any, Iterable, Literal
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from auth.tokens.google_token import GoogleToken
from auth.providers.google_provider import LocalGoogleProvider, create_local_google_provider
from mcp_tools.auth_tool_app import OAuthToolApp

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

    def create_event():
        pass

    def update_event():
        pass

    def list_calendars(self, max_results: int = 250) -> List[Dict[str, Any]]:
        """
        Lists calendars on the user's calendar list via calendarList.list. :contentReference[oaicite:4]{index=4}
        """
        auth_token = self.get_auth_token("any")
        creds = auth_token.present_creds()
        service = self.create_service(creds=creds)
        out: List[Dict[str, Any]] = []
        page_token = None

        try:
            while True:
                resp = (
                    service.calendarList()
                    .list(maxResults=max_results, pageToken=page_token)
                    .execute()
                )
                out.extend(resp.get("items", []))
                page_token = resp.get("nextPageToken")
                if not page_token:
                    break
            return out
        except HttpError as e:
            raise RuntimeError(f"Google Calendar API error (list_calendars): {e}") from e

    def list_events():
        pass


def main():
    provider = create_local_google_provider(SCOPES)
    # new_token = provider.get_access_token("s", SCOPES)
    # print(new_token.creds.token_state) 
    cal = GoogleCalendarToolApp(provider=provider, scopes=SCOPES)
    x = cal.list_calendars(20)

    AccessMode = Literal["read", "write"]

    def has_write_access(entry: Dict[str, Any]) -> bool:
        # Google Calendar accessRole values include: owner, writer, reader, freeBusyReader. 
        return entry.get("accessRole") in {"owner", "writer"}


    def has_read_access(entry: Dict[str, Any]) -> bool:
        return entry.get("accessRole") in {"owner", "writer", "reader", "freeBusyReader"}


    def print_calendars(
        calendars: Iterable[Dict[str, Any]],
        mode = "read",
        include_missing_description: bool = False,
    ) -> None:
        """
        Print calendars as:
        - Summary (ID)
            Description: ...

        mode:
        - "read": includes owner/writer/reader/freeBusyReader
        - "write": includes owner/writer only
        """
        if mode not in ("read", "write"):
            raise ValueError("mode must be 'read' or 'write'")

        allowed = has_read_access if mode == "read" else has_write_access

        printed_any = False
        for cal in calendars:
            if not allowed(cal):
                continue

            summary = cal.get("summary") or "<no summary>"
            cal_id = cal.get("id") or "<no id>"
            desc = (cal.get("description") or "").strip()

            if not desc and not include_missing_description:
                continue

            printed_any = True
            print(f"- {summary} ({cal_id})")
            if desc:
                print(f"  Description: {desc}")
            else:
                print("  Description: <none>")
            print(f"  Access: {cal.get('accessRole', '<unknown>')}")
            print()

        if not printed_any:
            print(f"(No calendars matched mode={mode!r} and description filter.)")
    
    print("Calendars with edit permissions\n")
    print_calendars(x, mode="write", include_missing_description=True)
    print()
    print("Calendars with read permissions\n")
    print_calendars(x, mode="read", include_missing_description=True)
    pass
