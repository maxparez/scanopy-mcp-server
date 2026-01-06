"""Tests for scanopy_mcp.allowlist."""

from scanopy_mcp.allowlist import WRITE_ALLOWLIST


def test_allowlist_contains_discovery_write():
    """Allowlist should contain discovery write operations."""
    assert "discoveries.create" in WRITE_ALLOWLIST
    assert "discoveries.start" in WRITE_ALLOWLIST
