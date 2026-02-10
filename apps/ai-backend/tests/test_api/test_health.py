"""
Health check endpoint tests.
"""

import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """Test basic health check endpoint."""
    response = client.get('/api/v1/health')

    assert response.status_code == 200
    data = response.json()

    assert 'status' in data
    assert data['status'] == 'healthy'
    assert 'gpu_available' in data
    assert 'model_loaded' in data


def test_health_check_detailed(client: TestClient) -> None:
    """Test detailed health check endpoint."""
    response = client.get('/api/v1/health?detailed=true')

    assert response.status_code == 200
    data = response.json()

    assert 'status' in data
    assert 'device_name' in data or data.get('device_name') is None


def test_gpu_status(client: TestClient) -> None:
    """Test GPU status endpoint."""
    response = client.get('/api/v1/health/gpu')

    assert response.status_code == 200
    data = response.json()

    assert 'gpu_available' in data
    assert 'memory_used_mb' in data or data['memory_used_mb'] is None


def test_model_status(client: TestClient) -> None:
    """Test model status endpoint."""
    response = client.get('/api/v1/health/model')

    assert response.status_code == 200
    data = response.json()

    assert 'is_loaded' in data
    assert 'info' in data
