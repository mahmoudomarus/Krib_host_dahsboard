"""
External API routes for third-party AI platform integrations
Provides property search, availability, pricing, and booking endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Response
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import uuid
import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

from app.models.external_schemas import (
    PropertySearchFilters,
    PropertySearchResult,
    PropertySearchResponse,
    AvailabilityRequest,
    AvailabilityResponse,
    PricingRequest,
    PricingResponse,
    PricingBreakdownItem,
    ExternalBookingRequest,
    ExternalBookingResponse,
    PropertyLocation,
    PropertyHost,
    PropertyRating,
    PropertyImage,
    ExternalAPIResponse,
    ExternalAPIError,
    HostPublicProfile,
    HostProfileResponse,
    ExternalMessageCreate,
    ExternalMessageResponse,
    ConversationMessage,
    ConversationThread,
)
from app.core.supabase_client import supabase_client
from app.api.dependencies_external import (
    get_external_service_context,
    verify_property_access_external,
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


def add_rate_limit_headers(
    response: Response, limit: str, service_name: str = "krib_ai_agent"
):
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
    min_price_per_night: Optional[float] = Query(
        None, description="Minimum price in AED"
    ),
    max_price_per_night: Optional[float] = Query(
        None, description="Maximum price in AED"
    ),
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
    service_context: dict = Depends(get_external_service_context),
):
    """
    Search for available properties with filtering and pagination

    This endpoint allows external AI platforms to search for rental properties
    with comprehensive filtering options including location, price, features, and availability.
    """
    try:
        logger.info(f"Property search requested by {service_context['service_name']}")

        # Start with base query for active properties only
        query = (
            supabase_client.table("properties")
            .select(
                """
            *,
            users!inner(id, name, email, created_at)
        """
            )
            .eq("status", "active")
        )

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
        if check_in and check_out:
            # Find properties that are NOT booked for these dates
            conflicting_bookings = (
                supabase_client.table("bookings")
                .select("property_id")
                .in_("status", ["confirmed", "pending"])
                .lt("check_in", check_out.isoformat())
                .gt("check_out", check_in.isoformat())
                .execute()
            )

            booked_property_ids = [
                booking["property_id"] for booking in conflicting_bookings.data
            ]

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
        count_result = (
            supabase_client.table("properties")
            .select("id", count="exact")
            .eq("status", "active")
        )

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
                        "longitude": float(prop.get("longitude", 0.0) or 0.0),
                    },
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
                    member_since=host_info.get("created_at", ""),
                ),
                rating=(
                    PropertyRating(
                        overall=float(prop.get("rating", 0.0)),
                        total_reviews=prop.get("review_count", 0),
                        cleanliness=float(prop.get("rating", 0.0)),
                        communication=float(prop.get("rating", 0.0)),
                        location=float(prop.get("rating", 0.0)),
                        value=float(prop.get("rating", 0.0)),
                    )
                    if prop.get("rating", 0) > 0
                    else None
                ),
                check_in_time="15:00",
                check_out_time="11:00",
                minimum_nights=1,
                house_rules=[],
                created_at=prop.get("created_at", ""),
                updated_at=prop.get("updated_at", ""),
            )
            properties.append(property_result.dict())

        # Add rate limit headers
        add_rate_limit_headers(
            response, "100/minute", service_context.get("service_name", "krib_ai_agent")
        )

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
                        "property_type": property_type,
                    },
                    "total_available": total_count,
                },
            },
        )

    except Exception as e:
        logger.error(f"Property search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        )


@router.get("/v1/properties/{property_id}", response_model=ExternalAPIResponse)
@limiter.limit("200/minute")
async def get_property_details(
    request: Request,
    property_id: str,
    service_context: dict = Depends(get_external_service_context),
):
    """
    Get detailed information for a specific property

    Returns comprehensive property details including host information,
    amenities, images, and policies for external AI platforms.
    """
    try:
        property_data = await verify_property_access_external(
            property_id, service_context
        )

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
                    "longitude": float(property_data.get("longitude", 0.0) or 0.0),
                },
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
                "currency": "AED",
            },
            "host_info": {
                "id": host_info.get("id", ""),
                "name": host_info.get("name", "Host"),
                "joined_date": host_info.get("created_at", ""),
                "response_rate": 95,
                "response_time": "within an hour",
                "is_superhost": False,
                "total_properties": 1,
                "languages": ["English", "Arabic"],
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
                    "value": float(property_data.get("rating", 0.0)),
                },
                "recent_reviews": [],  # Could be populated from reviews table
            },
            "policies": {
                "check_in_time": "15:00",
                "check_out_time": "11:00",
                "minimum_nights": 1,
                "cancellation_policy": "moderate",
                "house_rules": [],
            },
            "availability_calendar": {},  # Could implement 90-day calendar
            "created_at": property_data.get("created_at", ""),
            "updated_at": property_data.get("updated_at", ""),
        }

        return ExternalAPIResponse(success=True, data={"property": detailed_property})

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get property details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get property details: {str(e)}",
        )


@router.get(
    "/v1/properties/{property_id}/availability", response_model=ExternalAPIResponse
)
@limiter.limit("150/minute")
async def check_availability(
    request: Request,
    property_id: str,
    check_in: date = Query(..., description="Check-in date"),
    check_out: date = Query(..., description="Check-out date"),
    guests: Optional[int] = Query(1, description="Number of guests"),
    service_context: dict = Depends(get_external_service_context),
):
    """
    Check if property is available for specific dates

    Validates availability against existing bookings and property capacity.
    """
    try:
        # Verify property exists
        property_data = await verify_property_access_external(
            property_id, service_context
        )

        # Validate dates
        if check_out <= check_in:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Check-out date must be after check-in date",
            )

        # Check guest capacity
        capacity_ok = guests <= property_data["max_guests"]

        # Check for existing bookings
        existing_bookings = (
            supabase_client.table("bookings")
            .select("*")
            .eq("property_id", property_id)
            .in_("status", ["confirmed", "pending"])
            .lt("check_in", check_out.isoformat())
            .gt("check_out", check_in.isoformat())
            .execute()
        )

        has_conflicts = len(existing_bookings.data) > 0

        is_available = capacity_ok and not has_conflicts

        reasons = []
        if not capacity_ok:
            reasons.append(
                f"Property max guests is {property_data['max_guests']}, you requested {guests}"
            )
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
                alternative_dates=[],  # Could implement alternative date suggestions
            ).dict(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Availability check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Availability check failed: {str(e)}",
        )


@router.post(
    "/v1/properties/{property_id}/calculate-pricing", response_model=ExternalAPIResponse
)
@limiter.limit("150/minute")
async def calculate_pricing(
    request: Request,
    property_id: str,
    pricing_request: PricingRequest,
    service_context: dict = Depends(get_external_service_context),
):
    """
    Calculate total pricing for a potential booking

    Returns detailed price breakdown including all fees and taxes.
    """
    try:
        # Verify property exists
        property_data = await verify_property_access_external(
            property_id, service_context
        )

        # Calculate number of nights
        nights = (pricing_request.check_out - pricing_request.check_in).days

        if nights < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimum stay is 1 night",
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
                type="base",
            ),
            PricingBreakdownItem(name="Cleaning fee", amount=cleaning_fee, type="fee"),
            PricingBreakdownItem(
                name="Service fee", amount=round(service_fee, 2), type="fee"
            ),
            PricingBreakdownItem(name="Tourism tax", amount=tourism_tax, type="tax"),
        ]

        if discount > 0:
            breakdown.append(
                PricingBreakdownItem(
                    name=f"Discount ({pricing_request.promo_code})",
                    amount=-discount,
                    type="discount",
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
            breakdown=breakdown,
        )

        return ExternalAPIResponse(success=True, data=pricing_response.dict())

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pricing calculation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pricing calculation failed: {str(e)}",
        )


@router.post("/v1/bookings", response_model=ExternalAPIResponse)
@limiter.limit("50/minute")
async def create_external_booking(
    request: Request,
    booking_request: ExternalBookingRequest,
    service_context: dict = Depends(get_external_service_context),
):
    """
    Create a new booking from external AI platform

    Creates a booking request that will be reviewed by the property host.
    """
    try:
        # Verify property exists and is available
        property_data = await verify_property_access_external(
            booking_request.property_id, service_context
        )

        # Validate guest capacity
        if booking_request.guests > property_data["max_guests"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Property can accommodate maximum {property_data['max_guests']} guests",
            )

        # Check for date conflicts
        existing_bookings = (
            supabase_client.table("bookings")
            .select("*")
            .eq("property_id", booking_request.property_id)
            .in_("status", ["confirmed", "pending"])
            .lt("check_in", booking_request.check_out.isoformat())
            .gt("check_out", booking_request.check_in.isoformat())
            .execute()
        )

        if existing_bookings.data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Property not available for selected dates",
            )

        # Calculate nights
        nights = (booking_request.check_out - booking_request.check_in).days

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
            "updated_at": datetime.utcnow().isoformat(),
        }

        # Insert booking
        result = supabase_client.table("bookings").insert(booking_record).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create booking",
            )

        created_booking = result.data[0]

        # Send webhook for booking created
        from app.services.background_jobs import (
            send_booking_webhook,
            send_host_response_webhook,
        )

        webhook_data = {
            **created_booking,
            "property_info": {
                "id": property_data["id"],
                "title": property_data["title"],
            },
            "guest_info": booking_request.guest_info.dict(),
            "payment_info": {
                "method": booking_request.payment_method,
                "status": "pending",
            },
        }
        send_booking_webhook.delay("booking.created", booking_id, webhook_data)

        # Send host response needed webhook
        send_host_response_webhook.delay(
            booking_id,
            property_data["user_id"],
            {
                "booking_id": booking_id,
                "property_id": property_data["id"],
                "guest_name": f"{booking_request.guest_info.first_name} {booking_request.guest_info.last_name}",
                "check_in": booking_request.check_in.isoformat(),
                "check_out": booking_request.check_out.isoformat(),
                "total_amount": booking_request.total_amount,
                "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
            },
        )

        # Send host notification
        from app.services.notification_service import NotificationService

        await NotificationService.create_booking_notification(
            host_id=property_data["user_id"],
            booking_id=booking_id,
            property_id=property_data["id"],
            notification_type="new_booking",
            guest_name=f"{booking_request.guest_info.first_name} {booking_request.guest_info.last_name}",
            property_title=property_data["title"],
            booking_details=created_booking,
        )

        # Format response
        booking_response = ExternalBookingResponse(
            booking_id=booking_id,
            status="pending",
            property={
                "id": property_data["id"],
                "title": property_data["title"],
                "address": f"{property_data['address']}, {property_data['city']}, {property_data['state']}",
            },
            dates={
                "check_in": booking_request.check_in.isoformat(),
                "check_out": booking_request.check_out.isoformat(),
                "nights": nights,
            },
            guest_info=booking_request.guest_info,
            total_amount=booking_request.total_amount,
            currency="AED",
            payment={
                "method": booking_request.payment_method,
                "status": "pending",
                "payment_intent_id": None,
            },
            next_steps=[
                "Booking request submitted to host",
                "Host will review and confirm within 24 hours",
                "You will receive confirmation email once approved",
                "Payment will be processed after confirmation",
            ],
            cancellation_policy="moderate",
            host_contact={
                "name": property_data.get("host_info", {}).get("name", "Host"),
                "response_time": "within an hour",
            },
        )

        logger.info(
            f"External booking created: {booking_id} by {service_context['service_name']}"
        )

        return ExternalAPIResponse(
            success=True,
            data=booking_response.dict(),
            message="Booking request created successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"External booking creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Booking creation failed: {str(e)}",
        )


@router.get(
    "/v1/external/hosts/{host_id}/pending-bookings", response_model=ExternalAPIResponse
)
@limiter.limit("100/minute")
async def get_host_pending_bookings(
    request: Request,
    host_id: str,
    limit: int = Query(20, ge=1, le=100, description="Number of bookings to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    service_context: dict = Depends(get_external_service_context),
):
    """Get pending bookings for a host"""
    try:
        # Get host's properties
        properties_result = (
            supabase_client.table("properties")
            .select("id, title, address, city, state")
            .eq("user_id", host_id)
            .execute()
        )
        property_ids = [prop["id"] for prop in properties_result.data]
        properties_dict = {prop["id"]: prop for prop in properties_result.data}

        if not property_ids:
            return ExternalAPIResponse(
                success=True,
                data={
                    "bookings": [],
                    "total_count": 0,
                    "returned_count": 0,
                    "has_more": False,
                    "host_id": host_id,
                },
            )

        # Get total count of pending bookings
        count_result = (
            supabase_client.table("bookings")
            .select("id", count="exact")
            .in_("property_id", property_ids)
            .eq("status", "pending")
            .execute()
        )

        total_count = count_result.count or 0

        # Get pending bookings for host's properties with pagination
        bookings_result = (
            supabase_client.table("bookings")
            .select("*")
            .in_("property_id", property_ids)
            .eq("status", "pending")
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )

        bookings = []
        for booking in bookings_result.data:
            property_info = properties_dict.get(booking["property_id"], {})
            bookings.append(
                {
                    "id": booking["id"],
                    "property_id": booking["property_id"],
                    "property_title": property_info.get("title", ""),
                    "property_address": f"{property_info.get('address', '')}, {property_info.get('city', '')}, {property_info.get('state', '')}",
                    "guest_name": booking["guest_name"],
                    "guest_email": booking["guest_email"],
                    "guest_phone": booking["guest_phone"],
                    "check_in": booking["check_in"],
                    "check_out": booking["check_out"],
                    "nights": booking["nights"],
                    "guests": booking["guests"],
                    "total_amount": booking["total_amount"],
                    "special_requests": booking.get("special_requests", ""),
                    "created_at": booking["created_at"],
                    "updated_at": booking["updated_at"],
                }
            )

        return ExternalAPIResponse(
            success=True,
            data={
                "bookings": bookings,
                "total_count": total_count,
                "returned_count": len(bookings),
                "has_more": (offset + limit) < total_count,
                "host_id": host_id,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "next_offset": (
                        offset + limit if (offset + limit) < total_count else None
                    ),
                },
            },
        )

    except Exception as e:
        logger.error(f"Failed to get pending bookings for host {host_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pending bookings: {str(e)}",
        )


@router.put(
    "/v1/external/bookings/{booking_id}/status", response_model=ExternalAPIResponse
)
@limiter.limit("50/minute")
async def update_booking_status_external(
    request: Request,
    booking_id: str,
    status_update: Dict[str, str],
    service_context: dict = Depends(get_external_service_context),
):
    """Update booking status via external API"""
    try:
        new_status = status_update.get("status")
        if new_status not in ["confirmed", "cancelled", "pending"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status. Must be: confirmed, cancelled, or pending",
            )

        # Get booking details with property and host info
        booking_result = (
            supabase_client.table("bookings")
            .select(
                """
            *,
            properties!inner(id, title, user_id, address, city, state)
        """
            )
            .eq("id", booking_id)
            .execute()
        )

        if not booking_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
            )

        booking = booking_result.data[0]
        property_info = booking["properties"]
        host_id = property_info["user_id"]

        # Update booking status
        result = (
            supabase_client.table("bookings")
            .update({"status": new_status, "updated_at": datetime.utcnow().isoformat()})
            .eq("id", booking_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update booking status",
            )

        updated_booking = result.data[0]

        # Send webhook notification
        from app.services.background_jobs import send_booking_webhook

        webhook_data = {
            **updated_booking,
            "property_id": booking["property_id"],
            "host_id": host_id,
            "property_info": property_info,
            "guest_info": {
                "name": booking["guest_name"],
                "email": booking["guest_email"],
                "phone": booking["guest_phone"],
            },
        }
        send_booking_webhook.delay(f"booking.{new_status}", booking_id, webhook_data)

        # Send host notification
        from app.services.notification_service import NotificationService

        await NotificationService.create_booking_notification(
            host_id=host_id,
            booking_id=booking_id,
            property_id=booking["property_id"],
            notification_type=f"booking_{new_status}",
            guest_name=booking["guest_name"],
            property_title=property_info["title"],
            booking_details=updated_booking,
        )

        logger.info(
            f"Booking status updated via external API",
            extra={
                "booking_id": booking_id,
                "old_status": booking["status"],
                "new_status": new_status,
                "host_id": host_id,
                "service_name": service_context.get("service_name", "unknown"),
            },
        )

        return ExternalAPIResponse(
            success=True,
            data={
                "booking_id": booking_id,
                "old_status": booking["status"],
                "new_status": new_status,
                "updated_at": updated_booking["updated_at"],
                "host_id": host_id,
                "property_title": property_info["title"],
            },
            message=f"Booking status updated to {new_status}",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update booking status for {booking_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update booking status: {str(e)}",
        )


@router.post(
    "/v1/external/bookings/{booking_id}/auto-approve",
    response_model=ExternalAPIResponse,
)
@limiter.limit("20/minute")
async def auto_approve_booking(
    request: Request,
    booking_id: str,
    service_context: dict = Depends(get_external_service_context),
):
    """Auto-approve a booking based on host's settings"""
    try:
        # Get booking details with property and host info
        booking_result = (
            supabase_client.table("bookings")
            .select(
                """
            *,
            properties!inner(id, title, user_id, address, city, state)
        """
            )
            .eq("id", booking_id)
            .execute()
        )

        if not booking_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
            )

        booking = booking_result.data[0]
        property_info = booking["properties"]
        host_id = property_info["user_id"]

        # Check if booking is in pending status
        if booking["status"] != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot auto-approve booking with status: {booking['status']}",
            )

        # Check if host has auto-approval enabled
        settings_result = (
            supabase_client.table("host_settings")
            .select("auto_approve_bookings, auto_approve_amount_limit")
            .eq("user_id", host_id)
            .execute()
        )

        auto_approve = False
        amount_limit = 1000.0

        if settings_result.data:
            auto_approve = settings_result.data[0].get("auto_approve_bookings", False)
            amount_limit = float(
                settings_result.data[0].get("auto_approve_amount_limit", 1000.0)
            )

        if not auto_approve:
            return ExternalAPIResponse(
                success=False,
                data={
                    "booking_id": booking_id,
                    "auto_approve_enabled": False,
                    "reason": "Auto-approval not enabled for this host",
                },
                message="Auto-approval not enabled for this host",
            )

        # Check if booking amount is within auto-approval limit
        if booking["total_amount"] > amount_limit:
            return ExternalAPIResponse(
                success=False,
                data={
                    "booking_id": booking_id,
                    "auto_approve_enabled": True,
                    "amount_limit": amount_limit,
                    "booking_amount": booking["total_amount"],
                    "reason": f"Booking amount {booking['total_amount']} exceeds auto-approval limit {amount_limit}",
                },
                message="Booking amount exceeds auto-approval limit",
            )

        # Auto-approve the booking
        confirmed_at = datetime.utcnow().isoformat()
        result = (
            supabase_client.table("bookings")
            .update(
                {
                    "status": "confirmed",
                    "confirmed_at": confirmed_at,
                    "updated_at": confirmed_at,
                }
            )
            .eq("id", booking_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to auto-approve booking",
            )

        confirmed_booking = result.data[0]

        # Send confirmations
        from app.services.background_jobs import (
            send_booking_webhook,
            send_booking_confirmation_email,
        )

        # Send webhook
        webhook_data = {
            **confirmed_booking,
            "auto_approved": True,
            "property_info": property_info,
            "guest_info": {
                "name": booking["guest_name"],
                "email": booking["guest_email"],
                "phone": booking["guest_phone"],
            },
        }
        send_booking_webhook.delay("booking.confirmed", booking_id, webhook_data)

        # Send email confirmation
        send_booking_confirmation_email.delay(booking_id, confirmed_booking)

        # Send host notification
        from app.services.notification_service import NotificationService

        await NotificationService.create_booking_notification(
            host_id=host_id,
            booking_id=booking_id,
            property_id=booking["property_id"],
            notification_type="booking_confirmed",
            guest_name=booking["guest_name"],
            property_title=property_info["title"],
            booking_details=confirmed_booking,
        )

        logger.info(
            f"Booking auto-approved via external API",
            extra={
                "booking_id": booking_id,
                "host_id": host_id,
                "amount": booking["total_amount"],
                "amount_limit": amount_limit,
                "service_name": service_context.get("service_name", "unknown"),
            },
        )

        return ExternalAPIResponse(
            success=True,
            data={
                "booking_id": booking_id,
                "status": "confirmed",
                "auto_approved": True,
                "confirmed_at": confirmed_at,
                "amount": booking["total_amount"],
                "amount_limit": amount_limit,
                "host_id": host_id,
                "property_title": property_info["title"],
            },
            message="Booking auto-approved successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to auto-approve booking {booking_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to auto-approve booking: {str(e)}",
        )


@router.get(
    "/v1/external/bookings/{booking_id}/status", response_model=ExternalAPIResponse
)
@limiter.limit("200/minute")
async def get_booking_status(
    request: Request,
    booking_id: str,
    service_context: dict = Depends(get_external_service_context),
):
    """Get current booking status"""
    try:
        result = (
            supabase_client.table("bookings")
            .select(
                """
            id, status, created_at, updated_at, confirmed_at, total_amount, nights, guests,
            check_in, check_out, guest_name, guest_email,
            properties!inner(id, title, address, city, state, user_id)
        """
            )
            .eq("id", booking_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
            )

        booking = result.data[0]
        property_info = booking["properties"]

        return ExternalAPIResponse(
            success=True,
            data={
                "booking_id": booking_id,
                "status": booking["status"],
                "created_at": booking["created_at"],
                "updated_at": booking["updated_at"],
                "confirmed_at": booking.get("confirmed_at"),
                "total_amount": booking["total_amount"],
                "nights": booking["nights"],
                "guests": booking["guests"],
                "check_in": booking["check_in"],
                "check_out": booking["check_out"],
                "guest_name": booking["guest_name"],
                "guest_email": booking["guest_email"],
                "property": {
                    "id": property_info["id"],
                    "title": property_info["title"],
                    "address": f"{property_info['address']}, {property_info['city']}, {property_info['state']}",
                },
                "host_id": property_info["user_id"],
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get booking status for {booking_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get booking status: {str(e)}",
        )


# ============================================================================
# HOST PROFILE ENDPOINTS (Public Information Only - No Email/Phone)
# ============================================================================


@router.get("/v1/hosts/{host_id}/profile", response_model=ExternalAPIResponse)
@limiter.limit("200/minute")
async def get_host_public_profile(
    request: Request,
    host_id: str,
    service_context: dict = Depends(get_external_service_context),
):
    """
    Get public host profile information for AI agents.
    
    Returns host's public information including:
    - Name and avatar
    - Superhost status
    - Response rate and time
    - Properties count and ratings
    
    DOES NOT return: email, phone number, or other sensitive data
    """
    try:
        # Get host basic info
        host_result = (
            supabase_client.table("users")
            .select("id, name, avatar_url, created_at")
            .eq("id", host_id)
            .execute()
        )

        if not host_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Host not found",
            )

        host_data = host_result.data[0]

        # Get superhost status
        superhost_result = (
            supabase_client.table("superhost_verifications")
            .select("status, verified_at")
            .eq("user_id", host_id)
            .eq("status", "verified")
            .execute()
        )
        is_superhost = len(superhost_result.data) > 0 if superhost_result.data else False

        # Get host's active properties count
        properties_result = (
            supabase_client.table("properties")
            .select("id, title, city, state, price_per_night, images, rating, review_count")
            .eq("user_id", host_id)
            .eq("status", "active")
            .execute()
        )
        
        total_properties = len(properties_result.data) if properties_result.data else 0
        
        # Calculate aggregate ratings
        total_reviews = 0
        total_rating_sum = 0
        for prop in (properties_result.data or []):
            prop_reviews = prop.get("review_count", 0) or 0
            prop_rating = prop.get("rating", 0) or 0
            total_reviews += prop_reviews
            total_rating_sum += prop_rating * prop_reviews
        
        average_rating = round(total_rating_sum / total_reviews, 2) if total_reviews > 0 else 0.0

        # Get host profile/settings for additional info
        profile_result = (
            supabase_client.table("profiles")
            .select("bio, languages, response_rate, response_time")
            .eq("user_id", host_id)
            .execute()
        )
        
        profile_data = profile_result.data[0] if profile_result.data else {}

        # Build public profile (NO email or phone!)
        host_profile = HostPublicProfile(
            id=host_data["id"],
            name=host_data.get("name", "Host"),
            avatar_url=host_data.get("avatar_url"),
            is_superhost=is_superhost,
            response_rate=profile_data.get("response_rate", 95),
            response_time=profile_data.get("response_time", "within a few hours"),
            member_since=host_data.get("created_at", ""),
            total_properties=total_properties,
            total_reviews=total_reviews,
            average_rating=average_rating,
            languages=profile_data.get("languages", ["English", "Arabic"]),
            about=profile_data.get("bio"),
            verified=is_superhost,
        )

        # Build properties preview (limited info)
        properties_preview = []
        for prop in (properties_result.data or [])[:5]:  # Max 5 properties preview
            first_image = prop.get("images", [])[0] if prop.get("images") else None
            properties_preview.append({
                "id": prop["id"],
                "title": prop["title"],
                "location": f"{prop.get('city', '')}, {prop.get('state', '')}",
                "price_per_night": float(prop.get("price_per_night", 0)),
                "rating": float(prop.get("rating", 0) or 0),
                "review_count": prop.get("review_count", 0) or 0,
                "thumbnail": first_image,
            })

        return ExternalAPIResponse(
            success=True,
            data={
                "host": host_profile.dict(),
                "properties_preview": properties_preview,
            },
            message="Host profile retrieved successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get host profile for {host_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get host profile: {str(e)}",
        )


# ============================================================================
# MESSAGING ENDPOINTS FOR AI AGENTS
# ============================================================================


@router.post("/v1/messages", response_model=ExternalAPIResponse)
@limiter.limit("100/minute")
async def send_message_to_host(
    request: Request,
    message_request: ExternalMessageCreate,
    service_context: dict = Depends(get_external_service_context),
):
    """
    Send a message to a property host from AI agent on behalf of a guest.
    
    Creates or continues a conversation thread between guest and host.
    """
    try:
        # Verify property exists and get host info
        property_result = (
            supabase_client.table("properties")
            .select("id, title, user_id")
            .eq("id", message_request.property_id)
            .eq("status", "active")
            .execute()
        )

        if not property_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found",
            )

        property_data = property_result.data[0]
        host_id = property_data["user_id"]

        # Get host info for response
        host_result = (
            supabase_client.table("users")
            .select("id, name")
            .eq("id", host_id)
            .execute()
        )
        host_name = host_result.data[0]["name"] if host_result.data else "Host"

        # Check for existing conversation or create new one
        existing_conversation = (
            supabase_client.table("conversations")
            .select("id")
            .eq("property_id", message_request.property_id)
            .eq("guest_email", message_request.sender_email)
            .eq("status", "active")
            .execute()
        )

        if existing_conversation.data:
            conversation_id = existing_conversation.data[0]["id"]
        else:
            # Create new conversation
            conversation_id = str(uuid.uuid4())
            conversation_record = {
                "id": conversation_id,
                "property_id": message_request.property_id,
                "host_id": host_id,
                "guest_name": message_request.sender_name,
                "guest_email": message_request.sender_email,
                "booking_id": message_request.booking_id,
                "status": "active",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
            supabase_client.table("conversations").insert(conversation_record).execute()

        # Create message
        message_id = str(uuid.uuid4())
        message_record = {
            "id": message_id,
            "conversation_id": conversation_id,
            "sender_type": "guest",
            "sender_id": message_request.sender_email,  # Use email as guest ID
            "content": message_request.content,
            "is_read": False,
            "is_ai_generated": False,
            "created_at": datetime.utcnow().isoformat(),
        }
        supabase_client.table("messages").insert(message_record).execute()

        # Update conversation last message time
        supabase_client.table("conversations").update({
            "last_message_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "unread_count": supabase_client.table("conversations")
                .select("unread_count")
                .eq("id", conversation_id)
                .execute()
                .data[0].get("unread_count", 0) + 1 if True else 1,
        }).eq("id", conversation_id).execute()

        # Send notification to host
        try:
            from app.services.notification_service import NotificationService
            await NotificationService.create_message_notification(
                host_id=host_id,
                conversation_id=conversation_id,
                property_id=message_request.property_id,
                guest_name=message_request.sender_name,
                message_preview=message_request.content[:100],
            )
        except Exception as notif_error:
            logger.warning(f"Failed to send notification: {notif_error}")

        logger.info(
            f"Message sent via external API",
            extra={
                "conversation_id": conversation_id,
                "message_id": message_id,
                "property_id": message_request.property_id,
                "service_name": service_context.get("service_name"),
            }
        )

        return ExternalAPIResponse(
            success=True,
            data={
                "message_id": message_id,
                "conversation_id": conversation_id,
                "status": "sent",
                "sent_at": datetime.utcnow().isoformat(),
                "host_info": {
                    "name": host_name,
                    "response_time": "within a few hours",
                },
                "property": {
                    "id": property_data["id"],
                    "title": property_data["title"],
                },
            },
            message="Message sent to host successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}",
        )


@router.get("/v1/conversations/{conversation_id}", response_model=ExternalAPIResponse)
@limiter.limit("200/minute")
async def get_conversation_thread(
    request: Request,
    conversation_id: str,
    guest_email: str = Query(..., description="Guest email for verification"),
    limit: int = Query(50, ge=1, le=100, description="Max messages to return"),
    service_context: dict = Depends(get_external_service_context),
):
    """
    Get a conversation thread including all messages.
    
    Requires guest_email for verification to ensure only the
    conversation participant can read messages.
    """
    try:
        # Get conversation with property and host info
        conversation_result = (
            supabase_client.table("conversations")
            .select("""
                *,
                properties!inner(id, title, city, state, user_id,
                    users!inner(id, name, avatar_url, created_at)
                )
            """)
            .eq("id", conversation_id)
            .execute()
        )

        if not conversation_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        conversation = conversation_result.data[0]

        # Verify guest email matches
        if conversation["guest_email"] != guest_email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this conversation",
            )

        property_data = conversation["properties"]
        host_data = property_data["users"]

        # Get superhost status
        superhost_result = (
            supabase_client.table("superhost_verifications")
            .select("status")
            .eq("user_id", host_data["id"])
            .eq("status", "verified")
            .execute()
        )
        is_superhost = len(superhost_result.data) > 0 if superhost_result.data else False

        # Get messages
        messages_result = (
            supabase_client.table("messages")
            .select("*")
            .eq("conversation_id", conversation_id)
            .order("created_at", desc=False)
            .limit(limit)
            .execute()
        )

        # Build host profile (public info only)
        host_profile = HostPublicProfile(
            id=host_data["id"],
            name=host_data.get("name", "Host"),
            avatar_url=host_data.get("avatar_url"),
            is_superhost=is_superhost,
            member_since=host_data.get("created_at"),
            total_properties=1,
            total_reviews=0,
            average_rating=0.0,
            languages=["English", "Arabic"],
            verified=is_superhost,
        )

        # Format messages
        messages = []
        for msg in (messages_result.data or []):
            sender_name = conversation["guest_name"] if msg["sender_type"] == "guest" else host_data["name"]
            messages.append(ConversationMessage(
                id=msg["id"],
                sender_type=msg["sender_type"],
                sender_name=sender_name,
                content=msg["content"],
                sent_at=msg["created_at"],
                is_read=msg.get("is_read", False),
                is_ai_generated=msg.get("is_ai_generated", False),
            ).dict())

        # Count unread messages for guest
        unread_count = sum(1 for msg in (messages_result.data or []) 
                         if msg["sender_type"] == "host" and not msg.get("is_read", False))

        return ExternalAPIResponse(
            success=True,
            data={
                "conversation_id": conversation_id,
                "property_id": property_data["id"],
                "property_title": property_data["title"],
                "property_location": f"{property_data.get('city', '')}, {property_data.get('state', '')}",
                "booking_id": conversation.get("booking_id"),
                "host": host_profile.dict(),
                "guest_name": conversation["guest_name"],
                "guest_email": conversation["guest_email"],
                "status": conversation["status"],
                "messages": messages,
                "unread_count": unread_count,
                "last_message_at": conversation.get("last_message_at"),
                "created_at": conversation["created_at"],
            },
            message="Conversation retrieved successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation: {str(e)}",
        )


@router.get("/v1/messages/by-booking/{booking_id}", response_model=ExternalAPIResponse)
@limiter.limit("200/minute")
async def get_messages_by_booking(
    request: Request,
    booking_id: str,
    guest_email: str = Query(..., description="Guest email for verification"),
    service_context: dict = Depends(get_external_service_context),
):
    """
    Get all messages related to a specific booking.
    """
    try:
        # Get booking to verify guest
        booking_result = (
            supabase_client.table("bookings")
            .select("id, guest_email, property_id")
            .eq("id", booking_id)
            .execute()
        )

        if not booking_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )

        booking = booking_result.data[0]

        # Verify guest email
        if booking["guest_email"] != guest_email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        # Get conversation for this booking
        conversation_result = (
            supabase_client.table("conversations")
            .select("id")
            .eq("booking_id", booking_id)
            .execute()
        )

        if not conversation_result.data:
            return ExternalAPIResponse(
                success=True,
                data={
                    "booking_id": booking_id,
                    "conversation_id": None,
                    "messages": [],
                    "message_count": 0,
                },
                message="No messages found for this booking",
            )

        conversation_id = conversation_result.data[0]["id"]

        # Get messages
        messages_result = (
            supabase_client.table("messages")
            .select("*")
            .eq("conversation_id", conversation_id)
            .order("created_at", desc=False)
            .execute()
        )

        messages = []
        for msg in (messages_result.data or []):
            messages.append({
                "id": msg["id"],
                "sender_type": msg["sender_type"],
                "content": msg["content"],
                "sent_at": msg["created_at"],
                "is_read": msg.get("is_read", False),
            })

        return ExternalAPIResponse(
            success=True,
            data={
                "booking_id": booking_id,
                "conversation_id": conversation_id,
                "messages": messages,
                "message_count": len(messages),
            },
            message="Messages retrieved successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get messages for booking {booking_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get messages: {str(e)}",
        )


@router.post("/v1/conversations/{conversation_id}/reply", response_model=ExternalAPIResponse)
@limiter.limit("100/minute")
async def reply_to_conversation(
    request: Request,
    conversation_id: str,
    guest_email: str = Query(..., description="Guest email for verification"),
    content: str = Query(..., min_length=1, max_length=2000, description="Reply message"),
    service_context: dict = Depends(get_external_service_context),
):
    """
    Send a reply message in an existing conversation.
    """
    try:
        # Verify conversation and guest access
        conversation_result = (
            supabase_client.table("conversations")
            .select("*, properties!inner(id, title, user_id)")
            .eq("id", conversation_id)
            .execute()
        )

        if not conversation_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        conversation = conversation_result.data[0]

        if conversation["guest_email"] != guest_email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this conversation",
            )

        # Create message
        message_id = str(uuid.uuid4())
        message_record = {
            "id": message_id,
            "conversation_id": conversation_id,
            "sender_type": "guest",
            "sender_id": guest_email,
            "content": content,
            "is_read": False,
            "is_ai_generated": False,
            "created_at": datetime.utcnow().isoformat(),
        }
        supabase_client.table("messages").insert(message_record).execute()

        # Update conversation
        supabase_client.table("conversations").update({
            "last_message_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("id", conversation_id).execute()

        # Notify host
        try:
            from app.services.notification_service import NotificationService
            await NotificationService.create_message_notification(
                host_id=conversation["properties"]["user_id"],
                conversation_id=conversation_id,
                property_id=conversation["property_id"],
                guest_name=conversation["guest_name"],
                message_preview=content[:100],
            )
        except Exception as notif_error:
            logger.warning(f"Failed to send notification: {notif_error}")

        return ExternalAPIResponse(
            success=True,
            data={
                "message_id": message_id,
                "conversation_id": conversation_id,
                "status": "sent",
                "sent_at": datetime.utcnow().isoformat(),
            },
            message="Reply sent successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send reply: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send reply: {str(e)}",
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
            "version": "2.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "endpoints": {
                "properties": [
                    "GET /api/v1/properties/search - Search properties with filters",
                    "GET /api/v1/properties/{id} - Get property details",
                    "GET /api/v1/properties/{id}/availability - Check availability",
                    "POST /api/v1/properties/{id}/calculate-pricing - Calculate pricing",
                ],
                "bookings": [
                    "POST /api/v1/bookings - Create a booking",
                    "GET /api/v1/external/bookings/{id}/status - Get booking status",
                    "PUT /api/v1/external/bookings/{id}/status - Update booking status",
                    "POST /api/v1/external/bookings/{id}/auto-approve - Auto-approve booking",
                ],
                "hosts": [
                    "GET /api/v1/hosts/{id}/profile - Get host public profile (no email/phone)",
                    "GET /api/v1/external/hosts/{id}/pending-bookings - Get pending bookings",
                ],
                "messaging": [
                    "POST /api/v1/messages - Send message to host",
                    "GET /api/v1/conversations/{id} - Get conversation thread",
                    "GET /api/v1/messages/by-booking/{id} - Get messages by booking",
                    "POST /api/v1/conversations/{id}/reply - Reply to conversation",
                ],
                "payments": [
                    "POST /api/external/v1/bookings/{id}/process-payment - Process payment",
                    "GET /api/external/v1/bookings/{id}/payment-status - Get payment status",
                ],
            },
        },
        message="External API is operational",
    )
