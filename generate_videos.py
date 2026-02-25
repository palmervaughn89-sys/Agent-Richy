#!/usr/bin/env python3
"""Agent Richy — Batch Video Generator

Run this script on a machine with an NVIDIA GPU (12GB+ VRAM recommended)
to generate all educational videos using CogVideoX-2b.

Usage:
    # Generate ALL 30 videos:
    python generate_videos.py

    # Generate only kids videos:
    python generate_videos.py --audience kids

    # Generate only a specific video:
    python generate_videos.py --key savings_piggy_bank

    # Force regenerate (overwrite existing):
    python generate_videos.py --force

    # Fewer inference steps for faster (lower quality) previews:
    python generate_videos.py --steps 25

    # List all available video prompts:
    python generate_videos.py --list

Requirements:
    pip install diffusers torch accelerate

    NVIDIA GPU with 12GB+ VRAM (RTX 3060 12GB, RTX 4070, RTX 4080, etc.)
    First run will download the CogVideoX-2b model (~5GB).
"""

import argparse
import sys
import time

# Ensure the project root is importable
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_richy.utils.video_generator import (
    VIDEO_PROMPTS,
    generate_video,
    generate_all_videos,
    get_video_path,
    get_all_generated_videos,
    is_video_generation_available,
    VIDEO_DIR,
)


def list_prompts():
    """Print all available video prompts."""
    print("\n" + "=" * 70)
    print("  Available Video Prompts")
    print("=" * 70)

    by_audience = {}
    for key, meta in VIDEO_PROMPTS.items():
        by_audience.setdefault(meta["audience"], []).append((key, meta))

    for audience in ["kids", "middle", "high"]:
        prompts = by_audience.get(audience, [])
        print(f"\n  🎓 {audience.upper()} ({len(prompts)} videos)")
        for key, meta in prompts:
            existing = get_video_path(key)
            status = "✅ generated" if existing else "⬜ not generated"
            print(f"     {key:<30} {meta['title']:<35} [{status}]")

    # Summary
    existing = get_all_generated_videos()
    print(f"\n  Total: {len(VIDEO_PROMPTS)} prompts | "
          f"Generated: {len(existing)} | "
          f"Remaining: {len(VIDEO_PROMPTS) - len(existing)}")
    print(f"  Output directory: {VIDEO_DIR}\n")


def check_system():
    """Print system info and check readiness."""
    print("\n" + "=" * 70)
    print("  System Check")
    print("=" * 70)

    # Python version
    print(f"  Python: {sys.version.split()[0]}")

    # PyTorch + CUDA
    try:
        import torch
        print(f"  PyTorch: {torch.__version__}")
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_mem / (1024 ** 3)
            print(f"  GPU: {gpu_name} ({vram:.1f} GB VRAM)")
            print(f"  CUDA: {torch.version.cuda}")

            if vram >= 16:
                print("  Mode: Full GPU (fastest) ✅")
            elif vram >= 10:
                print("  Mode: Model CPU offload (balanced) ✅")
            else:
                print("  Mode: Sequential CPU offload (slow) ⚠️")
        else:
            print("  GPU: None detected ❌")
            print("  Mode: CPU only (very slow, not recommended)")
    except ImportError:
        print("  PyTorch: NOT INSTALLED ❌")
        print("  Run: pip install torch")
        return False

    # Diffusers
    try:
        import diffusers
        print(f"  Diffusers: {diffusers.__version__}")
    except ImportError:
        print("  Diffusers: NOT INSTALLED ❌")
        print("  Run: pip install diffusers accelerate")
        return False

    # Accelerate
    try:
        import accelerate
        print(f"  Accelerate: {accelerate.__version__}")
    except ImportError:
        print("  Accelerate: NOT INSTALLED ⚠️")
        print("  Run: pip install accelerate")

    print("=" * 70 + "\n")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Agent Richy — Generate educational financial literacy videos with CogVideoX",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_videos.py                     # Generate all 30 videos
  python generate_videos.py --audience kids     # Only kids videos
  python generate_videos.py --key savings_piggy_bank  # One specific video
  python generate_videos.py --list              # List all prompts
  python generate_videos.py --check             # Check system readiness
  python generate_videos.py --steps 25          # Faster preview (lower quality)
        """,
    )
    parser.add_argument("--list", action="store_true", help="List all available video prompts and their status")
    parser.add_argument("--check", action="store_true", help="Check system requirements and GPU info")
    parser.add_argument("--audience", choices=["kids", "middle", "high"], help="Generate only for this audience")
    parser.add_argument("--key", type=str, help="Generate a single video by prompt key")
    parser.add_argument("--force", action="store_true", help="Regenerate even if video already exists")
    parser.add_argument("--steps", type=int, default=50, help="Inference steps (default: 50, lower = faster but lower quality)")
    parser.add_argument("--frames", type=int, default=49, help="Number of frames (default: 49)")
    parser.add_argument("--guidance", type=float, default=6.0, help="Guidance scale (default: 6.0)")

    args = parser.parse_args()

    # ── List mode ────────────────────────────────────────────────────
    if args.list:
        list_prompts()
        return

    # ── System check ─────────────────────────────────────────────────
    if args.check:
        ok = check_system()
        list_prompts()
        if not ok:
            print("⚠️  System is not ready for video generation.")
            print("Install requirements: pip install diffusers torch accelerate\n")
        return

    # ── Validate system before generating ────────────────────────────
    print("\n🎬 Agent Richy — Video Generator")
    print("=" * 50)

    if not is_video_generation_available():
        print("\n❌ Required packages not found.")
        print("Install them with:")
        print("  pip install diffusers torch accelerate")
        print("\nRun --check for full system info.\n")
        sys.exit(1)

    start_time = time.time()

    # ── Single video mode ────────────────────────────────────────────
    if args.key:
        if args.key not in VIDEO_PROMPTS:
            print(f"\n❌ Unknown video key: '{args.key}'")
            print(f"Available keys: {', '.join(VIDEO_PROMPTS.keys())}")
            sys.exit(1)

        existing = get_video_path(args.key)
        if existing and not args.force:
            print(f"\n⏭️  '{args.key}' already exists at {existing}")
            print("Use --force to regenerate.\n")
            return

        path = generate_video(
            args.key,
            num_frames=args.frames,
            guidance_scale=args.guidance,
            num_inference_steps=args.steps,
        )
        if path:
            elapsed = time.time() - start_time
            print(f"\n✅ Done in {elapsed:.1f}s — saved to {path}\n")
        else:
            print("\n❌ Generation failed.\n")
            sys.exit(1)
        return

    # ── Batch mode ───────────────────────────────────────────────────
    results = generate_all_videos(
        audience=args.audience,
        num_frames=args.frames,
        guidance_scale=args.guidance,
        num_inference_steps=args.steps,
        skip_existing=not args.force,
    )

    total_time = time.time() - start_time
    minutes = total_time / 60
    print(f"  ⏱️  Total time: {minutes:.1f} minutes")
    print(f"  📁 Videos in: {VIDEO_DIR}\n")

    if results:
        print("Generated videos:")
        for p in results:
            print(f"  • {p}")
        print()


if __name__ == "__main__":
    main()
