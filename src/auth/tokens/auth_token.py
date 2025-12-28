"""
Provides an interface for tokens, corresponding to OAuth client responsibilities. Does not dictate 
specific token fields, but provides needed methods.
"""

from abc import ABC, abstractmethod

class OAuthToken(ABC):
    """
    Provides a parent interface for OAuth 2.0 tokens.

    Handles the common OAuth responsibilities for tokens:
    - Check token for expiration
    - Refresh token if possible
    """
    @abstractmethod
    def is_valid(self):
        pass

    @abstractmethod
    def can_refresh(self):
        pass

    @abstractmethod
    def refresh(self):
        pass

    @abstractmethod
    def set_creds(self):
        pass