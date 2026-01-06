"""Tool registry for scanning OpenAPI spec and registering MCP tools."""

from collections.abc import Mapping


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
        """
        tools = {}

        for path, ops in self.spec.get("paths", {}).items():
            for method, op in ops.items():
                op_id = op.get("operationId")
                if not op_id:
                    continue

                is_write = method.lower() in {"post", "put", "patch", "delete"}
                if is_write and op_id not in self.allowlist:
                    continue

                tools[op_id] = {"method": method.upper(), "path": path}

        return tools
