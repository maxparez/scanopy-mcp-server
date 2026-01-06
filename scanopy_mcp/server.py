"""MCP server for Scanopy API."""

from scanopy_mcp.client import ScanopyClient
from scanopy_mcp.policy import PolicyGuard


class ScanopyMCPServer:
    """MCP server that exposes Scanopy API tools."""

    def __init__(
        self,
        tools: dict,
        client: ScanopyClient | None = None,
        guard: PolicyGuard | None = None,
    ):
        """Initialize the MCP server.

        Args:
            tools: Dictionary of registered tools from ToolRegistry.
            client: Optional HTTP client for making requests.
            guard: Optional policy guard for write operations.
        """
        self._tools = tools
        self._client = client
        self._guard = guard

    def tools_list(self) -> dict:
        """List all available tools.

        Returns:
            Dictionary of tool metadata.
        """
        return self._tools

    def tools_call(self, name: str, args: dict, confirm: str | None = None) -> dict:
        """Call a tool by name.

        Args:
            name: Tool operation ID to call.
            args: Arguments to pass to the tool.
            confirm: Optional confirmation string for write operations.

        Returns:
            Tool result as a dictionary.

        Raises:
            ValueError: If tool not found or policy violation.
        """
        if name not in self._tools:
            raise ValueError(f"Tool not found: {name}")

        tool = self._tools[name]
        method = tool["method"]
        path = tool["path"]
        required = tool.get("input_schema", {}).get("required", []) or []
        missing = [field for field in required if field not in args]
        if missing:
            missing_list = ", ".join(missing)
            raise ValueError(f"Missing required fields: {missing_list}")

        # Enforce policy for write operations
        if method in {"POST", "PUT", "PATCH", "DELETE"} and self._guard:
            self._guard.enforce_write(name, confirm=confirm)

        # Pass all arguments - client will extract path params from them
        return self._client.request(method, path, json=args, params=args)
