-- Production Reference Data for Krib AI
-- This file creates reference tables and lookup data needed for production operation

-- Create amenity suggestions table for the application
CREATE TABLE IF NOT EXISTS public.amenity_suggestions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    icon TEXT,
    popular BOOLEAN DEFAULT false,
    property_types TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Insert amenity suggestions for production use
INSERT INTO public.amenity_suggestions (name, category, icon, popular, property_types) VALUES
-- Essential amenities
('WiFi', 'essential', 'wifi', true, '{apartment,house,condo,villa,studio,cabin}'),
('Kitchen', 'essential', 'chef-hat', true, '{apartment,house,condo,villa,studio,cabin}'),
('Air Conditioning', 'comfort', 'snowflake', true, '{apartment,house,condo,villa,studio}'),
('Heating', 'comfort', 'thermometer', true, '{apartment,house,condo,villa,studio,cabin}'),
('TV', 'entertainment', 'tv', true, '{apartment,house,condo,villa,studio,cabin}'),

-- Bathroom amenities
('Hair Dryer', 'bathroom', 'wind', false, '{apartment,house,condo,villa,studio,cabin}'),
('Towels', 'bathroom', 'bath', true, '{apartment,house,condo,villa,studio,cabin}'),
('Shampoo', 'bathroom', 'bottle', false, '{apartment,house,condo,villa,studio,cabin}'),
('Hot Water', 'bathroom', 'droplet', true, '{apartment,house,condo,villa,studio,cabin}'),

-- Kitchen amenities
('Refrigerator', 'kitchen', 'refrigerator', true, '{apartment,house,condo,villa,studio,cabin}'),
('Microwave', 'kitchen', 'microwave', true, '{apartment,house,condo,villa,studio,cabin}'),
('Dishwasher', 'kitchen', 'dishwasher', false, '{apartment,house,condo,villa}'),
('Coffee Maker', 'kitchen', 'coffee', true, '{apartment,house,condo,villa,studio,cabin}'),
('Cooking Basics', 'kitchen', 'utensils', true, '{apartment,house,condo,villa,studio,cabin}'),

-- Outdoor amenities
('Pool', 'outdoor', 'waves', true, '{house,villa}'),
('Hot Tub', 'outdoor', 'hot-tub', false, '{house,villa,cabin}'),
('BBQ Grill', 'outdoor', 'grill', false, '{house,villa,cabin}'),
('Garden', 'outdoor', 'flower', false, '{house,villa,cabin}'),
('Balcony', 'outdoor', 'balcony', true, '{apartment,condo}'),
('Patio', 'outdoor', 'patio', false, '{house,villa,cabin}'),
('Beach Access', 'outdoor', 'beach', false, '{house,villa}'),

-- Transportation
('Parking', 'transportation', 'car', true, '{apartment,house,condo,villa,studio,cabin}'),
('Garage', 'transportation', 'garage', false, '{house,villa}'),
('EV Charging', 'transportation', 'electric', false, '{apartment,house,condo,villa,studio,cabin}'),

-- Laundry
('Washing Machine', 'laundry', 'washing-machine', true, '{apartment,house,condo,villa,cabin}'),
('Dryer', 'laundry', 'dryer', true, '{apartment,house,condo,villa,cabin}'),
('Laundromat Nearby', 'laundry', 'map-pin', false, '{studio}'),

-- Entertainment
('Cable TV', 'entertainment', 'tv-2', false, '{apartment,house,condo,villa,studio,cabin}'),
('Streaming Services', 'entertainment', 'play', true, '{apartment,house,condo,villa,studio,cabin}'),
('Sound System', 'entertainment', 'speaker', false, '{apartment,house,condo,villa,studio,cabin}'),
('Board Games', 'entertainment', 'puzzle', false, '{house,villa,cabin}'),
('Books', 'entertainment', 'book', false, '{apartment,house,condo,villa,studio,cabin}'),

-- Safety & Security
('Smoke Detector', 'safety', 'smoke', true, '{apartment,house,condo,villa,studio,cabin}'),
('Carbon Monoxide Detector', 'safety', 'alert-triangle', true, '{apartment,house,condo,villa,studio,cabin}'),
('Fire Extinguisher', 'safety', 'fire-extinguisher', false, '{apartment,house,condo,villa,studio,cabin}'),
('First Aid Kit', 'safety', 'heart-pulse', false, '{apartment,house,condo,villa,studio,cabin}'),
('Security Camera', 'safety', 'camera', false, '{house,villa}'),
('Safe', 'safety', 'lock', false, '{apartment,house,condo,villa,studio,cabin}'),

-- Accessibility
('Wheelchair Accessible', 'accessibility', 'accessibility', false, '{apartment,house,condo,villa}'),
('Elevator', 'accessibility', 'elevator', false, '{apartment,condo}'),
('Step-Free Access', 'accessibility', 'accessibility', false, '{apartment,house,condo,villa,studio}'),

-- Family-Friendly
('Family Friendly', 'family', 'users', true, '{apartment,house,condo,villa,cabin}'),
('High Chair', 'family', 'baby', false, '{apartment,house,condo,villa,cabin}'),
('Pack n Play', 'family', 'baby', false, '{apartment,house,condo,villa,cabin}'),
('Baby Safety Gates', 'family', 'shield', false, '{house,villa,cabin}'),
('Children''s Books', 'family', 'book-open', false, '{apartment,house,condo,villa,cabin}'),

-- Work-Friendly
('Dedicated Workspace', 'work', 'laptop', true, '{apartment,house,condo,villa,studio,cabin}'),
('High-Speed Internet', 'work', 'wifi', true, '{apartment,house,condo,villa,studio,cabin}'),
('Printer', 'work', 'printer', false, '{apartment,house,condo,villa,studio,cabin}'),
('Ergonomic Chair', 'work', 'chair', false, '{apartment,house,condo,villa,studio,cabin}'),

-- Pet-Friendly
('Pet Friendly', 'pets', 'pet', false, '{apartment,house,condo,villa,studio,cabin}'),
('Dog Bed', 'pets', 'dog', false, '{apartment,house,condo,villa,studio,cabin}'),
('Pet Bowls', 'pets', 'bowl', false, '{apartment,house,condo,villa,studio,cabin}'),
('Fenced Yard', 'pets', 'fence', false, '{house,villa,cabin}'),

-- Luxury Amenities
('Gym', 'luxury', 'dumbbell', false, '{condo,villa}'),
('Spa', 'luxury', 'spa', false, '{villa}'),
('Concierge', 'luxury', 'bell', false, '{condo,villa}'),
('Room Service', 'luxury', 'room-service', false, '{villa}'),
('Private Beach', 'luxury', 'beach-private', false, '{villa}'),
('Wine Cellar', 'luxury', 'wine', false, '{house,villa}'),
('Home Theater', 'luxury', 'theater', false, '{house,villa}'),

-- Climate
('Fireplace', 'comfort', 'flame', false, '{house,villa,cabin}'),
('Ceiling Fan', 'comfort', 'fan', true, '{apartment,house,condo,villa,studio,cabin}'),
('Portable Heater', 'comfort', 'heater', false, '{cabin}'),

-- Views
('Ocean View', 'view', 'ocean', false, '{apartment,house,condo,villa,cabin}'),
('Mountain View', 'view', 'mountain', false, '{apartment,house,condo,villa,cabin}'),
('City View', 'view', 'city', false, '{apartment,condo}'),
('Garden View', 'view', 'garden', false, '{apartment,house,condo,villa}'),
('Lake View', 'view', 'lake', false, '{apartment,house,condo,villa,cabin}');

-- Create property type information table
CREATE TABLE IF NOT EXISTS public.property_type_info (
    property_type TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    description TEXT,
    typical_amenities TEXT[],
    avg_price_range TEXT,
    max_guests_typical INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Insert property type information
INSERT INTO public.property_type_info VALUES
('apartment', 'Apartment', 'Urban dwelling in a multi-unit building', 
 '{WiFi,Kitchen,Air Conditioning,TV,Parking}', '$80-250', 4),
('house', 'House', 'Standalone residential property with private yard',
 '{WiFi,Kitchen,Washing Machine,Parking,Garden,BBQ Grill}', '$120-400', 8),
('condo', 'Condo', 'Privately owned unit in a managed building with amenities',
 '{WiFi,Kitchen,Air Conditioning,Elevator,Pool,Gym}', '$100-300', 6),
('villa', 'Villa', 'Luxury property with premium amenities and privacy',
 '{WiFi,Kitchen,Pool,Garden,Parking,BBQ Area,Spa}', '$200-800', 12),
('studio', 'Studio', 'Compact all-in-one living space',
 '{WiFi,Kitchenette,Air Conditioning,TV}', '$60-180', 2),
('cabin', 'Cabin', 'Rustic or modern retreat, often in natural settings',
 '{WiFi,Kitchen,Fireplace,Nature Views,Parking,Hot Tub}', '$90-350', 6),
('other', 'Other', 'Unique property type not fitting standard categories',
 '{WiFi,Kitchen}', '$70-300', 4);

-- Create booking status lookup table
CREATE TABLE IF NOT EXISTS public.booking_statuses (
    status TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    color TEXT DEFAULT '#64748b',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Insert booking status information
INSERT INTO public.booking_statuses (status, display_name, description, is_active, color) VALUES
('pending', 'Pending', 'Booking request awaiting confirmation', true, '#f59e0b'),
('confirmed', 'Confirmed', 'Booking confirmed and payment received', true, '#10b981'),
('cancelled', 'Cancelled', 'Booking cancelled by guest or host', false, '#ef4444'),
('completed', 'Completed', 'Guest stay completed successfully', false, '#6366f1'),
('no_show', 'No Show', 'Guest did not show up for confirmed booking', false, '#64748b');

-- Create payment status lookup table
CREATE TABLE IF NOT EXISTS public.payment_statuses (
    status TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    description TEXT,
    is_final BOOLEAN DEFAULT false,
    color TEXT DEFAULT '#64748b',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Insert payment status information
INSERT INTO public.payment_statuses (status, display_name, description, is_final, color) VALUES
('pending', 'Pending', 'Payment is being processed', false, '#f59e0b'),
('paid', 'Paid', 'Payment completed successfully', true, '#10b981'),
('refunded', 'Refunded', 'Payment fully refunded to guest', true, '#64748b'),
('partially_refunded', 'Partially Refunded', 'Payment partially refunded', true, '#8b5cf6');

-- Create useful views for common queries
CREATE OR REPLACE VIEW public.property_summary AS
SELECT 
    p.id,
    p.title,
    p.city,
    p.state,
    p.property_type,
    p.bedrooms,
    p.bathrooms,
    p.max_guests,
    p.price_per_night,
    p.status,
    p.rating,
    p.review_count,
    p.booking_count,
    p.total_revenue,
    p.created_at,
    u.name as owner_name,
    u.email as owner_email
FROM public.properties p
JOIN public.users u ON p.user_id = u.id;

CREATE OR REPLACE VIEW public.booking_summary AS
SELECT 
    b.id,
    b.property_id,
    p.title as property_title,
    p.city as property_city,
    p.state as property_state,
    b.guest_name,
    b.guest_email,
    b.check_in,
    b.check_out,
    b.nights,
    b.guests,
    b.total_amount,
    b.status,
    b.payment_status,
    b.created_at,
    u.name as owner_name,
    u.email as owner_email
FROM public.bookings b
JOIN public.properties p ON b.property_id = p.id
JOIN public.users u ON p.user_id = u.id;

-- Add useful functions for analytics
CREATE OR REPLACE FUNCTION public.get_monthly_revenue(user_uuid UUID, months_back INTEGER DEFAULT 12)
RETURNS TABLE (
    month_year TEXT,
    revenue DECIMAL,
    bookings BIGINT
) AS $$
BEGIN
    RETURN QUERY
    WITH monthly_data AS (
        SELECT 
            TO_CHAR(b.created_at, 'YYYY-MM') as month_year,
            SUM(b.total_amount) as revenue,
            COUNT(*) as bookings
        FROM public.bookings b
        JOIN public.properties p ON b.property_id = p.id
        WHERE p.user_id = user_uuid
        AND b.status IN ('confirmed', 'completed')
        AND b.created_at >= NOW() - INTERVAL '1 month' * months_back
        GROUP BY TO_CHAR(b.created_at, 'YYYY-MM')
        ORDER BY month_year
    )
    SELECT 
        md.month_year,
        COALESCE(md.revenue, 0),
        COALESCE(md.bookings, 0)
    FROM monthly_data md;
END;
$$ LANGUAGE plpgsql;

-- Function to get property performance metrics
CREATE OR REPLACE FUNCTION public.get_property_performance(user_uuid UUID)
RETURNS TABLE (
    property_id UUID,
    property_title TEXT,
    total_revenue DECIMAL,
    booking_count BIGINT,
    avg_rating DECIMAL,
    review_count BIGINT,
    occupancy_rate DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.title,
        p.total_revenue,
        p.booking_count::BIGINT,
        p.rating,
        p.review_count::BIGINT,
        CASE 
            WHEN DATE_PART('day', NOW() - p.created_at) > 0 
            THEN (p.booking_count::DECIMAL / DATE_PART('day', NOW() - p.created_at)) * 100
            ELSE 0 
        END as occupancy_rate
    FROM public.properties p
    WHERE p.user_id = user_uuid
    ORDER BY p.total_revenue DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate dynamic pricing suggestions
CREATE OR REPLACE FUNCTION public.get_pricing_suggestion(
    prop_id UUID,
    target_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
    suggested_price DECIMAL,
    confidence_score DECIMAL,
    factors JSONB
) AS $$
DECLARE
    base_price DECIMAL;
    seasonal_multiplier DECIMAL := 1.0;
    demand_multiplier DECIMAL := 1.0;
    competition_factor DECIMAL := 1.0;
BEGIN
    -- Get base price from property
    SELECT price_per_night INTO base_price
    FROM public.properties 
    WHERE id = prop_id;
    
    -- Simple seasonal adjustment (this would be enhanced with real market data)
    CASE 
        WHEN EXTRACT(MONTH FROM target_date) IN (6, 7, 8, 12) THEN
            seasonal_multiplier := 1.2;
        WHEN EXTRACT(MONTH FROM target_date) IN (1, 2, 3) THEN
            seasonal_multiplier := 0.9;
        ELSE
            seasonal_multiplier := 1.0;
    END CASE;
    
    -- Weekend premium
    IF EXTRACT(DOW FROM target_date) IN (5, 6) THEN
        demand_multiplier := 1.15;
    END IF;
    
    RETURN QUERY
    SELECT 
        ROUND(base_price * seasonal_multiplier * demand_multiplier * competition_factor, 2) as suggested_price,
        0.75::DECIMAL as confidence_score,
        jsonb_build_object(
            'base_price', base_price,
            'seasonal_multiplier', seasonal_multiplier,
            'demand_multiplier', demand_multiplier,
            'competition_factor', competition_factor
        ) as factors;
END;
$$ LANGUAGE plpgsql;

-- Create indexes for reference tables
CREATE INDEX IF NOT EXISTS idx_amenity_suggestions_category ON public.amenity_suggestions(category);
CREATE INDEX IF NOT EXISTS idx_amenity_suggestions_popular ON public.amenity_suggestions(popular);
CREATE INDEX IF NOT EXISTS idx_property_type_info_type ON public.property_type_info(property_type);

-- Comments for documentation
COMMENT ON TABLE public.amenity_suggestions IS 'Curated list of amenities to suggest to users when creating properties';
COMMENT ON TABLE public.property_type_info IS 'Information about different property types and their characteristics';
COMMENT ON TABLE public.booking_statuses IS 'Lookup table for booking status values and their display properties';
COMMENT ON TABLE public.payment_statuses IS 'Lookup table for payment status values and their display properties';
COMMENT ON VIEW public.property_summary IS 'Simplified view of properties with owner information';
COMMENT ON VIEW public.booking_summary IS 'Detailed view of bookings with property and owner information';
COMMENT ON FUNCTION public.get_monthly_revenue(UUID, INTEGER) IS 'Get monthly revenue breakdown for a user';
COMMENT ON FUNCTION public.get_property_performance(UUID) IS 'Get performance metrics for all properties owned by a user';
COMMENT ON FUNCTION public.get_pricing_suggestion(UUID, DATE) IS 'Calculate dynamic pricing suggestions based on various factors';
