"""
Stripe Payment Service
Handles payment processing, refunds, and payment intent management
"""

import stripe
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from decimal import Decimal

from app.core.stripe_config import StripeConfig
from app.core.supabase_client import supabase_client

logger = logging.getLogger(__name__)


class StripePaymentService:
    """Service for processing payments through Stripe"""
    
    @staticmethod
    async def create_payment_intent(
        booking_id: str,
        amount: Decimal,
        currency: str = "AED",
        payment_method_types: list = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a PaymentIntent for a booking
        
        Args:
            booking_id: UUID of the booking
            amount: Amount to charge in the specified currency
            currency: Currency code (default: AED)
            payment_method_types: Accepted payment methods (default: ["card"])
            metadata: Additional metadata
            
        Returns:
            Dictionary with payment_intent_id, client_secret, etc.
        """
        try:
            # Get booking details
            booking_result = supabase_client.table("bookings").select(
                "id, property_id, guest_name, guest_email, total_amount, properties(title, user_id, users(stripe_account_id))"
            ).eq("id", booking_id).execute()
            
            if not booking_result.data:
                raise ValueError(f"Booking {booking_id} not found")
            
            booking = booking_result.data[0]
            property_data = booking.get("properties", {})
            host_data = property_data.get("users", {})
            host_stripe_account = host_data.get("stripe_account_id")
            
            if not host_stripe_account:
                raise ValueError(f"Property host does not have a Stripe Connect account set up")
            
            # Prepare metadata
            payment_metadata = {
                "booking_id": booking_id,
                "property_id": booking["property_id"],
                "guest_email": booking["guest_email"],
                "platform": "krib_host_dashboard"
            }
            if metadata:
                payment_metadata.update(metadata)
            
            # Convert amount to cents/fils (Stripe uses smallest currency unit)
            amount_in_fils = int(float(amount) * 100)
            
            # Create PaymentIntent
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_in_fils,
                currency=currency.lower(),
                payment_method_types=payment_method_types or ["card"],
                on_behalf_of=host_stripe_account,
                transfer_data={
                    "destination": host_stripe_account,
                },
                metadata=payment_metadata,
                description=f"Booking for {property_data.get('title', 'property')}",
                receipt_email=booking["guest_email"],
                automatic_payment_methods={
                    "enabled": True,
                    "allow_redirects": "never"
                }
            )
            
            logger.info(f"Created PaymentIntent {payment_intent.id} for booking {booking_id}")
            
            # Update booking with payment intent
            supabase_client.table("bookings").update({
                "stripe_payment_intent_id": payment_intent.id,
                "stripe_client_secret": payment_intent.client_secret,
                "payment_status": "processing",
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", booking_id).execute()
            
            return {
                "payment_intent_id": payment_intent.id,
                "client_secret": payment_intent.client_secret,
                "amount": amount,
                "currency": currency,
                "status": payment_intent.status,
                "created": payment_intent.created
            }
            
        except stripe.StripeError as e:
            logger.error(f"Stripe error creating payment intent for booking {booking_id}: {e}")
            raise Exception(f"Failed to create payment intent: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating payment intent for booking {booking_id}: {e}")
            raise
    
    @staticmethod
    async def confirm_payment(
        payment_intent_id: str,
        booking_id: str
    ) -> Dict[str, Any]:
        """
        Confirm a payment and update booking status
        
        Args:
            payment_intent_id: Stripe PaymentIntent ID
            booking_id: UUID of the booking
            
        Returns:
            Dictionary with payment status
        """
        try:
            # Retrieve payment intent
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            # Verify booking
            booking_result = supabase_client.table("bookings").select(
                "id, total_amount, property_id"
            ).eq("id", booking_id).execute()
            
            if not booking_result.data:
                raise ValueError(f"Booking {booking_id} not found")
            
            booking = booking_result.data[0]
            
            # Calculate platform fee and host payout
            total_amount = Decimal(str(booking["total_amount"]))
            platform_fee = total_amount * (Decimal(str(StripeConfig.PLATFORM_FEE_PERCENTAGE)) / 100)
            host_payout = total_amount - platform_fee
            
            # Update booking based on payment intent status
            update_data = {
                "stripe_payment_intent_id": payment_intent_id,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if payment_intent.status == "succeeded":
                update_data.update({
                    "payment_status": "succeeded",
                    "status": "confirmed",
                    "payment_processed_at": datetime.utcnow().isoformat(),
                    "platform_fee_amount": float(platform_fee),
                    "host_payout_amount": float(host_payout),
                    "stripe_charge_id": payment_intent.latest_charge
                })
            elif payment_intent.status == "requires_action":
                update_data["payment_status"] = "processing"
            else:
                update_data["payment_status"] = payment_intent.status
            
            supabase_client.table("bookings").update(update_data).eq("id", booking_id).execute()
            
            logger.info(f"Updated booking {booking_id} with payment status: {payment_intent.status}")
            
            # Get receipt URL if available
            receipt_url = None
            if payment_intent.status == "succeeded" and payment_intent.latest_charge:
                charge = stripe.Charge.retrieve(payment_intent.latest_charge)
                receipt_url = charge.receipt_url
            
            return {
                "payment_intent_id": payment_intent_id,
                "booking_id": booking_id,
                "payment_status": payment_intent.status,
                "booking_status": update_data.get("status", "pending"),
                "amount_received": Decimal(str(payment_intent.amount_received / 100)),
                "receipt_url": receipt_url,
                "paid_at": datetime.fromtimestamp(payment_intent.created) if payment_intent.status == "succeeded" else None
            }
            
        except stripe.StripeError as e:
            logger.error(f"Stripe error confirming payment {payment_intent_id}: {e}")
            raise Exception(f"Failed to confirm payment: {str(e)}")
        except Exception as e:
            logger.error(f"Error confirming payment for booking {booking_id}: {e}")
            raise
    
    @staticmethod
    async def create_refund(
        booking_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a refund for a booking
        
        Args:
            booking_id: UUID of the booking
            amount: Amount to refund (None for full refund)
            reason: Reason for refund
            
        Returns:
            Dictionary with refund details
        """
        try:
            # Get booking and payment intent
            booking_result = supabase_client.table("bookings").select(
                "id, stripe_payment_intent_id, stripe_charge_id, total_amount, refund_amount, payment_status"
            ).eq("id", booking_id).execute()
            
            if not booking_result.data:
                raise ValueError(f"Booking {booking_id} not found")
            
            booking = booking_result.data[0]
            
            if booking["payment_status"] != "succeeded":
                raise ValueError(f"Cannot refund booking with payment status: {booking['payment_status']}")
            
            if not booking["stripe_charge_id"]:
                raise ValueError(f"No charge ID found for booking {booking_id}")
            
            # Calculate refund amount
            total_amount = Decimal(str(booking["total_amount"]))
            already_refunded = Decimal(str(booking.get("refund_amount", 0)))
            
            if amount is None:
                refund_amount = total_amount - already_refunded
            else:
                refund_amount = amount
            
            if refund_amount <= 0:
                raise ValueError("Refund amount must be greater than 0")
            
            if refund_amount + already_refunded > total_amount:
                raise ValueError("Refund amount exceeds available amount")
            
            # Convert to fils
            refund_amount_fils = int(float(refund_amount) * 100)
            
            # Create refund
            refund = stripe.Refund.create(
                charge=booking["stripe_charge_id"],
                amount=refund_amount_fils,
                reason=reason or "requested_by_customer",
                metadata={
                    "booking_id": booking_id,
                    "platform": "krib_host_dashboard"
                }
            )
            
            logger.info(f"Created refund {refund.id} for booking {booking_id}, amount: {refund_amount}")
            
            # Update booking
            new_refund_total = already_refunded + refund_amount
            new_payment_status = "refunded" if new_refund_total >= total_amount else "partially_refunded"
            
            supabase_client.table("bookings").update({
                "refund_amount": float(new_refund_total),
                "payment_status": new_payment_status,
                "refund_reason": reason,
                "status": "cancelled" if new_payment_status == "refunded" else booking.get("status"),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", booking_id).execute()
            
            return {
                "refund_id": refund.id,
                "booking_id": booking_id,
                "payment_intent_id": booking["stripe_payment_intent_id"],
                "amount": refund_amount,
                "currency": refund.currency.upper(),
                "status": refund.status,
                "reason": reason,
                "created_at": datetime.fromtimestamp(refund.created)
            }
            
        except stripe.StripeError as e:
            logger.error(f"Stripe error creating refund for booking {booking_id}: {e}")
            raise Exception(f"Failed to create refund: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating refund for booking {booking_id}: {e}")
            raise
    
    @staticmethod
    async def handle_payment_intent_succeeded(payment_intent_id: str, payment_intent_data: Dict[str, Any]) -> None:
        """
        Handle payment_intent.succeeded webhook
        
        Args:
            payment_intent_id: Stripe PaymentIntent ID
            payment_intent_data: Payment intent data from webhook
        """
        try:
            # Find booking with this payment intent
            booking_result = supabase_client.table("bookings").select(
                "id, total_amount"
            ).eq("stripe_payment_intent_id", payment_intent_id).execute()
            
            if not booking_result.data:
                logger.warning(f"No booking found with payment intent {payment_intent_id}")
                return
            
            booking = booking_result.data[0]
            booking_id = booking["id"]
            
            # Confirm payment
            await StripePaymentService.confirm_payment(payment_intent_id, booking_id)
            
            logger.info(f"Processed payment_intent.succeeded for booking {booking_id}")
            
        except Exception as e:
            logger.error(f"Error handling payment_intent.succeeded for {payment_intent_id}: {e}")
            raise


stripe_payment_service = StripePaymentService()

