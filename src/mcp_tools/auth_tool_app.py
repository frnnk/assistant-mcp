"""
Provides a generic interface for MCP integrations using OAuth 2.0. Makes use of OAuthProvider,
found in auth.providers.provider, to supply an OAuth token.

OAuth tokens use the generic interface OAuthToken, found in auth.tokens.auth_token
"""

from abc import ABC
from typing import Sequence
from auth.providers.provider import OAuthProvider
from auth.tokens.auth_token import OAuthToken


class OAuthToolApp(ABC):
    """
    Docstring for OAuthToolApp
    """
    def __init__(self, provider: OAuthProvider, scopes: Sequence[str] = None):
        self.provider = provider
        self.scopes = scopes
    
    def get_auth_token(self, principal_id) -> OAuthToken:
        return self.provider.get_access_token(principal_id, scopes=self.scopes)
    
    def start_auth_process(self):
        pass
    
    """
    Need to break oauth provider into:
        - can get access token: return it if possible otherwise say you can't
        - if we cant, make auth link, spin up server, and then return link
        have server on standby async
        - once server receives end user authentication, fetch the token async
        - so an implementation tool app:
            - cannot get auth token,
            - instead startup auth process and return the auth url
            - server will be on standby
    """


