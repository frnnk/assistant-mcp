"""
Provides implementations for Google OAuth providers. Serves as an abstraction layer to app logic.
"""

from provider import OAuthProvider

class LocalGoogleProvider(OAuthProvider):
    """
    Google-based OAuth 2.0 provider for appication logic. Relies on local token storage. Primary
    id only maps to local dev user.

    Primarily used for local dev testing.
    """
    



