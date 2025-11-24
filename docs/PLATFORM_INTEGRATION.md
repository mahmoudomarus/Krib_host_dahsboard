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
```sql
INSERT INTO conversations (property_id, guest_id, host_id)
VALUES (property_id, guest_id, (SELECT user_id FROM properties WHERE id = property_id));

INSERT INTO messages (conversation_id, sender_type, content)
VALUES (conversation_id, 'guest', message_content);
```

**Host Dashboard Receives**:
- GET `/api/messages/conversations` - Lists all conversations
- GET `/api/messages/conversations/{id}/messages` - Message history
- POST `/api/messages/generate-ai-response` - AI-powered reply
- POST `/api/messages/send` - Send response

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

## Support & Resources

- **Host Dashboard API**: https://api.host.krib.ae/docs
- **Supabase Dashboard**: https://supabase.com/dashboard
- **Stripe Dashboard**: https://dashboard.stripe.com
- **Error Tracking**: Sentry (if configured)

