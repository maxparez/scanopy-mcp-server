"""Tests for scanopy_mcp.stdio_server."""

import json

from scanopy_mcp.config import Config
from scanopy_mcp.stdio_server import MCPStdioServer


def test_stdio_server_handles_initialize_request():
    """Server should respond to initialize request."""
    config = Config(
        base_url="http://test", api_key="key", confirm_string="CONFIRM"
    )
    server = MCPStdioServer(config=config, openapi_url="", allowlist=set())

    request = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    response = server.handle_request(request)

    assert response["result"]["serverInfo"]["name"] == "scanopy-mcp-server"
    assert response["result"]["serverInfo"]["version"] == "0.1.0"


def test_stdio_server_handles_tools_list_request():
    """Server should list available tools."""
    config = Config(
        base_url="http://test", api_key="key", confirm_string="CONFIRM"
    )
    server = MCPStdioServer(
        config=config,
        openapi_url="",
        allowlist=set(),
        openapi_spec={"paths": {"/api/v1/hosts": {"get": {"operationId": "hosts.list"}}}},
    )

    request = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
    response = server.handle_request(request)

    assert "tools" in response["result"]
    assert any(t["name"] == "hosts.list" for t in response["result"]["tools"])


def test_stdio_server_handles_tools_call_request(mocker):
    """Server should call tools."""
    config = Config(
        base_url="http://test", api_key="key", confirm_string="CONFIRM"
    )
    server = MCPStdioServer(
        config=config,
        openapi_url="",
        allowlist=set(),
        openapi_spec={"paths": {"/api/v1/hosts": {"get": {"operationId": "hosts.list"}}}},
    )

    # Mock the HTTP client
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"hosts": []}
    mock_response.raise_for_status = mocker.Mock()
    mocker.patch("httpx.Client.request", return_value=mock_response)

    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": "hosts.list", "arguments": {}},
    }
    response = server.handle_request(request)

    # MCP format wraps result in content array
    assert response["result"]["content"][0]["type"] == "text"
    assert json.loads(response["result"]["content"][0]["text"]) == {"hosts": []}
