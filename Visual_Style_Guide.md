FRONTIER: Visual Style & Art Direction Guide

Target Aesthetic: "Hi-Bit" / Modern Retro (Reference: Octopath Traveler, Eastward, The Long Dark UI)

1. Core Visual Pillars

A. The "Living Illustration" Standard

The goal is not to look like a generic SNES game, but to look like a moving 19th-century illustration.

Resolution: High-density pixel art. Avoid "blocky" or "low-res" abstraction.

Outline Rule: Use "selective outlining." Characters have dark (but colored) outlines to separate them from the background. Internal details use softer, lighter contrast lines to define muscle and cloth folds without creating visual noise.

Texture: Surfaces must read clearly. Canvas should look rough, horse coats should look sleek, metal should have high specular highlights.

B. Modern Color Depth

We are not restricted to a hardware palette.

Color Grading: The game utilizes full 32-bit color depth.

Palette Strategy:

Base Sprites: Rendered in "Neutral Daylight" (warm, desaturated earth tones).

Runtime Tinting: Phaser applies hex-code tints based on the time of day.

Shadows: Shadows are not black; they are deep purple or cool blue depending on the biome.

C. Secondary Motion ("The Juice")

Nothing is ever perfectly still.

Wind Interaction: All accessory layers (bandanas, manes, wagon canvas) must respond to the windSpeed game state.

Sub-Pixel Animation: Use "breathe" effects (1px vertical scaling) on Idle states to prevent static "frozen" looks.

2. Character & Sprite Fidelity

The Layering Advantage

Depth: Because accessories are separate layers, they cast small drop-shadows onto the base sprite. This creates a faux-3D effect (2.5D) that adds volume to the characters.

Degradation: Equipment (wagons, saddles) has "worn" texture variants. A fresh wagon looks crisp; a damaged one has splintered wood pixels and torn canvas transparency.

Animation Fluidity

Frame Rate: 12fps animation running on a 60fps canvas.

The 8-Frame Standard: Walk cycles use 8 frames to capture the "contact," "recoil," "passing," and "high-point" of a step. This prevents the "sliding feet" look common in lower-budget pixel games.

3. Environmental Integration

Lighting & Atmosphere

The sprites must interact with the background layers.

Rim Lighting: During "Sunset" and "Dawn" states, sprites receive a 1px bright edge highlight on the sun-facing side.

Particle Emitters:

Dust: Horses kick up 2-4 pixel dust particles at the hoof contact point (synced to Walk/Run frames).

Breath: In "Mountain/Cold" biomes, characters emit semi-transparent white breath clouds.

4. UI & Presentation

Typography: Crimson Text or Lora. High readability, serif, no pixel-fonts for body text.

The Frame: The game plays inside a sophisticated "Storybook" frame. The pixel art lives in the "Illustration Panel" (Upper Right), treated like a window into the reality of the text.