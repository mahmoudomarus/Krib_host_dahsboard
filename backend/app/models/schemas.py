"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


# Enums
class PropertyType(str, Enum):
    apartment = "apartment"
    house = "house"
    condo = "condo"
    villa = "villa"
    studio = "studio"
    cabin = "cabin"
    other = "other"


class PropertyStatus(str, Enum):
    draft = "draft"
    active = "active"
    inactive = "inactive"
    suspended = "suspended"


class BookingStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"


class PaymentStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    refunded = "refunded"


# User Models
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    settings: Optional[Dict[str, Any]] = None
    total_revenue: float = 0


# Property Models
class PropertyCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    address: str = Field(..., min_length=5, max_length=500)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    country: str = Field(..., min_length=1, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    property_type: PropertyType
    bedrooms: int = Field(..., ge=0, le=20)
    bathrooms: float = Field(..., ge=0, le=20)
    max_guests: int = Field(..., ge=1, le=50)
    price_per_night: float = Field(..., gt=0, le=10000)
    amenities: List[str] = []
    images: List[str] = []
    
    @validator('bathrooms')
    def validate_bathrooms(cls, v):
        # Allow half bathrooms (0.5, 1.5, etc.)
        if v * 2 != int(v * 2):
            raise ValueError('Bathrooms must be whole or half numbers (e.g., 1, 1.5, 2)')
        return v


class PropertyUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    address: Optional[str] = Field(None, min_length=5, max_length=500)
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    property_type: Optional[PropertyType] = None
    bedrooms: Optional[int] = Field(None, ge=0, le=20)
    bathrooms: Optional[float] = Field(None, ge=0, le=20)
    max_guests: Optional[int] = Field(None, ge=1, le=50)
    price_per_night: Optional[float] = Field(None, gt=0, le=10000)
    amenities: Optional[List[str]] = None
    images: Optional[List[str]] = None
    status: Optional[PropertyStatus] = None


class PropertyResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    address: str
    city: str
    state: str
    country: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    property_type: PropertyType
    bedrooms: int
    bathrooms: float
    max_guests: int
    price_per_night: float
    amenities: List[str]
    images: List[str]
    status: PropertyStatus
    rating: float = 0
    review_count: int = 0
    booking_count: int = 0
    total_revenue: float = 0
    created_at: datetime
    updated_at: datetime


# Booking Models
class BookingCreate(BaseModel):
    property_id: str
    guest_name: str = Field(..., min_length=1, max_length=100)
    guest_email: EmailStr
    guest_phone: Optional[str] = None
    check_in: date
    check_out: date
    guests: int = Field(..., ge=1, le=50)
    special_requests: Optional[str] = Field(None, max_length=500)
    
    @validator('check_out')
    def validate_dates(cls, v, values):
        if 'check_in' in values and v <= values['check_in']:
            raise ValueError('Check-out date must be after check-in date')
        return v


class BookingUpdate(BaseModel):
    guest_name: Optional[str] = Field(None, min_length=1, max_length=100)
    guest_email: Optional[EmailStr] = None
    guest_phone: Optional[str] = None
    check_in: Optional[date] = None
    check_out: Optional[date] = None
    guests: Optional[int] = Field(None, ge=1, le=50)
    status: Optional[BookingStatus] = None
    payment_status: Optional[PaymentStatus] = None
    special_requests: Optional[str] = Field(None, max_length=500)


class BookingResponse(BaseModel):
    id: str
    property_id: str
    guest_name: str
    guest_email: str
    guest_phone: Optional[str] = None
    check_in: date
    check_out: date
    nights: int
    guests: int
    total_amount: float
    status: BookingStatus
    payment_status: PaymentStatus
    special_requests: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Include property details for convenience
    property_title: Optional[str] = None
    property_address: Optional[str] = None


# Review Models
class ReviewCreate(BaseModel):
    property_id: str
    booking_id: Optional[str] = None
    guest_name: str = Field(..., min_length=1, max_length=100)
    guest_email: EmailStr
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)


class ReviewResponse(BaseModel):
    id: str
    property_id: str
    booking_id: Optional[str] = None
    guest_name: str
    guest_email: str
    rating: int
    comment: Optional[str] = None
    created_at: datetime


# AI Service Models
class AIDescriptionRequest(BaseModel):
    property_data: Dict[str, Any]
    use_anthropic: bool = False


class AIDescriptionResponse(BaseModel):
    description: str
    summary: str
    highlights: List[str]


class AmenitiesSuggestionRequest(BaseModel):
    property_data: Dict[str, Any]
    existing_amenities: List[str] = []


class AmenitiesSuggestionResponse(BaseModel):
    suggested_amenities: List[str]


class TitleOptimizationRequest(BaseModel):
    original_title: str
    property_data: Dict[str, Any]


class TitleOptimizationResponse(BaseModel):
    optimized_titles: List[str]


class PricingStrategyRequest(BaseModel):
    property_data: Dict[str, Any]
    market_data: Optional[Dict[str, Any]] = None


class PricingStrategyResponse(BaseModel):
    base_price: float
    weekend_multiplier: float
    seasonal_adjustments: Dict[str, float]
    suggested_range: Dict[str, float]
    recommendations: List[str]


# Upload Models
class ImageUploadResponse(BaseModel):
    url: str
    s3_key: str
    size: int
    content_type: str


class PresignedUploadRequest(BaseModel):
    filename: str
    content_type: str
    property_id: str


class PresignedUploadResponse(BaseModel):
    upload_url: str
    fields: Dict[str, str]
    final_url: str
    s3_key: str


# Analytics Models
class PropertyAnalytics(BaseModel):
    property_id: str
    date: date
    views: int = 0
    bookings: int = 0
    revenue: float = 0
    occupancy_rate: float = 0
    avg_daily_rate: float = 0


class AnalyticsResponse(BaseModel):
    total_revenue: float
    total_bookings: int
    total_properties: int
    occupancy_rate: float
    monthly_data: List[Dict[str, Any]]
    property_performance: List[Dict[str, Any]]
    market_insights: Dict[str, Any]
    forecast: Dict[str, Any]
    recommendations: List[Dict[str, Any]]


# Authentication Models
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# General Response Models
class SuccessResponse(BaseModel):
    success: bool = True
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None
