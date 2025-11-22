"""
Payout API Routes
Handles host payout processing and history
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, Optional

from app.models.stripe_schemas import PayoutProcess, PayoutResponse, PayoutList
from app.services.payout_service import payout_service
from app.api.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/process-booking-payout", response_model=Dict[str, Any])
async def process_booking_payout(
    payout_data: PayoutProcess, current_user: dict = Depends(get_current_user)
):
    """
    Process payout to host for a completed booking

    Requires authentication (admin or automated system)
    Only works for bookings that have:
    - Successful payment
    - Passed checkout date + delay period
    - Host with verified Stripe Connect account
    """
    try:
        result = await payout_service.process_booking_payout(
            booking_id=payout_data.booking_id,
            platform_fee_percentage=payout_data.platform_fee_percentage,
        )

        return {"success": True, "data": result}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing payout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process payout",
        )


@router.get("/host-payouts", response_model=Dict[str, Any])
async def get_host_payouts(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
):
    """
    Get all payouts for the authenticated host

    Requires authentication
    Returns list of payouts with totals by status
    """
    try:
        user_id = current_user["id"]

        result = await payout_service.get_host_payouts(
            user_id=user_id, status=status, limit=limit, offset=offset
        )

        return {"success": True, "data": result}

    except Exception as e:
        logger.error(f"Error getting host payouts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get payouts",
        )
