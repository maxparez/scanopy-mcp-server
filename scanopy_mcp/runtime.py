"""Runtime builder for wiring all MCP server components."""

from scanopy_mcp.client import ScanopyClient
from scanopy_mcp.policy import PolicyGuard
from scanopy_mcp.server import ScanopyMCPServer
from scanopy_mcp.tool_registry import ToolRegistry


def build_runtime(
    openapi_spec: dict,
    allowlist: set[str],
    base_url: str = "",
    api_key: str = "",
    confirm_string: str = "",
) -> ScanopyMCPServer:
    """Build a complete MCP server runtime with all components wired.

    Args:
        openapi_spec: OpenAPI specification dictionary.
        allowlist: Set of write operation IDs that are allowed.
        base_url: Base URL for Scanopy API.
        api_key: API key for authentication.
        confirm_string: Required confirmation string for writes.

    Returns:
        Configured ScanopyMCPServer instance.
    """
    # Register tools from OpenAPI spec
    tools = ToolRegistry(openapi_spec, allowlist=allowlist).list_tools()

    # Create HTTP client
    client = ScanopyClient(base_url=base_url, api_key=api_key)

    # Create policy guard
    guard = PolicyGuard(allowlist=allowlist, confirm_string=confirm_string)

    # Wire up server
    return ScanopyMCPServer(tools=tools, client=client, guard=guard)
