"""
Security utilities for Hasselize AI Backend.

Provides authentication, authorization, and security utilities.
"""

import os
from typing import Optional

from jose import JWTError, jwt
from pydantic import BaseModel


class SupabaseToken(BaseModel):
    """
    Supabase JWT token claims.

    Extracted and validated from Authorization header.
    """

    sub: str  # User ID
    email: Optional[str] = None
    role: str = "authenticated"
    aud: str = "authenticated"


class SecurityError(Exception):
    """Security-related exception."""

    def __init__(self, message: str, code: str = "security_error"):
        self.message = message
        self.code = code
        super().__init__(message)


def verify_supabase_token(token: str) -> SupabaseToken:
    """
    Verify and decode Supabase JWT token.

    Args:
        token: JWT token string (without 'Bearer ' prefix)

    Returns:
        Decoded token claims

    Raises:
        SecurityError: If token is invalid or expired
    """
    try:
        from .config import settings

        # Decode JWT (Supabase uses HS256)
        # In production, you might want to use JWKS endpoint
        payload = jwt.decode(
            token,
            key=settings.supabase_service_role_key,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )

        return SupabaseToken(**payload)

    except JWTError as e:
        raise SecurityError(f"Invalid token: {e}", code="invalid_token")
    except Exception as e:
        raise SecurityError(f"Token verification failed: {e}", code="verification_failed")


def extract_token_from_header(authorization: str) -> str:
    """
    Extract JWT token from Authorization header.

    Args:
        authorization: Authorization header value

    Returns:
        JWT token string

    Raises:
        SecurityError: If header format is invalid
    """
    if not authorization:
        raise SecurityError("Missing Authorization header", code="missing_header")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise SecurityError(
            "Invalid Authorization header format. Expected: Bearer <token>",
            code="invalid_header_format",
        )

    return parts[1]


def is_valid_origin(origin: str) -> bool:
    """
    Check if origin is in allowed list.

    Args:
        origin: Origin URL to check

    Returns:
        True if origin is allowed
    """
    from .config import settings

    allowed_origins = settings.cors_origins
    return origin in allowed_origins


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for filesystem
    """
    # Remove path separators
    filename = os.path.basename(filename)

    # Remove dangerous characters
    filename = "".join(
        c for c in filename if c.isalnum() or c in "._-"
    )

    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[: 255 - len(ext)] + ext

    return filename or "unnamed"


def generate_secure_token(length: int = 32) -> str:
    """
    Generate cryptographically secure random token.

    Args:
        length: Token length in bytes

    Returns:
        Hex-encoded token
    """
    import secrets

    return secrets.token_hex(length)
