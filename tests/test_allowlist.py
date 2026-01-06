"""Tests for scanopy_mcp.allowlist."""

from scanopy_mcp.allowlist import WRITE_ALLOWLIST


def test_allowlist_contains_discovery_write():
    """Allowlist should contain discovery write operations."""
    assert "create_discovery" in WRITE_ALLOWLIST
    assert "cancel_discovery" in WRITE_ALLOWLIST
