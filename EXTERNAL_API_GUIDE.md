# 🤖 Krib AI External API Integration Guide

## 📋 Overview

The Krib AI External API provides third-party AI platforms and services with access to property data, availability checking, pricing calculations, and booking creation for the UAE rental market.

**Base URL**: `https://krib-host-dahsboard-backend.onrender.com/api/external`

---

## 🔐 Authentication

All external API endpoints require authentication using API keys passed in the Authorization header.

### Headers Required
```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

### API Key Types
- **Krib AI Agent**: Full access (search, book, pricing)
- **ChatGPT Agent**: Read-only access (search, availability)
- **Claude Agent**: Read-only access (search, availability)
- **Booking Service**: Full booking access

### Test API Keys
For development and testing:
```
krib_ai_agent: krib_ai_test_key_12345
chatgpt_agent: chatgpt_test_key_67890
claude_agent: claude_test_key_abcde
booking_service: booking_test_key_fghij
```

---

## 🔍 API Endpoints

### 1. Property Search
**GET** `/properties/search`

Search for available rental properties with comprehensive filtering.

#### Query Parameters
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `city` | string | City or area name | `Dubai Marina` |
| `state` | string | UAE Emirate | `Dubai` |
| `min_price_per_night` | float | Minimum price in AED | `200` |
| `max_price_per_night` | float | Maximum price in AED | `1000` |
| `bedrooms` | int | Minimum bedrooms | `2` |
| `bathrooms` | float | Minimum bathrooms | `1.5` |
| `max_guests` | int | Minimum guest capacity | `4` |
| `property_type` | string | Property type | `apartment` |
| `check_in` | date | Check-in date | `2024-03-15` |
| `check_out` | date | Check-out date | `2024-03-17` |
| `limit` | int | Results per page (1-50) | `20` |
| `offset` | int | Results offset | `0` |
| `sort_by` | string | Sort order | `price_asc` |

#### Example Request
```bash
curl -X GET "https://krib-host-dahsboard-backend.onrender.com/api/external/properties/search?city=Dubai%20Marina&bedrooms=2&limit=5" \
  -H "Authorization: Bearer krib_ai_test_key_12345"
```

#### Example Response
```json
{
  "success": true,
  "data": {
    "properties": [
      {
        "id": "prop_123",
        "title": "Luxury 2BR Marina Apartment",
        "description": "Stunning waterfront apartment...",
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
          "coordinates": {"latitude": 25.0757, "longitude": 55.1395}
        },
        "amenities": ["WiFi", "Pool", "Gym", "Parking", "Sea View"],
        "images": [
          {"url": "https://...", "is_primary": true, "order": 1}
        ],
        "host": {
          "id": "host_456",
          "name": "Ahmed Al-Mansouri",
          "response_rate": 98,
          "is_superhost": true
        },
        "rating": {
          "overall": 4.8,
          "total_reviews": 24,
          "cleanliness": 4.9,
          "communication": 4.7,
          "location": 4.9,
          "value": 4.6
        }
      }
    ],
    "total_count": 45,
    "has_more": true,
    "search_metadata": {
      "filters_applied": {"city": "Dubai Marina", "bedrooms": 2},
      "total_available": 45
    }
  }
}
```

---

### 2. Property Details
**GET** `/properties/{property_id}`

Get comprehensive details for a specific property.

#### Example Request
```bash
curl -X GET "https://krib-host-dahsboard-backend.onrender.com/api/external/properties/prop_123" \
  -H "Authorization: Bearer krib_ai_test_key_12345"
```

#### Example Response
```json
{
  "success": true,
  "data": {
    "property": {
      "id": "prop_123",
      "title": "Luxury 2BR Marina Apartment",
      "description": "Experience luxury living...",
      "base_price_per_night": 450.0,
      "pricing_info": {
        "base_price": 450.0,
        "cleaning_fee": 75.0,
        "security_deposit": 500.0,
        "currency": "AED"
      },
      "host_info": {
        "id": "host_456",
        "name": "Ahmed Al-Mansouri",
        "joined_date": "2023-01-15T10:30:00Z",
        "response_rate": 98,
        "response_time": "within an hour",
        "is_superhost": true,
        "total_properties": 3,
        "languages": ["English", "Arabic"]
      },
      "reviews_summary": {
        "total_reviews": 24,
        "overall_rating": 4.8,
        "rating_breakdown": {
          "cleanliness": 4.9,
          "accuracy": 4.8,
          "communication": 4.7,
          "location": 4.9,
          "check_in": 4.8,
          "value": 4.6
        }
      },
      "policies": {
        "check_in_time": "15:00",
        "check_out_time": "11:00",
        "minimum_nights": 2,
        "cancellation_policy": "moderate",
        "house_rules": ["No smoking", "No parties"]
      }
    }
  }
}
```

---

### 3. Availability Check
**GET** `/properties/{property_id}/availability`

Check if a property is available for specific dates.

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | date | Yes | Check-in date (YYYY-MM-DD) |
| `end_date` | date | Yes | Check-out date (YYYY-MM-DD) |
| `guests` | int | No | Number of guests (default: 1) |

#### Example Request
```bash
curl -X GET "https://krib-host-dahsboard-backend.onrender.com/api/external/properties/prop_123/availability?start_date=2024-03-15&end_date=2024-03-17&guests=2" \
  -H "Authorization: Bearer krib_ai_test_key_12345"
```

#### Example Response
```json
{
  "success": true,
  "data": {
    "property_id": "prop_123",
    "start_date": "2024-03-15",
    "end_date": "2024-03-17",
    "guests": 2,
    "is_available": true,
    "reasons": [],
    "alternative_dates": []
  }
}
```

---

### 4. Pricing Calculator
**POST** `/properties/{property_id}/calculate-pricing`

Calculate total pricing including all fees and taxes.

#### Request Body
```json
{
  "check_in": "2024-03-15",
  "check_out": "2024-03-17", 
  "guests": 2,
  "promo_code": "KRIB10"
}
```

#### Example Request
```bash
curl -X POST "https://krib-host-dahsboard-backend.onrender.com/api/external/properties/prop_123/calculate-pricing" \
  -H "Authorization: Bearer krib_ai_test_key_12345" \
  -H "Content-Type: application/json" \
  -d '{"check_in": "2024-03-15", "check_out": "2024-03-17", "guests": 2}'
```

#### Example Response
```json
{
  "success": true,
  "data": {
    "property_id": "prop_123",
    "check_in": "2024-03-15",
    "check_out": "2024-03-17",
    "guests": 2,
    "nights": 2,
    "base_price": 900.0,
    "cleaning_fee": 75.0,
    "service_fee": 27.0,
    "taxes": 30.0,
    "discount": 0.0,
    "total_price": 1032.0,
    "currency": "AED",
    "breakdown": [
      {"name": "AED 450 × 2 nights", "amount": 900.0, "type": "base"},
      {"name": "Cleaning fee", "amount": 75.0, "type": "fee"},
      {"name": "Service fee", "amount": 27.0, "type": "fee"},
      {"name": "Tourism tax", "amount": 30.0, "type": "tax"}
    ]
  }
}
```

---

### 5. Create Booking
**POST** `/bookings`

Create a new booking request for a property.

#### Request Body
```json
{
  "property_id": "prop_123",
  "check_in": "2024-03-15",
  "check_out": "2024-03-17",
  "guests": 2,
  "guest_info": {
    "first_name": "Sarah",
    "last_name": "Johnson",
    "email": "sarah.johnson@email.com",
    "phone": "501234567",
    "country_code": "+971"
  },
  "special_requests": "Late check-in preferred",
  "total_amount": 1032.0,
  "payment_method": "pending",
  "source": "krib_ai_agent"
}
```

#### Example Request
```bash
curl -X POST "https://krib-host-dahsboard-backend.onrender.com/api/external/bookings" \
  -H "Authorization: Bearer krib_ai_test_key_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "property_id": "prop_123",
    "check_in": "2024-03-15",
    "check_out": "2024-03-17",
    "guests": 2,
    "guest_info": {
      "first_name": "Sarah",
      "last_name": "Johnson",
      "email": "sarah.johnson@email.com",
      "phone": "501234567",
      "country_code": "+971"
    },
    "total_amount": 1032.0,
    "payment_method": "pending"
  }'
```

#### Example Response
```json
{
  "success": true,
  "data": {
    "booking_id": "book_789",
    "status": "pending",
    "property": {
      "id": "prop_123",
      "title": "Luxury 2BR Marina Apartment",
      "address": "Marina Walk, Dubai Marina, Dubai"
    },
    "dates": {
      "check_in": "2024-03-15",
      "check_out": "2024-03-17",
      "nights": 2
    },
    "guest_info": {
      "first_name": "Sarah",
      "last_name": "Johnson",
      "email": "sarah.johnson@email.com",
      "phone": "501234567",
      "country_code": "+971"
    },
    "total_amount": 1032.0,
    "currency": "AED",
    "payment": {
      "method": "pending",
      "status": "pending",
      "payment_intent_id": null
    },
    "next_steps": [
      "Booking request submitted to host",
      "Host will review and confirm within 24 hours",
      "You will receive confirmation email once approved"
    ],
    "cancellation_policy": "moderate",
    "host_contact": {
      "name": "Ahmed Al-Mansouri",
      "response_time": "within an hour"
    }
  },
  "message": "Booking request created successfully"
}
```

---

## 🚀 Getting Started

### 1. Test the API
```bash
# Health check
curl -X GET "https://krib-host-dahsboard-backend.onrender.com/api/external/health" \
  -H "Authorization: Bearer krib_ai_test_key_12345"

# Search properties
curl -X GET "https://krib-host-dahsboard-backend.onrender.com/api/external/properties/search?city=Dubai&limit=3" \
  -H "Authorization: Bearer krib_ai_test_key_12345"
```

### 2. API Documentation
Visit the interactive API docs:
`https://krib-host-dahsboard-backend.onrender.com/docs`

Look for the "external-api" section.

### 3. Production API Keys
Contact the Krib AI team to get production API keys:
- Include your use case and expected volume
- Specify required permissions
- Provide technical contact information

---

## ⚡ Rate Limits

| Service Type | Requests/Minute |
|--------------|-----------------|
| Krib AI Agent | 200 |
| ChatGPT Agent | 100 |
| Claude Agent | 100 |
| Booking Service | 150 |
| Default | 60 |

---

## 🔒 Security Best Practices

1. **API Key Security**
   - Never expose API keys in client-side code
   - Store keys as environment variables
   - Rotate keys quarterly

2. **Request Validation**
   - Validate all input parameters
   - Handle rate limit responses (429)
   - Implement retry logic with exponential backoff

3. **Error Handling**
   - Always check the `success` field in responses
   - Handle common HTTP status codes (401, 404, 500)
   - Log errors for monitoring

---

## 🚨 Error Responses

All errors follow this format:
```json
{
  "success": false,
  "error": "Error message",
  "details": {},
  "code": "ERROR_CODE"
}
```

### Common Error Codes
- `401`: Invalid or missing API key
- `403`: Insufficient permissions
- `404`: Resource not found
- `409`: Conflict (e.g., property not available)
- `429`: Rate limit exceeded
- `500`: Internal server error

---

## 📞 Support

For technical support and API access:
- **Email**: api-support@krib.ai
- **Documentation**: This guide and `/docs` endpoint
- **Status Page**: Monitor API availability

---

## 🔄 Webhook Notifications (Coming Soon)

Future webhook support for:
- Booking confirmations
- Availability changes
- Pricing updates
- Host responses

---

*Last Updated: January 2025*  
*API Version: 1.0.0*
