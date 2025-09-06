"""
Pydantic models for external API integrations
Schemas for third-party AI platforms and booking services
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal


# External Property Search Models
class PropertySearchFilters(BaseModel):
    # Location filters
    city: Optional[str] = Field(None, description="City or area name (e.g., 'Dubai Marina', 'Downtown')")
    state: Optional[str] = Field(None, description="UAE Emirate (Dubai, Abu Dhabi, etc.)")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude coordinate")
    radius_km: Optional[float] = Field(None, gt=0, le=100, description="Search radius in kilometers")
    
    # Property filters
    min_price_per_night: Optional[float] = Field(None, ge=0, description="Minimum price per night in AED")
    max_price_per_night: Optional[float] = Field(None, ge=0, description="Maximum price per night in AED")
    bedrooms: Optional[int] = Field(None, ge=0, le=20, description="Minimum number of bedrooms")
    bathrooms: Optional[float] = Field(None, ge=0, le=20, description="Minimum number of bathrooms")
    max_guests: Optional[int] = Field(None, ge=1, le=50, description="Minimum guest capacity")
    property_type: Optional[str] = Field(None, description="Property type (apartment, villa, studio, etc.)")
    
    # Availability filters
    check_in: Optional[date] = Field(None, description="Check-in date (YYYY-MM-DD)")
    check_out: Optional[date] = Field(None, description="Check-out date (YYYY-MM-DD)")
    
    # Feature filters
    amenities: Optional[List[str]] = Field([], description="Required amenities list")
    
    # Pagination and sorting
    limit: Optional[int] = Field(20, ge=1, le=50, description="Number of results to return")
    offset: Optional[int] = Field(0, ge=0, description="Number of results to skip")
    sort_by: Optional[str] = Field("price_asc", description="Sort order: price_asc, price_desc, rating, distance")
    
    @validator('check_out')
    def validate_dates(cls, v, values):
        if 'check_in' in values and values['check_in'] and v:
            if v <= values['check_in']:
                raise ValueError('Check-out date must be after check-in date')
        return v


class PropertyLocation(BaseModel):
    street: str = Field(..., description="Street address")
    area: str = Field(..., description="Area/District (e.g., Dubai Marina)")
    city: str = Field(..., description="City name")
    emirate: str = Field(..., description="UAE Emirate")
    country: str = Field(default="UAE", description="Country")
    coordinates: Dict[str, float] = Field(..., description="Latitude and longitude")


class PropertyHost(BaseModel):
    id: str = Field(..., description="Host user ID")
    name: str = Field(..., description="Host name")
    response_rate: Optional[int] = Field(95, ge=0, le=100, description="Response rate percentage")
    is_superhost: bool = Field(False, description="Superhost status")
    member_since: Optional[str] = Field(None, description="Host join date")


class PropertyRating(BaseModel):
    overall: float = Field(0.0, ge=0, le=5, description="Overall rating")
    total_reviews: int = Field(0, ge=0, description="Total number of reviews")
    cleanliness: Optional[float] = Field(0.0, ge=0, le=5, description="Cleanliness rating")
    communication: Optional[float] = Field(0.0, ge=0, le=5, description="Communication rating")
    location: Optional[float] = Field(0.0, ge=0, le=5, description="Location rating")
    value: Optional[float] = Field(0.0, ge=0, le=5, description="Value rating")


class PropertyImage(BaseModel):
    url: str = Field(..., description="Image URL")
    is_primary: bool = Field(False, description="Whether this is the main property image")
    order: int = Field(1, description="Display order")


class PropertySearchResult(BaseModel):
    id: str = Field(..., description="Property ID")
    title: str = Field(..., description="Property title")
    description: Optional[str] = Field(None, description="Property description")
    base_price_per_night: float = Field(..., description="Base price per night in AED")
    bedrooms: int = Field(..., description="Number of bedrooms")
    bathrooms: float = Field(..., description="Number of bathrooms")
    max_guests: int = Field(..., description="Maximum guest capacity")
    property_type: str = Field(..., description="Property type")
    
    # Location
    address: PropertyLocation = Field(..., description="Property address details")
    
    # Features
    amenities: List[str] = Field([], description="Property amenities list")
    
    # Images
    images: List[PropertyImage] = Field([], description="Property images")
    
    # Host information
    host: PropertyHost = Field(..., description="Host information")
    
    # Rating and reviews
    rating: Optional[PropertyRating] = Field(None, description="Property ratings")
    
    # Policies and rules
    check_in_time: str = Field("15:00", description="Check-in time")
    check_out_time: str = Field("11:00", description="Check-out time")
    minimum_nights: int = Field(1, ge=1, description="Minimum stay in nights")
    house_rules: List[str] = Field([], description="House rules list")
    
    # Metadata
    created_at: str = Field(..., description="Property creation date")
    updated_at: str = Field(..., description="Last update date")


class PropertySearchResponse(BaseModel):
    success: bool = Field(True, description="Request success status")
    data: Dict[str, Any] = Field(..., description="Search results data")
    pagination: Dict[str, Any] = Field(..., description="Pagination information")


# Availability Check Models
class AvailabilityRequest(BaseModel):
    check_in: date = Field(..., description="Check-in date")
    check_out: date = Field(..., description="Check-out date")
    guests: Optional[int] = Field(1, ge=1, le=50, description="Number of guests")
    
    @validator('check_out')
    def validate_dates(cls, v, values):
        if 'check_in' in values and v <= values['check_in']:
            raise ValueError('Check-out date must be after check-in date')
        return v


class AvailabilityResponse(BaseModel):
    property_id: str = Field(..., description="Property ID")
    check_in: str = Field(..., description="Check-in date")
    check_out: str = Field(..., description="Check-out date")
    guests: int = Field(..., description="Number of guests")
    is_available: bool = Field(..., description="Whether property is available")
    reasons: List[Optional[str]] = Field([], description="Reasons if not available")
    alternative_dates: List[Dict[str, str]] = Field([], description="Alternative date suggestions")


# Pricing Models
class PricingRequest(BaseModel):
    check_in: date = Field(..., description="Check-in date")
    check_out: date = Field(..., description="Check-out date")
    guests: int = Field(..., ge=1, le=50, description="Number of guests")
    promo_code: Optional[str] = Field(None, description="Promotional code")
    
    @validator('check_out')
    def validate_dates(cls, v, values):
        if 'check_in' in values and v <= values['check_in']:
            raise ValueError('Check-out date must be after check-in date')
        return v


class PricingBreakdownItem(BaseModel):
    name: str = Field(..., description="Fee description")
    amount: float = Field(..., description="Amount in AED")
    type: str = Field(..., description="Type: base, fee, tax, discount")


class PricingResponse(BaseModel):
    property_id: str = Field(..., description="Property ID")
    check_in: str = Field(..., description="Check-in date")
    check_out: str = Field(..., description="Check-out date")
    guests: int = Field(..., description="Number of guests")
    nights: int = Field(..., description="Number of nights")
    base_price: float = Field(..., description="Base accommodation cost")
    cleaning_fee: float = Field(0, description="Cleaning fee")
    service_fee: float = Field(0, description="Service fee")
    taxes: float = Field(0, description="Tourism taxes")
    discount: float = Field(0, description="Applied discount")
    total_price: float = Field(..., description="Total price including all fees")
    currency: str = Field("AED", description="Currency code")
    breakdown: List[PricingBreakdownItem] = Field([], description="Detailed price breakdown")


# External Booking Models
class GuestInfo(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50, description="Guest first name")
    last_name: str = Field(..., min_length=1, max_length=50, description="Guest last name")
    email: str = Field(..., description="Guest email address")
    phone: str = Field(..., description="Guest phone number")
    country_code: str = Field("+971", description="Phone country code")


class ExternalBookingRequest(BaseModel):
    property_id: str = Field(..., description="Property ID to book")
    check_in: date = Field(..., description="Check-in date")
    check_out: date = Field(..., description="Check-out date")
    guests: int = Field(..., ge=1, le=50, description="Number of guests")
    guest_info: GuestInfo = Field(..., description="Guest information")
    special_requests: Optional[str] = Field(None, max_length=500, description="Special requests")
    total_amount: float = Field(..., gt=0, description="Total booking amount in AED")
    payment_method: str = Field("pending", description="Payment method (pending, stripe, bank_transfer)")
    source: str = Field("krib_ai_agent", description="Booking source")
    
    @validator('check_out')
    def validate_dates(cls, v, values):
        if 'check_in' in values and v <= values['check_in']:
            raise ValueError('Check-out date must be after check-in date')
        return v


class BookingPaymentInfo(BaseModel):
    method: str = Field(..., description="Payment method")
    status: str = Field(..., description="Payment status")
    payment_intent_id: Optional[str] = Field(None, description="Payment processor ID")


class BookingPropertyInfo(BaseModel):
    id: str = Field(..., description="Property ID")
    title: str = Field(..., description="Property title")
    address: str = Field(..., description="Property address")


class BookingDates(BaseModel):
    check_in: str = Field(..., description="Check-in date")
    check_out: str = Field(..., description="Check-out date")
    nights: int = Field(..., description="Number of nights")


class ExternalBookingResponse(BaseModel):
    booking_id: str = Field(..., description="Unique booking ID")
    status: str = Field(..., description="Booking status")
    property: BookingPropertyInfo = Field(..., description="Property information")
    dates: BookingDates = Field(..., description="Booking dates")
    guest_info: GuestInfo = Field(..., description="Guest information")
    total_amount: float = Field(..., description="Total amount in AED")
    currency: str = Field("AED", description="Currency")
    payment: BookingPaymentInfo = Field(..., description="Payment information")
    next_steps: List[str] = Field([], description="Next steps for guest")
    cancellation_policy: str = Field("moderate", description="Cancellation policy")
    host_contact: Dict[str, str] = Field({}, description="Host contact information")


# Standard API Response Models
class ExternalAPIResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    data: Dict[str, Any] = Field(..., description="Response data")
    message: Optional[str] = Field(None, description="Success message")


class ExternalAPIError(BaseModel):
    success: bool = Field(False, description="Request success status")
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    code: Optional[str] = Field(None, description="Error code")
