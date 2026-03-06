# Decisions Log

> Append-only. Each entry records a choice that future sessions should not revisit.
> Format: date, decision, rationale, alternatives rejected.

## 2026-02-20 — Adopt Combo multi-agent framework
- **Why:** Multi-agent development requires persistent context. Any agent can read ai/STATE.md to resume work instantly.
- **Rejected:** Relying solely on conversation history (lost on session end).
- **Agent:** Claude Code (Opus 4.6)
