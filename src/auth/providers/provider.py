"""
Provides an interface for common-ground OAuth client responsibilities for downstream MCP integrations
and clients.
"""

from abc import ABC, abstractmethod
from typing import Optional, Sequence
from auth.tokens.auth_token import OAuthToken

class OAuthProvider(ABC):
    """
    Provides a parent interface for OAuth 2.0 providers.

    Handles the common OAuth responsibilities:
    - Get token given a principal id, if it exists
    - If token is expired, refresh if possible
    - Generate end-user auth url
    - Replace with new token from callback
    """
    def __init__(self):
        self.token: Optional[OAuthToken] = None
        self.scopes: Optional[Sequence[str]] = None
    
    def _set_token(self, token: OAuthToken) -> None:
        self.token = token
    
    # @abstractmethod
    # def _refresh_access_token(self) -> bool:
    #     return self.token.refresh()

    @abstractmethod
    def _get_existing_token(self, principal_id):
        pass

    @abstractmethod
    def _generate_auth_url(self):
        pass

    @abstractmethod
    def get_access_token(self, principal_id: str, scopes: Sequence[str]):
        pass

        






