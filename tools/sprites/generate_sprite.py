#!/usr/bin/env python3
"""
Frontier Sprite Generator — HuggingFace SDXL Pipeline

Generates individual sprite frames via the HuggingFace Inference API
using the SDXL model. Frames are saved as individual PNGs, then can be
assembled into sprite sheets matching the 7-row, 8-column FSM grid.

Usage:
  # Generate a single frame
  python generate_sprite.py --entity player_base --state idle --frame 0

  # Generate all frames for an entity
  python generate_sprite.py --entity player_base --all

  # Generate all frames for all entities
  python generate_sprite.py --all-entities

  # List available entities
  python generate_sprite.py --list-entities

Requires:
  - HF_TOKEN environment variable (Hugging Face API token)
  - pip install huggingface_hub Pillow
"""

import argparse
import os
import sys
from pathlib import Path

from huggingface_hub import InferenceClient
from PIL import Image

# ============================================================
# CONFIGURATION
# ============================================================

MODEL_ID = "stabilityai/stable-diffusion-xl-base-1.0"

# Frame dimensions per entity class (width x height in pixels)
FRAME_SIZES = {
    "human": (64, 64),
    "horse": (96, 64),
    "wagon": (128, 64),
    "cat": (32, 32),
}

# FSM grid: 7 rows, 8 columns (fixed grid per handoff spec)
ROWS = 7
COLS = 8

STATES = {
    "idle": {"row": 0, "frames": 4},
    "walk": {"row": 1, "frames": 8},
    "run": {"row": 2, "frames": 6},
    "mount": {"row": 3, "frames": 4},
    "ride": {"row": 4, "frames": 6},
    "interact": {"row": 5, "frames": 8},
    "injured": {"row": 6, "frames": 2},
}

# ============================================================
# ENTITY MANIFEST
# ============================================================

ENTITIES = {
    "cat_mouser": {
        "class": "cat",
        "name": "Grey Mouser Cat",
        "description": "small grey female cat, sleek fur, alert posture",
        "interact_action": "batting at fireplace sparks, hunting vermin",
        "state_notes": {
            "idle": "sitting upright, tail flicking gently",
            "walk": "low prowl, stalking posture, belly close to ground",
            "run": "bounding gallop, legs fully extended",
            "mount": "leaping up into wagon bed",
            "ride": "curled up contentedly, eyes half-closed",
            "interact": "batting at sparks, pouncing on mice",
            "injured": "cowering, hissing, ears flattened",
        },
    },
    "player_base": {
        "class": "human",
        "name": "Trail Rider",
        "description": "male, fair skin, short light brown hair, square glasses, light blue eyes, rugged canvas trail clothes, no hat",
        "interact_action": "general camp activity",
        "state_notes": {
            "idle": "standing at ease, weight on one leg, looking ahead",
            "walk": "steady trail walk, arms swinging naturally",
            "run": "urgent sprint, leaning forward",
            "mount": "climbing onto horse, foot in stirrup",
            "ride": "seated upright in saddle, reins in hand",
            "interact": "kneeling by campfire, tending gear",
            "injured": "limping, clutching side, grimacing",
        },
    },
    "horse_riding_base": {
        "class": "horse",
        "name": "Bay Riding Horse",
        "description": "sturdy unbranded bay horse, brown coat, black mane and tail, no tack or saddle",
        "interact_action": "grazing, drinking from stream",
        "state_notes": {
            "idle": "standing still, occasional ear twitch, tail swish",
            "walk": "steady four-beat walk, head bobbing gently",
            "run": "full gallop, mane flowing, all four legs extending",
            "mount": "standing still while rider mounts, slight shift",
            "ride": "trotting with rider, controlled gait",
            "interact": "head lowered grazing, nuzzling water",
            "injured": "favoring one leg, head drooping",
        },
    },
    "horse_riding_tack": {
        "class": "horse",
        "name": "Saddle & Tack Overlay",
        "description": "western saddle with stirrups, leather saddlebags, asymmetric rifle holster on right side, all on transparent background",
        "interact_action": "tack visible during grazing",
        "state_notes": {},
    },
    "companion_elias_base": {
        "class": "human",
        "name": "Elias Coe",
        "description": "older man, graying beard, faded Union army sack coat and trousers, rigid military posture, weathered face",
        "interact_action": "checking compass and map, navigation",
        "state_notes": {
            "idle": "standing at attention, hands behind back",
            "walk": "measured military stride, upright posture",
            "run": "disciplined sprint, controlled form",
            "mount": "efficient mount, practiced motion",
            "ride": "straight-backed in saddle, scanning horizon",
            "interact": "kneeling with compass and map spread on ground",
            "injured": "stoic grimace, pressing wound, still standing",
        },
    },
    "companion_elias_kepi": {
        "class": "human",
        "name": "Elias Kepi Overlay",
        "description": "weathered Union army kepi hat, dark blue faded fabric, on transparent background",
        "interact_action": "",
        "state_notes": {},
    },
    "wagon_prairie_schooner": {
        "class": "wagon",
        "name": "Prairie Schooner Wagon",
        "description": "large heavy-duty wooden wagon, white canvas bonnet, side-lashed water barrels, wooden wheels with iron rims, no draft animals",
        "interact_action": "side canvas rolled up exposing cargo",
        "state_notes": {
            "idle": "parked, canvas gently shifting in breeze",
            "walk": "slow rolling, wheels turning steadily",
            "run": "violent rattle and jolt, hard push pace",
            "mount": "front and rear canvas flaps opening",
            "ride": "smooth cruise, gentle rocking",
            "interact": "side canvas rolled up, cargo visible",
            "injured": "broken wheel, tilted axle, listing to one side",
        },
    },
    "horse_draft_base": {
        "class": "horse",
        "name": "Heavy Draft Horse",
        "description": "large draft horse, thicker neck, heavy feathering on legs, broad chest, distinct from riding horse, no harness",
        "interact_action": "standing patiently, stamping hoof",
        "state_notes": {
            "idle": "standing solidly, occasional head shake",
            "walk": "heavy deliberate walk, powerful stride",
            "run": "thundering gallop, ground-shaking",
            "mount": "standing for harnessing",
            "ride": "pulling steadily, leaning into collar",
            "interact": "drinking deeply, resting",
            "injured": "stumbling, breathing hard",
        },
    },
    "horse_draft_harness": {
        "class": "horse",
        "name": "Draft Harness Overlay",
        "description": "heavy leather pulling collar, hames, and traces, on transparent background",
        "interact_action": "",
        "state_notes": {},
    },
    "companion_luisa_base": {
        "class": "human",
        "name": "Luisa Vega",
        "description": "woman of Mexican-Apache heritage, practical trail blouse and split riding skirt, hair tied back, determined expression",
        "interact_action": "kneeling grinding poultice, inspecting medicinal plants",
        "state_notes": {
            "idle": "standing balanced, hands on belt, watchful",
            "walk": "confident stride, purposeful movement",
            "run": "swift and agile sprint",
            "mount": "fluid mount, experienced rider",
            "ride": "relaxed but alert in saddle",
            "interact": "kneeling, grinding herbs in mortar, inspecting plants",
            "injured": "pressing cloth to wound, jaw set tight",
        },
    },
    "companion_luisa_serape": {
        "class": "human",
        "name": "Luisa Serape Overlay",
        "description": "woven earth-toned Mexican serape draped over shoulders, on transparent background",
        "interact_action": "",
        "state_notes": {},
    },
    "companion_tom_base": {
        "class": "human",
        "name": "Tom Blanchard",
        "description": "young man, slightly messy hair, nervous energy, plain work shirt and canvas pants, wiry build",
        "interact_action": "crouching with rifle aimed, skinning game",
        "state_notes": {
            "idle": "fidgeting slightly, shifting weight, scanning around",
            "walk": "quick nervous walk, head on a swivel",
            "run": "panicked sprint, arms pumping",
            "mount": "hasty scramble onto horse",
            "ride": "hunched in saddle, gripping reins tight",
            "interact": "crouching, aiming rifle, then kneeling to dress game",
            "injured": "curled tightly, frozen, hands over head",
        },
    },
    "companion_tom_hat_bandana": {
        "class": "human",
        "name": "Tom Hat & Bandana Overlay",
        "description": "weathered wide-brimmed cowboy hat and tied neck bandana, on transparent background",
        "interact_action": "",
        "state_notes": {},
    },
}

# ============================================================
# PROMPT TEMPLATES
# ============================================================

STYLE_HEADER = (
    "side-view pixel art sprite, crisp pixel clusters, no blur, "
    "no anti-aliasing, limited color palette, hi-bit pixel art style, "
    "game sprite, 1866 American frontier western, facing right"
)

NEGATIVE_PROMPT = (
    "painterly shading, gradients, blurry edges, extra limbs, text, watermark, "
    "signature, 3d render, photograph, realistic, anti-aliasing, smooth gradients, "
    "modern clothing, anachronistic items"
)

BACKGROUND_INSTRUCTION = "solid bright magenta (#FF00FF) background for chroma keying"


def build_prompt(entity_key: str, state: str, frame: int) -> str:
    """Build a generation prompt for a specific entity/state/frame."""
    entity = ENTITIES[entity_key]
    frame_count = STATES[state]["frames"]

    # State-specific pose description
    state_note = entity["state_notes"].get(state, f"{state} pose")

    # Frame-specific motion cue
    if frame_count > 1:
        progress = frame / (frame_count - 1) if frame_count > 1 else 0
        if state in ("walk", "run"):
            cycle_cues = [
                "contact pose, leading foot down",
                "passing pose, legs crossing",
                "reaching pose, stride extended",
                "contact pose, trailing foot down",
            ]
            cue = cycle_cues[frame % len(cycle_cues)]
        elif state == "idle":
            cue = f"subtle breathing frame {frame + 1} of {frame_count}"
        else:
            cue = f"animation frame {frame + 1} of {frame_count}, {progress:.0%} through motion"
    else:
        cue = "static pose"

    prompt = (
        f"{STYLE_HEADER}, "
        f"{entity['description']}, "
        f"{state_note}, "
        f"{cue}, "
        f"{BACKGROUND_INSTRUCTION}"
    )

    return prompt


# ============================================================
# GENERATION
# ============================================================


def get_client() -> InferenceClient:
    """Create HuggingFace InferenceClient with API token."""
    token = os.environ.get("HF_TOKEN")
    if not token:
        print("Error: HF_TOKEN environment variable not set.", file=sys.stderr)
        print("Get your token at https://huggingface.co/settings/tokens", file=sys.stderr)
        sys.exit(1)
    return InferenceClient(token=token)


def generate_frame(
    client: InferenceClient,
    entity_key: str,
    state: str,
    frame: int,
    output_dir: Path,
    size: tuple[int, int] | None = None,
) -> Path:
    """Generate a single sprite frame and save it."""
    entity = ENTITIES[entity_key]
    entity_class = entity["class"]
    fw, fh = size or FRAME_SIZES[entity_class]

    prompt = build_prompt(entity_key, state, frame)

    print(f"  Generating {entity_key}/{state}/frame_{frame:02d}...")
    print(f"    Prompt: {prompt[:120]}...")

    # Generate at 2x for better detail, will downscale in cleanup
    gen_width = max(512, fw * 4)
    gen_height = max(512, fh * 4)
    # SDXL requires dimensions divisible by 8
    gen_width = (gen_width // 8) * 8
    gen_height = (gen_height // 8) * 8

    image = client.text_to_image(
        prompt=prompt,
        negative_prompt=NEGATIVE_PROMPT,
        model=MODEL_ID,
        width=gen_width,
        height=gen_height,
        num_inference_steps=30,
        guidance_scale=7.5,
    )

    # Save raw output
    frame_dir = output_dir / entity_key / state
    frame_dir.mkdir(parents=True, exist_ok=True)
    output_path = frame_dir / f"frame_{frame:02d}_raw.png"
    image.save(output_path)
    print(f"    Saved: {output_path}")
    return output_path


def generate_entity(
    client: InferenceClient, entity_key: str, output_dir: Path
) -> list[Path]:
    """Generate all frames for a single entity."""
    paths = []
    print(f"\nGenerating entity: {entity_key} ({ENTITIES[entity_key]['name']})")

    for state_name, state_info in STATES.items():
        for frame_idx in range(state_info["frames"]):
            path = generate_frame(client, entity_key, state_name, frame_idx, output_dir)
            paths.append(path)

    return paths


def generate_all(client: InferenceClient, output_dir: Path) -> None:
    """Generate all frames for all entities."""
    for entity_key in ENTITIES:
        generate_entity(client, entity_key, output_dir)


# ============================================================
# CLI
# ============================================================


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Frontier Sprite Generator — HuggingFace SDXL Pipeline"
    )
    parser.add_argument("--entity", help="Entity key (e.g., player_base)")
    parser.add_argument("--state", help="Animation state (e.g., idle, walk)")
    parser.add_argument("--frame", type=int, help="Frame index (0-based)")
    parser.add_argument(
        "--all", action="store_true", help="Generate all frames for --entity"
    )
    parser.add_argument(
        "--all-entities", action="store_true", help="Generate everything"
    )
    parser.add_argument("--list-entities", action="store_true", help="List entities")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output_raw"),
        help="Output directory (default: output_raw)",
    )
    parser.add_argument(
        "--prompt-only",
        action="store_true",
        help="Print prompts without generating (dry run)",
    )

    args = parser.parse_args()

    if args.list_entities:
        print("Available entities:")
        for key, ent in ENTITIES.items():
            cls = ent["class"]
            fw, fh = FRAME_SIZES[cls]
            print(f"  {key:30s}  class={cls:6s}  frame={fw}x{fh}  {ent['name']}")
        return

    if args.prompt_only:
        if args.entity and args.state is not None and args.frame is not None:
            prompt = build_prompt(args.entity, args.state, args.frame)
            print(f"Prompt:\n{prompt}\n\nNegative:\n{NEGATIVE_PROMPT}")
        elif args.entity:
            for state_name, info in STATES.items():
                for f in range(info["frames"]):
                    prompt = build_prompt(args.entity, state_name, f)
                    print(f"[{state_name}/frame_{f:02d}] {prompt[:100]}...")
        return

    client = get_client()

    if args.all_entities:
        generate_all(client, args.output_dir)
    elif args.entity and args.all:
        generate_entity(client, args.entity, args.output_dir)
    elif args.entity and args.state is not None and args.frame is not None:
        generate_frame(client, args.entity, args.state, args.frame, args.output_dir)
    else:
        parser.print_help()
        print("\nExamples:")
        print("  python generate_sprite.py --list-entities")
        print("  python generate_sprite.py --entity player_base --state idle --frame 0")
        print("  python generate_sprite.py --entity player_base --all")
        print("  python generate_sprite.py --entity player_base --state walk --frame 0 --prompt-only")


if __name__ == "__main__":
    main()
