"""
Construction of custom errors.
"""

class OAuthRequiredError(RuntimeError):
    def __init__(self, message: str, elicitation_id: str):
        self.message = message
        self.elicitation_id = elicitation_id

class MethodNotFoundError(RuntimeError):
    pass

class ScopesNotFoundError(RuntimeError):
    pass
