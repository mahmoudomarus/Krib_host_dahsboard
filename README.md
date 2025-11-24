# Krib Host Platform

Enterprise-grade property management platform for short-term rental hosts in the UAE.

## Features

- **Property Management**: Multi-property dashboard with image management
- **Booking System**: Complete reservation workflow with status tracking
- **Advanced Analytics**: AI-powered insights and Dubai market intelligence
- **Financial Dashboard**: Revenue tracking, Stripe Connect integration, automated payouts
- **Messaging System**: Guest-host communication with AI response suggestions
- **Superhost Program**: Performance-based verification system
- **Market Intelligence**: Real-time Dubai market data and pricing recommendations

## Tech Stack

**Frontend:**
- React 18 + TypeScript
- Vite
- TailwindCSS + shadcn/ui
- Recharts
- Supabase Auth

**Backend:**
- FastAPI (Python 3.11)
- PostgreSQL (Supabase)
- Redis (caching)
- Stripe Connect (payments)
- Resend (emails)
- OpenAI (AI features)

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL (Supabase account)
- Redis
- Stripe account
- Resend account
- OpenAI account

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/krib-host-platform.git
cd krib-host-platform

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp env_example.txt .env
# Edit .env with your credentials
uvicorn main:app --reload

# Frontend setup (new terminal)
cd frontend
npm install
cp env.example .env
# Edit .env with your credentials
npm run dev
```

Visit:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Documentation

Comprehensive documentation is available in the `/docs` directory:

- **[Setup Guide](docs/SETUP.md)**: Complete installation and deployment guide
- **[Superadmin Guide](docs/SUPERADMIN_GUIDE.md)**: Platform administration and configuration
- **[API Documentation](docs/API_DOCUMENTATION.md)**: REST API reference for integrations

## Deployment

### Production URLs

- Frontend: https://host.krib.ae
- Backend API: https://api.host.krib.ae
- Database: Supabase (managed PostgreSQL)

### Deployment Platforms

- Frontend: Render (Static Site)
- Backend: Render (Web Service)
- Database: Supabase
- Redis: Redis Cloud or Render

See [Setup Guide](docs/SETUP.md) for detailed deployment instructions.

## Environment Variables

### Required Backend Variables

```bash
# Core
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Stripe
STRIPE_SECRET_KEY=sk_...
STRIPE_WEBHOOK_SECRET=whsec_...
PLATFORM_FEE_PERCENTAGE=15.0

# Email
RESEND_API_KEY=re_...
FROM_EMAIL=notifications@host.krib.ae

# AI
OPENAI_API_KEY=sk-...
```

### Required Frontend Variables

```bash
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_anon_key
VITE_API_URL=https://api.host.krib.ae/api
```

See [Setup Guide](docs/SETUP.md) for complete list of environment variables.

## Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Type Checking

```bash
cd frontend
npm run type-check
```

### E2E Tests

```bash
cd frontend
npx playwright install
npx playwright test
```

## CI/CD

GitHub Actions pipeline includes:
- Automated testing (backend + frontend)
- Code quality checks (Black, Flake8, ESLint)
- Security auditing
- Automated deployment to Render

## Key Features

### Property Management
- Create, edit, delete properties
- Multi-image upload
- UAE location picker (Emirates/Areas)
- Real-time availability calendar
- Amenities and property type selection

### Booking System
- Complete booking workflow
- Status management (pending, confirmed, cancelled, completed)
- Guest information tracking
- Internal notes for hosts
- Email notifications

### Analytics Dashboard
- Revenue trends and forecasts
- Occupancy rates
- Market comparison
- Seasonal insights
- Dubai-specific market data
- AI-powered recommendations

### Financial Management
- Stripe Connect integration
- Automated commission calculation (15% platform fee)
- Real-time earnings tracking
- Transaction history
- Payout management

### Messaging System
- Guest-host communication
- AI-powered response suggestions
- Unread message tracking
- Email notifications
- Conversation archiving

### Superhost Program
- Automatic eligibility checking
- Performance metrics tracking
- Admin approval workflow
- Verified badge display

## Security Features

- Row Level Security (RLS) on all database tables
- JWT-based authentication
- Secure secret generation
- Rate limiting
- SQL injection protection
- XSS protection
- CORS configuration
- Secure password hashing

## Performance Optimizations

- Redis caching for frequently accessed data
- Optimized database queries with proper indexes
- CDN caching for static assets
- Lazy loading for images
- Code splitting for frontend

## Contributing

This is a proprietary project. For access or contributions, contact the development team.

## License

Proprietary - All rights reserved

## Support

For support or questions:
- Technical Documentation: See `/docs` directory
- Email: dev@krib.ae

## Architecture

```
┌─────────────────┐
│  React Frontend │ (Vite + TypeScript)
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│  FastAPI Backend│ (Python)
└────────┬────────┘
         │
    ┌────┴──────┬──────────┬────────────┐
    ▼           ▼          ▼            ▼
┌────────┐  ┌────────┐  ┌──────┐   ┌────────┐
│Supabase│  │ Redis  │  │Stripe│   │ OpenAI │
└────────┘  └────────┘  └──────┘   └────────┘
(PostgreSQL)  (Cache)   (Payments)    (AI)
```

## Project Status

✅ Production Ready
- All core features implemented
- Security audited
- Performance optimized
- Documentation complete
- CI/CD pipeline active

## Roadmap

Future enhancements:
- Mobile app (React Native)
- Advanced admin dashboard
- Multi-language support
- Calendar sync with Airbnb/Booking.com
- Automated pricing optimization
- Guest review system
- WhatsApp integration

---

**Built with ❤️ for UAE property hosts**
