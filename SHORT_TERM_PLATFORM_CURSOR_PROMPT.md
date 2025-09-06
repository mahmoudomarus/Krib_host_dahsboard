# 🏠 Cursor Agent Prompt: Short-Term Rental Platform API Integration

## 🎯 **OBJECTIVE**
Build API endpoints for Kribz AI integration to enable property search, details, pricing, and booking functionality for short-term rentals (vacation/Airbnb-style properties).

## 📋 **CURRENT PLATFORM INFO**
- **URL**: https://krib-host-dahsboard-backend.onrender.com
- **Status**: RentalAI API v1.0.0 ✅ Running
- **Type**: Short-term vacation rental management platform
- **Target**: Integration with Kribz AI agents for property discovery and booking

---

## 🚀 **IMPLEMENTATION TASKS**

### **Task 1: Create Property Search Endpoint**

Create a new API endpoint for property search:

```python
# File: /api/v1/properties/search.py (or similar structure)

from fastapi import APIRouter, Query, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import date

router = APIRouter()

class PropertySearchFilters(BaseModel):
    # Location filters
    city: Optional[str] = None
    area: Optional[str] = None  # Dubai Marina, Downtown, etc.
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: Optional[float] = None
    
    # Property filters
    min_price_per_night: Optional[float] = None
    max_price_per_night: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    max_guests: Optional[int] = None
    property_type: Optional[str] = None  # apartment, villa, studio, townhouse
    
    # Availability filters
    check_in: Optional[date] = None
    check_out: Optional[date] = None
    
    # Feature filters
    instant_book: Optional[bool] = None
    pet_friendly: Optional[bool] = None
    amenities: Optional[List[str]] = []
    
    # Pagination
    limit: Optional[int] = 20
    offset: Optional[int] = 0
    sort_by: Optional[str] = "price_asc"  # price_asc, price_desc, rating, distance

class PropertySearchResult(BaseModel):
    id: str
    title: str
    description: str
    base_price_per_night: float
    bedrooms: int
    bathrooms: float
    max_guests: int
    property_type: str
    
    # Address
    address: dict = {
        "street": "string",
        "area": "string",  # Dubai Marina, Downtown
        "city": "Dubai", 
        "emirate": "Dubai",
        "country": "UAE",
        "coordinates": {"latitude": 0.0, "longitude": 0.0}
    }
    
    # Features
    instant_book: bool
    pet_friendly: bool = False
    amenities: List[str] = []
    
    # Images
    images: List[dict] = [
        {"url": "string", "is_primary": True, "order": 1}
    ]
    
    # Pricing
    cleaning_fee: Optional[float] = None
    security_deposit: Optional[float] = None
    minimum_nights: int = 1
    
    # Host info
    host: dict = {
        "id": "string",
        "name": "string", 
        "response_rate": 0.0,
        "is_superhost": False
    }
    
    # Ratings
    rating: float = 0.0
    review_count: int = 0

class PropertySearchResponse(BaseModel):
    success: bool = True
    data: dict = {
        "properties": List[PropertySearchResult],
        "total": int,
        "page": int,
        "limit": int
    }
    error: Optional[dict] = None

@router.get("/api/v1/properties/search", response_model=PropertySearchResponse)
async def search_properties(
    # Location filters
    city: Optional[str] = Query(None, description="City name (e.g., Dubai, Abu Dhabi)"),
    area: Optional[str] = Query(None, description="Area name (e.g., Dubai Marina, Downtown)"),
    latitude: Optional[float] = Query(None, description="Latitude coordinate"),
    longitude: Optional[float] = Query(None, description="Longitude coordinate"),
    radius_km: Optional[float] = Query(None, description="Search radius in kilometers"),
    
    # Property filters
    min_price_per_night: Optional[float] = Query(None, description="Minimum price per night in AED"),
    max_price_per_night: Optional[float] = Query(None, description="Maximum price per night in AED"),
    bedrooms: Optional[int] = Query(None, description="Number of bedrooms"),
    bathrooms: Optional[int] = Query(None, description="Number of bathrooms"),
    max_guests: Optional[int] = Query(None, description="Maximum guests"),
    property_type: Optional[str] = Query(None, description="apartment, villa, studio, townhouse"),
    
    # Availability filters
    check_in: Optional[date] = Query(None, description="Check-in date (YYYY-MM-DD)"),
    check_out: Optional[date] = Query(None, description="Check-out date (YYYY-MM-DD)"),
    
    # Feature filters
    instant_book: Optional[bool] = Query(None, description="Instant booking available"),
    pet_friendly: Optional[bool] = Query(None, description="Pet-friendly properties"),
    amenities: Optional[str] = Query(None, description="Comma-separated amenities (wifi,pool,gym)"),
    
    # Pagination
    page: Optional[int] = Query(1, description="Page number"),
    limit: Optional[int] = Query(20, description="Results per page"),
    sort_by: Optional[str] = Query("price_asc", description="Sort order")
):
    """
    Search properties based on filters
    
    Returns a list of properties matching the search criteria.
    Supports location-based search, price filtering, amenity filtering,
    and availability checking.
    """
    try:
        # Build query based on your database structure
        query = your_database.query(Property)
        
        # Apply filters
        if city:
            query = query.filter(Property.city.ilike(f"%{city}%"))
        if area:
            query = query.filter(Property.area.ilike(f"%{area}%"))
        if min_price_per_night:
            query = query.filter(Property.base_price_per_night >= min_price_per_night)
        if max_price_per_night:
            query = query.filter(Property.base_price_per_night <= max_price_per_night)
        if bedrooms:
            query = query.filter(Property.bedrooms >= bedrooms)
        if property_type:
            query = query.filter(Property.property_type == property_type)
        if instant_book is not None:
            query = query.filter(Property.instant_book == instant_book)
        
        # Handle amenities filter
        if amenities:
            amenity_list = amenities.split(",")
            for amenity in amenity_list:
                query = query.filter(Property.amenities.contains([amenity.strip()]))
        
        # Apply availability filter if dates provided
        if check_in and check_out:
            # Check against your availability/booking tables
            unavailable_property_ids = get_unavailable_properties(check_in, check_out)
            if unavailable_property_ids:
                query = query.filter(~Property.id.in_(unavailable_property_ids))
        
        # Apply sorting
        if sort_by == "price_asc":
            query = query.order_by(Property.base_price_per_night.asc())
        elif sort_by == "price_desc":
            query = query.order_by(Property.base_price_per_night.desc())
        elif sort_by == "rating":
            query = query.order_by(Property.rating.desc())
        
        # Get total count for pagination
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        properties = query.offset(offset).limit(limit).all()
        
        # Format response
        property_results = []
        for prop in properties:
            property_results.append({
                "id": prop.id,
                "title": prop.title,
                "description": prop.description,
                "base_price_per_night": prop.base_price_per_night,
                "bedrooms": prop.bedrooms,
                "bathrooms": prop.bathrooms,
                "max_guests": prop.max_guests,
                "property_type": prop.property_type,
                "address": {
                    "street": prop.street,
                    "area": prop.area,
                    "city": prop.city,
                    "emirate": prop.emirate,
                    "country": "UAE",
                    "coordinates": {
                        "latitude": prop.latitude,
                        "longitude": prop.longitude
                    }
                },
                "instant_book": prop.instant_book,
                "pet_friendly": prop.pet_friendly,
                "amenities": prop.amenities,
                "images": [
                    {
                        "url": img.url,
                        "is_primary": img.is_primary,
                        "order": img.order
                    } for img in prop.images
                ],
                "cleaning_fee": prop.cleaning_fee,
                "security_deposit": prop.security_deposit,
                "minimum_nights": prop.minimum_nights,
                "host": {
                    "id": prop.host.id,
                    "name": prop.host.name,
                    "response_rate": prop.host.response_rate,
                    "is_superhost": prop.host.is_superhost
                },
                "rating": prop.rating,
                "review_count": prop.review_count
            })
        
        return {
            "success": True,
            "data": {
                "properties": property_results,
                "total": total,
                "page": page,
                "limit": limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
```

### **Task 2: Create Property Details Endpoint**

```python
@router.get("/api/v1/properties/{property_id}", response_model=PropertySearchResponse)
async def get_property_details(property_id: str):
    """
    Get detailed information about a specific property
    
    Returns comprehensive property data including:
    - Full description and amenities
    - All images
    - Host information
    - Reviews and ratings
    - Pricing details
    - Location information
    """
    try:
        property = your_database.query(Property).filter(Property.id == property_id).first()
        
        if not property:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # Format detailed response
        property_data = {
            "id": property.id,
            "title": property.title,
            "description": property.description,
            "base_price_per_night": property.base_price_per_night,
            "bedrooms": property.bedrooms,
            "bathrooms": property.bathrooms,
            "max_guests": property.max_guests,
            "property_type": property.property_type,
            "address": {
                "street": property.street,
                "area": property.area,
                "city": property.city,
                "emirate": property.emirate,
                "country": "UAE",
                "postal_code": property.postal_code,
                "coordinates": {
                    "latitude": property.latitude,
                    "longitude": property.longitude
                }
            },
            "instant_book": property.instant_book,
            "pet_friendly": property.pet_friendly,
            "amenities": property.amenities,
            "images": [
                {
                    "url": img.url,
                    "is_primary": img.is_primary,
                    "order": img.order,
                    "caption": img.caption
                } for img in property.images
            ],
            "cleaning_fee": property.cleaning_fee,
            "security_deposit": property.security_deposit,
            "minimum_nights": property.minimum_nights,
            "maximum_nights": property.maximum_nights,
            "host": {
                "id": property.host.id,
                "name": property.host.name,
                "response_rate": property.host.response_rate,
                "response_time": property.host.response_time,
                "is_superhost": property.host.is_superhost,
                "languages": property.host.languages,
                "about": property.host.about
            },
            "rating": property.rating,
            "review_count": property.review_count,
            "recent_reviews": [
                {
                    "id": review.id,
                    "guest_name": review.guest_name,
                    "rating": review.rating,
                    "comment": review.comment,
                    "date": review.created_at.isoformat()
                } for review in property.recent_reviews[:5]
            ],
            "house_rules": property.house_rules,
            "check_in_time": property.check_in_time,
            "check_out_time": property.check_out_time,
            "cancellation_policy": property.cancellation_policy
        }
        
        return {
            "success": True,
            "data": property_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get property details: {str(e)}")
```

### **Task 3: Create Availability Check Endpoint**

```python
@router.get("/api/v1/properties/{property_id}/availability")
async def check_availability(
    property_id: str,
    check_in: date = Query(..., description="Check-in date (YYYY-MM-DD)"),
    check_out: date = Query(..., description="Check-out date (YYYY-MM-DD)"),
    guests: Optional[int] = Query(1, description="Number of guests")
):
    """
    Check if property is available for specific dates
    
    Returns availability status and any restrictions
    """
    try:
        property = your_database.query(Property).filter(Property.id == property_id).first()
        
        if not property:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # Validate dates
        if check_in >= check_out:
            raise HTTPException(status_code=400, detail="Check-out must be after check-in")
        
        if guests > property.max_guests:
            raise HTTPException(status_code=400, detail=f"Property only accommodates {property.max_guests} guests")
        
        # Check availability against bookings
        existing_bookings = your_database.query(Booking).filter(
            Booking.property_id == property_id,
            Booking.status.in_(["confirmed", "pending"]),
            Booking.check_out > check_in,
            Booking.check_in < check_out
        ).first()
        
        is_available = existing_bookings is None
        
        # Calculate nights and check minimum stay
        nights = (check_out - check_in).days
        meets_minimum_stay = nights >= property.minimum_nights
        
        return {
            "success": True,
            "data": {
                "property_id": property_id,
                "check_in": check_in.isoformat(),
                "check_out": check_out.isoformat(),
                "nights": nights,
                "guests": guests,
                "is_available": is_available and meets_minimum_stay,
                "availability_details": {
                    "has_conflicts": existing_bookings is not None,
                    "meets_minimum_stay": meets_minimum_stay,
                    "minimum_nights_required": property.minimum_nights
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Availability check failed: {str(e)}")
```

### **Task 4: Create Pricing Calculator Endpoint**

```python
class PricingRequest(BaseModel):
    check_in: date
    check_out: date
    guests: int
    discount_code: Optional[str] = None

@router.post("/api/v1/properties/{property_id}/calculate-pricing")
async def calculate_pricing(property_id: str, pricing_request: PricingRequest):
    """
    Calculate total pricing with breakdown for a booking
    
    Includes base price, fees, taxes, and discounts
    """
    try:
        property = your_database.query(Property).filter(Property.id == property_id).first()
        
        if not property:
            raise HTTPException(status_code=404, detail="Property not found")
        
        check_in = pricing_request.check_in
        check_out = pricing_request.check_out
        guests = pricing_request.guests
        
        # Calculate nights
        nights = (check_out - check_in).days
        
        if nights < property.minimum_nights:
            raise HTTPException(status_code=400, detail=f"Minimum stay is {property.minimum_nights} nights")
        
        # Base pricing calculation
        base_total = property.base_price_per_night * nights
        
        # Additional fees
        cleaning_fee = property.cleaning_fee or 0
        security_deposit = property.security_deposit or 0
        
        # Service fee (platform fee)
        service_fee_rate = 0.03  # 3%
        service_fee = base_total * service_fee_rate
        
        # Tourism tax (Dubai specific)
        tourism_tax_per_night = 10.0  # AED 10 per night
        tourism_tax = tourism_tax_per_night * nights
        
        # VAT (5% in UAE)
        vat_rate = 0.05
        subtotal = base_total + service_fee + tourism_tax
        vat_amount = subtotal * vat_rate
        
        # Apply discount if provided
        discount_amount = 0
        if pricing_request.discount_code:
            discount = get_discount_by_code(pricing_request.discount_code)
            if discount and discount.is_valid:
                if discount.type == "percentage":
                    discount_amount = base_total * (discount.value / 100)
                elif discount.type == "fixed":
                    discount_amount = discount.value
        
        # Calculate total
        total_amount = base_total + cleaning_fee + service_fee + tourism_tax + vat_amount - discount_amount
        
        return {
            "success": True,
            "data": {
                "property_id": property_id,
                "check_in": check_in.isoformat(),
                "check_out": check_out.isoformat(),
                "nights": nights,
                "guests": guests,
                "pricing_breakdown": {
                    "base_price_per_night": property.base_price_per_night,
                    "base_total": base_total,
                    "cleaning_fee": cleaning_fee,
                    "service_fee": service_fee,
                    "tourism_tax": tourism_tax,
                    "vat_amount": vat_amount,
                    "discount_amount": discount_amount,
                    "security_deposit": security_deposit,
                    "total_amount": total_amount
                },
                "payment_schedule": {
                    "due_now": total_amount - security_deposit,
                    "security_deposit": security_deposit,
                    "refundable_amount": security_deposit
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pricing calculation failed: {str(e)}")
```

### **Task 5: Create Booking Creation Endpoint**

```python
class BookingRequest(BaseModel):
    property_id: str
    check_in: date
    check_out: date
    guests: int
    guest_info: dict = {
        "name": "string",
        "email": "string",
        "phone": "string",
        "country": "string"
    }
    total_amount: float
    payment_method: Optional[str] = "card"
    special_requests: Optional[str] = None

@router.post("/api/v1/bookings")
async def create_booking(booking_request: BookingRequest):
    """
    Create a new booking request
    
    Processes the booking and returns booking confirmation details
    """
    try:
        # Validate property exists
        property = your_database.query(Property).filter(
            Property.id == booking_request.property_id
        ).first()
        
        if not property:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # Final availability check
        existing_bookings = your_database.query(Booking).filter(
            Booking.property_id == booking_request.property_id,
            Booking.status.in_(["confirmed", "pending"]),
            Booking.check_out > booking_request.check_in,
            Booking.check_in < booking_request.check_out
        ).first()
        
        if existing_bookings:
            raise HTTPException(status_code=400, detail="Property not available for selected dates")
        
        # Generate booking ID
        booking_id = f"BK{int(time.time())}{random.randint(1000, 9999)}"
        
        # Create booking record
        new_booking = Booking(
            id=booking_id,
            property_id=booking_request.property_id,
            check_in=booking_request.check_in,
            check_out=booking_request.check_out,
            guests=booking_request.guests,
            guest_name=booking_request.guest_info["name"],
            guest_email=booking_request.guest_info["email"],
            guest_phone=booking_request.guest_info["phone"],
            total_amount=booking_request.total_amount,
            status="pending",
            payment_method=booking_request.payment_method,
            special_requests=booking_request.special_requests,
            created_at=datetime.utcnow()
        )
        
        your_database.add(new_booking)
        your_database.commit()
        
        # Send confirmation emails (implement separately)
        send_booking_confirmation_email(new_booking)
        notify_host_of_booking(new_booking)
        
        return {
            "success": True,
            "data": {
                "booking_id": booking_id,
                "status": "pending",
                "property": {
                    "id": property.id,
                    "title": property.title,
                    "address": f"{property.area}, {property.city}"
                },
                "booking_details": {
                    "check_in": booking_request.check_in.isoformat(),
                    "check_out": booking_request.check_out.isoformat(),
                    "nights": (booking_request.check_out - booking_request.check_in).days,
                    "guests": booking_request.guests,
                    "total_amount": booking_request.total_amount
                },
                "guest_info": booking_request.guest_info,
                "next_steps": [
                    "Payment processing will begin within 24 hours",
                    "You will receive check-in instructions 24 hours before arrival",
                    "Host will be notified of your booking"
                ],
                "contact_info": {
                    "support_email": "support@yourplatform.com",
                    "emergency_phone": "+971-xxx-xxx-xxxx"
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        your_database.rollback()
        raise HTTPException(status_code=500, detail=f"Booking creation failed: {str(e)}")
```

---

## 🔐 **Authentication Implementation**

Add this authentication middleware:

```python
from fastapi import Header, HTTPException

async def verify_krib_ai_auth(authorization: str = Header(...)):
    """Verify Kribz AI service account authentication"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    api_key = authorization[7:]  # Remove "Bearer " prefix
    
    # Check against your configured API keys
    valid_keys = {
        "krib_ai_test_key_12345": "test",
        os.getenv("KRIB_AI_AGENT_API_KEY"): "production"
    }
    
    if api_key not in valid_keys:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return {"service": "krib_ai", "environment": valid_keys[api_key]}

# Add to all endpoints:
# async def endpoint_name(..., auth: dict = Depends(verify_krib_ai_auth)):
```

---

## 🧪 **Testing Commands**

After implementation, test with these curl commands:

```bash
# Test property search
curl -X GET "https://krib-host-dahsboard-backend.onrender.com/api/v1/properties/search?city=Dubai&bedrooms=2&max_price_per_night=500" \
  -H "Authorization: Bearer krib_ai_test_key_12345"

# Test property details
curl -X GET "https://krib-host-dahsboard-backend.onrender.com/api/v1/properties/prop_123" \
  -H "Authorization: Bearer krib_ai_test_key_12345"

# Test availability
curl -X GET "https://krib-host-dahsboard-backend.onrender.com/api/v1/properties/prop_123/availability?check_in=2025-03-01&check_out=2025-03-05&guests=2" \
  -H "Authorization: Bearer krib_ai_test_key_12345"

# Test pricing
curl -X POST "https://krib-host-dahsboard-backend.onrender.com/api/v1/properties/prop_123/calculate-pricing" \
  -H "Authorization: Bearer krib_ai_test_key_12345" \
  -H "Content-Type: application/json" \
  -d '{"check_in": "2025-03-01", "check_out": "2025-03-05", "guests": 2}'

# Test booking
curl -X POST "https://krib-host-dahsboard-backend.onrender.com/api/v1/bookings" \
  -H "Authorization: Bearer krib_ai_test_key_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "property_id": "prop_123",
    "check_in": "2025-03-01",
    "check_out": "2025-03-05",
    "guests": 2,
    "guest_info": {"name": "John Doe", "email": "john@example.com", "phone": "+971501234567"},
    "total_amount": 1200.00
  }'
```

---

## ✅ **SUCCESS CRITERIA**

Your implementation is complete when:

1. ✅ All 5 endpoints return proper JSON responses
2. ✅ Authentication works with `krib_ai_test_key_12345`
3. ✅ Property search returns real Dubai properties
4. ✅ Availability checking works with date ranges
5. ✅ Pricing calculator includes all fees and taxes
6. ✅ Booking creation generates confirmation IDs
7. ✅ All responses follow the exact data structure above

**Copy this code exactly - don't modify the API design. Kribz AI agents are configured to work with these specific endpoints and data formats.**
