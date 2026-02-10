"""
Image processing utilities for Hasselize AI Backend.

Handles image preprocessing, validation, and postprocessing.
"""

import io
import logging
from typing import Optional, Tuple

import numpy as np
from PIL import Image
from typing_extensions import TypeAlias

logger = logging.getLogger(__name__)

# Type aliases
PILImage: TypeAlias = Image.Image


class ImageValidationError(Exception):
    """Raised when image validation fails."""

    pass


def load_image_from_bytes(data: bytes) -> PILImage:
    """
    Load PIL Image from bytes data.

    Args:
        data: Image data as bytes

    Returns:
        PIL Image instance

    Raises:
        ImageValidationError: If image loading fails
    """
    try:
        image = Image.open(io.BytesIO(data))
        # Convert to RGB if necessary
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGB")
        elif image.mode == "RGBA":
            # Convert RGBA to RGB with white background
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])  # Alpha channel as mask
            image = background

        return image

    except Exception as e:
        raise ImageValidationError(f"Failed to load image: {e}")


def resize_image(
    image: PILImage,
    target_size: Tuple[int, int],
    method: Image.Resampling = Image.Resampling.LANCZOS,
) -> PILImage:
    """
    Resize image while maintaining aspect ratio.

    Args:
        image: PIL Image
        target_size: Target (width, height)
        method: Resampling method

    Returns:
        Resized PIL Image
    """
    # Calculate aspect ratio
    original_width, original_height = image.size
    target_width, target_height = target_size

    # Determine resize dimensions
    width_ratio = target_width / original_width
    height_ratio = target_height / original_height
    ratio = min(width_ratio, height_ratio)

    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)

    # Resize image
    resized = image.resize((new_width, new_height), method)

    # Center crop if needed
    if new_width != target_width or new_height != target_height:
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        resized = resized.crop((left, top, right, bottom))

    return resized


def validate_image_size(
    image: PILImage,
    min_size: int = 64,
    max_size: int = 8192,
) -> None:
    """
    Validate image dimensions are within acceptable range.

    Args:
        image: PIL Image to validate
        min_size: Minimum dimension (width or height)
        max_size: Maximum dimension (width or height)

    Raises:
        ImageValidationError: If dimensions are invalid
    """
    width, height = image.size

    if width < min_size or height < min_size:
        raise ImageValidationError(
            f"Image too small: {width}x{height}. Minimum: {min_size}x{min_size}"
        )

    if width > max_size or height > max_size:
        raise ImageValidationError(
            f"Image too large: {width}x{height}. Maximum: {max_size}x{max_size}"
        )


def validate_image_format(image: PILImage) -> None:
    """
    Validate image format is supported.

    Args:
        image: PIL Image to validate

    Raises:
        ImageValidationError: If format is not supported
    """
    supported_formats = {"JPEG", "PNG", "WEBP"}
    image_format = image.format

    if image_format not in supported_formats:
        raise ImageValidationError(
            f"Unsupported format: {image_format}. Supported: {supported_formats}"
        )


def preprocess_image(
    image: PILImage,
    target_size: Optional[Tuple[int, int]] = None,
    normalize: bool = True,
) -> np.ndarray:
    """
    Preprocess image for model input.

    Args:
        image: PIL Image
        target_size: Target (width, height), or None to keep original
        normalize: Whether to normalize to [-1, 1]

    Returns:
        Preprocessed numpy array in shape (H, W, C)
    """
    # Resize if target size specified
    if target_size:
        image = resize_image(image, target_size)

    # Convert to numpy array
    image_array = np.array(image).astype(np.float32)

    # Normalize to [-1, 1] if requested
    if normalize:
        image_array = (image_array / 127.5) - 1.0

    return image_array


def postprocess_image(image_array: np.ndarray) -> PILImage:
    """
    Postprocess model output to PIL Image.

    Args:
        image_array: Model output array, typically in [-1, 1]

    Returns:
        PIL Image
    """
    # Denormalize from [-1, 1] to [0, 255]
    if image_array.min() < 0:
        image_array = (image_array + 1.0) * 127.5
    else:
        image_array = image_array * 255.0

    # Clip and convert to uint8
    image_array = np.clip(image_array, 0, 255).astype(np.uint8)

    # Create PIL Image
    return Image.fromarray(image_array)


def image_to_bytes(
    image: PILImage,
    format: str = "JPEG",
    quality: int = 95,
) -> bytes:
    """
    Convert PIL Image to bytes.

    Args:
        image: PIL Image
        format: Image format (JPEG, PNG, WEBP)
        quality: JPEG/WEBP quality (1-100)

    Returns:
        Image data as bytes
    """
    buffer = io.BytesIO()

    save_kwargs = {"format": format}
    if format in ("JPEG", "WEBP"):
        save_kwargs["quality"] = quality

    image.save(buffer, **save_kwargs)
    return buffer.getvalue()


def create_thumbnail(
    image: PILImage,
    size: Tuple[int, int] = (256, 256),
    quality: int = 85,
) -> bytes:
    """
    Create thumbnail image bytes.

    Args:
        image: Source PIL Image
        size: Thumbnail dimensions
        quality: JPEG quality

    Returns:
        Thumbnail bytes
    """
    thumbnail = resize_image(image, size)
    return image_to_bytes(thumbnail, format="JPEG", quality=quality)


def get_image_info(image: PILImage) -> dict:
    """
    Get image information.

    Args:
        image: PIL Image

    Returns:
        Dictionary with image metadata
    """
    return {
        "width": image.width,
        "height": image.height,
        "format": image.format,
        "mode": image.mode,
        "size_bytes": len(image_to_bytes(image)),
    }
