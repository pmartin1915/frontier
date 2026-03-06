# Frontier sprite generation handoff pack for Claude Code

## Goals and scope for this handoff

This report distills the sprite-generation decisions you and “Gemini” already converged on into a format that an implementation-focused agent (Claude Code via entity["company","Anthropic","ai lab, san francisco"]) can turn directly into infrastructure: asset manifests, animation registration, runtime layering, and a repeatable generation/QC pipeline.

The scope here is intentionally narrow and mechanical:

- A universal animation grid (FSM) that all animatable entities obey  
- A right-facing-only authoring rule with runtime left-facing via horizontal flip  
- A modular overlay system for accessories/tack/harnesses (separate transparent sheets aligned to the same grid)  
- A practical, free toolchain strategy for producing “hi-bit” pixel art sprites with consistent proportions and minimal “AI slop”  
- Concrete implementation hooks: naming, schemas, animation key strategy, and QA checks

image_group{"layout":"carousel","aspect_ratio":"16:9","query":["pixel art sprite sheet grid layout 7 rows 8 columns example","Phaser 3 spritesheet animation example","pixel art character layered sprite example"],"num_per_query":1}

## Canonical animation grid and rendering rules

### Universal grid definition

All animatable entities use a mandatory **7-row** state machine laid out as a single sprite sheet (base layer) with optional aligned overlay sheets.

Row meanings and intended frame counts (your “strict FSM”):

- Row 0: **idle** (4 frames)  
- Row 1: **walk** (8 frames)  
- Row 2: **run** (6 frames)  
- Row 3: **mount/dismount** (4 frames)  
- Row 4: **ride** (6 frames)  
- Row 5: **interact** (4–8 frames; you’ve been leaning toward 6–8 for richer storytelling)  
- Row 6: **injured** (2 frames)

### Authoring rules

**Right-facing rule (authoring):** Every base sprite and every overlay sprite is authored facing right. Left-facing behavior is produced at runtime by flipping (scaleX = -1 / flipX). This ensures you don’t double your texture memory budget for the same entity.

**Overlay rule:** Anything that can be removed, swapped, degraded, or toggled (hats, serapes, saddle/tack, harness) must be in a separate transparent-background sheet that is **pixel-aligned to the base**, frame-for-frame.

**Frame-locked motion rule:** The walk/run animation speeds must be tied to movement speed so the feet don’t “moonwalk.” In practice, this is achieved in code by adjusting animation playback speed (timeScale) based on the entity’s current movement speed, rather than creating multiple separate animation definitions.

### A key suggestion: choose a single fixed column count

Right now your frame counts vary by row (4/8/6/4/6/8/2). This is artist-friendly but can be code-annoying unless you fix a canonical sheet width.

To make Claude’s job radically simpler, pick one of these approaches:

**Option A (recommended for infrastructure simplicity): fixed 8 columns for every row**  
You still “use” only 6 frames for run and ride, and only 2 for injured—but you reserve the unused cells as blank/transparent (or duplicates). The sheet is always `rows=7, cols=8`.  
This gives you a clean frame index formula and makes overlay alignment trivial.

**Option B: variable row widths**  
This saves a little texture space but forces custom frame-index mapping logic and complicates tooling (sheet slicing, overlay syncing, debugging).

If you want the project to stay frictionless for code + content, Option A is usually worth the tiny wasted space.

## Asset manifest distilled from your conversation

This is the “what we have accomplished” portion, rewritten into a structured manifest Claude can implement.

### Entities and their layers

**Camp Pet — Grey Mouser Cat**  
Base sheet only (for now). States are as defined; notable interpretive beats: idle sitting/tail flick; walk low prowl; run bounding; mount/dismount = leap into/out of wagon; ride curled/settled; interact batting sparks/hunting; injured cower/hiss.

**Player — Base Character**  
Base sheet only. Male; fair skin; short light brown hair; square glasses; light blue eyes; rugged canvas trail clothes; no heavy coat/hat/poncho to keep the base “clean” for modular layers later.

**Primary Riding Horse — Base**  
Base sheet only: unbranded bay horse, no tack.

**Primary Riding Horse — Saddle/Tack Overlay (transparent)**  
Overlay sheet aligned to horse base. Includes saddle, stirrups, saddlebags, and an asymmetric rifle holster called out as “flip-exempt” in your notes (see implementation questions below because “flip-exempt” has multiple plausible meanings in a 2D side-view).

**Elias Coe — Base Companion**  
Base sheet only: Union veteran vibe, faded sack coat/trousers, rigid posture; Row 5 interact = navigation behavior (map/compass).

**Elias Coe — Kepi Overlay (transparent)**  
Hat overlay sheet aligned to base.

**Prairie Schooner Wagon — Base**  
Base sheet only: heavy-duty wagon with canvas bonnet; barrels/visual cues for capacity; **no draft animals attached** (draft animals are separate entities).

Mapped to the same 7 rows even though it’s inanimate:
- idle = parked canvas subtle movement  
- walk = slow roll  
- run = violent rattle/jolt “hard push”  
- mount/dismount = boarding/loading beats (canvas flap / tie-off)  
- ride = smoother cruise animation  
- interact = side canvas rolled up showing cargo  
- injured = broken wheel / tilted axle “catastrophic failure”

**Heavy Draft Horse — Base**  
Base sheet only: thicker neck/broader chest; visually distinct.

**Heavy Draft Horse — Harness Overlay (transparent)**  
Overlay sheet aligned to base. Includes collar/hames/traces. (Traces attaching to wagon may be easiest as a separate “connector” layer rather than baked into the horse overlay; see suggestions section.)

**Luisa Vega — Base Companion**  
Base sheet only: practical durable trail clothes; hair tied back; Row 5 interact = medicine/herbal work.

**Luisa Vega — Serape Overlay (transparent)**  
Outerwear overlay aligned to base.

**Tom Blanchard — Base Companion**  
Base sheet only: young cowhand vibe; anxious energy; Row 5 interact = hunting (aim rifle → kneel/field dress).

**Tom Blanchard — Hat + Bandana Overlay (transparent)**  
Overlay aligned to base; supports “hat can blow away” gameplay by toggling layer visibility.

### Minimal “identity keys” Claude should implement

Claude will need stable IDs to avoid refactors later. I strongly recommend you treat the following as canonical string keys:

- `cat_mouser`
- `player_base`
- `horse_riding_base`
- `horse_riding_tack`
- `companion_elias_base`
- `companion_elias_kepi`
- `wagon_prairie_schooner`
- `horse_draft_base`
- `horse_draft_harness`
- `companion_luisa_base`
- `companion_luisa_serape`
- `companion_tom_base`
- `companion_tom_hat_bandana`

If you later introduce “worn tack,” “damaged harness,” “winter poncho,” etc., keep them as additional overlay texture keys rather than branching the base entity.

## Implementation spec for Claude Code

This section is written so you can paste it as-is into a “Sprite_Pipeline_Spec.md” and have Claude convert it into TypeScript + Phaser infrastructure.

### Files and folders to create

A clean, scalable layout:

- `assets/sprites/<spriteKey>/base.png`
- `assets/sprites/<spriteKey>/overlays/<overlayKey>.png`
- `assets/sprites/manifest.json` (or `.ts`)  
- `src/render/sprites/`
  - `registerAnimations.ts`
  - `SpriteStack.ts`
  - `spriteManifest.ts`
  - `pace.ts` (mapping pace → speed multipliers and animation timeScale rules)

### Data schema

Use a single manifest that drives loading, animation creation, and layering.

A practical schema (expressed in prose so you can hand it to Claude without bikeshedding syntax):

**SpriteSheetSpec**
- `key`: string (texture key)
- `url`: string (relative asset path)
- `frameWidth`: number
- `frameHeight`: number
- `rows`: number (always 7)
- `cols`: number (recommend 8, fixed)
- `framesPerState`: map: `{ idle: 4, walk: 8, run: 6, mount: 4, ride: 6, interact: 8, injured: 2 }`
- `statesToRowIndex`: map: `{ idle: 0, walk: 1, run: 2, mount: 3, ride: 4, interact: 5, injured: 6 }`

**LayerSpec**
- `textureKey`: string (points to a SpriteSheetSpec)
- `zIndex`: number (render order)
- `flipMode`: enum (see below)
- `visibleByDefault`: boolean

**EntityVisualSpec**
- `entityKey`: string
- `base`: LayerSpec
- `overlays`: LayerSpec[]
- `anchors` (optional but recommended): named points used for mounting/riding/attachments

### Animation key strategy (important Phaser detail)

Because entity["organization","Phaser","html5 game framework"] animations are registered globally by a string key, you must avoid collisions across textures.

A robust convention:

- Animation key: `<textureKey>::<state>`
  - Example: `horse_riding_base::walk`
  - Example: `horse_riding_tack::walk`

Then, when you play an animation on a stacked entity, you call it per layer:

- Base sprite plays `baseTextureKey::state`
- Each overlay sprite plays `overlayTextureKey::state`

This guarantees overlays are always frame-synced to the base as long as the sheets share the same grid.

### SpriteStack abstraction

Have Claude implement a `SpriteStack` wrapper that internally owns:

- one base `Sprite`
- N overlay `Sprite`s
- optional “connector” sprites (traces, muzzle flashes, etc.)
- methods:
  - `playState(state, { paceMultiplier })`
  - `setFacing(facing)` (left/right)
  - `setOverlayVisible(overlayKey, boolean)`
  - `setOverlayVariant(overlayGroupKey, variantKey)` (for worn/damaged swaps)
  - `destroy()`

The key is that gameplay code never touches raw sprites directly; it tells the stack what state it’s in, and the stack keeps visuals coherent.

### Facing and “flip-exempt” overlays

This needs one explicit design decision because “flip-exempt” can mean at least three different things:

1. **Don’t mirror the overlay pixels** (keep orientation of insignia/text so it doesn’t read backwards), while still moving it with the body.
2. **Don’t mirror its position** (keep it on a specific hip/side) even when the base sprite flips.
3. **Swap to a different overlay variant** (a hand-authored “left-facing correct” overlay) for the rare assets where mirroring breaks believability.

Because you’re intentionally not authoring left-facing art, you likely want either (1) or a hybrid rule:
- default overlays: mirror with base
- special overlays: keep pixel orientation (so logos/text stay readable), but still accept mirrored position

Claude should implement `flipMode` on each layer:

- `mirror_with_base` (default)
- `keep_pixel_orientation` (cancels the mirror on that layer but keeps alignment)
- `swap_variant_on_flip` (future-proof option)

If you later decide you truly need “holster stays on right hip,” you’ll almost certainly need either `swap_variant_on_flip` or accept a stylized compromise.

### Movement pace → animation pacing

Instead of creating separate walk animations per pace, set animation speed dynamically:

- Base rule: define a “reference speed” for walk/run per entity type (human vs horse vs wagon).
- At runtime: `sprite.anims.timeScale = currentSpeed / referenceSpeed`.

This is the cleanest way to keep walk cycles from foot-skating across terrain when conservative/normal/hard push speeds differ.

### Dev-only visual QA scene

Have Claude build a `SpriteGalleryScene` (or route) that can:

- cycle through every entity key in the manifest
- toggle overlays on/off
- switch facing left/right
- cycle states idle/walk/run/mount/ride/interact/injured
- apply pace multipliers live

This becomes your “sprite smoke test” and will pay for itself the first time an overlay sheet is off by 1 pixel or the frame order is wrong.

## How to generate sprites for consistent high quality

You asked two practical questions:

- “How exactly will sprites be generated?”  
- “How will we keep them high-quality?”  

The hard truth: the *quality problem* in AI sprite sheets isn’t raw detail—it’s **consistency across frames** (same proportions, same silhouette, no drift). So the pipeline must be built around consistency first, and detail second.

### The generation unit should be per-frame, not “one giant sheet,” unless you have strong control

It is tempting to prompt a model for “an 8-frame walk cycle sprite sheet.” Sometimes it works, often it drifts: different head sizes per frame, changing clothing folds, inconsistent pixel clusters.

For consistently stunning results, treat each frame as a controlled shot:

- Generate or hand-author a **single canonical reference frame** (idle frame 0).
- Generate subsequent frames using constraints so the model can’t “invent a new character” mid-cycle.

Practically, this means you either:
- do manual pixel animation after generating a single clean pose, or
- use a controlled AI workflow that supports reference conditioning (image prompt / adapter) and pose constraints.

### Free toolchain options that Claude can implement/build around

You said: “It needs to be free, or I can build my own with Claude.”

Here are the most realistic free paths, without assuming any specific vendor’s current free-tier limits.

#### Local, fully free pipeline (most reliable long-term)

- Run an open-source diffusion UI locally (ComfyUI / similar) with an SDXL-class model.
- Use a “pixel art” style adapter/model/LoRA and lock resolution low (so it can’t paint fancy gradients).
- Post-process via deterministic scripts: nearest-neighbor scaling, palette quantization, and chroma-key transparency.

Pros: no API dependence; reproducible; you control versions.  
Cons: needs a capable GPU for comfortable iteration speed.

#### Scripted local pipeline (Claude-friendly)

Claude can write a Python tool that:

- takes a `SpriteSpec` (state + frame index)
- renders a frame via a local model (Diffusers)
- applies a deterministic pixel-art cleanup pass
- assembles frames into a sheet using PIL

Pros: fully automatable; integrates directly with your manifest; no clicking.  
Cons: still needs local compute.

#### API-based pipeline (fast to start, but policy/limits can change)

Claude can write a script that calls an inference endpoint (e.g., via entity["company","Hugging Face","ml platform company"]), saves outputs, then processes locally.

Pros: easy startup if you don’t have GPU.  
Cons: limits, queueing, and terms can change; reproducibility is trickier.

### Non-negotiables for “hi-bit pixel art” quality

To keep sprites crisp and avoid the “AI-painted-but-pixelated” look:

**Lock resolution and scale with nearest neighbor.**  
Pick your true working resolution (per-frame W×H). Generate at or near it, then scale only by integer multiples (2×, 3×, 4×) using nearest neighbor.

**Force a limited palette.**  
Even “16-bit aesthetic with modern color depth” benefits from a palette ceiling per asset family. Your time-of-day and biome palettes become much easier if the base sprites aren’t full of near-duplicate colors.

**Prefer chroma-key transparency over ML background removal for pixel art.**  
ML background removal can soften or chew edges. A pixel-perfect method is: generate against a background color that will never appear in the sprite (classic “magenta key”), then replace exactly that color with alpha 0 in a script.

**Build a repeatable QC checklist.**  
At minimum, for each sheet:
- exact dimensions match `(cols * frameWidth, rows * frameHeight)`
- no non-transparent pixels exist in reserved “unused” frames (if you adopt fixed 8 columns)
- overlay sheets match base dimensions exactly
- all frames share the same origin convention (e.g., boots always rest on the same baseline pixel)

### Prompt and spec templating

Even if you generate locally or via API, the prompt format should be templated so Claude can auto-generate prompts from your manifest.

A useful structure:

- **Style header** (constant): “side-view sprite, crisp pixel clusters, no blur, no anti-aliasing, limited palette, game sprite”
- **Entity identity block** (constant per character): face/hair/clothes silhouette notes
- **State block** (varies): “walk cycle frame 3 of 8; right leg forward; arms counter-swing”
- **Technical constraints** (constant): “transparent or solid chroma background; orthographic; consistent proportions”
- **Negative constraints**: “no painterly shading, no gradients, no blurry edges, no extra limbs, no text”

This is exactly the kind of deterministic “prompt factory” Claude can build so you aren’t hand-editing prompts for every frame.

## Questions and decisions that will unblock Claude

These are the minimum clarifications that will prevent infrastructure rework later. If you answer these once, Claude can lock the schemas and move fast.

### Frame sizes and scale

- What are the target per-frame pixel dimensions for:  
  - humans  
  - riding horse  
  - draft horse  
  - wagon  
  - cat  
- What is the in-game scaling rule? (e.g., render at 3× nearest-neighbor, or author at final resolution)

### Column policy

- Do you want the **fixed 8-column grid** across all rows (recommended), with run/ride/injured padding?  
  If yes: do you want unused cells blank or duplicated frames?

### Attachment anchors

- Do you need explicit per-entity anchor points?
  - rider seat position on horses (for mount/ride alignment)
  - cat “wagon-bed” perch point
  - harness hitch point for traces to the wagon

If yes, should anchors be:
- constant per entity (one point), or
- per state, or
- per frame (highest fidelity, most work)

### “Flip-exempt” definition

- When you said the rifle holster is “flip-exempt,” which behavior do you want?

1) keep the holster’s pixels from mirroring (so it doesn’t look inside-out),  
2) keep it on the same body side even when facing flips, or  
3) accept mirroring and only prevent mirrored *logos/text*?

### Interact-row length per entity class

- Are you standardizing `interact` to 8 frames for all entities (humans/animals/wagon), or allowing 6 frames for some?  
Standardization helps tooling and animation registration but costs a little texture space.

### Palette system integration

- Are you planning:
  - runtime palette swapping (shader/pipeline), or
  - pre-baked textures per biome × time-of-day?

This decision affects how you store textures and how overlays are tinted consistently.

## Practical suggestions before you hand this to Claude

These are high-leverage improvements that keep your “beautiful plan” from becoming a brittle implementation.

First, encode everything in a manifest and treat sprite sheets as data, not special cases. The wagon, draft horses, and companions should all be loaded and animated by the same generic code path—your manifest is the “truth.”

Second, implement a dedicated sprite QA scene early, not after you have dozens of sheets. It becomes your immediate feedback loop for overlay alignment, flip correctness, and pace sync.

Third, separate “harness traces to wagon” as its own visual element rather than baking it into horse overlays. Traces are long, need flexible attachment to wagon position, and will look wrong if the wagon and horses animate with slight offsets. A connector sprite (or even a simple line/mesh later) gives you more control.

Fourth, standardize your sheet export pipeline around deterministic scripts (slice/pack/validate) so you never have to eyeball whether a sheet is aligned. If you can make the pipeline fail fast on mis-sized sheets, you’ll save hours.

Finally, if the priority is “visually stunning,” bias toward **consistency assets** (reference frame + controlled variants) over “one-shot generation of full cycles.” Most of the wow-factor in pixel art comes from clean silhouettes, deliberate shading, and frame-to-frame stability—not from raw model detail.

