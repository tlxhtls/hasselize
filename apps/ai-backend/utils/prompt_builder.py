"""
Prompt building utilities for Hasselize AI Backend.

Implements 3-tier prompt management strategy:
- Tier 1: .env file (simple system prompts)
- Tier 2: Supabase database (recommended, A/B testing)
- Tier 3: Local JSON files (git-ignored, complex prompts)
"""

import json
import logging
from pathlib import Path
from typing import Optional

from core.config import settings
from models.enums import CameraStyle

logger = logging.getLogger(__name__)


# Default prompts (Tier 1: .env fallback)
DEFAULT_PROMPTS = {
    CameraStyle.HASSELBLAD: {
        "positive": "medium format photography, hasselblad x2d, 100mm lens, f/2.8, exceptional sharpness, natural depth of field, professional color grading, 100 megapixel look",
        "negative": "blurry, noise, distorted, oversaturated, artificial lighting, poor composition",
    },
    CameraStyle.LEICA_M: {
        "positive": "leica m rangefinder photography, summicron 35mm f/2, high contrast, candid moments, street photography, cinematic color, film grain aesthetic",
        "negative": "blurry, oversaturated, hdr, digital look, poor focus",
    },
    CameraStyle.ZEISS: {
        "positive": "zeiss otus lens photography, exceptional sharpness, micro contrast, t* coating, natural colors, professional studio lighting, commercial photography",
        "negative": "soft focus, blur, chromatic aberration, oversaturated",
    },
    CameraStyle.FUJIFILM_GFX: {
        "positive": "fujifilm gfx medium format, film simulation, velvia colors, large sensor look, professional portrait, natural skin tones, shallow depth of field",
        "negative": "digital, artificial colors, oversaturated, poor composition",
    },
}


class PromptBuilder:
    """
    Builds prompts for image transformation.

    Tier Strategy:
    1. Check local JSON (Tier 3) - overrides everything
    2. Query Supabase (Tier 2) - A/B testing, versioned
    3. Use .env defaults (Tier 1) - fallback
    """

    def __init__(self):
        """Initialize prompt builder."""
        self._supabase_client = None
        self._local_prompts_cache: Optional[dict] = None

    def _get_local_prompts_path(self) -> Optional[Path]:
        """
        Get path to local prompts JSON file (Tier 3).

        Returns:
            Path if file exists, None otherwise
        """
        config_path = Path(__file__).parent.parent / "config" / "secret_prompts.json"
        if config_path.exists():
            logger.info(f"Using local prompts from {config_path}")
            return config_path
        return None

    def _load_local_prompts(self) -> dict:
        """
        Load prompts from local JSON file (Tier 3).

        Returns:
            Dictionary of prompts by style
        """
        if self._local_prompts_cache is not None:
            return self._local_prompts_cache

        local_path = self._get_local_prompts_path()
        if local_path is None:
            self._local_prompts_cache = {}
            return self._local_prompts_cache

        try:
            with open(local_path) as f:
                self._local_prompts_cache = json.load(f)
            logger.info(f"Loaded local prompts from {local_path}")
            return self._local_prompts_cache

        except Exception as e:
            logger.error(f"Failed to load local prompts: {e}")
            self._local_prompts_cache = {}
            return self._local_prompts_cache

    def _get_supabase_client(self):
        """
        Get or create Supabase client for Tier 2 prompts.

        Returns:
            Supabase client or None if not configured
        """
        if self._supabase_client is not None:
            return self._supabase_client

        try:
            from supabase import create_client

            self._supabase_client = create_client(
                settings.supabase_url,
                settings.supabase_service_role_key,
            )
            logger.info("Supabase client initialized for prompts")
            return self._supabase_client

        except ImportError:
            logger.warning("Supabase client not available, using default prompts")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            return None

    async def fetch_prompt_from_supabase(
        self,
        style: CameraStyle,
    ) -> Optional[dict]:
        """
        Fetch active prompt from Supabase (Tier 2).

        Args:
            style: Camera style to fetch prompt for

        Returns:
            Prompt dict with 'content' and 'negative_prompt', or None
        """
        client = self._get_supabase_client()
        if client is None:
            return None

        try:
            # Query active prompt for this camera style
            response = (
                client.table("prompts")
                .select("content", "negative_prompt")
                .join(
                    "camera_styles",
                    "camera_style_id",
                    "id",
                )
                .eq("camera_styles.slug", style.value)
                .eq("is_active", True)
                .order("created_at", desc=True)
                .limit(1)
                .execute()

            if response.data:
                prompt_data = response.data[0]
                return {
                    "positive": prompt_data["content"],
                    "negative": prompt_data.get("negative_prompt"),
                }

            return None

        except Exception as e:
            logger.error(f"Failed to fetch prompt from Supabase: {e}")
            return None

    def build_prompt(
        self,
        style: CameraStyle,
        custom_positive: Optional[str] = None,
        custom_negative: Optional[str] = None,
    ) -> tuple[str, str]:
        """
        Build complete prompt for image transformation.

        Priority:
        1. Custom overrides (parameters)
        2. Local JSON (Tier 3)
        3. Supabase (Tier 2) - async version available
        4. Default prompts (Tier 1)

        Args:
            style: Camera style to apply
            custom_positive: Custom positive prompt override
            custom_negative: Custom negative prompt override

        Returns:
            Tuple of (positive_prompt, negative_prompt)
        """
        # Use custom prompts if provided
        if custom_positive or custom_negative:
            return (
                custom_positive or DEFAULT_PROMPTS[style]["positive"],
                custom_negative or DEFAULT_PROMPTS[style]["negative"],
            )

        # Check local JSON (Tier 3)
        local_prompts = self._load_local_prompts()
        if style.value in local_prompts:
            prompt_data = local_prompts[style.value]
            logger.debug(f"Using local JSON prompt for {style.value}")
            return (
                prompt_data.get("positive", DEFAULT_PROMPTS[style]["positive"]),
                prompt_data.get("negative", DEFAULT_PROMPTS[style]["negative"]),
            )

        # Use default prompts (Tier 1)
        # Note: For Supabase (Tier 2), use async fetch_prompt_from_supabase
        logger.debug(f"Using default prompt for {style.value}")
        return (
            DEFAULT_PROMPTS[style]["positive"],
            DEFAULT_PROMPTS[style]["negative"],
        )

    async def build_prompt_async(
        self,
        style: CameraStyle,
        custom_positive: Optional[str] = None,
        custom_negative: Optional[str] = None,
    ) -> tuple[str, str]:
        """
        Async version that checks Supabase (Tier 2) before defaults.

        Priority:
        1. Custom overrides
        2. Local JSON (Tier 3)
        3. Supabase (Tier 2)
        4. Defaults (Tier 1)

        Args:
            style: Camera style to apply
            custom_positive: Custom positive prompt override
            custom_negative: Custom negative prompt override

        Returns:
            Tuple of (positive_prompt, negative_prompt)
        """
        # Use custom prompts if provided
        if custom_positive or custom_negative:
            return (
                custom_positive or DEFAULT_PROMPTS[style]["positive"],
                custom_negative or DEFAULT_PROMPTS[style]["negative"],
            )

        # Check local JSON (Tier 3)
        local_prompts = self._load_local_prompts()
        if style.value in local_prompts:
            prompt_data = local_prompts[style.value]
            return (
                prompt_data.get("positive", DEFAULT_PROMPTS[style]["positive"]),
                prompt_data.get("negative", DEFAULT_PROMPTS[style]["negative"]),
            )

        # Check Supabase (Tier 2)
        supabase_prompt = await self.fetch_prompt_from_supabase(style)
        if supabase_prompt:
            logger.debug(f"Using Supabase prompt for {style.value}")
            return (
                supabase_prompt["positive"],
                supabase_prompt["negative"] or DEFAULT_PROMPTS[style]["negative"],
            )

        # Fall back to defaults (Tier 1)
        logger.debug(f"Using default prompt for {style.value}")
        return (
            DEFAULT_PROMPTS[style]["positive"],
            DEFAULT_PROMPTS[style]["negative"],
        )


# Global prompt builder instance
prompt_builder = PromptBuilder()
