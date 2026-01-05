# Scanopy MCP Server Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a reliable, write-capable MCP server for Scanopy (A–D scope) driven by OpenAPI with strong guardrails.

**Architecture:** OpenAPI loader generates tool schema; allowlisted write tools only; HTTP client with strict auth + timeouts; policy guard enforces confirm + dry_run; MCP server exposes tools/list and tools/call.

**Tech Stack:** Python 3.11+, httpx, pydantic, pytest, ruff, mcp (Python SDK) or equivalent minimal MCP server.

---

### Task 1: Worktree + skeleton

**Files:**
- Create: `.gitignore`
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `.env.example`
- Create: `scanopy_mcp/__init__.py`
- Create: `scanopy_mcp/config.py`
- Create: `tests/__init__.py`

**Step 1: Write the failing test**

```python
# tests/test_config.py
import os
import importlib

def test_config_requires_base_url_and_key(monkeypatch):
    monkeypatch.delenv("SCANOPY_BASE_URL", raising=False)
    monkeypatch.delenv("SCANOPY_API_KEY", raising=False)
    cfg = importlib.import_module("scanopy_mcp.config")
    try:
        cfg.load_config()
        assert False, "expected ValueError"
    except ValueError:
        assert True
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py::test_config_requires_base_url_and_key -v`
Expected: FAIL with "ModuleNotFoundError" or missing `load_config`

**Step 3: Write minimal implementation**

```python
# scanopy_mcp/config.py
from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Config:
    base_url: str
    api_key: str
    confirm_string: str


def load_config() -> Config:
    base_url = os.getenv("SCANOPY_BASE_URL")
    api_key = os.getenv("SCANOPY_API_KEY")
    confirm_string = os.getenv("SCANOPY_CONFIRM_STRING", "I understand this will modify Scanopy")
    if not base_url or not api_key:
        raise ValueError("SCANOPY_BASE_URL and SCANOPY_API_KEY are required")
    return Config(base_url=base_url.rstrip("/"), api_key=api_key, confirm_string=confirm_string)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py::test_config_requires_base_url_and_key -v`
Expected: PASS

**Step 5: Commit**

```bash
git add .gitignore pyproject.toml README.md .env.example scanopy_mcp/__init__.py scanopy_mcp/config.py tests/__init__.py tests/test_config.py
git commit -m "chore: bootstrap scanopy mcp skeleton"
```

---

### Task 2: OpenAPI loader + schema cache

**Files:**
- Create: `scanopy_mcp/openapi_loader.py`
- Test: `tests/test_openapi_loader.py`

**Step 1: Write the failing test**

```python
# tests/test_openapi_loader.py
from scanopy_mcp.openapi_loader import OpenAPILoader

def test_loads_openapi_and_paths(requests_mock):
    url = "http://scanopy.local/openapi.json"
    requests_mock.get(url, json={"openapi": "3.0.0", "paths": {"/api/v1/x": {"get": {}}}})
    loader = OpenAPILoader(url=url)
    spec = loader.load()
    assert "/api/v1/x" in spec["paths"]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_openapi_loader.py::test_loads_openapi_and_paths -v`
Expected: FAIL with missing `OpenAPILoader`

**Step 3: Write minimal implementation**

```python
# scanopy_mcp/openapi_loader.py
import time
import requests

class OpenAPILoader:
    def __init__(self, url: str, ttl_seconds: int = 600):
        self.url = url
        self.ttl_seconds = ttl_seconds
        self._cache = None
        self._loaded_at = 0.0

    def load(self):
        now = time.time()
        if self._cache and (now - self._loaded_at) < self.ttl_seconds:
            return self._cache
        resp = requests.get(self.url, timeout=5)
        resp.raise_for_status()
        self._cache = resp.json()
        self._loaded_at = now
        return self._cache
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_openapi_loader.py::test_loads_openapi_and_paths -v`
Expected: PASS

**Step 5: Commit**

```bash
git add scanopy_mcp/openapi_loader.py tests/test_openapi_loader.py
git commit -m "feat: add openapi loader with ttl cache"
```

---

### Task 3: Policy guard (allowlist + confirm + dry_run)

**Files:**
- Create: `scanopy_mcp/policy.py`
- Test: `tests/test_policy.py`

**Step 1: Write the failing test**

```python
# tests/test_policy.py
from scanopy_mcp.policy import PolicyGuard


def test_write_requires_confirm():
    guard = PolicyGuard(allowlist={"discovery.start"}, confirm_string="CONFIRM")
    try:
        guard.enforce_write("discovery.start", confirm=None)
        assert False, "expected ValueError"
    except ValueError:
        assert True
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_policy.py::test_write_requires_confirm -v`
Expected: FAIL with missing `PolicyGuard`

**Step 3: Write minimal implementation**

```python
# scanopy_mcp/policy.py
class PolicyGuard:
    def __init__(self, allowlist: set[str], confirm_string: str):
        self.allowlist = allowlist
        self.confirm_string = confirm_string

    def enforce_write(self, tool_name: str, confirm: str | None):
        if tool_name not in self.allowlist:
            raise ValueError("tool not allowlisted")
        if confirm != self.confirm_string:
            raise ValueError("invalid confirm string")
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_policy.py::test_write_requires_confirm -v`
Expected: PASS

**Step 5: Commit**

```bash
git add scanopy_mcp/policy.py tests/test_policy.py
git commit -m "feat: add write policy guard"
```

---

### Task 4: Scanopy HTTP client (auth + timeouts)

**Files:**
- Create: `scanopy_mcp/client.py`
- Test: `tests/test_client.py`

**Step 1: Write the failing test**

```python
# tests/test_client.py
from scanopy_mcp.client import ScanopyClient


def test_auth_header_is_bearer():
    client = ScanopyClient(base_url="http://x", api_key="scp_u_test")
    assert client._headers()["Authorization"].startswith("Bearer ")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_client.py::test_auth_header_is_bearer -v`
Expected: FAIL with missing `ScanopyClient`

**Step 3: Write minimal implementation**

```python
# scanopy_mcp/client.py
import httpx

class ScanopyClient:
    def __init__(self, base_url: str, api_key: str, timeout_s: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_s = timeout_s

    def _headers(self):
        return {"Authorization": f"Bearer {self.api_key}"}

    def request(self, method: str, path: str, json: dict | None = None):
        url = f"{self.base_url}{path}"
        with httpx.Client(timeout=self.timeout_s) as client:
            resp = client.request(method, url, headers=self._headers(), json=json)
            resp.raise_for_status()
            return resp.json()
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_client.py::test_auth_header_is_bearer -v`
Expected: PASS

**Step 5: Commit**

```bash
git add scanopy_mcp/client.py tests/test_client.py
git commit -m "feat: add scanopy http client"
```

---

### Task 5: Tool registry from OpenAPI (read + allowlisted write)

**Files:**
- Create: `scanopy_mcp/tool_registry.py`
- Test: `tests/test_tool_registry.py`

**Step 1: Write the failing test**

```python
# tests/test_tool_registry.py
from scanopy_mcp.tool_registry import ToolRegistry


def test_registry_filters_write_ops():
    spec = {"paths": {"/api/v1/hosts": {"get": {"operationId": "hosts.list"}, "post": {"operationId": "hosts.create"}}}}
    reg = ToolRegistry(spec, allowlist={"hosts.create"})
    tools = reg.list_tools()
    assert "hosts.list" in tools
    assert "hosts.create" in tools
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_tool_registry.py::test_registry_filters_write_ops -v`
Expected: FAIL with missing `ToolRegistry`

**Step 3: Write minimal implementation**

```python
# scanopy_mcp/tool_registry.py
class ToolRegistry:
    def __init__(self, openapi_spec: dict, allowlist: set[str]):
        self.spec = openapi_spec
        self.allowlist = allowlist

    def list_tools(self):
        tools = {}
        for path, ops in self.spec.get("paths", {}).items():
            for method, op in ops.items():
                op_id = op.get("operationId")
                if not op_id:
                    continue
                is_write = method.lower() in {"post", "put", "patch", "delete"}
                if is_write and op_id not in self.allowlist:
                    continue
                tools[op_id] = {"method": method.upper(), "path": path}
        return tools
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_tool_registry.py::test_registry_filters_write_ops -v`
Expected: PASS

**Step 5: Commit**

```bash
git add scanopy_mcp/tool_registry.py tests/test_tool_registry.py
git commit -m "feat: add tool registry from openapi"
```

---

### Task 6: MCP server wiring (tools/list + tools/call)

**Files:**
- Create: `scanopy_mcp/server.py`
- Create: `scanopy_mcp/main.py`
- Test: `tests/test_server_tools.py`

**Step 1: Write the failing test**

```python
# tests/test_server_tools.py
from scanopy_mcp.server import ScanopyMCPServer


def test_tools_list_returns_registered_tools():
    server = ScanopyMCPServer(tools={"x.y": {"method": "GET", "path": "/api/v1/x"}})
    out = server.tools_list()
    assert "x.y" in out
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_server_tools.py::test_tools_list_returns_registered_tools -v`
Expected: FAIL with missing `ScanopyMCPServer`

**Step 3: Write minimal implementation**

```python
# scanopy_mcp/server.py
from scanopy_mcp.client import ScanopyClient
from scanopy_mcp.policy import PolicyGuard

class ScanopyMCPServer:
    def __init__(self, tools: dict, client: ScanopyClient | None = None, guard: PolicyGuard | None = None):
        self._tools = tools
        self._client = client
        self._guard = guard

    def tools_list(self):
        return self._tools

    def tools_call(self, name: str, args: dict, confirm: str | None = None):
        tool = self._tools[name]
        method = tool["method"]
        path = tool["path"]
        if method in {"POST", "PUT", "PATCH", "DELETE"} and self._guard:
            self._guard.enforce_write(name, confirm=confirm)
        return self._client.request(method, path, json=args)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_server_tools.py::test_tools_list_returns_registered_tools -v`
Expected: PASS

**Step 5: Commit**

```bash
git add scanopy_mcp/server.py scanopy_mcp/main.py tests/test_server_tools.py
git commit -m "feat: add mcp server core"
```

---

### Task 7: CLI entrypoint + env wiring

**Files:**
- Modify: `scanopy_mcp/main.py`
- Modify: `pyproject.toml`
- Create: `scanopy_mcp/runtime.py`
- Test: `tests/test_runtime.py`

**Step 1: Write the failing test**

```python
# tests/test_runtime.py
from scanopy_mcp.runtime import build_runtime


def test_runtime_builds_with_allowlist():
    runtime = build_runtime(openapi_spec={"paths": {}}, allowlist=set())
    assert runtime is not None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_runtime.py::test_runtime_builds_with_allowlist -v`
Expected: FAIL with missing `build_runtime`

**Step 3: Write minimal implementation**

```python
# scanopy_mcp/runtime.py
from scanopy_mcp.client import ScanopyClient
from scanopy_mcp.policy import PolicyGuard
from scanopy_mcp.tool_registry import ToolRegistry
from scanopy_mcp.server import ScanopyMCPServer


def build_runtime(openapi_spec: dict, allowlist: set[str], base_url: str = "", api_key: str = "", confirm_string: str = ""):
    tools = ToolRegistry(openapi_spec, allowlist=allowlist).list_tools()
    client = ScanopyClient(base_url=base_url, api_key=api_key)
    guard = PolicyGuard(allowlist=allowlist, confirm_string=confirm_string)
    return ScanopyMCPServer(tools=tools, client=client, guard=guard)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_runtime.py::test_runtime_builds_with_allowlist -v`
Expected: PASS

**Step 5: Commit**

```bash
git add scanopy_mcp/runtime.py tests/test_runtime.py scanopy_mcp/main.py pyproject.toml
git commit -m "feat: add runtime wiring"
```

---

### Task 8: Guarded write allowlist for A–D tools

**Files:**
- Create: `scanopy_mcp/allowlist.py`
- Test: `tests/test_allowlist.py`

**Step 1: Write the failing test**

```python
# tests/test_allowlist.py
from scanopy_mcp.allowlist import WRITE_ALLOWLIST

def test_allowlist_contains_discovery_write():
    assert any("discover" in item for item in WRITE_ALLOWLIST)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_allowlist.py::test_allowlist_contains_discovery_write -v`
Expected: FAIL with missing `WRITE_ALLOWLIST`

**Step 3: Write minimal implementation**

```python
# scanopy_mcp/allowlist.py
WRITE_ALLOWLIST = {
    # discovery
    "discoveries.create",
    "discoveries.start",
    # hosts
    "hosts.update",
    "hosts.merge",
    # networks/subnets
    "networks.create",
    "networks.update",
    "subnets.create",
    "subnets.update",
    # services/ports
    "services.update",
    "ports.update",
}
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_allowlist.py::test_allowlist_contains_discovery_write -v`
Expected: PASS

**Step 5: Commit**

```bash
git add scanopy_mcp/allowlist.py tests/test_allowlist.py
git commit -m "feat: add write allowlist for a-d scope"
```

---

### Task 9: Minimal MCP transport (stdio) or SDK wiring

**Files:**
- Modify: `scanopy_mcp/main.py`
- Create: `scanopy_mcp/transport.py`
- Test: `tests/test_transport.py`

**Step 1: Write the failing test**

```python
# tests/test_transport.py
from scanopy_mcp.transport import build_tools_response

def test_tools_list_payload():
    payload = build_tools_response({"x.y": {"method": "GET", "path": "/x"}})
    assert "x.y" in payload
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_transport.py::test_tools_list_payload -v`
Expected: FAIL with missing `build_tools_response`

**Step 3: Write minimal implementation**

```python
# scanopy_mcp/transport.py
import json

def build_tools_response(tools: dict) -> str:
    return json.dumps({"tools": tools})
```

**Note:** If the official Python MCP SDK is available, replace this minimal helper with real MCP `tools/list` and `tools/call` handlers and wire `scanopy_mcp.server.ScanopyMCPServer` into the SDK's transport.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_transport.py::test_tools_list_payload -v`
Expected: PASS

**Step 5: Commit**

```bash
git add scanopy_mcp/transport.py tests/test_transport.py scanopy_mcp/main.py
git commit -m "feat: add minimal transport helpers"
```

---

### Task 10: Smoke test guide + docs

**Files:**
- Modify: `README.md`
- Create: `docs/USAGE.md`

**Step 1: Write the failing test**

```python
# tests/test_docs.py
import pathlib

def test_usage_docs_exist():
    assert pathlib.Path("docs/USAGE.md").exists()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_docs.py::test_usage_docs_exist -v`
Expected: FAIL with missing docs

**Step 3: Write minimal implementation**

```markdown
# docs/USAGE.md

## Environment
- SCANOPY_BASE_URL=http://192.168.2.200:60072
- SCANOPY_API_KEY=Bearer scp_u_...
- SCANOPY_CONFIRM_STRING=I understand this will modify Scanopy

## Smoke test
- Call tools/list
- Call a read tool
- Call one write tool with confirm string
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_docs.py::test_usage_docs_exist -v`
Expected: PASS

**Step 5: Commit**

```bash
git add README.md docs/USAGE.md tests/test_docs.py
git commit -m "docs: add usage and smoke test guide"
```
