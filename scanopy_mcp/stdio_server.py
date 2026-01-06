"""JSON-RPC stdio server for MCP protocol."""

import json
import sys

from scanopy_mcp.config import Config
from scanopy_mcp.openapi_loader import OpenAPILoader
from scanopy_mcp.server import ScanopyMCPServer


class MCPStdioServer:
    """JSON-RPC stdio server that implements MCP protocol."""

    def __init__(
        self,
        config: Config,
        openapi_url: str,
        allowlist: set[str],
        openapi_spec: dict | None = None,
    ):
        """Initialize the stdio server.

        Args:
            config: Configuration for Scanopy API.
            openapi_url: URL to fetch OpenAPI spec from.
            allowlist: Set of write operation IDs that are allowed.
            openapi_spec: Optional pre-loaded OpenAPI spec (for testing).
        """
        self.config = config
        self.openapi_url = openapi_url
        self.allowlist = allowlist
        self.openapi_spec = openapi_spec

        # Lazy initialization of runtime
        self._runtime: ScanopyMCPServer | None = None

    def _get_runtime(self) -> ScanopyMCPServer:
        """Get or create the MCP server runtime.

        Returns:
            Configured ScanopyMCPServer instance.
        """
        if self._runtime is None:
            # Load OpenAPI spec
            if self.openapi_spec is None:
                loader = OpenAPILoader(url=self.openapi_url)
                spec = loader.load()
            else:
                spec = self.openapi_spec

            # Import runtime builder locally to avoid circular imports
            from scanopy_mcp.runtime import build_runtime

            self._runtime = build_runtime(
                openapi_spec=spec,
                allowlist=self.allowlist,
                base_url=self.config.base_url,
                api_key=self.config.api_key,
                confirm_string=self.config.confirm_string,
            )

        return self._runtime

    def handle_request(self, request: dict) -> dict:
        """Handle a single JSON-RPC request.

        Args:
            request: JSON-RPC request dictionary.

        Returns:
            JSON-RPC response dictionary.
        """
        method = request.get("method")
        params = request.get("params", {})
        req_id = request.get("id")

        try:
            if method == "initialize":
                return self._handle_initialize(req_id, params)
            elif method == "tools/list":
                return self._handle_tools_list(req_id, params)
            elif method == "tools/call":
                return self._handle_tools_call(req_id, params)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32603, "message": str(e)},
            }

    def _handle_initialize(self, req_id: int, params: dict) -> dict:
        """Handle initialize request.

        Returns:
            JSON-RPC response with server info and capabilities.
        """
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "serverInfo": {
                    "name": "scanopy-mcp-server",
                    "version": "0.1.0",
                },
                "capabilities": {
                    "tools": {},
                },
            },
        }

    def _handle_tools_list(self, req_id: int, params: dict) -> dict:
        """Handle tools/list request.

        Returns:
            JSON-RPC response with list of available tools.
        """
        runtime = self._get_runtime()
        tools = runtime.tools_list()

        # Convert to MCP tool format
        mcp_tools = []
        for name, meta in tools.items():
            method = meta.get("method", "GET")
            is_write = method in {"POST", "PUT", "PATCH", "DELETE"}

            base_schema = meta.get("input_schema") or {"type": "object", "properties": {}}
            # Copy schema to avoid mutating registry data
            input_schema = {
                "type": "object",
                "properties": dict(base_schema.get("properties", {})),
            }
            required = set(base_schema.get("required", []) or [])

            if is_write:
                input_schema["properties"]["confirm"] = {
                    "type": "string",
                    "description": "Confirmation string for write operations",
                }
                required.add("confirm")

            if required:
                input_schema["required"] = sorted(required)

            mcp_tools.append(
                {
                    "name": name,
                    "description": f"{meta['method']} {meta['path']}",
                    "inputSchema": input_schema,
                }
            )

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": mcp_tools},
        }

    def _handle_tools_call(self, req_id: int, params: dict) -> dict:
        """Handle tools/call request.

        Args:
            params: Must contain 'name' and optionally 'arguments'.

        Returns:
            JSON-RPC response with tool result.

        Raises:
            ValueError: If tool name is missing or tool not found.
        """
        name = params.get("name")
        if not name:
            raise ValueError("Missing 'name' in request")

        arguments = params.get("arguments", {})
        confirm = arguments.pop("confirm", None)

        runtime = self._get_runtime()
        result = runtime.tools_call(name, arguments, confirm=confirm)

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(result)}],
            },
        }

    def run(self) -> None:
        """Run the stdio server.

        Reads JSON-RPC requests from stdin and writes responses to stdout.
        """
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                request = json.loads(line)
                response = self.handle_request(request)
                print(json.dumps(response))
                sys.stdout.flush()
            except json.JSONDecodeError:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": "Parse error"},
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
