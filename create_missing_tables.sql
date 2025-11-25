-- Create reviews table
CREATE TABLE IF NOT EXISTS public.reviews (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    property_id UUID REFERENCES public.properties(id) ON DELETE CASCADE NOT NULL,
    booking_id UUID REFERENCES public.bookings(id) ON DELETE SET NULL,
    guest_name TEXT NOT NULL,
    guest_email TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    cleanliness_rating INTEGER CHECK (cleanliness_rating >= 1 AND cleanliness_rating <= 5),
    accuracy_rating INTEGER CHECK (accuracy_rating >= 1 AND accuracy_rating <= 5),
    communication_rating INTEGER CHECK (communication_rating >= 1 AND communication_rating <= 5),
    location_rating INTEGER CHECK (location_rating >= 1 AND location_rating <= 5),
    value_rating INTEGER CHECK (value_rating >= 1 AND value_rating <= 5),
    comment TEXT,
    pros TEXT,
    cons TEXT,
    host_response TEXT,
    responded_at TIMESTAMPTZ,
    is_verified BOOLEAN DEFAULT false,
    is_featured BOOLEAN DEFAULT false,
    helpful_votes INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- RLS policies for reviews
ALTER TABLE public.reviews ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view reviews for their properties" ON public.reviews;
CREATE POLICY "Users can view reviews for their properties"
ON public.reviews FOR SELECT
USING (
    property_id IN (
        SELECT id FROM public.properties WHERE user_id = auth.uid()
    )
);

DROP POLICY IF EXISTS "Users can respond to reviews" ON public.reviews;
CREATE POLICY "Users can respond to reviews"
ON public.reviews FOR UPDATE
USING (
    property_id IN (
        SELECT id FROM public.properties WHERE user_id = auth.uid()
    )
);

