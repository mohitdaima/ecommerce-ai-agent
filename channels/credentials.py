"""
Loads marketplace API credentials from a private `secrets.yaml` file.

secrets.yaml is git-ignored so your keys never get uploaded. Copy
`secrets.example.yaml` to `secrets.yaml` and fill in the keys you have.
Marketplaces you leave blank simply run in safe dry-run / export mode.
"""

from __future__ import annotations

import os

try:
    import yaml
except ImportError:
    yaml = None

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRETS_PATH = os.path.join(HERE, "secrets.yaml")


def load_secrets() -> dict:
    if yaml is None or not os.path.exists(SECRETS_PATH):
        return {}
    try:
        with open(SECRETS_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def creds_for(channel: str) -> dict:
    """Return the credential block for a channel, or {} if not configured."""
    data = load_secrets()
    return (data.get(channel) or data.get(channel.lower()) or {})
