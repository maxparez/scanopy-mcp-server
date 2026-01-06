from unittest.mock import Mock

from scanopy_mcp.server import ScanopyMCPServer


def test_dry_run_blocks_write():
    client = Mock()
    guard = Mock()
    tools = {"hosts.create": {"method": "POST", "path": "/api/v1/hosts"}}
    server = ScanopyMCPServer(tools=tools, client=client, guard=guard)

    result = server.tools_call("hosts.create", {"name": "x"}, dry_run=True)

    assert result["dry_run"] is True
    assert result["request"]["method"] == "POST"
    assert result["request"]["path"] == "/api/v1/hosts"
    assert result["request"]["args"] == {"name": "x"}
    client.request.assert_not_called()
    guard.enforce_write.assert_not_called()
