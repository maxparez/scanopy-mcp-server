# Scanopy MCP Server - Usage Guide

## Environment Setup

Create a `.env` file in the project root:

```bash
SCANOPY_BASE_URL=http://192.168.2.200:60072
SCANOPY_API_KEY=your_api_key_here
SCANOPY_CONFIRM_STRING=I understand this will modify Scanopy
```

## Running the Server

```bash
python -m scanopy_mcp.main
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

3. **Call a read tool (list hosts):**
   ```bash
   echo '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "get_all_hosts", "arguments": {}}, "id": 3}' | python -m scanopy_mcp.main
   ```

4. **Call a read tool with query params (list networks with filter):**
   ```bash
   echo '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "list_networks", "arguments": {"limit": 10}}, "id": 4}' | python -m scanopy_mcp.main
   ```

5. **Call a write tool with path param (get host by ID):**
   ```bash
   echo '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "get_host_by_id", "arguments": {"id": "123"}}, "id": 5}' | python -m scanopy_mcp.main
   ```

6. **Call a write tool (create discovery) with confirm:**
   ```bash
   echo '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "create_discovery", "arguments": {"target": "192.168.1.0/24", "confirm": "I understand this will modify Scanopy"}}, "id": 6}' | python -m scanopy_mcp.main
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
