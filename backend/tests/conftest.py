"""
Pytest configuration and fixtures
"""

import pytest
import os

# Set test environment before importing app
os.environ["DEBUG"] = "true"
os.environ["SUPABASE_URL"] = os.getenv("TEST_SUPABASE_URL", "https://test.supabase.co")
os.environ["SUPABASE_ANON_KEY"] = os.getenv("TEST_SUPABASE_ANON_KEY", "test_anon_key")
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = os.getenv(
    "TEST_SUPABASE_SERVICE_ROLE_KEY", "test_service_key"
)

from fastapi.testclient import TestClient
from app.core.config import Settings


@pytest.fixture(scope="session")
def test_settings():
    """Override settings for testing"""
    return Settings(
        debug=True,
        supabase_url=os.getenv("TEST_SUPABASE_URL", "https://test.supabase.co"),
        supabase_anon_key=os.getenv("TEST_SUPABASE_ANON_KEY", "test_anon_key"),
        supabase_service_role_key=os.getenv(
            "TEST_SUPABASE_SERVICE_ROLE_KEY", "test_service_key"
        ),
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
        secret_key="test-secret-key",
        jwt_secret_key="test-jwt-secret",
    )


@pytest.fixture(scope="session")
def test_client(test_settings):
    """Create test client"""
    from main import app

    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Mock authentication headers"""
    return {"Authorization": "Bearer test_token"}


@pytest.fixture
def mock_user():
    """Mock user data"""
    return {"id": "test-user-id", "email": "test@example.com", "role": "host"}
