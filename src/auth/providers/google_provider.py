"""
Provides implementations for Google OAuth providers. Serves as an abstraction layer to app logic.
"""

from typing import Sequence
from provider import OAuthProvider, LocalRedirectWSGIApp
from auth.tokens.google_token import GoogleToken
from google_auth_oauthlib.flow import Flow
import wsgiref.simple_server


class LocalGoogleProvider(OAuthProvider):
    """
    Google-based OAuth 2.0 provider for appication logic. Relies on local token storage. Primary
    id only maps to local dev user.

    Primarily used for local dev testing.
    """
    def __init__(self, flow: Flow):
        self.flow = flow
        self.scopes = None
        self.local_server = None
        self.redirect_app = None

    def _get_stored_token(self, principal_id):
        pass

    def _generate_auth_url(
        self,  
        host="localhost", 
        port=8080, 
        trailing_slash=True,
        **auth_kwargs
    ):
        fmt = "http://{}:{}/" if trailing_slash else "http://{}:{}"
        self.flow.redirect_uri = fmt.format(host, port)
        auth_url, _ = self.flow.authorization_url(**auth_kwargs)

        return auth_url

    def _fetch_token(self, auth_response):
        self.flow.fetch_token(authorization_response=auth_response)

    def _start_local_auth(
        self, 
        host="localhost", 
        port=8080,
        **auth_kwargs
    ):
        self.redirect_app = LocalRedirectWSGIApp()
        wsgiref.simple_server.WSGIServer.allow_reuse_address = False
        self.local_server = wsgiref.simple_server.make_server(host=host, port=port, app=self.redirect_app)
        print(f"started local server @ https://{host}:{port}")

        auth_url = self._generate_auth_url(host=host, port=port, **auth_kwargs)
        print(auth_url)
        print(self.flow.redirect_uri)

        self.local_server.timeout = 300
        return auth_url

    def _end_local_auth(self):
        # Note: using https here because oauthlib is very picky that
        # OAuth 2.0 should only occur over https.
        authorization_response = self.redirect_app.last_request_uri.replace("http", "https")
        self._fetch_token(auth_response=authorization_response)
        self.local_server.server_close()

        return self.flow.credentials

    def get_access_token(self, principal_id: str, scopes: Sequence[str]):
        pass


if __name__ == "__main__":
    pass


