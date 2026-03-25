# Project State: Frontier

<!-- Keep this file under 200 lines. Any agent may read/write it. -->
<!-- Updated: 2026-03-24, Session 7 -->

## Objective

- Narrative-driven survival game on the 1866 Goodnight-Loving Trail
- Three-layer engine: Game Logic -> Director -> Narrator (Claude Sonnet 4.6)
- Web + iOS: React 18 + Phaser 3.80 + Zustand 5 + Tauri 2.10
- 60-90 in-game days, 3 author voices (Adams, Irving, McMurtry)
- Deployed: Vercel (web + API), TestFlight v1.0.4 (iOS)

## Constraints

- Anachronism firewall: 1866 period accuracy (no Winchester rifles, barbed wire, telegraph west of settlements)
- API budget: ~$0.00825 per Narrator call, ~$0.80 per full playthrough
- 60fps on mobile Safari (simultaneous React + Phaser rendering)
- Narrator is prose-only — never modifies game state
- Offline fallback: hard-coded entries from fallback-ledger.ts on API timeout (8s)

## Architecture

- `src/engine/game-logic.ts` (464 LOC): Layer 1 — pure TypeScript, all mechanical outcomes
- `src/engine/director.ts` (369 LOC): Layer 2 — voice selection, prompt assembly (no AI calls)
- `src/engine/narrator.ts` (107 LOC): Layer 3 — API client, 8s timeout, fallback handling
- `src/engine/daily-cycle.ts` (191 LOC): Orchestrates Layer 1 -> 2 -> 3 for one in-game day
- `src/engine/auto-player.ts` (290 LOC): Automated decision-making for playtesting
- `src/systems/` (2,200 LOC across 10 files): movement, supplies, health, morale, equipment, encounters, companions, camp, fail-forward, waypoint
- `src/store/index.ts` (400+ LOC): Zustand store + atomic selectors
- `src/phaser/`: TrailScene, CampScene, PreloadScene + sprite system + 5 effect managers
- `src/audio/`: SFX (Web Audio synthesis, 10 events) + Ambiance (Howler.js, 7 biome tracks)
- `src/ui/`: React panels (TravelLog, AnimationPanel, HUD, MapPanel) + overlays
- `api/narrator.ts` (283 LOC): Vercel edge function (Anthropic/Moonshot/Gemini, CORS, caching)
- `src/data/`: Trail routes, weather tables, encounter templates, fallback ledger, voice bibles
- **External:** C:\sprite-forge (Sprite Forge pipeline) generates and deploys assets

## What's Done

1. Full type system: 9 type files (1,716 LOC) — game-state, narrative, animation, companions, encounters, camp, map-objects, audio
2. All 10 game systems implemented and tested (~2,200 LOC)
3. Three-layer engine: game-logic, director, narrator, daily-cycle — all wired
4. Zustand store with full GameState, atomic selectors, React-Phaser bridge
5. Phaser scenes: PreloadScene, TrailScene (7-layer parallax), CampScene (procedural stars, campfire)
6. Sprite system: 13 entities, FSM animation, accessory layers, degradation visuals
7. Narrator edge function with 3 LLM providers, prompt caching, per-voice calibration, rate limiting, CORS
8. Voice bibles (Adams/Irving/McMurtry ~2,500 tokens each) + fallback ledger (30+ entries)
9. Audio system: SFX synthesis (10 events), Howler.js ambiance (biome-reactive, crossfade)
10. Persistence: IndexedDB active/archive split, JSON backup, integrity hashing
11. Simulator: headless CLI, 4 strategies, report generator
12. iOS pipeline: Tauri 2.10, GitHub Actions CI/CD, manual code signing, TestFlight v1.0.4
13. 418 Vitest unit tests passing, 29 Playwright e2e tests, TypeScript clean
14. Sprite Forge pipeline (74 tests, 33 files) at C:\sprite-forge
15. API hardening: rate limiting, CORS enforcement, server timeouts, hash validation, store race fixes

## What's Next

1. [x] ~~Verify Narrator API end-to-end in Vercel production~~ (done 2026-03-24, CORS+rate limit+hash verified)
2. [x] ~~Implement rate limiting via Vercel KV~~ (done 2026-03-24, in-memory Map-based MVP; KV upgrade deferred)
3. [ ] Configure Moonshot/Anthropic API keys in Vercel env vars (narrator returns 502 — keys not set)
4. [ ] Source 7 ambient audio MP3s (system coded, files missing at public/audio/ambient/)
5. [ ] Fix 3 NEEDS_WORK sprites: elias_base (stocky), luisa_base (interact row), cat_mouser (run blobs)
6. [ ] Upgrade rate limiting to Vercel KV for cross-instance persistence
7. [ ] Implement integrityHash session registry (currently format-only validation)
8. [ ] Add more encounter templates and companion events
9. [ ] Mobile performance optimization (CampScene)
10. [ ] iOS haptics on encounters and day transitions
11. [ ] Landscape orientation lock for gameplay

## Sprite Status

| Rating | Count | Sprites |
|--------|-------|---------|
| GOOD | 8 | wagon, tom_base, tom_hat_bandana, elias_kepi, horse_riding_base, horse_draft_base, player_cowboy, player_base (unused) |
| NEEDS_WORK | 3 | elias_base (stocky), luisa_base (interact row), cat_mouser (run blobs) |
| DISABLED | 4 | luisa_serape, luisa_poncho, horse_riding_tack, horse_draft_harness (diff-extraction noise in silhouette mode) |

## Open Loops

- **Loop:** ~~Narrator not verified in production~~ **CLOSED** (2026-03-24). CORS, rate limiting, hash validation all verified via curl. Provider calls return 502 because API keys not yet configured in Vercel env.
  **Next probe:** Perry: add MOONSHOT_API_KEY / ANTHROPIC_API_KEY to Vercel env vars

- **Loop:** Ambient audio files missing — system coded but public/audio/ambient/ directory empty
  **Next probe:** Source/generate 7 MP3 loops, verify Howler loads them

- **Loop:** Vercel KV not configured — in-memory rate limiting works but resets on cold start
  **Next probe:** Set up Vercel KV store for persistent cross-instance rate limiting

## Git State

- **Branch:** main
- **Latest commit:** 615b0ef fix: API hardening sprint — rate limiting, CORS, timeouts, store race conditions
- **Latest tag:** v1.0.4 (on TestFlight)
- **Vercel URL:** https://frontier-kappa-two.vercel.app/ (deployed 2026-03-24, hardened)
