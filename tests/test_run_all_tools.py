import json
import subprocess
import sys


def test_tool_enumeration(tmp_path):
    out = tmp_path / "report.json"
    subprocess.run([sys.executable, "scripts/run_all_tools.py", "--out", str(out)], capture_output=True)
    data = json.loads(out.read_text())
    assert "tools" in data
