-- Check bookings table columns and constraints
SELECT 
    column_name,
    data_type,
    column_default,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'bookings'
ORDER BY ordinal_position;

-- Check constraints
SELECT 
    conname as constraint_name,
    pg_get_constraintdef(oid) as definition
FROM pg_constraint
WHERE conrelid = 'public.bookings'::regclass
AND contype = 'c';

