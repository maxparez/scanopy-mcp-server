"""Tests for scanopy_mcp.transport."""

from scanopy_mcp.transport import build_tools_response


def test_tools_list_payload():
    """Transport helper should build MCP tools list payload."""
    payload = build_tools_response({"x.y": {"method": "GET", "path": "/api/v1/x"}})

    assert "x.y" in payload
