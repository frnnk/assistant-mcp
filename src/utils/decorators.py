"""
Construction of useful decorators and closures.
"""

import time
import asyncio
from typing import Tuple, Type
from random import randint
from utils.errors import OAuthError

# decorators

def tool_retry_factory(
    error_message: str, 
    retry_on: Tuple[Type[Exception]] = (Exception,), 
    retries=3,
):
    def decorator(fn):
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

def async_tool_retry_factory(
    error_message: str, 
    retry_on: Tuple[Type[Exception]] = (Exception,), 
    retries=3,
):
    def decorator(fn):
        async def wrapper(*args, **kwargs):
            for cnt in range(retries):
                try:
                    result = await fn(*args, **kwargs)
                    return result
                except retry_on as e:
                    print(e)
                    duration = 2**cnt + randint(0, 100) / 100
                    await asyncio.sleep(duration)
                    continue
            
            raise RuntimeError(f"{error_message}")
        
        return wrapper
    return decorator

# closures