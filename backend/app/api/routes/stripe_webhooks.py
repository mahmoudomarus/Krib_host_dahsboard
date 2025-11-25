"""
Stripe Webhooks Handler
Processes Stripe webhook events for payments, transfers, and account updates
"""

from fastapi import APIRouter, Request, HTTPException, status, Header
from typing import Optional
import stripe
import logging
import json
from datetime import datetime

from app.core.stripe_config import StripeConfig
from app.core.supabase_client import supabase_client
from app.services.stripe_connect_service import stripe_connect_service
from app.services.stripe_payment_service import stripe_payment_service
from app.services.payout_service import payout_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/billing/webhook")
async def handle_stripe_webhook(
    request: Request, stripe_signature: str = Header(None, alias="Stripe-Signature")
):
    """
    Handle Stripe webhook events

    Verifies webhook signature and processes events
    All events are logged to stripe_events table for audit
    """
    try:
        # Get raw body
        payload = await request.body()

        # Verify webhook signature if secret is configured
        event = None
        if StripeConfig.STRIPE_WEBHOOK_SECRET:
            try:
                event = stripe.Webhook.construct_event(
                    payload, stripe_signature, StripeConfig.STRIPE_WEBHOOK_SECRET
                )
            except stripe.SignatureVerificationError as e:
                logger.error(f"Webhook signature verification failed: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature"
                )
        else:
            # Parse without verification (test mode)
            event = json.loads(payload)
            logger.warning(
                "Processing webhook without signature verification (no webhook secret configured)"
            )

        # Log event to database
        event_id = event.get("id")
        event_type = event.get("type")
        event_data = event.get("data", {}).get("object", {})

        # Extract relevant IDs from event data
        account_id = event_data.get("account") if "account" in event_data else None
        payment_intent_id = (
            event_data.get("payment_intent")
            if "payment_intent" in event_data
            else (
                event_data.get("id")
                if event_type.startswith("payment_intent")
                else None
            )
        )
        charge_id = (
            event_data.get("charge")
            if "charge" in event_data
            else event_data.get("id") if event_type.startswith("charge") else None
        )
        transfer_id = (
            event_data.get("transfer")
            if "transfer" in event_data
            else event_data.get("id") if event_type.startswith("transfer") else None
        )
        payout_id = (
            event_data.get("payout")
            if "payout" in event_data
            else event_data.get("id") if event_type.startswith("payout") else None
        )

        try:
            # Insert into stripe_events table
            supabase_client.table("stripe_events").insert(
                {
                    "stripe_event_id": event_id,
                    "event_type": event_type,
                    "account_id": account_id,
                    "payment_intent_id": payment_intent_id,
                    "charge_id": charge_id,
                    "transfer_id": transfer_id,
                    "payout_id": payout_id,
                    "raw_data": event,
                    "api_version": event.get("api_version"),
                    "processed": False,
                    "event_created": (
                        datetime.fromtimestamp(event.get("created")).isoformat()
                        if event.get("created")
                        else None
                    ),
                }
            ).execute()

            logger.info(f"Logged Stripe event: {event_id}, type: {event_type}")
        except Exception as log_error:
            # Don't fail webhook if logging fails
            logger.error(f"Failed to log webhook event: {log_error}")

        # Process event based on type
        try:
            await process_webhook_event(event_id, event_type, event_data)

            supabase_client.table("stripe_events").update(
                {"processed": True, "processed_at": datetime.utcnow().isoformat()}
            ).eq("stripe_event_id", event_id).execute()

        except Exception as process_error:
            # Log processing error but don't fail webhook
            error_message = str(process_error)
            logger.error(f"Error processing webhook event {event_id}: {error_message}")

            supabase_client.table("stripe_events").update(
                {"error_message": error_message, "retry_count": 1}
            ).eq("stripe_event_id", event_id).execute()

        return {"success": True, "event_id": event_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook handler error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed",
        )


async def process_webhook_event(event_id: str, event_type: str, event_data: dict):
    """
    Process webhook event based on type

    Args:
        event_id: Stripe event ID
        event_type: Type of event
        event_data: Event data object
    """
    logger.info(f"Processing webhook event {event_id} ({event_type})")

    # Account events (Connect onboarding)
    if event_type == "account.updated":
        account_id = event_data.get("id")
        await stripe_connect_service.handle_account_updated_webhook(
            account_id, event_data
        )

    # Payment Intent events
    elif event_type == "payment_intent.succeeded":
        payment_intent_id = event_data.get("id")
        await stripe_payment_service.handle_payment_intent_succeeded(
            payment_intent_id, event_data
        )

    elif event_type == "payment_intent.payment_failed":
        payment_intent_id = event_data.get("id")
        await handle_payment_failed(payment_intent_id, event_data)

    # Charge events
    elif event_type == "charge.succeeded":
        await handle_charge_succeeded(event_data)

    elif event_type == "charge.refunded":
        await handle_charge_refunded(event_data)

    # Transfer events (host payouts)
    elif event_type == "transfer.created":
        await handle_transfer_created(event_data)

    elif event_type == "transfer.paid":
        transfer_id = event_data.get("id")
        await payout_service.handle_transfer_paid_webhook(transfer_id, event_data)

    elif event_type == "transfer.failed":
        transfer_id = event_data.get("id")
        await payout_service.handle_transfer_failed_webhook(transfer_id, event_data)

    # Payout events (to host's bank)
    elif event_type == "payout.paid":
        await handle_payout_paid(event_data)

    elif event_type == "payout.failed":
        await handle_payout_failed(event_data)

    else:
        logger.info(f"Unhandled event type: {event_type}")


async def handle_payment_failed(payment_intent_id: str, payment_intent_data: dict):
    """Handle failed payment intent"""
    try:
        # Find booking
        booking_result = (
            supabase_client.table("bookings")
            .select("id")
            .eq("stripe_payment_intent_id", payment_intent_id)
            .execute()
        )

        if booking_result.data:
            booking_id = booking_result.data[0]["id"]

            # Update booking
            supabase_client.table("bookings").update(
                {
                    "payment_status": "failed",
                    "status": "cancelled",
                    "updated_at": datetime.utcnow().isoformat(),
                }
            ).eq("id", booking_id).execute()

            logger.info(f"Marked booking as failed payment: {booking_id}")
    except Exception as e:
        logger.error(f"Error handling payment failed: {e}")
        raise


async def handle_charge_succeeded(charge_data: dict):
    """Handle successful charge"""
    try:
        payment_intent_id = charge_data.get("payment_intent")
        charge_id = charge_data.get("id")

        if payment_intent_id:
            # Update booking with charge ID
            supabase_client.table("bookings").update(
                {
                    "stripe_charge_id": charge_id,
                    "updated_at": datetime.utcnow().isoformat(),
                }
            ).eq("stripe_payment_intent_id", payment_intent_id).execute()

            logger.info(f"Updated booking with charge ID: {charge_id}")
    except Exception as e:
        logger.error(f"Error handling charge succeeded: {e}")
        raise


async def handle_charge_refunded(charge_data: dict):
    """Handle refunded charge"""
    try:
        charge_id = charge_data.get("id")
        refunded = charge_data.get("refunded", False)
        amount_refunded = (
            charge_data.get("amount_refunded", 0) / 100
        )  # Convert from fils

        # Find booking
        booking_result = (
            supabase_client.table("bookings")
            .select("id, total_amount")
            .eq("stripe_charge_id", charge_id)
            .execute()
        )

        if booking_result.data:
            booking = booking_result.data[0]
            total = booking["total_amount"]

            status = (
                "refunded"
                if refunded or amount_refunded >= total
                else "partially_refunded"
            )

            supabase_client.table("bookings").update(
                {
                    "payment_status": status,
                    "refund_amount": amount_refunded,
                    "status": (
                        "cancelled" if status == "refunded" else booking.get("status")
                    ),
                    "updated_at": datetime.utcnow().isoformat(),
                }
            ).eq("id", booking["id"]).execute()

            logger.info(f"Updated booking with refund status: {booking['id']}")
    except Exception as e:
        logger.error(f"Error handling charge refunded: {e}")
        raise


async def handle_transfer_created(transfer_data: dict):
    """Handle transfer created"""
    try:
        transfer_id = transfer_data.get("id")

        # Update payout status to in_transit
        supabase_client.table("payouts").update(
            {"status": "in_transit", "updated_at": datetime.utcnow().isoformat()}
        ).eq("stripe_transfer_id", transfer_id).execute()

        logger.info(f"Marked transfer as in_transit: {transfer_id}")
    except Exception as e:
        logger.error(f"Error handling transfer created: {e}")
        raise


async def handle_payout_paid(payout_data: dict):
    """Handle payout paid to host's bank"""
    try:
        payout_id = payout_data.get("id")
        arrival_date = payout_data.get("arrival_date")

        # This is the Stripe payout to bank, not our payout record
        # Log for informational purposes
        logger.info(
            f"Stripe payout {payout_id} paid to bank, arrival date: {arrival_date}"
        )
    except Exception as e:
        logger.error(f"Error handling payout paid: {e}")


async def handle_payout_failed(payout_data: dict):
    """Handle failed payout to host's bank"""
    try:
        payout_id = payout_data.get("id")
        failure_message = payout_data.get("failure_message")

        logger.error(f"Stripe payout {payout_id} failed: {failure_message}")
    except Exception as e:
        logger.error(f"Error handling payout failed: {e}")
