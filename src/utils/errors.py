"""
Construction of custom errors.
"""

class OAuthRequiredError(RuntimeError):
    pass

class MethodNotFoundError(RuntimeError):
    pass
