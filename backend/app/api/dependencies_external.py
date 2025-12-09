"""
External API dependencies for third-party integrations
Authentication for external AI platforms and service accounts

API keys are validated against the database, not hardcoded values.
"""

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging
from app.core.supabase_client import supabase_client
from app.services.api_key_service import api_key_service

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def verify_external_api_key(authorization: str = Header(...)):
    """
    Verify external API key for third-party integrations

    Validates the API key against the database (hashed keys).
    API keys are never stored in code - they're generated and stored
    securely in the api_keys table.

    Args:
        authorization: Bearer token from Authorization header

    Returns:
        Service account info with permissions

    Raises:
        HTTPException: If API key is invalid or expired
    """
    try:
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format. Use 'Bearer <api_key>'",
                headers={"WWW-Authenticate": "Bearer"},
            )

        api_key = authorization[7:]  # Remove "Bearer " prefix

        # Validate against database (checks hash, expiration, active status)
        is_valid, key_info = api_key_service.validate_key(api_key)

        if not is_valid or not key_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired API key",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Log the API access
        logger.info(
            f"External API access granted: {key_info['key_prefix']}... ({key_info['name']})"
        )

        return {
            "key_id": key_info["id"],
            "service_name": key_info["name"],
            "key_prefix": key_info["key_prefix"],
            "permissions": key_info["permissions"],
            "tier": key_info["tier"],
            "rate_limit": key_info["rate_limit_per_minute"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"External API authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate API credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_external_service_context(
    service_account: dict = Depends(verify_external_api_key),
) -> dict:
    """
    Get service context for external API calls
    """
    return {
        "service_name": service_account["service_name"],
        "is_external": True,
        "permissions": service_account["permissions"],
    }


async def verify_property_access_external(
    property_id: str, service_context: dict
) -> dict:
    """
    Verify that a property exists and is publicly accessible for external services
    Only returns active properties
    """
    try:
        result = (
            supabase_client.table("properties")
            .select("*")
            .eq("id", property_id)
            .eq("status", "active")
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found or not available",
            )

        property_data = result.data[0]

        # Get user/host info for the property
        host_result = (
            supabase_client.table("users")
            .select("id, name, email, created_at")
            .eq("id", property_data["user_id"])
            .execute()
        )

        if host_result.data:
            property_data["host_info"] = host_result.data[0]

        return property_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Property access verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify property access",
        )
