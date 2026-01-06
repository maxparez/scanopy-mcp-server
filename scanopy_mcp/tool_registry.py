"""Tool registry for scanning OpenAPI spec and registering MCP tools."""

from collections.abc import Mapping

# Standard HTTP methods we support (excluding OPTIONS, TRACE, etc.)
_STANDARD_METHODS = {"get", "head", "post", "put", "patch", "delete"}

# OpenAPI Path Item object fields that are not HTTP methods
_OPENAPI_PATH_METADATA = {
    "$ref",
    "summary",
    "description",
    "servers",
    "parameters",
}


class ToolRegistry:
    """Registry for MCP tools derived from OpenAPI specification."""

    def __init__(self, openapi_spec: Mapping, allowlist: set[str]):
        """Initialize the registry.

        Args:
            openapi_spec: OpenAPI specification as a dictionary.
            allowlist: Set of write operation IDs that are allowed.
        """
        self.spec = openapi_spec
        self.allowlist = allowlist

    def list_tools(self) -> dict:
        """List all available tools from the OpenAPI spec.

        Returns:
            Dictionary mapping operation IDs to tool metadata.
            Write operations not in allowlist are excluded.

        Raises:
            ValueError: If duplicate operationId is found.
        """
        tools = {}

        for path, ops in self.spec.get("paths", {}).items():
            for method, op in ops.items():
                # Skip OpenAPI metadata keys
                if method in _OPENAPI_PATH_METADATA or method.lower() not in _STANDARD_METHODS:
                    continue

                op_id = op.get("operationId")
                if not op_id:
                    continue

                # Filter write operations by allowlist FIRST
                is_write = method.lower() in {"post", "put", "patch", "delete"}
                if is_write and op_id not in self.allowlist:
                    continue

                # Check for duplicate operationId AFTER filtering
                if op_id in tools:
                    raise ValueError(f"Duplicate operationId: {op_id}")

                tools[op_id] = {"method": method.upper(), "path": path}

        return tools
