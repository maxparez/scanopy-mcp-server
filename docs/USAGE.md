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

1. **List available tools:**
   ```bash
   # Should return JSON with all available tools
   echo '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' | python -m scanopy_mcp.main
   ```

2. **Call a read tool:**
   ```bash
   # Example: list hosts
   echo '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "hosts.list", "arguments": {}}, "id": 2}' | python -m scanopy_mcp.main
   ```

3. **Call a write tool (with confirm):**
   ```bash
   # Example: start discovery
   echo '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "discoveries.start", "arguments": {"target": "192.168.1.0/24"}, "confirm": "I understand this will modify Scanopy"}, "id": 3}' | python -m scanopy_mcp.main
   ```

## Write Operations

Only allowlisted write operations are permitted:

- `discoveries.create`, `discoveries.start`, `discoveries.stop`
- `hosts.update`, `hosts.merge`
- `networks.create`, `networks.update`
- `subnets.create`, `subnets.update`
- `services.update`, `ports.update`

All write operations require the exact `SCANOPY_CONFIRM_STRING` to be provided.
