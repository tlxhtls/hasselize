"""
Enumerations for Hasselize AI Backend.

Defines all enum types used across the application.
"""

from enum import Enum


class CameraStyle(str, Enum):
    """Available camera style options (LoRA-based)."""

    HASSELBLAD = "hasselblad"
    LEICA_M = "leica_m"
    ZEISS = "zeiss"
    FUJIFILM_GFX = "fujifilm_gfx"


class ResolutionMode(str, Enum):
    """Output resolution modes."""

    PREVIEW = "preview"      # 512x512, fast
    STANDARD = "standard"    # 1024x1024, balanced
    HIGH = "high"            # 2048x2048, premium


class ModelType(str, Enum):
    """AI model types supported."""

    Z_IMAGE_TURBO = "z-image-turbo"
    FLUX_SCHNELL = "flux-schnell"


class TransformationStatus(str, Enum):
    """Transformation processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SubscriptionTier(str, Enum):
    """User subscription tiers."""

    FREE = "free"
    PREMIUM = "premium"
