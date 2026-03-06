# Frontier

Oregon Trail game design documentation, sprite generation, and visual asset pipeline specifications.

## Description

Frontier is a comprehensive game design and visual asset project for an Oregon Trail-style game. It includes detailed game design documents (GDD), sprite generation specifications, visual style guides, and a Python-based sprite generation pipeline that leverages AI for creating pixel-art animations. The project features an 8-stage sprite pipeline with vision audit capabilities and multi-model orchestration.

## Tech Stack

- **Languages:** JavaScript (sprite download scripts), Python 3 (sprite generation pipeline)
- **Sprite Generation:** Replicate API, Claude Vision, Gemini Vision, Kimi Vision
- **Game Engine:** Phaser (referenced)
- **Utilities:** Node.js for sprite download coordination

## Key Components

### Documentation
- `Frontier_GDD_v4.docx` - Complete game design document (v4)
- `Sprite_Pipeline_Spec.md` - Sprite generation FSM and animation rules
- `Visual_Style_Guide.md` - Art direction and aesthetic guidelines
- `Sprite_generation_handoff.md` - Sprite creation workflow

### Sprite Generation Pipeline (Python)
- **Stages:** Generation, assembly, validation, audit, palette optimization, diff analysis, alignment, deployment
- **Vision Audit:** Claude, Gemini, and Kimi vision models for frame quality assurance
- **Frame Grid:** 7 rows × 8 columns per entity (56 frames per spritesheet)
- **Budget:** $10.00 per pipeline run

### Asset Scripts
- `download_sprites.js` - Download generated sprites from Replicate
- `download_sprites_64.js` - 64x64 resolution variant

## Setup

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables for API keys:
   ```bash
   cp .env.example .env
   # Edit .env with Replicate, Claude, Gemini, Kimi API keys
   ```

3. Generate sprites:
   ```bash
   python -m sprite_forge.cli generate --entity player-character
   ```

4. Run full pipeline:
   ```bash
   python -m sprite_forge.cli generate-all
   ```

## Game Assets

The project specifies 8 major assets with detailed FSM mappings:
1. Camp Pet (Grey Mouser Cat)
2. Base Player Character
3. Primary Riding Horse
4. Elias Coe (Companion)
5. Prairie Schooner Wagon
6. Heavy Draft Horse
7. Luisa Vega (Companion)
8. Tom Blanchard (Companion)

## Status

**Active Development** - Comprehensive game design and sprite generation framework. Multiple commits for game balancing research, sprite pipeline refinement, and visual documentation.
