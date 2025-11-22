"""
Health check and basic API tests
"""

import pytest


def test_health_check(test_client):
    """Test health endpoint"""
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_root_endpoint(test_client):
    """Test root endpoint"""
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Krib Host Dashboard API"
    assert data["status"] == "operational"


def test_simple_health(test_client):
    """Test simple health endpoint"""
    response = test_client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

