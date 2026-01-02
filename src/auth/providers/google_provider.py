"""
Provides implementations for Google OAuth providers. Serves as an abstraction layer to app logic.
"""

import os
import os.path
from typing import Sequence, Union, Optional, Dict
from auth.providers.provider import OAuthProvider, LocalRedirectWSGIApp
from auth.tokens.google_token import GoogleToken
from utils.errors import OAuthRequiredError
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv
import wsgiref.simple_server

load_dotenv()
SCOPES = ["https://www.googleapis.com/auth/calendar"]
GOOGLE_SECRETS_PATH = os.getenv("GOOGLE_SECRETS_PATH")
GOOGLE_LOCAL_TOKEN_PATH = os.getenv("GOOGLE_LOCAL_TOKEN_PATH")

class LocalGoogleProvider(OAuthProvider):
    """
    Google-based OAuth 2.0 provider for appication logic. Relies on local token storage. Primary
    id only maps to local dev user.

    Primarily used for local dev testing.
    """
    def __init__(self, flow: Flow):
        self.flow = flow
        self.local_server = None
        self.redirect_app = None
    
    @property
    def name(self):
        return "google-local"

    def _get_stored_token(self, principal_id, scopes) -> Optional[GoogleToken]:
        if os.path.exists(GOOGLE_LOCAL_TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(GOOGLE_LOCAL_TOKEN_PATH, scopes)
            return GoogleToken(creds)
        
        return None 

    def generate_auth_url(
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
    ) -> str:
        self.redirect_app = LocalRedirectWSGIApp()
        wsgiref.simple_server.WSGIServer.allow_reuse_address = False
        self.local_server = wsgiref.simple_server.make_server(host=host, port=port, app=self.redirect_app)
        print(f"started local server @ https://{host}:{self.local_server.server_port}")

        auth_url = self.generate_auth_url(host=host, port=self.local_server.server_port, **auth_kwargs)
        print(auth_url)

        return auth_url

    def _end_local_auth(self):
        # Note: using https here because oauthlib is very picky that
        # OAuth 2.0 should only occur over https.
        authorization_response = self.redirect_app.last_request_uri.replace("http", "https")
        self._fetch_token(auth_response=authorization_response)
        self.local_server.server_close()

        return self.flow.credentials

    def get_access_token(self, principal_id: str, scopes: Sequence[str]) -> Optional[GoogleToken]:
        """
        Get valid token or return None.
        """
        token = self._get_stored_token(principal_id, scopes)
        if token is not None and token.is_valid:
            if not token.is_stale:
                return token
            if token.can_refresh:
                token.refresh()
                with open(GOOGLE_LOCAL_TOKEN_PATH, 'w') as new_token:
                    new_token.write(token.creds.to_json())
            
                return token
        
        return None

    def start_auth(self, scopes):
        # start local auth
        auth_url = self._start_local_auth(host="127.0.0.1", port=0)
        self.local_server.timeout = 300
        self.local_server.handle_request()
        creds = self._end_local_auth()

        # save new fetched token
        with open(GOOGLE_LOCAL_TOKEN_PATH, 'w') as new_token:
            new_token.write(creds.to_json())
        print(creds.token_state)
        
        raise OAuthRequiredError(
            message="Please authenticate with the give authorization link",
            auth_url=auth_url
        )


class GoogleProvider(OAuthProvider):
    """
    Google-based OAuth 2.0 provider for appication logic.

    Primarily used for local dev testing.
    """
    def __init__(self):
        self.local_server = None
        self.redirect_app = None

    @property
    def name(self):
        return "google"

    def _get_stored_token(self, principal_id, scopes) -> Optional[GoogleToken]:
        if os.path.exists(GOOGLE_LOCAL_TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(GOOGLE_LOCAL_TOKEN_PATH, scopes)
            return GoogleToken(creds)
        
        return None
    
    def get_access_token(self, principal_id: str, scopes: Sequence[str]) -> Optional[GoogleToken]:
        """
        Get valid token or return None.
        """
        token = self._get_stored_token(principal_id, scopes)
        if token is not None and token.is_valid:
            if not token.is_stale:
                return token
            if token.can_refresh:
                token.refresh()
                with open(GOOGLE_LOCAL_TOKEN_PATH, 'w') as new_token:
                    new_token.write(token.creds.to_json())
            
                return token
        
        return None

    def generate_auth_url(
        self,
        scopes: Sequence[str],
        elicitation_id: str,  
        host="localhost", 
        port=8080, 
        trailing_slash=True,
        **auth_kwargs
    ):
        flow = Flow.from_client_secrets_file(GOOGLE_SECRETS_PATH, scopes=scopes)
        fmt = "http://{}:{}/{}/" if trailing_slash else "http://{}:{}/{}"
        redirect_uri = fmt.format(host, port, elicitation_id)
        flow.redirect_uri = redirect_uri
        auth_url, state = flow.authorization_url(**auth_kwargs)

        return {
            'id': elicitation_id,
            'provider': self.name,
            'auth_url': auth_url,
            'redirect_uri': redirect_uri,
            'scopes': scopes,
            'state': state
        }
    
    def finish_auth(self, provider_state: Dict, uri):
        # restore flow
        flow = Flow.from_client_secrets_file(
            client_secrets_file=GOOGLE_SECRETS_PATH,
            scopes=provider_state['scopes'],
            state=provider_state['state']
        )
        flow.redirect_uri = provider_state['redirect_uri']

        # Note: using https here because oauthlib is very picky that
        # OAuth 2.0 should only occur over https.
        authorization_response = uri.replace("http", "https")
        flow.fetch_token(authorization_response=authorization_response)
        creds = flow.credentials

        with open(GOOGLE_LOCAL_TOKEN_PATH, 'w') as new_token:
            new_token.write(creds.to_json())
        print(creds.token_state)


def create_local_google_provider():
    flow = Flow.from_client_secrets_file(GOOGLE_SECRETS_PATH, scopes=SCOPES)
    provider = LocalGoogleProvider(flow)
    
    return provider

def create_google_provider():
    return GoogleProvider()


def main():
    provider = create_local_google_provider(SCOPES)
    new_token = provider.get_access_token("s", SCOPES)
    print(new_token.creds.token_state) 

if __name__ == "__main__":
    main()
    pass


