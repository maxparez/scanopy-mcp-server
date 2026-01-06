import json
import subprocess
import sys


def test_tool_enumeration(tmp_path):
    out = tmp_path / "report.json"
    subprocess.run([sys.executable, "scripts/run_all_tools.py", "--out", str(out)], capture_output=True)
    data = json.loads(out.read_text())
    assert "tools" in data

def test_read_tools_reported(tmp_path):
    out = tmp_path / "report.json"
    subprocess.run(
        [sys.executable, "scripts/run_all_tools.py", "--out", str(out), "--dry-run-writes"],
        capture_output=True,
    )
    data = json.loads(out.read_text())
    assert "results" in data

def test_write_tools_dry_run(tmp_path):
    out = tmp_path / "report.json"
    subprocess.run(
        [sys.executable, "scripts/run_all_tools.py", "--out", str(out), "--dry-run-writes"],
        capture_output=True,
    )
    data = json.loads(out.read_text())
    assert data.get("dry_run") is True
