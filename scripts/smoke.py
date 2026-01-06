import argparse
import json
import subprocess
import sys
import time


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    log = {"started_at": time.time(), "steps": []}

    try:
        steps = [
            {
                "name": "initialize",
                "req": {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            },
            {
                "name": "tools/list",
                "req": {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            },
        ]

        if args.dry_run:
            for step in steps:
                log["steps"].append({"name": step["name"], "status": "dry-run"})
        else:
            for step in steps:
                proc = subprocess.run(
                    [sys.executable, "-m", "scanopy_mcp.main"],
                    input=(json.dumps(step["req"]) + "\n").encode(),
                    capture_output=True,
                )
                log["steps"].append(
                    {
                        "name": step["name"],
                        "status": "ok" if proc.returncode == 0 else "error",
                        "stdout": proc.stdout.decode(),
                        "stderr": proc.stderr.decode(),
                    }
                )
    finally:
        with open(args.log, "w", encoding="utf-8") as f:
            json.dump(log, f, indent=2)


if __name__ == "__main__":
    main()
