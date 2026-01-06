"""Tests for scanopy_mcp.tool_registry."""

import pytest

from scanopy_mcp.tool_registry import ToolRegistry


def test_registry_skips_openapi_metadata_keys():
    """Registry should skip OpenAPI metadata keys like parameters, summary."""
    spec = {
        "paths": {
            "/api/v1/hosts": {
                "get": {"operationId": "hosts.list"},
                "parameters": [{"name": "filter", "in": "query"}],
                "summary": "Host operations",
            }
        }
    }

    reg = ToolRegistry(spec, allowlist=set())
    tools = reg.list_tools()

    # Should include the operation, skip metadata
    assert "hosts.list" in tools
    assert len(tools) == 1


def test_registry_raises_on_duplicate_operation_id():
    """Registry should raise error on duplicate operationId."""
    spec = {
        "paths": {
            "/api/v1/hosts": {"get": {"operationId": "duplicate"}},
            "/api/v1/devices": {"get": {"operationId": "duplicate"}},
        }
    }

    reg = ToolRegistry(spec, allowlist=set())

    with pytest.raises(ValueError, match="Duplicate operationId"):
        reg.list_tools()


def test_duplicate_detection_is_order_independent():
    """Duplicate detection should work regardless of dict key order."""
    # Same operationId for GET (read) and POST (write, not allowlisted)
    # Should NOT raise because POST is filtered out
    spec = {
        "paths": {
            "/api/v1/hosts": {
                "get": {"operationId": "same.id"},
                "post": {"operationId": "same.id"},
            }
        }
    }

    reg = ToolRegistry(spec, allowlist=set())  # POST not allowed
    tools = reg.list_tools()

    # Only GET should be included, no error
    assert "same.id" in tools
    assert tools["same.id"]["method"] == "GET"
    assert len(tools) == 1


def test_registry_skips_unknown_http_methods():
    """Registry should skip non-standard HTTP methods."""
    spec = {
        "paths": {
            "/api/v1/hosts": {
                "get": {"operationId": "hosts.list"},
                "options": {"operationId": "hosts.options"},
                "trace": {"operationId": "hosts.trace"},
            }
        }
    }

    reg = ToolRegistry(spec, allowlist=set())
    tools = reg.list_tools()

    # Only standard methods should be included
    assert "hosts.list" in tools
    assert "hosts.options" not in tools
    assert "hosts.trace" not in tools


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


def test_registry_builds_input_schema_from_parameters_and_body():
    """Input schema should include path/query params and request body fields."""
    spec = {
        "paths": {
            "/api/v1/hosts/{id}": {
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}
                ],
                "get": {
                    "operationId": "get_host_by_id",
                    "parameters": [
                        {"name": "include", "in": "query", "schema": {"type": "string"}}
                    ],
                },
                "put": {
                    "operationId": "update_host",
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
    }

    reg = ToolRegistry(spec, allowlist={"update_host"})
    tools = reg.list_tools()

    get_schema = tools["get_host_by_id"]["input_schema"]
    assert "id" in get_schema["properties"]
    assert "include" in get_schema["properties"]
    assert "id" in get_schema["required"]

    put_schema = tools["update_host"]["input_schema"]
    assert "name" in put_schema["properties"]
    assert "name" in put_schema["required"]


def test_registry_resolves_ref_in_request_body_schema():
    """Input schema should resolve local $ref schemas."""
    spec = {
        "components": {
            "schemas": {
                "HostUpdate": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"],
                }
            }
        },
        "paths": {
            "/api/v1/hosts/{id}": {
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}
                ],
                "put": {
                    "operationId": "update_host",
                    "requestBody": {
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/HostUpdate"}}
                        }
                    },
                },
            }
        },
    }

    reg = ToolRegistry(spec, allowlist={"update_host"})
    tools = reg.list_tools()

    put_schema = tools["update_host"]["input_schema"]
    assert "name" in put_schema["properties"]
    assert "name" in put_schema["required"]
