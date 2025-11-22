-- Performance Optimizations for RLS Policies
-- Fixes auth.uid() re-evaluation issues and optimizes multiple permissive policies

-- ============================================================================
-- PART 1: Fix auth.uid() Performance in RLS Policies
-- ============================================================================

-- Drop existing policies that have performance issues
-- We'll recreate them with optimized (select auth.uid()) syntax

-- Users table policies
DROP POLICY IF EXISTS "Users can view own profile" ON public.users;
DROP POLICY IF EXISTS "Users can update own profile" ON public.users;

CREATE POLICY "Users can view own profile"
ON public.users FOR SELECT
TO authenticated
USING (id = (select auth.uid()));

CREATE POLICY "Users can update own profile"
ON public.users FOR UPDATE
TO authenticated
USING (id = (select auth.uid()));

-- Properties table policies
DROP POLICY IF EXISTS "Users can view own properties" ON public.properties;
DROP POLICY IF EXISTS "Users can insert own properties" ON public.properties;
DROP POLICY IF EXISTS "Users can update own properties" ON public.properties;
DROP POLICY IF EXISTS "Users can delete own properties" ON public.properties;

CREATE POLICY "Users can view own properties"
ON public.properties FOR SELECT
TO authenticated
USING (user_id = (select auth.uid()));

CREATE POLICY "Users can insert own properties"
ON public.properties FOR INSERT
TO authenticated
WITH CHECK (user_id = (select auth.uid()));

CREATE POLICY "Users can update own properties"
ON public.properties FOR UPDATE
TO authenticated
USING (user_id = (select auth.uid()));

CREATE POLICY "Users can delete own properties"
ON public.properties FOR DELETE
TO authenticated
USING (user_id = (select auth.uid()));

-- Bookings table policies
DROP POLICY IF EXISTS "Property owners can view their bookings" ON public.bookings;
DROP POLICY IF EXISTS "Property owners can update their bookings" ON public.bookings;

CREATE POLICY "Property owners can view their bookings"
ON public.bookings FOR SELECT
TO authenticated
USING (
    property_id IN (
        SELECT id FROM public.properties WHERE user_id = (select auth.uid())
    )
);

CREATE POLICY "Property owners can update their bookings"
ON public.bookings FOR UPDATE
TO authenticated
USING (
    property_id IN (
        SELECT id FROM public.properties WHERE user_id = (select auth.uid())
    )
);

-- Host notifications policies
DROP POLICY IF EXISTS "Users can view own notifications" ON public.host_notifications;
DROP POLICY IF EXISTS "Users can update own notifications" ON public.host_notifications;

CREATE POLICY "Users can view own notifications"
ON public.host_notifications FOR SELECT
TO authenticated
USING (host_id = (select auth.uid()));

CREATE POLICY "Users can update own notifications"
ON public.host_notifications FOR UPDATE
TO authenticated
USING (host_id = (select auth.uid()));

-- Host settings policies
DROP POLICY IF EXISTS "Users can manage own settings" ON public.host_settings;

CREATE POLICY "Users can manage own settings"
ON public.host_settings FOR ALL
TO authenticated
USING (user_id = (select auth.uid()));

-- Payouts table policies
DROP POLICY IF EXISTS "Users can view own payouts" ON public.payouts;

CREATE POLICY "Users can view own payouts"
ON public.payouts FOR SELECT
TO authenticated
USING (user_id = (select auth.uid()));

-- Stripe events policies
DROP POLICY IF EXISTS "Service role can manage stripe events" ON public.stripe_events;

CREATE POLICY "Service role can manage stripe events"
ON public.stripe_events FOR ALL
TO service_role
USING (true);

-- Host bank accounts policies
DROP POLICY IF EXISTS "Users can view own bank accounts" ON public.host_bank_accounts;
DROP POLICY IF EXISTS "Users can insert own bank accounts" ON public.host_bank_accounts;
DROP POLICY IF EXISTS "Users can update own bank accounts" ON public.host_bank_accounts;

CREATE POLICY "Users can view own bank accounts"
ON public.host_bank_accounts FOR SELECT
TO authenticated
USING (user_id = (select auth.uid()));

CREATE POLICY "Users can insert own bank accounts"
ON public.host_bank_accounts FOR INSERT
TO authenticated
WITH CHECK (user_id = (select auth.uid()));

CREATE POLICY "Users can update own bank accounts"
ON public.host_bank_accounts FOR UPDATE
TO authenticated
USING (user_id = (select auth.uid()));

-- Financial transactions policies
DROP POLICY IF EXISTS "Users can view own transactions" ON public.financial_transactions;

CREATE POLICY "Users can view own transactions"
ON public.financial_transactions FOR SELECT
TO authenticated
USING (
    user_id = (select auth.uid()) OR
    booking_id IN (
        SELECT b.id FROM public.bookings b
        JOIN public.properties p ON b.property_id = p.id
        WHERE p.user_id = (select auth.uid())
    )
);

-- Host payouts policies
DROP POLICY IF EXISTS "Users can view own payouts" ON public.host_payouts;
DROP POLICY IF EXISTS "Users can request payouts" ON public.host_payouts;

CREATE POLICY "Users can view own payouts"
ON public.host_payouts FOR SELECT
TO authenticated
USING (user_id = (select auth.uid()));

CREATE POLICY "Users can request payouts"
ON public.host_payouts FOR INSERT
TO authenticated
WITH CHECK (user_id = (select auth.uid()));

-- Payout transactions policies
DROP POLICY IF EXISTS "Users can view own payout transactions" ON public.payout_transactions;

CREATE POLICY "Users can view own payout transactions"
ON public.payout_transactions FOR SELECT
TO authenticated
USING (
    payout_id IN (
        SELECT id FROM public.host_payouts WHERE user_id = (select auth.uid())
    )
);

-- Tax documents policies
DROP POLICY IF EXISTS "Users can view own tax documents" ON public.tax_documents;

CREATE POLICY "Users can view own tax documents"
ON public.tax_documents FOR SELECT
TO authenticated
USING (user_id = (select auth.uid()));

-- Payout settings policies
DROP POLICY IF EXISTS "Users can view own payout settings" ON public.payout_settings;
DROP POLICY IF EXISTS "Users can insert own payout settings" ON public.payout_settings;
DROP POLICY IF EXISTS "Users can update own payout settings" ON public.payout_settings;

CREATE POLICY "Users can view own payout settings"
ON public.payout_settings FOR SELECT
TO authenticated
USING (user_id = (select auth.uid()));

CREATE POLICY "Users can insert own payout settings"
ON public.payout_settings FOR INSERT
TO authenticated
WITH CHECK (user_id = (select auth.uid()));

CREATE POLICY "Users can update own payout settings"
ON public.payout_settings FOR UPDATE
TO authenticated
USING (user_id = (select auth.uid()));

-- ============================================================================
-- PART 2: Optimize Multiple Permissive Policies
-- ============================================================================

-- Properties table: Combine "Anyone can view active properties" with "Users can view own properties"
DROP POLICY IF EXISTS "Anyone can view active properties" ON public.properties;

-- Recreate as single optimized policy
CREATE POLICY "View active or own properties"
ON public.properties FOR SELECT
TO authenticated
USING (
    status = 'active' OR user_id = (select auth.uid())
);

-- Also allow anon users to view active properties
CREATE POLICY "Anon users can view active properties"
ON public.properties FOR SELECT
TO anon
USING (status = 'active');

-- Payouts table: Keep service role separate, but optimize user policy
DROP POLICY IF EXISTS "Service role can manage all payouts" ON public.payouts;

CREATE POLICY "Service role can manage all payouts"
ON public.payouts FOR ALL
TO service_role
USING (true);

-- ============================================================================
-- PART 3: Drop Duplicate Indexes on kv_store table
-- ============================================================================

-- Keep only the first index, drop all duplicates
DROP INDEX IF EXISTS public.kv_store_3c640fc2_key_idx1;
DROP INDEX IF EXISTS public.kv_store_3c640fc2_key_idx2;
DROP INDEX IF EXISTS public.kv_store_3c640fc2_key_idx3;
DROP INDEX IF EXISTS public.kv_store_3c640fc2_key_idx4;
DROP INDEX IF EXISTS public.kv_store_3c640fc2_key_idx5;
DROP INDEX IF EXISTS public.kv_store_3c640fc2_key_idx6;
DROP INDEX IF EXISTS public.kv_store_3c640fc2_key_idx7;

-- Verify the original index still exists
-- public.kv_store_3c640fc2_key_idx should remain

-- ============================================================================
-- VERIFICATION
-- ============================================================================

DO $$
DECLARE
    policy_count INTEGER;
    index_count INTEGER;
BEGIN
    -- Check that RLS policies are still active
    SELECT COUNT(*)
    INTO policy_count
    FROM pg_policies
    WHERE schemaname = 'public'
    AND tablename IN ('users', 'properties', 'bookings', 'host_notifications', 'payouts');
    
    IF policy_count > 0 THEN
        RAISE NOTICE 'SUCCESS: RLS policies recreated with performance optimizations';
    ELSE
        RAISE WARNING 'WARNING: No RLS policies found, check migration';
    END IF;
    
    -- Check duplicate indexes are removed
    SELECT COUNT(*)
    INTO index_count
    FROM pg_indexes
    WHERE schemaname = 'public'
    AND tablename = 'kv_store_3c640fc2'
    AND indexname LIKE 'kv_store_3c640fc2_key_idx%';
    
    IF index_count = 1 THEN
        RAISE NOTICE 'SUCCESS: Duplicate indexes removed, only 1 index remains';
    ELSE
        RAISE WARNING 'WARNING: Expected 1 index, found %', index_count;
    END IF;
END;
$$;

