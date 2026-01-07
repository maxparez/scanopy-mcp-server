# MCP CLI Installation Instructions Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Expand `README.md` with step-by-step MCP installation instructions for Claude CLI, Codex CLI, and Gemini CLI clients so the repo is immediately usable by CLI-driven users.

**Architecture:** Add a new section after installation overview describing CLI-based MCP registration commands, environment variables, confirmation steps, and verification commands. Reuse existing information about environment setup and highlight the new `scanopy` tool name.

**Tech Stack:** Markdown documentation edits

---

### Task 1: Draft CLI installation instructions

**Files:**
- Modify: `README.md`

**Step 1: Write the failing test**

Add `tests/test_public_ready.py` asserts covering the new README text (already has tests checking example URL). Extend to ensure CLI instructions appear.

**Step 2: Run test to verify it fails**

Run `.venv/bin/python -m pytest tests/test_public_ready.py::test_readme_mentions_cli_instructions -v` expected failure.

**Step 3: Add CLI instructions block to README**

Add a new section detailing `claude mcp add`, `codex mcp add`, `glm mcp add`, required env vars, verifying via `/help`, `codex mcp list`, `glm mcp list`, and refer to `scripts/smoke.py` for dry-run.

**Step 4: Run test to verify it passes**

Re-run `.venv/bin/python -m pytest tests/test_public_ready.py::test_readme_mentions_cli_instructions -v`.

**Step 5: Commit**

`git add README.md tests/test_public_ready.py && git commit -m "docs: add CLI install instructions"`

