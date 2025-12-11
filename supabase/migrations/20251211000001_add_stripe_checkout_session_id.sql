-- Add stripe_checkout_session_id column to bookings table
-- This column stores the Stripe Checkout session ID for guest payments

ALTER TABLE public.bookings 
ADD COLUMN IF NOT EXISTS stripe_checkout_session_id TEXT;

-- Add index for faster lookups
CREATE INDEX IF NOT EXISTS idx_bookings_stripe_checkout_session_id 
ON public.bookings(stripe_checkout_session_id) 
WHERE stripe_checkout_session_id IS NOT NULL;

-- Add comment for documentation
COMMENT ON COLUMN public.bookings.stripe_checkout_session_id IS 'Stripe Checkout session ID for guest payment processing';

