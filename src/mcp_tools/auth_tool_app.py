"""
Provides a generic interface for MCP integrations using OAuth 2.0. Makes use of OAuthProvider,
found in auth.providers.provider, to supply an OAuth token.

OAuth tokens use the generic interface OAuthToken, found in auth.tokens.auth_token
"""

from abc import ABC
from typing import Sequence, Dict, Any
from auth.providers.provider import OAuthProvider
from auth.tokens.auth_token import OAuthToken
from utils.errors import MethodNotFoundError

class OAuthToolApp(ABC):
    """
    Docstring for OAuthToolApp
    """
    def __init__(self, provider: OAuthProvider, scopes: Sequence[str] = None):
        self.provider = provider
        self.scopes = scopes
    
    def get_auth_token(self, principal_id) -> OAuthToken:
        return self.provider.get_access_token(principal_id, scopes=self.scopes)

    def run_method(self, method_name: str, *, ctx: Dict[str, Any], **kwargs):
        method = getattr(self, method_name, None)
        # implement individual scoping here, use decorators to add scopes
        # scopes = getattr(method, ...)
        if method is None:
            raise MethodNotFoundError
        
        principal_id = ctx.get("principal_id", "localtest")
        token = self.provider.get_access_token(principal_id, self.scopes)
        if token is not None:
            kwargs['token'] = token
            return method(ctx=ctx, **kwargs)

        # otherwise start auth process and finish
        self.provider.start_auth(self.scopes)



