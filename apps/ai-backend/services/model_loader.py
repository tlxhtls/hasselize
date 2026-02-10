"""
AI model loader for Hasselize AI Backend.

Implements FLUX.1-Schnell with img2img pipeline for high-speed
transformation on RTX 5090 GPU.

Spec:
- Model: FLUX.1-Schnell (FP4 quantized)
- Pipeline: img2img with Denoising Strength 0.3-0.4
- Resolution: 256x256 (minimal latency)
- Optimization: TensorRT-RTX with JIT compilation
"""

import logging
import os
from pathlib import Path
from typing import Optional

import torch
from diffusers import (
    FluxImg2ImgPipeline,
    FluxPipeline,
)
from huggingface_hub import login as hf_login

from core.config import settings
from core.gpu_manager import gpu_manager
from models.enums import CameraStyle, ModelType

logger = logging.getLogger(__name__)


class ModelLoadError(Exception):
    """Raised when model loading fails."""

    pass


class ModelLoader:
    """
    AI model loader and manager.

    Features:
    - Lazy loading (loads on first use)
    - LoRA style injection
    - FP16/BF16 optimization
    - TensorRT compilation (optional)
    - GPU memory management
    """

    def __init__(self):
        """Initialize model loader."""
        self._pipeline: Optional[FluxImg2ImgPipeline] = None
        self._model_type = ModelType.FLUX_SCHNELL
        self._is_loaded = False

    @property
    def device(self) -> torch.device:
        """Get the computation device."""
        return gpu_manager.device

    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._is_loaded and self._pipeline is not None

    def _load_lora_weights(
        self,
        style: CameraStyle,
    ) -> tuple[str, float]:
        """
        Get LoRA weights path and weight for camera style.

        Args:
            style: Camera style to load

        Returns:
            Tuple of (lora_path, lora_weight)
        """
        # LoRA weight mapping for each camera style
        # These paths should exist in LORA_CACHE_DIR
        lora_configs = {
            CameraStyle.HASSELBLAD: (
                "c41_hasselblad_portra400.safetensors",
                1.0,
            ),
            CameraStyle.LEICA_M: (
                "leica_m_style.safetensors",
                0.9,
            ),
            CameraStyle.ZEISS: (
                "zeiss_otus_style.safetensors",
                0.95,
            ),
            CameraStyle.FUJIFILM_GFX: (
                "fujifilm_gfx_style.safetensors",
                1.0,
            ),
        }

        lora_file, weight = lora_configs.get(
            style,
            lora_configs[CameraStyle.HASSELBLAD],
        )

        lora_path = str(settings.lora_cache_dir / lora_file)

        if not Path(lora_path).exists():
            logger.warning(f"LoRA file not found: {lora_path}, using base model")
            return None, 1.0

        return lora_path, weight

    def load_model(
        self,
        force_reload: bool = False,
    ) -> FluxImg2ImgPipeline:
        """
        Load FLUX.1-Schnell model with optimizations.

        Args:
            force_reload: Force reload even if already loaded

        Returns:
            Loaded pipeline

        Raises:
            ModelLoadError: If loading fails
        """
        if self._is_loaded and not force_reload:
            logger.debug("Model already loaded, skipping")
            return self._pipeline

        try:
            logger.info(f"Loading model: {settings.model_name}")

            # Login to HuggingFace if token provided
            hf_token = os.getenv("HUGGINGFACE_TOKEN")
            if hf_token:
                hf_login(token=hf_token)

            # Load FLUX.1-Schnell pipeline
            # Using BF16 for RTX 5090 optimal performance
            model_kwargs = {
                "torch_dtype": torch.bfloat16,  # BF16 for RTX 5090
            }

            # Load img2img pipeline for style transfer
            # FLUX.1-Schnell supports img2img natively
            pipeline = FluxImg2ImgPipeline.from_pretrained(
                settings.model_name,
                **model_kwargs,
                cache_dir=settings.model_cache_dir,
                variant="bf16",  # Use BF16 variant
            )

            # Move to GPU
            pipeline = pipeline.to(self.device)

            # Enable memory optimizations
            pipeline.enable_attention_slicing()

            # Enable xformers if available (RTX 5090 optimized)
            try:
                pipeline.enable_xformers_memory_efficient_attention()
                logger.info("Enabled xformers memory efficient attention")
            except Exception as e:
                logger.debug(f"xformers not available: {e}")

            # Optional: Compile with Torch 2.0+ for TensorRT optimization
            if settings.torch_compile:
                try:
                    # Compile for RTX 5090 TensorRT backend
                    pipeline.transformer = torch.compile(
                        pipeline.transformer,
                        mode="max-autotune",
                        fullgraph=True,
                    )
                    logger.info("Enabled torch.compile with max-autotune")
                except Exception as e:
                    logger.warning(f"Could not enable torch.compile: {e}")

            self._pipeline = pipeline
            self._is_loaded = True

            logger.info(f"Model loaded successfully on {self.device}")
            gpu_manager.cleanup()  # Clear loading cache

            return pipeline

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise ModelLoadError(f"Model loading failed: {e}")

    def apply_lora_style(
        self,
        style: CameraStyle,
    ) -> None:
        """
        Apply LoRA weights for camera style.

        Args:
            style: Camera style to apply
        """
        if self._pipeline is None:
            raise ModelLoadError("Model not loaded")

        lora_path, lora_weight = self._load_lora_weights(style)

        if lora_path and Path(lora_path).exists():
            try:
                # Load and fuse LoRA weights
                self._pipeline.load_lora_weights(lora_path)
                self._pipeline.fuse_lora(lora_weight)

                logger.info(
                    f"Applied LoRA style: {style.value} "
                    f"(weight: {lora_weight}, path: {lora_path})"
                )
            except Exception as e:
                logger.warning(f"Failed to load LoRA weights: {e}")

    def unload_model(self) -> None:
        """
        Unload model from GPU memory.

        Use this to free up GPU memory when idle.
        """
        if self._pipeline is None:
            return

        try:
            del self._pipeline
            self._pipeline = None
            self._is_loaded = False

            gpu_manager.cleanup()
            logger.info("Model unloaded from GPU")

        except Exception as e:
            logger.error(f"Failed to unload model: {e}")

    def get_pipeline(
        self,
        style: Optional[CameraStyle] = None,
    ) -> FluxImg2ImgPipeline:
        """
        Get or load the pipeline.

        Args:
            style: Optional camera style to apply

        Returns:
            Ready-to-use pipeline
        """
        if not self._is_loaded:
            self.load_model()

        if style is not None:
            self.apply_lora_style(style)

        return self._pipeline

    def get_model_info(self) -> dict:
        """
        Get model information for health checks.

        Returns:
            Dictionary with model info
        """
        return {
            "model_name": settings.model_name,
            "model_type": self._model_type,
            "device": str(self.device),
            "device_name": gpu_manager.device_name,
            "is_loaded": self._is_loaded,
            "torch_dtype": str(torch.bfloat16) if self._is_loaded else None,
            "compile_enabled": settings.torch_compile,
        }


# Global model loader instance
model_loader = ModelLoader()
