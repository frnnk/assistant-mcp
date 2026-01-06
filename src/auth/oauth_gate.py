"""
Constructs a function representing the OAuth gate, separating auth layers from tool logic. Serves
to store logic related to the OAuth gate within the auth module.

Called within OAuthToolApp's run_method (mcp_tools.auth_tool_app)
"""

import os
import uuid
from typing import Sequence, Dict, Any, Callable
from auth.providers.provider import OAuthProvider
from utils.errors import OAuthRequiredError

elicitation_mapping = {}
callback_state = {}

def ensure_auth(
    provider: OAuthProvider,
    method: Callable,
    ctx: Dict[str, Any],
    scopes: Sequence[str],
    **kwargs
):
    """
    Docstring for retrieve_auth_token
    
    :param provider: Description
    :type provider: OAuthProvider
    :param method: Description
    :type method: Callable
    :param ctx: Description
    :type ctx: Dict[str, Any]
    :param principal_id: Description
    :type principal_id: str
    :param scopes: Description
    :type scopes: Sequence[str]
    :param kwargs: Description
    """
    principal_id = 'localtest'
    token = provider.get_access_token(principal_id, scopes)
    if token is not None:
        kwargs['token'] = token
        return method(ctx=ctx, **kwargs)
    
    elicitation_id = str(uuid.uuid4())
    elicitation_mapping[elicitation_id] = {
        'provider_name': provider.name, 
        'scopes': scopes
    }

    raise OAuthRequiredError(
        message='OAuth required',
        elicitation_id=elicitation_id
    )
