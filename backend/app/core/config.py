"""
Configuration settings for Krib AI backend
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os
import secrets


def _require_env_in_production(var_name: str, default: Optional[str] = None) -> str:
    """Require environment variable in production, use default in development"""
    value = os.getenv(var_name, default)
    if not value and os.getenv("DEBUG", "true").lower() == "false":
        raise ValueError(f"{var_name} must be set in production environment")
    return value or ""


class Settings(BaseSettings):
    # Application
    app_name: str = "Krib AI API"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    secret_key: str = os.getenv("SECRET_KEY") or secrets.token_urlsafe(32)

    # JWT
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY") or secrets.token_urlsafe(32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )

    # Supabase
    supabase_url: str = os.getenv(
        "SUPABASE_URL", "https://bpomacnqaqzgeuahhlka.supabase.co"
    )
    supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY", "")
    supabase_service_role_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

    # Supabase S3-Compatible Storage
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    s3_bucket_name: Optional[str] = None
    s3_endpoint_url: Optional[str] = None

    # AI Services
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Monitoring and Observability
    sentry_dsn: Optional[str] = None
    enable_metrics: bool = True
    log_level: str = "INFO"

    # Rate Limiting
    enable_rate_limiting: bool = True
    default_rate_limit: str = "1000/hour"

    # Webhook Configuration
    webhook_secret_key: str = os.getenv("WEBHOOK_SECRET_KEY") or secrets.token_urlsafe(
        32
    )
    webhook_timeout: int = int(os.getenv("WEBHOOK_TIMEOUT", "30"))
    webhook_max_retries: int = int(os.getenv("WEBHOOK_MAX_RETRIES", "3"))

    # SSE Configuration
    sse_heartbeat_interval: int = int(os.getenv("SSE_HEARTBEAT_INTERVAL", "5"))
    sse_max_connections: int = int(os.getenv("SSE_MAX_CONNECTIONS", "1000"))

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = False

    def validate_production_config(self):
        """Validate that all required config is set for production"""
        if not self.debug:
            required = ["supabase_anon_key", "supabase_service_role_key"]
            missing = [key for key in required if not getattr(self, key)]
            if missing:
                raise ValueError(
                    f"Production requires these environment variables: {', '.join(missing)}"
                )


# Global settings instance
settings = Settings()

# Validate config on startup in production (skip in test environment)
if not settings.debug and not os.getenv("PYTEST_CURRENT_TEST"):
    settings.validate_production_config()
