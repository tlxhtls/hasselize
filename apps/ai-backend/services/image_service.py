"""
Image transformation service for Hasselize AI Backend.

Orchestrates the complete image transformation pipeline:
1. Image upload and preprocessing
2. Prompt engineering (Supabase + camera style)
3. AI inference with FLUX.1-Schnell
4. Postprocessing and storage

Spec (from docs/ai_plan.md):
- Model: FLUX.1-Schnell (FP4 quantized)
- Pipeline: img2img with Denoising Strength 0.3-0.4
- Resolution: 256x256 (minimal latency)
- Target: <1 second inference time
"""

import asyncio
import logging
import time
import uuid
from io import BytesIO
from typing import Optional

import numpy as np
import torch
from PIL import Image

from core.config import settings
from core.gpu_manager import gpu_manager
from models.enums import CameraStyle, ModelType, ResolutionMode, TransformationStatus
from models.requests import TransformRequest
from models.responses import TransformResponse
from services.model_loader import model_loader
from services.storage_service import StorageError, storage_service
from utils.image_utils import (
    ImageValidationError,
    create_thumbnail,
    image_to_bytes,
    load_image_from_bytes,
    resize_image,
    validate_image_format,
    validate_image_size,
)
from utils.prompt_builder import prompt_builder

logger = logging.getLogger(__name__)


class TransformationError(Exception):
    """Raised when transformation fails."""

    pass


class ImageService:
    """
    Main image transformation service.

    Orchestrates the complete pipeline:
    1. Load and validate image
    2. Build prompts for camera style
    3. Run FLUX.1-Schnell img2img inference
    4. Upload results to R2
    5. Return transformation response
    """

    # Resolution mapping (from docs/ai_plan.md: 256x256 for speed)
    RESOLUTION_MAP = {
        ResolutionMode.PREVIEW: (256, 256),
        ResolutionMode.STANDARD: (512, 512),
        ResolutionMode.HIGH: (1024, 1024),
    }

    # Denoising strength from spec: 0.3-0.4 for subject preservation
    DEFAULT_DENOISING_STRENGTH = 0.35
    DENOISING_STRENGTH_RANGE = (0.3, 0.4)

    def __init__(self):
        """Initialize image service."""
        self._ensure_model_loaded()

    def _ensure_model_loaded(self) -> None:
        """Ensure model is loaded on GPU."""
        if not model_loader.is_loaded:
            model_loader.load_model()

    async def transform_image(
        self,
        request: TransformRequest,
        image_data: bytes,
        user_id: Optional[str] = None,
    ) -> TransformResponse:
        """
        Transform image with camera style.

        Args:
            request: Transform request with style and options
            image_data: Original image bytes
            user_id: Optional user ID for authentication

        Returns:
            Transform response with image URLs

        Raises:
            TransformationError: If transformation fails
        """
        start_time = time.time()
        transformation_id = str(uuid.uuid4())

        try:
            # Step 1: Load and validate image
            logger.info(f"[{transformation_id}] Loading image...")
            original_image = load_image_from_bytes(image_data)
            validate_image_size(original_image)
            validate_image_format(original_image)

            # Step 2: Resize to target resolution (256x256 for speed)
            target_size = self.RESOLUTION_MAP.get(
                request.resolution,
                self.RESOLUTION_MAP[ResolutionMode.PREVIEW],
            )
            logger.info(f"[{transformation_id}] Resizing to {target_size}")
            resized_image = resize_image(original_image, target_size)

            # Step 3: Build prompts
            logger.info(f"[{transformation_id}] Building prompts for {request.style.value}")
            positive_prompt, negative_prompt = await prompt_builder.build_prompt_async(
                style=request.style,
                custom_negative=request.negative_prompt,
            )

            # Step 4: Apply LoRA style
            logger.info(f"[{transformation_id}] Applying LoRA style: {request.style.value}")
            pipeline = model_loader.get_pipeline(style=request.style)

            # Step 5: Run FLUX.1-Schnell img2img inference
            logger.info(f"[{transformation_id}] Running inference...")
            inference_start = time.time()

            result_image = await self._run_inference(
                pipeline=pipeline,
                image=resized_image,
                prompt=positive_prompt,
                negative_prompt=negative_prompt,
                seed=request.seed,
            )

            inference_time = (time.time() - inference_start) * 1000
            logger.info(f"[{transformation_id}] Inference completed in {inference_time:.0f}ms")

            # Step 6: Convert result to bytes
            result_bytes = image_to_bytes(result_image, format="JPEG", quality=95)
            thumbnail_bytes = create_thumbnail(result_image)

            # Step 7: Upload to R2
            logger.info(f"[{transformation_id}] Uploading to R2...")

            # Generate storage keys
            original_key = storage_service.generate_key(
                "original",
                filename=f"{transformation_id}.jpg",
            )
            transformed_key = storage_service.generate_key(
                "transformed",
                filename=f"{transformation_id}.jpg",
            )
            thumbnail_key = storage_service.generate_key(
                "thumbnails",
                filename=f"{transformation_id}.jpg",
            )

            # Upload original
            original_url = storage_service.upload_file(
                image_data,
                original_key,
                content_type="image/jpeg",
            )

            # Upload transformed
            transformed_url = storage_service.upload_file(
                result_bytes,
                transformed_key,
                content_type="image/jpeg",
            )

            # Upload thumbnail
            thumbnail_url = storage_service.upload_file(
                thumbnail_bytes,
                thumbnail_key,
                content_type="image/jpeg",
            )

            # Step 8: Build response
            total_time = (time.time() - start_time) * 1000

            response = TransformResponse(
                id=transformation_id,
                user_id=user_id,
                original_image_url=original_url,
                transformed_image_url=transformed_url,
                thumbnail_url=thumbnail_url,
                style=request.style,
                resolution=request.resolution,
                model_used=ModelType.FLUX_SCHNELL,
                seed=request.seed,
                processing_time_ms=int(total_time),
                status=TransformationStatus.COMPLETED,
            )

            logger.info(
                f"[{transformation_id}] Transformation completed in {total_time:.0f}ms"
            )

            return response

        except Exception as e:
            logger.error(f"[{transformation_id}] Transformation failed: {e}")
            raise TransformationError(f"Transformation failed: {e}")

    async def _run_inference(
        self,
        pipeline,
        image: Image.Image,
        prompt: str,
        negative_prompt: str,
        seed: Optional[int] = None,
        num_inference_steps: int = 4,  # FLUX.1-Schnell: 1-4 steps
    ) -> Image.Image:
        """
        Run FLUX.1-Schnell img2img inference.

        Args:
            pipeline: Loaded FLUX pipeline
            image: Source PIL Image
            prompt: Positive prompt
            negative_prompt: Negative prompt
            seed: Optional random seed
            num_inference_steps: Number of denoising steps (1-4 for speed)

        Returns:
            Transformed PIL Image
        """
        # Set random seed for reproducibility
        generator = None
        if seed is not None:
            generator = torch.Generator(device=gpu_manager.device).manual_seed(seed)

        # Run img2img pipeline
        # Denoising strength: 0.3-0.4 (from spec)
        with gpu_manager.memory_context(cleanup=False):
            result = pipeline(
                image=image,
                prompt=prompt,
                negative_prompt=negative_prompt,
                strength=self.DEFAULT_DENOISING_STRENGTH,  # 0.35 for subject preservation
                guidance_scale=1.0,  # FLUX.1-Schnell uses CFG=1.0
                num_inference_steps=num_inference_steps,
                generator=generator,
                output_type="pil",
            )

        return result.images[0]

    async def transform_from_url(
        self,
        request: TransformRequest,
        user_id: Optional[str] = None,
    ) -> TransformResponse:
        """
        Transform image fetched from URL.

        Args:
            request: Transform request with image_url
            user_id: Optional user ID

        Returns:
            Transform response
        """
        if not request.image_url:
            raise TransformationError("image_url is required")

        # Fetch image from URL
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.get(request.image_url) as response:
                if response.status != 200:
                    raise TransformationError(f"Failed to fetch image: {response.status}")
                image_data = await response.read()

        return await self.transform_image(request, image_data, user_id)


# Global image service instance
image_service = ImageService()
