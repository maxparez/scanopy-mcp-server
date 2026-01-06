"""Tool registry for scanning OpenAPI spec and registering MCP tools."""

from collections.abc import Mapping

# Standard HTTP methods we support (excluding OPTIONS, TRACE, etc.)
_STANDARD_METHODS = {"get", "head", "post", "put", "patch", "delete"}

# OpenAPI Path Item object fields that are not HTTP methods
_OPENAPI_PATH_METADATA = {
    "$ref",
    "summary",
    "description",
    "servers",
    "parameters",
}


class ToolRegistry:
    """Registry for MCP tools derived from OpenAPI specification."""

    def __init__(self, openapi_spec: Mapping, allowlist: set[str]):
        """Initialize the registry.

        Args:
            openapi_spec: OpenAPI specification as a dictionary.
            allowlist: Set of write operation IDs that are allowed.
        """
        self.spec = openapi_spec
        self.allowlist = allowlist
        self._components = self.spec.get("components", {}).get("schemas", {})

    def list_tools(self) -> dict:
        """List all available tools from the OpenAPI spec.

        Returns:
            Dictionary mapping operation IDs to tool metadata.
            Write operations not in allowlist are excluded.

        Raises:
            ValueError: If duplicate operationId is found.
        """
        tools = {}

        for path, ops in self.spec.get("paths", {}).items():
            for method, op in ops.items():
                # Skip OpenAPI metadata keys
                if method in _OPENAPI_PATH_METADATA or method.lower() not in _STANDARD_METHODS:
                    continue

                op_id = op.get("operationId")
                if not op_id:
                    continue

                # Filter write operations by allowlist FIRST
                is_write = method.lower() in {"post", "put", "patch", "delete"}
                if is_write and op_id not in self.allowlist:
                    continue

                # Check for duplicate operationId AFTER filtering
                if op_id in tools:
                    raise ValueError(f"Duplicate operationId: {op_id}")

                input_schema = self._build_input_schema(ops, op)

                tools[op_id] = {
                    "method": method.upper(),
                    "path": path,
                    "input_schema": input_schema,
                }

        return tools

    def _build_input_schema(self, path_item: Mapping, operation: Mapping) -> dict:
        """Build JSON schema for tool inputs from OpenAPI params and request body."""
        schema = {"type": "object", "properties": {}, "required": []}
        required = set()

        for param in self._collect_parameters(path_item, operation):
            name = param.get("name")
            if not name:
                continue
            param_schema = self._resolve_schema(param.get("schema", {}))
            schema["properties"][name] = param_schema or {}
            if param.get("required") or param.get("in") == "path":
                required.add(name)

        body_schema = self._get_request_body_schema(operation)
        if body_schema:
            body_schema = self._resolve_schema(body_schema)
            if body_schema.get("type") == "object" or "properties" in body_schema:
                for prop, prop_schema in body_schema.get("properties", {}).items():
                    schema["properties"][prop] = prop_schema
                for req in body_schema.get("required", []) or []:
                    required.add(req)
            else:
                schema["properties"]["body"] = body_schema

        if required:
            schema["required"] = sorted(required)
        else:
            schema.pop("required", None)

        return schema

    def _collect_parameters(self, path_item: Mapping, operation: Mapping) -> list[dict]:
        """Collect parameters from path item and operation, de-duplicated by name+in."""
        params = {}
        for source in (path_item.get("parameters", []), operation.get("parameters", [])):
            for param in source or []:
                key = (param.get("name"), param.get("in"))
                if key == (None, None):
                    continue
                params[key] = param
        return list(params.values())

    def _get_request_body_schema(self, operation: Mapping) -> dict | None:
        """Extract request body schema from OpenAPI operation if present."""
        body = operation.get("requestBody")
        if not body:
            return None
        content = body.get("content", {})
        if not content:
            return None
        if "application/json" in content:
            return content["application/json"].get("schema")
        # Fallback: first content type
        first = next(iter(content.values()), None)
        if not first:
            return None
        return first.get("schema")

    def _resolve_schema(self, schema: dict) -> dict:
        """Resolve local $ref schemas under #/components/schemas."""
        current = schema or {}
        while isinstance(current, dict) and "$ref" in current:
            ref = current.get("$ref", "")
            if not ref.startswith("#/components/schemas/"):
                break
            name = ref.split("/")[-1]
            current = self._components.get(name, {})
        return current or {}
