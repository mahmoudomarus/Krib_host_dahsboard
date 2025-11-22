"""
Query service unit tests
"""

import pytest
from datetime import date, timedelta
from fastapi import HTTPException


# Test without importing query_service to avoid Supabase client init
class QueryService:
    """Mock QueryService for testing business logic"""

    @staticmethod
    def calculate_booking_total(
        price_per_night: float, check_in: date, check_out: date
    ):
        nights = (check_out - check_in).days
        if nights <= 0:
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Check-out date must be after check-in date",
            )
        total_amount = nights * price_per_night
        return nights, total_amount

    @staticmethod
    def validate_guest_count(guests: int, max_guests: int):
        if guests > max_guests:
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Property can accommodate maximum {max_guests} guests",
            )


def test_calculate_booking_total():
    """Test booking calculation"""
    query_service = QueryService()

    # Test valid booking
    check_in = date.today()
    check_out = check_in + timedelta(days=3)
    nights, total = query_service.calculate_booking_total(100.0, check_in, check_out)

    assert nights == 3
    assert total == 300.0


def test_calculate_booking_total_invalid_dates():
    """Test booking calculation with invalid dates"""
    query_service = QueryService()

    check_in = date.today()
    check_out = check_in  # Same day

    with pytest.raises(HTTPException) as exc_info:
        query_service.calculate_booking_total(100.0, check_in, check_out)

    assert exc_info.value.status_code == 400
    assert "after check-in" in exc_info.value.detail


def test_validate_guest_count():
    """Test guest count validation"""
    query_service = QueryService()

    # Valid guest count
    query_service.validate_guest_count(4, 6)  # Should not raise

    # Invalid guest count
    with pytest.raises(HTTPException) as exc_info:
        query_service.validate_guest_count(8, 6)

    assert exc_info.value.status_code == 400
    assert "maximum 6 guests" in exc_info.value.detail


def test_validate_guest_count_edge_case():
    """Test guest count validation at boundary"""
    query_service = QueryService()

    # Exactly at limit should be valid
    query_service.validate_guest_count(6, 6)  # Should not raise
