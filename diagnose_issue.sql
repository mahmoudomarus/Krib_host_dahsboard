-- Check user
SELECT id, email, name FROM public.users WHERE email = 'mahmoudomarus@gmail.com';

-- Check properties
SELECT id, title, status, price_per_night FROM public.properties 
WHERE user_id = (SELECT id FROM public.users WHERE email = 'mahmoudomarus@gmail.com');

-- If properties exist but status is 'draft', update one to 'active'
UPDATE public.properties 
SET status = 'active'
WHERE id = (
    SELECT id FROM public.properties 
    WHERE user_id = (SELECT id FROM public.users WHERE email = 'mahmoudomarus@gmail.com')
    AND status = 'draft'
    LIMIT 1
);

-- Verify update
SELECT id, title, status FROM public.properties 
WHERE user_id = (SELECT id FROM public.users WHERE email = 'mahmoudomarus@gmail.com');

