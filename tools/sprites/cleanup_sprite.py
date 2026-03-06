#!/usr/bin/env python3
"""
Frontier Sprite Cleanup — Background Removal & Sheet Assembly

Takes raw SDXL output and:
  1. Removes background via rembg (or chroma key for magenta backgrounds)
  2. Scales to target frame size via nearest-neighbor interpolation
  3. Optionally applies palette quantization for hi-bit pixel art look
  4. Assembles individual frames into a 7-row x 8-column sprite sheet

Usage:
  # Clean a single frame (rembg background removal)
  python cleanup_sprite.py clean --input frame_raw.png --output frame_clean.png

  # Clean all raw frames for an entity
  python cleanup_sprite.py clean-entity --entity player_base --raw-dir output_raw --clean-dir output_clean

  # Assemble cleaned frames into a sprite sheet
  python cleanup_sprite.py assemble --entity player_base --clean-dir output_clean --output sheets/

  # Full pipeline: clean + assemble for an entity
  python cleanup_sprite.py pipeline --entity player_base --raw-dir output_raw --output sheets/

  # Validate a sprite sheet against expected dimensions
  python cleanup_sprite.py validate --sheet sheets/player_base.png --entity player_base

Requires:
  - pip install rembg Pillow numpy
"""

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

# ============================================================
# CONFIGURATION (must match generate_sprite.py)
# ============================================================

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

FRAME_SIZES = {
    "human": (64, 64),
    "horse": (96, 64),
    "wagon": (128, 64),
    "cat": (32, 32),
}

ENTITY_CLASSES = {
    "cat_mouser": "cat",
    "player_base": "human",
    "horse_riding_base": "horse",
    "horse_riding_tack": "horse",
    "companion_elias_base": "human",
    "companion_elias_kepi": "human",
    "wagon_prairie_schooner": "wagon",
    "horse_draft_base": "horse",
    "horse_draft_harness": "horse",
    "companion_luisa_base": "human",
    "companion_luisa_serape": "human",
    "companion_tom_base": "human",
    "companion_tom_hat_bandana": "human",
}

# Chroma key color (bright magenta)
CHROMA_KEY = (255, 0, 255)
CHROMA_TOLERANCE = 30

# Default palette size for quantization
DEFAULT_PALETTE_COLORS = 32


# ============================================================
# BACKGROUND REMOVAL
# ============================================================


def remove_background_rembg(image: Image.Image) -> Image.Image:
    """Remove background using rembg ML model."""
    from rembg import remove

    # rembg expects and returns PIL Images
    result = remove(image)
    return result.convert("RGBA")


def remove_background_chroma(
    image: Image.Image,
    key_color: tuple[int, int, int] = CHROMA_KEY,
    tolerance: int = CHROMA_TOLERANCE,
) -> Image.Image:
    """Remove background using chroma key (magenta).

    Preferred for pixel art as it preserves crisp edges better than ML removal.
    """
    img_array = np.array(image.convert("RGBA"))
    rgb = img_array[:, :, :3].astype(np.int16)

    # Calculate distance from chroma key color
    diff = np.abs(rgb - np.array(key_color, dtype=np.int16))
    mask = np.all(diff <= tolerance, axis=2)

    # Set matching pixels to transparent
    img_array[mask, 3] = 0

    return Image.fromarray(img_array, "RGBA")


def clean_frame(
    input_path: Path,
    output_path: Path,
    target_size: tuple[int, int],
    method: str = "rembg",
    palette_colors: int | None = None,
) -> None:
    """Clean a single raw frame: remove background, scale, optionally quantize."""
    image = Image.open(input_path).convert("RGBA")

    # Step 1: Background removal
    if method == "chroma":
        image = remove_background_chroma(image)
    else:
        image = remove_background_rembg(image)

    # Step 2: Nearest-neighbor resize to target frame size
    image = image.resize(target_size, Image.NEAREST)

    # Step 3: Optional palette quantization (preserves transparency)
    if palette_colors is not None:
        image = quantize_palette(image, palette_colors)

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)


def quantize_palette(image: Image.Image, num_colors: int) -> Image.Image:
    """Reduce color count while preserving transparency.

    Separates the alpha channel, quantizes RGB, then reapplies alpha.
    """
    # Split alpha
    alpha = image.split()[3]
    rgb = image.convert("RGB")

    # Quantize RGB
    quantized = rgb.quantize(colors=num_colors, method=Image.Quantize.MEDIANCUT)
    quantized_rgb = quantized.convert("RGB")

    # Reapply alpha
    result = quantized_rgb.convert("RGBA")
    result.putalpha(alpha)
    return result


# ============================================================
# ENTITY CLEANING
# ============================================================


def clean_entity(
    entity_key: str,
    raw_dir: Path,
    clean_dir: Path,
    method: str = "rembg",
    palette_colors: int | None = None,
) -> int:
    """Clean all raw frames for an entity. Returns count of frames processed."""
    entity_class = ENTITY_CLASSES.get(entity_key)
    if not entity_class:
        print(f"Error: Unknown entity '{entity_key}'", file=sys.stderr)
        return 0

    target_size = FRAME_SIZES[entity_class]
    count = 0

    print(f"Cleaning entity: {entity_key} (class={entity_class}, target={target_size})")

    for state_name, state_info in STATES.items():
        for frame_idx in range(state_info["frames"]):
            raw_path = raw_dir / entity_key / state_name / f"frame_{frame_idx:02d}_raw.png"
            clean_path = clean_dir / entity_key / state_name / f"frame_{frame_idx:02d}.png"

            if not raw_path.exists():
                print(f"  Warning: Missing {raw_path}")
                continue

            clean_frame(raw_path, clean_path, target_size, method, palette_colors)
            count += 1
            print(f"  Cleaned: {state_name}/frame_{frame_idx:02d}")

    print(f"  Total frames cleaned: {count}")
    return count


# ============================================================
# SHEET ASSEMBLY
# ============================================================


def assemble_sheet(
    entity_key: str,
    clean_dir: Path,
    output_dir: Path,
) -> Path | None:
    """Assemble cleaned frames into a 7x8 sprite sheet."""
    entity_class = ENTITY_CLASSES.get(entity_key)
    if not entity_class:
        print(f"Error: Unknown entity '{entity_key}'", file=sys.stderr)
        return None

    fw, fh = FRAME_SIZES[entity_class]
    sheet_width = COLS * fw
    sheet_height = ROWS * fh

    print(f"Assembling sheet: {entity_key} ({sheet_width}x{sheet_height})")

    # Create transparent sheet
    sheet = Image.new("RGBA", (sheet_width, sheet_height), (0, 0, 0, 0))

    frames_placed = 0
    frames_missing = 0

    for state_name, state_info in STATES.items():
        row = state_info["row"]
        for frame_idx in range(state_info["frames"]):
            frame_path = clean_dir / entity_key / state_name / f"frame_{frame_idx:02d}.png"

            if not frame_path.exists():
                print(f"  Missing: {state_name}/frame_{frame_idx:02d}")
                frames_missing += 1
                continue

            frame = Image.open(frame_path).convert("RGBA")

            # Verify frame dimensions
            if frame.size != (fw, fh):
                print(
                    f"  Warning: {state_name}/frame_{frame_idx:02d} is {frame.size}, "
                    f"expected {(fw, fh)}. Resizing."
                )
                frame = frame.resize((fw, fh), Image.NEAREST)

            # Place frame on sheet
            x = frame_idx * fw
            y = row * fh
            sheet.paste(frame, (x, y), frame)
            frames_placed += 1

    # Save sheet
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{entity_key}.png"
    sheet.save(output_path)

    print(f"  Frames placed: {frames_placed}, missing: {frames_missing}")
    print(f"  Sheet saved: {output_path}")
    return output_path


# ============================================================
# VALIDATION
# ============================================================


def validate_sheet(sheet_path: Path, entity_key: str) -> bool:
    """Validate a sprite sheet against expected dimensions and structure."""
    entity_class = ENTITY_CLASSES.get(entity_key)
    if not entity_class:
        print(f"Error: Unknown entity '{entity_key}'", file=sys.stderr)
        return False

    fw, fh = FRAME_SIZES[entity_class]
    expected_width = COLS * fw
    expected_height = ROWS * fh

    if not sheet_path.exists():
        print(f"FAIL: Sheet not found: {sheet_path}")
        return False

    image = Image.open(sheet_path).convert("RGBA")
    issues = []

    # Check dimensions
    if image.size != (expected_width, expected_height):
        issues.append(
            f"Dimensions: got {image.size}, expected ({expected_width}, {expected_height})"
        )

    # Check unused cells are transparent
    img_array = np.array(image)
    for state_name, state_info in STATES.items():
        row = state_info["row"]
        used_frames = state_info["frames"]

        for col in range(used_frames, COLS):
            x_start = col * fw
            y_start = row * fh
            cell = img_array[y_start : y_start + fh, x_start : x_start + fw]

            non_transparent = np.any(cell[:, :, 3] > 0)
            if non_transparent:
                issues.append(
                    f"Non-transparent pixels in unused cell: row={row} ({state_name}), col={col}"
                )

    # Check used frames have content
    for state_name, state_info in STATES.items():
        row = state_info["row"]
        for col in range(state_info["frames"]):
            x_start = col * fw
            y_start = row * fh
            cell = img_array[y_start : y_start + fh, x_start : x_start + fw]

            has_content = np.any(cell[:, :, 3] > 0)
            if not has_content:
                issues.append(
                    f"Empty frame (all transparent): row={row} ({state_name}), frame={col}"
                )

    if issues:
        print(f"VALIDATION FAILED for {entity_key}:")
        for issue in issues:
            print(f"  - {issue}")
        return False

    print(f"VALIDATION PASSED: {entity_key} ({image.size[0]}x{image.size[1]})")
    return True


# ============================================================
# FULL PIPELINE
# ============================================================


def run_pipeline(
    entity_key: str,
    raw_dir: Path,
    output_dir: Path,
    method: str = "rembg",
    palette_colors: int | None = None,
) -> None:
    """Full pipeline: clean raw frames + assemble into sheet."""
    clean_dir = raw_dir.parent / "output_clean"

    print(f"=== Pipeline: {entity_key} ===\n")

    # Step 1: Clean frames
    count = clean_entity(entity_key, raw_dir, clean_dir, method, palette_colors)
    if count == 0:
        print("No frames cleaned. Aborting.")
        return

    # Step 2: Assemble sheet
    print()
    sheet_path = assemble_sheet(entity_key, clean_dir, output_dir)

    # Step 3: Validate
    if sheet_path:
        print()
        validate_sheet(sheet_path, entity_key)


# ============================================================
# CLI
# ============================================================


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Frontier Sprite Cleanup — Background Removal & Sheet Assembly"
    )
    subparsers = parser.add_subparsers(dest="command")

    # --- clean ---
    p_clean = subparsers.add_parser("clean", help="Clean a single raw frame")
    p_clean.add_argument("--input", type=Path, required=True, help="Input raw PNG")
    p_clean.add_argument("--output", type=Path, required=True, help="Output clean PNG")
    p_clean.add_argument(
        "--entity", required=True, help="Entity key (for frame size)"
    )
    p_clean.add_argument(
        "--method",
        choices=["rembg", "chroma"],
        default="rembg",
        help="Background removal method (default: rembg)",
    )
    p_clean.add_argument(
        "--palette", type=int, default=None, help="Palette color count (optional)"
    )

    # --- clean-entity ---
    p_ce = subparsers.add_parser("clean-entity", help="Clean all frames for an entity")
    p_ce.add_argument("--entity", required=True, help="Entity key")
    p_ce.add_argument(
        "--raw-dir", type=Path, default=Path("output_raw"), help="Raw frames directory"
    )
    p_ce.add_argument(
        "--clean-dir",
        type=Path,
        default=Path("output_clean"),
        help="Clean frames directory",
    )
    p_ce.add_argument(
        "--method", choices=["rembg", "chroma"], default="rembg"
    )
    p_ce.add_argument("--palette", type=int, default=None)

    # --- assemble ---
    p_asm = subparsers.add_parser("assemble", help="Assemble frames into sprite sheet")
    p_asm.add_argument("--entity", required=True, help="Entity key")
    p_asm.add_argument(
        "--clean-dir",
        type=Path,
        default=Path("output_clean"),
        help="Clean frames directory",
    )
    p_asm.add_argument(
        "--output", type=Path, default=Path("sheets"), help="Output directory for sheets"
    )

    # --- pipeline ---
    p_pipe = subparsers.add_parser(
        "pipeline", help="Full pipeline: clean + assemble"
    )
    p_pipe.add_argument("--entity", required=True, help="Entity key")
    p_pipe.add_argument(
        "--raw-dir", type=Path, default=Path("output_raw"), help="Raw frames directory"
    )
    p_pipe.add_argument(
        "--output", type=Path, default=Path("sheets"), help="Output directory"
    )
    p_pipe.add_argument(
        "--method", choices=["rembg", "chroma"], default="rembg"
    )
    p_pipe.add_argument("--palette", type=int, default=None)

    # --- validate ---
    p_val = subparsers.add_parser("validate", help="Validate a sprite sheet")
    p_val.add_argument("--sheet", type=Path, required=True, help="Sheet PNG path")
    p_val.add_argument("--entity", required=True, help="Entity key")

    args = parser.parse_args()

    if args.command == "clean":
        entity_class = ENTITY_CLASSES.get(args.entity)
        if not entity_class:
            print(f"Error: Unknown entity '{args.entity}'", file=sys.stderr)
            sys.exit(1)
        target_size = FRAME_SIZES[entity_class]
        clean_frame(args.input, args.output, target_size, args.method, args.palette)
        print(f"Cleaned: {args.output}")

    elif args.command == "clean-entity":
        clean_entity(args.entity, args.raw_dir, args.clean_dir, args.method, args.palette)

    elif args.command == "assemble":
        assemble_sheet(args.entity, args.clean_dir, args.output)

    elif args.command == "pipeline":
        run_pipeline(args.entity, args.raw_dir, args.output, args.method, args.palette)

    elif args.command == "validate":
        success = validate_sheet(args.sheet, args.entity)
        sys.exit(0 if success else 1)

    else:
        parser.print_help()
        print("\nExamples:")
        print("  python cleanup_sprite.py clean --entity player_base --input raw.png --output clean.png")
        print("  python cleanup_sprite.py clean-entity --entity player_base --raw-dir output_raw")
        print("  python cleanup_sprite.py assemble --entity player_base --clean-dir output_clean")
        print("  python cleanup_sprite.py pipeline --entity player_base --raw-dir output_raw")
        print("  python cleanup_sprite.py validate --entity player_base --sheet sheets/player_base.png")


if __name__ == "__main__":
    main()
