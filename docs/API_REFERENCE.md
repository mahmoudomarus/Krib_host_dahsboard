# Host Dashboard API Reference

## Base URL
```
Production: https://api.host.krib.ae/api
```

## Authentication

All authenticated endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## API Endpoints

### Authentication

#### Health Check
```http
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-24T12:00:00Z",
  "version": "1.0.0"
}
```

---

### Users

#### Get Current User
```http
GET /users/me
```

**Headers**: `Authorization: Bearer {token}`

**Response**:
```json
{
  "id": "uuid",
  "email": "host@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "host",
  "avatar_url": "https://...",
  "bio": "Experienced host...",
  "phone_number": "+971501234567",
  "created_at": "2025-01-01T00:00:00Z"
}
```

#### Update User Profile
```http
PUT /users/me
```

**Headers**: `Authorization: Bearer {token}`

**Body**:
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "bio": "Updated bio",
  "phone_number": "+971501234567",
  "avatar_url": "https://..."
}
```

---

### Properties

#### List Properties
```http
GET /properties
```

**Headers**: `Authorization: Bearer {token}`

**Query Parameters**:
- `status` (optional): active, draft, inactive
- `sort` (optional): created_at, price_per_night, title

**Response**:
```json
[
  {
    "id": "uuid",
    "title": "Luxury Apartment",
    "address": "123 Marina Walk",
    "city": "Dubai Marina",
    "state": "Dubai",
    "country": "UAE",
    "latitude": 25.0797,
    "longitude": 55.1377,
    "property_type": "apartment",
    "bedrooms": 2,
    "bathrooms": 2,
    "max_guests": 4,
    "price_per_night": 800,
    "description": "Beautiful apartment...",
    "status": "active",
    "amenities": ["WiFi", "AC"],
    "images": ["https://..."],
    "rating": 4.8,
    "review_count": 25,
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

#### Get Single Property
```http
GET /properties/{property_id}
```

**Headers**: `Authorization: Bearer {token}`

**Response**: Single property object (same structure as list)

#### Create Property
```http
POST /properties
```

**Headers**: `Authorization: Bearer {token}`

**Body**:
```json
{
  "title": "Luxury Apartment in Dubai Marina",
  "address": "123 Marina Walk",
  "city": "Dubai Marina",
  "state": "Dubai",
  "country": "UAE",
  "latitude": 25.0797,
  "longitude": 55.1377,
  "property_type": "apartment",
  "bedrooms": 2,
  "bathrooms": 2,
  "max_guests": 4,
  "price_per_night": 800,
  "description": "Beautiful 2BR apartment...",
  "amenities": ["WiFi", "AC", "Kitchen", "Parking"],
  "images": ["https://..."]
}
```

**Response**: Created property object

#### Update Property
```http
PUT /properties/{property_id}
```

**Headers**: `Authorization: Bearer {token}`

**Body**: Partial property object (only fields to update)

**Response**: Updated property object

#### Delete Property
```http
DELETE /properties/{property_id}
```

**Headers**: `Authorization: Bearer {token}`

**Response**: `204 No Content`

---

### Bookings

#### List Bookings
```http
GET /bookings
```

**Headers**: `Authorization: Bearer {token}`

**Query Parameters**:
- `status` (optional): pending, confirmed, cancelled, completed
- `property_id` (optional): filter by property
- `start_date` (optional): YYYY-MM-DD
- `end_date` (optional): YYYY-MM-DD

**Response**:
```json
[
  {
    "id": "uuid",
    "property_id": "uuid",
    "property_title": "Luxury Apartment",
    "guest_id": "uuid",
    "guest_name": "John Doe",
    "guest_email": "guest@example.com",
    "check_in": "2025-12-01",
    "check_out": "2025-12-05",
    "total_amount": 3200.00,
    "platform_fee_amount": 480.00,
    "host_payout_amount": 2720.00,
    "status": "confirmed",
    "payment_status": "paid",
    "guest_count": 4,
    "created_at": "2025-11-24T00:00:00Z",
    "confirmed_at": "2025-11-24T01:00:00Z"
  }
]
```

#### Get Single Booking
```http
GET /bookings/{booking_id}
```

**Headers**: `Authorization: Bearer {token}`

**Response**: Single booking object (same structure as list)

#### Update Booking Status
```http
PATCH /bookings/{booking_id}/status
```

**Headers**: `Authorization: Bearer {token}`

**Body**:
```json
{
  "status": "confirmed"
}
```

**Valid Statuses**: `pending`, `confirmed`, `cancelled`, `completed`

**Response**: Updated booking object

---

### Financials

#### Get Financial Summary
```http
GET /financials/summary
```

**Headers**: `Authorization: Bearer {token}`

**Query Parameters**:
- `period` (required): 7days, 30days, 90days, 1year, all

**Response**:
```json
{
  "total_revenue": 25000.00,
  "pending_amount": 5000.00,
  "available_balance": 20000.00,
  "total_paid_out": 15000.00,
  "total_bookings": 45,
  "average_booking_value": 555.56,
  "revenue_trend": [
    { "date": "2025-11-01", "amount": 800.00 },
    { "date": "2025-11-02", "amount": 0.00 }
  ],
  "recent_transactions": [
    {
      "type": "booking_payment",
      "amount": 800.00,
      "booking_id": "uuid",
      "created_at": "2025-11-24T00:00:00Z"
    }
  ]
}
```

---

### Analytics

#### Get Analytics Dashboard
```http
GET /analytics
```

**Headers**: `Authorization: Bearer {token}`

**Response**:
```json
{
  "total_revenue": 25000.00,
  "total_bookings": 45,
  "total_properties": 3,
  "occupancy_rate": 75.5,
  "average_rating": 4.8,
  "revenue_trend": [...],
  "booking_trend": [...],
  "top_properties": [
    {
      "property_id": "uuid",
      "property_title": "Luxury Apartment",
      "revenue": 12000.00,
      "bookings": 20,
      "occupancy_rate": 85.0
    }
  ],
  "market_comparison": {
    "your_adr": 556.00,
    "market_adr": 500.00,
    "your_occupancy": 75.5,
    "market_occupancy": 70.0
  }
}
```

---

### Stripe Connect

#### Get Account Status
```http
GET /v1/stripe/host/account-status
```

**Headers**: `Authorization: Bearer {token}`

**Response**:
```json
{
  "has_account": true,
  "account_id": "acct_...",
  "charges_enabled": true,
  "payouts_enabled": true,
  "details_submitted": true,
  "requirements": [],
  "capabilities": {
    "transfers": "active"
  }
}
```

#### Create Stripe Account
```http
POST /v1/stripe/host/create-account
```

**Headers**: `Authorization: Bearer {token}`

**Response**:
```json
{
  "account_id": "acct_...",
  "onboarding_url": "https://connect.stripe.com/..."
}
```

#### Create Onboarding Link
```http
POST /v1/stripe/host/onboarding-link
```

**Headers**: `Authorization: Bearer {token}`

**Body**:
```json
{
  "refresh_url": "https://host.krib.ae/dashboard/financials",
  "return_url": "https://host.krib.ae/dashboard/financials"
}
```

**Response**:
```json
{
  "url": "https://connect.stripe.com/..."
}
```

---

### Payouts

#### Get Host Payouts
```http
GET /v1/payouts/host-payouts
```

**Headers**: `Authorization: Bearer {token}`

**Response**:
```json
{
  "available_balance": 5000.00,
  "pending_balance": 2000.00,
  "payouts": [
    {
      "id": "uuid",
      "amount": 3000.00,
      "status": "paid",
      "stripe_payout_id": "po_...",
      "payout_date": "2025-11-24",
      "created_at": "2025-11-24T00:00:00Z"
    }
  ],
  "next_payout_date": "2025-12-01",
  "payout_schedule": "weekly"
}
```

---

### Notifications

#### Get Notifications
```http
GET /v1/hosts/{host_id}/notifications
```

**Headers**: `Authorization: Bearer {token}`

**Query Parameters**:
- `limit` (optional, default 20): number of notifications
- `unread_only` (optional, default false): boolean
- `priority_filter` (optional): high, medium, low
- `type_filter` (optional): new_booking, payment_received, guest_message, urgent, booking_update

**Response**:
```json
{
  "success": true,
  "data": {
    "notifications": [
      {
        "id": "uuid",
        "type": "new_booking",
        "title": "New Booking Request",
        "message": "You have a new booking request...",
        "priority": "high",
        "is_read": false,
        "booking_id": "uuid",
        "property_id": "uuid",
        "action_url": "/dashboard/bookings/uuid",
        "created_at": "2025-11-24T00:00:00Z"
      }
    ],
    "unread_count": 5,
    "total": 50
  }
}
```

#### Mark Notification as Read
```http
PUT /v1/hosts/{host_id}/notifications/{notification_id}/read
```

**Headers**: `Authorization: Bearer {token}`

**Response**:
```json
{
  "success": true,
  "message": "Notification marked as read"
}
```

---

### Messages

#### Get Conversations
```http
GET /messages/conversations
```

**Headers**: `Authorization: Bearer {token}`

**Response**:
```json
{
  "success": true,
  "conversations": [
    {
      "id": "uuid",
      "property_id": "uuid",
      "guest_id": "uuid",
      "guest_name": "John Doe",
      "property_title": "Luxury Apartment",
      "last_message_at": "2025-11-24T12:00:00Z",
      "unread_count": 2,
      "is_archived": false
    }
  ]
}
```

#### Get Messages
```http
GET /messages/conversations/{conversation_id}/messages
```

**Headers**: `Authorization: Bearer {token}`

**Response**:
```json
{
  "success": true,
  "messages": [
    {
      "id": "uuid",
      "conversation_id": "uuid",
      "sender_type": "guest",
      "content": "What is the check-in time?",
      "is_read": true,
      "created_at": "2025-11-24T10:00:00Z"
    },
    {
      "id": "uuid",
      "conversation_id": "uuid",
      "sender_type": "host",
      "content": "Check-in is at 3 PM",
      "is_read": false,
      "created_at": "2025-11-24T10:30:00Z"
    }
  ]
}
```

#### Send Message
```http
POST /messages/send
```

**Headers**: `Authorization: Bearer {token}`

**Body**:
```json
{
  "conversation_id": "uuid",
  "message": "Thank you for your inquiry!"
}
```

**Response**:
```json
{
  "success": true,
  "message": {
    "id": "uuid",
    "content": "Thank you for your inquiry!",
    "created_at": "2025-11-24T12:00:00Z"
  }
}
```

#### Generate AI Response
```http
POST /messages/generate-ai-response
```

**Headers**: `Authorization: Bearer {token}`

**Body**:
```json
{
  "conversation_id": "uuid",
  "guest_message": "What is the check-in time?"
}
```

**Response**:
```json
{
  "success": true,
  "response": "Check-in time is 3:00 PM. Our property manager will meet you at the entrance to provide keys and a brief tour."
}
```

---

### Reviews

#### Get All Reviews
```http
GET /v1/reviews
```

**Headers**: `Authorization: Bearer {token}`

**Query Parameters**:
- `page` (optional, default 1): page number
- `page_size` (optional, default 20): items per page
- `property_id` (optional): filter by property

**Response**:
```json
{
  "reviews": [
    {
      "id": "uuid",
      "booking_id": "uuid",
      "property_id": "uuid",
      "guest_id": "uuid",
      "guest_name": "John Doe",
      "property_title": "Luxury Apartment",
      "rating": 5.0,
      "cleanliness_rating": 5.0,
      "communication_rating": 5.0,
      "checkin_rating": 5.0,
      "location_rating": 5.0,
      "comment": "Amazing stay! Highly recommend.",
      "host_response": "Thank you!",
      "responded_at": "2025-11-24T12:00:00Z",
      "created_at": "2025-11-24T10:00:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 20,
  "average_rating": 4.8
}
```

#### Get Property Reviews
```http
GET /v1/properties/{property_id}/reviews
```

**Headers**: `Authorization: Bearer {token}`

**Response**: Same structure as all reviews

#### Respond to Review
```http
POST /v1/reviews/{review_id}/respond
```

**Headers**: `Authorization: Bearer {token}`

**Body**:
```json
{
  "response": "Thank you for your wonderful review! We hope to host you again."
}
```

**Response**:
```json
{
  "success": true,
  "message": "Response added successfully",
  "review_id": "uuid"
}
```

#### Get Review Statistics
```http
GET /v1/reviews/stats
```

**Headers**: `Authorization: Bearer {token}`

**Response**:
```json
{
  "total_reviews": 50,
  "average_rating": 4.7,
  "pending_responses": 3,
  "ratings_breakdown": {
    "5": 35,
    "4": 10,
    "3": 3,
    "2": 1,
    "1": 1
  }
}
```

---

### Superhost

#### Get Eligibility
```http
GET /superhost/eligibility
```

**Headers**: `Authorization: Bearer {token}`

**Response**:
```json
{
  "eligible": true,
  "metrics": {
    "total_bookings": 50,
    "average_rating": 4.8,
    "response_rate": 95.0,
    "cancellation_rate": 2.0,
    "total_revenue": 25000.00
  },
  "requirements": {
    "total_bookings": {
      "required": 10,
      "current": 50,
      "met": true
    },
    "average_rating": {
      "required": 4.7,
      "current": 4.8,
      "met": true
    },
    "response_rate": {
      "required": 90.0,
      "current": 95.0,
      "met": true
    },
    "cancellation_rate": {
      "required": 5.0,
      "current": 2.0,
      "met": true
    }
  },
  "reasons": []
}
```

#### Request Verification
```http
POST /superhost/request-verification
```

**Headers**: `Authorization: Bearer {token}`

**Body**:
```json
{
  "reason": "I have maintained excellent ratings and guest satisfaction..."
}
```

**Response**:
```json
{
  "success": true,
  "request_id": "uuid",
  "status": "pending",
  "submitted_at": "2025-11-24T12:00:00Z"
}
```

#### Get Verification Status
```http
GET /superhost/verification-status
```

**Headers**: `Authorization: Bearer {token}`

**Response**:
```json
{
  "has_request": true,
  "status": "pending",
  "requested_at": "2025-11-24T12:00:00Z",
  "reviewed_at": null,
  "admin_notes": null
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not authorized to access this resource"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "price_per_night"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

- **Default**: 1000 requests per hour
- **Headers**:
  - `X-RateLimit-Limit`: Total requests allowed
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Timestamp when limit resets

---

## Webhooks (Stripe)

### Endpoint
```
POST /api/billing/webhook
```

### Events Handled
- `payment_intent.succeeded`
- `payment_intent.payment_failed`
- `charge.dispute.created`
- `payout.paid`
- `payout.failed`
- `account.updated`

### Webhook Signature Verification
Required header: `Stripe-Signature`

---

## Data Types

### Property Status
- `draft` - Not published
- `active` - Live and bookable
- `inactive` - Unlisted

### Booking Status
- `pending` - Awaiting host confirmation
- `confirmed` - Host confirmed
- `in_progress` - Guest checked in
- `completed` - Guest checked out
- `cancelled` - Booking cancelled

### Payment Status
- `pending` - Payment not processed
- `paid` - Payment successful
- `failed` - Payment failed
- `refunded` - Payment refunded

### Notification Types
- `new_booking` - New booking request
- `payment_received` - Payment confirmed
- `guest_message` - New message from guest
- `urgent` - Urgent action required
- `booking_update` - Booking status changed

### Priority Levels
- `high` - Requires immediate attention
- `medium` - Normal priority
- `low` - Informational

---

## Pagination

**Request**:
```http
GET /endpoint?page=2&page_size=20
```

**Response Headers**:
```
X-Total-Count: 150
X-Page: 2
X-Page-Size: 20
X-Total-Pages: 8
```

---

## Versioning

Current version: `v1`

API versioning in URL: `/api/v1/endpoint`

---

## SDK Examples

### JavaScript/TypeScript
```javascript
const API_URL = 'https://api.host.krib.ae/api';
const token = localStorage.getItem('auth_token');

const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
};

// Get properties
const properties = await fetch(`${API_URL}/properties`, { headers })
  .then(res => res.json());

// Create property
const newProperty = await fetch(`${API_URL}/properties`, {
  method: 'POST',
  headers,
  body: JSON.stringify(propertyData)
}).then(res => res.json());
```

### Python
```python
import requests

API_URL = 'https://api.host.krib.ae/api'
token = 'your_auth_token'

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# Get properties
response = requests.get(f'{API_URL}/properties', headers=headers)
properties = response.json()

# Create property
response = requests.post(
    f'{API_URL}/properties',
    headers=headers,
    json=property_data
)
new_property = response.json()
```

---

## Support

- **Documentation**: https://docs.krib.ae
- **API Status**: https://status.krib.ae
- **Support Email**: support@krib.ae

