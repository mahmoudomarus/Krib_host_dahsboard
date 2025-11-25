-- Get actual bookings for the user to see what data we have
SELECT 
    b.id,
    b.property_id,
    b.guest_name,
    b.guest_email,
    b.guest_phone,
    b.check_in,
    b.check_out,
    b.nights,
    b.guests,
    b.total_amount,
    b.status,
    b.payment_status,
    b.created_at,
    b.updated_at,
    p.title as property_title,
    p.address as property_address
FROM public.bookings b
JOIN public.properties p ON b.property_id = p.id
WHERE p.user_id = (SELECT id FROM public.users WHERE email = 'mahmoudomarus@gmail.com')
ORDER BY b.created_at DESC;

