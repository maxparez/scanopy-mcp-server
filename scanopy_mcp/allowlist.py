"""Write operation allowlist for Scanopy MCP A-D scope."""

# Write operations that are allowed to be called via MCP
# Format: "resource.action" matching OpenAPI operationId
WRITE_ALLOWLIST = {
    # Discovery operations
    "discoveries.create",
    "discoveries.start",
    "discoveries.stop",
    # Host operations
    "hosts.update",
    "hosts.merge",
    # Network/subnet operations
    "networks.create",
    "networks.update",
    "subnets.create",
    "subnets.update",
    # Service/port operations
    "services.update",
    "ports.update",
}
