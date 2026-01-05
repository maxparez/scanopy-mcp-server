"""Configuration management for Scanopy MCP."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """Configuration for Scanopy MCP server."""

    base_url: str
    api_key: str
    confirm_string: str


def load_config() -> Config:
    """Load configuration from environment variables.

    Raises:
        ValueError: If required environment variables are missing.
    """
    base_url = os.getenv("SCANOPY_BASE_URL")
    api_key = os.getenv("SCANOPY_API_KEY")
    confirm_string = os.getenv("SCANOPY_CONFIRM_STRING", "I understand this will modify Scanopy")

    if not base_url or not api_key:
        raise ValueError("SCANOPY_BASE_URL and SCANOPY_API_KEY are required")

    return Config(base_url=base_url.rstrip("/"), api_key=api_key, confirm_string=confirm_string)
