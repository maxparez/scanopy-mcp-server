import pytest

from scanopy_mcp.server import ScanopyMCPServer


class DummyClient:
    def request(self, method, path, json=None, params=None):
        raise AssertionError("should not be called")


def test_prevalidation_missing_required_raises():
    tools = {
        "create_thing": {
            "method": "POST",
            "path": "/api/v1/things",
            "input_schema": {"type": "object", "required": ["name"]},
        }
    }
    server = ScanopyMCPServer(tools=tools, client=DummyClient())
    with pytest.raises(ValueError, match="Missing required fields"):
        server.tools_call("create_thing", args={})
