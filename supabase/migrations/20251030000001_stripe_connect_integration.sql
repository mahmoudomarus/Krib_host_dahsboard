-- Stripe Connect Integration Migration
-- Adds fields for Stripe Connect Express accounts, payment processing, and payouts

-- =====================================================================
-- UPDATE USERS TABLE - Add Stripe Connect fields
-- =====================================================================

ALTER TABLE public.users 
ADD COLUMN IF NOT EXISTS stripe_account_id VARCHAR(255) UNIQUE,
ADD COLUMN IF NOT EXISTS stripe_account_status VARCHAR(50) DEFAULT 'not_connected' 
    CHECK (stripe_account_status IN ('not_connected', 'pending', 'active', 'restricted', 'disabled')),
ADD COLUMN IF NOT EXISTS stripe_charges_enabled BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS stripe_payouts_enabled BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS stripe_onboarding_completed BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS stripe_details_submitted BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS bank_account_last4 VARCHAR(4),
ADD COLUMN IF NOT EXISTS bank_account_country VARCHAR(2),
ADD COLUMN IF NOT EXISTS stripe_requirements JSONB DEFAULT '{"currently_due": [], "eventually_due": [], "past_due": []}'::jsonb,
ADD COLUMN IF NOT EXISTS stripe_updated_at TIMESTAMP WITH TIME ZONE;

-- Index for Stripe account lookups
CREATE INDEX IF NOT EXISTS idx_users_stripe_account ON public.users(stripe_account_id) WHERE stripe_account_id IS NOT NULL;

-- =====================================================================
-- UPDATE BOOKINGS TABLE - Add Stripe payment fields
-- =====================================================================

ALTER TABLE public.bookings
ADD COLUMN IF NOT EXISTS stripe_payment_intent_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS stripe_charge_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS stripe_transfer_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS stripe_client_secret VARCHAR(500),
ADD COLUMN IF NOT EXISTS platform_fee_amount DECIMAL(10, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS host_payout_amount DECIMAL(10, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS host_payout_status VARCHAR(50) DEFAULT 'pending' 
    CHECK (host_payout_status IN ('pending', 'processing', 'paid', 'failed', 'canceled')),
ADD COLUMN IF NOT EXISTS host_payout_date TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS payment_processed_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS refund_amount DECIMAL(10, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS refund_reason TEXT;

-- Update existing payment_status check constraint
ALTER TABLE public.bookings DROP CONSTRAINT IF EXISTS bookings_payment_status_check;
ALTER TABLE public.bookings ADD CONSTRAINT bookings_payment_status_check 
    CHECK (payment_status IN ('pending', 'processing', 'succeeded', 'failed', 'refunded', 'partially_refunded'));

-- Indexes for payment lookups
CREATE INDEX IF NOT EXISTS idx_bookings_payment_intent ON public.bookings(stripe_payment_intent_id) WHERE stripe_payment_intent_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_bookings_payout_status ON public.bookings(host_payout_status);

-- =====================================================================
-- CREATE STRIPE_EVENTS TABLE - Webhook event log
-- =====================================================================

CREATE TABLE IF NOT EXISTS public.stripe_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    stripe_event_id VARCHAR(255) UNIQUE NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    
    -- Related Stripe IDs
    account_id VARCHAR(255),
    payment_intent_id VARCHAR(255),
    charge_id VARCHAR(255),
    transfer_id VARCHAR(255),
    payout_id VARCHAR(255),
    
    -- Event data
    raw_data JSONB NOT NULL,
    api_version VARCHAR(50),
    
    -- Processing status
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    event_created TIMESTAMP WITH TIME ZONE
);

-- Indexes for event processing
CREATE INDEX IF NOT EXISTS idx_stripe_events_event_id ON public.stripe_events(stripe_event_id);
CREATE INDEX IF NOT EXISTS idx_stripe_events_type ON public.stripe_events(event_type);
CREATE INDEX IF NOT EXISTS idx_stripe_events_processed ON public.stripe_events(processed) WHERE processed = FALSE;
CREATE INDEX IF NOT EXISTS idx_stripe_events_account ON public.stripe_events(account_id) WHERE account_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_stripe_events_payment_intent ON public.stripe_events(payment_intent_id) WHERE payment_intent_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_stripe_events_created ON public.stripe_events(created_at DESC);

-- =====================================================================
-- CREATE PAYOUTS TABLE - Track host payouts
-- =====================================================================

CREATE TABLE IF NOT EXISTS public.payouts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- References
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    booking_id UUID REFERENCES public.bookings(id) ON DELETE SET NULL,
    property_id UUID REFERENCES public.properties(id) ON DELETE SET NULL,
    
    -- Stripe IDs
    stripe_transfer_id VARCHAR(255) UNIQUE,
    stripe_payout_id VARCHAR(255),
    stripe_destination_payment VARCHAR(255),
    
    -- Amount details
    amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
    currency VARCHAR(3) DEFAULT 'AED' NOT NULL,
    platform_fee DECIMAL(10, 2) DEFAULT 0,
    original_booking_amount DECIMAL(10, 2),
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'pending' NOT NULL
        CHECK (status IN ('pending', 'processing', 'in_transit', 'paid', 'failed', 'canceled', 'reversed')),
    
    -- Descriptions and errors
    description TEXT,
    failure_code VARCHAR(100),
    failure_message TEXT,
    
    -- Timing
    initiated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    expected_arrival_date DATE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Additional data
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Indexes for payout queries
CREATE INDEX IF NOT EXISTS idx_payouts_user ON public.payouts(user_id);
CREATE INDEX IF NOT EXISTS idx_payouts_booking ON public.payouts(booking_id) WHERE booking_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_payouts_status ON public.payouts(status);
CREATE INDEX IF NOT EXISTS idx_payouts_transfer_id ON public.payouts(stripe_transfer_id) WHERE stripe_transfer_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_payouts_created ON public.payouts(created_at DESC);

-- =====================================================================
-- UPDATE TRIGGERS
-- =====================================================================

-- Update trigger for payouts updated_at
CREATE OR REPLACE FUNCTION update_payouts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_payouts_updated_at ON public.payouts;
CREATE TRIGGER set_payouts_updated_at
    BEFORE UPDATE ON public.payouts
    FOR EACH ROW
    EXECUTE FUNCTION update_payouts_updated_at();

-- =====================================================================
-- RLS POLICIES
-- =====================================================================

-- Enable RLS
ALTER TABLE public.stripe_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payouts ENABLE ROW LEVEL SECURITY;

-- Stripe events: Only accessible by service role
CREATE POLICY "Service role can manage stripe events"
    ON public.stripe_events
    FOR ALL
    USING (auth.role() = 'service_role');

-- Payouts: Users can view their own payouts
CREATE POLICY "Users can view own payouts"
    ON public.payouts
    FOR SELECT
    USING (auth.uid() = user_id);

-- Payouts: Service role can manage all
CREATE POLICY "Service role can manage all payouts"
    ON public.payouts
    FOR ALL
    USING (auth.role() = 'service_role');

-- =====================================================================
-- HELPER FUNCTIONS
-- =====================================================================

-- Function to calculate platform fee
CREATE OR REPLACE FUNCTION calculate_platform_fee(
    booking_amount DECIMAL,
    fee_percentage DECIMAL DEFAULT 15.0
)
RETURNS DECIMAL AS $$
BEGIN
    RETURN ROUND(booking_amount * (fee_percentage / 100.0), 2);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to get host payout amount
CREATE OR REPLACE FUNCTION calculate_host_payout(
    booking_amount DECIMAL,
    fee_percentage DECIMAL DEFAULT 15.0
)
RETURNS DECIMAL AS $$
BEGIN
    RETURN booking_amount - calculate_platform_fee(booking_amount, fee_percentage);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- =====================================================================
-- COMMENTS
-- =====================================================================

COMMENT ON TABLE public.stripe_events IS 'Log of all Stripe webhook events for audit and debugging';
COMMENT ON TABLE public.payouts IS 'Host payout tracking with Stripe transfer details';
COMMENT ON COLUMN public.users.stripe_account_id IS 'Stripe Connect Express account ID';
COMMENT ON COLUMN public.users.stripe_account_status IS 'Current status of Stripe Connect account';
COMMENT ON COLUMN public.bookings.stripe_payment_intent_id IS 'Stripe PaymentIntent ID for guest payment';
COMMENT ON COLUMN public.bookings.platform_fee_amount IS 'Platform commission (typically 15%)';
COMMENT ON COLUMN public.bookings.host_payout_amount IS 'Amount to be paid to host after platform fee';

