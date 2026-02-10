"""
FastAPI application for Hasselize AI Backend.

Main application entry point with:
- Lifespan management for model loading/cleanup
- CORS middleware
- Exception handlers
- Route registration

Spec: FLUX.1-Schnell with img2img pipeline
Target: <1 second inference, <5 second total request time
"""

import logging
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from core.gpu_manager import gpu_manager
from core.logging import logger
from models.responses import ErrorResponse, ValidationErrorResponse

# Import routes
from api.routes import health, transform


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup (model loading) and shutdown (cleanup).
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")

    # Log GPU info
    gpu_stats = gpu_manager.get_memory_stats()
    logger.info(f"GPU Status: {gpu_stats}")

    # Preload model on startup (optional - can lazy load)
    try:
        from services.model_loader import model_loader

        model_loader.load_model()
        logger.info("Model preloaded successfully")
    except Exception as e:
        logger.warning(f"Model preload failed (will lazy load): {e}")

    yield

    # Shutdown
    logger.info("Shutting down...")

    # Unload model to free GPU memory
    try:
        from services.model_loader import model_loader

        model_loader.unload_model()
        logger.info("Model unloaded")
    except Exception as e:
        logger.error(f"Failed to unload model: {e}")

    # Cleanup GPU memory
    gpu_manager.cleanup()


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        Configured FastAPI app
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI-powered photography transformation backend",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # GZip compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Exception handlers
    register_exception_handlers(app)

    # Register routes
    register_routes(app)

    return app


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Handle validation errors."""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ValidationErrorResponse(
                error="validation_error",
                message="Request validation failed",
                details=[
                    {"field": ".".join(str(loc) for loc in error["loc"]), "message": error["msg"]}
                    for error in exc.errors()
                ],
            ).model_dump(),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request,
        exc: HTTPException,
    ) -> JSONResponse:
        """Handle HTTP exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error="http_error",
                message=exc.detail,
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle all other exceptions."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="internal_error",
                message="An unexpected error occurred",
                details={"detail": str(exc)} if settings.is_development else None,
            ).model_dump(),
        )


def register_routes(app: FastAPI) -> None:
    """Register API routes."""

    @app.get("/", tags=["root"])
    async def root():
        """Root endpoint."""
        return {
            "app": settings.app_name,
            "version": settings.app_version,
            "status": "running",
            "docs": "/docs",
        }

    # API routes
    app.include_router(
        health.router,
        prefix=settings.api_v1_prefix,
        tags=["health"],
    )

    app.include_router(
        transform.router,
        prefix=settings.api_v1_prefix,
        tags=["transform"],
    )


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )
