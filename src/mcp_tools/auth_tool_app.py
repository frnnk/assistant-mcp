"""
Provides a generic interface for MCP integrations using OAuth 2.0. Makes use of OAuthProvider,
found in auth.providers.provider, to supply an OAuth token.

OAuth tokens use the generic interface OAuthToken, found in auth.tokens.auth_token
"""

from abc import ABC
from typing import Sequence, Dict, Any
from auth.providers.provider import OAuthProvider
from auth.tokens.auth_token import OAuthToken
from auth.oauth_gate import ensure_auth
from utils.errors import MethodNotFoundError, ScopesNotFoundError

class OAuthToolApp(ABC):
    """
    Docstring for OAuthToolApp
    """
    def __init__(self, provider: OAuthProvider):
        self.provider = provider
    
    def run_method(self, method_name: str, *, ctx: Dict[str, Any], **kwargs):
        method = getattr(self, method_name, None)
        scopes = getattr(method, '__scopes__', None)
    
        if method is None:
            raise MethodNotFoundError
        if scopes is None:
            raise ScopesNotFoundError
        
        # pass to oauth gateway
        result = ensure_auth(
            provider=self.provider,
            method=method,
            ctx=ctx,
            scopes=scopes,
            **kwargs
        )

        return result
        
        



