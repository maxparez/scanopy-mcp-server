# Scanopy MCP Server - Usage Guide

## Environment Setup

Create a `.env` file in the project root:

```bash
SCANOPY_BASE_URL=https://scanopy.example.com
SCANOPY_API_KEY=your_api_key_here
SCANOPY_CONFIRM_STRING=I understand this will modify Scanopy
```

## Running the Server

```bash
python3 -m scanopy_mcp.main
```

## Smoke Test

1. **Initialize server:**
   ```bash
   echo '{"jsonrpc": "2.0", "method": "initialize", "id": 1, "params": {}}' | python -m scanopy_mcp.main
   ```

2. **List available tools:**
   ```bash
   echo '{"jsonrpc": "2.0", "method": "tools/list", "id": 2}' | python -m scanopy_mcp.main
   ```
   Use the returned `name` fields as tool names. These are the OpenAPI `operationId` values.

3. **Call a read tool (list hosts):**
   ```bash
   echo '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "get_all_hosts", "arguments": {}}, "id": 3}' | python -m scanopy_mcp.main
   ```

4. **Call a read tool with query params (list networks with filter):**
   ```bash
   echo '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "list_networks", "arguments": {"limit": 10}}, "id": 4}' | python -m scanopy_mcp.main
   ```

5. **Call a read tool with path param (get host by ID):**
   ```bash
   echo '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "get_host_by_id", "arguments": {"id": "123"}}, "id": 5}' | python -m scanopy_mcp.main
   ```

6. **Call a write tool (create discovery) with confirm:**
   ```bash
   echo '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "create_discovery", "arguments": {"name":"MCP_TEST","daemon_id":"DAEMON_ID","network_id":"NETWORK_ID","discovery_type":{"type":"Network","subnet_ids":null,"host_naming_fallback":"BestService"},"run_type":{"type":"AdHoc"},"tags":[],"confirm": "I understand this will modify Scanopy"}}, "id": 6}' | python -m scanopy_mcp.main
   ```

## Write Operations

Only allowlisted write operations are permitted:

- **Discovery:** `create_discovery`, `cancel_discovery`, `update_discovery`
- **Hosts:** `update_host`, `consolidate_hosts`
- **Networks:** `create_network`, `update_network`
- **Subnets:** `create_subnet`, `update_subnet`
- **Services:** `update_service`
- **Ports:** `update_port`

All write operations require the exact `SCANOPY_CONFIRM_STRING` to be provided in the `arguments` dict.

## Notes / Future Work

- `cancel_discovery` requires an **active session_id**. Creating an AdHoc discovery does not guarantee an active session.
  To support cancel, the MCP server likely needs a start/run workflow (or a way to surface active session IDs).

## Real Server Findings (Jan 6, 2026)

- `list_networks` does **not** expose pagination/filter params in OpenAPI (empty parameters list).
- `create_subnet` requires `network_id`, `subnet_type`, `source`, and `tags`. Sending `id=""` fails (invalid UUID).
  Omit `id` entirely on create.
- Creating a subnet with an existing CIDR returns the existing subnet (idempotent behavior).
- `create_network` with API key returns 403; session-cookie calls require `organization_id`.
  Delete network works via session cookie even though DELETE is not in OpenAPI.
- `create_discovery` requires **object** shapes for `discovery_type` and `run_type` (strings like `"ICMP"` fail with 422).
  `name` and `tags` are required (tags can be empty list).
- `cancel_discovery` returns 404 for invalid/unknown `session_id`.
- `update_host` syncs children; only send empty `interfaces/ports/services` for hosts that actually have none.
- `update_port` and `update_service` accept full objects (including readOnly fields) without errors.
- `consolidate_hosts` is destructive (deletes `other_host`) and should be run only with explicit operator approval.

## Path Parameters

For operations with path parameters (e.g., `/api/v1/hosts/{id}`), include the param in `arguments`:

```json
{
  "name": "get_host_by_id",
  "arguments": {"id": "123"}
}
```

## Query Parameters (GET requests)

For GET requests, query parameters are passed in `arguments`:

```json
{
  "name": "get_all_hosts",
  "arguments": {"limit": 10, "offset": 0}
}
```

## PUT/PATCH Body Requirements

Some update endpoints require the path `id` **and** the same `id` in the JSON body.
Example for `update_host`:

```json
{
  "name": "update_host",
  "arguments": {
    "id": "30520c3b-617d-4f95-a14f-45f029686185",
    "name": "switch netgear GS108E",
    "hidden": false,
    "tags": [],
    "confirm": "I understand this will modify Scanopy"
  }
}
```

## Discovery Request Shapes

The Scanopy API expects **object** shapes for `discovery_type` and `run_type`:

```json
{
  "name": "MCP_TEST",
  "daemon_id": "DAEMON_ID",
  "network_id": "NETWORK_ID",
  "discovery_type": {
    "type": "Network",
    "subnet_ids": null,
    "host_naming_fallback": "BestService"
  },
  "run_type": {
    "type": "AdHoc"
  },
  "tags": []
}
```
