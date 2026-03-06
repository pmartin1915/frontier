# Delegation Rules (Opus -> Sonnet)

Delegate via Task(model: "sonnet") for mechanical tasks:
- Codebase exploration, grep, find usages
- Running tests and reporting results
- Boilerplate and scaffold generation
- Documentation updates
- Lint/typecheck execution
- Mechanical refactors (rename, move)
- Test case generation from specs

Never delegate:
- Architecture/design decisions
- Three-layer rule enforcement
- API security review
- Cross-model orchestration decisions
- Complex multi-file debugging

Always review Sonnet's output before accepting.
Always re-run tests after applying Sonnet's changes.
