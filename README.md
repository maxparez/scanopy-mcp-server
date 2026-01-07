# Scanopy MCP Server

Model Context Protocol (MCP) server that exposes [Scanopy](https://scanopy.com) API tools to AI assistants like Claude, Codex, and Gemini.

## What is this?

This MCP server allows AI assistants to interact with your Scanopy instance through a set of automatically generated tools based on Scanopy's OpenAPI specification. It provides:

- **Read operations**: List networks, sessions, devices, and more
- **Write operations**: Create, update, and delete resources (with safety confirmations)
- **Dry-run support**: Test write operations without making actual changes
- **Allowlist control**: Only expose the tools you need

## How it works

1. The server loads Scanopy's OpenAPI spec and generates MCP tools
2. Your AI assistant connects to the server via stdio
3. The assistant can call tools to interact with your Scanopy instance
4. Write operations require a confirmation string for safety

## Installation

Installation differs by platform. Choose your AI assistant below.

### Claude Code (CLI)

1. **Clone and set up the repository**:
```bash
git clone https://github.com/maxparez/scanopy-mcp-server.git
cd scanopy-mcp-server
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

2. **Configure your environment**:
Create a `.env` file in the repository root:
```bash
SCANOPY_BASE_URL=https://your-scanopy-instance.com
SCANOPY_API_KEY=scp_u_your_api_key_here
SCANOPY_CONFIRM_STRING=I understand this will modify Scanopy
```

3. **Register the MCP server**:
```bash
claude mcp add scanopy \
  --env SCANOPY_BASE_URL="$SCANOPY_BASE_URL" \
  --env SCANOPY_API_KEY="$SCANOPY_API_KEY" \
  --env SCANOPY_CONFIRM_STRING="$SCANOPY_CONFIRM_STRING" \
  -- $(pwd)/.venv/bin/python -m scanopy_mcp.main
```

4. **Verify installation**:
```bash
claude mcp list
```
You should see `scanopy` in the list of registered MCP servers.

### Codex CLI

1. **Set up the repository** (same as Claude Code steps 1-2 above)

2. **Register the MCP server**:
```bash
codex mcp add scanopy \
  --env SCANOPY_BASE_URL="$SCANOPY_BASE_URL" \
  --env SCANOPY_API_KEY="$SCANOPY_API_KEY" \
  --env SCANOPY_CONFIRM_STRING="$SCANOPY_CONFIRM_STRING" \
  -- $(pwd)/.venv/bin/python -m scanopy_mcp.main
```

3. **Verify installation**:
```bash
codex mcp list
codex mcp invoke --name tools/list
```

### Gemini CLI

1. **Set up the repository** (same as Claude Code steps 1-2 above)

2. **Register the MCP server**:
```bash
gemini mcp add scanopy \
  --scope user \
  --command $(pwd)/.venv/bin/python \
  --args -m scanopy_mcp.main
```

3. **Verify installation**:
```bash
gemini mcp list
```

## Using the Server

Once installed, you can interact with Scanopy through your AI assistant:

**In Claude Code**:
```
/mcp list                           # See all available tools
/mcp call list_networks             # Call a specific tool
```

**Example conversations**:
- "List all networks in my Scanopy instance"
- "Show me recent sessions for network XYZ"
- "Create a new network named 'Production' (with confirmation)"

## Safety Features

- **Write protection**: All write operations (POST, PUT, PATCH, DELETE) require a confirmation string
- **Dry-run mode**: Test write operations without making actual changes
- **Allowlist**: Configure which tools are exposed (via `scanopy_mcp/allowlist.py`)

## Development

### Running tests
```bash
pytest
```

### Running the server standalone
```bash
python -m scanopy_mcp.main
```

### Testing all tools
```bash
python3 scripts/run_all_tools.py --out logs/tool-report.json --dry-run-writes
```

## Configuration Reference

| Environment Variable | Required | Description |
|---------------------|----------|-------------|
| `SCANOPY_BASE_URL` | Yes | Your Scanopy instance URL (e.g., `https://scanopy.example.com`) |
| `SCANOPY_API_KEY` | Yes | Your Scanopy API key (starts with `scp_u_`) |
| `SCANOPY_CONFIRM_STRING` | Yes | Confirmation phrase for write operations |
| `SCANOPY_SESSION_ID` | No | Optional session ID for tracking |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT - See [LICENSE](LICENSE) for details.

## Security

Never commit your `.env` file or API keys to version control. See [SECURITY.md](SECURITY.md) for security best practices.
