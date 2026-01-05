"""Tests for scanopy_mcp.policy."""

from scanopy_mcp.policy import PolicyGuard


def test_write_requires_confirm():
    """Write operations should require matching confirm string."""
    guard = PolicyGuard(allowlist={"discovery.start"}, confirm_string="CONFIRM")

    try:
        guard.enforce_write("discovery.start", confirm=None)
        assert False, "expected ValueError"
    except ValueError:
        assert True
