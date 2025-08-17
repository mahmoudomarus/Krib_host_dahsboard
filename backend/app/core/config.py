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
    supabase_anon_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJwb21hY25xYXF6Z2V1YWhobGthIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU0NTcyMjUsImV4cCI6MjA3MTAzMzIyNX0.wiDqoFa0KjqE_pRnZIGILmpVJ_3-xZb4dSURCyzDNTs"
    supabase_service_role_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJwb21hY25xYXF6Z2V1YWhobGthIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTQ1NzIyNSwiZXhwIjoyMDcxMDMzMjI1fQ.Esc_wEXe2WnbDiMpsHa3Za9eon6BVjdFYzBXftPBWAc"
    
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
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
