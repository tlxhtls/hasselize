"""
Security utilities for Hasselize AI Backend.

Provides authentication, authorization, and security utilities.
"""

import os
import time
from collections import defaultdict
from threading import Lock
from typing import Optional

from fastapi import HTTPException, Request, status
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
    filename = "".join(c for c in filename if c.isalnum() or c in "._-")

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


class RateLimiter:
    """Simple in-memory sliding window limiter."""

    def __init__(self, requests_limit: int, window_seconds: int):
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self._requests: defaultdict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        window_start = now - self.window_seconds

        with self._lock:
            recent = [ts for ts in self._requests[client_id] if ts > window_start]
            self._requests[client_id] = recent

            if len(recent) >= self.requests_limit:
                return False

            self._requests[client_id].append(now)
            return True


def _resolve_client_ip(request: Request) -> str:
    """Resolve client identity from request headers/socket."""
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()

    x_real_ip = request.headers.get("x-real-ip")
    if x_real_ip:
        return x_real_ip.strip()

    if request.client and request.client.host:
        return request.client.host

    return "unknown"


def _create_rate_limiter() -> RateLimiter:
    from .config import settings

    return RateLimiter(
        requests_limit=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
    )


rate_limiter = _create_rate_limiter()


async def rate_limit_dependency(request: Request) -> None:
    """FastAPI dependency for transform endpoint throttling."""
    client_id = _resolve_client_ip(request)

    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again shortly.",
        )
