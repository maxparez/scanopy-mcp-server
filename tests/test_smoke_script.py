import json
import subprocess
import sys


def test_smoke_log_written(tmp_path, monkeypatch):
    monkeypatch.setenv("SCANOPY_BASE_URL", "http://example")
    monkeypatch.setenv("SCANOPY_API_KEY", "key")
    out = tmp_path / "smoke.json"
    subprocess.run([sys.executable, "scripts/smoke.py", "--log", str(out)], capture_output=True)
    assert out.exists()

def test_smoke_records_steps(tmp_path, monkeypatch):
    monkeypatch.setenv("SCANOPY_BASE_URL", "http://example")
    monkeypatch.setenv("SCANOPY_API_KEY", "key")
    out = tmp_path / "smoke.json"
    subprocess.run(
        [sys.executable, "scripts/smoke.py", "--log", str(out), "--dry-run"],
        capture_output=True,
    )
    data = json.loads(out.read_text())
    assert any(step["name"] == "initialize" for step in data["steps"])
