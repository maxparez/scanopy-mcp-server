"""Tests for scanopy_mcp.policy fixes."""

import pytest

from scanopy_mcp.policy import PolicyGuard


def test_write_rejects_non_allowlisted_tool():
    """Write operations should reject tools not in allowlist."""
    guard = PolicyGuard(allowlist={"discovery.start"}, confirm_string="CONFIRM")

    with pytest.raises(ValueError, match="not allowlisted"):
        guard.enforce_write("unknown.tool", confirm="CONFIRM")


def test_write_requires_matching_confirm():
    """Write operations should require exact confirm string match."""
    guard = PolicyGuard(allowlist={"discovery.start"}, confirm_string="CONFIRM")

    with pytest.raises(ValueError, match="Invalid confirm string"):
        guard.enforce_write("discovery.start", confirm="WRONG")


def test_write_accepts_valid_confirm():
    """Write operations should succeed with valid confirm."""
    guard = PolicyGuard(allowlist={"discovery.start"}, confirm_string="CONFIRM")

    # Should not raise
    guard.enforce_write("discovery.start", confirm="CONFIRM")
