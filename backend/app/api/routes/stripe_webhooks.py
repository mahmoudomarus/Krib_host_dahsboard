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

    # Checkout Session events (guest payments)
    elif event_type == "checkout.session.completed":
        await handle_checkout_completed(event_data)

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


async def handle_checkout_completed(session_data: dict):
    """
    Handle Stripe Checkout session completed (guest payment)
    - Creates booking from checkout metadata (booking is NOT created until payment succeeds)
    - Sets status to confirmed + paid
    - Notifies host and guest
    - Sends webhook to AI Agent platform
    """
    try:
        import uuid

        session_id = session_data.get("id")
        metadata = session_data.get("metadata", {})
        payment_intent = session_data.get("payment_intent")
        customer_email = session_data.get("customer_email")
        amount_total = session_data.get("amount_total", 0) / 100  # Convert from fils

        # Check if this is from external API (has checkout_id) or guest payment page (has booking_id)
        checkout_id = metadata.get("checkout_id")
        booking_id = metadata.get("booking_id")

        logger.info(
            f"Checkout completed: session={session_id}, checkout_id={checkout_id}, booking_id={booking_id}"
        )

        if checkout_id and not booking_id:
            # External API flow - CREATE booking from metadata
            logger.info(f"Creating booking from checkout metadata for {checkout_id}")

            property_id = metadata.get("property_id")
            host_id = metadata.get("host_id")

            if not property_id:
                logger.error(f"No property_id in checkout session {session_id}")
                return

            # Create the booking now that payment is complete
            booking_id = str(uuid.uuid4())
            booking_record = {
                "id": booking_id,
                "property_id": property_id,
                "guest_name": metadata.get("guest_name", "Guest"),
                "guest_email": metadata.get("guest_email", customer_email),
                "guest_phone": metadata.get("guest_phone", ""),
                "check_in": metadata.get("check_in"),
                "check_out": metadata.get("check_out"),
                "guests": int(metadata.get("guests", 1)),
                "total_amount": float(metadata.get("total_amount", amount_total)),
                "status": "confirmed",  # Already confirmed since paid
                "payment_status": "paid",
                "stripe_payment_intent_id": payment_intent,
                "stripe_checkout_session_id": session_id,
                "special_requests": metadata.get("special_requests", ""),
                "confirmed_at": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }

            result = supabase_client.table("bookings").insert(booking_record).execute()

            if not result.data:
                logger.error(f"Failed to create booking from checkout {checkout_id}")
                return

            logger.info(f"Created booking {booking_id} from checkout {checkout_id}")

            # Get property details for notification
            property_result = (
                supabase_client.table("properties")
                .select("id, title, user_id")
                .eq("id", property_id)
                .execute()
            )
            property_data = property_result.data[0] if property_result.data else {}
            booking = booking_record

        elif booking_id:
            # Guest payment page flow - UPDATE existing booking
            logger.info(f"Updating existing booking {booking_id}")

            # Get booking details
            booking_result = (
                supabase_client.table("bookings")
                .select("*, properties(id, title, user_id)")
                .eq("id", booking_id)
                .execute()
            )

            if not booking_result.data:
                logger.error(f"Booking {booking_id} not found")
                return

            booking = booking_result.data[0]
            property_data = booking.get("properties", {})

            # Update booking status
            supabase_client.table("bookings").update(
                {
                    "status": "confirmed",
                    "payment_status": "paid",
                    "stripe_payment_intent_id": payment_intent,
                    "confirmed_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                }
            ).eq("id", booking_id).execute()
        else:
            logger.error(f"No checkout_id or booking_id in session {session_id}")
            return

        logger.info(f"Booking {booking_id} confirmed and paid")

        # 2. Block dates on property (dates are already blocked by having confirmed booking)
        # The availability check queries bookings table for confirmed/pending bookings
        # No additional action needed - booking existence blocks the dates

        # 3. Send notification to host
        try:
            from app.services.notification_service import NotificationService

            await NotificationService.create_booking_notification(
                user_id=property_data.get("user_id"),
                booking_id=booking_id,
                notification_type="booking_paid",
                title="Payment Received! 💰",
                message=f"Guest {booking['guest_name']} has paid AED {amount_total} for {property_data.get('title')}",
                metadata={
                    "property_id": property_data.get("id"),
                    "guest_name": booking["guest_name"],
                    "check_in": booking["check_in"],
                    "check_out": booking["check_out"],
                    "amount": amount_total,
                },
            )
        except Exception as notif_error:
            logger.warning(f"Failed to send host notification: {notif_error}")

        # 4. Send webhook to AI Agent platform
        try:
            from app.services.background_jobs import send_booking_webhook

            webhook_data = {
                "booking_id": booking_id,
                "status": "confirmed",
                "payment_status": "paid",
                "amount_paid": amount_total,
                "currency": "AED",
                "property_id": property_data.get("id"),
                "property_title": property_data.get("title"),
                "guest_name": booking["guest_name"],
                "guest_email": booking["guest_email"],
                "check_in": booking["check_in"],
                "check_out": booking["check_out"],
                "nights": booking.get("nights"),
                "confirmed_at": datetime.utcnow().isoformat(),
            }
            send_booking_webhook.delay("booking.confirmed", booking_id, webhook_data)
            send_booking_webhook.delay("payment.succeeded", booking_id, webhook_data)
        except Exception as webhook_error:
            logger.warning(f"Failed to send webhook: {webhook_error}")

        # 5. TODO: Send confirmation email to guest
        # send_booking_confirmation_email.delay(booking_id, customer_email)

        logger.info(f"Checkout completed successfully for booking {booking_id}")

    except Exception as e:
        logger.error(f"Error handling checkout completed: {e}")
        raise
