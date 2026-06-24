"""
CORS configuration (security-hardened) -- entity-agnostic.

Allowed origins come from the ALLOWED_ORIGINS environment variable (comma-separated). When it is
unset, this falls back to common localhost development origins. Credentials are enabled ONLY for an
explicit origin allow-list: the CORS specification forbids pairing a wildcard origin ("*") with
credentials (browsers reject it), so get_cors_credentials() returns False whenever the configured
origins are a wildcard. Configure production by setting, e.g.:

    ALLOWED_ORIGINS=https://app.example.com,https://www.example.com
"""

from __future__ import annotations

import os

# Sensible localhost defaults for local development when ALLOWED_ORIGINS is not set.
_DEV_DEFAULT_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]


def get_cors_origins() -> list:
    """Return the allowed CORS origins from ALLOWED_ORIGINS, or localhost dev defaults if unset."""
    raw = os.getenv("ALLOWED_ORIGINS", "").strip()
    if raw:
        return [origin.strip() for origin in raw.split(",") if origin.strip()]
    return list(_DEV_DEFAULT_ORIGINS)


def get_cors_credentials() -> bool:
    """Allow credentials only with an explicit origin list (never with a wildcard origin)."""
    return "*" not in get_cors_origins()
