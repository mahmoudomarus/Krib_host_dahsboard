"""
API Key Management Routes
Admin endpoints for generating, viewing, and revoking API keys.

These endpoints are protected and only accessible by admin users.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel, Field
from app.api.dependencies import get_current_user
from app.services.api_key_service import api_key_service
from app.core.external_config import ExternalAPIConfig
from app.core.supabase_client import supabase_client
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# Request/Response Models
class CreateAPIKeyRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Display name for the key")
    description: Optional[str] = Field(None, max_length=500, description="Optional description")
    tier: str = Field("standard", description="Permission tier: read_only, standard, full_access")
    permissions: Optional[List[str]] = Field(None, description="Custom permissions (overrides tier)")
    rate_limit: int = Field(100, ge=10, le=1000, description="Requests per minute")
    expires_in_days: Optional[int] = Field(None, ge=1, le=365, description="Expiration in days")
    environment: str = Field("prod", description="Environment: prod, test, dev")


class APIKeyResponse(BaseModel):
    id: str
    key_prefix: str
    name: str
    description: Optional[str]
    tier: str
    permissions: List[str]
    rate_limit_per_minute: int
    is_active: bool
    last_used_at: Optional[str]
    total_requests: int
    expires_at: Optional[str]
    created_at: str


class CreateAPIKeyResponse(BaseModel):
    """Response when creating a new key - includes the actual key (shown ONCE)"""
    api_key: str = Field(..., description="The API key - SAVE THIS NOW, it won't be shown again!")
    key_info: APIKeyResponse


class UpdateAPIKeyRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    permissions: Optional[List[str]] = None
    rate_limit: Optional[int] = Field(None, ge=10, le=1000)
    is_active: Optional[bool] = None


async def verify_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Verify that the current user is an admin"""
    # Check if user has admin role
    try:
        result = (
            supabase_client.table("users")
            .select("role")
            .eq("id", current_user["id"])
            .execute()
        )
        
        if result.data and result.data[0].get("role") == "admin":
            return current_user
        
        # For now, also allow if user is the owner of any property (host)
        # In production, you'd want stricter admin checks
        property_result = (
            supabase_client.table("properties")
            .select("id")
            .eq("user_id", current_user["id"])
            .limit(1)
            .execute()
        )
        
        if property_result.data:
            return current_user
            
    except Exception as e:
        logger.error(f"Admin verification error: {e}")
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Admin access required"
    )


@router.post("/generate", response_model=CreateAPIKeyResponse)
async def generate_api_key(
    request: CreateAPIKeyRequest,
    current_user: dict = Depends(verify_admin_user)
):
    """
    Generate a new API key
    
    ⚠️ IMPORTANT: The API key is returned ONLY ONCE in this response.
    Save it immediately - it cannot be retrieved again!
    
    Tiers:
    - read_only: Search properties, check availability, view reviews
    - standard: read_only + messaging
    - full_access: All permissions including bookings and payments
    """
    try:
        # Validate tier
        valid_tiers = ["read_only", "standard", "full_access"]
        if request.tier not in valid_tiers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tier. Must be one of: {valid_tiers}"
            )
        
        # Validate permissions if provided
        if request.permissions:
            all_permissions = ExternalAPIConfig.get_all_permissions()
            invalid = [p for p in request.permissions if p not in all_permissions]
            if invalid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid permissions: {invalid}. Valid: {all_permissions}"
                )
        
        # Generate the key
        api_key, key_info = api_key_service.generate_key(
            name=request.name,
            description=request.description,
            tier=request.tier,
            permissions=request.permissions,
            rate_limit=request.rate_limit,
            created_by=current_user["id"],
            expires_in_days=request.expires_in_days,
            environment=request.environment
        )
        
        logger.info(f"API key generated by user {current_user['id']}: {key_info['key_prefix']}...")
        
        return CreateAPIKeyResponse(
            api_key=api_key,
            key_info=APIKeyResponse(
                id=key_info["id"],
                key_prefix=key_info["key_prefix"],
                name=key_info["name"],
                description=key_info["description"],
                tier=key_info["tier"],
                permissions=key_info["permissions"],
                rate_limit_per_minute=key_info["rate_limit_per_minute"],
                is_active=True,
                last_used_at=None,
                total_requests=0,
                expires_at=key_info["expires_at"],
                created_at=key_info["created_at"]
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate API key"
        )


@router.get("/", response_model=List[APIKeyResponse])
async def list_api_keys(
    include_revoked: bool = False,
    current_user: dict = Depends(verify_admin_user)
):
    """
    List all API keys
    
    Returns key metadata only - not the actual keys (which are never stored)
    """
    try:
        keys = api_key_service.list_keys(
            include_revoked=include_revoked,
            created_by=None  # Admins can see all keys
        )
        
        return [
            APIKeyResponse(
                id=key["id"],
                key_prefix=key["key_prefix"],
                name=key["name"],
                description=key.get("description"),
                tier=key["tier"],
                permissions=key["permissions"],
                rate_limit_per_minute=key["rate_limit_per_minute"],
                is_active=key["is_active"],
                last_used_at=key.get("last_used_at"),
                total_requests=key.get("total_requests", 0),
                expires_at=key.get("expires_at"),
                created_at=key["created_at"]
            )
            for key in keys
        ]
        
    except Exception as e:
        logger.error(f"Failed to list API keys: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list API keys"
        )


@router.get("/{key_id}", response_model=APIKeyResponse)
async def get_api_key(
    key_id: str,
    current_user: dict = Depends(verify_admin_user)
):
    """Get details for a specific API key"""
    try:
        key = api_key_service.get_key_by_id(key_id)
        
        if not key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        return APIKeyResponse(
            id=key["id"],
            key_prefix=key["key_prefix"],
            name=key["name"],
            description=key.get("description"),
            tier=key["tier"],
            permissions=key["permissions"],
            rate_limit_per_minute=key["rate_limit_per_minute"],
            is_active=key["is_active"],
            last_used_at=key.get("last_used_at"),
            total_requests=key.get("total_requests", 0),
            expires_at=key.get("expires_at"),
            created_at=key["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get API key"
        )


@router.put("/{key_id}", response_model=APIKeyResponse)
async def update_api_key(
    key_id: str,
    request: UpdateAPIKeyRequest,
    current_user: dict = Depends(verify_admin_user)
):
    """Update API key metadata (name, description, permissions, rate limit)"""
    try:
        # Validate permissions if provided
        if request.permissions:
            all_permissions = ExternalAPIConfig.get_all_permissions()
            invalid = [p for p in request.permissions if p not in all_permissions]
            if invalid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid permissions: {invalid}"
                )
        
        key = api_key_service.update_key(
            key_id=key_id,
            name=request.name,
            description=request.description,
            permissions=request.permissions,
            rate_limit=request.rate_limit,
            is_active=request.is_active
        )
        
        if not key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        return APIKeyResponse(
            id=key["id"],
            key_prefix=key["key_prefix"],
            name=key["name"],
            description=key.get("description"),
            tier=key["tier"],
            permissions=key["permissions"],
            rate_limit_per_minute=key["rate_limit_per_minute"],
            is_active=key["is_active"],
            last_used_at=key.get("last_used_at"),
            total_requests=key.get("total_requests", 0),
            expires_at=key.get("expires_at"),
            created_at=key["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update API key"
        )


@router.delete("/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: dict = Depends(verify_admin_user)
):
    """
    Revoke an API key
    
    This immediately disables the key. It cannot be undone.
    """
    try:
        success = api_key_service.revoke_key(
            key_id=key_id,
            revoked_by=current_user["id"]
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        logger.info(f"API key revoked by user {current_user['id']}: {key_id}")
        
        return {"message": "API key revoked successfully", "key_id": key_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to revoke API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke API key"
        )


@router.get("/{key_id}/usage")
async def get_api_key_usage(
    key_id: str,
    days: int = 30,
    current_user: dict = Depends(verify_admin_user)
):
    """Get usage statistics for an API key"""
    try:
        stats = api_key_service.get_usage_stats(key_id, days)
        
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get API key usage: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get usage statistics"
        )


@router.get("/permissions/all")
async def list_all_permissions(
    current_user: dict = Depends(verify_admin_user)
):
    """List all available permissions"""
    return {
        "permissions": ExternalAPIConfig.get_all_permissions(),
        "tiers": {
            "read_only": ExternalAPIConfig.get_tier_permissions("read_only"),
            "standard": ExternalAPIConfig.get_tier_permissions("standard"),
            "full_access": ExternalAPIConfig.get_tier_permissions("full_access"),
        }
    }

