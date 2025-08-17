-- Row Level Security (RLS) Policies for RentalAI
-- This file sets up comprehensive security policies for all tables

-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.property_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.saved_searches ENABLE ROW LEVEL SECURITY;

-- Users policies
DROP POLICY IF EXISTS "Users can view own profile" ON public.users;
CREATE POLICY "Users can view own profile" ON public.users
    FOR SELECT USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON public.users;
CREATE POLICY "Users can update own profile" ON public.users
    FOR UPDATE USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can insert own profile" ON public.users;
CREATE POLICY "Users can insert own profile" ON public.users
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Properties policies
DROP POLICY IF EXISTS "Users can view own properties" ON public.properties;
CREATE POLICY "Users can view own properties" ON public.properties
    FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can view published properties" ON public.properties;
CREATE POLICY "Users can view published properties" ON public.properties
    FOR SELECT USING (status = 'active');

DROP POLICY IF EXISTS "Users can insert own properties" ON public.properties;
CREATE POLICY "Users can insert own properties" ON public.properties
    FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own properties" ON public.properties;
CREATE POLICY "Users can update own properties" ON public.properties
    FOR UPDATE USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own properties" ON public.properties;
CREATE POLICY "Users can delete own properties" ON public.properties
    FOR DELETE USING (auth.uid() = user_id);

-- Bookings policies
DROP POLICY IF EXISTS "Property owners can view bookings" ON public.bookings;
CREATE POLICY "Property owners can view bookings" ON public.bookings
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.properties 
            WHERE id = property_id AND user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "Guests can view own bookings" ON public.bookings;
CREATE POLICY "Guests can view own bookings" ON public.bookings
    FOR SELECT USING (
        guest_email = (
            SELECT email FROM auth.users WHERE id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "Anyone can create bookings" ON public.bookings;
CREATE POLICY "Anyone can create bookings" ON public.bookings
    FOR INSERT WITH CHECK (true);

DROP POLICY IF EXISTS "Property owners can update bookings" ON public.bookings;
CREATE POLICY "Property owners can update bookings" ON public.bookings
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.properties 
            WHERE id = property_id AND user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "Property owners can delete bookings" ON public.bookings;
CREATE POLICY "Property owners can delete bookings" ON public.bookings
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM public.properties 
            WHERE id = property_id AND user_id = auth.uid()
        )
    );

-- Reviews policies
DROP POLICY IF EXISTS "Anyone can view reviews" ON public.reviews;
CREATE POLICY "Anyone can view reviews" ON public.reviews
    FOR SELECT USING (true);

DROP POLICY IF EXISTS "Property owners can view all reviews" ON public.reviews;
CREATE POLICY "Property owners can view all reviews" ON public.reviews
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.properties 
            WHERE id = property_id AND user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "Guests can create reviews" ON public.reviews;
CREATE POLICY "Guests can create reviews" ON public.reviews
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.bookings 
            WHERE property_id = reviews.property_id 
            AND guest_email = reviews.guest_email
            AND status = 'completed'
        )
    );

DROP POLICY IF EXISTS "Property owners can respond to reviews" ON public.reviews;
CREATE POLICY "Property owners can respond to reviews" ON public.reviews
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.properties 
            WHERE id = property_id AND user_id = auth.uid()
        )
    );

-- Property analytics policies
DROP POLICY IF EXISTS "Property owners can view analytics" ON public.property_analytics;
CREATE POLICY "Property owners can view analytics" ON public.property_analytics
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.properties 
            WHERE id = property_id AND user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "System can insert analytics" ON public.property_analytics;
CREATE POLICY "System can insert analytics" ON public.property_analytics
    FOR INSERT WITH CHECK (true);

DROP POLICY IF EXISTS "System can update analytics" ON public.property_analytics;
CREATE POLICY "System can update analytics" ON public.property_analytics
    FOR UPDATE USING (true);

-- User sessions policies
DROP POLICY IF EXISTS "Users can view own sessions" ON public.user_sessions;
CREATE POLICY "Users can view own sessions" ON public.user_sessions
    FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own sessions" ON public.user_sessions;
CREATE POLICY "Users can insert own sessions" ON public.user_sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own sessions" ON public.user_sessions;
CREATE POLICY "Users can update own sessions" ON public.user_sessions
    FOR UPDATE USING (auth.uid() = user_id);

-- Saved searches policies
DROP POLICY IF EXISTS "Users can manage own saved searches" ON public.saved_searches;
CREATE POLICY "Users can manage own saved searches" ON public.saved_searches
    FOR ALL USING (auth.uid() = user_id);

-- Create functions for common queries
CREATE OR REPLACE FUNCTION public.get_user_properties(user_uuid UUID)
RETURNS SETOF public.properties AS $$
BEGIN
    RETURN QUERY 
    SELECT * FROM public.properties 
    WHERE user_id = user_uuid 
    ORDER BY created_at DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION public.get_property_bookings(prop_id UUID, owner_id UUID)
RETURNS SETOF public.bookings AS $$
BEGIN
    -- Verify the user owns the property
    IF NOT EXISTS (
        SELECT 1 FROM public.properties 
        WHERE id = prop_id AND user_id = owner_id
    ) THEN
        RAISE EXCEPTION 'Access denied';
    END IF;
    
    RETURN QUERY 
    SELECT * FROM public.bookings 
    WHERE property_id = prop_id 
    ORDER BY created_at DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION public.get_property_analytics_summary(prop_id UUID, owner_id UUID)
RETURNS TABLE (
    total_revenue DECIMAL,
    total_bookings BIGINT,
    avg_rating DECIMAL,
    total_reviews BIGINT,
    occupancy_rate DECIMAL
) AS $$
BEGIN
    -- Verify the user owns the property
    IF NOT EXISTS (
        SELECT 1 FROM public.properties 
        WHERE id = prop_id AND user_id = owner_id
    ) THEN
        RAISE EXCEPTION 'Access denied';
    END IF;
    
    RETURN QUERY 
    SELECT 
        p.total_revenue,
        p.booking_count::BIGINT,
        p.rating,
        p.review_count::BIGINT,
        COALESCE(AVG(pa.occupancy_rate), 0) as occupancy_rate
    FROM public.properties p
    LEFT JOIN public.property_analytics pa ON pa.property_id = p.id
    WHERE p.id = prop_id
    GROUP BY p.total_revenue, p.booking_count, p.rating, p.review_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check booking availability
CREATE OR REPLACE FUNCTION public.check_availability(
    prop_id UUID,
    checkin_date DATE,
    checkout_date DATE
)
RETURNS BOOLEAN AS $$
DECLARE
    conflict_count INTEGER;
BEGIN
    -- Check for conflicting bookings
    SELECT COUNT(*) INTO conflict_count
    FROM public.bookings
    WHERE property_id = prop_id
    AND status IN ('confirmed', 'pending')
    AND (
        (check_in < checkout_date AND check_out > checkin_date)
    );
    
    RETURN conflict_count = 0;
END;
$$ LANGUAGE plpgsql;

-- Function to create property analytics entry
CREATE OR REPLACE FUNCTION public.record_property_view(prop_id UUID)
RETURNS VOID AS $$
BEGIN
    INSERT INTO public.property_analytics (property_id, date, views)
    VALUES (prop_id, CURRENT_DATE, 1)
    ON CONFLICT (property_id, date)
    DO UPDATE SET views = property_analytics.views + 1;
    
    -- Also update the property views count
    UPDATE public.properties 
    SET views_count = views_count + 1 
    WHERE id = prop_id;
END;
$$ LANGUAGE plpgsql;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO authenticated;

-- Grant limited permissions to anonymous users (for public property viewing)
GRANT SELECT ON public.properties TO anon;
GRANT SELECT ON public.reviews TO anon;
GRANT INSERT ON public.bookings TO anon;

-- Create indexes for RLS performance
CREATE INDEX IF NOT EXISTS idx_properties_user_id_status ON public.properties(user_id, status);
CREATE INDEX IF NOT EXISTS idx_bookings_property_guest ON public.bookings(property_id, guest_email);
CREATE INDEX IF NOT EXISTS idx_reviews_property_guest ON public.reviews(property_id, guest_email);

-- Add helpful comments
COMMENT ON POLICY "Users can view own profile" ON public.users IS 'Users can only view their own profile data';
COMMENT ON POLICY "Users can view published properties" ON public.properties IS 'Anyone can view active/published properties';
COMMENT ON POLICY "Property owners can view bookings" ON public.bookings IS 'Property owners can view all bookings for their properties';
COMMENT ON POLICY "Guests can view own bookings" ON public.bookings IS 'Guests can view bookings made with their email';
COMMENT ON FUNCTION public.check_availability(UUID, DATE, DATE) IS 'Check if a property is available for given dates';
COMMENT ON FUNCTION public.record_property_view(UUID) IS 'Record a view for analytics tracking';
