#!/usr/bin/env python3
"""
Helper script to download AI models for Hasselize.

Usage:
    python scripts/download_models.py --model flux-schnell --lora
"""

import argparse
import os
from pathlib import Path

from huggingface_hub import login, snapshot_download
from core.config import settings


def download_model(model_name: str = None) -> Path:
    """
    Download FLUX.1-Schnell model from HuggingFace.

    Args:
        model_name: Model name (default: from settings)

    Returns:
        Path to downloaded model
    """
    model_name = model_name or settings.model_name

    print(f"📥 Downloading model: {model_name}")
    print(f"📁 Cache directory: {settings.model_cache_dir}")

    # Login if token provided
    token = os.getenv("HUGGINGFACE_TOKEN")
    if token:
        login(token=token)

    # Download model
    cache_path = snapshot_download(
        repo_id=model_name,
        cache_dir=settings.model_cache_dir,
        local_dir=settings.model_cache_dir / model_name.replace("/", "--"),
        local_dir_use_symlinks=False,
    )

    print(f"✅ Model downloaded to: {cache_path}")
    return Path(cache_path)


def download_lora_weights(style: str = None) -> None:
    """
    Download LoRA weights for camera style.

    Args:
        style: Camera style slug (hasselblad, leica_m, zeiss, fujifilm_gfx)
    """
    # Map styles to LoRA repositories
    # These are placeholder repos - replace with actual HuggingFace repos
    #
    # To find suitable LoRAs:
    # - Civitai: https://civitai.com/tag/loras (search for "hasselblad", "leica", etc.)
    # - HuggingFace: https://huggingface.co/models?search=lora
    #
    # LoRA files should be:
    # - FLUX.1-Schnell compatible
    # - .safetensors format
    # - Trained on photography/style transfer
    lora_repos = {
        "hasselblad": "place-holder/hasselblad-x2d-lora-flux",  # Replace with actual
        "leica_m": "place-holder/leica-m-lora-flux",
        "zeiss": "place-holder/zeiss-otus-lora-flux",
        "fujifilm_gfx": "place-holder/fujifilm-gfx-lora-flux",
    }

    if style and style in lora_repos:
        repo = lora_repos[style]
        print(f"📥 Downloading LoRA: {repo}")
        print(f"⚠️  NOTE: This is a placeholder repo!")
        print(f"    Replace with actual HuggingFace repo in download_models.py")

        try:
            cache_path = snapshot_download(
                repo_id=repo,
                cache_dir=settings.lora_cache_dir,
            )
            print(f"✅ LoRA downloaded to: {cache_path}")
        except Exception as e:
            print(f"❌ Failed to download: {e}")
            print(f"   You may need to manually download LoRA files")
    else:
        print("⚠️  No LoRA repository configured for this style")
        print("Available styles:", list(lora_repos.keys()))


def main():
    parser = argparse.ArgumentParser(description="Download AI models for Hasselize")
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Model name to download (default: from config)",
    )
    parser.add_argument(
        "--lora",
        action="store_true",
        help="Download LoRA weights",
    )
    parser.add_argument(
        "--style",
        type=str,
        choices=["hasselblad", "leica_m", "zeiss", "fujifilm_gfx"],
        help="Camera style LoRA to download",
    )

    args = parser.parse_args()

    # Download model
    if args.model or not args.lora:
        download_model(args.model)

    # Download LoRA weights
    if args.lora:
        if args.style:
            download_lora_weights(args.style)
        else:
            print("Downloading all LoRA weights...")
            for style in ["hasselblad", "leica_m", "zeiss", "fujifilm_gfx"]:
                download_lora_weights(style)


if __name__ == "__main__":
    main()
