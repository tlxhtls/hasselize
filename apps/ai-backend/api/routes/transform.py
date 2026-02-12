"""
Image transformation endpoints for Hasselize AI Backend.

Main API endpoint for transforming images with camera styles.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import ValidationError

from core.logging import logger
from core.security import rate_limit_dependency
from models.enums import CameraStyle, ResolutionMode
from models.requests import TransformRequest
from models.responses import TransformResponse
from services.image_service import TransformationError, image_service

router = APIRouter()


@router.post(
    "/transform",
    response_model=TransformResponse,
    status_code=status.HTTP_200_OK,
    summary="Transform image",
    description="Transform an image with camera style using FLUX.1-Schnell",
    dependencies=[Depends(rate_limit_dependency)],
)
async def transform_image(
    image: UploadFile = File(..., description="Image file to transform"),
    style: CameraStyle = Form(CameraStyle.HASSELBLAD, description="Camera style"),
    resolution: ResolutionMode = Form(
        ResolutionMode.PREVIEW,
        description="Output resolution (preview=256x256 for speed)",
    ),
    seed: Optional[int] = Form(None, description="Random seed for reproducibility"),
    negative_prompt: Optional[str] = Form(None, description="Custom negative prompt"),
) -> TransformResponse:
    """
    Transform image with camera style.

    Args:
        image: Uploaded image file
        style: Camera style to apply
        resolution: Output resolution mode
        seed: Optional random seed
        negative_prompt: Optional custom negative prompt

    Returns:
        Transform response with image URLs

    Raises:
        HTTPException: If transformation fails
    """
    try:
        # Read image data
        image_data = await image.read()

        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024
        if len(image_data) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Image too large. Maximum size: {max_size // (1024 * 1024)}MB",
            )

        # Build transform request
        request = TransformRequest(
            style=style,
            resolution=resolution,
            seed=seed,
            negative_prompt=negative_prompt,
        )

        # Run transformation
        logger.info(f"Transform request: style={style}, resolution={resolution}")
        result = await image_service.transform_image(request, image_data)

        return result

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {e}",
        )
    except TransformationError as e:
        logger.error(f"Transformation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.post(
    "/transform/url",
    response_model=TransformResponse,
    status_code=status.HTTP_200_OK,
    summary="Transform image from URL",
    description="Transform an image from URL with camera style",
    dependencies=[Depends(rate_limit_dependency)],
)
async def transform_image_from_url(
    request: TransformRequest,
) -> TransformResponse:
    """
    Transform image fetched from URL.

    Args:
        request: Transform request with image_url

    Returns:
        Transform response with image URLs
    """
    try:
        logger.info(f"Transform from URL: {request.image_url}")
        result = await image_service.transform_from_url(request)
        return result

    except TransformationError as e:
        logger.error(f"Transformation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
