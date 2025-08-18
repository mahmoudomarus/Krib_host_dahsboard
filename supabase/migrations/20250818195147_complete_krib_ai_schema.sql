-- COMPLETE KRIB AI SCHEMA
-- This migration creates ALL tables needed for the Krib AI platform
-- Includes: Properties, Bookings, Financial System, and Payment Methods

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================================
-- CORE TABLES (Properties, Bookings, Users)
-- =====================================================================

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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- =====================================================================
-- FINANCIAL SYSTEM TABLES
-- =====================================================================

-- Host Bank Account Information (Payment Methods)
CREATE TABLE IF NOT EXISTS public.host_bank_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    account_holder_name VARCHAR(255) NOT NULL,
    bank_name VARCHAR(255) NOT NULL,
    account_number_last4 VARCHAR(4) NOT NULL, -- Only store last 4 digits for security
    routing_number VARCHAR(9),
    account_type VARCHAR(20) CHECK (account_type IN ('checking', 'savings')) DEFAULT 'checking',
    is_primary BOOLEAN DEFAULT false,
    is_verified BOOLEAN DEFAULT false,
    stripe_account_id VARCHAR(255), -- For Stripe Connect integration
    verification_status VARCHAR(20) CHECK (verification_status IN ('pending', 'verified', 'failed', 'under_review')) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Financial Transactions (Revenue tracking)
CREATE TABLE IF NOT EXISTS public.financial_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID REFERENCES public.bookings(id) ON DELETE CASCADE,
    property_id UUID REFERENCES public.properties(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Transaction Details
    transaction_type VARCHAR(20) CHECK (transaction_type IN ('booking_payment', 'refund', 'cancellation_fee', 'cleaning_fee', 'security_deposit')) NOT NULL,
    gross_amount DECIMAL(10,2) NOT NULL, -- Total amount paid by guest
    platform_fee DECIMAL(10,2) NOT NULL DEFAULT 0, -- Krib AI platform fee (e.g., 3%)
    payment_processing_fee DECIMAL(10,2) NOT NULL DEFAULT 0, -- Stripe/payment processor fee
    net_amount DECIMAL(10,2) NOT NULL, -- Amount due to host
    
    -- Status and Timing
    status VARCHAR(20) CHECK (status IN ('pending', 'completed', 'failed', 'disputed', 'refunded')) DEFAULT 'pending',
    payment_date TIMESTAMP WITH TIME ZONE, -- When guest paid
    processed_date TIMESTAMP WITH TIME ZONE, -- When we processed it
    
    -- External References
    stripe_payment_intent_id VARCHAR(255),
    stripe_transfer_id VARCHAR(255),
    external_transaction_id VARCHAR(255),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Host Payouts (Money going to hosts)
CREATE TABLE IF NOT EXISTS public.host_payouts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    bank_account_id UUID NOT NULL REFERENCES public.host_bank_accounts(id) ON DELETE RESTRICT,
    
    -- Payout Details
    payout_amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payout_method VARCHAR(20) CHECK (payout_method IN ('bank_transfer', 'stripe_express', 'paypal', 'manual')) DEFAULT 'bank_transfer',
    
    -- Status and Timing
    status VARCHAR(20) CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')) DEFAULT 'pending',
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Processing Details
    stripe_payout_id VARCHAR(255),
    external_payout_id VARCHAR(255),
    failure_reason TEXT,
    
    -- Metadata
    payout_period_start DATE, -- Start of earning period
    payout_period_end DATE,   -- End of earning period
    transaction_count INTEGER DEFAULT 0, -- Number of transactions included
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Junction table linking payouts to specific transactions
CREATE TABLE IF NOT EXISTS public.payout_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payout_id UUID NOT NULL REFERENCES public.host_payouts(id) ON DELETE CASCADE,
    transaction_id UUID NOT NULL REFERENCES public.financial_transactions(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL, -- Amount from this transaction included in payout
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(payout_id, transaction_id)
);

-- Tax Documents (1099s, etc.)
CREATE TABLE IF NOT EXISTS public.tax_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Document Details
    document_type VARCHAR(20) CHECK (document_type IN ('1099k', '1099misc', 'annual_summary')) NOT NULL,
    tax_year INTEGER NOT NULL,
    total_earnings DECIMAL(12,2) NOT NULL,
    total_transactions INTEGER NOT NULL,
    
    -- File Information
    document_url TEXT, -- Link to generated PDF
    generated_at TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    
    -- Status
    status VARCHAR(20) CHECK (status IN ('draft', 'generated', 'sent', 'filed')) DEFAULT 'draft',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Payout Settings per host
CREATE TABLE IF NOT EXISTS public.payout_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Payout Preferences
    payout_frequency VARCHAR(20) CHECK (payout_frequency IN ('daily', 'weekly', 'biweekly', 'monthly')) DEFAULT 'weekly',
    minimum_payout_amount DECIMAL(10,2) DEFAULT 25.00,
    auto_payout_enabled BOOLEAN DEFAULT true,
    payout_day_of_week INTEGER CHECK (payout_day_of_week BETWEEN 0 AND 6), -- 0 = Sunday
    payout_day_of_month INTEGER CHECK (payout_day_of_month BETWEEN 1 AND 31),
    
    -- Hold period (how many days to hold funds before payout)
    hold_period_days INTEGER DEFAULT 1, -- 1 day hold period
    
    -- Tax Information
    tax_id VARCHAR(50), -- SSN or EIN (encrypted)
    tax_id_type VARCHAR(10) CHECK (tax_id_type IN ('ssn', 'ein')),
    business_type VARCHAR(20) CHECK (business_type IN ('individual', 'business', 'llc', 'corporation')),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================================
-- REFERENCE DATA TABLES
-- =====================================================================

-- Amenity suggestions for AI property creation
CREATE TABLE IF NOT EXISTS public.amenity_suggestions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    popularity_score INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Property type information
CREATE TABLE IF NOT EXISTS public.property_type_info (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_name VARCHAR(50) NOT NULL UNIQUE,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    typical_amenities TEXT[],
    avg_price_range_min DECIMAL(10,2),
    avg_price_range_max DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Booking status types
CREATE TABLE IF NOT EXISTS public.booking_status_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    status_code VARCHAR(20) NOT NULL UNIQUE,
    status_name VARCHAR(50) NOT NULL,
    description TEXT,
    color_code VARCHAR(7), -- Hex color for UI
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================================

-- Core table indexes
CREATE INDEX IF NOT EXISTS idx_properties_user_id ON public.properties(user_id);
CREATE INDEX IF NOT EXISTS idx_properties_status ON public.properties(status);
CREATE INDEX IF NOT EXISTS idx_properties_location ON public.properties(city, state, country);
CREATE INDEX IF NOT EXISTS idx_properties_price ON public.properties(price_per_night);

CREATE INDEX IF NOT EXISTS idx_bookings_property_id ON public.bookings(property_id);
CREATE INDEX IF NOT EXISTS idx_bookings_dates ON public.bookings(check_in, check_out);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON public.bookings(status);
CREATE INDEX IF NOT EXISTS idx_bookings_guest_email ON public.bookings(guest_email);

-- Financial table indexes
CREATE INDEX IF NOT EXISTS idx_financial_transactions_user_id ON public.financial_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_financial_transactions_booking_id ON public.financial_transactions(booking_id);
CREATE INDEX IF NOT EXISTS idx_financial_transactions_status ON public.financial_transactions(status);
CREATE INDEX IF NOT EXISTS idx_financial_transactions_payment_date ON public.financial_transactions(payment_date);

CREATE INDEX IF NOT EXISTS idx_host_payouts_user_id ON public.host_payouts(user_id);
CREATE INDEX IF NOT EXISTS idx_host_payouts_status ON public.host_payouts(status);
CREATE INDEX IF NOT EXISTS idx_host_payouts_requested_at ON public.host_payouts(requested_at);

CREATE INDEX IF NOT EXISTS idx_payout_transactions_payout_id ON public.payout_transactions(payout_id);
CREATE INDEX IF NOT EXISTS idx_payout_transactions_transaction_id ON public.payout_transactions(transaction_id);

CREATE INDEX IF NOT EXISTS idx_host_bank_accounts_user_id ON public.host_bank_accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_host_bank_accounts_is_primary ON public.host_bank_accounts(is_primary);

-- =====================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================================

-- Enable RLS on all user tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.host_bank_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.financial_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.host_payouts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payout_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tax_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payout_settings ENABLE ROW LEVEL SECURITY;

-- Users policies
CREATE POLICY "Users can view own profile" ON public.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.users
    FOR UPDATE USING (auth.uid() = id);

-- Properties policies
CREATE POLICY "Users can view own properties" ON public.properties
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own properties" ON public.properties
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own properties" ON public.properties
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own properties" ON public.properties
    FOR DELETE USING (auth.uid() = user_id);

-- Allow public to view active properties (for guests)
CREATE POLICY "Anyone can view active properties" ON public.properties
    FOR SELECT USING (status = 'active');

-- Bookings policies
CREATE POLICY "Property owners can view their bookings" ON public.bookings
    FOR SELECT USING (EXISTS (
        SELECT 1 FROM public.properties 
        WHERE properties.id = bookings.property_id 
        AND properties.user_id = auth.uid()
    ));

CREATE POLICY "Property owners can update their bookings" ON public.bookings
    FOR UPDATE USING (EXISTS (
        SELECT 1 FROM public.properties 
        WHERE properties.id = bookings.property_id 
        AND properties.user_id = auth.uid()
    ));

-- Bank accounts policies
CREATE POLICY "Users can view own bank accounts" ON public.host_bank_accounts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own bank accounts" ON public.host_bank_accounts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own bank accounts" ON public.host_bank_accounts
    FOR UPDATE USING (auth.uid() = user_id);

-- Financial transactions policies
CREATE POLICY "Users can view own transactions" ON public.financial_transactions
    FOR SELECT USING (auth.uid() = user_id);

-- Host payouts policies
CREATE POLICY "Users can view own payouts" ON public.host_payouts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can request payouts" ON public.host_payouts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Payout transactions policies
CREATE POLICY "Users can view own payout transactions" ON public.payout_transactions
    FOR SELECT USING (EXISTS (
        SELECT 1 FROM public.host_payouts hp 
        WHERE hp.id = payout_transactions.payout_id 
        AND hp.user_id = auth.uid()
    ));

-- Tax documents policies
CREATE POLICY "Users can view own tax documents" ON public.tax_documents
    FOR SELECT USING (auth.uid() = user_id);

-- Payout settings policies
CREATE POLICY "Users can view own payout settings" ON public.payout_settings
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own payout settings" ON public.payout_settings
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own payout settings" ON public.payout_settings
    FOR UPDATE USING (auth.uid() = user_id);

-- =====================================================================
-- FINANCIAL CALCULATION FUNCTIONS
-- =====================================================================

-- Function to calculate host's total balance
CREATE OR REPLACE FUNCTION calculate_host_balance(host_user_id UUID)
RETURNS DECIMAL(10,2) AS $$
DECLARE
    total_earned DECIMAL(10,2);
    total_paid_out DECIMAL(10,2);
BEGIN
    -- Calculate total earnings from completed transactions
    SELECT COALESCE(SUM(net_amount), 0) INTO total_earned
    FROM public.financial_transactions
    WHERE user_id = host_user_id
    AND status = 'completed';
    
    -- Calculate total amount already paid out
    SELECT COALESCE(SUM(payout_amount), 0) INTO total_paid_out
    FROM public.host_payouts
    WHERE user_id = host_user_id
    AND status = 'completed';
    
    RETURN total_earned - total_paid_out;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get pending earnings (available for payout)
CREATE OR REPLACE FUNCTION get_pending_earnings(host_user_id UUID)
RETURNS DECIMAL(10,2) AS $$
DECLARE
    pending_amount DECIMAL(10,2);
    hold_days INTEGER;
BEGIN
    -- Get user's hold period
    SELECT COALESCE(hold_period_days, 1) INTO hold_days
    FROM public.payout_settings
    WHERE user_id = host_user_id;
    
    -- Calculate earnings that are past the hold period and not yet included in payouts
    SELECT COALESCE(SUM(ft.net_amount), 0) INTO pending_amount
    FROM public.financial_transactions ft
    WHERE ft.user_id = host_user_id
    AND ft.status = 'completed'
    AND ft.processed_date <= NOW() - INTERVAL '1 day' * hold_days
    AND NOT EXISTS (
        SELECT 1 FROM public.payout_transactions pt
        JOIN public.host_payouts hp ON pt.payout_id = hp.id
        WHERE pt.transaction_id = ft.id
        AND hp.status IN ('pending', 'processing', 'completed')
    );
    
    RETURN pending_amount;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================================
-- TRIGGERS
-- =====================================================================

-- Trigger to automatically create financial transaction when booking is confirmed
CREATE OR REPLACE FUNCTION create_financial_transaction_on_booking()
RETURNS TRIGGER AS $$
DECLARE
    platform_fee_rate DECIMAL(5,4) := 0.03; -- 3% platform fee
    processing_fee_rate DECIMAL(5,4) := 0.029; -- 2.9% + $0.30 Stripe fee
    processing_fee_fixed DECIMAL(4,2) := 0.30;
    gross_amount DECIMAL(10,2);
    calculated_platform_fee DECIMAL(10,2);
    calculated_processing_fee DECIMAL(10,2);
    net_amount DECIMAL(10,2);
BEGIN
    -- Only create transaction when booking moves to confirmed status
    IF OLD.status != 'confirmed' AND NEW.status = 'confirmed' THEN
        gross_amount := NEW.total_amount;
        calculated_platform_fee := gross_amount * platform_fee_rate;
        calculated_processing_fee := (gross_amount * processing_fee_rate) + processing_fee_fixed;
        net_amount := gross_amount - calculated_platform_fee - calculated_processing_fee;
        
        INSERT INTO public.financial_transactions (
            booking_id,
            property_id,
            user_id,
            transaction_type,
            gross_amount,
            platform_fee,
            payment_processing_fee,
            net_amount,
            status,
            payment_date,
            processed_date
        ) VALUES (
            NEW.id,
            NEW.property_id,
            (SELECT user_id FROM public.properties WHERE id = NEW.property_id),
            'booking_payment',
            gross_amount,
            calculated_platform_fee,
            calculated_processing_fee,
            net_amount,
            'completed',
            NOW(),
            NOW()
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop trigger if it exists and recreate
DROP TRIGGER IF EXISTS trigger_create_financial_transaction ON public.bookings;

CREATE TRIGGER trigger_create_financial_transaction
    AFTER UPDATE ON public.bookings
    FOR EACH ROW
    EXECUTE FUNCTION create_financial_transaction_on_booking();

-- =====================================================================
-- REFERENCE DATA INSERTS
-- =====================================================================

-- Insert amenity suggestions
INSERT INTO public.amenity_suggestions (name, category, description, popularity_score) VALUES 
('WiFi', 'Connectivity', 'High-speed wireless internet', 95),
('Air Conditioning', 'Climate', 'Central or window AC units', 85),
('Kitchen', 'Facilities', 'Full kitchen with appliances', 90),
('Parking', 'Convenience', 'Free parking on premises', 80),
('Pool', 'Recreation', 'Swimming pool access', 70),
('Gym', 'Recreation', 'Fitness center or gym access', 60),
('Pet Friendly', 'Policies', 'Pets allowed with restrictions', 45),
('Balcony', 'Features', 'Private or shared balcony', 65),
('Washer/Dryer', 'Facilities', 'In-unit laundry facilities', 75),
('Hot Tub', 'Recreation', 'Hot tub or jacuzzi access', 55)
ON CONFLICT (name) DO NOTHING;

-- Insert property type information
INSERT INTO public.property_type_info (type_name, display_name, description, typical_amenities, avg_price_range_min, avg_price_range_max) VALUES 
('apartment', 'Apartment', 'Multi-unit residential building', ARRAY['WiFi', 'Kitchen', 'Air Conditioning'], 80.00, 200.00),
('house', 'House', 'Single-family residential home', ARRAY['WiFi', 'Kitchen', 'Parking', 'Washer/Dryer'], 120.00, 350.00),
('condo', 'Condominium', 'Privately owned unit in a complex', ARRAY['WiFi', 'Kitchen', 'Pool', 'Gym'], 100.00, 280.00),
('villa', 'Villa', 'Luxury standalone property', ARRAY['WiFi', 'Kitchen', 'Pool', 'Hot Tub', 'Parking'], 200.00, 800.00),
('studio', 'Studio', 'Single room living space', ARRAY['WiFi', 'Kitchen'], 60.00, 150.00),
('cabin', 'Cabin', 'Rustic or mountain retreat', ARRAY['WiFi', 'Kitchen', 'Parking'], 90.00, 250.00)
ON CONFLICT (type_name) DO NOTHING;

-- Insert booking status types
INSERT INTO public.booking_status_types (status_code, status_name, description, color_code) VALUES 
('pending', 'Pending', 'Booking request awaiting confirmation', '#FFA500'),
('confirmed', 'Confirmed', 'Booking confirmed and payment received', '#4CAF50'),
('cancelled', 'Cancelled', 'Booking cancelled by guest or host', '#F44336'),
('completed', 'Completed', 'Guest has checked out', '#2196F3'),
('no_show', 'No Show', 'Guest did not arrive for booking', '#9E9E9E')
ON CONFLICT (status_code) DO NOTHING;

-- =====================================================================
-- COMMENTS
-- =====================================================================

COMMENT ON TABLE public.host_bank_accounts IS 'Host bank account information for payouts';
COMMENT ON TABLE public.financial_transactions IS 'All financial transactions including platform fees';
COMMENT ON TABLE public.host_payouts IS 'Payout requests and processing status';
COMMENT ON TABLE public.payout_transactions IS 'Links payouts to specific transactions';
COMMENT ON TABLE public.tax_documents IS 'Tax documents like 1099s for hosts';
COMMENT ON TABLE public.payout_settings IS 'Host payout preferences and settings';
COMMENT ON TABLE public.properties IS 'Rental properties managed by hosts';
COMMENT ON TABLE public.bookings IS 'Guest bookings and reservations';
COMMENT ON TABLE public.users IS 'User profiles extending Supabase auth';
