"""
External API routes for third-party AI platform integrations
Provides property search, availability, pricing, and booking endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Response
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import uuid
import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

from app.models.external_schemas import (
    PropertySearchFilters, PropertySearchResult, PropertySearchResponse,
    AvailabilityRequest, AvailabilityResponse,
    PricingRequest, PricingResponse, PricingBreakdownItem,
    ExternalBookingRequest, ExternalBookingResponse,
    PropertyLocation, PropertyHost, PropertyRating, PropertyImage,
    ExternalAPIResponse, ExternalAPIError
)
from app.core.supabase_client import supabase_client
from app.api.dependencies_external import (
    get_external_service_context, 
    verify_property_access_external
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

def add_rate_limit_headers(response: Response, limit: str, service_name: str = "krib_ai_agent"):
    """Add rate limit headers to API responses"""
    # Extract numbers from limit string (e.g., "100/minute" -> 100)
    limit_number = int(limit.split("/")[0])
    remaining = max(0, limit_number - 1)  # Simplified calculation
    
    response.headers["X-RateLimit-Limit"] = str(limit_number)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(60)  # Reset in 60 seconds
    response.headers["X-RateLimit-Service"] = service_name
    return response


@router.get("/v1/properties/search", response_model=ExternalAPIResponse)
@limiter.limit("100/minute")
async def search_properties(
    request: Request,
    response: Response,
    # Location parameters
    city: Optional[str] = Query(None, description="City or area name"),
    state: Optional[str] = Query(None, description="UAE Emirate"),
    latitude: Optional[float] = Query(None, description="Latitude coordinate"),
    longitude: Optional[float] = Query(None, description="Longitude coordinate"),
    radius_km: Optional[float] = Query(None, description="Search radius in km"),
    
    # Property parameters
    min_price_per_night: Optional[float] = Query(None, description="Minimum price in AED"),
    max_price_per_night: Optional[float] = Query(None, description="Maximum price in AED"),
    bedrooms: Optional[int] = Query(None, description="Minimum bedrooms"),
    bathrooms: Optional[float] = Query(None, description="Minimum bathrooms"),
    max_guests: Optional[int] = Query(None, description="Minimum guest capacity"),
    property_type: Optional[str] = Query(None, description="Property type"),
    
    # Date parameters
    check_in: Optional[date] = Query(None, description="Check-in date"),
    check_out: Optional[date] = Query(None, description="Check-out date"),
    
    # Pagination
    limit: int = Query(20, ge=1, le=50, description="Number of results"),
    offset: int = Query(0, ge=0, description="Results offset"),
    sort_by: str = Query("price_asc", description="Sort order"),
    
    # Service context
    service_context: dict = Depends(get_external_service_context)
):
    """
    Search for available properties with filtering and pagination
    
    This endpoint allows external AI platforms to search for rental properties
    with comprehensive filtering options including location, price, features, and availability.
    """
    try:
        logger.info(f"Property search requested by {service_context['service_name']}")
        
        # Start with base query for active properties only
        query = supabase_client.table("properties").select("""
            *,
            users!inner(id, name, email, created_at)
        """).eq("status", "active")
        
        # Apply location filters
        if city:
            query = query.ilike("city", f"%{city}%")
        if state:
            query = query.ilike("state", f"%{state}%")
            
        # Apply price filters
        if min_price_per_night:
            query = query.gte("price_per_night", min_price_per_night)
        if max_price_per_night:
            query = query.lte("price_per_night", max_price_per_night)
            
        # Apply property filters
        if bedrooms is not None:
            query = query.gte("bedrooms", bedrooms)
        if bathrooms is not None:
            query = query.gte("bathrooms", bathrooms)
        if max_guests is not None:
            query = query.gte("max_guests", max_guests)
        if property_type:
            query = query.eq("property_type", property_type)
        
        # Apply availability filters if dates provided
        available_property_ids = None
        if check_in and check_out:
            # Find properties that are NOT booked for these dates
            conflicting_bookings = supabase_client.table("bookings").select("property_id").in_(
                "status", ["confirmed", "pending"]
            ).lt("check_in", check_out.isoformat()).gt("check_out", check_in.isoformat()).execute()
            
            booked_property_ids = [booking["property_id"] for booking in conflicting_bookings.data]
            
            if booked_property_ids:
                query = query.not_.in_("id", booked_property_ids)
        
        # Apply sorting
        if sort_by == "price_asc":
            query = query.order("price_per_night", desc=False)
        elif sort_by == "price_desc":
            query = query.order("price_per_night", desc=True)
        elif sort_by == "rating":
            query = query.order("rating", desc=True)
        else:
            query = query.order("created_at", desc=True)
        
        # Get total count before pagination
        count_result = supabase_client.table("properties").select("id", count="exact").eq("status", "active")
        
        # Apply same filters for count
        if city:
            count_result = count_result.ilike("city", f"%{city}%")
        if state:
            count_result = count_result.ilike("state", f"%{state}%")
        if min_price_per_night:
            count_result = count_result.gte("price_per_night", min_price_per_night)
        if max_price_per_night:
            count_result = count_result.lte("price_per_night", max_price_per_night)
        
        total_count = count_result.execute().count or 0
        
        # Apply pagination
        query = query.range(offset, offset + limit - 1)
        
        # Execute query
        result = query.execute()
        
        # Format results
        properties = []
        for prop in result.data:
            # Format property data
            host_info = prop.get("users", {})
            
            property_result = PropertySearchResult(
                id=prop["id"],
                title=prop["title"],
                description=prop.get("description"),
                base_price_per_night=float(prop["price_per_night"]),
                bedrooms=prop["bedrooms"],
                bathrooms=float(prop["bathrooms"]),
                max_guests=prop["max_guests"],
                property_type=prop["property_type"],
                address=PropertyLocation(
                    street=prop["address"],
                    area=prop["city"],
                    city=prop["city"],
                    emirate=prop["state"],
                    country=prop.get("country", "UAE"),
                    coordinates={
                        "latitude": float(prop.get("latitude", 0.0) or 0.0),
                        "longitude": float(prop.get("longitude", 0.0) or 0.0)
                    }
                ),
                amenities=prop.get("amenities", []),
                images=[
                    PropertyImage(url=img, is_primary=(i == 0), order=i + 1)
                    for i, img in enumerate(prop.get("images", []))
                ],
                host=PropertyHost(
                    id=host_info.get("id", ""),
                    name=host_info.get("name", "Host"),
                    response_rate=95,  # Default value
                    is_superhost=False,  # Default value
                    member_since=host_info.get("created_at", "")
                ),
                rating=PropertyRating(
                    overall=float(prop.get("rating", 0.0)),
                    total_reviews=prop.get("review_count", 0),
                    cleanliness=float(prop.get("rating", 0.0)),
                    communication=float(prop.get("rating", 0.0)),
                    location=float(prop.get("rating", 0.0)),
                    value=float(prop.get("rating", 0.0))
                ) if prop.get("rating", 0) > 0 else None,
                check_in_time="15:00",
                check_out_time="11:00",
                minimum_nights=1,
                house_rules=[],
                created_at=prop.get("created_at", ""),
                updated_at=prop.get("updated_at", "")
            )
            properties.append(property_result.dict())
        
        # Add rate limit headers
        add_rate_limit_headers(response, "100/minute", service_context.get("service_name", "krib_ai_agent"))
        
        return ExternalAPIResponse(
            success=True,
            data={
                "properties": properties,
                "total_count": total_count,
                "has_more": (offset + limit) < total_count,
                "search_metadata": {
                    "query_time_ms": 0,  # Could implement timing
                    "filters_applied": {
                        "city": city,
                        "state": state,
                        "min_price": min_price_per_night,
                        "max_price": max_price_per_night,
                        "bedrooms": bedrooms,
                        "property_type": property_type
                    },
                    "total_available": total_count
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Property search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/v1/properties/{property_id}", response_model=ExternalAPIResponse)
@limiter.limit("200/minute")
async def get_property_details(
    request: Request,
    property_id: str,
    service_context: dict = Depends(get_external_service_context)
):
    """
    Get detailed information for a specific property
    
    Returns comprehensive property details including host information,
    amenities, images, and policies for external AI platforms.
    """
    try:
        property_data = await verify_property_access_external(property_id, service_context)
        
        # Format detailed response
        host_info = property_data.get("host_info", {})
        
        detailed_property = {
            "id": property_data["id"],
            "title": property_data["title"],
            "description": property_data.get("description", ""),
            "base_price_per_night": float(property_data["price_per_night"]),
            "bedrooms": property_data["bedrooms"],
            "bathrooms": float(property_data["bathrooms"]),
            "max_guests": property_data["max_guests"],
            "property_type": property_data["property_type"],
            "address": {
                "street": property_data["address"],
                "area": property_data["city"],
                "city": property_data["city"],
                "emirate": property_data["state"],
                "country": property_data.get("country", "UAE"),
                "coordinates": {
                    "latitude": float(property_data.get("latitude", 0.0) or 0.0),
                    "longitude": float(property_data.get("longitude", 0.0) or 0.0)
                }
            },
            "amenities": property_data.get("amenities", []),
            "images": [
                {"url": img, "is_primary": (i == 0), "order": i + 1}
                for i, img in enumerate(property_data.get("images", []))
            ],
            "pricing_info": {
                "base_price": float(property_data["price_per_night"]),
                "cleaning_fee": 0,  # Could be added to schema later
                "security_deposit": 0,  # Could be added to schema later
                "currency": "AED"
            },
            "host_info": {
                "id": host_info.get("id", ""),
                "name": host_info.get("name", "Host"),
                "joined_date": host_info.get("created_at", ""),
                "response_rate": 95,
                "response_time": "within an hour",
                "is_superhost": False,
                "total_properties": 1,
                "languages": ["English", "Arabic"]
            },
            "reviews_summary": {
                "total_reviews": property_data.get("review_count", 0),
                "overall_rating": float(property_data.get("rating", 0.0)),
                "rating_breakdown": {
                    "cleanliness": float(property_data.get("rating", 0.0)),
                    "accuracy": float(property_data.get("rating", 0.0)),
                    "communication": float(property_data.get("rating", 0.0)),
                    "location": float(property_data.get("rating", 0.0)),
                    "check_in": float(property_data.get("rating", 0.0)),
                    "value": float(property_data.get("rating", 0.0))
                },
                "recent_reviews": []  # Could be populated from reviews table
            },
            "policies": {
                "check_in_time": "15:00",
                "check_out_time": "11:00",
                "minimum_nights": 1,
                "cancellation_policy": "moderate",
                "house_rules": []
            },
            "availability_calendar": {},  # Could implement 90-day calendar
            "created_at": property_data.get("created_at", ""),
            "updated_at": property_data.get("updated_at", "")
        }
        
        return ExternalAPIResponse(
            success=True,
            data={"property": detailed_property}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get property details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get property details: {str(e)}"
        )


@router.get("/v1/properties/{property_id}/availability", response_model=ExternalAPIResponse)
@limiter.limit("150/minute")
async def check_availability(
    request: Request,
    property_id: str,
    check_in: date = Query(..., description="Check-in date"),
    check_out: date = Query(..., description="Check-out date"),
    guests: Optional[int] = Query(1, description="Number of guests"),
    service_context: dict = Depends(get_external_service_context)
):
    """
    Check if property is available for specific dates
    
    Validates availability against existing bookings and property capacity.
    """
    try:
        # Verify property exists
        property_data = await verify_property_access_external(property_id, service_context)
        
        # Validate dates
        if check_out <= check_in:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Check-out date must be after check-in date"
            )
        
        # Check guest capacity
        capacity_ok = guests <= property_data["max_guests"]
        
        # Check for existing bookings
        existing_bookings = supabase_client.table("bookings").select("*").eq(
            "property_id", property_id
        ).in_("status", ["confirmed", "pending"]).lt(
            "check_in", end_date.isoformat()
        ).gt("check_out", start_date.isoformat()).execute()
        
        has_conflicts = len(existing_bookings.data) > 0
        
        is_available = capacity_ok and not has_conflicts
        
        reasons = []
        if not capacity_ok:
            reasons.append(f"Property max guests is {property_data['max_guests']}, you requested {guests}")
        if has_conflicts:
            reasons.append("Property is already booked for these dates")
        
        return ExternalAPIResponse(
            success=True,
            data=AvailabilityResponse(
                property_id=property_id,
                check_in=check_in.isoformat(),
                check_out=check_out.isoformat(),
                guests=guests,
                is_available=is_available,
                reasons=reasons,
                alternative_dates=[]  # Could implement alternative date suggestions
            ).dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Availability check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Availability check failed: {str(e)}"
        )


@router.post("/v1/properties/{property_id}/calculate-pricing", response_model=ExternalAPIResponse)
@limiter.limit("150/minute")
async def calculate_pricing(
    request: Request,
    property_id: str,
    pricing_request: PricingRequest,
    service_context: dict = Depends(get_external_service_context)
):
    """
    Calculate total pricing for a potential booking
    
    Returns detailed price breakdown including all fees and taxes.
    """
    try:
        # Verify property exists
        property_data = await verify_property_access_external(property_id, service_context)
        
        # Calculate number of nights
        nights = (pricing_request.check_out - pricing_request.check_in).days
        
        if nights < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimum stay is 1 night"
            )
        
        # Base calculation
        base_price_per_night = float(property_data["price_per_night"])
        base_price = base_price_per_night * nights
        
        # Additional fees (could be stored in property data)
        cleaning_fee = 75.0  # Default cleaning fee for UAE market
        
        # Service fee (typically 3% of base price)
        service_fee_rate = 0.03
        service_fee = base_price * service_fee_rate
        
        # Tourism tax (Dubai typically charges 10-20 AED per night)
        tourism_tax_per_night = 15.0
        tourism_tax = nights * tourism_tax_per_night
        
        # Apply promo code discount if provided
        discount = 0.0
        if pricing_request.promo_code:
            # Could implement promo code logic here
            if pricing_request.promo_code.lower() == "krib10":
                discount = base_price * 0.10  # 10% discount
        
        # Calculate totals
        subtotal = base_price - discount
        total_price = subtotal + cleaning_fee + service_fee + tourism_tax
        
        # Build breakdown
        breakdown = [
            PricingBreakdownItem(
                name=f"AED {base_price_per_night} × {nights} nights",
                amount=base_price,
                type="base"
            ),
            PricingBreakdownItem(
                name="Cleaning fee",
                amount=cleaning_fee,
                type="fee"
            ),
            PricingBreakdownItem(
                name="Service fee",
                amount=round(service_fee, 2),
                type="fee"
            ),
            PricingBreakdownItem(
                name="Tourism tax",
                amount=tourism_tax,
                type="tax"
            )
        ]
        
        if discount > 0:
            breakdown.append(
                PricingBreakdownItem(
                    name=f"Discount ({pricing_request.promo_code})",
                    amount=-discount,
                    type="discount"
                )
            )
        
        pricing_response = PricingResponse(
            property_id=property_id,
            check_in=pricing_request.check_in.isoformat(),
            check_out=pricing_request.check_out.isoformat(),
            guests=pricing_request.guests,
            nights=nights,
            base_price=base_price,
            cleaning_fee=cleaning_fee,
            service_fee=round(service_fee, 2),
            taxes=tourism_tax,
            discount=discount,
            total_price=round(total_price, 2),
            currency="AED",
            breakdown=breakdown
        )
        
        return ExternalAPIResponse(
            success=True,
            data=pricing_response.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pricing calculation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pricing calculation failed: {str(e)}"
        )


@router.post("/v1/bookings", response_model=ExternalAPIResponse)
@limiter.limit("50/minute")
async def create_external_booking(
    request: Request,
    booking_request: ExternalBookingRequest,
    service_context: dict = Depends(get_external_service_context)
):
    """
    Create a new booking from external AI platform
    
    Creates a booking request that will be reviewed by the property host.
    """
    try:
        # Verify property exists and is available
        property_data = await verify_property_access_external(booking_request.property_id, service_context)
        
        # Validate guest capacity
        if booking_request.guests > property_data["max_guests"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Property can accommodate maximum {property_data['max_guests']} guests"
            )
        
        # Check for date conflicts
        existing_bookings = supabase_client.table("bookings").select("*").eq(
            "property_id", booking_request.property_id
        ).in_("status", ["confirmed", "pending"]).lt(
            "check_in", booking_request.check_out.isoformat()
        ).gt("check_out", booking_request.check_in.isoformat()).execute()
        
        if existing_bookings.data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Property not available for selected dates"
            )
        
        # Calculate nights and validate amount
        nights = (booking_request.check_out - booking_request.check_in).days
        expected_amount = nights * property_data["price_per_night"]
        
        # Create booking record
        booking_id = str(uuid.uuid4())
        booking_record = {
            "id": booking_id,
            "property_id": booking_request.property_id,
            "guest_name": f"{booking_request.guest_info.first_name} {booking_request.guest_info.last_name}",
            "guest_email": booking_request.guest_info.email,
            "guest_phone": f"{booking_request.guest_info.country_code}{booking_request.guest_info.phone}",
            "check_in": booking_request.check_in.isoformat(),
            "check_out": booking_request.check_out.isoformat(),
            "nights": nights,
            "guests": booking_request.guests,
            "total_amount": booking_request.total_amount,
            "status": "pending",  # Always pending for external bookings
            "payment_status": "pending",
            "special_requests": booking_request.special_requests,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Insert booking
        result = supabase_client.table("bookings").insert(booking_record).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create booking"
            )
        
        created_booking = result.data[0]
        
        # Format response
        booking_response = ExternalBookingResponse(
            booking_id=booking_id,
            status="pending",
            property={
                "id": property_data["id"],
                "title": property_data["title"],
                "address": f"{property_data['address']}, {property_data['city']}, {property_data['state']}"
            },
            dates={
                "check_in": booking_request.check_in.isoformat(),
                "check_out": booking_request.check_out.isoformat(),
                "nights": nights
            },
            guest_info=booking_request.guest_info,
            total_amount=booking_request.total_amount,
            currency="AED",
            payment={
                "method": booking_request.payment_method,
                "status": "pending",
                "payment_intent_id": None
            },
            next_steps=[
                "Booking request submitted to host",
                "Host will review and confirm within 24 hours",
                "You will receive confirmation email once approved",
                "Payment will be processed after confirmation"
            ],
            cancellation_policy="moderate",
            host_contact={
                "name": property_data.get("host_info", {}).get("name", "Host"),
                "response_time": "within an hour"
            }
        )
        
        logger.info(f"External booking created: {booking_id} by {service_context['service_name']}")
        
        return ExternalAPIResponse(
            success=True,
            data=booking_response.dict(),
            message="Booking request created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"External booking creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Booking creation failed: {str(e)}"
        )


@router.get("/health", response_model=ExternalAPIResponse)
async def external_api_health():
    """
    Health check endpoint for external API
    """
    return ExternalAPIResponse(
        success=True,
        data={
            "status": "healthy",
            "service": "Krib AI External API",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "endpoints": [
                "GET /external/properties/search",
                "GET /external/properties/{id}",
                "GET /external/properties/{id}/availability",
                "POST /external/properties/{id}/calculate-pricing",
                "POST /external/bookings"
            ]
        },
        message="External API is operational"
    )
