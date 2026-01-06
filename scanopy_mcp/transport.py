"""MCP transport helpers for building protocol payloads."""

import json


def build_tools_response(tools: dict) -> str:
    """Build an MCP tools/list response payload.

    Args:
        tools: Dictionary of tool metadata.

    Returns:
        JSON string of tools list.
    """
    return json.dumps({"tools": tools})


def build_call_response(result: dict) -> str:
    """Build an MCP tools/call response payload.

    Args:
        result: Tool execution result.

    Returns:
        JSON string of call result.
    """
    return json.dumps({"result": result})
