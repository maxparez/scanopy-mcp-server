# Public Repo Readiness Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make the repo safe and ready for public release by removing internal URLs from docs, adding MIT license, and adding SECURITY/CONTRIBUTING guides.

**Architecture:** Minimal doc edits and new top-level community files. No code changes beyond docs and metadata.

**Tech Stack:** Markdown, repo metadata

---

### Task 1: Replace internal base URL placeholders in docs

**Files:**
- Modify: `README.md`
- Modify: `docs/USAGE.md`

**Step 1: Write the failing test**

```python
def test_public_docs_use_example_base_url():
    import pathlib
    readme = pathlib.Path("README.md").read_text(encoding="utf-8")
    usage = pathlib.Path("docs/USAGE.md").read_text(encoding="utf-8")
    assert "192.168.2.200" not in readme
    assert "192.168.2.200" not in usage
    assert "https://scanopy.example.com" in readme
    assert "https://scanopy.example.com" in usage
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_public_ready.py::test_public_docs_use_example_base_url -v`
Expected: FAIL

**Step 3: Write minimal implementation**

Replace the internal URL with `https://scanopy.example.com` in both files.

**Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_public_ready.py::test_public_docs_use_example_base_url -v`
Expected: PASS

**Step 5: Commit**

```bash
git add README.md docs/USAGE.md tests/test_public_ready.py
git commit -m "docs: replace internal base URL"
```

---

### Task 2: Add MIT License

**Files:**
- Create: `LICENSE`

**Step 1: Write the failing test**

```python
def test_license_exists():
    import pathlib
    assert pathlib.Path("LICENSE").exists()
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_public_ready.py::test_license_exists -v`
Expected: FAIL

**Step 3: Write minimal implementation**

Add standard MIT License text with correct year and author.

**Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_public_ready.py::test_license_exists -v`
Expected: PASS

**Step 5: Commit**

```bash
git add LICENSE tests/test_public_ready.py
git commit -m "chore: add MIT license"
```

---

### Task 3: Add SECURITY.md and CONTRIBUTING.md

**Files:**
- Create: `SECURITY.md`
- Create: `CONTRIBUTING.md`

**Step 1: Write the failing test**

```python
def test_community_files_exist():
    import pathlib
    assert pathlib.Path("SECURITY.md").exists()
    assert pathlib.Path("CONTRIBUTING.md").exists()
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_public_ready.py::test_community_files_exist -v`
Expected: FAIL

**Step 3: Write minimal implementation**

Create minimal guides with contact instructions and contribution workflow.

**Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_public_ready.py::test_community_files_exist -v`
Expected: PASS

**Step 5: Commit**

```bash
git add SECURITY.md CONTRIBUTING.md tests/test_public_ready.py
git commit -m "docs: add security and contributing guides"
```

