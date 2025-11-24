# Superadmin Guide

## Overview

The Krib Host Platform includes superadmin features for managing hosts, approving superhost requests, and platform configuration.

## User Roles

```sql
-- Roles in users table
role: 'user' | 'admin' | 'super_admin'
```

- **user**: Regular host (default)
- **admin**: Platform administrator
- **super_admin**: Full platform control

## Setting Up First Superadmin

Run in Supabase SQL Editor:

```sql
UPDATE public.users
SET role = 'super_admin'
WHERE email = 'your-admin-email@example.com';
```

## Superhost System

### Overview

The superhost system allows hosts to apply for verified status based on performance metrics.

### Eligibility Criteria

Hosts must meet ALL criteria:
- ≥1 active property
- ≥5 completed bookings
- Average rating ≥4.5
- Response rate ≥90%
- Cancellation rate ≤5%

### Configuration (Environment Variables)

```bash
# In backend environment
SUPERHOST_MIN_PROPERTIES=1
SUPERHOST_MIN_BOOKINGS=5
SUPERHOST_MIN_RATING=4.5
SUPERHOST_MIN_RESPONSE_RATE=90
SUPERHOST_MAX_CANCELLATION_RATE=5
```

### Admin Workflow

1. Host requests superhost verification via Settings page
2. Admin reviews request (future: dedicated admin panel)
3. Admin approves/rejects via API

### API Endpoints (Admin Only)

#### Get Pending Verification Requests

```http
GET /api/superhost/admin/requests?status=pending
Authorization: Bearer {admin_token}
```

#### Approve Request

```http
POST /api/superhost/admin/approve/{user_id}
Authorization: Bearer {admin_token}
```

#### Reject Request

```http
POST /api/superhost/admin/reject/{user_id}
Content-Type: application/json
Authorization: Bearer {admin_token}

{
  "reason": "Insufficient booking history"
}
```

## Messaging System

### Overview

AI-powered messaging system for guest-host communication.

### Features

- Real-time conversations
- AI-generated response suggestions
- Email notifications for new messages
- Archive conversations
- Unread message tracking

### Admin Monitoring

Future feature: Admin dashboard to monitor conversations and intervene if needed.

## Platform Configuration

### Dubai Market Multipliers

Configure market-based pricing via environment variables:

```bash
# Area Pricing Multipliers
AREA_MULT_PALM_JUMEIRAH=2.0
AREA_MULT_MARINA=1.6
AREA_MULT_DOWNTOWN=1.5
AREA_MULT_JBR=1.4
AREA_MULT_BUSINESS_BAY=1.2
AREA_MULT_JUMEIRAH=1.3
AREA_MULT_JLT=1.0
AREA_MULT_SILICON_OASIS=0.8
AREA_MULT_DEIRA=0.7
AREA_MULT_BURDUBAI=0.6

# Seasonal Multipliers
SEASON_MULT_PEAK_WINTER=1.5
SEASON_MULT_HIGH_WINTER=1.3
SEASON_MULT_SHOULDER=1.0
SEASON_MULT_LOW_SUMMER=0.7

# Base Analytics
BASE_ADR=120
ANALYTICS_TOP_PROPERTIES=5
COMPETITIVE_EXCELLENT_THRESHOLD=110
COMPETITIVE_GOOD_THRESHOLD=90
ANALYTICS_DEFAULT_BASELINE=1000
```

### Platform Fee

```bash
PLATFORM_FEE_PERCENTAGE=15.0  # 15% commission
PAYOUT_DELAY_DAYS=1
```

### Cache Configuration

```bash
# Cache TTL (seconds)
CACHE_TTL_USER_PROFILE=300
CACHE_TTL_PROPERTIES=180
CACHE_TTL_ANALYTICS=600
CACHE_TTL_MARKET_DATA=1800
CACHE_TTL_FINANCIAL_SUMMARY=300
CACHE_TTL_BOOKINGS=120
CACHE_TTL_PROPERTY_DETAILS=600
CACHE_TTL_SEARCH_RESULTS=180
```

### Rate Limits

```bash
RATE_LIMIT_AI_AGENT=200
RATE_LIMIT_DEFAULT=60
```

### Notification Settings

```bash
NOTIFICATION_EXPIRY_NEW_BOOKING=72
NOTIFICATION_EXPIRY_DEFAULT=168
```

## Email System

### Configuration

The platform uses Resend for transactional emails.

### Email Templates

1. **New Booking Notification**
   - Sent to host when new booking is created
   - Includes booking details and action link

2. **Payment Received**
   - Sent to host when payment is processed
   - Includes amount and financial dashboard link

### Customization

Edit templates in `backend/app/services/email_service.py`

## Database Management

### Backup Strategy

1. Supabase auto-backups (daily)
2. Manual exports before major migrations
3. Test migrations on staging first

### Common Queries

#### List All Superhosts

```sql
SELECT id, name, email, superhost_status, superhost_approved_at
FROM public.users
WHERE is_superhost = TRUE
ORDER BY superhost_approved_at DESC;
```

#### Pending Verification Requests

```sql
SELECT u.id, u.name, u.email, svr.status, svr.created_at, svr.message
FROM public.superhost_verification_requests svr
JOIN public.users u ON svr.user_id = u.id
WHERE svr.status = 'pending'
ORDER BY svr.created_at ASC;
```

#### Active Conversations

```sql
SELECT c.id, c.guest_name, c.guest_email, u.name as host_name, c.last_message_at, c.unread_count_host
FROM public.conversations c
JOIN public.users u ON c.host_id = u.id
WHERE c.status = 'active'
ORDER BY c.last_message_at DESC;
```

## Security Best Practices

1. **Never commit secrets** to git
2. **Rotate API keys** quarterly
3. **Monitor failed login attempts**
4. **Review admin actions** regularly
5. **Keep dependencies updated**

## Monitoring

### Key Metrics

- Active users
- Booking conversion rate
- Average response time
- Email delivery rate
- API error rate

### Logs

- Backend: Render logs
- Frontend: Browser console
- Database: Supabase logs
- Email: Resend dashboard

## Support

### User Support Workflow

1. User contacts support
2. Admin reviews issue
3. Admin can:
   - View user data (RLS allows admin access)
   - Modify bookings if needed
   - Adjust host settings
   - Send direct messages

### Emergency Procedures

#### Take Host Offline

```sql
UPDATE public.properties
SET status = 'suspended'
WHERE user_id = '{host_user_id}';
```

#### Cancel All Bookings

```sql
UPDATE public.bookings
SET status = 'cancelled'
WHERE property_id IN (
  SELECT id FROM public.properties WHERE user_id = '{host_user_id}'
)
AND status IN ('pending', 'confirmed');
```

