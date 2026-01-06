"""Tests for scanopy_mcp.tool_registry."""

from scanopy_mcp.tool_registry import ToolRegistry


def test_registry_filters_write_ops():
    """Registry should include all read ops but only allowlisted write ops."""
    spec = {
        "paths": {
            "/api/v1/hosts": {
                "get": {"operationId": "hosts.list"},
                "post": {"operationId": "hosts.create"},
            }
        }
    }
    allowlist = {"hosts.create"}

    reg = ToolRegistry(spec, allowlist=allowlist)
    tools = reg.list_tools()

    # Read operation should be included
    assert "hosts.list" in tools
    assert tools["hosts.list"]["method"] == "GET"
    assert tools["hosts.list"]["path"] == "/api/v1/hosts"

    # Allowlisted write operation should be included
    assert "hosts.create" in tools
    assert tools["hosts.create"]["method"] == "POST"


def test_registry_excludes_non_allowlisted_writes():
    """Registry should exclude write ops not in allowlist."""
    spec = {
        "paths": {
            "/api/v1/hosts": {
                "delete": {"operationId": "hosts.delete"},
            }
        }
    }
    allowlist = set()  # Empty allowlist

    reg = ToolRegistry(spec, allowlist=allowlist)
    tools = reg.list_tools()

    # Write op not in allowlist should be excluded
    assert "hosts.delete" not in tools


def test_registry_handles_missing_operation_id():
    """Registry should skip operations without operationId."""
    spec = {
        "paths": {
            "/api/v1/unknown": {
                "get": {},  # No operationId
            }
        }
    }

    reg = ToolRegistry(spec, allowlist=set())
    tools = reg.list_tools()

    # Should not crash, just skip
    assert len(tools) == 0
