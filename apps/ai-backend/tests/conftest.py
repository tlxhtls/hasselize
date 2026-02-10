"""
Pytest configuration and fixtures for Hasselize AI Backend.
"""

import os
import pytest
from typing import AsyncGenerator, Generator

from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture
def client() -> Generator:
    """
    Create a test client for the FastAPI app.
    """
    from fastapi.testclient import TestClient

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def test_image_bytes() -> bytes:
    """
    Create test image bytes for testing.

    Returns a small 64x64 JPEG image.
    """
    from PIL import Image
    from io import BytesIO

    # Create a simple test image
    img = Image.new('RGB', (64, 64), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    return img_bytes.getvalue()


@pytest.fixture
def mock_settings(monkeypatch) -> None:
    """
    Mock environment variables for testing.
    """
    monkeypatch.setenv('ENVIRONMENT', 'testing')
    monkeypatch.setenv('SECRET_KEY', 'test-secret-key')
    monkeypatch.setenv('SUPABASE_URL', 'https://test.supabase.co')
    monkeypatch.setenv('SUPABASE_SERVICE_ROLE_KEY', 'test-key')
    monkeypatch.setenv('R2_ENDPOINT_URL', 'https://test.r2.dev')
    monkeypatch.setenv('R2_ACCESS_KEY_ID', 'test-key')
    monkeypatch.setenv('R2_SECRET_ACCESS_KEY', 'test-secret')
    monkeypatch.setenv('R2_BUCKET_NAME', 'test-bucket')
