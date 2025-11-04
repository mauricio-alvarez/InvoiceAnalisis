"""Tests for API endpoints"""
import pytest
from unittest.mock import patch, Mock
from fastapi import status


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "healthy"


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_register_endpoint_validation():
    """Test registration endpoint with invalid data"""
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    
    # Test with missing password
    response = client.post("/api/auth/register", json={"email": "test@example.com"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Test with invalid email
    response = client.post("/api/auth/register", json={
        "email": "invalid-email",
        "password": "password123"
    })
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_verify_token_endpoint_unauthorized():
    """Test verify token endpoint without authentication"""
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    
    # Test without token
    response = client.post("/api/auth/verify-token")
    assert response.status_code == status.HTTP_403_FORBIDDEN
