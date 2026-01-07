# Scanopy MCP Server

Model Context Protocol (MCP) server for Scanopy API.

## Installation

```bash
pip install -e ".[dev]"
```

## Configuration

Create a `.env` file:

```bash
SCANOPY_BASE_URL=https://scanopy.example.com
SCANOPY_API_KEY=scp_u_...
SCANOPY_CONFIRM_STRING=I understand this will modify Scanopy
```

## Running

```bash
python -m scanopy_mcp.main
```

## Testing

```bash
pytest
```

## Registering the MCP server with CLI clients

Set the same four environment variables (`SCANOPY_BASE_URL`, `SCANOPY_API_KEY`, `SCANOPY_CONFIRM_STRING`, `SCANOPY_SESSION_ID`) before using any CLI. Each command below registers the `scanopy` MCP entrypoint using the `.venv` interpreter installed in this repo.

### Claude CLI

```bash
claude mcp add scanopy \
  --env SCANOPY_BASE_URL="$SCANOPY_BASE_URL" \
  --env SCANOPY_API_KEY="$SCANOPY_API_KEY" \
  --env SCANOPY_CONFIRM_STRING="$SCANOPY_CONFIRM_STRING" \
  --env SCANOPY_SESSION_ID="$SCANOPY_SESSION_ID" \
  -- /home/pavel/vyvoj_sw/scanopy-mcp-server/.venv/bin/python -m scanopy_mcp.main
claude mcp list
```

Once registered, run `/mcp list` in Claude CLI to see the tool catalog, then `/mcp call` for any tool.

### Codex CLI

```bash
codex mcp add scanopy \
  --env SCANOPY_BASE_URL="$SCANOPY_BASE_URL" \
  --env SCANOPY_API_KEY="$SCANOPY_API_KEY" \
  --env SCANOPY_CONFIRM_STRING="$SCANOPY_CONFIRM_STRING" \
  --env SCANOPY_SESSION_ID="$SCANOPY_SESSION_ID" \
  -- /home/pavel/vyvoj_sw/scanopy-mcp-server/.venv/bin/python -m scanopy_mcp.main
codex mcp list
```

Use `codex mcp invoke --name tools/list` to confirm it responds, then switch to any write tool with `--dry-run`.

### Gemini CLI

```bash
gemini mcp add scanopy \
  --scope user \
  --command /home/pavel/vyvoj_sw/scanopy-mcp-server/.venv/bin/python \
  --args -m scanopy_mcp.main
gemini mcp list
```

Interact with Gemini by invoking `/mcp list` and `/mcp call --name list_networks`. Your CLI on the local machine will proxy requests to this MCP server.

Need to sanity-check everything? Run `python3 scripts/run_all_tools.py --out logs/tool-report.json --dry-run-writes` to document the registered tools via dry-run.
