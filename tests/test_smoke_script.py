import json
import subprocess
import sys


def test_smoke_log_written(tmp_path, monkeypatch):
    monkeypatch.setenv("SCANOPY_BASE_URL", "http://example")
    monkeypatch.setenv("SCANOPY_API_KEY", "key")
    out = tmp_path / "smoke.json"
    subprocess.run([sys.executable, "scripts/smoke.py", "--log", str(out)], capture_output=True)
    assert out.exists()
