-- RentalAI Database Schema
-- Initial migration to create all tables and policies

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    settings JSONB DEFAULT '{
        "notifications": {
            "bookings": true,
            "marketing": false,
            "system_updates": true
        },
        "preferences": {
            "currency": "USD",
            "timezone": "America/New_York",
            "language": "English"
        }
    }'::jsonb,
    total_revenue DECIMAL(12,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Properties table
CREATE TABLE IF NOT EXISTS public.properties (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    title TEXT NOT NULL CHECK (length(title) >= 3),
    description TEXT,
    address TEXT NOT NULL CHECK (length(address) >= 5),
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    country TEXT NOT NULL DEFAULT 'USA',
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    property_type TEXT NOT NULL CHECK (property_type IN ('apartment', 'house', 'condo', 'villa', 'studio', 'cabin', 'other')),
    bedrooms INTEGER NOT NULL DEFAULT 0 CHECK (bedrooms >= 0 AND bedrooms <= 20),
    bathrooms DECIMAL(3,1) NOT NULL DEFAULT 0 CHECK (bathrooms >= 0 AND bathrooms <= 20),
    max_guests INTEGER NOT NULL DEFAULT 1 CHECK (max_guests >= 1 AND max_guests <= 50),
    price_per_night DECIMAL(10,2) NOT NULL CHECK (price_per_night > 0 AND price_per_night <= 10000),
    amenities TEXT[] DEFAULT '{}',
    images TEXT[] DEFAULT '{}',
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'inactive', 'suspended')),
    rating DECIMAL(3,2) DEFAULT 0 CHECK (rating >= 0 AND rating <= 5),
    review_count INTEGER DEFAULT 0 CHECK (review_count >= 0),
    booking_count INTEGER DEFAULT 0 CHECK (booking_count >= 0),
    total_revenue DECIMAL(12,2) DEFAULT 0 CHECK (total_revenue >= 0),
    views_count INTEGER DEFAULT 0 CHECK (views_count >= 0),
    featured BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Bookings table
CREATE TABLE IF NOT EXISTS public.bookings (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    property_id UUID REFERENCES public.properties(id) ON DELETE CASCADE NOT NULL,
    guest_name TEXT NOT NULL CHECK (length(guest_name) >= 1),
    guest_email TEXT NOT NULL CHECK (guest_email ~* '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$'),
    guest_phone TEXT,
    check_in DATE NOT NULL,
    check_out DATE NOT NULL CHECK (check_out > check_in),
    nights INTEGER GENERATED ALWAYS AS (check_out - check_in) STORED,
    guests INTEGER NOT NULL CHECK (guests >= 1 AND guests <= 50),
    total_amount DECIMAL(10,2) NOT NULL CHECK (total_amount >= 0),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'cancelled', 'completed', 'no_show')),
    payment_status TEXT DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'refunded', 'partially_refunded')),
    special_requests TEXT,
    internal_notes TEXT,
    booking_source TEXT DEFAULT 'direct',
    commission_rate DECIMAL(5,4) DEFAULT 0,
    confirmed_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    cancellation_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Reviews table
CREATE TABLE IF NOT EXISTS public.reviews (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    property_id UUID REFERENCES public.properties(id) ON DELETE CASCADE NOT NULL,
    booking_id UUID REFERENCES public.bookings(id) ON DELETE SET NULL,
    guest_name TEXT NOT NULL,
    guest_email TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    pros TEXT,
    cons TEXT,
    response_from_host TEXT,
    is_verified BOOLEAN DEFAULT false,
    is_featured BOOLEAN DEFAULT false,
    helpful_votes INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Property analytics table for tracking daily metrics
CREATE TABLE IF NOT EXISTS public.property_analytics (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    property_id UUID REFERENCES public.properties(id) ON DELETE CASCADE NOT NULL,
    date DATE NOT NULL,
    views INTEGER DEFAULT 0 CHECK (views >= 0),
    bookings INTEGER DEFAULT 0 CHECK (bookings >= 0),
    revenue DECIMAL(10,2) DEFAULT 0 CHECK (revenue >= 0),
    occupancy_rate DECIMAL(5,2) DEFAULT 0 CHECK (occupancy_rate >= 0 AND occupancy_rate <= 100),
    avg_daily_rate DECIMAL(10,2) DEFAULT 0 CHECK (avg_daily_rate >= 0),
    inquiries INTEGER DEFAULT 0 CHECK (inquiries >= 0),
    conversion_rate DECIMAL(5,4) DEFAULT 0 CHECK (conversion_rate >= 0 AND conversion_rate <= 1),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    UNIQUE(property_id, date)
);

-- User sessions table for tracking user activity
CREATE TABLE IF NOT EXISTS public.user_sessions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    device_info JSONB,
    ip_address INET,
    user_agent TEXT,
    session_start TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    session_end TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true
);

-- Saved searches table for user preferences
CREATE TABLE IF NOT EXISTS public.saved_searches (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    name TEXT NOT NULL,
    search_params JSONB NOT NULL,
    is_alert_enabled BOOLEAN DEFAULT false,
    alert_frequency TEXT DEFAULT 'daily' CHECK (alert_frequency IN ('immediate', 'daily', 'weekly')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_properties_user_id ON public.properties(user_id);
CREATE INDEX IF NOT EXISTS idx_properties_status ON public.properties(status);
CREATE INDEX IF NOT EXISTS idx_properties_location ON public.properties(city, state, country);
CREATE INDEX IF NOT EXISTS idx_properties_type_price ON public.properties(property_type, price_per_night);
CREATE INDEX IF NOT EXISTS idx_properties_created_at ON public.properties(created_at);

CREATE INDEX IF NOT EXISTS idx_bookings_property_id ON public.bookings(property_id);
CREATE INDEX IF NOT EXISTS idx_bookings_dates ON public.bookings(check_in, check_out);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON public.bookings(status);
CREATE INDEX IF NOT EXISTS idx_bookings_guest_email ON public.bookings(guest_email);
CREATE INDEX IF NOT EXISTS idx_bookings_created_at ON public.bookings(created_at);

CREATE INDEX IF NOT EXISTS idx_reviews_property_id ON public.reviews(property_id);
CREATE INDEX IF NOT EXISTS idx_reviews_rating ON public.reviews(rating);
CREATE INDEX IF NOT EXISTS idx_reviews_created_at ON public.reviews(created_at);

CREATE INDEX IF NOT EXISTS idx_analytics_property_date ON public.property_analytics(property_id, date);
CREATE INDEX IF NOT EXISTS idx_analytics_date ON public.property_analytics(date);

CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON public.users(created_at);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc'::text, NOW());
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for automatic updated_at handling
DROP TRIGGER IF EXISTS update_users_updated_at ON public.users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

DROP TRIGGER IF EXISTS update_properties_updated_at ON public.properties;
CREATE TRIGGER update_properties_updated_at
    BEFORE UPDATE ON public.properties
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

DROP TRIGGER IF EXISTS update_bookings_updated_at ON public.bookings;
CREATE TRIGGER update_bookings_updated_at
    BEFORE UPDATE ON public.bookings
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

DROP TRIGGER IF EXISTS update_reviews_updated_at ON public.reviews;
CREATE TRIGGER update_reviews_updated_at
    BEFORE UPDATE ON public.reviews
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

DROP TRIGGER IF EXISTS update_saved_searches_updated_at ON public.saved_searches;
CREATE TRIGGER update_saved_searches_updated_at
    BEFORE UPDATE ON public.saved_searches
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- Function to update property statistics when bookings change
CREATE OR REPLACE FUNCTION public.update_property_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Update property statistics
    UPDATE public.properties 
    SET 
        booking_count = (
            SELECT COUNT(*) 
            FROM public.bookings 
            WHERE property_id = COALESCE(NEW.property_id, OLD.property_id) 
            AND status IN ('confirmed', 'completed')
        ),
        total_revenue = (
            SELECT COALESCE(SUM(total_amount), 0) 
            FROM public.bookings 
            WHERE property_id = COALESCE(NEW.property_id, OLD.property_id) 
            AND status IN ('confirmed', 'completed')
        )
    WHERE id = COALESCE(NEW.property_id, OLD.property_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ language 'plpgsql';

-- Create trigger for property stats updates
DROP TRIGGER IF EXISTS update_property_stats_trigger ON public.bookings;
CREATE TRIGGER update_property_stats_trigger
    AFTER INSERT OR UPDATE OR DELETE ON public.bookings
    FOR EACH ROW
    EXECUTE FUNCTION public.update_property_stats();

-- Function to update property rating when reviews change
CREATE OR REPLACE FUNCTION public.update_property_rating()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE public.properties 
    SET 
        rating = (
            SELECT ROUND(AVG(rating::numeric), 2)
            FROM public.reviews 
            WHERE property_id = COALESCE(NEW.property_id, OLD.property_id)
        ),
        review_count = (
            SELECT COUNT(*) 
            FROM public.reviews 
            WHERE property_id = COALESCE(NEW.property_id, OLD.property_id)
        )
    WHERE id = COALESCE(NEW.property_id, OLD.property_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ language 'plpgsql';

-- Create trigger for property rating updates
DROP TRIGGER IF EXISTS update_property_rating_trigger ON public.reviews;
CREATE TRIGGER update_property_rating_trigger
    AFTER INSERT OR UPDATE OR DELETE ON public.reviews
    FOR EACH ROW
    EXECUTE FUNCTION public.update_property_rating();

-- Comment on tables for documentation
COMMENT ON TABLE public.users IS 'Extended user profiles linked to Supabase auth.users';
COMMENT ON TABLE public.properties IS 'Property listings with full details and metadata';
COMMENT ON TABLE public.bookings IS 'Property reservations and booking management';
COMMENT ON TABLE public.reviews IS 'Guest reviews and ratings for properties';
COMMENT ON TABLE public.property_analytics IS 'Daily analytics data for properties';
COMMENT ON TABLE public.user_sessions IS 'User session tracking for analytics';
COMMENT ON TABLE public.saved_searches IS 'User saved search preferences and alerts';
