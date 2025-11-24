# Booking Flow Testing Guide

## Complete Booking Lifecycle

This document outlines the complete booking flow from creation to completion, including all touchpoints between Customer Platform and Host Dashboard.

---

## Flow Diagram

```
Customer Platform                    Host Dashboard                   System
─────────────────────────────────────────────────────────────────────────────────

1. Guest searches properties  -->
2. Guest selects property     -->
3. Guest creates booking      -->   4. Notification created         Supabase DB
                                     5. Email sent                  Email Service
                                 <-- 6. Host views notification
                                 <-- 7. Host reviews booking
                                 <-- 8. Host confirms booking
9. Guest receives confirmation <--   
10. Payment processed         -->   11. Payment notification        Stripe
                                 <-- 12. Host sees revenue
13. Check-in occurs           -->
14. Stay in progress          -->
15. Check-out occurs          -->   16. Auto-status update          Supabase DB
17. Guest leaves review       -->   18. Review notification
                                 <-- 19. Host responds to review
20. Payout processed          -->   21. Payout notification         Stripe
```

---

## Detailed Testing Steps

### Phase 1: Property Setup (Host Dashboard)

#### 1.1 Create Property
```bash
curl -X POST https://api.host.krib.ae/api/properties \
  -H "Authorization: Bearer $HOST_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Property - Dubai Marina",
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
    "price_per_night": 500,
    "description": "Test property for booking flow",
    "amenities": ["WiFi", "AC", "Kitchen"],
    "images": ["https://placehold.co/600x400"]
  }'
```

**Expected Response**:
```json
{
  "id": "prop-uuid-123",
  "status": "draft",
  "created_at": "2025-11-24T..."
}
```

**Save**: `PROPERTY_ID=prop-uuid-123`

#### 1.2 Activate Property
```bash
curl -X PUT https://api.host.krib.ae/api/properties/$PROPERTY_ID \
  -H "Authorization: Bearer $HOST_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "active"}'
```

**Verification**: Property now visible to customers

---

### Phase 2: Booking Creation (Customer Platform)

#### 2.1 Search Properties
```sql
-- Customer Platform Query
SELECT id, title, price_per_night, city, images
FROM properties
WHERE status = 'active'
  AND city = 'Dubai Marina'
  AND max_guests >= 2;
```

**Should Return**: Test property created in Phase 1

#### 2.2 Create Booking
```sql
-- Customer Platform
INSERT INTO bookings (
  property_id,
  guest_id,
  check_in,
  check_out,
  total_amount,
  status,
  guest_count,
  created_at
) VALUES (
  'prop-uuid-123',
  'guest-uuid-456',
  '2025-12-01',
  '2025-12-05',
  2000.00,  -- 4 nights * 500 AED
  'pending',
  2,
  NOW()
) RETURNING *;
```

**Expected Result**:
```json
{
  "id": "booking-uuid-789",
  "status": "pending",
  "created_at": "2025-11-24T..."
}
```

**Save**: `BOOKING_ID=booking-uuid-789`

---

### Phase 3: Host Notification (Automatic)

#### 3.1 Verify Notification Created
```bash
curl https://api.host.krib.ae/api/v1/hosts/$HOST_ID/notifications \
  -H "Authorization: Bearer $HOST_TOKEN"
```

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "notifications": [
      {
        "id": "notif-uuid-111",
        "type": "new_booking",
        "title": "New Booking Request",
        "message": "You have a new booking request for Test Property",
        "booking_id": "booking-uuid-789",
        "is_read": false,
        "priority": "high",
        "created_at": "2025-11-24T..."
      }
    ],
    "unread_count": 1
  }
}
```

#### 3.2 Check Email Sent
**If RESEND_API_KEY configured**:
- Check host email inbox
- Should receive "New Booking Request" email
- Email contains booking details and action link

---

### Phase 4: Booking Confirmation (Host Dashboard)

#### 4.1 View Booking Details
```bash
curl https://api.host.krib.ae/api/bookings/$BOOKING_ID \
  -H "Authorization: Bearer $HOST_TOKEN"
```

**Expected Response**:
```json
{
  "id": "booking-uuid-789",
  "property_id": "prop-uuid-123",
  "property_title": "Test Property - Dubai Marina",
  "guest_id": "guest-uuid-456",
  "guest_name": "John Doe",
  "check_in": "2025-12-01",
  "check_out": "2025-12-05",
  "total_amount": 2000.00,
  "status": "pending",
  "guest_count": 2,
  "created_at": "2025-11-24T..."
}
```

#### 4.2 Confirm Booking
```bash
curl -X PATCH https://api.host.krib.ae/api/bookings/$BOOKING_ID/status \
  -H "Authorization: Bearer $HOST_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "confirmed"}'
```

**Expected Response**:
```json
{
  "success": true,
  "booking": {
    "id": "booking-uuid-789",
    "status": "confirmed",
    "confirmed_at": "2025-11-24T..."
  }
}
```

#### 4.3 Verify Guest Notified
**Customer Platform** should show:
- Booking status updated to "confirmed"
- Guest receives confirmation email
- Booking appears in "Upcoming" section

---

### Phase 5: Payment Processing

#### 5.1 Process Payment (Stripe)
```javascript
// Customer Platform
const paymentIntent = await stripe.paymentIntents.create({
  amount: 200000,  // 2000 AED in fils
  currency: 'aed',
  customer: customerId,
  metadata: {
    booking_id: 'booking-uuid-789',
    property_id: 'prop-uuid-123',
    host_id: 'host-uuid-123'
  },
  application_fee_amount: 30000,  // 15% platform fee
  transfer_data: {
    destination: hostStripeAccountId
  }
});
```

#### 5.2 Webhook Updates Booking
**Stripe sends webhook** → `https://api.host.krib.ae/api/billing/webhook`

**Webhook Handler**:
```sql
UPDATE bookings
SET 
  payment_status = 'paid',
  payment_intent_id = 'pi_...',
  stripe_fee_amount = 30.00,
  host_payout_amount = 1670.00,  -- After platform fee and Stripe fee
  paid_at = NOW()
WHERE id = 'booking-uuid-789';
```

#### 5.3 Verify Host Notified
```bash
curl https://api.host.krib.ae/api/v1/hosts/$HOST_ID/notifications \
  -H "Authorization: Bearer $HOST_TOKEN"
```

**Should Include**:
```json
{
  "type": "payment_received",
  "title": "Payment Received",
  "message": "Payment received for booking at Test Property",
  "booking_id": "booking-uuid-789"
}
```

---

### Phase 6: Financial Tracking (Host Dashboard)

#### 6.1 Check Financial Summary
```bash
curl "https://api.host.krib.ae/api/financials/summary?period=30days" \
  -H "Authorization: Bearer $HOST_TOKEN"
```

**Expected Response**:
```json
{
  "total_revenue": 1670.00,
  "pending_amount": 1670.00,
  "available_balance": 0.00,
  "total_bookings": 1,
  "recent_transactions": [
    {
      "type": "booking_payment",
      "amount": 1670.00,
      "booking_id": "booking-uuid-789",
      "created_at": "2025-11-24T..."
    }
  ]
}
```

#### 6.2 Check Host Balance
```bash
curl https://api.host.krib.ae/api/v1/payouts/host-payouts \
  -H "Authorization: Bearer $HOST_TOKEN"
```

**Expected Response**:
```json
{
  "available_balance": 0.00,
  "pending_balance": 1670.00,
  "next_payout_date": "2025-12-08",
  "payout_schedule": "weekly"
}
```

**Note**: Pending balance becomes available after check-in + holding period

---

### Phase 7: Check-In Process

#### 7.1 Auto-Status Update (Check-In Date)
**Automated Job** runs daily:
```sql
UPDATE bookings
SET status = 'in_progress'
WHERE status = 'confirmed'
  AND check_in <= CURRENT_DATE
  AND check_out > CURRENT_DATE;
```

#### 7.2 Release Payment Hold
**After check-in** (24 hours later):
```sql
UPDATE financial_transactions
SET status = 'available',
    available_at = NOW()
WHERE booking_id = 'booking-uuid-789'
  AND status = 'pending';
```

#### 7.3 Host Dashboard Shows Available Balance
```bash
curl https://api.host.krib.ae/api/v1/payouts/host-payouts \
  -H "Authorization: Bearer $HOST_TOKEN"
```

**Now Shows**:
```json
{
  "available_balance": 1670.00,
  "pending_balance": 0.00
}
```

---

### Phase 8: Check-Out & Completion

#### 8.1 Auto-Status Update (Check-Out Date)
```sql
UPDATE bookings
SET status = 'completed',
    completed_at = NOW()
WHERE status = 'in_progress'
  AND check_out <= CURRENT_DATE;
```

#### 8.2 Request Review (Customer Platform)
**Automated email** sent to guest:
- "How was your stay?"
- Link to review form

---

### Phase 9: Review Process

#### 9.1 Guest Submits Review (Customer Platform)
```sql
INSERT INTO reviews (
  booking_id,
  property_id,
  guest_id,
  rating,
  cleanliness_rating,
  communication_rating,
  location_rating,
  comment,
  created_at
) VALUES (
  'booking-uuid-789',
  'prop-uuid-123',
  'guest-uuid-456',
  5.0,
  5.0,
  5.0,
  5.0,
  'Amazing stay! Highly recommend.',
  NOW()
);
```

#### 9.2 Update Property Rating
```sql
UPDATE properties
SET 
  rating = (
    SELECT AVG(rating) FROM reviews WHERE property_id = 'prop-uuid-123'
  ),
  review_count = review_count + 1
WHERE id = 'prop-uuid-123';
```

#### 9.3 Host Receives Notification
```bash
curl https://api.host.krib.ae/api/v1/hosts/$HOST_ID/notifications \
  -H "Authorization: Bearer $HOST_TOKEN"
```

**Should Include**:
```json
{
  "type": "guest_review",
  "title": "New Review Received",
  "message": "John Doe left a 5-star review",
  "priority": "medium"
}
```

#### 9.4 Host Views Review (Host Dashboard)
```bash
curl https://api.host.krib.ae/api/v1/reviews \
  -H "Authorization: Bearer $HOST_TOKEN"
```

#### 9.5 Host Responds to Review
```bash
curl -X POST https://api.host.krib.ae/api/v1/reviews/review-uuid-222/respond \
  -H "Authorization: Bearer $HOST_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "response": "Thank you for your wonderful review! We hope to host you again."
  }'
```

---

### Phase 10: Payout Process

#### 10.1 Automatic Payout (Weekly Schedule)
**Stripe Connect** processes payout:
```javascript
const payout = await stripe.payouts.create({
  amount: 167000,  // 1670 AED in fils
  currency: 'aed',
  destination: hostBankAccount
}, {
  stripeAccount: hostStripeAccountId
});
```

#### 10.2 Record Payout in Database
```sql
INSERT INTO host_payouts (
  host_id,
  amount,
  stripe_payout_id,
  status,
  payout_date,
  created_at
) VALUES (
  'host-uuid-123',
  1670.00,
  'po_...',
  'paid',
  NOW(),
  NOW()
);
```

#### 10.3 Host Receives Notification
```bash
curl https://api.host.krib.ae/api/v1/hosts/$HOST_ID/notifications \
  -H "Authorization: Bearer $HOST_TOKEN"
```

**Should Include**:
```json
{
  "type": "payout_received",
  "title": "Payout Processed",
  "message": "AED 1,670.00 has been transferred to your account",
  "priority": "medium"
}
```

#### 10.4 Verify in Dashboard
```bash
curl https://api.host.krib.ae/api/financials/summary \
  -H "Authorization: Bearer $HOST_TOKEN"
```

**Shows**:
```json
{
  "total_revenue": 1670.00,
  "total_paid_out": 1670.00,
  "available_balance": 0.00,
  "recent_payouts": [
    {
      "amount": 1670.00,
      "status": "paid",
      "payout_date": "2025-12-08"
    }
  ]
}
```

---

## Testing Checklist

### Pre-Booking
- [ ] Property created successfully
- [ ] Property activated and visible
- [ ] Property appears in search results
- [ ] Pricing displays correctly

### Booking Creation
- [ ] Booking created in database
- [ ] Host notification created
- [ ] Host email sent
- [ ] Booking appears in Host Dashboard
- [ ] Booking appears in Customer Platform

### Confirmation
- [ ] Host can view booking details
- [ ] Host can confirm booking
- [ ] Status updates correctly
- [ ] Guest receives confirmation
- [ ] Guest email sent

### Payment
- [ ] Stripe payment processes
- [ ] Webhook received and processed
- [ ] Booking marked as paid
- [ ] Payment notification sent
- [ ] Financial record created
- [ ] Balance updated correctly

### Check-In
- [ ] Status auto-updates on check-in date
- [ ] Payment hold released
- [ ] Available balance increases

### Check-Out
- [ ] Status auto-updates on check-out date
- [ ] Review request sent to guest

### Review
- [ ] Guest can submit review
- [ ] Property rating updated
- [ ] Host receives notification
- [ ] Host can view review
- [ ] Host can respond to review
- [ ] Response visible to customer

### Payout
- [ ] Payout scheduled correctly
- [ ] Stripe processes payout
- [ ] Payout recorded in database
- [ ] Host notified of payout
- [ ] Balance reflected correctly

---

## Error Scenarios to Test

### 1. Double Booking Prevention
```sql
-- Should FAIL if dates overlap
INSERT INTO bookings (property_id, check_in, check_out, ...)
VALUES ('prop-uuid-123', '2025-12-02', '2025-12-06', ...);
-- Overlaps with existing booking (Dec 1-5)
```

**Expected**: Error or validation failure

### 2. Cancelled Booking
```bash
curl -X PATCH https://api.host.krib.ae/api/bookings/$BOOKING_ID/status \
  -H "Authorization: Bearer $HOST_TOKEN" \
  -d '{"status": "cancelled"}'
```

**Verify**:
- Refund processed
- Host notified
- Guest notified
- Calendar freed up

### 3. Payment Failure
**Stripe webhook** with `payment_failed` event

**Verify**:
- Booking status updated to `payment_failed`
- Host notified
- Guest notified to retry payment

### 4. Disputed Booking
**Guest disputes charge** in Stripe

**Verify**:
- Host notified of dispute
- Payment held pending resolution
- Admin notified for review

---

## Automated Testing Script

```bash
#!/bin/bash

# Complete Booking Flow Test
# Requires: jq, curl, valid tokens

set -e

HOST_TOKEN="your-host-token"
GUEST_TOKEN="your-guest-token"
API_URL="https://api.host.krib.ae/api"

echo "=== Phase 1: Create Property ==="
PROPERTY_RESPONSE=$(curl -s -X POST "$API_URL/properties" \
  -H "Authorization: Bearer $HOST_TOKEN" \
  -H "Content-Type: application/json" \
  -d @test-property.json)

PROPERTY_ID=$(echo $PROPERTY_RESPONSE | jq -r '.id')
echo "Property created: $PROPERTY_ID"

echo "=== Phase 2: Activate Property ==="
curl -s -X PUT "$API_URL/properties/$PROPERTY_ID" \
  -H "Authorization: Bearer $HOST_TOKEN" \
  -d '{"status":"active"}' | jq

echo "=== Phase 3: Verify in Search ==="
curl -s "$API_URL/properties?status=active" | jq ".[] | select(.id==\"$PROPERTY_ID\")"

echo "=== Phase 4: Create Booking (via Supabase) ==="
# This would normally be done via Customer Platform
# For testing, insert directly into Supabase

echo "=== Phase 5: Verify Notification ==="
NOTIFICATIONS=$(curl -s "$API_URL/v1/hosts/$HOST_ID/notifications" \
  -H "Authorization: Bearer $HOST_TOKEN")
echo $NOTIFICATIONS | jq '.data.notifications[0]'

echo "=== Phase 6: Confirm Booking ==="
curl -s -X PATCH "$API_URL/bookings/$BOOKING_ID/status" \
  -H "Authorization: Bearer $HOST_TOKEN" \
  -d '{"status":"confirmed"}' | jq

echo "=== Phase 7: Check Financials ==="
curl -s "$API_URL/financials/summary" \
  -H "Authorization: Bearer $HOST_TOKEN" | jq

echo "=== Test Complete ==="
```

---

## Performance Benchmarks

**Expected Response Times**:
- Property creation: < 500ms
- Booking creation: < 300ms
- Notification delivery: < 100ms
- Email delivery: < 2s
- Financial summary: < 500ms
- Webhook processing: < 200ms

**Load Testing**:
- Concurrent bookings: 100/min
- Notification throughput: 1000/min
- API requests: 10,000/min

---

## Monitoring & Alerts

**Key Metrics to Monitor**:
1. Booking creation success rate
2. Notification delivery rate
3. Email delivery rate
4. Payment success rate
5. Webhook processing time
6. API response times

**Alerts to Configure**:
- Booking creation failures > 1%
- Payment failures > 2%
- Webhook failures > 0.5%
- API errors > 1%
- Email bounces > 5%

---

## Support & Troubleshooting

**Common Issues**:
1. **Booking not showing**: Check RLS policies
2. **Notification missing**: Verify trigger function
3. **Payment not processed**: Check Stripe webhook logs
4. **Email not received**: Verify RESEND_API_KEY

**Debug Commands**:
```bash
# Check booking status
psql -c "SELECT * FROM bookings WHERE id = 'booking-uuid-789';"

# Check notifications
psql -c "SELECT * FROM host_notifications WHERE booking_id = 'booking-uuid-789';"

# Check financial records
psql -c "SELECT * FROM financial_transactions WHERE booking_id = 'booking-uuid-789';"
```

