"""Tests for scanopy_mcp.config."""

import importlib


def test_config_requires_base_url_and_key(monkeypatch):
    """Config should raise ValueError when SCANOPY_BASE_URL or SCANOPY_API_KEY are missing."""
    monkeypatch.delenv("SCANOPY_BASE_URL", raising=False)
    monkeypatch.delenv("SCANOPY_API_KEY", raising=False)

    cfg = importlib.import_module("scanopy_mcp.config")
    try:
        cfg.load_config()
        assert False, "expected ValueError"
    except ValueError:
        assert True
