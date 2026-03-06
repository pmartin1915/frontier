# Project State: Frontier

<!-- Keep this file under 200 lines. Any agent may read/write it. -->

## Objective

Narrative-driven survival game on the 1866 Goodnight-Loving Trail. Phaser.js animation, React UI, Zustand state, Anthropic API narrator.

## What's Done

- [x] CLAUDE.md with full architecture spec (three-layer rule, state management, module boundaries)
- [x] Scaffold created at frontier-scaffold/frontier/
- [x] Adopted Combo multi-agent framework (.clinerules, ai/, .claude/rules/)

## What's Next

- [ ] Phase 0 walking skeleton (Vite + React + Phaser bridge)
- [ ] Zustand store with GameState types
- [ ] React-Phaser command queue and event bridge
- [ ] 60fps benchmark with all bridges active

## Open Loops

- [ ] sprite-forge pipeline for game sprites (separate project at C:\sprite-forge)
