import pathlib


def test_public_docs_use_example_base_url():
    readme = pathlib.Path("README.md").read_text(encoding="utf-8")
    usage = pathlib.Path("docs/USAGE.md").read_text(encoding="utf-8")
    assert "192.168.2.200" not in readme
    assert "192.168.2.200" not in usage
    assert "https://scanopy.example.com" in readme
    assert "https://scanopy.example.com" in usage


def test_readme_mentions_cli_installations():
    readme = pathlib.Path("README.md").read_text(encoding="utf-8")
    assert "claude mcp add scanopy" in readme
    assert "codex mcp add scanopy" in readme
    assert "gemini mcp add scanopy" in readme


def test_license_exists():
    assert pathlib.Path("LICENSE").exists()


def test_community_files_exist():
    assert pathlib.Path("SECURITY.md").exists()
    assert pathlib.Path("CONTRIBUTING.md").exists()
