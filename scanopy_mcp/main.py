"""Main entrypoint for Scanopy MCP server."""

import dotenv

from scanopy_mcp.allowlist import WRITE_ALLOWLIST
from scanopy_mcp.config import load_config
from scanopy_mcp.stdio_server import MCPStdioServer


def main() -> None:
    """Run the Scanopy MCP server."""
    # Load .env file if exists
    dotenv.load_dotenv()

    # Load configuration from environment
    config = load_config()

    # Create stdio server
    openapi_url = f"{config.base_url}/openapi.json"
    server = MCPStdioServer(
        config=config,
        openapi_url=openapi_url,
        allowlist=WRITE_ALLOWLIST,
    )

    # Run stdio server
    server.run()


if __name__ == "__main__":
    main()
