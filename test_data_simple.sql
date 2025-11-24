-- STEP 1: First run this to see if messaging tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('conversations', 'messages');

-- If you get 0 rows, you need to run the migration first:
-- Go to: supabase/migrations/20251124000001_add_profiles_and_messaging.sql
-- Copy and paste it in Supabase SQL Editor and run it

-- STEP 2: After migration is run, execute this test data script:
-- (Change the email below to your email)

DO $$
DECLARE
    v_user_id UUID;
    v_property_id UUID;
    v_conversation_id UUID;
    v_user_email TEXT := 'mahmoudomarus@gmail.com';  -- CHANGE THIS TO YOUR EMAIL
BEGIN
    -- Get user ID
    SELECT id INTO v_user_id 
    FROM public.users 
    WHERE email = v_user_email
    LIMIT 1;
    
    IF v_user_id IS NULL THEN
        RAISE EXCEPTION 'User not found with email: %', v_user_email;
    END IF;
    
    RAISE NOTICE '✓ Found user ID: %', v_user_id;
    
    -- Get a property (any status - active or draft)
    SELECT id INTO v_property_id
    FROM public.properties
    WHERE user_id = v_user_id
    LIMIT 1;
    
    IF v_property_id IS NULL THEN
        RAISE EXCEPTION 'No properties found. Create a property first at https://host.krib.ae/dashboard/properties';
    END IF;
    
    RAISE NOTICE '✓ Using property ID: %', v_property_id;
    
    -- Create test conversation
    INSERT INTO public.conversations (
        host_id,
        property_id,
        guest_name,
        guest_email,
        status,
        unread_count_host,
        unread_count_guest
    ) VALUES (
        v_user_id,
        v_property_id,
        'Test Guest',
        'test.guest@example.com',
        'active',
        2,
        0
    )
    RETURNING id INTO v_conversation_id;
    
    RAISE NOTICE '✓ Created conversation ID: %', v_conversation_id;
    
    -- Create test messages
    INSERT INTO public.messages (conversation_id, content, sender_type, is_read) VALUES
    (v_conversation_id, 'Hi! What time is check-in? We will be arriving around 2 PM.', 'guest', false),
    (v_conversation_id, 'Also, is parking available? We are driving from Abu Dhabi and need a place to park.', 'guest', false);
    
    RAISE NOTICE '✓ Created 2 test messages';
    
    -- Update conversation with last message info
    UPDATE public.conversations 
    SET 
        last_message_at = NOW(),
        updated_at = NOW()
    WHERE id = v_conversation_id;
    
    -- Create test notifications (check if notifications table exists)
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'notifications') THEN
        INSERT INTO public.notifications (user_id, type, title, message, data, read) VALUES
        (v_user_id, 'new_message', 'New Message from Test Guest', 'You have a new message about check-in time', 
         jsonb_build_object('conversation_id', v_conversation_id, 'guest_name', 'Test Guest'), false),
        (v_user_id, 'new_booking', 'New Booking Received', 'You have a new booking for Marina Apartment',
         jsonb_build_object('guest_name', 'John Doe', 'check_in', '2024-12-15', 'property_id', v_property_id), false),
        (v_user_id, 'payment_received', 'Payment Received', 'Payment of AED 2,500 has been received',
         jsonb_build_object('amount', 2500, 'currency', 'AED', 'booking_id', gen_random_uuid()), false);
        
        RAISE NOTICE '✓ Created 3 test notifications';
    ELSE
        RAISE NOTICE '⚠ Notifications table does not exist - skipping notifications';
    END IF;
    
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE '✓ TEST DATA CREATED SUCCESSFULLY!';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Next Steps:';
    RAISE NOTICE '1. Go to: https://host.krib.ae/dashboard/messages';
    RAISE NOTICE '2. You should see conversation with "Test Guest"';
    RAISE NOTICE '3. Click to view 2 messages';
    RAISE NOTICE '4. Try replying to messages';
    RAISE NOTICE '5. Test "Generate AI Response" button';
    RAISE NOTICE '6. Click notification bell (top right) - should show 3 notifications';
    RAISE NOTICE '';
    RAISE NOTICE 'Conversation ID: %', v_conversation_id;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'ERROR: %', SQLERRM;
        RAISE NOTICE '';
        RAISE NOTICE 'Common issues:';
        RAISE NOTICE '1. Migration not run - Run: supabase/migrations/20251124000001_add_profiles_and_messaging.sql';
        RAISE NOTICE '2. Email not found - Change email in line 15 of this script';
        RAISE NOTICE '3. No properties - Create a property at: https://host.krib.ae/dashboard/properties';
        RAISE;
END $$;

-- To clean up test data later:
-- DELETE FROM public.conversations WHERE guest_email = 'test.guest@example.com';
-- DELETE FROM public.notifications WHERE title LIKE '%Test%';

