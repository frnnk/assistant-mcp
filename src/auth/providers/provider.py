"""
Provides an interface for common-ground OAuth client responsibilities for downstream MCP integrations
and clients.
"""

from abc import ABC, abstractmethod
from typing import Optional, Sequence
import wsgiref.util
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
    def _get_stored_token(self, principal_id):
        pass

    @abstractmethod
    def _generate_auth_url(self):
        pass

    @abstractmethod
    def get_access_token(self, principal_id: str, scopes: Sequence[str]):
        pass


class LocalRedirectWSGIApp:
    """
    WSGI app to handle the authorization redirect.

    Stores the request URI and displays the given success message.
    """
    def __init__(self, success_message="You may close this tab."):
        """
        Args:
            success_message (str): The message to display in the web browser
                the authorization flow is complete.
        """
        self.last_request_uri = None
        self._success_message = success_message
        

    def __call__(self, environ, start_response):
        """
        WSGI Callable.

        Args:
            environ (Mapping[str, Any]): The WSGI environment.
            start_response (Callable[str, list]): The WSGI start_response
                callable.

        Returns:
            Iterable[bytes]: The response body.
        """
        start_response("200 OK", [("Content-type", "text/plain; charset=utf-8")])
        self.last_request_uri = wsgiref.util.request_uri(environ)
        return [self._success_message.encode("utf-8")]

        






