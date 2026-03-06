# Decisions Log

> Append-only. Each entry records a choice that future sessions should not revisit.
> Format: date, decision, rationale, alternatives rejected.

## 2026-02-19 — Three-layer engine architecture (Game Logic -> Director -> Narrator)
- **Why:** Strict separation ensures AI never controls game state. Layer 1 is deterministic, Layer 2 is rule-based, Layer 3 is AI prose only.
- **Rejected:** Single-layer AI-driven approach (unreliable game state).
- **Agent:** Frontier agent

## 2026-02-19 — Claude Sonnet 4.5 for Narrator via Vercel edge function
- **Why:** High-quality prose generation at ~$0.00825/call. Prompt caching (5-min TTL) reduces cost. Vercel edge keeps API key server-side.
- **Rejected:** Client-side API calls (exposes key), GPT-4 (higher cost, different voice quality).
- **Agent:** Frontier agent

## 2026-02-19 — Zustand as single source of truth (not Redux, not Phaser state)
- **Why:** Lightweight, subscribe()-based. Phaser reads state via subscribe() without triggering React re-renders.
- **Rejected:** Redux (boilerplate), Phaser-internal state (not accessible to React).
- **Agent:** Frontier agent

## 2026-02-19 — Sprite Forge as standalone tool at C:\sprite-forge
- **Why:** Decoupled from game code. Generates sprites via AI pipeline and deploys to Frontier's public/assets/sprites/. Can be run independently.
- **Rejected:** Inline sprite tooling within Frontier repo.
- **Agent:** Claude Code (Combo integration)

## 2026-02-19 — Adopt Combo framework state patterns (STATE.md, DECISIONS.md)
- **Why:** Multi-agent development (Claude, Gemini, Kimi) requires persistent context. ai/STATE.md gives any agent instant project awareness.
- **Rejected:** Relying solely on CLAUDE.md (not agent-agnostic).
- **Agent:** Claude Code (Combo integration)
