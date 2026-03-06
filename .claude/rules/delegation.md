# Delegation Rules (Opus -> Sonnet) — Frontier

Delegate via Task(model: "sonnet") for mechanical tasks:
- Codebase exploration, grep, find usages, list files
- Running tests and reporting results
- Boilerplate and scaffold generation
- Documentation updates (JSDoc, markdown)
- Lint/typecheck execution and simple fixes
- Mechanical refactors (rename, move, search-replace)
- Test case generation from system specs

Never delegate:
- Architecture and design decisions
- Three-layer rule enforcement (Game Logic / Director / Narrator boundaries)
- Narrator prompt engineering (anachronism firewall, author voice selection)
- API security review (Vercel edge, rate limiting, integrity hash)
- Cross-model orchestration decisions (gear-shifting)
- Complex multi-file debugging

Always review Sonnet's output before accepting.
Always re-run tests after applying Sonnet's changes.
