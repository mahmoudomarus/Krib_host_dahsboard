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
    # Text search
    q: Optional[str] = Query(
        None, description="Text search across title, description, city"
    ),
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
        # Use LEFT JOIN (users!left) so properties show even without user record
        query = (
            supabase_client.table("properties")
            .select(
                """
            *,
            users!left(id, name, email, created_at)
        """
            )
            .eq("status", "active")
        )

        # Apply text search across title, description, city
        if q:
            # Use OR filter for text search across multiple fields
            query = query.or_(
                f"title.ilike.%{q}%,description.ilike.%{q}%,city.ilike.%{q}%,address.ilike.%{q}%"
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
        if q:
            count_result = count_result.or_(
                f"title.ilike.%{q}%,description.ilike.%{q}%,city.ilike.%{q}%,address.ilike.%{q}%"
            )
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

    Validates availability against existing bookings, property capacity,
    minimum/maximum nights, and date restrictions.
    """
    try:
        # Verify property exists
        property_data = await verify_property_access_external(
            property_id, service_context
        )

        today = date.today()
        nights = (check_out - check_in).days
        reasons = []

        # Validate dates - check_out must be after check_in
        if check_out <= check_in:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Check-out date must be after check-in date",
            )

        # Smart date validation - cannot book past dates
        if check_in < today:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Check-in date cannot be in the past. Today is {today.isoformat()}",
            )

        # Check minimum nights (default to 1 if not set)
        min_nights = property_data.get("minimum_nights", 1) or 1
        if nights < min_nights:
            reasons.append(
                f"Minimum stay is {min_nights} nights, you requested {nights}"
            )

        # Check maximum nights (default to 365 if not set)
        max_nights = property_data.get("maximum_nights", 365) or 365
        if nights > max_nights:
            reasons.append(
                f"Maximum stay is {max_nights} nights, you requested {nights}"
            )

        # Check property availability window
        available_from = property_data.get("available_from")
        available_to = property_data.get("available_to")

        if available_from:
            avail_from_date = (
                date.fromisoformat(available_from)
                if isinstance(available_from, str)
                else available_from
            )
            if check_in < avail_from_date:
                reasons.append(
                    f"Property is available from {avail_from_date.isoformat()}"
                )

        if available_to:
            avail_to_date = (
                date.fromisoformat(available_to)
                if isinstance(available_to, str)
                else available_to
            )
            if check_out > avail_to_date:
                reasons.append(
                    f"Property is available until {avail_to_date.isoformat()}"
                )

        # Check guest capacity
        capacity_ok = guests <= property_data["max_guests"]
        if not capacity_ok:
            reasons.append(
                f"Property max guests is {property_data['max_guests']}, you requested {guests}"
            )

        # Check for existing bookings (conflicting reservations)
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
        if has_conflicts:
            reasons.append("Property is already booked for these dates")

        # Property is available only if all checks pass
        is_available = capacity_ok and not has_conflicts and len(reasons) == 0

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
    Smart date validation ensures bookings are valid and within property settings.
    """
    try:
        # Verify property exists and is available
        property_data = await verify_property_access_external(
            booking_request.property_id, service_context
        )

        today = date.today()
        nights = (booking_request.check_out - booking_request.check_in).days

        # Smart date validation - cannot book past dates
        if booking_request.check_in < today:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Check-in date cannot be in the past. Today is {today.isoformat()}",
            )

        # Validate check-out is after check-in
        if booking_request.check_out <= booking_request.check_in:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Check-out date must be after check-in date",
            )

        # Check minimum nights (default to 1 if not set)
        min_nights = property_data.get("minimum_nights", 1) or 1
        if nights < min_nights:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Minimum stay is {min_nights} nights, you requested {nights} nights",
            )

        # Check maximum nights (default to 365 if not set)
        max_nights = property_data.get("maximum_nights", 365) or 365
        if nights > max_nights:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum stay is {max_nights} nights, you requested {nights} nights",
            )

        # Check property availability window
        available_from = property_data.get("available_from")
        available_to = property_data.get("available_to")

        if available_from:
            avail_from_date = (
                date.fromisoformat(available_from)
                if isinstance(available_from, str)
                else available_from
            )
            if booking_request.check_in < avail_from_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Property is available from {avail_from_date.isoformat()}",
                )

        if available_to:
            avail_to_date = (
                date.fromisoformat(available_to)
                if isinstance(available_to, str)
                else available_to
            )
            if booking_request.check_out > avail_to_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Property is available until {avail_to_date.isoformat()}",
                )

        # Validate guest capacity
        if booking_request.guests > property_data["max_guests"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Property can accommodate maximum {property_data['max_guests']} guests",
            )

        # Check for date conflicts with existing bookings
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
                detail="Property is already booked for these dates",
            )

        # Create booking record (nights already calculated above)
        # Note: 'nights' is a generated column in the database (computed from check_out - check_in)
        # so we don't include it in the insert
        booking_id = str(uuid.uuid4())
        booking_record = {
            "id": booking_id,
            "property_id": booking_request.property_id,
            "guest_name": f"{booking_request.guest_info.first_name} {booking_request.guest_info.last_name}",
            "guest_email": booking_request.guest_info.email,
            "guest_phone": f"{booking_request.guest_info.country_code}{booking_request.guest_info.phone}",
            "check_in": booking_request.check_in.isoformat(),
            "check_out": booking_request.check_out.isoformat(),
            # nights is generated automatically by the database
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

        # Send webhooks (non-blocking - booking succeeds even if webhooks fail)
        try:
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
        except Exception as webhook_error:
            # Log but don't fail booking - webhooks are non-critical
            logger.warning(f"Webhook failed for booking {booking_id}: {webhook_error}")

        # Send host notification (non-blocking)
        try:
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
        except Exception as notification_error:
            logger.warning(
                f"Notification failed for booking {booking_id}: {notification_error}"
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
            "endpoints": [
                # Property endpoints
                "GET /external/v1/properties/search",
                "GET /external/v1/properties/{id}",
                "GET /external/v1/properties/{id}/availability",
                "POST /external/v1/properties/{id}/calculate-pricing",
                "GET /external/v1/properties/{id}/reviews",
                # Booking endpoints
                "POST /external/v1/bookings",
                "GET /external/v1/bookings/{booking_id}/status",
                "PUT /external/v1/bookings/{booking_id}/status",
                "POST /external/v1/bookings/{booking_id}/auto-approve",
                # Host endpoints
                "GET /external/v1/hosts/{host_id}/profile",
                "GET /external/v1/hosts/{host_id}/pending-bookings",
                # Messaging endpoints
                "POST /external/v1/messages",
                "GET /external/v1/conversations/{conversation_id}",
                "POST /external/v1/conversations/{conversation_id}/messages",
            ],
        },
        message="External API is operational",
    )


# =============================================================================
# HOST PROFILE ENDPOINTS
# =============================================================================


@router.get("/v1/hosts/{host_id}/profile", response_model=ExternalAPIResponse)
@limiter.limit("200/minute")
async def get_host_public_profile(
    request: Request,
    host_id: str,
    service_context: dict = Depends(get_external_service_context),
):
    """
    Get public host profile information

    Returns host's public information including:
    - Name and avatar
    - Superhost status
    - Response rate and time
    - Number of listings
    - Average rating

    **Does NOT return**: email, phone, or other private information
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
                status_code=status.HTTP_404_NOT_FOUND, detail="Host not found"
            )

        host = host_result.data[0]

        # Get host's properties count
        properties_result = (
            supabase_client.table("properties")
            .select("id", count="exact")
            .eq("user_id", host_id)
            .eq("status", "active")
            .execute()
        )
        properties_count = properties_result.count or 0

        # Get superhost status
        superhost_result = (
            supabase_client.table("superhost_verifications")
            .select("status, verified_at")
            .eq("user_id", host_id)
            .eq("status", "approved")
            .execute()
        )
        is_superhost = (
            len(superhost_result.data) > 0 if superhost_result.data else False
        )

        # Get average rating from all host's property reviews
        reviews_result = (
            supabase_client.table("reviews")
            .select("rating, properties!inner(user_id)")
            .eq("properties.user_id", host_id)
            .execute()
        )

        total_reviews = len(reviews_result.data) if reviews_result.data else 0
        average_rating = 0.0
        if total_reviews > 0:
            ratings = [r["rating"] for r in reviews_result.data if r.get("rating")]
            average_rating = round(sum(ratings) / len(ratings), 1) if ratings else 0.0

        # Build public profile
        host_profile = {
            "id": host["id"],
            "name": host.get("name", "Host"),
            "avatar_url": host.get("avatar_url"),
            "is_superhost": is_superhost,
            "response_rate": 95,  # Default, could be calculated from messages
            "response_time": "within an hour",
            "member_since": (
                host.get("created_at", "")[:10] if host.get("created_at") else ""
            ),
            "total_listings": properties_count,
            "total_reviews": total_reviews,
            "average_rating": average_rating,
            "languages": ["English", "Arabic"],  # Could be stored in user profile
            "about": None,  # Could be added to user profile later
            "verified": True,  # All hosts are verified via Supabase auth
        }

        return ExternalAPIResponse(
            success=True,
            data={
                "host": host_profile,
                "properties_count": properties_count,
                "can_message": True,
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


# =============================================================================
# MESSAGING ENDPOINTS (AI Agent <-> Host Communication)
# =============================================================================


@router.post("/v1/messages", response_model=ExternalAPIResponse)
@limiter.limit("50/minute")
async def send_message_to_host(
    request: Request,
    message_data: Dict[str, Any],
    service_context: dict = Depends(get_external_service_context),
):
    """
    Send a message to a host about a property

    Creates a conversation if one doesn't exist, then sends the message.
    This is the primary way for AI agents to initiate communication with hosts.

    Required fields in message_data:
    - property_id: Property the inquiry is about
    - guest_name: Name of the guest/user
    - guest_email: Email for notifications
    - message: The message content

    Optional fields:
    - booking_id: Related booking if applicable
    - inquiry_type: general, availability, pricing, amenities, booking_question
    """
    try:
        property_id = message_data.get("property_id")
        guest_name = message_data.get("guest_name")
        guest_email = message_data.get("guest_email")
        message_content = message_data.get("message")
        booking_id = message_data.get("booking_id")
        inquiry_type = message_data.get("inquiry_type", "general")

        # Validate required fields
        if not all([property_id, guest_name, guest_email, message_content]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required fields: property_id, guest_name, guest_email, message",
            )

        # Get property and host info
        property_result = (
            supabase_client.table("properties")
            .select("id, title, user_id, users!inner(id, name)")
            .eq("id", property_id)
            .eq("status", "active")
            .execute()
        )

        if not property_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found or not available",
            )

        property_data = property_result.data[0]
        host_id = property_data["user_id"]
        host_name = (
            property_data["users"]["name"] if property_data.get("users") else "Host"
        )

        # Check for existing conversation
        existing_conversation = (
            supabase_client.table("conversations")
            .select("id")
            .eq("property_id", property_id)
            .eq("guest_email", guest_email)
            .eq("status", "active")
            .execute()
        )

        conversation_id = None
        if existing_conversation.data:
            conversation_id = existing_conversation.data[0]["id"]
        else:
            # Create new conversation
            conversation_result = (
                supabase_client.table("conversations")
                .insert(
                    {
                        "property_id": property_id,
                        "host_id": host_id,
                        "guest_name": guest_name,
                        "guest_email": guest_email,
                        "booking_id": booking_id,
                        "status": "active",
                        "inquiry_type": inquiry_type,
                    }
                )
                .execute()
            )

            if not conversation_result.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create conversation",
                )

            conversation_id = conversation_result.data[0]["id"]

        # Send the message
        message_result = (
            supabase_client.table("messages")
            .insert(
                {
                    "conversation_id": conversation_id,
                    "sender_id": guest_email,  # Use email as guest identifier
                    "sender_type": "guest",
                    "content": message_content,
                    "is_read": False,
                    "is_ai_generated": False,
                }
            )
            .execute()
        )

        if not message_result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send message",
            )

        message_record = message_result.data[0]

        # Update conversation last_message_at
        supabase_client.table("conversations").update(
            {
                "last_message_at": datetime.utcnow().isoformat(),
                "unread_host": True,
            }
        ).eq("id", conversation_id).execute()

        # Create notification for host
        try:
            from app.services.notification_service import NotificationService

            await NotificationService.create_notification(
                user_id=host_id,
                notification_type="new_message",
                title=f"New message from {guest_name}",
                message=f"Inquiry about {property_data['title']}: {message_content[:100]}...",
                data={
                    "conversation_id": conversation_id,
                    "property_id": property_id,
                    "guest_name": guest_name,
                },
            )
        except Exception as notify_error:
            logger.warning(f"Failed to create notification: {notify_error}")

        logger.info(
            f"External message sent: conversation={conversation_id}, from={guest_name}"
        )

        return ExternalAPIResponse(
            success=True,
            data={
                "conversation_id": conversation_id,
                "message_id": message_record["id"],
                "status": "sent",
                "host_id": host_id,
                "host_name": host_name,
                "property_title": property_data["title"],
                "estimated_response_time": "within an hour",
                "created_at": message_record["created_at"],
            },
            message="Message sent successfully",
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
@limiter.limit("100/minute")
async def get_conversation(
    request: Request,
    conversation_id: str,
    limit: int = Query(50, ge=1, le=100, description="Number of messages to return"),
    service_context: dict = Depends(get_external_service_context),
):
    """
    Get conversation details and messages

    Returns the full conversation including:
    - Conversation metadata
    - Host public profile
    - All messages in chronological order
    """
    try:
        # Get conversation
        conversation_result = (
            supabase_client.table("conversations")
            .select(
                """
                *,
                properties!inner(id, title, user_id),
                users!conversations_host_id_fkey(id, name, avatar_url, created_at)
            """
            )
            .eq("id", conversation_id)
            .execute()
        )

        if not conversation_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )

        conversation = conversation_result.data[0]
        property_data = conversation.get("properties", {})
        host_data = conversation.get("users", {})

        # Get messages
        messages_result = (
            supabase_client.table("messages")
            .select("*")
            .eq("conversation_id", conversation_id)
            .order("created_at", desc=False)
            .limit(limit)
            .execute()
        )

        messages = []
        for msg in messages_result.data or []:
            messages.append(
                {
                    "id": msg["id"],
                    "sender_type": msg["sender_type"],
                    "sender_name": (
                        conversation["guest_name"]
                        if msg["sender_type"] == "guest"
                        else host_data.get("name", "Host")
                    ),
                    "content": msg["content"],
                    "is_read": msg.get("is_read", False),
                    "is_ai_generated": msg.get("is_ai_generated", False),
                    "created_at": msg["created_at"],
                }
            )

        # Count unread messages
        unread_count = sum(
            1 for m in messages if not m["is_read"] and m["sender_type"] == "host"
        )

        # Build host public profile
        host_profile = {
            "id": host_data.get("id", ""),
            "name": host_data.get("name", "Host"),
            "avatar_url": host_data.get("avatar_url"),
            "is_superhost": False,  # Could check superhost table
            "response_rate": 95,
            "response_time": "within an hour",
            "member_since": (
                host_data.get("created_at", "")[:10]
                if host_data.get("created_at")
                else ""
            ),
            "total_listings": 0,
            "total_reviews": 0,
            "average_rating": 0.0,
            "languages": ["English", "Arabic"],
            "about": None,
            "verified": True,
        }

        return ExternalAPIResponse(
            success=True,
            data={
                "conversation_id": conversation_id,
                "property_id": property_data.get("id", ""),
                "property_title": property_data.get("title", ""),
                "host": host_profile,
                "guest_name": conversation["guest_name"],
                "guest_email": conversation["guest_email"],
                "status": conversation["status"],
                "messages": messages,
                "unread_count": unread_count,
                "created_at": conversation["created_at"],
                "last_message_at": conversation.get("last_message_at"),
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


@router.post(
    "/v1/conversations/{conversation_id}/messages", response_model=ExternalAPIResponse
)
@limiter.limit("50/minute")
async def send_follow_up_message(
    request: Request,
    conversation_id: str,
    message_data: Dict[str, Any],
    service_context: dict = Depends(get_external_service_context),
):
    """
    Send a follow-up message in an existing conversation

    Required fields in message_data:
    - message: The message content
    - guest_email: Must match the conversation's guest email for verification
    """
    try:
        message_content = message_data.get("message")
        guest_email = message_data.get("guest_email")

        if not message_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message content is required",
            )

        # Get conversation and verify guest
        conversation_result = (
            supabase_client.table("conversations")
            .select("*, properties!inner(id, title)")
            .eq("id", conversation_id)
            .execute()
        )

        if not conversation_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )

        conversation = conversation_result.data[0]

        # Verify guest email matches
        if guest_email and conversation["guest_email"] != guest_email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Guest email does not match conversation",
            )

        # Check conversation is active
        if conversation["status"] != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Conversation is not active",
            )

        # Send message
        message_result = (
            supabase_client.table("messages")
            .insert(
                {
                    "conversation_id": conversation_id,
                    "sender_id": conversation["guest_email"],
                    "sender_type": "guest",
                    "content": message_content,
                    "is_read": False,
                    "is_ai_generated": False,
                }
            )
            .execute()
        )

        if not message_result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send message",
            )

        message_record = message_result.data[0]

        # Update conversation
        supabase_client.table("conversations").update(
            {
                "last_message_at": datetime.utcnow().isoformat(),
                "unread_host": True,
            }
        ).eq("id", conversation_id).execute()

        # Notify host
        try:
            from app.services.notification_service import NotificationService

            await NotificationService.create_notification(
                user_id=conversation["host_id"],
                notification_type="new_message",
                title=f"New message from {conversation['guest_name']}",
                message=f"{message_content[:100]}...",
                data={
                    "conversation_id": conversation_id,
                    "property_id": conversation["property_id"],
                },
            )
        except Exception as notify_error:
            logger.warning(f"Failed to create notification: {notify_error}")

        return ExternalAPIResponse(
            success=True,
            data={
                "message_id": message_record["id"],
                "conversation_id": conversation_id,
                "status": "sent",
                "created_at": message_record["created_at"],
            },
            message="Message sent successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send follow-up message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}",
        )


# =============================================================================
# PROPERTY REVIEWS ENDPOINTS
# =============================================================================


@router.get("/v1/properties/{property_id}/reviews", response_model=ExternalAPIResponse)
@limiter.limit("100/minute")
async def get_property_reviews(
    request: Request,
    property_id: str,
    limit: int = Query(20, ge=1, le=50, description="Number of reviews to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    sort_by: str = Query("recent", description="Sort: recent, highest, lowest"),
    service_context: dict = Depends(get_external_service_context),
):
    """
    Get reviews for a property

    Returns:
    - Review summary with average ratings
    - Rating distribution
    - Individual reviews with guest names (first name only for privacy)
    - Host responses to reviews
    """
    try:
        # Verify property exists
        property_result = (
            supabase_client.table("properties")
            .select("id, title, user_id")
            .eq("id", property_id)
            .eq("status", "active")
            .execute()
        )

        if not property_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Property not found"
            )

        # Get total count
        count_result = (
            supabase_client.table("reviews")
            .select("id", count="exact")
            .eq("property_id", property_id)
            .execute()
        )
        total_reviews = count_result.count or 0

        # Get reviews with sorting
        query = (
            supabase_client.table("reviews").select("*").eq("property_id", property_id)
        )

        if sort_by == "highest":
            query = query.order("rating", desc=True)
        elif sort_by == "lowest":
            query = query.order("rating", desc=False)
        else:  # recent
            query = query.order("created_at", desc=True)

        query = query.range(offset, offset + limit - 1)
        reviews_result = query.execute()

        reviews = []
        rating_sum = 0
        rating_distribution = {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}

        # Rating breakdown sums
        cleanliness_sum = 0
        communication_sum = 0
        location_sum = 0
        value_sum = 0
        accuracy_sum = 0
        check_in_sum = 0
        breakdown_count = 0

        for review in reviews_result.data or []:
            rating = review.get("rating", 0)
            rating_sum += rating
            rating_distribution[str(int(rating))] = (
                rating_distribution.get(str(int(rating)), 0) + 1
            )

            # Sum breakdown ratings if present
            if review.get("cleanliness_rating"):
                cleanliness_sum += review["cleanliness_rating"]
                communication_sum += review.get("communication_rating", 0)
                location_sum += review.get("location_rating", 0)
                value_sum += review.get("value_rating", 0)
                accuracy_sum += review.get("accuracy_rating", 0)
                check_in_sum += review.get("check_in_rating", 0)
                breakdown_count += 1

            # Get guest name (first name only for privacy)
            guest_name = review.get("guest_name", "Guest")
            if " " in guest_name:
                guest_name = guest_name.split(" ")[0]

            # Format stay date
            stay_date = ""
            if review.get("check_in"):
                try:
                    check_in_date = datetime.fromisoformat(
                        review["check_in"].replace("Z", "+00:00")
                    )
                    stay_date = check_in_date.strftime("%B %Y")
                except Exception:
                    stay_date = review.get("check_in", "")[:7]

            reviews.append(
                {
                    "id": review["id"],
                    "guest_name": guest_name,
                    "guest_avatar": None,  # Could be added if we store guest avatars
                    "rating": rating,
                    "comment": review.get("comment", ""),
                    "stay_date": stay_date,
                    "cleanliness_rating": review.get("cleanliness_rating"),
                    "communication_rating": review.get("communication_rating"),
                    "location_rating": review.get("location_rating"),
                    "value_rating": review.get("value_rating"),
                    "accuracy_rating": review.get("accuracy_rating"),
                    "check_in_rating": review.get("check_in_rating"),
                    "host_response": review.get("host_response"),
                    "host_response_date": review.get("host_response_date"),
                    "created_at": review.get("created_at", ""),
                }
            )

        # Calculate averages
        average_rating = round(rating_sum / len(reviews), 1) if reviews else 0.0

        # Calculate breakdown averages
        cleanliness_avg = (
            round(cleanliness_sum / breakdown_count, 1)
            if breakdown_count > 0
            else average_rating
        )
        communication_avg = (
            round(communication_sum / breakdown_count, 1)
            if breakdown_count > 0
            else average_rating
        )
        location_avg = (
            round(location_sum / breakdown_count, 1)
            if breakdown_count > 0
            else average_rating
        )
        value_avg = (
            round(value_sum / breakdown_count, 1)
            if breakdown_count > 0
            else average_rating
        )
        accuracy_avg = (
            round(accuracy_sum / breakdown_count, 1)
            if breakdown_count > 0
            else average_rating
        )
        check_in_avg = (
            round(check_in_sum / breakdown_count, 1)
            if breakdown_count > 0
            else average_rating
        )

        return ExternalAPIResponse(
            success=True,
            data={
                "property_id": property_id,
                "total_reviews": total_reviews,
                "average_rating": average_rating,
                "rating_breakdown": {
                    "cleanliness": cleanliness_avg,
                    "communication": communication_avg,
                    "location": location_avg,
                    "value": value_avg,
                    "accuracy": accuracy_avg,
                    "check_in": check_in_avg,
                },
                "rating_distribution": rating_distribution,
                "reviews": reviews,
                "has_more": (offset + limit) < total_reviews,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "total": total_reviews,
                },
            },
            message="Reviews retrieved successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get reviews for property {property_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get reviews: {str(e)}",
        )
