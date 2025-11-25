-- Fix superhost metrics calculation to use correct rating column
-- The properties table uses 'rating' not 'average_rating'

CREATE OR REPLACE FUNCTION public.calculate_host_metrics(host_user_id UUID)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  result JSON;
BEGIN
  SELECT json_build_object(
    'total_properties', (
      SELECT COUNT(*) 
      FROM properties 
      WHERE user_id = host_user_id AND status = 'active'
    ),
    'total_bookings', (
      SELECT COUNT(*) 
      FROM bookings b 
      JOIN properties p ON b.property_id = p.id 
      WHERE p.user_id = host_user_id AND b.status IN ('confirmed', 'completed')
    ),
    'total_revenue', (
      SELECT COALESCE(SUM(total_amount), 0) 
      FROM bookings b 
      JOIN properties p ON b.property_id = p.id 
      WHERE p.user_id = host_user_id AND b.status IN ('confirmed', 'completed')
    ),
    'average_rating', (
      SELECT COALESCE(AVG(p.rating), 0) 
      FROM properties p 
      WHERE p.user_id = host_user_id AND p.rating > 0
    ),
    'response_rate', (
      SELECT COALESCE(
        (COUNT(CASE WHEN b.status IN ('confirmed', 'rejected', 'completed') THEN 1 END)::DECIMAL / NULLIF(COUNT(*), 0)) * 100,
        0
      )
      FROM bookings b
      JOIN properties p ON b.property_id = p.id
      WHERE p.user_id = host_user_id
    ),
    'cancellation_rate', (
      SELECT COALESCE(
        (COUNT(CASE WHEN b.status = 'cancelled' THEN 1 END)::DECIMAL / NULLIF(COUNT(*), 0)) * 100,
        0
      )
      FROM bookings b
      JOIN properties p ON b.property_id = p.id
      WHERE p.user_id = host_user_id
    )
  ) INTO result;
  
  RETURN result;
END;
$$;

