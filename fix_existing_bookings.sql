-- Update existing bookings to calculate nights if missing
UPDATE public.bookings
SET nights = (check_out - check_in)
WHERE nights IS NULL OR nights = 0;

-- Verify the update
SELECT 
    id,
    property_id,
    guest_name,
    check_in,
    check_out,
    nights,
    total_amount,
    status
FROM public.bookings
WHERE property_id IN (
    SELECT id FROM public.properties 
    WHERE user_id = (SELECT id FROM public.users WHERE email = 'mahmoudomarus@gmail.com')
)
ORDER BY created_at DESC;

