# CLAUDE.md — Autonomous Development Guide (Scanopy MCP)

This file defines how Claude CLI should work autonomously on this repo. Keep it strict, minimal, and reproducible.

## 1) Always use Superpowers
- Before any response or action, invoke relevant Superpowers skills.
- If in doubt, invoke the skill. Never skip mandatory workflows.
- Required default skills:
  - `using-superpowers`
  - `brainstorming` (before any creative work)
  - `writing-plans` (before multi-step implementation)
  - `test-driven-development` (before any feature/bugfix code)
  - `systematic-debugging` (for any failure/bug)
  - `verification-before-completion` (before claiming done)
  - `requesting-code-review` (before merging)

## 1.1) Fresh library documentation (Context7)
- For any external library usage or API details, consult Context7 first.
- Always call `resolve-library-id` before `get-library-docs`.
- Prefer official/primary sources over blog posts or secondary summaries.

## 2) Planning and execution
- For any non-trivial change, write a plan first.
- Plan format: `docs/plans/YYYY-MM-DD-<topic>.md`.
- Use TDD: write failing tests first, then minimal implementation.
- Keep steps small (2–5 minutes each) and commit frequently.

## 3) Use consultations (Codex + Gemini) as advisors
Use other models as *consultants only*, never as the primary executor.

### When to consult
- **Codex GPT‑5.2 xhigh**: architecture decisions, code review, refactoring risks, protocol/MCP specifics.
- **Gemini Flash 3.0**: fast second opinion, naming, docs wording, quick sanity checks.

### How to consult
- Provide a concise prompt with:
  - goal
  - current assumptions
  - specific question
  - constraints (KISS/YAGNI, minimal scope)
- Never paste secrets or API keys.
- Always validate suggestions against local tests and repo conventions.
- Final decisions must be justified and traceable in commits or notes.

## 4) KISS / YAGNI / Safety
- Prefer the simplest working solution.
- Avoid speculative features.
- Keep tool surface minimal and allowlisted.
- All write operations require explicit confirm string.
- Never log secrets.

## 5) GitHub workflow
- Work on a feature branch or worktree.
- Commit after each small task.
- Push to GitHub at logical milestones (minimum: end of plan).
- Use clear commit messages: `feat:`, `fix:`, `chore:`, `docs:`.

## 6) Review discipline
- Run tests before declaring success.
- Perform a self-review for:
  - correctness
  - safety/guardrails
  - regression risks
  - test coverage gaps
- If requested, produce a formal code review summary.
- After every commit, request a review from Codex GPT (this repo’s orchestrator) and wait for feedback before starting the next task.

## 7) Secrets handling
- Never store secrets in repo files.
- Use `.env` locally; commit `.env.example` only.
- Redact any secrets in logs or outputs.

## 8) Definition of done
- Plan executed.
- Tests pass.
- Docs updated.
- Changes pushed to GitHub.
- Short review summary recorded.
