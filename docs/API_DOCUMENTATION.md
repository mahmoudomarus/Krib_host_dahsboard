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

External platforms (customer booking apps, marketplace platforms) can integrate with the Host Dashboard to enable:
- Property discovery and booking
- Guest-host messaging
- Review submission
- Real-time notifications

### Authentication Approaches

**Option 1: Shared Supabase Auth (Recommended)**
- Customer and host both authenticate via same Supabase instance
- Customer gets their own JWT token
- RLS policies ensure data isolation
- Enables real-time subscriptions

**Option 2: Service Role Key (Admin Operations)**
- Use for server-to-server operations
- Admin access to all data
- Bypass RLS policies (use carefully)
- Required for super admin operations

### Customer Platform Integration Patterns

#### Pattern 1: Direct Database Access (Shared Supabase)

```javascript
// Customer Platform (Frontend)
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  SUPABASE_URL,
  SUPABASE_ANON_KEY  // Safe for frontend
)

// Authenticate customer
const { data: authData } = await supabase.auth.signUp({
  email: 'customer@example.com',
  password: 'secure_password'
})

// Customer browses active properties
const { data: properties } = await supabase
  .from('properties')
  .select('*')
  .eq('status', 'active')
  .order('created_at', { ascending: false });

// Customer creates booking
const { data: booking } = await supabase
  .from('bookings')
  .insert({
    property_id: selectedProperty.id,
    guest_id: authData.user.id,
    check_in: '2025-12-01',
    check_out: '2025-12-05',
    guests: 2,
    status: 'pending'
  })
  .select()
  .single();

// Customer sends message to host
const { data: message } = await supabase
  .from('messages')
  .insert({
    conversation_id: conversationId,
    sender_type: 'guest',
    sender_id: authData.user.id,
    content: 'Is early check-in available?',
    is_read: false
  })
  .select()
  .single();

// Customer submits review after stay
const { data: review } = await supabase
  .from('reviews')
  .insert({
    booking_id: completedBooking.id,
    property_id: completedBooking.property_id,
    guest_id: authData.user.id,
    rating: 5,
    comment: 'Amazing property!'
  })
  .select()
  .single();
```

#### Pattern 2: Host Dashboard API Proxy

```javascript
// Customer Platform (Backend) proxies to Host Dashboard API
const customerBookProperty = async (req, res) => {
  // Validate customer is authenticated
  const customerId = req.user.id;
  
  // Map customer data to host API format
  const bookingData = {
    property_id: req.body.propertyId,
    guest_name: req.user.name,
    guest_email: req.user.email,
    guest_phone: req.user.phone,
    check_in: req.body.checkIn,
    check_out: req.body.checkOut,
    guests: req.body.guestCount
  };

  // Call Host Dashboard API
  const response = await fetch('https://api.host.krib.ae/api/bookings', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${HOST_API_TOKEN}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(bookingData)
  });

  const booking = await response.json();
  res.json(booking);
};
```

#### Pattern 3: Real-time Updates (Supabase Subscriptions)

```javascript
// Customer Platform: Subscribe to booking updates
supabase
  .channel('customer-bookings')
  .on('postgres_changes',
    {
      event: 'UPDATE',
      schema: 'public',
      table: 'bookings',
      filter: `guest_id=eq.${customerId}`
    },
    (payload) => {
      // Booking status changed (host confirmed, cancelled, etc.)
      updateBookingUI(payload.new);
      showNotification(`Booking ${payload.new.status}`);
    }
  )
  .subscribe();

// Subscribe to host messages
supabase
  .channel('customer-messages')
  .on('postgres_changes',
    {
      event: 'INSERT',
      schema: 'public',
      table: 'messages',
      filter: `conversation_id=eq.${conversationId}`
    },
    (payload) => {
      if (payload.new.sender_type === 'host') {
        displayNewMessage(payload.new);
        playNotificationSound();
      }
    }
  )
  .subscribe();
```

### Customer Platform Features Implementation

#### 1. Property Browsing
```javascript
// Search and filter properties
const searchProperties = async (filters) => {
  let query = supabase
    .from('properties')
    .select('*')
    .eq('status', 'active');

  if (filters.city) {
    query = query.eq('city', filters.city);
  }
  if (filters.minPrice && filters.maxPrice) {
    query = query.gte('price_per_night', filters.minPrice)
                 .lte('price_per_night', filters.maxPrice);
  }
  if (filters.guests) {
    query = query.gte('max_guests', filters.guests);
  }
  if (filters.bedrooms) {
    query = query.gte('bedrooms', filters.bedrooms);
  }

  const { data } = await query;
  return data;
};
```

#### 2. Guest-Host Messaging
```javascript
// Create conversation when customer inquires
const startConversation = async (propertyId, guestId, initialMessage) => {
  // Get host_id from property
  const { data: property } = await supabase
    .from('properties')
    .select('user_id')
    .eq('id', propertyId)
    .single();

  // Create conversation
  const { data: conversation } = await supabase
    .from('conversations')
    .insert({
      property_id: propertyId,
      guest_id: guestId,
      host_id: property.user_id
    })
    .select()
    .single();

  // Send first message
  await supabase
    .from('messages')
    .insert({
      conversation_id: conversation.id,
      sender_type: 'guest',
      sender_id: guestId,
      content: initialMessage,
      is_read: false
    });

  return conversation;
};

// Load conversation messages
const getMessages = async (conversationId) => {
  const { data } = await supabase
    .from('messages')
    .select('*')
    .eq('conversation_id', conversationId)
    .order('created_at', { ascending: true });

  return data;
};
```

#### 3. Review Submission
```javascript
// Check if customer can review
const canReview = async (bookingId, guestId) => {
  const { data: booking } = await supabase
    .from('bookings')
    .select('status, check_out, guest_id')
    .eq('id', bookingId)
    .single();

  // Must be guest's booking, completed, and past check-out date
  if (booking.guest_id !== guestId) return false;
  if (booking.status !== 'completed') return false;
  if (new Date(booking.check_out) > new Date()) return false;

  // Check if not already reviewed
  const { data: existing } = await supabase
    .from('reviews')
    .select('id')
    .eq('booking_id', bookingId)
    .limit(1);

  return existing.length === 0;
};

// Submit review
const submitReview = async (reviewData) => {
  const { data: review } = await supabase
    .from('reviews')
    .insert({
      booking_id: reviewData.bookingId,
      property_id: reviewData.propertyId,
      guest_id: reviewData.guestId,
      guest_name: reviewData.guestName,
      guest_email: reviewData.guestEmail,
      rating: reviewData.overallRating,
      cleanliness_rating: reviewData.cleanliness,
      communication_rating: reviewData.communication,
      accuracy_rating: reviewData.accuracy,
      location_rating: reviewData.location,
      value_rating: reviewData.value,
      comment: reviewData.comment
    })
    .select()
    .single();

  // Property rating automatically updates via DB trigger
  return review;
};
```

#### 4. Customer Notifications
```javascript
// Create customer notification system
const sendCustomerNotification = async (notification) => {
  // Insert into customer_notifications table
  const { data } = await supabase
    .from('customer_notifications')
    .insert({
      guest_id: notification.guestId,
      type: notification.type,
      title: notification.title,
      message: notification.message,
      booking_id: notification.bookingId,
      action_url: notification.actionUrl,
      priority: notification.priority || 'medium'
    })
    .select()
    .single();

  return data;
};

// Subscribe to customer notifications
supabase
  .channel('guest-notifications')
  .on('postgres_changes',
    {
      event: 'INSERT',
      schema: 'public',
      table: 'customer_notifications',
      filter: `guest_id=eq.${guestId}`
    },
    (payload) => {
      displayNotification(payload.new);
    }
  )
  .subscribe();
```

### Security Best Practices

#### Row-Level Security (RLS)

The shared database uses RLS to ensure customers only access their data:

```sql
-- Customers see only their bookings
CREATE POLICY "Guests view own bookings"
ON bookings FOR SELECT
USING (auth.uid() = guest_id);

-- Customers see only their conversations
CREATE POLICY "Guests view own conversations"
ON conversations FOR SELECT
USING (auth.uid() = guest_id);

-- Customers see only their reviews
CREATE POLICY "Guests view own reviews"
ON reviews FOR SELECT
USING (auth.uid() = guest_id);

-- Everyone can view active properties
CREATE POLICY "Public view active properties"
ON properties FOR SELECT
USING (status = 'active');
```

#### API Security Checklist

- [ ] Never expose service role key to frontend
- [ ] Validate all user inputs server-side
- [ ] Use Supabase RLS policies for data access control
- [ ] Implement rate limiting (60 req/min default)
- [ ] Verify JWT tokens on every request
- [ ] Sanitize user-generated content (messages, reviews)
- [ ] Use HTTPS only for all API calls
- [ ] Log all cross-platform interactions

### Example Customer Platform Architecture

```
Customer Platform Frontend (React/Vue/Next.js)
  ↓ (Supabase ANON_KEY auth)
Supabase Database (Shared with Host Dashboard)
  ↓ (RLS policies enforce access control)
Supabase Realtime (subscriptions for live updates)
  ↓
Host Dashboard API (optional, for complex operations)
  ↓
Host Dashboard Frontend (receives notifications, messages)
```

### Testing Integration

Use the provided SQL scripts and guides:
- `test_booking_flow.sql` - Creates test bookings and reviews
- `BOOKING_FLOW_TESTING.md` - Step-by-step testing guide
- `API_TESTING_GUIDE.md` - API endpoint testing

### Security Notes

- **NEVER** expose service role key to client
- Validate all inputs on your server
- Use RLS policies for data security
- Rate limit your API calls
- Customer Platform should have separate auth for admin operations

## Support

For API support or questions:
- Email: dev@krib.ae
- Documentation: https://docs.krib.ae

