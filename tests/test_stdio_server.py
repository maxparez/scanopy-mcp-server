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

    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {"protocolVersion": "2024-11-05"},
    }
    response = server.handle_request(request)

    assert response["result"]["serverInfo"]["name"] == "scanopy-mcp-server"
    assert response["result"]["serverInfo"]["version"] == "0.1.0"
    assert response["result"]["protocolVersion"] == "2024-11-05"


def test_stdio_server_ignores_initialized_notification():
    """Server should ignore initialized notifications."""
    config = Config(
        base_url="http://test", api_key="key", confirm_string="CONFIRM"
    )
    server = MCPStdioServer(config=config, openapi_url="", allowlist=set())
    request = {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
    response = server.handle_request(request)
    assert response is None


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


def test_stdio_server_tools_list_includes_input_schema_and_confirm_for_writes():
    """tools/list should include inputSchema and require confirm for write ops."""
    config = Config(base_url="http://test", api_key="key", confirm_string="CONFIRM")
    server = MCPStdioServer(
        config=config,
        openapi_url="",
        allowlist={"create_host"},
        openapi_spec={
            "paths": {
                "/api/v1/hosts": {
                    "get": {
                        "operationId": "get_all_hosts",
                        "parameters": [
                            {"name": "limit", "in": "query", "schema": {"type": "integer"}}
                        ],
                    },
                    "post": {
                        "operationId": "create_host",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {"name": {"type": "string"}},
                                        "required": ["name"],
                                    }
                                }
                            }
                        },
                    },
                }
            }
        },
    )

    request = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
    response = server.handle_request(request)

    tools = {t["name"]: t for t in response["result"]["tools"]}
    read_schema = tools["get_all_hosts"]["inputSchema"]
    assert "limit" in read_schema["properties"]
    assert "confirm" not in read_schema["properties"]

    write_schema = tools["create_host"]["inputSchema"]
    assert "name" in write_schema["properties"]
    assert "confirm" in write_schema["properties"]
    assert "confirm" in write_schema.get("required", [])


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
