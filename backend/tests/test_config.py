"""
Configuration tests
"""

import pytest
import os
from app.core.config import Settings


def test_config_defaults():
    """Test configuration defaults"""
    settings = Settings()
    
    assert settings.app_name == "Krib AI API"
    assert settings.algorithm == "HS256"
    assert settings.access_token_expire_minutes == 60
    assert settings.enable_rate_limiting is True


def test_config_from_env(monkeypatch):
    """Test configuration from environment variables"""
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("SUPABASE_URL", "https://custom.supabase.co")
    
    settings = Settings()
    
    assert settings.debug is False
    assert settings.supabase_url == "https://custom.supabase.co"


def test_production_config_validation(monkeypatch):
    """Test production config validation"""
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "")
    
    settings = Settings()
    
    with pytest.raises(ValueError) as exc_info:
        settings.validate_production_config()
    
    assert "supabase_anon_key" in str(exc_info.value)


def test_secure_secret_generation(monkeypatch):
    """Test that secrets are generated securely"""
    # Clear environment variables to test auto-generation
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    monkeypatch.delenv("WEBHOOK_SECRET_KEY", raising=False)
    
    # Create settings instance
    settings = Settings()
    
    # Secrets should be auto-generated with sufficient length
    assert len(settings.secret_key) >= 32, f"secret_key length is {len(settings.secret_key)}, should be >= 32"
    assert len(settings.jwt_secret_key) >= 32, f"jwt_secret_key length is {len(settings.jwt_secret_key)}, should be >= 32"
    assert len(settings.webhook_secret_key) >= 32, f"webhook_secret_key length is {len(settings.webhook_secret_key)}, should be >= 32"
    
    # Secrets should not be placeholders
    assert "change-in-production" not in settings.secret_key
    assert "your-" not in settings.jwt_secret_key
    assert "your-" not in settings.secret_key

