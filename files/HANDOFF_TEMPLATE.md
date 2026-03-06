# Agent Handoff Document

> Fill out every field. Save as HANDOFF.md in the project root.
> The receiving agent reads this to pick up where you left off.
> If `ai/STATE.md` exists, read it first -- it contains live project state that
> may be more current than this handoff document.

## Handoff Metadata

- **Timestamp:** [YYYY-MM-DD HH:MM]
- **Sending Agent:** [Claude Code / Cline + Gemini / Gemini CLI / Kimi CLI / Aider]
- **Receiving Agent:** [Recommended: Claude Code / Cline + Gemini / Gemini CLI / Kimi CLI / Aider]
- **Reason for Handoff:** [context limit / task mismatch / rate limit / second opinion / session end]
- **Context Usage:** [low (<25%) / medium (25-50%) / high (50-75%) / near-limit (>75%)]
- **ai/STATE.md status:** [current / stale / does not exist]
- **Files in Sending Agent's Context:**
  - `path/to/file1.ts`
  - `path/to/file2.tsx`

## Project

- **Name:** Frontier
- **Stack:** Phaser.js, React, Zustand, TypeScript, Anthropic API, Vite, Vercel
- **Repo:** c:\Frontier\files\frontier-scaffold\frontier

## Current State

- **What's working:** [brief description]
- **What's broken:** [if anything]
- **Dev server:** [e.g., localhost:5173 -- running/stopped]

## Session Summary

1. [completed task]
2. [completed task]

## Blocked On

- **Issue:** [describe the blocker]
- **Relevant files:**
  - `path/to/file1.tsx`
  - `path/to/file2.ts`
- **Error message (if any):**

```text
[paste error here]
```

## Next Steps

> If switching projects, only list tasks relevant to the *receiving* project.

1. [ ] [immediate next task]
2. [ ] [follow-up task]
3. [ ] [stretch goal]
