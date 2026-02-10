"""
Request models for Hasselize AI Backend.

Pydantic models for validating incoming API requests.
"""

from base64 import b64decode
from io import BytesIO
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from .enums import CameraStyle, ResolutionMode


class TransformRequest(BaseModel):
    """
    Request model for image transformation.

    Accepts either:
    - image_base64: Base64-encoded image data
    - image_url: URL to fetch image from
    """

    # Style configuration
    style: CameraStyle = Field(
        default=CameraStyle.HASSELBLAD,
        description="Camera style to apply (LoRA model)",
    )
    resolution: ResolutionMode = Field(
        default=ResolutionMode.PREVIEW,
        description="Output resolution mode",
    )

    # Image input (one required)
    image_base64: Optional[str] = Field(
        default=None,
        description="Base64-encoded image data (with or without data URI prefix)",
    )
    image_url: Optional[str] = Field(
        default=None,
        description="URL to fetch image from (R2, S3, etc.)",
    )

    # Generation options
    seed: Optional[int] = Field(
        default=None,
        description="Random seed for reproducibility",
        ge=0,
        le=2**32 - 1,
    )
    negative_prompt: Optional[str] = Field(
        default=None,
        description="Custom negative prompt to override default",
    )

    @field_validator("image_base64", mode="before")
    @classmethod
    def clean_base64(cls, v: Optional[str]) -> Optional[str]:
        """Remove data URI prefix if present."""
        if v and "," in v:
            return v.split(",", 1)[1]
        return v

    @field_validator("image_base64")
    @classmethod
    def validate_base64(cls, v: Optional[str]) -> Optional[str]:
        """Validate base64 string can be decoded."""
        if v:
            try:
                b64decode(v, validate=True)
            except Exception as e:
                raise ValueError(f"Invalid base64 encoding: {e}")
        return v

    @field_validator("image_url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        """Basic URL validation."""
        if v:
            if not v.startswith(("http://", "https://")):
                raise ValueError("URL must start with http:// or https://")
        return v


class HealthCheckRequest(BaseModel):
    """Request model for health check endpoint."""

    detailed: bool = Field(
        default=False,
        description="Return detailed GPU and model information",
    )
