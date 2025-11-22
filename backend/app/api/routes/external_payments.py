"""
External Payment API Routes
Allows external platforms (AI agents) to process payments for bookings
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Dict, Any
from datetime import datetime
import logging

from app.models.external_schemas import ExternalAPIResponse
from app.api.dependencies_external import get_external_service_context
from app.services.stripe_payment_service import stripe_payment_service
from app.services.payout_service import payout_service
from app.core.supabase_client import supabase_client
from slowapi import Limiter
from slowapi.util import get_remote_address

logger = logging.getLogger(__name__)
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/v1/bookings/{booking_id}/process-payment", response_model=ExternalAPIResponse
)
@limiter.limit("50/minute")
async def process_booking_payment(
    request: Request,
    booking_id: str,
    payment_method_id: str = None,  # Stripe payment method ID (optional for test mode)
    service_context: dict = Depends(get_external_service_context),
):
    """
    Process payment for a booking and schedule automatic host payout

    For external AI agents to complete the booking payment flow.
    In test mode, payments are simulated automatically.
    """
    try:
        # Get booking details
        booking_result = (
            supabase_client.table("bookings")
            .select(
                """
            *,
            properties!inner(
                id, title, user_id, base_price_per_night,
                users!inner(id, name, email, stripe_account_id, payouts_enabled)
            )
        """
            )
            .eq("id", booking_id)
            .execute()
        )

        if not booking_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
            )

        booking = booking_result.data[0]
        property_info = booking["properties"]
        host_info = property_info["users"]

        # Check if booking is in pending status
        if booking["status"] != "pending" and booking["status"] != "confirmed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot process payment for booking with status: {booking['status']}",
            )

        # Check if payment already processed
        if booking["payment_status"] == "paid":
            return ExternalAPIResponse(
                success=True,
                data={
                    "booking_id": booking_id,
                    "payment_status": "paid",
                    "message": "Payment already processed",
                },
                message="Payment already processed for this booking",
            )

        # Verify host has Stripe account
        if not host_info.get("stripe_account_id"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Host has not set up payout account yet",
            )

        # Process payment through Stripe
        # In test mode, we simulate the payment
        logger.info(
            f"Processing payment for booking {booking_id}, amount: {booking['total_amount']} AED"
        )

        try:
            # Create payment intent (or simulate in test mode)
            payment_result = await stripe_payment_service.create_payment_intent(
                amount=float(booking["total_amount"]),
                currency="aed",
                booking_id=booking_id,
                metadata={
                    "booking_id": booking_id,
                    "property_id": property_info["id"],
                    "property_title": property_info["title"],
                    "host_id": host_info["id"],
                    "guest_name": booking["guest_name"],
                    "check_in": booking["check_in"],
                    "check_out": booking["check_out"],
                    "source": "external_ai_agent",
                },
            )

            # For test mode or if payment method provided, auto-confirm
            if payment_method_id or True:  # Always auto-confirm for AI agent
                # Confirm payment
                await stripe_payment_service.confirm_payment(
                    payment_intent_id=payment_result["payment_intent_id"],
                    payment_method_id=payment_method_id or "pm_card_visa",  # Test card
                )

            # Update booking status
            supabase_client.table("bookings").update(
                {
                    "status": "confirmed",
                    "payment_status": "paid",
                    "payment_method": "stripe",
                    "confirmed_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                }
            ).eq("id", booking_id).execute()

            logger.info(f"Payment processed successfully for booking {booking_id}")

            # Calculate payout amounts
            payout_amounts = payout_service.calculate_payout_amount(
                total_amount=float(booking["total_amount"])
            )

            return ExternalAPIResponse(
                success=True,
                data={
                    "booking_id": booking_id,
                    "payment_status": "paid",
                    "payment_intent_id": payment_result.get("payment_intent_id"),
                    "amount_paid": booking["total_amount"],
                    "currency": "AED",
                    "host_payout": {
                        "amount": payout_amounts["host_amount"],
                        "scheduled_date": payout_amounts.get("payout_date"),
                        "status": "scheduled",
                        "platform_fee": payout_amounts["platform_fee"],
                        "platform_fee_percentage": payout_amounts[
                            "platform_fee_percentage"
                        ],
                    },
                    "message": f"Payment processed. Host payout of {payout_amounts['host_amount']} AED scheduled for 1 day after checkout.",
                },
                message="Payment processed successfully, host payout scheduled",
            )

        except Exception as stripe_error:
            logger.error(
                f"Stripe payment error for booking {booking_id}: {str(stripe_error)}"
            )

            # Update booking with payment error
            supabase_client.table("bookings").update(
                {
                    "payment_status": "failed",
                    "updated_at": datetime.utcnow().isoformat(),
                }
            ).eq("id", booking_id).execute()

            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Payment processing failed: {str(stripe_error)}",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing payment for booking {booking_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process payment",
        )


@router.get(
    "/v1/bookings/{booking_id}/payment-status", response_model=ExternalAPIResponse
)
@limiter.limit("100/minute")
async def get_payment_status(
    request: Request,
    booking_id: str,
    service_context: dict = Depends(get_external_service_context),
):
    """
    Get payment status for a booking
    """
    try:
        booking_result = (
            supabase_client.table("bookings")
            .select("id, status, payment_status, total_amount, payment_method")
            .eq("id", booking_id)
            .execute()
        )

        if not booking_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
            )

        booking = booking_result.data[0]

        return ExternalAPIResponse(
            success=True,
            data={
                "booking_id": booking_id,
                "booking_status": booking["status"],
                "payment_status": booking["payment_status"],
                "payment_method": booking.get("payment_method"),
                "amount": booking["total_amount"],
                "currency": "AED",
            },
            message="Payment status retrieved successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting payment status for booking {booking_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve payment status",
        )
