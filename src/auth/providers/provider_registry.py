"""
Registry for different providers, to support dynamic retrieval of providers.

Providers should be one-time initialized.
"""

from auth.providers.google_provider import create_google_provider
from auth.providers.provider import OAuthProvider

GOOGLE_PROVIDER = create_google_provider()

PROVIDER_REGISTRY = {
    'google': GOOGLE_PROVIDER
}

def get_provider(provider_name: str) -> OAuthProvider:
    if PROVIDER_REGISTRY.get(provider_name) is None:
        raise RuntimeError("provider not found")

    return PROVIDER_REGISTRY[provider_name]