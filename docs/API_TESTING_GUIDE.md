# API Testing Guide - Krib Host Dashboard

## Base URLs
- **Production API**: `https://api.host.krib.ae/api`
- **Frontend**: `https://host.krib.ae`

---

## Authentication Flow

### 1. Sign Up / Login
```bash
# Sign up via Supabase Auth (handled by frontend)
# Returns: auth_token (JWT)
```

**Store Token**: Save `auth_token` for subsequent requests

**Headers for Authenticated Requests**:
```json
{
  "Authorization": "Bearer YOUR_AUTH_TOKEN",
  "Content-Type": "application/json"
}
```

---

## Core API Endpoints Testing

### Health Check
```bash
curl https://api.host.krib.ae/api/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-24T...",
  "version": "1.0.0"
}
```

---

## 1. User Profile Management

### Get Current User
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.host.krib.ae/api/users/me
```

**Expected Response**:
```json
{
  "id": "uuid",
  "email": "host@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "host",
  "avatar_url": "https://...",
  "bio": "...",
  "phone_number": "+971...",
  "created_at": "2025-..."
}
```

### Update Profile
```bash
curl -X PUT -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Smith",
    "bio": "Experienced host in Dubai",
    "phone_number": "+971501234567"
  }' \
  https://api.host.krib.ae/api/users/me
```

---

## 2. Properties Management

### Create Property
```bash
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
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
    "description": "Beautiful 2BR apartment with marina views",
    "amenities": ["WiFi", "AC", "Kitchen", "Parking"],
    "images": ["https://...", "https://..."]
  }' \
  https://api.host.krib.ae/api/properties
```

**Expected Response**:
```json
{
  "id": "property-uuid",
  "title": "Luxury Apartment in Dubai Marina",
  "status": "draft",
  "created_at": "2025-...",
  ...
}
```

### Get All Properties
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.host.krib.ae/api/properties
```

### Get Single Property
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.host.krib.ae/api/properties/PROPERTY_ID
```

### Update Property
```bash
curl -X PUT -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "price_per_night": 850,
    "status": "active"
  }' \
  https://api.host.krib.ae/api/properties/PROPERTY_ID
```

### Delete Property
```bash
curl -X DELETE -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.host.krib.ae/api/properties/PROPERTY_ID
```

---

## 3. Bookings Management

### Get All Bookings
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.host.krib.ae/api/bookings
```

**Query Parameters**:
- `status`: pending, confirmed, cancelled, completed
- `property_id`: filter by property
- `start_date`: filter from date (YYYY-MM-DD)
- `end_date`: filter to date (YYYY-MM-DD)

### Get Single Booking
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.host.krib.ae/api/bookings/BOOKING_ID
```

### Update Booking Status
```bash
curl -X PATCH -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "confirmed"
  }' \
  https://api.host.krib.ae/api/bookings/BOOKING_ID/status
```

**Valid Statuses**: `pending`, `confirmed`, `cancelled`, `completed`

---

## 4. Financial APIs

### Get Financial Summary
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.host.krib.ae/api/financials/summary?period=30days"
```

**Periods**: `7days`, `30days`, `90days`, `1year`, `all`

**Expected Response**:
```json
{
  "total_revenue": 15000,
  "pending_amount": 2000,
  "available_balance": 13000,
  "total_bookings": 25,
  "average_booking_value": 600,
  "revenue_trend": [...]
}
```

### Get Host Payouts
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.host.krib.ae/api/v1/payouts/host-payouts
```

---

## 5. Analytics APIs

### Get Analytics Dashboard
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.host.krib.ae/api/analytics
```

**Expected Response**:
```json
{
  "total_revenue": 15000,
  "total_bookings": 25,
  "occupancy_rate": 75.5,
  "average_rating": 4.8,
  "revenue_trend": [...],
  "booking_trend": [...],
  "top_properties": [...]
}
```

### Get Market Comparison
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.host.krib.ae/api/analytics/market-comparison?area=Dubai%20Marina"
```

---

## 6. Stripe Connect

### Get Account Status
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.host.krib.ae/api/v1/stripe/host/account-status
```

**Expected Response**:
```json
{
  "has_account": true,
  "account_id": "acct_...",
  "charges_enabled": true,
  "payouts_enabled": true,
  "details_submitted": true,
  "requirements": []
}
```

### Create Stripe Account
```bash
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.host.krib.ae/api/v1/stripe/host/create-account
```

### Create Onboarding Link
```bash
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_url": "https://host.krib.ae/dashboard/financials",
    "return_url": "https://host.krib.ae/dashboard/financials"
  }' \
  https://api.host.krib.ae/api/v1/stripe/host/onboarding-link
```

---

## 7. Notifications

### Get Notifications
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.host.krib.ae/api/v1/hosts/USER_ID/notifications?limit=20"
```

**Query Parameters**:
- `limit`: number of notifications (default 20)
- `unread_only`: boolean (default false)
- `priority_filter`: high, medium, low
- `type_filter`: new_booking, payment_received, guest_message, urgent, booking_update

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "notifications": [
      {
        "id": "uuid",
        "type": "new_booking",
        "title": "New Booking Request",
        "message": "You have a new booking...",
        "priority": "high",
        "is_read": false,
        "created_at": "2025-11-24T..."
      }
    ],
    "unread_count": 5,
    "total": 50
  }
}
```

### Mark Notification as Read
```bash
curl -X PUT -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.host.krib.ae/api/v1/hosts/USER_ID/notifications/NOTIFICATION_ID/read
```

---

## 8. Messages

### Get Conversations
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.host.krib.ae/api/messages/conversations
```

**Expected Response**:
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
      "last_message_at": "2025-11-24T...",
      "unread_count": 2
    }
  ]
}
```

### Get Messages in Conversation
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.host.krib.ae/api/messages/conversations/CONVERSATION_ID/messages
```

### Send Message
```bash
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "uuid",
    "message": "Thank you for your inquiry!"
  }' \
  https://api.host.krib.ae/api/messages/send
```

### Generate AI Response
```bash
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "uuid",
    "guest_message": "What is the check-in time?"
  }' \
  https://api.host.krib.ae/api/messages/generate-ai-response
```

---

## 9. Reviews

### Get All Reviews
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.host.krib.ae/api/v1/reviews?page=1&page_size=20"
```

**Query Parameters**:
- `page`: page number (default 1)
- `page_size`: items per page (default 20)
- `property_id`: filter by property (optional)

### Get Property Reviews
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.host.krib.ae/api/v1/properties/PROPERTY_ID/reviews
```

### Respond to Review
```bash
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "response": "Thank you for your wonderful review!"
  }' \
  https://api.host.krib.ae/api/v1/reviews/REVIEW_ID/respond
```

### Get Review Statistics
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.host.krib.ae/api/v1/reviews/stats
```

**Expected Response**:
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

## 10. Superhost System

### Get Superhost Eligibility
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.host.krib.ae/api/superhost/eligibility
```

**Expected Response**:
```json
{
  "eligible": true,
  "metrics": {
    "total_bookings": 50,
    "average_rating": 4.8,
    "response_rate": 95,
    "cancellation_rate": 2
  },
  "requirements": {
    "total_bookings": { "required": 10, "current": 50, "met": true },
    "average_rating": { "required": 4.7, "current": 4.8, "met": true }
  }
}
```

### Request Superhost Verification
```bash
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "I have maintained high standards..."
  }' \
  https://api.host.krib.ae/api/superhost/request-verification
```

### Get Verification Status
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.host.krib.ae/api/superhost/verification-status
```

---

## Testing Workflow

### 1. Complete Booking Flow Test
```bash
# Step 1: Create property
# Step 2: Set property to active status
# Step 3: Simulate booking creation (via customer platform)
# Step 4: Check notification received
# Step 5: Confirm booking
# Step 6: Check payment notification
# Step 7: Complete booking
```

### 2. Notification Test
```bash
# Step 1: Run test_notifications.sql in Supabase
# Step 2: Check GET /api/v1/hosts/{user_id}/notifications
# Step 3: Mark one as read
# Step 4: Verify unread count decreased
# Step 5: Check email received (if RESEND_API_KEY configured)
```

### 3. Reviews Test
```bash
# Step 1: Run test_reviews.sql in Supabase
# Step 2: GET /api/v1/reviews
# Step 3: Respond to a review
# Step 4: Check stats endpoint
# Step 5: Run cleanup_test_data.sql
```

### 4. Messaging Test
```bash
# Step 1: Create test conversation
# Step 2: Send guest message
# Step 3: Generate AI response
# Step 4: Send host reply
# Step 5: Check conversation list
```

---

## Error Handling

### Common Error Responses

**401 Unauthorized**:
```json
{
  "detail": "Not authenticated"
}
```

**403 Forbidden**:
```json
{
  "detail": "Not authorized to access this resource"
}
```

**404 Not Found**:
```json
{
  "detail": "Resource not found"
}
```

**422 Validation Error**:
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

**500 Internal Server Error**:
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

- Default: 1000 requests per hour per user
- Configurable via `RATE_LIMIT_*` environment variables
- Header: `X-RateLimit-Remaining`

---

## Testing Tools Recommendation

1. **Postman**: Import collection (create from this guide)
2. **curl**: Command-line testing
3. **Python requests**: Automated testing
4. **pytest**: Unit and integration tests

---

## Next Steps

1. Test each endpoint systematically
2. Verify error handling
3. Test edge cases
4. Load testing for production readiness
5. Security audit

