"""Tests for scanopy_mcp.config fixes."""

import pytest

from scanopy_mcp.config import load_config


def test_config_rejects_empty_confirm_string(monkeypatch):
    """Config should reject empty confirm string."""
    monkeypatch.setenv("SCANOPY_BASE_URL", "http://test")
    monkeypatch.setenv("SCANOPY_API_KEY", "test_key")
    monkeypatch.setenv("SCANOPY_CONFIRM_STRING", "")

    with pytest.raises(ValueError, match="non-empty"):
        load_config()


def test_config_rejects_whitespace_confirm_string(monkeypatch):
    """Config should reject whitespace-only confirm string."""
    monkeypatch.setenv("SCANOPY_BASE_URL", "http://test")
    monkeypatch.setenv("SCANOPY_API_KEY", "test_key")
    monkeypatch.setenv("SCANOPY_CONFIRM_STRING", "   ")

    with pytest.raises(ValueError, match="non-empty"):
        load_config()


def test_config_accepts_valid_confirm_string(monkeypatch):
    """Config should accept valid non-empty confirm string."""
    monkeypatch.setenv("SCANOPY_BASE_URL", "http://test")
    monkeypatch.setenv("SCANOPY_API_KEY", "test_key")
    monkeypatch.setenv("SCANOPY_CONFIRM_STRING", "I CONFIRM")

    cfg = load_config()
    assert cfg.confirm_string == "I CONFIRM"
