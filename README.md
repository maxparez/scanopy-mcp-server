# Scanopy MCP Server

Model Context Protocol (MCP) server for Scanopy API.

## Installation

```bash
pip install -e ".[dev]"
```

## Configuration

Create a `.env` file:

```bash
SCANOPY_BASE_URL=http://192.168.2.200:60072
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
