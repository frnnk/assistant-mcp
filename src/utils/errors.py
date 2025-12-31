"""
Construction of custom errors.
"""

class OAuthRequiredError(RuntimeError):
    def __init__(self, message: str, auth_url: str):
        self.message = message
        self.auth_url = auth_url
    pass

class MethodNotFoundError(RuntimeError):
    pass
