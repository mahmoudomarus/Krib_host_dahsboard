"""
Guest payment routes - public endpoints for guest checkout
No authentication required
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
import stripe
import logging
from datetime import datetime

from app.core.supabase_client import supabase_client
from app.core.stripe_config import StripeConfig

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/bookings/{booking_id}")
async def get_guest_booking(booking_id: str) -> Dict[str, Any]:
    """Get booking details for guest payment page (public endpoint)"""
    try:
        result = (
            supabase_client.table("bookings")
            .select(
                "id, check_in, check_out, nights, guests, guest_name, guest_email, "
                "total_amount, status, payment_status, "
                "properties(title, address, city, state)"
            )
            .eq("id", booking_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Booking not found")

        booking = result.data[0]
        property_data = booking.get("properties", {})

        return {
            "success": True,
            "data": {
                "id": booking["id"],
                "property_title": property_data.get("title", "Property"),
                "property_address": f"{property_data.get('address', '')}, {property_data.get('city', '')}, {property_data.get('state', '')}",
                "check_in": booking["check_in"],
                "check_out": booking["check_out"],
                "nights": booking["nights"],
                "guests": booking["guests"],
                "guest_name": booking["guest_name"],
                "guest_email": booking["guest_email"],
                "total_amount": float(booking["total_amount"]),
                "status": booking["status"],
                "payment_status": booking["payment_status"],
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching booking {booking_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch booking")


@router.post("/bookings/{booking_id}/checkout")
async def create_checkout_session(booking_id: str) -> Dict[str, Any]:
    """Create Stripe Checkout session for guest payment"""
    try:
        # Get booking with property and host info
        result = (
            supabase_client.table("bookings")
            .select("*, properties(id, title, user_id, users(stripe_account_id))")
            .eq("id", booking_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Booking not found")

        booking = result.data[0]

        if booking["payment_status"] == "paid":
            raise HTTPException(status_code=400, detail="Booking already paid")

        property_data = booking.get("properties", {})
        host_data = property_data.get("users", {})
        host_stripe_account = host_data.get("stripe_account_id")

        if not host_stripe_account:
            raise HTTPException(status_code=400, detail="Host payment setup incomplete")

        # Calculate platform fee (15%)
        total_amount = float(booking["total_amount"])
        platform_fee = int(total_amount * 0.15 * 100)  # In fils
        amount_in_fils = int(total_amount * 100)

        # Create Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "aed",
                        "unit_amount": amount_in_fils,
                        "product_data": {
                            "name": property_data.get("title", "Property Booking"),
                            "description": f"{booking['nights']} nights • {booking['check_in']} to {booking['check_out']}",
                        },
                    },
                    "quantity": 1,
                }
            ],
            payment_intent_data={
                "application_fee_amount": platform_fee,
                "transfer_data": {"destination": host_stripe_account},
                "metadata": {
                    "booking_id": booking_id,
                    "property_id": property_data.get("id"),
                    "guest_email": booking["guest_email"],
                },
            },
            customer_email=booking["guest_email"],
            success_url=f"https://host.krib.ae/pay/{booking_id}/success",
            cancel_url=f"https://host.krib.ae/pay/{booking_id}",
            metadata={"booking_id": booking_id},
        )

        # Update booking with checkout session
        supabase_client.table("bookings").update(
            {
                "stripe_checkout_session_id": checkout_session.id,
                "payment_status": "processing",
                "updated_at": datetime.utcnow().isoformat(),
            }
        ).eq("id", booking_id).execute()

        logger.info(
            f"Created checkout session {checkout_session.id} for booking {booking_id}"
        )

        return {
            "success": True,
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id,
        }

    except HTTPException:
        raise
    except stripe.StripeError as e:
        logger.error(f"Stripe error for booking {booking_id}: {e}")
        raise HTTPException(status_code=400, detail=f"Payment error: {str(e)}")
    except Exception as e:
        logger.error(f"Checkout error for booking {booking_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create checkout")
