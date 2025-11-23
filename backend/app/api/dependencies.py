"""
FastAPI dependencies for authentication and authorization
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.supabase_client import supabase_client
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Get current authenticated user from JWT token

    Args:
        credentials: HTTP Bearer token from request header

    Returns:
        User data dictionary

    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        # Extract token from credentials
        token = credentials.credentials

        # Verify token with Supabase
        user_response = supabase_client.auth.get_user(token)

        if not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = user_response.user

        # Get additional user profile data
        profile_result = (
            supabase_client.table("users").select("*").eq("id", user.id).execute()
        )

        if profile_result.data:
            # Return merged user data
            profile = profile_result.data[0]
            return {
                "id": user.id,
                "email": user.email,
                "name": profile.get("name", user.user_metadata.get("name", "")),
                "phone": profile.get("phone"),
                "avatar_url": profile.get("avatar_url"),
                "settings": profile.get("settings", {}),
                "total_revenue": profile.get("total_revenue", 0),
                "created_at": profile.get("created_at"),
                "updated_at": profile.get("updated_at"),
            }
        else:
            # Create profile if it doesn't exist (for OAuth users)
            profile_data = {
                "id": user.id,
                "name": user.user_metadata.get("full_name")
                or user.user_metadata.get("name")
                or user.email.split("@")[0],
                "email": user.email,
                "settings": {},
                "total_revenue": 0,
            }

            # Insert new profile
            supabase_client.table("users").insert(profile_data).execute()

            return {
                "id": user.id,
                "email": user.email,
                "name": profile_data["name"],
                "phone": None,
                "avatar_url": None,
                "settings": {},
                "total_revenue": 0,
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Get current active user (add additional checks if needed)

    Args:
        current_user: User data from get_current_user

    Returns:
        Active user data

    Raises:
        HTTPException: If user is inactive/suspended
    """
    # Add any additional checks here (e.g., user status, subscription, etc.)
    # For now, just return the user
    return current_user


async def verify_property_ownership(
    property_id: str, current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Verify that the current user owns the specified property

    Args:
        property_id: Property ID to verify
        current_user: Current authenticated user

    Returns:
        Property data if user owns it

    Raises:
        HTTPException: If property not found or user doesn't own it
    """
    try:
        result = (
            supabase_client.table("properties")
            .select("*")
            .eq("id", property_id)
            .eq("user_id", current_user["id"])
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found or access denied",
            )

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Property ownership verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not verify property ownership",
        )


async def verify_booking_access(
    booking_id: str, current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Verify that the current user has access to the specified booking
    (either owns the property or is the guest)

    Args:
        booking_id: Booking ID to verify
        current_user: Current authenticated user

    Returns:
        Booking data if user has access

    Raises:
        HTTPException: If booking not found or user doesn't have access
    """
    try:
        # Get booking with property information
        result = (
            supabase_client.table("bookings")
            .select(
                """
            *,
            properties!inner(user_id)
        """
            )
            .eq("id", booking_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
            )

        booking = result.data[0]

        # Check if user owns the property
        if booking["properties"]["user_id"] == current_user["id"]:
            return booking

        # Check if user is the guest (by email)
        if booking["guest_email"] == current_user["email"]:
            return booking

        # User has no access to this booking
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this booking",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Booking access verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not verify booking access",
        )


async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Verify that the current user has admin or super_admin role

    Args:
        current_user: Current authenticated user

    Returns:
        User data if user is admin

    Raises:
        HTTPException: If user is not an admin
    """
    try:
        # Get user role from database
        result = (
            supabase_client.table("users")
            .select("role")
            .eq("id", current_user["id"])
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )

        user_role = result.data[0].get("role", "user")

        if user_role not in ["admin", "super_admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required",
            )

        return current_user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not verify admin status",
        )
