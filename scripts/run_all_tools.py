import argparse
import json
import os
import subprocess
import sys
from typing import Any


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--dry-run-writes", action="store_true")
    args = parser.parse_args()

    report: dict[str, Any] = {
        "tools": [],
        "results": {},
        "dry_run": bool(args.dry_run_writes),
    }

    def rpc_call(payload: dict) -> dict:
        proc = subprocess.run(
            [sys.executable, "-m", "scanopy_mcp.main"],
            input=(json.dumps(payload) + "\n").encode(),
            capture_output=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.decode())
        return json.loads(proc.stdout)

    def call_tool(name: str, arguments: dict) -> dict:
        req = {
            "jsonrpc": "2.0",
            "id": 1000 + len(report["results"]),
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        }
        return rpc_call(req)

    try:
        # tools/list
        resp = rpc_call({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}})
        tools = resp.get("result", {}).get("tools", [])
        report["tools"] = tools

        # build lookup for required fields
        required_by_tool = {}
        for tool in tools:
            name = tool["name"]
            schema = tool.get("inputSchema", {})
            required_by_tool[name] = schema.get("required", []) or []

        # cache some ids from list endpoints
        cache: dict[str, str] = {}
        list_map = {
            "list_networks": ("network_id",),
            "list_subnets": ("subnet_id",),
            "get_all_hosts": ("host_id",),
            "list_ports": ("port_id",),
            "list_services": ("service_id",),
            "list_discoveries": ("discovery_id",),
            "get_daemons": ("daemon_id",),
        }
        for list_tool, keys in list_map.items():
            if any(t["name"] == list_tool for t in tools):
                try:
                    resp = call_tool(list_tool, {})
                    text = resp.get("result", {}).get("content", [{}])[0].get("text", "[]")
                    data = json.loads(text)
                    items = data.get("data") if isinstance(data, dict) else data
                    if isinstance(items, list) and items:
                        first = items[0]
                        for key in keys:
                            cache[key] = first.get("id")
                except Exception:
                    continue

        # execute read tools
        for tool in tools:
            name = tool["name"]
            method = tool.get("description", "").split(" ")[0].upper()
            is_write = method in {"POST", "PUT", "PATCH", "DELETE"}
            args_payload: dict[str, Any] = {}

            required = required_by_tool.get(name, [])
            for field in required:
                if field in cache:
                    args_payload[field] = cache[field]
                elif field.endswith("_id") and field != "id":
                    args_payload[field] = cache.get(field)
                elif field == "id":
                    # choose any cached id
                    args_payload[field] = cache.get("host_id") or cache.get("network_id")
                elif field in {"tags", "interfaces", "ports", "services", "bindings"}:
                    args_payload[field] = []
                elif field in {"hidden"}:
                    args_payload[field] = False
                else:
                    args_payload[field] = ""

            if is_write and args_payload and args_payload.get("id") == "":
                args_payload.pop("id", None)

            if is_write and args.dry_run_writes:
                args_payload["dry_run"] = True

            if is_write and not args.dry_run_writes:
                continue

            try:
                call_tool(name, args_payload)
                report["results"][name] = {
                    "status": "ok",
                    "dry_run": bool(args_payload.get("dry_run")),
                }
            except Exception as exc:
                report["results"][name] = {"status": "error", "error": str(exc)}
    except Exception as exc:
        report["error"] = str(exc)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)


if __name__ == "__main__":
    main()
