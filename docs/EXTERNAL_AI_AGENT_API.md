# Krib External API for AI Agent Platforms

## Overview

The Krib External API enables AI agent platforms to interact with the Krib property rental marketplace. This API allows AI agents to:

- **Search** for properties with detailed filters
- **Check availability** and calculate pricing
- **Create bookings** on behalf of users
- **Communicate** with hosts via the messaging system
- **View host profiles** (public information only)
- **Read property reviews**

**Base URL:** `https://api.host.krib.ae/api/external`

---

## Authentication

All API requests require a Bearer token in the Authorization header:

```bash
Authorization: Bearer YOUR_API_KEY
```

### Getting Your API Key

API keys are generated through the Krib admin dashboard. Contact the Krib team or generate one yourself if you have admin access:

**Admin Endpoint:** `POST /api/admin/api-keys/generate`

```bash
curl -X POST "https://api.host.krib.ae/api/admin/api-keys/generate" \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My AI Agent Platform",
    "tier": "full_access",
    "rate_limit": 200
  }'
```

⚠️ **IMPORTANT:** The API key is shown **ONLY ONCE** when created. Save it immediately!

### API Key Tiers

| Tier | Permissions |
|------|-------------|
| `read_only` | Search, availability, reviews, host profiles |
| `standard` | read_only + messaging |
| `full_access` | All permissions including bookings & payments |

### Example Request

```bash
curl -X GET "https://api.host.krib.ae/api/external/v1/properties/search?bedrooms=2&city=Dubai" \
  -H "Authorization: Bearer krib_prod_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

---

## Rate Limits

| Endpoint Type | Rate Limit |
|--------------|------------|
| Search endpoints | 100 requests/minute |
| Property details | 200 requests/minute |
| Availability/Pricing | 150 requests/minute |
| Booking creation | 50 requests/minute |
| Messaging | 50 requests/minute |

Rate limit headers are included in all responses:
- `X-RateLimit-Limit`: Max requests per minute
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Seconds until reset

---

## Complete API Reference

### 1. Property Search

Search for available properties with comprehensive filters.

**Endpoint:** `GET /v1/properties/search`

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `city` | string | City or area name (e.g., "Dubai Marina") |
| `state` | string | UAE Emirate (Dubai, Abu Dhabi, etc.) |
| `bedrooms` | integer | Minimum number of bedrooms |
| `bathrooms` | float | Minimum number of bathrooms |
| `max_guests` | integer | Minimum guest capacity |
| `min_price_per_night` | float | Minimum price in AED |
| `max_price_per_night` | float | Maximum price in AED |
| `property_type` | string | apartment, villa, studio, townhouse |
| `check_in` | date | Check-in date (YYYY-MM-DD) |
| `check_out` | date | Check-out date (YYYY-MM-DD) |
| `limit` | integer | Results per page (1-50, default: 20) |
| `offset` | integer | Pagination offset |
| `sort_by` | string | price_asc, price_desc, rating |

**Example - Find 2-bedroom apartments for 10 days:**

```bash
curl -X GET "https://api.host.krib.ae/api/external/v1/properties/search?\
bedrooms=2&\
check_in=2025-01-12&\
check_out=2025-01-22&\
city=Dubai&\
sort_by=price_asc" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**

```json
{
  "success": true,
  "data": {
    "properties": [
      {
        "id": "prop_uuid_123",
        "title": "Luxury 2BR in Dubai Marina",
        "description": "Beautiful apartment with sea view...",
        "base_price_per_night": 450.0,
        "bedrooms": 2,
        "bathrooms": 2.0,
        "max_guests": 4,
        "property_type": "apartment",
        "address": {
          "street": "Marina Walk",
          "area": "Dubai Marina",
          "city": "Dubai Marina",
          "emirate": "Dubai",
          "country": "UAE",
          "coordinates": {
            "latitude": 25.0772,
            "longitude": 55.1395
          }
        },
        "amenities": ["WiFi", "Pool", "Gym", "Parking"],
        "images": [
          {
            "url": "https://storage.krib.ae/properties/image1.jpg",
            "is_primary": true,
            "order": 1
          }
        ],
        "host": {
          "id": "host_uuid_456",
          "name": "Ahmed",
          "response_rate": 95,
          "is_superhost": true,
          "member_since": "2023-01-15"
        },
        "rating": {
          "overall": 4.8,
          "total_reviews": 24,
          "cleanliness": 4.9,
          "communication": 4.8,
          "location": 4.7,
          "value": 4.6
        },
        "check_in_time": "15:00",
        "check_out_time": "11:00",
        "minimum_nights": 1
      }
    ],
    "total_count": 45,
    "has_more": true,
    "search_metadata": {
      "query_time_ms": 125,
      "filters_applied": {
        "bedrooms": 2,
        "city": "Dubai"
      }
    }
  }
}
```

---

### 2. Property Details

Get comprehensive details for a specific property.

**Endpoint:** `GET /v1/properties/{property_id}`

**Response includes:**
- Full property description
- All images
- Complete amenities list
- Host information (public only)
- Pricing details
- House rules and policies
- Reviews summary

---

### 3. Check Availability

Verify if a property is available for specific dates.

**Endpoint:** `GET /v1/properties/{property_id}/availability`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `check_in` | date | Yes | Check-in date |
| `check_out` | date | Yes | Check-out date |
| `guests` | integer | No | Number of guests (default: 1) |

**Example:**

```bash
curl -X GET "https://api.host.krib.ae/api/external/v1/properties/prop_123/availability?\
check_in=2025-01-12&\
check_out=2025-01-22&\
guests=4" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**

```json
{
  "success": true,
  "data": {
    "property_id": "prop_123",
    "check_in": "2025-01-12",
    "check_out": "2025-01-22",
    "guests": 4,
    "is_available": true,
    "reasons": [],
    "alternative_dates": []
  }
}
```

---

### 4. Calculate Pricing

Get detailed pricing breakdown for a booking.

**Endpoint:** `POST /v1/properties/{property_id}/calculate-pricing`

**Request Body:**

```json
{
  "check_in": "2025-01-12",
  "check_out": "2025-01-22",
  "guests": 4,
  "promo_code": "KRIB10"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "property_id": "prop_123",
    "check_in": "2025-01-12",
    "check_out": "2025-01-22",
    "guests": 4,
    "nights": 10,
    "base_price": 4500.00,
    "cleaning_fee": 75.00,
    "service_fee": 135.00,
    "taxes": 150.00,
    "discount": 450.00,
    "total_price": 4410.00,
    "currency": "AED",
    "breakdown": [
      {"name": "AED 450 × 10 nights", "amount": 4500.00, "type": "base"},
      {"name": "Cleaning fee", "amount": 75.00, "type": "fee"},
      {"name": "Service fee", "amount": 135.00, "type": "fee"},
      {"name": "Tourism tax", "amount": 150.00, "type": "tax"},
      {"name": "Discount (KRIB10)", "amount": -450.00, "type": "discount"}
    ]
  }
}
```

---

### 5. Create Booking

Create a new booking request.

**Endpoint:** `POST /v1/bookings`

**Request Body:**

```json
{
  "property_id": "prop_123",
  "check_in": "2025-01-12",
  "check_out": "2025-01-22",
  "guests": 4,
  "guest_info": {
    "first_name": "John",
    "last_name": "Smith",
    "email": "john.smith@email.com",
    "phone": "501234567",
    "country_code": "+971"
  },
  "special_requests": "Early check-in if possible",
  "total_amount": 4410.00,
  "payment_method": "stripe",
  "source": "krib_ai_agent"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "booking_id": "booking_uuid_789",
    "status": "pending",
    "property": {
      "id": "prop_123",
      "title": "Luxury 2BR in Dubai Marina",
      "address": "Marina Walk, Dubai Marina, Dubai"
    },
    "dates": {
      "check_in": "2025-01-12",
      "check_out": "2025-01-22",
      "nights": 10
    },
    "guest_info": {...},
    "total_amount": 4410.00,
    "currency": "AED",
    "payment": {
      "method": "stripe",
      "status": "pending",
      "payment_intent_id": null
    },
    "next_steps": [
      "Booking request submitted to host",
      "Host will review and confirm within 24 hours",
      "You will receive confirmation email once approved",
      "Payment will be processed after confirmation"
    ],
    "cancellation_policy": "moderate",
    "host_contact": {
      "name": "Ahmed",
      "response_time": "within an hour"
    }
  },
  "message": "Booking request created successfully"
}
```

---

### 6. Get Booking Status

Check the status of a booking.

**Endpoint:** `GET /v1/external/bookings/{booking_id}/status`

**Response:**

```json
{
  "success": true,
  "data": {
    "booking_id": "booking_789",
    "status": "confirmed",
    "payment_status": "paid",
    "created_at": "2025-01-10T10:30:00Z",
    "confirmed_at": "2025-01-10T12:45:00Z",
    "total_amount": 4410.00,
    "property": {
      "id": "prop_123",
      "title": "Luxury 2BR in Dubai Marina"
    }
  }
}
```

---

### 7. Process Payment

Process payment for a confirmed booking.

**Endpoint:** `POST /external/v1/bookings/{booking_id}/process-payment`

**Request Body (optional):**

```json
{
  "payment_method_id": "pm_card_visa"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "booking_id": "booking_789",
    "payment_status": "paid",
    "payment_intent_id": "pi_xxxxx",
    "amount_paid": 4410.00,
    "currency": "AED",
    "host_payout": {
      "amount": 3748.50,
      "scheduled_date": "2025-01-23",
      "status": "scheduled",
      "platform_fee": 661.50,
      "platform_fee_percentage": 15.0
    }
  },
  "message": "Payment processed successfully"
}
```

---

### 8. Get Host Profile

Get public host profile (no private information).

**Endpoint:** `GET /v1/hosts/{host_id}/profile`

**Response:**

```json
{
  "success": true,
  "data": {
    "host": {
      "id": "host_456",
      "name": "Ahmed",
      "avatar_url": "https://storage.krib.ae/avatars/ahmed.jpg",
      "is_superhost": true,
      "response_rate": 98,
      "response_time": "within an hour",
      "member_since": "2023-01-15",
      "total_listings": 5,
      "total_reviews": 124,
      "average_rating": 4.8,
      "languages": ["English", "Arabic"],
      "verified": true
    },
    "properties_count": 5,
    "can_message": true
  }
}
```

**Note:** Email and phone are NEVER exposed through this endpoint.

---

### 9. Send Message to Host

Initiate communication with a property host.

**Endpoint:** `POST /v1/messages`

**Request Body:**

```json
{
  "property_id": "prop_123",
  "guest_name": "John Smith",
  "guest_email": "john.smith@email.com",
  "message": "Hi! I'm interested in booking your apartment for January 12-22. Is it available? Also, do you allow early check-in?",
  "inquiry_type": "availability"
}
```

**Inquiry Types:**
- `general` - General questions
- `availability` - Date availability
- `pricing` - Pricing questions
- `amenities` - Amenity inquiries
- `booking_question` - Questions about existing booking

**Response:**

```json
{
  "success": true,
  "data": {
    "conversation_id": "conv_uuid_abc",
    "message_id": "msg_uuid_xyz",
    "status": "sent",
    "host_id": "host_456",
    "host_name": "Ahmed",
    "property_title": "Luxury 2BR in Dubai Marina",
    "estimated_response_time": "within an hour",
    "created_at": "2025-01-10T14:30:00Z"
  },
  "message": "Message sent successfully"
}
```

---

### 10. Get Conversation

Retrieve conversation with all messages.

**Endpoint:** `GET /v1/conversations/{conversation_id}`

**Query Parameters:**
- `limit`: Number of messages (default: 50, max: 100)

**Response:**

```json
{
  "success": true,
  "data": {
    "conversation_id": "conv_abc",
    "property_id": "prop_123",
    "property_title": "Luxury 2BR in Dubai Marina",
    "host": {
      "id": "host_456",
      "name": "Ahmed",
      "avatar_url": "https://storage.krib.ae/avatars/ahmed.jpg",
      "is_superhost": true,
      "response_rate": 98,
      "response_time": "within an hour"
    },
    "guest_name": "John Smith",
    "status": "active",
    "messages": [
      {
        "id": "msg_1",
        "sender_type": "guest",
        "sender_name": "John Smith",
        "content": "Hi! I'm interested in booking...",
        "is_read": true,
        "is_ai_generated": false,
        "created_at": "2025-01-10T14:30:00Z"
      },
      {
        "id": "msg_2",
        "sender_type": "host",
        "sender_name": "Ahmed",
        "content": "Hello John! Yes, the apartment is available...",
        "is_read": false,
        "is_ai_generated": false,
        "created_at": "2025-01-10T15:00:00Z"
      }
    ],
    "unread_count": 1,
    "created_at": "2025-01-10T14:30:00Z",
    "last_message_at": "2025-01-10T15:00:00Z"
  }
}
```

---

### 11. Send Follow-up Message

Send a follow-up message in an existing conversation.

**Endpoint:** `POST /v1/conversations/{conversation_id}/messages`

**Request Body:**

```json
{
  "message": "That sounds great! Can we proceed with the booking?",
  "guest_email": "john.smith@email.com"
}
```

---

### 12. Get Property Reviews

Get reviews for a property.

**Endpoint:** `GET /v1/properties/{property_id}/reviews`

**Query Parameters:**
- `limit`: Reviews per page (default: 20, max: 50)
- `offset`: Pagination offset
- `sort_by`: `recent`, `highest`, `lowest`

**Response:**

```json
{
  "success": true,
  "data": {
    "property_id": "prop_123",
    "total_reviews": 24,
    "average_rating": 4.8,
    "rating_breakdown": {
      "cleanliness": 4.9,
      "communication": 4.8,
      "location": 4.7,
      "value": 4.6,
      "accuracy": 4.8,
      "check_in": 4.9
    },
    "rating_distribution": {
      "5": 18,
      "4": 4,
      "3": 2,
      "2": 0,
      "1": 0
    },
    "reviews": [
      {
        "id": "review_1",
        "guest_name": "Sarah",
        "rating": 5.0,
        "comment": "Amazing apartment with stunning views! Ahmed was very responsive and helpful.",
        "stay_date": "December 2024",
        "cleanliness_rating": 5.0,
        "communication_rating": 5.0,
        "location_rating": 4.5,
        "value_rating": 4.5,
        "host_response": "Thank you Sarah! It was a pleasure hosting you!",
        "host_response_date": "2024-12-28",
        "created_at": "2024-12-27T10:00:00Z"
      }
    ],
    "has_more": true,
    "pagination": {
      "limit": 20,
      "offset": 0,
      "total": 24
    }
  }
}
```

---

## Complete Booking Flow Example

Here's how an AI agent would complete a full booking:

### Step 1: User Request
> "I need a 2-bedroom apartment in Dubai for 10 days, January 12-22"

### Step 2: Search Properties

```bash
GET /v1/properties/search?bedrooms=2&check_in=2025-01-12&check_out=2025-01-22&city=Dubai
```

### Step 3: Check Availability

```bash
GET /v1/properties/{property_id}/availability?check_in=2025-01-12&check_out=2025-01-22&guests=4
```

### Step 4: Calculate Pricing

```bash
POST /v1/properties/{property_id}/calculate-pricing
{
  "check_in": "2025-01-12",
  "check_out": "2025-01-22",
  "guests": 4
}
```

### Step 5: Optional - Message Host

```bash
POST /v1/messages
{
  "property_id": "prop_123",
  "guest_name": "John Smith",
  "guest_email": "john@email.com",
  "message": "Hi! Is early check-in possible on January 12?"
}
```

### Step 6: Create Booking

```bash
POST /v1/bookings
{
  "property_id": "prop_123",
  "check_in": "2025-01-12",
  "check_out": "2025-01-22",
  "guests": 4,
  "guest_info": {
    "first_name": "John",
    "last_name": "Smith",
    "email": "john@email.com",
    "phone": "501234567",
    "country_code": "+971"
  },
  "total_amount": 4410.00
}
```

### Step 7: Process Payment

```bash
POST /external/v1/bookings/{booking_id}/process-payment
```

### Step 8: Monitor Status

```bash
GET /v1/external/bookings/{booking_id}/status
```

---

## Webhooks

Set up webhooks to receive real-time updates.

### Webhook Events

| Event | Description |
|-------|-------------|
| `booking.created` | New booking request created |
| `booking.confirmed` | Host confirmed booking |
| `booking.cancelled` | Booking was cancelled |
| `booking.completed` | Stay completed |
| `payment.succeeded` | Payment processed |
| `payment.failed` | Payment failed |
| `message.received` | New message from host |
| `host.response` | Host responded to inquiry |

### Webhook Payload Example

```json
{
  "event": "booking.confirmed",
  "timestamp": "2025-01-10T15:30:00Z",
  "data": {
    "booking_id": "booking_789",
    "property_id": "prop_123",
    "status": "confirmed",
    "guest_email": "john@email.com",
    "check_in": "2025-01-12",
    "check_out": "2025-01-22"
  },
  "signature": "sha256=..."
}
```

### Verifying Webhook Signatures

```python
import hmac
import hashlib

def verify_webhook(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

---

## Error Handling

### Error Response Format

```json
{
  "success": false,
  "error": "Error message",
  "details": {
    "field": "specific error"
  },
  "code": "ERROR_CODE"
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Invalid or missing API key |
| `FORBIDDEN` | 403 | Access denied |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 400 | Invalid request data |
| `CONFLICT` | 409 | Resource conflict (e.g., dates not available) |
| `RATE_LIMITED` | 429 | Too many requests |
| `PAYMENT_REQUIRED` | 402 | Payment failed |
| `SERVER_ERROR` | 500 | Internal server error |

---

## Best Practices

1. **Always check availability** before creating a booking
2. **Calculate pricing** to show users accurate totals
3. **Use pagination** for search results
4. **Handle rate limits** with exponential backoff
5. **Verify webhook signatures** for security
6. **Cache property details** to reduce API calls
7. **Never store** host email or phone (we don't expose them)

---

## Support

- **API Status:** https://status.krib.ae
- **Documentation:** https://docs.krib.ae
- **Technical Support:** dev@krib.ae

---

## Changelog

### v2.0.0 (December 2024)
- Added host profile endpoint
- Added messaging system for AI agents
- Added property reviews endpoint
- Enhanced booking flow
- Improved error responses

### v1.0.0 (November 2024)
- Initial release
- Property search and details
- Booking creation
- Payment processing

