"""
Runtime secret loading (SEC004) -- entity-agnostic, pluggable backend.

Server secrets (database credentials, JWT/encryption keys, provider API keys) are sourced at RUNTIME
from a configurable backend -- never baked into images or committed to git. The default backend is
environment variables (use an untracked .env for local development). Set SECRETS_BACKEND to use a
managed store instead:

    SECRETS_BACKEND=env      (default) -- os.environ
    SECRETS_BACKEND=aws      -- AWS Secrets Manager (needs boto3); JSON secret id in SECRETS_AWS_NAME
    SECRETS_BACKEND=vault    -- HashiCorp Vault (needs hvac); VAULT_ADDR / VAULT_TOKEN / SECRETS_VAULT_PATH

get_secret(name, default) returns the value, preferring an explicit environment variable (so you can
override locally) and falling back to the managed store. Managed backends are imported lazily and the
fetched secret map is cached, so the dependency is optional and only loaded when that backend is used.

Usage in config:

    from config.secrets import get_secret
    SECRET_KEY = get_secret("SECRET_KEY")
    DATABASE_URL = get_secret("DATABASE_URL")
"""

import json
import os
from functools import lru_cache
from typing import Optional


@lru_cache(maxsize=1)
def _managed_secrets() -> dict:
    """Load and cache the secret map from the configured managed backend (empty for env/unknown)."""
    backend = os.getenv("SECRETS_BACKEND", "env").strip().lower()
    if backend == "aws":
        return _load_aws_secrets()
    if backend == "vault":
        return _load_vault_secrets()
    return {}


def _load_aws_secrets() -> dict:
    """Fetch a JSON secret from AWS Secrets Manager (SECRETS_AWS_NAME). Requires boto3."""
    secret_id = os.getenv("SECRETS_AWS_NAME")
    if not secret_id:
        return {}
    import boto3  # optional dependency, only imported for the aws backend

    client = boto3.client("secretsmanager", region_name=os.getenv("AWS_REGION", "us-east-1"))
    payload = client.get_secret_value(SecretId=secret_id).get("SecretString") or "{}"
    try:
        data = json.loads(payload)
    except (TypeError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _load_vault_secrets() -> dict:
    """Fetch a KV-v2 secret from HashiCorp Vault (SECRETS_VAULT_PATH). Requires hvac."""
    path = os.getenv("SECRETS_VAULT_PATH")
    if not path:
        return {}
    import hvac  # optional dependency, only imported for the vault backend

    client = hvac.Client(url=os.getenv("VAULT_ADDR"), token=os.getenv("VAULT_TOKEN"))
    secret = client.secrets.kv.v2.read_secret_version(path=path) or {}
    data = secret.get("data", {}).get("data", {})
    return data if isinstance(data, dict) else {}


def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    """Return a secret by name.

    Resolution order: an explicit environment variable (always wins, for local overrides), then the
    configured managed backend, then ``default``.
    """
    value = os.getenv(name)
    if value is not None:
        return value
    managed = _managed_secrets()
    if managed.get(name) is not None:
        return str(managed[name])
    return default
