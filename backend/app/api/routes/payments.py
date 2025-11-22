"""
Payment API Routes
Handles payment processing, refunds, and payment status
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional

from app.models.stripe_schemas import (
    PaymentIntentCreate,
    PaymentIntentResponse,
    PaymentConfirm,
    PaymentStatus,
    RefundCreate,
    RefundResponse,
)
from app.services.stripe_payment_service import stripe_payment_service
from app.api.dependencies import get_current_user
from app.api.dependencies_external import get_external_service_context
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/create-payment-intent", response_model=Dict[str, Any])
async def create_payment_intent(
    payment_data: PaymentIntentCreate, user_context: dict = Depends(get_current_user)
):
    """
    Create a payment intent for a booking

    Requires authentication (guest user or external API key)
    """
    try:
        result = await stripe_payment_service.create_payment_intent(
            booking_id=payment_data.booking_id,
            amount=payment_data.amount,
            currency=payment_data.currency,
            payment_method_types=payment_data.payment_method_types,
            metadata=payment_data.metadata,
        )

        return {"success": True, "data": result}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating payment intent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment intent",
        )


@router.post("/confirm-payment", response_model=Dict[str, Any])
async def confirm_payment(
    payment_confirm: PaymentConfirm, user_context: dict = Depends(get_current_user)
):
    """
    Confirm payment and update booking status

    Requires authentication
    """
    try:
        result = await stripe_payment_service.confirm_payment(
            payment_intent_id=payment_confirm.payment_intent_id,
            booking_id=payment_confirm.booking_id,
        )

        return {"success": True, "data": result}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error confirming payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to confirm payment",
        )


@router.post("/refund", response_model=Dict[str, Any])
async def create_refund(
    refund_data: RefundCreate, current_user: dict = Depends(get_current_user)
):
    """
    Create a refund for a booking

    Requires authentication (host or admin)
    """
    try:
        result = await stripe_payment_service.create_refund(
            booking_id=refund_data.booking_id,
            amount=refund_data.amount,
            reason=refund_data.reason,
        )

        return {"success": True, "data": result}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating refund: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create refund",
        )
