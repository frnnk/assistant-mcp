"""
Construction of useful decorators and closures.
"""

import os
import time
from typing import Tuple, Type, Sequence
from random import randint
from functools import wraps
from dotenv import load_dotenv
from mcp.types import ElicitRequestURLParams
from mcp.shared.exceptions import UrlElicitationRequiredError
from utils.errors import OAuthRequiredError

load_dotenv()
SERVER_HOST = os.getenv('SERVER_HOST')
SERVER_PORT = os.getenv('SERVER_PORT')
SERVER_ORIGIN_PROXY = os.getenv('SERVER_ORIGIN_PROXY')


def tool_retry_factory(
    error_message: str, 
    retry_on: Tuple[Type[Exception]] = (Exception,), 
    retries=3,
):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            for cnt in range(retries + 1):
                try:
                    return fn(*args, **kwargs)
                except retry_on as e:
                    if cnt == retries:
                        raise RuntimeError(f"{error_message}") from e

                    print(f"retrying, ran into error: {e}")
                    duration = 2**cnt + randint(0, 100) / 100
                    time.sleep(duration)
        
        return wrapper
    return decorator


def tool_scope_factory(
    scopes: Sequence[str]
):
    def decorator(fn):
        fn.__scopes__ = scopes
        return fn
    return decorator


def mcp_oauth_handler(message: str = "Authorization is required."):
    """
    Decorator that handles OAuthRequiredError and converts it to UrlElicitationRequiredError
    for MCP tool functions. Automatically reads SERVER_HOST and SERVER_PORT from environment.

    Args:
        message: Custom message to display to the user when OAuth is required
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except OAuthRequiredError as e:
                origin = SERVER_ORIGIN_PROXY if SERVER_ORIGIN_PROXY else f"{SERVER_HOST}:{SERVER_PORT}"
                raise UrlElicitationRequiredError(
                    elicitations=[
                        ElicitRequestURLParams(
                            mode='url',
                            elicitationId=e.elicitation_id,
                            url=f"http://{origin}/auth/connect/{e.elicitation_id}",
                            message=message
                        )
                    ]
                )
        return wrapper
    return decorator

