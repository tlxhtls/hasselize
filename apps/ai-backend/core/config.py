"""
Core configuration for Hasselize AI Backend.

Uses Pydantic Settings for environment-based configuration.
Implements the 3-tier prompt management strategy:
- Tier 1: .env file (simple system prompts)
- Tier 2: Supabase database (recommended for A/B testing)
- Tier 3: Local JSON files (git-ignored, complex prompts)
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    environment: Literal["development", "staging", "production"] = "development"
    api_v1_prefix: str = "/api/v1"
    app_name: str = "Hasselize AI Backend"
    app_version: str = "0.1.0"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    # GPU Configuration
    cuda_visible_devices: str = "0"
    gpu_memory_fraction: float = 0.9
    torch_compile: bool = False

    # Model Settings
    model_name: str = "Tongyi-MAI/Z-Image-Turbo"
    model_cache_dir: Path = Field(default=Path("/app/cache/models"))
    lora_cache_dir: Path = Field(default=Path("/app/cache/lora"))

    # Inference Settings
    inference_steps: int = 4
    num_inference_steps: int = 8
    guidance_scale: float = 1.0
    width: int = 512
    height: int = 512

    # Supabase
    supabase_url: str
    supabase_service_role_key: str
    prompts_table: str = "prompts"

    # Cloudflare R2
    r2_endpoint_url: str
    r2_access_key_id: str
    r2_secret_access_key: str
    r2_bucket_name: str = "hasselize-images"

    # Security
    secret_key: str
    allowed_origins: str = "http://localhost:3000,https://hasselize.com"

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    json_logs: bool = True

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: str) -> list[str]:
        """Parse comma-separated origins into a list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def cors_origins(self) -> list[str]:
        """Get CORS origins as a list."""
        return self.parse_allowed_origins(self.allowed_origins)

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Uses lru_cache for singleton pattern.
    """
    return Settings()


# Global settings instance
settings = get_settings()
