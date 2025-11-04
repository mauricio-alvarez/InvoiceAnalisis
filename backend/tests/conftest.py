"""Pytest configuration and fixtures"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def mock_firebase_user():
    """Mock Firebase user for testing"""
    return {
        'uid': 'test-user-123',
        'email': 'test@example.com',
        'email_verified': True,
        'custom_claims': {'role': 'user'}
    }


@pytest.fixture
def mock_admin_user():
    """Mock admin user for testing"""
    return {
        'uid': 'admin-user-123',
        'email': 'admin@example.com',
        'email_verified': True,
        'custom_claims': {'role': 'admin'}
    }
