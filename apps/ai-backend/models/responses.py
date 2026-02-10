"""
Response models for Hasselize AI Backend.

Pydantic models for API response serialization.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from .enums import CameraStyle, ModelType, ResolutionMode, TransformationStatus


class HealthCheckResponse(BaseModel):
    """Health check response with GPU status."""

    status: str = Field(description="Service health status", example="healthy")
    gpu_available: bool = Field(description="Whether GPU is available")
    gpu_memory_used_mb: Optional[int] = Field(
        default=None,
        description="GPU memory used in MB",
    )
    gpu_memory_total_mb: Optional[int] = Field(
        default=None,
        description="Total GPU memory in MB",
    )
    model_loaded: bool = Field(description="Whether AI model is loaded")
    model_name: Optional[str] = Field(
        default=None,
        description="Name of loaded model",
    )
    version: str = Field(description="API version")


class TransformResponse(BaseModel):
    """Response model for image transformation."""

    # Identifiers
    id: str = Field(description="Unique transformation ID")
    user_id: Optional[str] = Field(
        default=None,
        description="User ID if authenticated",
    )

    # Images
    original_image_url: str = Field(description="URL to original image")
    transformed_image_url: str = Field(description="URL to transformed image")
    thumbnail_url: Optional[str] = Field(
        default=None,
        description="URL to thumbnail image",
    )

    # Metadata
    style: CameraStyle = Field(description="Camera style applied")
    resolution: ResolutionMode = Field(description="Resolution mode used")
    model_used: ModelType = Field(description="AI model used for transformation")
    seed: Optional[int] = Field(
        default=None,
        description="Seed used for generation",
    )

    # Performance
    processing_time_ms: int = Field(
        description="Total processing time in milliseconds",
    )

    # Status
    status: TransformationStatus = Field(
        default=TransformationStatus.COMPLETED,
        description="Transformation status",
    )

    # Timestamps
    created_at: datetime = Field(description="Creation timestamp")


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(description="Error type", example="validation_error")
    message: str = Field(description="Human-readable error message")
    details: Optional[dict[str, Any]] = Field(
        default=None,
        description="Additional error details",
    )


class ValidationErrorResponse(ErrorResponse):
    """Validation error response with field details."""

    error: str = "validation_error"
    details: list[dict[str, str]] = Field(
        default_factory=list,
        description="List of validation errors per field",
    )
