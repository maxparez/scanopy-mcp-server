"""Tests for scanopy_mcp.runtime."""

from scanopy_mcp.runtime import build_runtime


def test_runtime_builds_with_allowlist():
    """Runtime should build with all components wired."""
    runtime = build_runtime(openapi_spec={"paths": {}}, allowlist=set())

    assert runtime is not None
    assert hasattr(runtime, "tools_list")
    assert hasattr(runtime, "tools_call")
