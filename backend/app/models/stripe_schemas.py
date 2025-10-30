"""
Pydantic schemas for Stripe-related operations
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal


# =====================================================================
# Connect Account Schemas
# =====================================================================

class ConnectAccountCreate(BaseModel):
    """Request to create Stripe Connect account"""
    country: str = Field(default="AE", description="ISO country code (AE for UAE)")
    email: EmailStr = Field(description="Host email address")
    business_type: str = Field(default="individual", description="individual or company")


class ConnectAccountStatus(BaseModel):
    """Stripe Connect account status"""
    stripe_account_id: str
    status: str  # not_connected, pending, active, restricted, disabled
    charges_enabled: bool
    payouts_enabled: bool
    details_submitted: bool
    onboarding_completed: bool
    bank_account_last4: Optional[str] = None
    bank_account_country: Optional[str] = None
    requirements: Dict[str, List[str]] = Field(
        default_factory=lambda: {
            "currently_due": [],
            "eventually_due": [],
            "past_due": []
        }
    )
    updated_at: Optional[datetime] = None


class OnboardingLinkResponse(BaseModel):
    """Response with onboarding link"""
    url: str
    expires_at: int  # Unix timestamp
    created: int  # Unix timestamp


class DashboardLinkResponse(BaseModel):
    """Response with dashboard link"""
    url: str
    expires_at: int  # Unix timestamp


# =====================================================================
# Payment Intent Schemas
# =====================================================================

class PaymentIntentCreate(BaseModel):
    """Request to create payment intent"""
    booking_id: str = Field(description="UUID of the booking")
    amount: Decimal = Field(gt=0, description="Total amount in AED")
    currency: str = Field(default="AED")
    payment_method_types: List[str] = Field(default=["card"])
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PaymentIntentResponse(BaseModel):
    """Payment intent response"""
    payment_intent_id: str
    client_secret: str
    amount: Decimal
    currency: str
    status: str  # requires_payment_method, requires_confirmation, succeeded, etc.
    created: int


class PaymentConfirm(BaseModel):
    """Request to confirm payment"""
    payment_intent_id: str
    booking_id: str


class PaymentStatus(BaseModel):
    """Payment status response"""
    payment_intent_id: str
    booking_id: str
    payment_status: str
    booking_status: str
    amount_received: Decimal
    receipt_url: Optional[str] = None
    paid_at: Optional[datetime] = None


# =====================================================================
# Payout Schemas
# =====================================================================

class PayoutProcess(BaseModel):
    """Request to process payout"""
    booking_id: str
    platform_fee_percentage: Optional[Decimal] = Field(default=15.0, ge=0, le=100)
    description: Optional[str] = None


class PayoutResponse(BaseModel):
    """Payout processing response"""
    payout_id: str
    transfer_id: Optional[str] = None
    host_user_id: str
    booking_id: str
    amount: Decimal
    platform_fee: Decimal
    host_amount: Decimal
    currency: str
    status: str  # pending, processing, in_transit, paid, failed
    initiated_at: datetime
    expected_arrival_date: Optional[date] = None


class PayoutDetail(BaseModel):
    """Detailed payout information"""
    id: str
    booking_id: Optional[str] = None
    property_id: Optional[str] = None
    property_title: Optional[str] = None
    amount: Decimal
    currency: str
    platform_fee: Decimal
    original_booking_amount: Optional[Decimal] = None
    status: str
    description: Optional[str] = None
    failure_message: Optional[str] = None
    initiated_at: datetime
    completed_at: Optional[datetime] = None
    expected_arrival_date: Optional[date] = None
    stripe_transfer_id: Optional[str] = None


class PayoutList(BaseModel):
    """List of payouts for a host"""
    payouts: List[PayoutDetail]
    total_count: int
    total_paid: Decimal
    total_pending: Decimal
    total_in_transit: Decimal
    total_failed: Decimal


# =====================================================================
# Webhook Schemas
# =====================================================================

class WebhookEvent(BaseModel):
    """Stripe webhook event"""
    id: str = Field(description="Stripe event ID")
    type: str = Field(description="Event type")
    data: Dict[str, Any] = Field(description="Event data")
    created: int = Field(description="Unix timestamp")
    api_version: Optional[str] = None


# =====================================================================
# Refund Schemas
# =====================================================================

class RefundCreate(BaseModel):
    """Request to create refund"""
    booking_id: str
    amount: Optional[Decimal] = Field(default=None, ge=0, description="Amount to refund (None for full refund)")
    reason: Optional[str] = Field(default=None, description="Reason for refund")


class RefundResponse(BaseModel):
    """Refund response"""
    refund_id: str
    booking_id: str
    payment_intent_id: str
    amount: Decimal
    currency: str
    status: str  # succeeded, pending, failed
    reason: Optional[str] = None
    created_at: datetime


# =====================================================================
# External API Payment Schemas (for AI agents)
# =====================================================================

class ExternalBookingPayment(BaseModel):
    """Payment information for external booking"""
    payment_method: str = Field(description="Payment method type (card, etc.)")
    payment_token: Optional[str] = Field(default=None, description="Stripe payment token")
    payment_method_id: Optional[str] = Field(default=None, description="Stripe PaymentMethod ID")
    process_payment: bool = Field(default=True, description="Whether to process payment immediately")
    save_payment_method: bool = Field(default=False, description="Save for future use")


class ExternalBookingWithPayment(BaseModel):
    """External booking request with payment"""
    property_id: str
    guest_name: str
    guest_email: EmailStr
    guest_phone: Optional[str] = None
    check_in: date
    check_out: date
    number_of_guests: int = Field(gt=0, le=50)
    total_price: Decimal = Field(gt=0)
    special_requests: Optional[str] = None
    payment: ExternalBookingPayment


class ExternalBookingPaymentResponse(BaseModel):
    """Response for external booking with payment"""
    booking_id: str
    status: str  # pending_payment, confirmed, failed
    payment_status: str
    confirmation_code: Optional[str] = None
    payment_details: Optional[PaymentStatus] = None
    requires_action: bool = Field(default=False)
    client_secret: Optional[str] = Field(default=None, description="For 3D Secure if needed")

