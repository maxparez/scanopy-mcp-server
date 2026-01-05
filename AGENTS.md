# AGENTS.md — Codex GPT Orchestrator Instructions

This file defines how the Codex GPT agent should operate in this repo.

## 1) Always use Superpowers
- Before any response or action, invoke relevant Superpowers skills.
- If unsure, invoke the skill anyway.
- Default required skills:
  - `using-superpowers`
  - `brainstorming` (before any creative work)
  - `writing-plans` (before multi-step implementation)
  - `test-driven-development` (before any feature/bugfix code)
  - `systematic-debugging` (for any failure/bug)
  - `verification-before-completion` (before claiming done)
  - `requesting-code-review` (before merging)

## 2) Planning discipline
- For any non-trivial change, create a plan in `docs/plans/YYYY-MM-DD-<topic>.md`.
- Use TDD and keep steps small (2–5 minutes).
- Commit frequently with clear messages.

## 3) Orchestrator role (Codex GPT)
- Codex acts as the coordinator and reviewer.
- Claude CLI is the primary implementer.
- Codex should:
  - define the plan
  - verify changes against plan
  - enforce KISS/YAGNI
  - review for correctness and safety

## 4) External consultations
- Use other models as advisors only.
- **Codex GPT‑5.2 xhigh**: architecture decisions, code review, MCP protocol details.
- **Gemini Flash 3.0**: quick second opinions, naming, docs wording.
- Never share secrets or API keys in consultations.

## 5) GitHub workflow
- Ensure a remote exists before pushing.
- Use `main` as default branch unless told otherwise.
- Push at milestones.

## 6) Review and verification
- Never claim success without tests.
- Document risks, regressions, or gaps.
- If unsure, ask for clarification before large changes.

## 7) Security
- Secrets only in environment variables.
- Do not log sensitive headers or payloads.
- Redact keys in any output.
