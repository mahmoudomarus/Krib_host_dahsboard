# Testing Checklist - Krib Host Dashboard

## Quick Testing Guide

Use this checklist to systematically test all platform features.

---

## 1. Authentication & User Profile

### Sign Up / Login
- [ ] Sign up with email
- [ ] Receive verification email
- [ ] Login with credentials
- [ ] JWT token stored correctly
- [ ] Token persists on refresh

### Profile Management
```bash
# Test endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.host.krib.ae/api/users/me
```

- [ ] Get current user profile
- [ ] Update first/last name
- [ ] Update bio
- [ ] Update phone number
- [ ] Upload profile picture
- [ ] Profile data persists

---

## 2. Property Management

### Create Property
```bash
# Test endpoint
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d @test-property.json \
  https://api.host.krib.ae/api/properties
```

- [ ] Create property with all required fields
- [ ] Upload multiple images
- [ ] Set location on map (latitude/longitude)
- [ ] Select amenities
- [ ] Property appears in list
- [ ] Property saved as draft

### Update Property
- [ ] Edit property details
- [ ] Update pricing
- [ ] Add/remove amenities
- [ ] Change property status to active
- [ ] Delete images
- [ ] Add new images

### View Properties
- [ ] View all properties list
- [ ] Filter by status (draft/active)
- [ ] View single property details
- [ ] Property images display correctly

### Delete Property
- [ ] Delete property
- [ ] Confirm deletion
- [ ] Property removed from list

---

## 3. Bookings

### View Bookings
```bash
# Test endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.host.krib.ae/api/bookings
```

- [ ] View all bookings
- [ ] Filter by status
- [ ] Filter by property
- [ ] Filter by date range
- [ ] Bookings display correctly

### Manage Booking Status
```bash
# Confirm booking
curl -X PATCH -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"status":"confirmed"}' \
  https://api.host.krib.ae/api/bookings/BOOKING_ID/status
```

- [ ] Confirm pending booking
- [ ] Cancel booking
- [ ] View booking details
- [ ] Guest information displays
- [ ] Booking dates correct

---

## 4. Financial Dashboard

### View Financial Summary
```bash
# Test endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.host.krib.ae/api/financials/summary?period=30days"
```

- [ ] Total revenue displays
- [ ] Pending amount displays
- [ ] Available balance displays
- [ ] Revenue trend chart shows
- [ ] Transaction history displays

### Stripe Connect
```bash
# Check account status
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.host.krib.ae/api/v1/stripe/host/account-status
```

- [ ] Create Stripe account
- [ ] Complete onboarding
- [ ] Verify account connected
- [ ] Charges enabled
- [ ] Payouts enabled

### Payouts
```bash
# View payouts
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.host.krib.ae/api/v1/payouts/host-payouts
```

- [ ] View payout history
- [ ] Check available balance
- [ ] Check pending balance
- [ ] Next payout date displays

---

## 5. Notifications

### View Notifications
```bash
# Test endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.host.krib.ae/api/v1/hosts/USER_ID/notifications
```

- [ ] Notification bell appears in header
- [ ] Unread count badge displays
- [ ] Click bell opens dropdown
- [ ] Notifications list displays
- [ ] Click notification navigates to correct page

### Mark as Read
```bash
# Mark notification read
curl -X PUT -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.host.krib.ae/api/v1/hosts/USER_ID/notifications/NOTIF_ID/read
```

- [ ] Mark notification as read
- [ ] Unread count decreases
- [ ] Notification styling changes

### Email Notifications
**Requires RESEND_API_KEY configured**

- [ ] Receive new booking email
- [ ] Receive payment email
- [ ] Receive guest message email
- [ ] Email links work correctly
- [ ] Email formatting correct

---

## 6. Messaging System

### View Conversations
```bash
# Test endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.host.krib.ae/api/messages/conversations
```

- [ ] View conversations list
- [ ] Unread count displays
- [ ] Guest names display
- [ ] Property titles display
- [ ] Last message timestamp shows

### Send Message
```bash
# Send message
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"conversation_id":"uuid","message":"Hello"}' \
  https://api.host.krib.ae/api/messages/send
```

- [ ] Send message to guest
- [ ] Message appears in conversation
- [ ] Timestamp displays correctly
- [ ] Guest receives notification

### AI Response
```bash
# Generate AI response
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"conversation_id":"uuid","guest_message":"Check-in time?"}' \
  https://api.host.krib.ae/api/messages/generate-ai-response
```

- [ ] Click AI generate button
- [ ] AI response appears
- [ ] Response is contextually relevant
- [ ] Can edit before sending
- [ ] Send AI response

---

## 7. Reviews

### View Reviews
```bash
# Test endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.host.krib.ae/api/v1/reviews
```

- [ ] View all reviews
- [ ] Filter by property
- [ ] Star ratings display
- [ ] Review comments display
- [ ] Guest names display

### Review Statistics
```bash
# Get stats
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.host.krib.ae/api/v1/reviews/stats
```

- [ ] Total reviews count
- [ ] Average rating displays
- [ ] Pending responses count
- [ ] Rating distribution chart
- [ ] All data accurate

### Respond to Review
```bash
# Respond to review
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"response":"Thank you!"}' \
  https://api.host.krib.ae/api/v1/reviews/REVIEW_ID/respond
```

- [ ] Click respond button
- [ ] Enter response text
- [ ] Submit response
- [ ] Response appears below review
- [ ] Response timestamp displays

---

## 8. Analytics

### View Analytics Dashboard
```bash
# Test endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.host.krib.ae/api/analytics
```

- [ ] Total revenue displays
- [ ] Total bookings displays
- [ ] Occupancy rate displays
- [ ] Average rating displays
- [ ] Revenue trend chart
- [ ] Booking trend chart
- [ ] Top properties list
- [ ] Market comparison data

### Charts & Visualizations
- [ ] Revenue chart loads
- [ ] Booking chart loads
- [ ] Charts respond to filters
- [ ] Data updates correctly
- [ ] No hardcoded values

---

## 9. Superhost System

### Check Eligibility
```bash
# Test endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.host.krib.ae/api/superhost/eligibility
```

- [ ] Navigate to Superhost page
- [ ] Eligibility status displays
- [ ] Metrics display correctly
- [ ] Requirements checklist shows
- [ ] Progress bars display

### Request Verification
```bash
# Request verification
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"reason":"I meet all requirements"}' \
  https://api.host.krib.ae/api/superhost/request-verification
```

- [ ] Fill verification form
- [ ] Submit request
- [ ] Confirmation message appears
- [ ] Request status displays
- [ ] Can view pending request

---

## 10. Settings

### Update Settings
- [ ] Change email preferences
- [ ] Update notification settings
- [ ] Change currency (should be AED)
- [ ] Change timezone (should be Dubai)
- [ ] Update password
- [ ] Settings save correctly

### Sign Out
- [ ] Click sign out
- [ ] Redirected to login page
- [ ] Session cleared
- [ ] Cannot access protected routes
- [ ] Can sign in again

---

## 11. Integration Testing

### Complete Booking Flow
1. [ ] Customer creates booking (Customer Platform)
2. [ ] Host receives notification (Host Dashboard)
3. [ ] Host confirms booking (Host Dashboard)
4. [ ] Customer receives confirmation (Customer Platform)
5. [ ] Payment processed (Stripe)
6. [ ] Host sees revenue (Host Dashboard)
7. [ ] Check-in auto-updates (System)
8. [ ] Check-out auto-updates (System)
9. [ ] Guest leaves review (Customer Platform)
10. [ ] Host responds to review (Host Dashboard)

### Database Integrity
```sql
-- Run in Supabase SQL editor
-- Check bookings
SELECT * FROM bookings ORDER BY created_at DESC LIMIT 5;

-- Check notifications
SELECT * FROM host_notifications ORDER BY created_at DESC LIMIT 5;

-- Check financial transactions
SELECT * FROM financial_transactions ORDER BY created_at DESC LIMIT 5;
```

- [ ] Bookings table populated correctly
- [ ] Notifications created automatically
- [ ] Financial records accurate
- [ ] RLS policies working
- [ ] No orphaned records

---

## 12. Error Handling

### Test Error Scenarios
- [ ] Invalid authentication token
- [ ] Access unauthorized resource
- [ ] Submit invalid data
- [ ] Network timeout
- [ ] Server error (500)
- [ ] Not found (404)
- [ ] Validation errors display
- [ ] Error messages user-friendly

---

## 13. Performance

### Response Times
- [ ] Property list loads < 500ms
- [ ] Booking list loads < 500ms
- [ ] Analytics loads < 1s
- [ ] Image upload < 5s per image
- [ ] API responses < 300ms average

### Load Testing
```bash
# Basic load test
for i in {1..100}; do
  curl -H "Authorization: Bearer YOUR_TOKEN" \
    https://api.host.krib.ae/api/properties &
done
wait
```

- [ ] Handle 100 concurrent requests
- [ ] No 500 errors under load
- [ ] Response times remain stable
- [ ] Database connections stable

---

## 14. Mobile Responsiveness

### Test on Mobile Devices
- [ ] Dashboard displays correctly
- [ ] Navigation works on mobile
- [ ] Forms are usable
- [ ] Images resize properly
- [ ] Touch targets adequate size
- [ ] No horizontal scrolling

---

## 15. Browser Compatibility

### Test in Different Browsers
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile browsers

---

## 16. Security

### Authentication & Authorization
- [ ] JWT token expires correctly
- [ ] Cannot access others' data
- [ ] RLS policies enforced
- [ ] SQL injection protected
- [ ] XSS protected
- [ ] CORS configured correctly

### Data Privacy
- [ ] Sensitive data encrypted
- [ ] Passwords hashed
- [ ] API keys secured
- [ ] No data leaks in responses

---

## Test Data Scripts

### Create Test Data
```bash
# Run in Supabase SQL editor

# 1. Create test notifications
\i test_notifications.sql

# 2. Create test reviews
\i test_reviews.sql

# 3. Check data
SELECT COUNT(*) FROM host_notifications;
SELECT COUNT(*) FROM reviews;
```

### Clean Up Test Data
```bash
# Run in Supabase SQL editor
\i cleanup_test_data.sql
```

---

## Automated Testing Script

```bash
#!/bin/bash
# complete-test.sh

set -e

TOKEN="YOUR_AUTH_TOKEN"
API="https://api.host.krib.ae/api"

echo "=== Testing Health ==="
curl -f "$API/health" || exit 1

echo "=== Testing Properties ==="
curl -f -H "Authorization: Bearer $TOKEN" "$API/properties" || exit 1

echo "=== Testing Bookings ==="
curl -f -H "Authorization: Bearer $TOKEN" "$API/bookings" || exit 1

echo "=== Testing Notifications ==="
curl -f -H "Authorization: Bearer $TOKEN" "$API/v1/hosts/$USER_ID/notifications" || exit 1

echo "=== Testing Reviews ==="
curl -f -H "Authorization: Bearer $TOKEN" "$API/v1/reviews" || exit 1

echo "=== All Tests Passed ==="
```

---

## Monitoring

### Key Metrics to Monitor
- [ ] API response times
- [ ] Error rate < 1%
- [ ] Uptime > 99.9%
- [ ] Database queries < 100ms
- [ ] Notification delivery > 99%
- [ ] Email delivery > 95%

### Logging
- [ ] All API calls logged
- [ ] Errors logged with stack traces
- [ ] User actions tracked
- [ ] Performance metrics collected

---

## Documentation Review

### Verify Documentation
- [ ] README.md complete
- [ ] API_REFERENCE.md accurate
- [ ] API_TESTING_GUIDE.md helpful
- [ ] BOOKING_FLOW_TESTING.md detailed
- [ ] PLATFORM_INTEGRATION.md clear
- [ ] All code examples work
- [ ] All URLs correct
- [ ] All screenshots current

---

## Deployment Verification

### Production Environment
- [ ] Frontend deployed to Render
- [ ] Backend deployed to Render
- [ ] Database on Supabase
- [ ] Environment variables set
- [ ] SSL certificates active
- [ ] CDN caching working
- [ ] Webhooks configured

### Health Checks
```bash
# Frontend
curl -f https://host.krib.ae

# Backend
curl -f https://api.host.krib.ae/api/health

# Database
# Check in Supabase dashboard
```

---

## Final Checklist

- [ ] All features working
- [ ] No console errors
- [ ] No broken links
- [ ] No hardcoded values
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Integration verified
- [ ] Performance acceptable
- [ ] Security audited
- [ ] Ready for production

---

## Support

If any test fails:
1. Check documentation: `/docs` directory
2. Check logs in Render dashboard
3. Check database in Supabase
4. Check Stripe dashboard for payment issues
5. Contact development team

---

## Test Results Template

```
Date: ____________________
Tester: __________________
Environment: Production / Staging

Authentication: ✓ / ✗
Properties: ✓ / ✗
Bookings: ✓ / ✗
Financials: ✓ / ✗
Notifications: ✓ / ✗
Messages: ✓ / ✗
Reviews: ✓ / ✗
Analytics: ✓ / ✗
Superhost: ✓ / ✗
Settings: ✓ / ✗

Issues Found:
1. _______________________
2. _______________________
3. _______________________

Overall Status: PASS / FAIL
```

