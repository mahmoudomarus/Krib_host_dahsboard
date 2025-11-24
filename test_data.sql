-- Test Data for Messaging & Notifications System
-- Run this in Supabase SQL Editor

-- Step 1: Find your user ID (replace with your email)
DO $$
DECLARE
    v_user_id UUID;
    v_property_id UUID;
    v_conversation_id UUID;
BEGIN
    -- Get user ID
    SELECT id INTO v_user_id 
    FROM public.users 
    WHERE email = 'mahmoudomarus@gmail.com'  -- CHANGE THIS TO YOUR EMAIL
    LIMIT 1;
    
    IF v_user_id IS NULL THEN
        RAISE EXCEPTION 'User not found';
    END IF;
    
    RAISE NOTICE 'Found user ID: %', v_user_id;
    
    -- Get a property
    SELECT id INTO v_property_id
    FROM public.properties
    WHERE user_id = v_user_id
    LIMIT 1;
    
    IF v_property_id IS NULL THEN
        RAISE EXCEPTION 'No properties found - create a property first!';
    END IF;
    
    RAISE NOTICE 'Using property ID: %', v_property_id;
    
    -- Create test conversation
    INSERT INTO public.conversations (
        host_id,
        property_id,
        guest_name,
        guest_email,
        status,
        last_message,
        last_message_at,
        unread_count_host,
        unread_count_guest
    ) VALUES (
        v_user_id,
        v_property_id,
        'Test Guest',
        'test.guest@example.com',
        'active',
        'Hi, I have questions about check-in',
        NOW(),
        2,
        0
    )
    RETURNING id INTO v_conversation_id;
    
    RAISE NOTICE 'Created conversation ID: %', v_conversation_id;
    
    -- Create test messages
    INSERT INTO public.messages (conversation_id, content, is_from_host, read) VALUES
    (v_conversation_id, 'Hi! What time is check-in? We''ll be arriving around 2 PM.', false, false),
    (v_conversation_id, 'Also, is parking available? We''re driving from Abu Dhabi.', false, false);
    
    RAISE NOTICE 'Created 2 test messages';
    
    -- Create test notifications
    INSERT INTO public.notifications (user_id, type, title, message, data, read) VALUES
    (v_user_id, 'new_message', 'New Message from Test Guest', 'You have a new message about check-in time', 
     json_build_object('conversation_id', v_conversation_id, 'guest_name', 'Test Guest'), false),
    (v_user_id, 'new_booking', 'New Booking Received', 'You have a new booking for next week',
     json_build_object('guest_name', 'John Doe', 'check_in', '2024-12-15'), false),
    (v_user_id, 'payment_received', 'Payment Received', 'Payment of AED 2,500 has been received',
     json_build_object('amount', 2500, 'currency', 'AED'), false);
    
    RAISE NOTICE 'Created 3 test notifications';
    
    RAISE NOTICE '✓ Test data created successfully!';
    RAISE NOTICE 'Go to: https://host.krib.ae/dashboard/messages';
    RAISE NOTICE 'Check notification bell for 3 notifications';
END $$;


-- To clean up test data later, run:
-- DELETE FROM public.conversations WHERE guest_email = 'test.guest@example.com';
-- DELETE FROM public.notifications WHERE title LIKE '%Test%';

