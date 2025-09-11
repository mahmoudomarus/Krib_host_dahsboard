"""
Configuration settings for Krib AI backend
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Application
    app_name: str = "Krib AI API"
    debug: bool = True
    secret_key: str = "your-super-secret-key-change-in-production"
    
    # JWT
    jwt_secret_key: str = "your-jwt-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    # Supabase
    supabase_url: str = "https://bpomacnqaqzgeuahhlka.supabase.co"
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    
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
    redis_url: str = "redis://localhost:6379"
    
    # Monitoring and Observability
    sentry_dsn: Optional[str] = None
    enable_metrics: bool = True
    log_level: str = "INFO"
    
    # Rate Limiting
    enable_rate_limiting: bool = True
    default_rate_limit: str = "1000/hour"
    
    # Webhook Configuration
    webhook_secret_key: str = "webhook-secret-key-change-in-production"
    webhook_timeout: int = 30
    webhook_max_retries: int = 3
    
    # SSE Configuration
    sse_heartbeat_interval: int = 5
    sse_max_connections: int = 1000
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
