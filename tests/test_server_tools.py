"""Tests for scanopy_mcp.server."""

from unittest.mock import Mock

from scanopy_mcp.server import ScanopyMCPServer


def test_tools_list_returns_registered_tools():
    """Server should return all registered tools."""
    server = ScanopyMCPServer(tools={"x.y": {"method": "GET", "path": "/api/v1/x"}})

    out = server.tools_list()
    assert "x.y" in out
    assert out["x.y"]["method"] == "GET"


def test_tools_call_requests_without_policy(mocker):
    """Server should make HTTP requests for read operations."""
    mock_response = Mock()
    mock_response.json.return_value = {"result": "ok"}
    mock_response.raise_for_status = Mock()
    mocker.patch("httpx.Client.request", return_value=mock_response)

    client = Mock()
    client.request = Mock(return_value={"result": "ok"})

    server = ScanopyMCPServer(
        tools={"hosts.list": {"method": "GET", "path": "/api/v1/hosts"}}, client=client
    )

    result = server.tools_call("hosts.list", {})

    client.request.assert_called_once_with("GET", "/api/v1/hosts", json={})
    assert result == {"result": "ok"}


def test_tools_call_enforces_policy_on_write():
    """Server should enforce policy guard for write operations."""
    guard = Mock()
    guard.enforce_write = Mock(side_effect=ValueError("not allowed"))

    server = ScanopyMCPServer(
        tools={"hosts.create": {"method": "POST", "path": "/api/v1/hosts"}},
        guard=guard,
    )

    try:
        server.tools_call("hosts.create", {}, confirm=None)
        assert False, "expected ValueError"
    except ValueError as e:
        assert "not allowed" in str(e)

    guard.enforce_write.assert_called_once_with("hosts.create", confirm=None)
