# Krib Host Platform - Setup Guide

## Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL (via Supabase)
- Redis
- Stripe Account
- Resend Account (for emails)
- OpenAI Account (for AI features)

## Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Variables

Create `backend/.env`:

```bash
# App
DEBUG=false
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_here

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Stripe
STRIPE_PUBLISHABLE_KEY=pk_...
STRIPE_SECRET_KEY=sk_...
STRIPE_WEBHOOK_SECRET=whsec_...
PLATFORM_FEE_PERCENTAGE=15.0

# Email (Resend)
RESEND_API_KEY=re_...
FROM_EMAIL=notifications@host.krib.ae
FROM_NAME=Krib Host Platform

# AI (OpenAI)
OPENAI_API_KEY=sk-...
AI_MODEL=gpt-4o-mini

# Redis
REDIS_URL=redis://localhost:6379
```

### Database Migrations

Run SQL migrations in Supabase SQL Editor:

```bash
supabase/migrations/*.sql
```

Run in order:
1. `20240117000001_initial_schema.sql`
2. `20251123000001_security_fixes.sql`
3. `20251123000002_performance_optimizations.sql`
4. `20251123000003_superhost_verification_fixed.sql`
5. `20251123000004_add_user_role.sql`
6. `20251124000001_add_profiles_and_messaging.sql`

### Start Backend

```bash
uvicorn main:app --reload
```

## Frontend Setup

```bash
cd frontend
npm install
```

### Environment Variables

Create `frontend/.env`:

```bash
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_anon_key
VITE_API_URL=https://api.host.krib.ae/api  # Or http://localhost:8000/api
```

### Start Frontend

```bash
npm run dev
```

## Production Deployment

### Backend (Render)

1. Create Web Service on Render
2. Set environment variables (see above)
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend (Render Static Site)

1. Create Static Site on Render
2. Build Command: `npm install && npm run build`
3. Publish Directory: `dist`
4. Add `_headers` file for caching

## Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Tests

```bash
cd frontend
npm run type-check
npm run build
```

### E2E Tests (Playwright)

```bash
cd frontend
npx playwright install
npx playwright test
```

## Troubleshooting

### Mixed Content Errors

- Ensure `VITE_API_URL` uses HTTPS in production
- Backend trusts `X-Forwarded-Proto` header

### Cache Issues

- Clear browser cache
- Hard refresh (Cmd+Shift+R or Ctrl+Shift+R)
- Check Render build logs for new hash

### Database Connection

- Verify Supabase credentials
- Check RLS policies are enabled
- Ensure migrations are run in order

