-- Security Fixes for Supabase Linter Issues
-- Run this migration to fix critical security vulnerabilities

-- ============================================================================
-- CRITICAL: Enable RLS on Reference Tables
-- ============================================================================

-- These are reference/lookup tables that should be read-only for all users
-- Enable RLS and create policies to allow public read access

ALTER TABLE public.amenity_suggestions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.property_type_info ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.booking_status_types ENABLE ROW LEVEL SECURITY;

-- Allow public read access to reference tables
CREATE POLICY "Allow public read access to amenity_suggestions"
ON public.amenity_suggestions FOR SELECT
TO public
USING (true);

CREATE POLICY "Allow public read access to property_type_info"
ON public.property_type_info FOR SELECT
TO public
USING (true);

CREATE POLICY "Allow public read access to booking_status_types"
ON public.booking_status_types FOR SELECT
TO public
USING (true);

-- ============================================================================
-- SECURITY: Fix Function Search Path Vulnerabilities
-- ============================================================================

-- Add SECURITY DEFINER and set search_path to prevent search_path injection attacks
-- This ensures functions execute with a fixed schema search path

CREATE OR REPLACE FUNCTION public.update_payouts_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION public.calculate_platform_fee(booking_amount NUMERIC)
RETURNS NUMERIC
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    platform_fee_percentage NUMERIC := 15.0;
BEGIN
    RETURN booking_amount * (platform_fee_percentage / 100);
END;
$$;

CREATE OR REPLACE FUNCTION public.cleanup_expired_notifications()
RETURNS INTEGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM public.host_notifications
    WHERE expires_at < NOW() AND expires_at IS NOT NULL;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$;

CREATE OR REPLACE FUNCTION public.calculate_host_payout(booking_amount NUMERIC)
RETURNS NUMERIC
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    platform_fee_percentage NUMERIC := 15.0;
BEGIN
    RETURN booking_amount * (1 - (platform_fee_percentage / 100));
END;
$$;

CREATE OR REPLACE FUNCTION public.get_unread_notification_count(p_host_id UUID)
RETURNS INTEGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    unread_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO unread_count
    FROM public.host_notifications
    WHERE host_id = p_host_id
    AND is_read = FALSE;
    
    RETURN unread_count;
END;
$$;

CREATE OR REPLACE FUNCTION public.disable_failed_webhook_subscriptions()
RETURNS INTEGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    disabled_count INTEGER;
BEGIN
    UPDATE public.webhook_subscriptions
    SET is_active = FALSE
    WHERE retry_count >= 5
    AND is_active = TRUE;
    
    GET DIAGNOSTICS disabled_count = ROW_COUNT;
    RETURN disabled_count;
END;
$$;

CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION public.get_pending_earnings(p_user_id UUID)
RETURNS NUMERIC
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    pending_total NUMERIC;
BEGIN
    SELECT COALESCE(SUM(host_payout_amount), 0)
    INTO pending_total
    FROM public.bookings
    WHERE property_id IN (
        SELECT id FROM public.properties WHERE user_id = p_user_id
    )
    AND payment_status = 'succeeded'
    AND host_payout_status = 'pending';
    
    RETURN pending_total;
END;
$$;

CREATE OR REPLACE FUNCTION public.create_financial_transaction_on_booking()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    IF NEW.payment_status = 'succeeded' AND OLD.payment_status != 'succeeded' THEN
        NEW.platform_fee_amount = calculate_platform_fee(NEW.total_amount);
        NEW.host_payout_amount = calculate_host_payout(NEW.total_amount);
    END IF;
    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION public.calculate_host_balance(p_user_id UUID)
RETURNS NUMERIC
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    total_balance NUMERIC;
BEGIN
    SELECT COALESCE(SUM(amount), 0)
    INTO total_balance
    FROM public.payouts
    WHERE user_id = p_user_id
    AND status = 'paid';
    
    RETURN total_balance;
END;
$$;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Verify RLS is enabled on reference tables
DO $$
DECLARE
    rls_check INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO rls_check
    FROM pg_tables
    WHERE schemaname = 'public'
    AND tablename IN ('amenity_suggestions', 'property_type_info', 'booking_status_types')
    AND rowsecurity = true;
    
    IF rls_check = 3 THEN
        RAISE NOTICE 'SUCCESS: RLS enabled on all reference tables';
    ELSE
        RAISE WARNING 'WARNING: RLS not enabled on all reference tables';
    END IF;
END;
$$;

