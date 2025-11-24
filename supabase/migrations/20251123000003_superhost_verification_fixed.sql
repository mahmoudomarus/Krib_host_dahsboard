-- Superhost Verification System (Fixed - Safe to rerun)
-- Add superhost status and verification to users table

-- Add superhost columns to users table
ALTER TABLE public.users 
ADD COLUMN IF NOT EXISTS is_superhost BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS superhost_status TEXT DEFAULT 'regular' CHECK (superhost_status IN ('regular', 'pending', 'approved', 'rejected')),
ADD COLUMN IF NOT EXISTS superhost_requested_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS superhost_approved_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS superhost_verified_by UUID REFERENCES auth.users(id);

-- Create superhost_verification_requests table
CREATE TABLE IF NOT EXISTS public.superhost_verification_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
  request_message TEXT,
  rejection_reason TEXT,
  admin_notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  reviewed_at TIMESTAMPTZ,
  reviewed_by UUID REFERENCES auth.users(id),
  
  -- Host performance metrics at time of request
  total_properties INTEGER DEFAULT 0,
  total_bookings INTEGER DEFAULT 0,
  total_revenue DECIMAL(10, 2) DEFAULT 0,
  average_rating DECIMAL(3, 2) DEFAULT 0,
  response_rate DECIMAL(5, 2) DEFAULT 0,
  cancellation_rate DECIMAL(5, 2) DEFAULT 0
);

-- Drop unique constraint if exists and recreate (in case structure changed)
DO $$
BEGIN
  ALTER TABLE public.superhost_verification_requests 
  DROP CONSTRAINT IF EXISTS unique_pending_request_per_user;
EXCEPTION
  WHEN undefined_object THEN NULL;
END $$;

ALTER TABLE public.superhost_verification_requests
ADD CONSTRAINT unique_pending_request_per_user UNIQUE (user_id, status);

-- Enable RLS on superhost_verification_requests
ALTER TABLE public.superhost_verification_requests ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Hosts can view their own verification requests" ON public.superhost_verification_requests;
DROP POLICY IF EXISTS "Hosts can create verification requests" ON public.superhost_verification_requests;
DROP POLICY IF EXISTS "Admins can update verification requests" ON public.superhost_verification_requests;
DROP POLICY IF EXISTS "Admins can view all verification requests" ON public.superhost_verification_requests;

-- Create RLS Policies

-- Hosts can view their own requests
CREATE POLICY "Hosts can view their own verification requests"
  ON public.superhost_verification_requests
  FOR SELECT
  USING ((select auth.uid()) = user_id);

-- Hosts can create their own requests
CREATE POLICY "Hosts can create verification requests"
  ON public.superhost_verification_requests
  FOR INSERT
  WITH CHECK ((select auth.uid()) = user_id);

-- Only admins/super admins can update requests
CREATE POLICY "Admins can update verification requests"
  ON public.superhost_verification_requests
  FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM public.users
      WHERE id = (select auth.uid())
      AND role IN ('admin', 'super_admin')
    )
  );

-- Admins can view all requests
CREATE POLICY "Admins can view all verification requests"
  ON public.superhost_verification_requests
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.users
      WHERE id = (select auth.uid())
      AND role IN ('admin', 'super_admin')
    )
  );

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_superhost_verification_user_id ON public.superhost_verification_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_superhost_verification_status ON public.superhost_verification_requests(status);
CREATE INDEX IF NOT EXISTS idx_superhost_verification_created_at ON public.superhost_verification_requests(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_users_superhost_status ON public.users(superhost_status) WHERE is_superhost = TRUE;

-- Function to calculate host metrics for superhost eligibility
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
      WHERE p.user_id = host_user_id AND b.status = 'confirmed'
    ),
    'total_revenue', (
      SELECT COALESCE(SUM(total_amount), 0) 
      FROM bookings b 
      JOIN properties p ON b.property_id = p.id 
      WHERE p.user_id = host_user_id AND b.status = 'confirmed'
    ),
    'average_rating', (
      SELECT COALESCE(AVG(p.average_rating), 0) 
      FROM properties p 
      WHERE p.user_id = host_user_id
    ),
    'response_rate', (
      -- Calculate based on how quickly host responds to bookings
      SELECT COALESCE(
        (COUNT(CASE WHEN b.status IN ('confirmed', 'rejected') THEN 1 END)::DECIMAL / NULLIF(COUNT(*), 0)) * 100,
        0
      )
      FROM bookings b
      JOIN properties p ON b.property_id = p.id
      WHERE p.user_id = host_user_id
    ),
    'cancellation_rate', (
      -- Calculate cancellation rate
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

-- Function to check superhost eligibility
CREATE OR REPLACE FUNCTION public.check_superhost_eligibility(host_user_id UUID)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  metrics JSON;
  eligible BOOLEAN := FALSE;
  reasons TEXT[] := ARRAY[]::TEXT[];
BEGIN
  metrics := calculate_host_metrics(host_user_id);
  
  -- Eligibility criteria
  IF (metrics->>'total_properties')::INTEGER >= 1 THEN
    eligible := TRUE;
  ELSE
    reasons := array_append(reasons, 'Need at least 1 active property');
  END IF;
  
  IF (metrics->>'total_bookings')::INTEGER >= 5 THEN
    eligible := eligible AND TRUE;
  ELSE
    reasons := array_append(reasons, 'Need at least 5 completed bookings');
    eligible := FALSE;
  END IF;
  
  IF (metrics->>'average_rating')::DECIMAL >= 4.5 THEN
    eligible := eligible AND TRUE;
  ELSE
    reasons := array_append(reasons, 'Average rating must be 4.5 or higher');
    eligible := FALSE;
  END IF;
  
  IF (metrics->>'response_rate')::DECIMAL >= 90 THEN
    eligible := eligible AND TRUE;
  ELSE
    reasons := array_append(reasons, 'Response rate must be 90% or higher');
    eligible := FALSE;
  END IF;
  
  IF (metrics->>'cancellation_rate')::DECIMAL <= 5 THEN
    eligible := eligible AND TRUE;
  ELSE
    reasons := array_append(reasons, 'Cancellation rate must be 5% or lower');
    eligible := FALSE;
  END IF;
  
  RETURN json_build_object(
    'eligible', eligible,
    'reasons', reasons,
    'metrics', metrics
  );
END;
$$;

-- Drop trigger if exists
DROP TRIGGER IF EXISTS trigger_update_superhost_verification_updated_at ON public.superhost_verification_requests;

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_superhost_verification_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$;

CREATE TRIGGER trigger_update_superhost_verification_updated_at
  BEFORE UPDATE ON public.superhost_verification_requests
  FOR EACH ROW
  EXECUTE FUNCTION update_superhost_verification_updated_at();

-- Comment on table
COMMENT ON TABLE public.superhost_verification_requests IS 'Stores superhost verification requests and their approval status';
COMMENT ON COLUMN public.users.is_superhost IS 'Whether the user is currently a superhost';
COMMENT ON COLUMN public.users.superhost_status IS 'Superhost verification status: regular, pending, approved, rejected';

