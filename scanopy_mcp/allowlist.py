"""Write operation allowlist for Scanopy MCP A-D scope."""

# Write operations that are allowed to be called via MCP
# Format: actual OpenAPI operationId (snake_case)
WRITE_ALLOWLIST = {
    # Discovery operations
    "create_discovery",
    "cancel_discovery",
    "update_discovery",
    # Host operations
    "update_host",
    "consolidate_hosts",
    # Network/subnet operations
    "create_network",
    "update_network",
    "create_subnet",
    "update_subnet",
    # Service/port operations
    "update_service",
    "update_port",
}
