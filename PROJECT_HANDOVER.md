# Krib Host Dashboard - Project Documentation

## System Overview

Property rental management platform for hosts with integrated Stripe Connect payment processing.

**Backend:** https://api.host.krib.ae (Render)  
**Frontend:** https://host.krib.ae (Render)  
**Database:** Supabase PostgreSQL  
**Payments:** Stripe Connect Express

---

## Architecture

### Backend (FastAPI + Python)
- Location: `/backend`
- Database: Supabase PostgreSQL with Row Level Security
- File Storage: Supabase S3-compatible storage
- Payment Processing: Stripe Connect Express (15% platform fee, 1-day payout delay)
- Authentication: Supabase Auth + JWT
- Real-time: Server-Sent Events (SSE)
- Background Jobs: Celery with Redis
- API Documentation: `/docs` endpoint

### Frontend (React + TypeScript)
- Location: `/frontend`
- Framework: React 18 with Vite
- UI: Tailwind CSS + shadcn/ui components
- State: React Context API
- Routing: React Router

### Database Schema
Core tables: `users`, `properties`, `bookings`, `reviews`, `payouts`, `stripe_events`, `property_analytics`, `webhook_subscriptions`, `host_notifications`

---

## Environment Variables

### Backend (Render)
```
SUPABASE_URL=https://bpomacnqaqzgeuahhlka.supabase.co
SUPABASE_ANON_KEY=[from Supabase dashboard]
SUPABASE_SERVICE_ROLE_KEY=[from Supabase dashboard]

STRIPE_PUBLISHABLE_KEY=[from Stripe dashboard]
STRIPE_SECRET_KEY=[from Stripe dashboard]
STRIPE_WEBHOOK_SECRET=[from Stripe webhook configuration]

KRIB_AI_AGENT_API_KEY=krib_prod_c4323aa1d8896254316e396995bf7f6fffacdaa8985ec09da4067da37f1e6ae8
ENVIRONMENT=production

PLATFORM_FEE_PERCENTAGE=15.0
PAYOUT_DELAY_DAYS=1
CURRENCY=AED
CONNECT_REFRESH_URL=https://host.krib.ae/dashboard/financials
CONNECT_RETURN_URL=https://host.krib.ae/dashboard/financials

REDIS_URL=[Render Redis instance]
OPENAI_API_KEY=[optional]
ANTHROPIC_API_KEY=[optional]
```

### Frontend (Render)
```
VITE_API_URL=https://api.host.krib.ae/api
VITE_SUPABASE_URL=https://bpomacnqaqzgeuahhlka.supabase.co
VITE_SUPABASE_ANON_KEY=[from Supabase dashboard]
```

---

## API Endpoints

### Host Dashboard APIs
```
POST   /api/auth/signup                           - Create host account
POST   /api/auth/signin                           - Host login
GET    /api/properties                            - List host properties
POST   /api/properties                            - Create property
PUT    /api/properties/{id}                       - Update property
GET    /api/bookings                              - List bookings
POST   /api/bookings/{id}/confirm                 - Confirm booking
GET    /api/financials/summary                    - Financial overview
GET    /api/v1/payouts/host-payouts              - Payout history
POST   /api/upload/property/{id}/images          - Upload images
```

### Stripe Connect APIs
```
POST   /api/v1/stripe/host/create-account        - Create Stripe Express account
POST   /api/v1/stripe/host/onboarding-link       - Get Stripe onboarding URL
GET    /api/v1/stripe/host/account-status        - Check Stripe account status
POST   /api/v1/stripe/host/dashboard-link        - Access Stripe dashboard
POST   /api/billing/webhook                      - Stripe webhook receiver
```

### External Platform APIs (AI Agent)
```
GET    /api/v1/properties/search                 - Search properties
GET    /api/v1/properties/{id}                   - Property details
GET    /api/v1/properties/{id}/availability      - Check availability
POST   /api/v1/properties/{id}/calculate-pricing - Calculate pricing
POST   /api/v1/bookings                          - Create booking
POST   /api/external/v1/bookings/{id}/process-payment - Process payment
```

Authentication: Bearer token in Authorization header

---

## Payment Flow

### Host Onboarding
1. Host clicks "Set up payouts" in dashboard
2. Backend creates Stripe Express account
3. Host redirected to Stripe for KYC verification
4. Upon completion, redirects to: https://host.krib.ae/dashboard/financials
5. Webhook `account.updated` updates database

### Payment Processing
1. External platform creates booking via API
2. External platform processes payment via API
3. Booking status updated to `confirmed`
4. Background job schedules payout for 1 day after checkout
5. Platform fee (15%) deducted, host receives 85%

### Payout Execution
1. Background job triggers 1 day after checkout
2. Stripe transfer created to host's connected account
3. Payout record created in database
4. Webhook `transfer.paid` confirms completion

---

## Stripe Dashboard Configuration

### Required Webhook Events
URL: `https://api.krib.ae/api/billing/webhook`

Events to subscribe:
- `account.updated`
- `payment_intent.succeeded`
- `payment_intent.payment_failed`
- `charge.succeeded`
- `charge.refunded`
- `transfer.created`
- `transfer.paid`
- `transfer.failed`
- `payout.paid`
- `payout.failed`

Copy webhook signing secret to `STRIPE_WEBHOOK_SECRET` environment variable.

---

## Deployment

### Backend (Render)
- Auto-deploys from GitHub main branch
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Add environment variables in Render dashboard

### Frontend (Render)
- Auto-deploys from GitHub main branch
- Build Command: `cd frontend && npm install && npm run build`
- Publish Directory: `frontend/dist`
- Add environment variables in Render dashboard

### Database Migrations
Apply SQL migrations in order from `supabase/migrations/` directory via Supabase dashboard or CLI.

---

## Key Files

### Backend
- `backend/main.py` - FastAPI application entry point
- `backend/app/api/routes/` - API route handlers
- `backend/app/services/` - Business logic services
- `backend/app/core/` - Configuration and database
- `backend/app/models/` - Pydantic schemas
- `backend/requirements.txt` - Python dependencies
- `backend/render.yaml` - Render deployment configuration

### Frontend
- `frontend/src/main.tsx` - React application entry
- `frontend/src/App.tsx` - Main app component
- `frontend/src/components/` - React components
- `frontend/src/contexts/AppContext.tsx` - API client and state
- `frontend/package.json` - Node dependencies
- `frontend/vite.config.ts` - Vite configuration

### Database
- `supabase/migrations/` - SQL schema migrations
- `supabase/config.toml` - Supabase configuration

### Documentation
- `HOST_DASHBOARD_INFO_NEEDED.md` - Super admin integration guide
- `setup_production_api_keys.md` - External API integration guide
- `Attributions.md` - Third-party licenses

---

## External Platform Integration

The external AI platform connects via the External Platform APIs to search properties and create bookings.

### Authentication
API Key: `krib_prod_c4323aa1d8896254316e396995bf7f6fffacdaa8985ec09da4067da37f1e6ae8`

### Payment Integration
After booking creation, the external platform calls:
```
POST /api/external/v1/bookings/{booking_id}/process-payment
```

This triggers:
- Booking confirmation
- Host notification
- Payout scheduling

Platform fee and payout calculation handled automatically.

---

## Database Access

### Supabase Dashboard
URL: https://supabase.com/dashboard/project/bpomacnqaqzgeuahhlka

### Direct Database Access (Super Admin)
Use service role key for full access bypassing Row Level Security.

### Row Level Security (RLS)
All tables have RLS enabled. Users can only access their own data unless using service role key.

---

## Monitoring & Logs

### Backend Logs
View in Render dashboard under "Logs" tab.

### Frontend Logs
View in browser console and Render deployment logs.

### Database Logs
View in Supabase dashboard under "Logs" section.

### Stripe Events
View in Stripe dashboard under "Developers > Events" and in `stripe_events` database table.

---

## Troubleshooting

### Payment Issues
1. Verify Stripe keys are correct in environment variables
2. Check webhook secret matches Stripe dashboard
3. Verify webhook URL is accessible: https://api.krib.ae/api/billing/webhook
4. Check `stripe_events` table for webhook delivery failures

### CORS Issues
Frontend domain must be listed in backend CORS configuration in `backend/main.py`.

### Database Connection Issues
Verify Supabase credentials and check database connection limits.

### Image Upload Issues
Verify Supabase storage bucket is public and storage policies are correct.

---

## Support Contacts

**Supabase Project:** bpomacnqaqzgeuahhlka  
**Render Backend:** api.host.krib.ae  
**Render Frontend:** host.krib.ae  
**Stripe Account:** [Configure webhook at dashboard.stripe.com]

---

## Security Configuration

### Critical Security Fixes Required

**Apply migration:** `supabase/migrations/20251123000001_security_fixes.sql`

This fixes:
1. Row Level Security not enabled on reference tables
2. Function search_path vulnerabilities (10 functions)

See `SECURITY_FIXES.md` for detailed instructions.

### Auth Security Settings

Configure in Supabase Dashboard → Authentication:
1. Set OTP expiry to 600 seconds (10 minutes)
2. Enable "Check password against HaveIBeenPwned"

### Database Upgrade

Schedule Postgres upgrade in Supabase Dashboard → Settings → Infrastructure when security patches are available.

---

## Production Checklist

- [ ] Applied security migration (20251123000001_security_fixes.sql)
- [ ] Verified RLS enabled on all reference tables
- [ ] Configured Auth OTP expiry < 1 hour
- [ ] Enabled leaked password protection
- [ ] All environment variables set in Render
- [ ] Stripe webhook configured and tested
- [ ] Database migrations applied
- [ ] Frontend deployed and accessible
- [ ] Backend deployed and accessible
- [ ] Test host can create account
- [ ] Test host can onboard with Stripe
- [ ] Test property creation
- [ ] Test booking creation via API
- [ ] Test payment processing
- [ ] Verify payout scheduling
- [ ] Check webhook delivery logs
- [ ] Run Supabase linter (0 errors expected)

