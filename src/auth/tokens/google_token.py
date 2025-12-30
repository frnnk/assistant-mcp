"""
Docstring for auth.tokens.google_token
"""

from .auth_token import OAuthToken
from google.auth.credentials import TokenState
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


class GoogleToken(OAuthToken):
    """
    Docstring for GoogleToken
    """
    def __init__(self, creds: Credentials):
        self.creds = creds

    @property
    def is_valid(self):
        return (
            self.creds.token_state == TokenState.FRESH or
            self.creds.token_state == TokenState.STALE
        )

    @property
    def is_stale(self):
        return self.creds.token_state == TokenState.STALE
    
    @property
    def can_refresh(self):
        return self.creds.refresh_token
        
    def refresh(self):
        self.creds.refresh(Request())

    def set_creds(self, creds: Credentials):
        self.creds = creds

    def present_creds(self) -> Credentials:
        return self.creds