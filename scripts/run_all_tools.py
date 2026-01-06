import argparse
import json
import subprocess
import sys


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    report = {"tools": []}

    # tools/list
    req = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
    proc = subprocess.run(
        [sys.executable, "-m", "scanopy_mcp.main"],
        input=(json.dumps(req) + "\n").encode(),
        capture_output=True,
    )
    if proc.returncode == 0 and proc.stdout:
        resp = json.loads(proc.stdout)
        tools = resp.get("result", {}).get("tools", [])
        report["tools"] = tools
    else:
        report["error"] = proc.stderr.decode()

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)


if __name__ == "__main__":
    main()
