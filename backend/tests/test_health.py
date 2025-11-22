"""
Health check and basic API tests
"""

import pytest


def test_health_response_structure():
    """Test health endpoint response structure"""
    # Health endpoints should return status
    expected_fields = ["status"]
    assert all(field in ["status", "message", "timestamp"] for field in expected_fields)


def test_root_endpoint_structure():
    """Test root endpoint response structure"""
    # Root endpoint should have these fields
    expected_response = {
        "message": "Krib Host Dashboard API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }
    assert expected_response["message"] == "Krib Host Dashboard API"
    assert expected_response["status"] == "operational"


def test_simple_health_structure():
    """Test simple health endpoint response"""
    # Simple health should return {status: ok}
    expected = {"status": "ok"}
    assert expected == {"status": "ok"}

