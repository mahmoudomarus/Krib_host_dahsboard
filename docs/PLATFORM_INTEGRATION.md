# Platform Integration Guide

## Overview

The Krib ecosystem consists of three platforms:
1. **Host Dashboard** - Property management for hosts
2. **Customer Platform** - Booking and search for guests
3. **Super Admin Platform** - System administration and oversight

---

## Architecture

```
┌─────────────────────┐
│  Customer Platform  │
│   (Guest Bookings)  │
└──────────┬──────────┘
           │
           ├─────────────► Shared Supabase Database
           │
┌──────────┴──────────┐
│  Host Dashboard     │
│ (Property Mgmt)     │
└──────────┬──────────┘
           │
           ├─────────────► Shared Supabase Database
           │
┌──────────┴──────────┐
│ Super Admin Panel   │
│ (System Admin)      │
└─────────────────────┘
```

---

## Shared Database Schema

All platforms share the same Supabase database with these core tables:

### Core Tables
- `users` - All users (hosts, guests, admins)
- `properties` - Property listings
- `bookings` - Booking records
- `reviews` - Guest reviews
- `financial_transactions` - Payment records
- `host_payouts` - Payout records
- `host_notifications` - Host notifications
- `conversations` - Guest-host messages
- `messages` - Message content
- `superhost_verification_requests` - Superhost requests

---

## Integration Points

### 1. Customer Platform → Host Dashboard

#### Booking Creation Flow

**Customer Platform Creates Booking**:
```sql
INSERT INTO bookings (
  property_id,
  guest_id,
  check_in,
  check_out,
  total_amount,
  status,
  guest_count
) VALUES (...);
```

**Host Dashboard Receives**:
- Automatic notification created
- Real-time update via Supabase subscription
- Email notification sent
- Dashboard shows new booking

**Host Dashboard API Endpoint**:
```
GET /api/bookings
POST /api/bookings/{booking_id}/status
```

#### Guest Message to Host

**Customer Platform Creates Conversation**:

When a customer views a property and wants to inquire, create a conversation:

```sql
-- Check if conversation already exists
SELECT id FROM conversations
WHERE property_id = $1 AND guest_id = $2 AND is_archived = false
LIMIT 1;

-- If not exists, create new conversation
INSERT INTO conversations (property_id, guest_id, host_id)
VALUES (
  property_id,
  guest_id,
  (SELECT user_id FROM properties WHERE id = property_id)
) RETURNING id;

-- Send initial message
INSERT INTO messages (conversation_id, sender_type, sender_id, content, is_read)
VALUES (conversation_id, 'guest', guest_id, message_content, false);
```

**Customer Platform API Integration**:

```javascript
// Example: Customer sends inquiry about property
const sendPropertyInquiry = async (propertyId, guestId, message) => {
  // Create or get conversation
  const { data: conversations } = await supabase
    .from('conversations')
    .select('id')
    .eq('property_id', propertyId)
    .eq('guest_id', guestId)
    .eq('is_archived', false)
    .limit(1);

  let conversationId;
  
  if (conversations.length === 0) {
    // Create new conversation
    const { data: newConv } = await supabase
      .from('conversations')
      .insert({
        property_id: propertyId,
        guest_id: guestId,
        host_id: hostId // Get from properties table
      })
      .select('id')
      .single();
    
    conversationId = newConv.id;
  } else {
    conversationId = conversations[0].id;
  }

  // Send message
  const { data: sentMessage } = await supabase
    .from('messages')
    .insert({
      conversation_id: conversationId,
      sender_type: 'guest',
      sender_id: guestId,
      content: message,
      is_read: false
    })
    .select()
    .single();

  return sentMessage;
};
```

**Host Dashboard Receives**:
- GET `/api/messages/conversations` - Lists all conversations
- GET `/api/messages/conversations/{id}/messages` - Message history
- POST `/api/messages/generate-ai-response` - AI-powered reply
- POST `/api/messages/send` - Send response

**Real-time Updates**:
```javascript
// Customer Platform: Listen for host replies
supabase
  .channel('guest-messages')
  .on('postgres_changes',
    {
      event: 'INSERT',
      schema: 'public',
      table: 'messages',
      filter: `conversation_id=eq.${conversationId}`
    },
    (payload) => {
      if (payload.new.sender_type === 'host' || payload.new.sender_type === 'ai') {
        // Display new message from host
        displayNewMessage(payload.new);
        // Optionally send push notification to customer
        sendPushNotification(payload.new);
      }
    }
  )
  .subscribe();
```

#### Payment Completion

**Customer Platform** (via Stripe):
```
stripe.paymentIntents.create({
  amount,
  currency: 'AED',
  application_fee_amount: platform_fee,
  transfer_data: {
    destination: host_stripe_account
  }
})
```

**Host Dashboard Receives**:
- Webhook updates `bookings` table
- Creates `financial_transactions` record
- Sends notification to host
- Updates available balance

---

### 2. Host Dashboard → Customer Platform

#### Property Listing

**Host Creates/Updates Property**:
```
POST /api/properties
PUT /api/properties/{id}
```

**Customer Platform Access**:
```sql
SELECT * FROM properties
WHERE status = 'active'
  AND user_id = host_user_id;
```

**RLS Ensures**:
- Customers see only active properties
- Hosts see only their properties
- Admins see all properties

#### Availability Management

**Host Updates Calendar**:
```sql
UPDATE properties
SET availability_calendar = jsonb_set(...)
WHERE id = property_id;
```

**Customer Platform Checks**:
```sql
SELECT * FROM properties
WHERE id = property_id
  AND NOT EXISTS (
    SELECT 1 FROM bookings
    WHERE property_id = properties.id
      AND status IN ('confirmed', 'pending')
      AND daterange(check_in, check_out) && daterange($1, $2)
  );
```

#### Pricing Updates

**Host Updates Price**:
```
PUT /api/properties/{id}
{ "price_per_night": 850 }
```

**Customer Platform**:
- Immediately reflects new pricing
- No cache invalidation needed (direct DB query)

---

#### Customer Reviews After Stay

**Customer Platform Review Submission**:

After a booking is completed, allow guests to submit reviews:

```javascript
// Check if guest can review (booking completed, not already reviewed)
const canReview = async (bookingId, guestId) => {
  const { data: booking } = await supabase
    .from('bookings')
    .select('status, check_out, guest_id')
    .eq('id', bookingId)
    .single();

  if (booking.guest_id !== guestId) return false;
  if (booking.status !== 'completed') return false;
  if (new Date(booking.check_out) > new Date()) return false;

  // Check if already reviewed
  const { data: existingReview } = await supabase
    .from('reviews')
    .select('id')
    .eq('booking_id', bookingId)
    .limit(1);

  return existingReview.length === 0;
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
      rating: reviewData.rating,
      cleanliness_rating: reviewData.cleanliness,
      communication_rating: reviewData.communication,
      accuracy_rating: reviewData.accuracy,
      location_rating: reviewData.location,
      value_rating: reviewData.value,
      comment: reviewData.comment
    })
    .select()
    .single();

  // This triggers automatic property rating update via DB trigger
  return review;
};
```

**Review Display on Property Pages**:
```javascript
// Customer Platform: Show reviews on property listing
const getPropertyReviews = async (propertyId, page = 1, limit = 10) => {
  const { data: reviews, count } = await supabase
    .from('reviews')
    .select('*, properties(title)', { count: 'exact' })
    .eq('property_id', propertyId)
    .order('created_at', { ascending: false })
    .range((page - 1) * limit, page * limit - 1);

  return { reviews, total: count };
};
```

**Host Dashboard Integration**:
- GET `/api/v1/reviews` - Host sees all reviews
- POST `/api/v1/reviews/{review_id}/respond` - Host responds to review
- Review statistics automatically update property rating

**Customer Platform Shows**:
- Property average rating (star display)
- Individual review cards with ratings breakdown
- Host responses to reviews
- Verified booking badge (review tied to actual stay)
- Review submission form after checkout

---

#### Customer Notifications Integration

**Notification Types for Customers**:

```javascript
// Customer Platform: Subscribe to booking notifications
const subscribeToBookingUpdates = (guestId) => {
  supabase
    .channel('guest-notifications')
    .on('postgres_changes',
      {
        event: 'INSERT',
        schema: 'public',
        table: 'bookings',
        filter: `guest_id=eq.${guestId}`
      },
      (payload) => {
        // New booking created
        sendNotification({
          title: 'Booking Confirmed',
          message: `Your booking at ${payload.new.property_title} is confirmed`,
          action_url: `/bookings/${payload.new.id}`
        });
      }
    )
    .on('postgres_changes',
      {
        event: 'UPDATE',
        schema: 'public',
        table: 'bookings',
        filter: `guest_id=eq.${guestId}`
      },
      (payload) => {
        // Booking status changed
        const status = payload.new.status;
        let notificationMessage;
        
        switch(status) {
          case 'confirmed':
            notificationMessage = 'Your booking has been confirmed by the host';
            break;
          case 'cancelled':
            notificationMessage = 'Your booking has been cancelled';
            break;
          case 'completed':
            notificationMessage = 'Thank you for your stay! Please leave a review';
            break;
        }
        
        sendNotification({
          title: 'Booking Update',
          message: notificationMessage,
          action_url: `/bookings/${payload.new.id}`
        });
      }
    )
    .subscribe();
};
```

**Customer Notification Scenarios**:

1. **Booking Confirmed by Host**:
```javascript
// Automatically triggered when host confirms via Host Dashboard
// Customer Platform receives real-time update and displays notification
```

2. **Payment Successful**:
```javascript
// After Stripe payment succeeds
// Both customer and host receive notifications
```

3. **Host Sends Message**:
```javascript
// Real-time message notification in Customer Platform
supabase
  .channel('messages')
  .on('postgres_changes',
    {
      event: 'INSERT',
      schema: 'public',
      table: 'messages',
      filter: `conversation_id=eq.${conversationId}`
    },
    (payload) => {
      if (payload.new.sender_type === 'host') {
        sendNotification({
          title: 'New Message',
          message: `${hostName}: ${payload.new.content.substring(0, 50)}...`,
          action_url: `/messages/${conversationId}`
        });
      }
    }
  )
  .subscribe();
```

4. **Check-in Reminder** (24 hours before):
```javascript
// Customer Platform can implement scheduled job
// Or backend sends notification via email/push
```

5. **Review Request** (after checkout):
```javascript
// Automated notification sent 1 day after check_out date
// Links to review submission form
```

**Customer Platform Notification Storage**:

If you want to store customer notifications similar to host notifications:

```sql
-- Create customer_notifications table (mirrors host_notifications)
CREATE TABLE public.customer_notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  guest_id UUID REFERENCES auth.users(id) NOT NULL,
  type VARCHAR(50) NOT NULL,
  title VARCHAR(255) NOT NULL,
  message TEXT NOT NULL,
  is_read BOOLEAN DEFAULT false,
  priority VARCHAR(20) DEFAULT 'medium',
  action_required BOOLEAN DEFAULT false,
  booking_id UUID REFERENCES bookings(id),
  property_id UUID REFERENCES properties(id),
  message_id UUID REFERENCES messages(id),
  action_url TEXT,
  expires_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS policies
CREATE POLICY "Guests view own notifications"
ON customer_notifications FOR SELECT
USING (auth.uid() = guest_id);
```

**Customer Platform API Pattern**:
```javascript
// Get customer notifications
const getCustomerNotifications = async (guestId, unreadOnly = false) => {
  let query = supabase
    .from('customer_notifications')
    .select('*')
    .eq('guest_id', guestId)
    .order('created_at', { ascending: false })
    .limit(20);

  if (unreadOnly) {
    query = query.eq('is_read', false);
  }

  const { data } = await query;
  return data;
};

// Mark as read
const markNotificationRead = async (notificationId) => {
  await supabase
    .from('customer_notifications')
    .update({ is_read: true })
    .eq('id', notificationId);
};
```

---

### 3. Super Admin → Host Dashboard

#### Superhost Verification

**Host Requests**:
```
POST /api/superhost/request-verification
{
  "reason": "I meet all requirements..."
}
```

**Super Admin Reviews**:
```sql
SELECT vr.*, u.email, u.first_name,
       calculate_host_metrics(vr.host_id) as metrics
FROM superhost_verification_requests vr
JOIN users u ON vr.host_id = u.id
WHERE vr.status = 'pending';
```

**Super Admin Approves/Rejects**:
```sql
UPDATE superhost_verification_requests
SET status = 'approved', reviewed_at = NOW()
WHERE id = request_id;

UPDATE users
SET is_superhost = true
WHERE id = host_id;
```

**Host Dashboard Receives**:
- Notification of approval/rejection
- Badge displayed on profile
- Superhost status in dashboard

#### Property Moderation

**Super Admin Can**:
```sql
-- Flag property for review
UPDATE properties
SET moderation_status = 'under_review',
    moderation_notes = 'Inappropriate content'
WHERE id = property_id;

-- Deactivate property
UPDATE properties
SET status = 'inactive',
    deactivated_reason = 'Policy violation'
WHERE id = property_id;
```

**Host Dashboard Shows**:
- Moderation status in property list
- Reason for deactivation
- Appeal process

#### User Management

**Super Admin Operations**:
```sql
-- Suspend host account
UPDATE users
SET account_status = 'suspended',
    suspension_reason = 'Terms violation'
WHERE id = host_id;

-- Ban user
UPDATE users
SET account_status = 'banned',
    banned_at = NOW()
WHERE id = host_id;
```

**Host Dashboard Impact**:
- Suspended: Limited access, can view but not create
- Banned: Full lockout, redirect to contact page

---

## API Integration Examples

### Customer Platform Booking Integration

**Step 1: Search Available Properties**
```javascript
// Customer Platform
const searchProperties = async (filters) => {
  const { data } = await supabase
    .from('properties')
    .select('*')
    .eq('status', 'active')
    .gte('max_guests', filters.guests)
    .eq('city', filters.city);
  
  return data;
};
```

**Step 2: Create Booking**
```javascript
// Customer Platform
const createBooking = async (bookingData) => {
  const { data, error } = await supabase
    .from('bookings')
    .insert({
      property_id: bookingData.propertyId,
      guest_id: currentUser.id,
      check_in: bookingData.checkIn,
      check_out: bookingData.checkOut,
      total_amount: bookingData.totalAmount,
      guest_count: bookingData.guests,
      status: 'pending'
    })
    .select()
    .single();

  if (!error) {
    // Create notification for host
    await createHostNotification(data);
  }

  return { data, error };
};
```

**Step 3: Host Receives Notification**
```javascript
// Host Dashboard (automatic)
// - Notification created via DB trigger
// - Real-time subscription updates UI
// - Email sent via notification service
```

### Host Dashboard Response Integration

**Host Confirms Booking**:
```javascript
// Host Dashboard
const confirmBooking = async (bookingId) => {
  const response = await fetch(
    `${API_URL}/api/bookings/${bookingId}/status`,
    {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ status: 'confirmed' })
    }
  );

  return response.json();
};
```

**Customer Platform Receives Update**:
```javascript
// Customer Platform (real-time subscription)
supabase
  .channel('booking-updates')
  .on('postgres_changes',
    {
      event: 'UPDATE',
      schema: 'public',
      table: 'bookings',
      filter: `guest_id=eq.${userId}`
    },
    (payload) => {
      // Update UI with new booking status
      updateBookingStatus(payload.new);
      // Send notification to guest
      notifyGuest(payload.new);
    }
  )
  .subscribe();
```

---

## Database Functions (Shared Across Platforms)

### Calculate Host Balance
```sql
SELECT * FROM calculate_host_balance(host_user_id);
```

**Returns**:
```json
{
  "total_earnings": 15000,
  "total_paid_out": 10000,
  "available_balance": 5000,
  "pending_amount": 2000
}
```

**Used By**:
- Host Dashboard: Display balance
- Super Admin: Verify payouts
- Payment System: Process withdrawals

### Check Superhost Eligibility
```sql
SELECT * FROM check_superhost_eligibility(host_user_id);
```

**Returns**:
```json
{
  "eligible": true,
  "reasons": []
}
```

**Used By**:
- Host Dashboard: Eligibility check
- Super Admin: Verification review
- Customer Platform: Display badge

### Calculate Host Metrics
```sql
SELECT * FROM calculate_host_metrics(host_user_id);
```

**Returns**:
```json
{
  "total_bookings": 50,
  "average_rating": 4.8,
  "response_rate": 95,
  "cancellation_rate": 2,
  "total_revenue": 25000
}
```

**Used By**:
- Host Dashboard: Analytics
- Super Admin: Performance monitoring
- Superhost System: Eligibility calculation

---

## Real-Time Communication

### Supabase Realtime Channels

**Booking Updates Channel**:
```javascript
const bookingChannel = supabase.channel('bookings');

// Customer Platform subscribes to their bookings
bookingChannel
  .on('postgres_changes',
    { event: '*', schema: 'public', table: 'bookings', filter: `guest_id=eq.${userId}` },
    handleBookingUpdate
  )
  .subscribe();

// Host Dashboard subscribes to their property bookings
bookingChannel
  .on('postgres_changes',
    { event: '*', schema: 'public', table: 'bookings', filter: `property_id=in.(${propertyIds})` },
    handleHostBookingUpdate
  )
  .subscribe();
```

**Message Channel**:
```javascript
const messageChannel = supabase.channel('messages');

// Real-time message delivery
messageChannel
  .on('postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'messages' },
    handleNewMessage
  )
  .subscribe();
```

---

## Security & Permissions

### Row Level Security (RLS)

**Properties Table**:
```sql
-- Hosts can view/edit their own properties
CREATE POLICY "Hosts manage own properties"
ON properties FOR ALL
USING (auth.uid() = user_id);

-- Everyone can view active properties
CREATE POLICY "Public view active properties"
ON properties FOR SELECT
USING (status = 'active');

-- Admins can view all
CREATE POLICY "Admins view all properties"
ON properties FOR SELECT
USING (
  auth.uid() IN (
    SELECT id FROM users WHERE role = 'admin'
  )
);
```

**Bookings Table**:
```sql
-- Guests see their bookings
CREATE POLICY "Guests view own bookings"
ON bookings FOR SELECT
USING (auth.uid() = guest_id);

-- Hosts see bookings for their properties
CREATE POLICY "Hosts view property bookings"
ON bookings FOR SELECT
USING (
  auth.uid() IN (
    SELECT user_id FROM properties WHERE id = bookings.property_id
  )
);

-- Hosts can update booking status
CREATE POLICY "Hosts update booking status"
ON bookings FOR UPDATE
USING (
  auth.uid() IN (
    SELECT user_id FROM properties WHERE id = bookings.property_id
  )
);
```

---

## Environment Variables

### Host Dashboard
```bash
# API
API_URL=https://api.host.krib.ae/api
VITE_API_URL=https://api.host.krib.ae/api

# Supabase
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_ANON_KEY=eyJhbG...
SUPABASE_SERVICE_ROLE_KEY=eyJhbG... (backend only)

# Google Maps
VITE_GOOGLE_MAPS_API_KEY=AIzaSy...
GOOGLE_API_KEY=AIzaSy... (backend)

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email (Optional)
RESEND_API_KEY=re_...
FROM_EMAIL=noreply@krib.ae
FROM_NAME=Krib Team

# AI (Optional)
OPENAI_API_KEY=sk-...
AI_MODEL=gpt-4-turbo-preview
```

### Customer Platform
```bash
# Supabase (shared)
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_ANON_KEY=eyJhbG...

# Stripe (shared)
STRIPE_PUBLISHABLE_KEY=pk_live_...

# Google Maps (shared)
GOOGLE_MAPS_API_KEY=AIzaSy...
```

### Super Admin Platform
```bash
# Supabase (needs service role key)
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbG...

# Admin API
ADMIN_API_URL=https://admin.krib.ae/api
```

---

## Testing Integration

### End-to-End Flow Test

1. **Customer books property** (Customer Platform)
2. **Host receives notification** (Host Dashboard)
3. **Host confirms booking** (Host Dashboard)
4. **Customer receives confirmation** (Customer Platform)
5. **Payment processed** (Stripe webhook → both platforms)
6. **Host sees revenue** (Host Dashboard)
7. **Customer completes stay** (Auto-update)
8. **Customer leaves review** (Customer Platform)
9. **Host responds to review** (Host Dashboard)
10. **Super admin reviews metrics** (Super Admin)

### Integration Test Script

```bash
#!/bin/bash

# 1. Create property (Host Dashboard)
PROPERTY_ID=$(curl -X POST "$HOST_API/properties" \
  -H "Authorization: Bearer $HOST_TOKEN" \
  -d @property_data.json | jq -r '.id')

# 2. Search properties (Customer Platform)
curl "$CUSTOMER_API/properties?city=Dubai" | jq

# 3. Create booking (Customer Platform)
BOOKING_ID=$(curl -X POST "$CUSTOMER_API/bookings" \
  -H "Authorization: Bearer $GUEST_TOKEN" \
  -d "{\"property_id\":\"$PROPERTY_ID\",...}" | jq -r '.id')

# 4. Check host notifications (Host Dashboard)
curl "$HOST_API/v1/hosts/$HOST_ID/notifications" \
  -H "Authorization: Bearer $HOST_TOKEN"

# 5. Confirm booking (Host Dashboard)
curl -X PATCH "$HOST_API/bookings/$BOOKING_ID/status" \
  -H "Authorization: Bearer $HOST_TOKEN" \
  -d '{"status":"confirmed"}'

# 6. Verify in customer (Customer Platform)
curl "$CUSTOMER_API/bookings/$BOOKING_ID" \
  -H "Authorization: Bearer $GUEST_TOKEN"
```

---

## Troubleshooting

### Common Integration Issues

**Issue**: Booking not showing in Host Dashboard
- **Check**: RLS policies on bookings table
- **Verify**: Property ownership matches
- **Solution**: Ensure `user_id` in properties matches authenticated user

**Issue**: Notifications not received
- **Check**: Notification service running
- **Verify**: Email service configured (RESEND_API_KEY)
- **Solution**: Run test SQL script to manually create notification

**Issue**: Real-time updates not working
- **Check**: Supabase Realtime enabled
- **Verify**: Subscription filters correct
- **Solution**: Check browser console for subscription errors

**Issue**: Payment not reflecting
- **Check**: Stripe webhook configured
- **Verify**: Webhook secret matches
- **Solution**: Check Stripe dashboard for webhook delivery

---

## Best Practices

1. **Use Supabase RLS** - Never bypass RLS in production
2. **Real-time Subscriptions** - Use for live updates
3. **Webhook Verification** - Always verify Stripe webhooks
4. **Error Handling** - Graceful degradation for failed integrations
5. **Logging** - Log all cross-platform interactions
6. **Testing** - Test integration flows end-to-end
7. **Documentation** - Keep API docs updated

---

---

## Customer Platform Integration Summary

### Complete Customer Journey Integration

#### 1. Property Discovery & Inquiry
```javascript
// View active properties
const properties = await supabase
  .from('properties')
  .select('*')
  .eq('status', 'active');

// Send inquiry message
await sendPropertyInquiry(propertyId, guestId, "Is this available for Dec 1-5?");
```

#### 2. Booking Creation
```javascript
// Create booking
const booking = await supabase
  .from('bookings')
  .insert({
    property_id: propertyId,
    guest_id: guestId,
    check_in: '2025-12-01',
    check_out: '2025-12-05',
    guests: 2,
    total_amount: 3200,
    status: 'pending'
  })
  .select()
  .single();

// Host receives notification automatically (via DB trigger)
// Customer receives confirmation notification
```

#### 3. Real-time Communication
```javascript
// Subscribe to host responses
supabase
  .channel('messages')
  .on('postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'messages' },
    handleNewMessage
  )
  .subscribe();

// Get conversation messages
const messages = await supabase
  .from('messages')
  .select('*')
  .eq('conversation_id', conversationId)
  .order('created_at');
```

#### 4. Payment & Confirmation
```javascript
// Process payment via Stripe
// Webhook updates booking status to 'confirmed'
// Both platforms receive payment confirmation

// Customer sees:
- Updated booking status
- Payment receipt
- Host confirmation notification
- Check-in instructions (via message)
```

#### 5. Pre-Stay
```javascript
// Customer receives:
- Check-in reminder (24h before)
- Host welcome message
- Property access instructions

// Can message host for questions
```

#### 6. Post-Stay Review
```javascript
// After check-out, customer can review
const canReview = await checkReviewEligibility(bookingId, guestId);

if (canReview) {
  await submitReview({
    bookingId,
    propertyId,
    guestId,
    rating: 5,
    cleanliness: 5,
    communication: 5,
    comment: "Amazing stay!"
  });
}

// Host sees review in dashboard
// Host can respond to review
// Future customers see review on property listing
```

### Key Database Tables for Customer Platform

**Read Access Required**:
- `properties` - Property listings (status = 'active')
- `reviews` - Property reviews and ratings
- `messages` - Conversation messages

**Write Access Required**:
- `bookings` - Create bookings (guest_id = current user)
- `conversations` - Create conversations (guest_id = current user)
- `messages` - Send messages (sender_type = 'guest')
- `reviews` - Submit reviews (guest_id = current user)
- `customer_notifications` - Notification management

**Read-Only via RLS**:
- Host contact info (after booking confirmed)
- Property detailed info (when active)
- Conversation history (only their conversations)

### Environment Variables for Customer Platform

```bash
# Supabase (Shared Database)
VITE_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbG...

# Google Maps (Property Location Display)
VITE_GOOGLE_MAPS_API_KEY=AIzaSy...

# Stripe (Customer Payment)
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_...

# API Endpoints (if using Host Dashboard API)
VITE_HOST_API_URL=https://api.host.krib.ae/api
```

### Customer Platform Features Checklist

- [ ] Property search and filtering
- [ ] Property detail pages with images and amenities
- [ ] Real-time availability checking
- [ ] Booking creation and payment
- [ ] Guest-host messaging system
- [ ] Booking status tracking
- [ ] Review submission after stay
- [ ] Notification center (booking updates, messages, reminders)
- [ ] Customer profile management
- [ ] Booking history
- [ ] Saved properties / favorites
- [ ] Real-time updates via Supabase subscriptions

### Testing Customer-Host Integration

**End-to-End Test Flow**:

1. **Customer searches for property** → Query `properties` table
2. **Customer sends inquiry** → Insert into `conversations` and `messages`
3. **Host receives notification** → Check `host_notifications` table
4. **Host responds** → Insert into `messages` with sender_type='host'
5. **Customer sees response** → Real-time update via subscription
6. **Customer books property** → Insert into `bookings`
7. **Host confirms booking** → Update booking status
8. **Customer receives confirmation** → Notification + email
9. **Payment processed** → Stripe webhook updates database
10. **After stay, customer reviews** → Insert into `reviews`
11. **Host responds to review** → Update `reviews` table
12. **Future customers see review** → Display on property page

**Test Script**:
```bash
# Use the API_TESTING_GUIDE.md for comprehensive endpoint testing
# Use BOOKING_FLOW_TESTING.md for complete booking scenarios
```

---

## Support & Resources

- **Host Dashboard API**: https://api.host.krib.ae/docs
- **Customer Platform Integration**: See sections above
- **Supabase Dashboard**: https://supabase.com/dashboard
- **Stripe Dashboard**: https://dashboard.stripe.com
- **Error Tracking**: Sentry (if configured)

