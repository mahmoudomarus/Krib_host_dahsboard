# Host Dashboard - Super Admin Integration Guide

**Backend API:** https://api.host.krib.ae  
**Frontend:** https://host.krib.ae

---

## 1. Environment Variables

```bash
# Supabase Database
SUPABASE_URL=https://bpomacnqaqzgeuahhlka.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJwb21hY25xYXF6Z2V1YWhobGthIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTQ1NzIyNSwiZXhwIjoyMDcxMDMzMjI1fQ.Esc_wEXe2WnbDiMpsHa3Za9eon6BVjdFYzBXftPBWAc

# API Authentication
API_KEY=krib_prod_c4323aa1d8896254316e396995bf7f6fffacdaa8985ec09da4067da37f1e6ae8
# Usage: Authorization: Bearer {API_KEY}
```

---

## 2. Database Schema

### Core Tables
- **`users`** - Host/user profiles (174 total properties across all hosts)
  - Fields: id, name, email, phone, avatar_url, settings, total_revenue, is_active, stripe_account_id, stripe_account_status, stripe_charges_enabled, stripe_payouts_enabled, bank_account_last4, etc.
  
- **`properties`** - Property listings
  - Fields: id, user_id, title, description, address, city, state, country, latitude, longitude, property_type, bedrooms, bathrooms, max_guests, price_per_night, amenities, images, status (draft/active/inactive/suspended), rating, review_count, booking_count, total_revenue, views_count, featured, created_at, updated_at
  
- **`bookings`** - Reservations
  - Fields: id, property_id, guest_name, guest_email, guest_phone, check_in, check_out, nights, guests, total_amount, status (pending/confirmed/cancelled/completed/no_show), payment_status (pending/processing/succeeded/failed/refunded/partially_refunded), special_requests, internal_notes, booking_source, commission_rate, stripe_payment_intent_id, stripe_charge_id, stripe_transfer_id, platform_fee_amount, host_payout_amount, host_payout_status, host_payout_date, payment_processed_at, refund_amount, refund_reason, created_at, updated_at
  
- **`reviews`** - Guest reviews
  - Fields: id, property_id, booking_id, guest_name, guest_email, rating, comment, pros, cons, response_from_host, is_verified, is_featured, helpful_votes, created_at, updated_at

### Financial Tables
- **`payouts`** - Host payouts tracking
  - Fields: id, user_id, booking_id, property_id, stripe_transfer_id, stripe_payout_id, amount, currency (AED), platform_fee, original_booking_amount, status (pending/processing/in_transit/paid/failed/canceled/reversed), description, failure_code, failure_message, initiated_at, expected_arrival_date, completed_at, metadata, created_at, updated_at
  
- **`stripe_events`** - Webhook event log
  - Fields: id, stripe_event_id, event_type, account_id, payment_intent_id, charge_id, transfer_id, payout_id, raw_data (JSONB), api_version, processed, processed_at, error_message, retry_count, created_at, event_created

### Analytics & Tracking Tables
- **`property_analytics`** - Daily metrics per property
  - Fields: id, property_id, date, views, bookings, revenue, occupancy_rate, avg_daily_rate, inquiries, conversion_rate, created_at
  
- **`user_sessions`** - User activity tracking
  - Fields: id, user_id, device_info, ip_address, user_agent, session_start, session_end, is_active
  
- **`saved_searches`** - User saved searches and alerts
  - Fields: id, user_id, name, search_params, is_alert_enabled, alert_frequency, created_at, updated_at

---

## 3. API Endpoints

### Authentication
```
POST   /api/auth/signup
POST   /api/auth/signin
POST   /api/auth/signout
GET    /api/auth/me
POST   /api/auth/refresh
```

### Users (Hosts)
```
GET    /api/users/profile
PUT    /api/users/profile
PUT    /api/users/settings
POST   /api/users/change-password
GET    /api/users/notifications
PUT    /api/users/notifications
```

### Properties (ADMIN ACCESS)
```
GET    /api/properties                    # List all properties
GET    /api/properties/{id}                # Get property details
POST   /api/properties                     # Create property
PUT    /api/properties/{id}                # Update property
DELETE /api/properties/{id}                # Delete property
POST   /api/properties/{id}/publish        # Activate property
POST   /api/properties/{id}/enhance-with-ai
POST   /api/properties/ai/generate-description
POST   /api/properties/ai/suggest-amenities
POST   /api/properties/ai/optimize-title
POST   /api/properties/ai/pricing-strategy
```

### Bookings (ADMIN ACCESS)
```
GET    /api/bookings                      # List all bookings
GET    /api/bookings/{id}                 # Get booking details
POST   /api/bookings                      # Create booking
PUT    /api/bookings/{id}                 # Update booking
POST   /api/bookings/{id}/confirm         # Confirm booking
POST   /api/bookings/{id}/cancel          # Cancel booking
```

### Analytics (HOST/ADMIN ACCESS)
```
GET    /api/analytics                     # Overall analytics
GET    /api/analytics/property/{id}       # Property-specific
GET    /api/analytics/dashboard-overview
GET    /api/analytics/pricing-calendar/{id}
GET    /api/analytics/market-comparison/{id}
```

### Financials (HOST/ADMIN ACCESS)
```
GET    /api/financials/summary            # Financial summary
GET    /api/financials/transactions       # Transaction history
GET    /api/financials/payouts            # Payout history
GET    /api/financials/settings           # Payout settings
PUT    /api/financials/settings
POST   /api/financials/bank-accounts
GET    /api/financials/bank-accounts
POST   /api/financials/payouts/request
```

### Stripe Connect (HOST/ADMIN)
```
POST   /api/v1/stripe/host/create-account        # Create Stripe Express account
POST   /api/v1/stripe/host/onboarding-link       # Get onboarding URL
GET    /api/v1/stripe/host/account-status        # Check account status
POST   /api/v1/stripe/host/dashboard-link        # Get Stripe dashboard link
POST   /api/v1/stripe/webhooks                   # Stripe webhook receiver
```

### Payments (ADMIN ACCESS)
```
POST   /api/v1/payments/create-payment-intent    # Create payment for booking
POST   /api/v1/payments/confirm-payment          # Confirm payment
POST   /api/v1/payments/refund                   # Refund payment
```

### Payouts (ADMIN ACCESS)
```
POST   /api/v1/payouts/process-booking-payout    # Manually trigger payout
GET    /api/v1/payouts/host-payouts              # List host payouts
```

### External API (AI Agent Platform)
```
GET    /api/v1/properties/search
GET    /api/v1/properties/{id}
GET    /api/v1/properties/{id}/availability
POST   /api/v1/properties/{id}/calculate-pricing
POST   /api/v1/bookings
POST   /api/external/v1/bookings/{id}/process-payment
GET    /api/external/v1/bookings/{id}/payment-status
GET    /api/v1/external/hosts/{host_id}/pending-bookings
PUT    /api/v1/external/bookings/{id}/status
POST   /api/v1/external/bookings/{id}/auto-approve
GET    /api/v1/external/bookings/{id}/status
GET    /api/health
```

### Webhooks & Notifications
```
POST   /api/v1/external/webhook-subscriptions
GET    /api/v1/external/webhook-subscriptions
GET    /api/v1/external/webhook-subscriptions/{id}
PUT    /api/v1/external/webhook-subscriptions/{id}
DELETE /api/v1/external/webhook-subscriptions/{id}
POST   /api/v1/external/webhook-subscriptions/{id}/toggle
POST   /api/v1/external/webhook-subscriptions/{id}/test
POST   /api/v1/external/webhooks/test
GET    /api/v1/external/webhooks/statistics

POST   /api/v1/hosts/{host_id}/notifications
GET    /api/v1/hosts/{host_id}/notifications
PUT    /api/v1/hosts/{host_id}/notifications/{id}/read
PUT    /api/v1/hosts/{host_id}/notifications/read-all
DELETE /api/v1/hosts/{host_id}/notifications/{id}
GET    /api/v1/hosts/{host_id}/notifications/count
GET    /api/v1/hosts/{host_id}/notifications/statistics
POST   /api/v1/external/hosts/{host_id}/booking-notifications
POST   /api/v1/external/notifications/bulk
POST   /api/v1/external/notifications/cleanup
```

### Server-Sent Events (Real-time)
```
GET    /api/v1/hosts/{host_id}/events            # Connect to SSE stream
POST   /api/v1/hosts/{host_id}/events/send       # Send event to host
GET    /api/v1/sse/statistics                    # SSE connection stats
POST   /api/v1/external/sse/broadcast            # Broadcast to all hosts
```

### Upload/Storage
```
POST   /api/upload/property/{id}/images
POST   /api/upload/property/{id}/presigned-upload
GET    /api/upload/property/{id}/images
DELETE /api/upload/property/{id}/images/{s3_key}
POST   /api/upload/property/{id}/reorder-images
```

### Locations/Reference Data
```
GET    /api/locations/emirates
GET    /api/locations/emirates/{emirate}/areas
GET    /api/locations/popular
GET    /api/locations/amenities
GET    /api/locations/property-types
GET    /api/locations/search
GET    /api/locations/validate
GET    /api/locations/nearby/{emirate}/{area}
```

---

## 4. User Types & Roles

- **Host** - Property owners who list properties, receive bookings, and get payouts
- **Guest** - Users who book properties (not stored in `users` table, only in bookings)
- **Service Role** (Admin) - Full database access via Supabase service role key

**Note:** Current system uses Supabase Row Level Security (RLS). Super admin should use `SUPABASE_SERVICE_ROLE_KEY` to bypass RLS and access all data.

---

## 5. Key Super Admin Operations

### View All Data
```bash
# Get all properties (174 total)
GET /api/properties
Authorization: Bearer {API_KEY}

# Get all bookings
GET /api/bookings
Authorization: Bearer {API_KEY}

# Get all users (hosts)
# Use Supabase REST API directly:
GET https://bpomacnqaqzgeuahhlka.supabase.co/rest/v1/users
Authorization: Bearer {SUPABASE_SERVICE_ROLE_KEY}
apikey: {SUPABASE_SERVICE_ROLE_KEY}
```

### Manage Properties
```bash
# Suspend a property
PUT /api/properties/{property_id}
Authorization: Bearer {API_KEY}
Content-Type: application/json

{
  "status": "suspended"
}

# Reactivate a property
PUT /api/properties/{property_id}
{
  "status": "active"
}

# Delete a property
DELETE /api/properties/{property_id}
```

### Manage Bookings
```bash
# Cancel a booking
POST /api/bookings/{booking_id}/cancel
Authorization: Bearer {API_KEY}

# Update booking status
PUT /api/bookings/{booking_id}
{
  "status": "cancelled",
  "payment_status": "refunded"
}
```

### Financial Operations
```bash
# Refund a payment
POST /api/v1/payments/refund
Authorization: Bearer {API_KEY}
Content-Type: application/json

{
  "booking_id": "booking-uuid",
  "amount": 950.00,
  "reason": "Guest cancellation"
}

# View host earnings
GET /api/v1/payouts/host-payouts?user_id={host_user_id}
Authorization: Bearer {API_KEY}

# View all payouts (via Supabase)
GET https://bpomacnqaqzgeuahhlka.supabase.co/rest/v1/payouts
Authorization: Bearer {SUPABASE_SERVICE_ROLE_KEY}
```

### Platform Statistics
```bash
# Overall platform analytics
GET /api/analytics
Authorization: Bearer {API_KEY}

# SSE connection stats
GET /api/v1/sse/statistics
Authorization: Bearer {API_KEY}

# Webhook statistics
GET /api/v1/external/webhooks/statistics
Authorization: Bearer {API_KEY}
```

---

## 6. Integration Notes

### Authentication Methods
1. **API Key** - For application-level access (properties, bookings, analytics)
2. **Supabase Service Role** - For direct database access (users, advanced queries, RLS bypass)

### Payment Flow
- **Currency:** AED (UAE Dirham)
- **Platform Fee:** 15% of booking amount
- **Payout Timing:** 1 day after checkout
- **Payment Method:** Stripe Connect Express accounts

### Property Status Transitions
- `draft` → `active` (published)
- `active` → `inactive` (host paused)
- `active` → `suspended` (admin action)
- `suspended` → `active` (admin restored)

### Booking Status Transitions
- `pending` → `confirmed` (payment successful)
- `confirmed` → `completed` (after checkout)
- `pending/confirmed` → `cancelled` (by host/guest/admin)

---

## 7. Example: Super Admin Dashboard Query

```python
import requests

API_BASE = "https://api.host.krib.ae"
SUPABASE_URL = "https://bpomacnqaqzgeuahhlka.supabase.co"
API_KEY = "krib_prod_c4323aa1d8896254316e396995bf7f6fffacdaa8985ec09da4067da37f1e6ae8"
SUPABASE_KEY = "<REQUEST_SERVICE_ROLE_KEY>"

headers = {"Authorization": f"Bearer {API_KEY}"}
supabase_headers = {
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "apikey": SUPABASE_KEY
}

# Get platform overview
properties = requests.get(f"{API_BASE}/api/properties", headers=headers).json()
bookings = requests.get(f"{API_BASE}/api/bookings", headers=headers).json()
analytics = requests.get(f"{API_BASE}/api/analytics", headers=headers).json()

# Get all hosts with payout info
hosts = requests.get(
    f"{SUPABASE_URL}/rest/v1/users?select=*",
    headers=supabase_headers
).json()

# Get all pending payouts
payouts = requests.get(
    f"{SUPABASE_URL}/rest/v1/payouts?status=eq.pending&select=*",
    headers=supabase_headers
).json()

print(f"Total Properties: {len(properties)}")
print(f"Total Bookings: {len(bookings)}")
print(f"Total Hosts: {len(hosts)}")
print(f"Pending Payouts: {len(payouts)}")
```

---

## 8. Contact & Support

**Owner:** Mahmoud Omar  
**Backend API:** https://api.host.krib.ae  
**Frontend:** https://host.krib.ae  
**Stripe Webhook:** https://api.krib.ae/api/billing/webhook

