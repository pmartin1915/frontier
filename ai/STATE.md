# Project State: Frontier

<!-- Keep this file under 200 lines. Any agent may read/write it. -->
<!-- Updated: after each subtask and at session end. -->

## Objective

- Narrative-driven survival game on the 1866 Goodnight-Loving Trail
- Three-layer engine: Game Logic -> Director -> Narrator (Claude Sonnet 4.5)
- Web-based: React + Phaser.js + Zustand, deployed on Vercel
- 60-90 in-game days, 3 author voices (Adams, Irving, McMurtry)

## Constraints

- Anachronism firewall: 1866 period accuracy (no Winchester rifles, no barbed wire, no telegraph west of settlements)
- API budget: ~$0.00825 per Narrator call, ~$0.80 per full playthrough
- 60fps on mobile Safari (simultaneous React + Phaser rendering)
- Narrator is prose-only — never modifies game state
- Offline fallback: hard-coded entries from fallback-ledger.ts on API timeout (8s)

## Architecture

- `src/engine/game-logic.ts`: Layer 1 — pure TypeScript, all mechanical outcomes
- `src/engine/director.ts`: Layer 2 — voice selection, prompt assembly (no AI calls)
- `src/engine/narrator.ts`: Layer 3 — Anthropic API client, fallback handling
- `src/systems/`: Movement, supplies, health, morale, equipment, encounters
- `src/store/`: Zustand (single source of truth)
- `src/phaser/`: Phaser.js scenes, sprites, bridge to Zustand
- `src/ui/`: React panels and overlays
- `api/narrator.ts`: Vercel edge function (rate limiting, CORS, API proxy)
- `src/data/`: Trail routes, weather tables, encounter templates, fallback ledger
- **External:** C:\sprite-forge (Sprite Forge pipeline) generates and deploys assets

## What's Done

1. Project scaffold with full type system (game-state.ts, narrative.ts, companions.ts)
2. Vercel edge function for Narrator with rate limiting and prompt caching
3. Phaser config + bridge to Zustand via subscribe()
4. Fallback ledger with biome/morale-tagged entries
5. Sprite Forge pipeline built and tested (74 tests, 33 files) at C:\sprite-forge
6. Combo framework state management adopted (STATE.md, DECISIONS.md) (2026-02-19)

## What's Next

1. [ ] First sprite generation run via Sprite Forge (cat_mouser proof-of-concept)
2. [ ] Deploy generated sprites to public/assets/sprites/
3. [ ] Implement remaining src/systems/ (movement, supplies, health, morale, equipment, encounters)
4. [ ] Build daily-cycle.ts orchestrator (Layer 1 -> 2 -> 3 flow)
5. [ ] Implement Zustand store with full GameState
6. [ ] Build Phaser scenes (BootScene, TrailScene, CampScene)

## Open Loops

- **Loop:** Most src/systems/ and src/phaser/scenes/ are .gitkeep stubs
  **Evidence:** Glob shows .gitkeep files in systems/, phaser/scenes/, phaser/sprites/
  **Next probe:** Implement movement.ts and supplies.ts first (core mechanics)

## Git State

- **Branch:** (scaffold state)
- **Last commit:** N/A
