-- Verify user
SELECT id, email, name FROM public.users WHERE email = 'mahmoudomarus@gmail.com';

-- Verify properties
SELECT id, title, status, user_id FROM public.properties 
WHERE user_id = (SELECT id FROM public.users WHERE email = 'mahmoudomarus@gmail.com');

-- Verify bookings
SELECT 
    b.id,
    b.property_id,
    b.status,
    b.payment_status,
    b.total_amount,
    b.guests,
    b.created_at,
    p.title,
    p.user_id
FROM public.bookings b
JOIN public.properties p ON b.property_id = p.id
WHERE p.user_id = (SELECT id FROM public.users WHERE email = 'mahmoudomarus@gmail.com')
ORDER BY b.created_at DESC;

-- Count by status
SELECT 
    b.status,
    COUNT(*) as count,
    SUM(b.total_amount) as total_revenue
FROM public.bookings b
JOIN public.properties p ON b.property_id = p.id
WHERE p.user_id = (SELECT id FROM public.users WHERE email = 'mahmoudomarus@gmail.com')
GROUP BY b.status;

