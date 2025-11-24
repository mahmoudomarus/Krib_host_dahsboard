# Krib Host Platform - API Documentation

## Overview

This document describes the public API for external platforms to integrate with the Krib Host Platform.

## Base URL

```
Production: https://api.host.krib.ae/api
Development: http://localhost:8000/api
```

## Authentication

All API requests require authentication using Bearer token from Supabase.

```http
Authorization: Bearer {supabase_access_token}
```

### Get Access Token

Users authenticate via Supabase Auth:

```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'password'
})

const token = data.session.access_token
```

## Properties API

### List Properties

```http
GET /api/properties
Authorization: Bearer {token}
```

Response:
```json
[
  {
    "id": "uuid",
    "title": "Luxury Marina Apartment",
    "description": "...",
    "property_type": "apartment",
    "max_guests": 4,
    "bedrooms": 2,
    "bathrooms": 2,
    "base_price": 500,
    "status": "active",
    "emirate": "Dubai",
    "area": "Marina",
    "full_address": "...",
    "amenities": ["wifi", "parking"],
    "images": ["url1", "url2"],
    "rating": 4.8,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### Get Property Details

```http
GET /api/properties/{property_id}
Authorization: Bearer {token}
```

### Create Property

```http
POST /api/properties
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Luxury Marina Apartment",
  "description": "Modern apartment with sea view",
  "property_type": "apartment",
  "max_guests": 4,
  "bedrooms": 2,
  "bathrooms": 2,
  "base_price": 500,
  "emirate": "Dubai",
  "area": "Marina",
  "full_address": "Address here",
  "amenities": ["wifi", "parking", "pool"],
  "images": ["https://..."]
}
```

### Update Property

```http
PUT /api/properties/{property_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Updated Title",
  "base_price": 550
}
```

### Delete Property

```http
DELETE /api/properties/{property_id}
Authorization: Bearer {token}
```

## Bookings API

### List Bookings

```http
GET /api/bookings
Authorization: Bearer {token}
```

Query Parameters:
- `status`: Filter by status (pending, confirmed, cancelled, completed)
- `property_id`: Filter by property
- `start_date`: Filter from date
- `end_date`: Filter to date

Response:
```json
[
  {
    "id": "uuid",
    "property_id": "uuid",
    "guest_name": "John Doe",
    "guest_email": "john@example.com",
    "guest_phone": "+971501234567",
    "check_in": "2024-12-01",
    "check_out": "2024-12-05",
    "nights": 4,
    "guests": 2,
    "total_amount": 2000,
    "status": "confirmed",
    "created_at": "2024-11-20T00:00:00Z"
  }
]
```

### Create Booking

```http
POST /api/bookings
Authorization: Bearer {token}
Content-Type: application/json

{
  "property_id": "uuid",
  "guest_name": "John Doe",
  "guest_email": "john@example.com",
  "guest_phone": "+971501234567",
  "check_in": "2024-12-01",
  "check_out": "2024-12-05",
  "guests": 2,
  "special_requests": "Early check-in if possible"
}
```

Response includes calculated `total_amount` and `nights`.

### Update Booking

```http
PUT /api/bookings/{booking_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "confirmed",
  "internal_notes": "Confirmed via phone"
}
```

## Analytics API

### Get Analytics Dashboard

```http
GET /api/analytics
Authorization: Bearer {token}
```

Query Parameters:
- `period`: Time period (7days, 30days, 12months)

Response:
```json
{
  "total_revenue": 45000,
  "total_bookings": 23,
  "total_properties": 2,
  "occupancy_rate": 75,
  "average_rating": 4.8,
  "monthly_growth": 12.5,
  "booking_growth": 8.3,
  "monthlyData": [
    {"month": "Jan", "revenue": 5000, "bookings": 3},
    ...
  ],
  "propertyPerformance": [...],
  "market_insights": {...},
  "forecast": {...}
}
```

### Get Market Insights

```http
GET /api/analytics/market/{area}
Authorization: Bearer {token}
```

Response includes Dubai market data, seasonal trends, pricing recommendations.

## Financials API

### Get Financial Summary

```http
GET /api/financials/summary
Authorization: Bearer {token}
```

Query Parameters:
- `period`: 7days, 30days, 90days, 12months

Response:
```json
{
  "total_earnings": 45000,
  "platform_fees": 6750,
  "net_earnings": 38250,
  "pending_amount": 1500,
  "available_for_payout": 36750,
  "earnings_trend": [...]
}
```

### Get Transactions

```http
GET /api/v1/stripe/transactions
Authorization: Bearer {token}
```

Query Parameters:
- `limit`: Number of transactions (default: 50)

## Stripe Connect

### Get Account Status

```http
GET /api/v1/stripe/host/account-status
Authorization: Bearer {token}
```

Response:
```json
{
  "has_account": true,
  "details_submitted": true,
  "charges_enabled": true,
  "payouts_enabled": true,
  "requirements": []
}
```

### Create Stripe Account

```http
POST /api/v1/stripe/host/create-account
Authorization: Bearer {token}
```

Returns onboarding link.

### Get Onboarding Link

```http
GET /api/v1/stripe/host/onboarding-link
Authorization: Bearer {token}
```

### Get Payouts

```http
GET /api/v1/payouts/host-payouts
Authorization: Bearer {token}
```

## Messaging API

### Get Conversations

```http
GET /api/messages/conversations
Authorization: Bearer {token}
```

Query Parameters:
- `status`: active, archived

Response:
```json
[
  {
    "id": "uuid",
    "guest_name": "John Doe",
    "guest_email": "john@example.com",
    "property_title": "Luxury Apartment",
    "last_message": "When is check-in?",
    "last_message_at": "2024-11-24T10:00:00Z",
    "unread_count": 2,
    "status": "active"
  }
]
```

### Get Messages

```http
GET /api/messages/{conversation_id}
Authorization: Bearer {token}
```

Response:
```json
[
  {
    "id": "uuid",
    "content": "What time is check-in?",
    "is_from_host": false,
    "created_at": "2024-11-24T10:00:00Z",
    "read": true
  }
]
```

### Send Message

```http
POST /api/messages/{conversation_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "content": "Check-in is at 3 PM",
  "is_from_host": true
}
```

### Generate AI Response

```http
POST /api/messages/{conversation_id}/ai-response
Authorization: Bearer {token}
Content-Type: application/json

{
  "guest_message": "What time is check-in?"
}
```

Response:
```json
{
  "response": "Our standard check-in time is 3:00 PM. If you need early check-in, please let us know and we'll do our best to accommodate."
}
```

### Archive Conversation

```http
POST /api/messages/{conversation_id}/archive
Authorization: Bearer {token}
```

## User Profile API

### Get User Profile

```http
GET /api/users/profile
Authorization: Bearer {token}
```

Response:
```json
{
  "id": "uuid",
  "name": "John Smith",
  "email": "john@example.com",
  "phone_number": "+971501234567",
  "bio": "Property owner in Dubai",
  "avatar_url": "https://...",
  "role": "user",
  "is_superhost": false,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Update Profile

```http
PUT /api/users/profile
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "John Smith",
  "phone_number": "+971501234567",
  "bio": "Updated bio",
  "avatar_url": "https://..."
}
```

## Superhost API

### Check Eligibility

```http
GET /api/superhost/eligibility
Authorization: Bearer {token}
```

Response:
```json
{
  "eligible": true,
  "metrics": {
    "total_properties": 2,
    "total_bookings": 15,
    "average_rating": 4.8,
    "response_rate": 95,
    "cancellation_rate": 2
  },
  "requirements": {
    "min_properties": 1,
    "min_bookings": 5,
    "min_rating": 4.5,
    "min_response_rate": 90,
    "max_cancellation_rate": 5
  }
}
```

### Request Verification

```http
POST /api/superhost/request
Authorization: Bearer {token}
Content-Type: application/json

{
  "message": "I believe I meet all requirements for superhost status"
}
```

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message here"
}
```

HTTP Status Codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `429`: Rate Limited
- `500`: Internal Server Error

## Rate Limiting

- Default: 60 requests per minute
- AI endpoints: 200 requests per minute

Rate limit headers:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1635724800
```

## Webhooks

### Stripe Webhooks

Stripe events are processed at:
```
POST https://api.host.krib.ae/api/billing/webhook
```

Supported events:
- `payment_intent.succeeded`
- `account.updated`
- `payout.paid`

## Customer Platform Integration

### Overview

For external platforms (e.g., customer booking platform) to integrate with host dashboard.

### Flow

1. Customer platform has own auth system
2. Customer platform makes API calls on behalf of hosts
3. Use Supabase service role key for server-to-server auth
4. OR: Use host's token if they've connected their account

### Example Integration

```javascript
// Server-side only (service role key)
const { createClient } = require('@supabase/supabase-js')

const supabase = createClient(
  SUPABASE_URL,
  SUPABASE_SERVICE_ROLE_KEY  // Server-side only!
)

// Get host's properties
const { data: properties } = await supabase
  .from('properties')
  .select('*')
  .eq('user_id', host_user_id)

// Create booking via API
const response = await fetch('https://api.host.krib.ae/api/bookings', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${service_role_key}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    property_id: property_id,
    guest_name: 'Customer Name',
    ...
  })
})
```

### Security Notes

- **NEVER** expose service role key to client
- Validate all inputs on your server
- Use RLS policies for data security
- Rate limit your API calls

## Support

For API support or questions:
- Email: dev@krib.ae
- Documentation: https://docs.krib.ae

