"""
Payout Service
Handles host payouts via Stripe Transfers after booking completion
"""

import stripe
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal

from app.core.stripe_config import StripeConfig
from app.core.supabase_client import supabase_client

logger = logging.getLogger(__name__)


class PayoutService:
    """Service for managing host payouts"""

    @staticmethod
    async def process_booking_payout(
        booking_id: str, platform_fee_percentage: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        Process payout to host for a completed booking

        Args:
            booking_id: UUID of the booking
            platform_fee_percentage: Override default platform fee percentage

        Returns:
            Dictionary with payout details
        """
        try:
            # Get booking details with property and host info
            booking_result = (
                supabase_client.table("bookings")
                .select(
                    "id, property_id, total_amount, platform_fee_amount, host_payout_amount, "
                    "host_payout_status, check_out, payment_status, stripe_payment_intent_id, stripe_charge_id, "
                    "properties(id, title, user_id, users(id, stripe_account_id, stripe_payouts_enabled, name, email))"
                )
                .eq("id", booking_id)
                .execute()
            )

            if not booking_result.data:
                raise ValueError(f"Booking {booking_id} not found")

            booking = booking_result.data[0]

            # Validations
            if booking["payment_status"] != "succeeded":
                raise ValueError(
                    f"Cannot process payout - payment status is {booking['payment_status']}"
                )

            if booking["host_payout_status"] == "paid":
                raise ValueError(f"Payout already processed for booking {booking_id}")

            property_data = booking.get("properties", {})
            host_data = property_data.get("users", {})

            if not host_data.get("stripe_account_id"):
                raise ValueError("Host does not have a Stripe Connect account")

            if not host_data.get("stripe_payouts_enabled"):
                raise ValueError("Host's Stripe account is not enabled for payouts")

            # Check if booking is completed (checkout date passed + delay)
            checkout_date = (
                datetime.fromisoformat(booking["check_out"]).date()
                if isinstance(booking["check_out"], str)
                else booking["check_out"]
            )
            payout_eligible_date = checkout_date + timedelta(
                days=StripeConfig.PAYOUT_DELAY_DAYS
            )

            if date.today() < payout_eligible_date:
                raise ValueError(
                    f"Payout not yet eligible. Available after {payout_eligible_date}"
                )

            # Calculate amounts
            total_amount = Decimal(str(booking["total_amount"]))

            if platform_fee_percentage is None:
                platform_fee_percentage = Decimal(
                    str(StripeConfig.PLATFORM_FEE_PERCENTAGE)
                )

            platform_fee = total_amount * (platform_fee_percentage / 100)
            host_payout_amount = total_amount - platform_fee

            # Convert to fils
            host_payout_fils = int(float(host_payout_amount) * 100)

            # Create Transfer to host's Stripe account
            transfer = stripe.Transfer.create(
                amount=host_payout_fils,
                currency=StripeConfig.CURRENCY.lower(),
                destination=host_data["stripe_account_id"],
                source_transaction=booking.get("stripe_charge_id"),
                description=f"Payout for booking {booking_id} - {property_data.get('title', 'property')}",
                metadata={
                    "booking_id": booking_id,
                    "property_id": booking["property_id"],
                    "host_user_id": host_data["id"],
                    "platform_fee": str(platform_fee),
                    "platform": "krib_host_dashboard",
                },
            )

            logger.info(
                f"Created transfer {transfer.id} for booking {booking_id}, amount: {host_payout_amount}"
            )

            # Create payout record
            payout_result = (
                supabase_client.table("payouts")
                .insert(
                    {
                        "user_id": host_data["id"],
                        "booking_id": booking_id,
                        "property_id": booking["property_id"],
                        "stripe_transfer_id": transfer.id,
                        "amount": float(host_payout_amount),
                        "currency": StripeConfig.CURRENCY,
                        "platform_fee": float(platform_fee),
                        "original_booking_amount": float(total_amount),
                        "status": "processing",
                        "description": f"Payout for {property_data.get('title', 'property')}",
                        "initiated_at": datetime.utcnow().isoformat(),
                        "metadata": {
                            "guest_email": booking.get("guest_email"),
                            "check_in": booking.get("check_in"),
                            "check_out": booking.get("check_out"),
                        },
                    }
                )
                .execute()
            )

            payout_id = payout_result.data[0]["id"]

            # Update booking with payout info
            supabase_client.table("bookings").update(
                {
                    "stripe_transfer_id": transfer.id,
                    "host_payout_status": "processing",
                    "host_payout_amount": float(host_payout_amount),
                    "platform_fee_amount": float(platform_fee),
                    "updated_at": datetime.utcnow().isoformat(),
                }
            ).eq("id", booking_id).execute()

            return {
                "payout_id": payout_id,
                "transfer_id": transfer.id,
                "host_user_id": host_data["id"],
                "booking_id": booking_id,
                "amount": host_payout_amount,
                "platform_fee": platform_fee,
                "host_amount": host_payout_amount,
                "currency": StripeConfig.CURRENCY,
                "status": "processing",
                "initiated_at": datetime.utcnow(),
            }

        except stripe.StripeError as e:
            logger.error(
                f"Stripe error processing payout for booking {booking_id}: {e}"
            )

            # Mark payout as failed if it was created
            supabase_client.table("bookings").update(
                {
                    "host_payout_status": "failed",
                    "updated_at": datetime.utcnow().isoformat(),
                }
            ).eq("id", booking_id).execute()

            raise Exception(f"Failed to process payout: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing payout for booking {booking_id}: {e}")
            raise

    @staticmethod
    async def get_host_payouts(
        user_id: str, status: Optional[str] = None, limit: int = 50, offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get all payouts for a host

        Args:
            user_id: UUID of the host user
            status: Filter by status (optional)
            limit: Number of results to return
            offset: Pagination offset

        Returns:
            Dictionary with payouts list and totals
        """
        try:
            # Build query
            query = (
                supabase_client.table("payouts")
                .select(
                    "id, booking_id, property_id, amount, currency, platform_fee, "
                    "original_booking_amount, status, description, failure_message, "
                    "initiated_at, completed_at, stripe_transfer_id, "
                    "properties(title), bookings(guest_name, check_in, check_out)"
                )
                .eq("user_id", user_id)
                .order("created_at", desc=True)
            )

            if status:
                query = query.eq("status", status)

            # Get paginated results
            payouts_result = query.range(offset, offset + limit - 1).execute()

            # Get totals by status
            totals_result = (
                supabase_client.table("payouts")
                .select("status, amount")
                .eq("user_id", user_id)
                .execute()
            )

            # Calculate totals
            total_paid = sum(
                Decimal(str(p["amount"]))
                for p in totals_result.data
                if p["status"] == "paid"
            )
            total_pending = sum(
                Decimal(str(p["amount"]))
                for p in totals_result.data
                if p["status"] == "pending"
            )
            total_in_transit = sum(
                Decimal(str(p["amount"]))
                for p in totals_result.data
                if p["status"] in ["processing", "in_transit"]
            )
            total_failed = sum(
                Decimal(str(p["amount"]))
                for p in totals_result.data
                if p["status"] == "failed"
            )

            # Format payouts
            payouts = []
            for payout in payouts_result.data:
                property_data = payout.get("properties", {})
                booking_data = payout.get("bookings", {})

                payouts.append(
                    {
                        "id": payout["id"],
                        "booking_id": payout["booking_id"],
                        "property_id": payout["property_id"],
                        "property_title": property_data.get("title"),
                        "amount": Decimal(str(payout["amount"])),
                        "currency": payout["currency"],
                        "platform_fee": (
                            Decimal(str(payout["platform_fee"]))
                            if payout["platform_fee"]
                            else None
                        ),
                        "original_booking_amount": (
                            Decimal(str(payout["original_booking_amount"]))
                            if payout["original_booking_amount"]
                            else None
                        ),
                        "status": payout["status"],
                        "description": payout["description"],
                        "failure_message": payout["failure_message"],
                        "initiated_at": payout["initiated_at"],
                        "completed_at": payout["completed_at"],
                        "stripe_transfer_id": payout["stripe_transfer_id"],
                        "guest_name": booking_data.get("guest_name"),
                        "booking_dates": (
                            f"{booking_data.get('check_in')} to {booking_data.get('check_out')}"
                            if booking_data.get("check_in")
                            else None
                        ),
                    }
                )

            return {
                "payouts": payouts,
                "total_count": len(totals_result.data),
                "total_paid": total_paid,
                "total_pending": total_pending,
                "total_in_transit": total_in_transit,
                "total_failed": total_failed,
            }

        except Exception as e:
            logger.error(f"Error getting payouts for user {user_id}: {e}")
            raise

    @staticmethod
    async def handle_transfer_paid_webhook(
        transfer_id: str, transfer_data: Dict[str, Any]
    ) -> None:
        """
        Handle transfer.paid webhook event

        Args:
            transfer_id: Stripe Transfer ID
            transfer_data: Transfer data from webhook
        """
        try:
            # Find payout with this transfer
            payout_result = (
                supabase_client.table("payouts")
                .select("id, user_id, booking_id")
                .eq("stripe_transfer_id", transfer_id)
                .execute()
            )

            if not payout_result.data:
                logger.warning(f"No payout found with transfer ID {transfer_id}")
                return

            payout = payout_result.data[0]

            # Update payout status
            supabase_client.table("payouts").update(
                {
                    "status": "paid",
                    "completed_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                }
            ).eq("id", payout["id"]).execute()

            # Update booking
            supabase_client.table("bookings").update(
                {
                    "host_payout_status": "paid",
                    "host_payout_date": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                }
            ).eq("id", payout["booking_id"]).execute()

            logger.info(
                f"Marked payout {payout['id']} as paid for transfer {transfer_id}"
            )

        except Exception as e:
            logger.error(f"Error handling transfer.paid webhook for {transfer_id}: {e}")
            raise

    @staticmethod
    async def handle_transfer_failed_webhook(
        transfer_id: str, transfer_data: Dict[str, Any]
    ) -> None:
        """
        Handle transfer.failed webhook event

        Args:
            transfer_id: Stripe Transfer ID
            transfer_data: Transfer data from webhook
        """
        try:
            # Find payout with this transfer
            payout_result = (
                supabase_client.table("payouts")
                .select("id, user_id, booking_id")
                .eq("stripe_transfer_id", transfer_id)
                .execute()
            )

            if not payout_result.data:
                logger.warning(f"No payout found with transfer ID {transfer_id}")
                return

            payout = payout_result.data[0]

            # Get failure details
            failure_code = transfer_data.get("failure_code")
            failure_message = transfer_data.get("failure_message", "Transfer failed")

            # Update payout status
            supabase_client.table("payouts").update(
                {
                    "status": "failed",
                    "failure_code": failure_code,
                    "failure_message": failure_message,
                    "updated_at": datetime.utcnow().isoformat(),
                }
            ).eq("id", payout["id"]).execute()

            # Update booking
            supabase_client.table("bookings").update(
                {
                    "host_payout_status": "failed",
                    "updated_at": datetime.utcnow().isoformat(),
                }
            ).eq("id", payout["booking_id"]).execute()

            logger.error(
                f"Payout {payout['id']} failed for transfer {transfer_id}: {failure_message}"
            )

        except Exception as e:
            logger.error(
                f"Error handling transfer.failed webhook for {transfer_id}: {e}"
            )
            raise


payout_service = PayoutService()
