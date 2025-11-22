"""
Query Service - Centralized database query logic
Reduces code duplication across routes
"""

from typing import List, Dict, Optional, Any
from datetime import date, datetime
from fastapi import HTTPException, status
from app.core.supabase_client import supabase_client
import logging

logger = logging.getLogger(__name__)


class QueryService:
    """Centralized service for common database operations"""

    @staticmethod
    def get_property_by_id(
        property_id: str, user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch property by ID with optional user ownership verification

        Args:
            property_id: Property UUID
            user_id: Optional user UUID to verify ownership

        Returns:
            Property data dictionary

        Raises:
            HTTPException: If property not found or user doesn't own it
        """
        try:
            query = (
                supabase_client.table("properties").select("*").eq("id", property_id)
            )

            if user_id:
                query = query.eq("user_id", user_id)

            result = query.execute()

            if not result.data:
                if user_id:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Property not found or you don't have access",
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Property not found",
                    )

            return result.data[0]

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching property {property_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch property: {str(e)}",
            )

    @staticmethod
    def get_active_property_by_id(property_id: str) -> Dict[str, Any]:
        """
        Fetch active property by ID

        Args:
            property_id: Property UUID

        Returns:
            Property data dictionary

        Raises:
            HTTPException: If property not found or not active
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

            return result.data[0]

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching active property {property_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch property: {str(e)}",
            )

    @staticmethod
    def get_user_properties(
        user_id: str,
        status_filter: Optional[str] = None,
        property_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Fetch properties for a user with optional filters

        Args:
            user_id: User UUID
            status_filter: Optional status filter ('active', 'draft', 'inactive')
            property_type: Optional property type filter
            limit: Max number of results
            offset: Pagination offset

        Returns:
            List of property dictionaries
        """
        try:
            query = (
                supabase_client.table("properties").select("*").eq("user_id", user_id)
            )

            if status_filter:
                query = query.eq("status", status_filter)

            if property_type:
                query = query.eq("property_type", property_type)

            query = query.order("created_at", desc=True).range(
                offset, offset + limit - 1
            )

            result = query.execute()
            return result.data

        except Exception as e:
            logger.error(f"Error fetching user properties for {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch properties: {str(e)}",
            )

    @staticmethod
    def check_booking_conflicts(
        property_id: str,
        check_in: date,
        check_out: date,
        exclude_booking_id: Optional[str] = None,
    ) -> bool:
        """
        Check if property has booking conflicts for given dates

        Args:
            property_id: Property UUID
            check_in: Check-in date
            check_out: Check-out date
            exclude_booking_id: Optional booking ID to exclude from check (for updates)

        Returns:
            True if there are conflicts, False otherwise
        """
        try:
            query = (
                supabase_client.table("bookings")
                .select("check_in, check_out")
                .eq("property_id", property_id)
                .in_("status", ["confirmed", "pending"])
            )

            if exclude_booking_id:
                query = query.neq("id", exclude_booking_id)

            result = query.execute()

            for booking in result.data:
                existing_checkin = datetime.strptime(
                    booking["check_in"], "%Y-%m-%d"
                ).date()
                existing_checkout = datetime.strptime(
                    booking["check_out"], "%Y-%m-%d"
                ).date()

                if check_in < existing_checkout and check_out > existing_checkin:
                    return True

            return False

        except Exception as e:
            logger.error(
                f"Error checking booking conflicts for property {property_id}: {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to check availability: {str(e)}",
            )

    @staticmethod
    def calculate_booking_total(
        price_per_night: float, check_in: date, check_out: date
    ) -> tuple[int, float]:
        """
        Calculate booking nights and total amount

        Args:
            price_per_night: Property price per night
            check_in: Check-in date
            check_out: Check-out date

        Returns:
            Tuple of (nights, total_amount)

        Raises:
            HTTPException: If dates are invalid
        """
        nights = (check_out - check_in).days

        if nights <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Check-out date must be after check-in date",
            )

        total_amount = nights * price_per_night
        return nights, total_amount

    @staticmethod
    def validate_guest_count(guests: int, max_guests: int) -> None:
        """
        Validate guest count against property capacity

        Args:
            guests: Number of guests
            max_guests: Maximum guests allowed

        Raises:
            HTTPException: If guest count exceeds capacity
        """
        if guests > max_guests:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Property can accommodate maximum {max_guests} guests",
            )

    @staticmethod
    def get_booking_by_id(
        booking_id: str, user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch booking by ID with optional user ownership verification

        Args:
            booking_id: Booking UUID
            user_id: Optional user UUID to verify ownership via property

        Returns:
            Booking data dictionary

        Raises:
            HTTPException: If booking not found or user doesn't own it
        """
        try:
            result = (
                supabase_client.table("bookings")
                .select("*, properties(user_id, title, address)")
                .eq("id", booking_id)
                .execute()
            )

            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
                )

            booking = result.data[0]

            if user_id and booking["properties"]["user_id"] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this booking",
                )

            return booking

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching booking {booking_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch booking: {str(e)}",
            )


# Global query service instance
query_service = QueryService()
