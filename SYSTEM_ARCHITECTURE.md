# 🏠 Krib AI - Property Management System Architecture

## 📋 Table of Contents
- [System Overview](#system-overview)
- [Architecture & Tech Stack](#architecture--tech-stack)
- [Frontend Structure](#frontend-structure)
- [Backend Structure](#backend-structure)
- [Database Design](#database-design)
- [Key Features](#key-features)
- [UAE Location System](#uae-location-system)
- [AI Integration](#ai-integration)
- [Authentication & Security](#authentication--security)
- [Design System](#design-system)
- [Deployment & Scalability](#deployment--scalability)
- [API Documentation](#api-documentation)

---

## 🎯 System Overview

**Krib AI** is a comprehensive property management platform designed specifically for the UAE real estate market. It combines modern web technologies with AI-powered features to help property owners manage their rental properties efficiently.

### Core Purpose
- **Property Management**: Add, edit, and manage rental properties
- **UAE-Focused**: Specialized for UAE emirates and local market needs
- **AI-Enhanced**: Automated property descriptions and market insights
- **Professional Tools**: Financial tracking, analytics, and booking management

---

## 🏗️ Architecture & Tech Stack

### **Frontend (React/TypeScript)**
```
Frontend/
├── React 18 + TypeScript
├── Vite (Build Tool)
├── Tailwind CSS + Shadcn UI
├── React Router DOM (Navigation)
├── Context API (State Management)
└── Supabase Client SDK
```

### **Backend (Python/FastAPI)**
```
Backend/
├── FastAPI (Web Framework)
├── Pydantic (Data Validation)
├── Supabase (Database & Auth)
├── Redis (Caching & Rate Limiting)
├── Celery (Background Jobs)
├── Docker (Containerization)
└── AI Services (OpenAI/Anthropic)
```

### **Database (PostgreSQL)**
```
Database/
├── Supabase PostgreSQL
├── Row Level Security (RLS)
├── Real-time subscriptions
├── File storage & CDN
└── Authentication system
```

### **Deployment**
```
Deployment/
├── Frontend: Vercel
├── Backend: Render
├── Database: Supabase Cloud
├── Monitoring: Sentry
└── CDN: Supabase Storage
```

---

## 🎨 Frontend Structure

### **Component Architecture**
```
src/
├── components/
│   ├── ui/                     # Shadcn UI components
│   ├── AddPropertyWizard.tsx   # Multi-step property creation
│   ├── DashboardOverview.tsx   # Main dashboard
│   ├── PropertyList.tsx        # Property management
│   ├── AnalyticsDashboard.tsx  # Market insights
│   ├── FinancialDashboard.tsx  # Financial tracking
│   ├── AuthForm.tsx           # Authentication
│   └── SettingsPage.tsx       # User settings
├── contexts/
│   └── AppContext.tsx         # Global state management
├── services/
│   ├── api.ts                 # API client
│   ├── auth.ts                # Authentication
│   └── imageUpload.ts         # File uploads
└── styles/
    └── globals.css            # Krib design system
```

### **Key Frontend Features**

#### **1. Property Creation Wizard**
Multi-step process for adding properties:
1. **Basic Info** - Title, address, UAE location selection
2. **Details** - Bedrooms, bathrooms, capacity
3. **Photos** - Image upload with preview
4. **Amenities** - UAE-specific features
5. **Pricing** - AED-based pricing
6. **Preview** - Final review before publishing

#### **2. UAE Location System**
- **7 Emirates**: Dubai, Abu Dhabi, Sharjah, Ajman, Ras Al Khaimah, Fujairah, Umm Al Quwain
- **200+ Areas**: Major districts within each emirate
- **Validation**: Ensures only valid Emirates/Area combinations
- **Fallback Data**: Works offline with local data

#### **3. State Management (Context API)**
```typescript
interface AppContextType {
  // Authentication
  user: User | null
  signIn: (email: string, password: string) => Promise<void>
  signInWithGoogle: () => Promise<void>
  
  // Property Management
  properties: Property[]
  createProperty: (data: PropertyCreate) => Promise<Property>
  loadProperties: () => Promise<void>
  
  // UAE Location Services
  getUAEEmirates: () => Promise<Emirates[]>
  getEmirateAreas: (emirate: string) => Promise<string[]>
  
  // AI Services
  generateAIDescription: (propertyData) => Promise<string>
}
```

---

## ⚙️ Backend Structure

### **FastAPI Application Structure**
```
backend/
├── app/
│   ├── api/routes/
│   │   ├── auth.py           # Authentication endpoints
│   │   ├── properties.py     # Property CRUD operations
│   │   ├── locations.py      # UAE location services
│   │   ├── analytics.py      # Market analytics
│   │   ├── financials.py     # Financial tracking
│   │   └── users.py          # User management
│   ├── core/
│   │   ├── config.py         # Configuration
│   │   ├── database.py       # Database initialization
│   │   ├── supabase_client.py # Supabase connection
│   │   ├── redis_client.py   # Redis connection
│   │   └── monitoring.py     # Sentry & metrics
│   ├── models/
│   │   └── schemas.py        # Pydantic models
│   ├── services/
│   │   ├── ai_service.py     # AI integrations
│   │   └── dubai_market.py   # Market intelligence
│   └── constants/
│       └── uae_locations.py  # UAE data
└── main.py                   # FastAPI app entry
```

### **API Endpoints Overview**

#### **Authentication (`/api/auth`)**
- `POST /api/auth/signin` - Email/password authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/google` - Google OAuth
- `GET /api/auth/me` - Get current user

#### **Properties (`/api/properties`)**
- `GET /api/properties` - List user properties
- `POST /api/properties` - Create new property
- `PUT /api/properties/{id}` - Update property
- `DELETE /api/properties/{id}` - Delete property

#### **UAE Locations (`/api/locations`)**
- `GET /api/locations/emirates` - List all emirates
- `GET /api/locations/emirates/{emirate}/areas` - Get areas by emirate
- `GET /api/locations/popular` - Popular locations
- `GET /api/locations/search?q={query}` - Search locations

#### **Analytics (`/api/analytics`)**
- `GET /api/analytics/overview` - Dashboard metrics
- `GET /api/analytics/market/{emirate}` - Market intelligence
- `GET /api/analytics/pricing/{property_id}` - Price optimization

---

## 🗄️ Database Design

### **Core Tables**

#### **Users Table**
```sql
CREATE TABLE public.users (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  phone TEXT,
  avatar_url TEXT,
  settings JSONB DEFAULT '{}'::jsonb,
  total_revenue DECIMAL(10,2) DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### **Properties Table**
```sql
CREATE TABLE public.properties (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT,
  address TEXT NOT NULL,
  city TEXT NOT NULL,           -- UAE Area/City
  state TEXT NOT NULL,          -- UAE Emirate
  country TEXT NOT NULL,        -- 'UAE'
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  property_type TEXT NOT NULL,  -- villa, apartment, etc.
  bedrooms INTEGER NOT NULL DEFAULT 0,
  bathrooms DECIMAL(3,1) NOT NULL DEFAULT 0,
  max_guests INTEGER NOT NULL DEFAULT 1,
  price_per_night DECIMAL(10,2) NOT NULL,
  amenities TEXT[] DEFAULT '{}',
  images TEXT[] DEFAULT '{}',
  status TEXT DEFAULT 'draft',
  rating DECIMAL(3,2) DEFAULT 0,
  review_count INTEGER DEFAULT 0,
  booking_count INTEGER DEFAULT 0,
  total_revenue DECIMAL(10,2) DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### **Bookings Table**
```sql
CREATE TABLE public.bookings (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  property_id UUID REFERENCES public.properties(id) ON DELETE CASCADE,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  guest_name TEXT NOT NULL,
  guest_email TEXT NOT NULL,
  check_in DATE NOT NULL,
  check_out DATE NOT NULL,
  guests INTEGER NOT NULL,
  total_amount DECIMAL(10,2) NOT NULL,
  status TEXT DEFAULT 'pending',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### **Row Level Security (RLS)**
```sql
-- Users can only access their own data
ALTER TABLE public.properties ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own properties" ON public.properties
  FOR ALL USING (user_id = auth.uid());

ALTER TABLE public.bookings ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own bookings" ON public.bookings
  FOR ALL USING (user_id = auth.uid());
```

---

## 🇦🇪 UAE Location System

### **Emirates Data Structure**
```python
UAE_EMIRATES = {
    "Dubai": {
        "name": "Dubai",
        "name_ar": "دبي",
        "code": "DXB",
        "major_areas": [
            "Downtown Dubai", "Dubai Marina", "Jumeirah Beach Residence (JBR)",
            "Business Bay", "Palm Jumeirah", "Jumeirah", "Arabian Ranches",
            "Dubai Hills Estate", "City Walk", "DIFC", "Al Barsha"
            # ... 200+ total areas
        ]
    },
    "Abu Dhabi": {
        "name": "Abu Dhabi",
        "name_ar": "أبو ظبي", 
        "code": "AUH",
        "major_areas": [
            "Abu Dhabi City", "Yas Island", "Saadiyat Island", 
            "Al Reem Island", "Khalifa City", "Al Raha"
            # ... more areas
        ]
    }
    # ... other emirates
}
```

### **Location Validation**
- **Frontend**: Dynamic dropdowns with Emirates → Areas cascade
- **Backend**: Validation ensures only valid combinations
- **Fallback**: Local data works when API is unavailable
- **Future**: Google Places API integration planned

### **UAE-Specific Features**
- **Property Types**: Villa, Townhouse, Penthouse, Compound, etc.
- **Amenities**: Maid's Room, Driver's Room, Central AC, 24/7 Security
- **Currency**: AED pricing throughout the system
- **Market Intelligence**: Dubai-specific insights and forecasting

---

## 🤖 AI Integration

### **AI-Powered Property Descriptions**
```python
class AIService:
    async def generate_property_description(self, property_data):
        # Enhanced fallback with dynamic content
        space_details = self._get_space_details(property_data)
        amenity_highlights = self._get_amenity_highlights(property_data)
        location_benefits = self._get_location_benefits(property_data.city)
        
        return f"""
        {space_details}
        
        This exceptional {property_data.property_type} features {amenity_highlights}.
        
        Located in the heart of {property_data.city}, {location_benefits}.
        
        Starting from AED {property_data.price_per_night} per night.
        """
```

### **Market Intelligence**
- **Seasonal Patterns**: Dubai peak/off-peak seasons
- **Event-Based Pricing**: DSF, Expo, holidays impact
- **Area Multipliers**: Different emirates pricing factors
- **Occupancy Forecasting**: ML-based predictions

---

## 🔐 Authentication & Security

### **Supabase Authentication**
- **Email/Password**: Traditional authentication
- **Google OAuth**: Social login integration
- **JWT Tokens**: Secure session management
- **Row Level Security**: Database-level access control

### **User Types & Permissions**
```typescript
interface User {
  id: string
  email: string
  name: string
  phone?: string
  avatar_url?: string
  settings?: {
    notifications?: UserNotifications
    preferences?: UserPreferences
  }
  identities?: AuthIdentity[] // OAuth provider detection
}
```

### **Password Management**
- **Email Users**: Standard password change with current password verification
- **OAuth Users**: Can set password without current password requirement
- **Provider Detection**: Checks `identities` to determine auth method

---

## 🎨 Design System

### **Krib Brand Colors**
```css
:root {
  --krib-lime: #B8FF00;        /* Primary brand color */
  --krib-lime-light: #CBFC50;  /* Light variant */
  --krib-lime-soft: rgba(184, 255, 0, 0.1); /* Transparent */
  --krib-black: #111111;       /* Brand black */
  --krib-gray-light: #F8F9FA;  /* Background */
}
```

### **Background System**
- **Auth Pages**: Realistic ink splash texture using CSS clip-path
- **Dashboard**: Clean geometric pattern with minimal opacity
- **Cards**: Enhanced shadows with lime accent borders
- **Buttons**: Gradient lime with hover animations

### **Component Standards**
- **Cards**: `.krib-card` with lime bottom border
- **Buttons**: `.krib-button-primary` with gradient
- **Inputs**: Consistent border-radius and focus states
- **Typography**: Clean, readable font hierarchy

---

## 🚀 Deployment & Scalability

### **Current Deployment**
```yaml
# Frontend (Vercel)
frontend:
  platform: Vercel
  build: npm run build
  env: production

# Backend (Render)
backend:
  platform: Render
  runtime: Python 3.11
  build: pip install -r requirements.txt
  start: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### **Scalability Features**
- **Redis Caching**: Property and user data caching
- **Background Jobs**: Celery for AI processing
- **Rate Limiting**: API protection with Redis
- **Monitoring**: Sentry error tracking & Prometheus metrics
- **Database Optimization**: Proper indexing and RLS

### **Performance Optimizations**
- **Frontend**: Code splitting, lazy loading, optimized images
- **Backend**: Async operations, connection pooling, caching
- **Database**: Indexed queries, efficient RLS policies
- **CDN**: Supabase storage for images and assets

---

## 📚 API Documentation

### **Request/Response Format**
All API endpoints follow REST conventions with JSON payloads:

```typescript
// Property Creation Request
interface PropertyCreate {
  title: string
  address: string
  city: string        // UAE area
  state: string       // UAE emirate
  country: "UAE"      // Fixed to UAE
  property_type: PropertyType
  bedrooms: number
  bathrooms: number
  max_guests: number
  price_per_night: number
  amenities: string[]
  images: string[]
}

// Standard API Response
interface APIResponse<T> {
  data: T
  success: boolean
  message?: string
  error?: string
}
```

### **Error Handling**
```python
# Standardized error responses
class APIError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

# Common HTTP status codes
200: Success
201: Created
400: Bad Request (validation errors)
401: Unauthorized
403: Forbidden
404: Not Found
500: Internal Server Error
```

---

## 🔮 Future Enhancements

### **Planned Features**
1. **Google Places API**: Real address autocomplete and geocoding
2. **Advanced Analytics**: Machine learning market predictions
3. **Mobile App**: React Native application
4. **Payment Integration**: Stripe for booking payments
5. **Messaging System**: Host-guest communication
6. **Multi-language**: Arabic language support
7. **Advanced Booking**: Calendar integration and availability management

### **Technical Roadmap**
1. **Microservices**: Break down monolithic backend
2. **GraphQL**: More efficient data fetching
3. **Real-time Features**: WebSocket integration
4. **Advanced Caching**: Redis cluster setup
5. **CI/CD Pipeline**: Automated testing and deployment

---

## 📞 Support & Maintenance

### **Monitoring & Logging**
- **Sentry**: Error tracking and performance monitoring
- **Prometheus**: Custom metrics and alerting
- **Health Checks**: API endpoint monitoring
- **Database Monitoring**: Query performance and connection health

### **Development Workflow**
1. **Local Development**: Docker-compose setup
2. **Testing**: Unit tests with pytest (backend) and Jest (frontend)
3. **Code Quality**: ESLint, Prettier, Black, mypy
4. **Version Control**: Git with conventional commits
5. **Deployment**: Automatic deployment on main branch push

---

## 🎯 Conclusion

The Krib AI system represents a modern, scalable solution for property management in the UAE market. By combining cutting-edge web technologies with local market expertise and AI enhancements, it provides property owners with a comprehensive platform for managing their rental business efficiently.

The system's architecture emphasizes:
- **Performance**: Fast, responsive user experience
- **Scalability**: Built to grow with user demands
- **Security**: Enterprise-grade data protection
- **Usability**: Intuitive, UAE-focused interface
- **Maintainability**: Clean, well-documented codebase

For technical questions or contributions, please refer to the development team or check the repository documentation.

---

*Last Updated: January 2025*
*Version: 1.0.0*
*Environment: Production*
