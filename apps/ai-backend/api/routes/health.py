"""
Health check endpoints for Hasselize AI Backend.

Provides GPU status, model info, and service health.
"""

from typing import Any

from fastapi import APIRouter, Depends, status

from core.gpu_manager import gpu_manager
from core.logging import logger
from models.requests import HealthCheckRequest
from models.responses import HealthCheckResponse
from services.model_loader import model_loader

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check service health and GPU status",
)
async def health_check(request: HealthCheckRequest = HealthCheckRequest()) -> dict[str, Any]:
    """
    Get service health status.

    Returns:
        Health status with GPU information
    """
    gpu_stats = gpu_manager.get_memory_stats()

    response = {
        "status": "healthy",
        "gpu_available": gpu_stats["gpu_available"],
        "gpu_memory_used_mb": gpu_stats["memory_used_mb"],
        "gpu_memory_total_mb": gpu_stats["memory_total_mb"],
        "model_loaded": model_loader.is_loaded,
        "version": "1.0.0",
    }

    # Add detailed info if requested
    if request.detailed:
        response.update(
            {
                "device_name": gpu_stats["device_name"],
                "memory_free_mb": gpu_stats["memory_free_mb"],
                "model_info": model_loader.get_model_info() if model_loader.is_loaded else None,
            }
        )

    return response


@router.get(
    "/health/gpu",
    summary="GPU status",
    description="Get detailed GPU memory and device information",
)
async def gpu_status() -> dict[str, Any]:
    """
    Get detailed GPU status.

    Returns:
        GPU statistics
    """
    return gpu_manager.get_memory_stats()


@router.get(
    "/health/model",
    summary="Model status",
    description="Get AI model loading status and info",
)
async def model_status() -> dict[str, Any]:
    """
    Get model status.

    Returns:
        Model information
    """
    return {
        "is_loaded": model_loader.is_loaded,
        "info": model_loader.get_model_info(),
    }
