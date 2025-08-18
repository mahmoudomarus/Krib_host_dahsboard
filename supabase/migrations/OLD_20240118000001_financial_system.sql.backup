-- Financial and Payouts System for Krib AI
-- This migration adds comprehensive financial tracking and payouts functionality

-- Host Bank Account Information
CREATE TABLE IF NOT EXISTS host_bank_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    account_holder_name VARCHAR(255) NOT NULL,
    bank_name VARCHAR(255) NOT NULL,
    account_number_last4 VARCHAR(4) NOT NULL, -- Only store last 4 digits for security
    routing_number VARCHAR(9),
    account_type VARCHAR(20) CHECK (account_type IN ('checking', 'savings')) DEFAULT 'checking',
    is_primary BOOLEAN DEFAULT false,
    is_verified BOOLEAN DEFAULT false,
    stripe_account_id VARCHAR(255), -- For Stripe Connect integration
    verification_status VARCHAR(20) CHECK (verification_status IN ('pending', 'verified', 'failed', 'under_review')) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Financial Transactions (Revenue tracking)
CREATE TABLE IF NOT EXISTS financial_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID, -- Will add foreign key constraint after bookings table exists
    property_id UUID, -- Will add foreign key constraint after properties table exists  
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Transaction Details
    transaction_type VARCHAR(20) CHECK (transaction_type IN ('booking_payment', 'refund', 'cancellation_fee', 'cleaning_fee', 'security_deposit')) NOT NULL,
    gross_amount DECIMAL(10,2) NOT NULL, -- Total amount paid by guest
    platform_fee DECIMAL(10,2) NOT NULL DEFAULT 0, -- Krib AI platform fee (e.g., 3%)
    payment_processing_fee DECIMAL(10,2) NOT NULL DEFAULT 0, -- Stripe/payment processor fee
    net_amount DECIMAL(10,2) NOT NULL, -- Amount due to host
    
    -- Status and Timing
    status VARCHAR(20) CHECK (status IN ('pending', 'completed', 'failed', 'disputed', 'refunded')) DEFAULT 'pending',
    payment_date TIMESTAMP WITH TIME ZONE, -- When guest paid
    processed_date TIMESTAMP WITH TIME ZONE, -- When we processed it
    
    -- External References
    stripe_payment_intent_id VARCHAR(255),
    stripe_transfer_id VARCHAR(255),
    external_transaction_id VARCHAR(255),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Host Payouts (Money going to hosts)
CREATE TABLE IF NOT EXISTS host_payouts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    bank_account_id UUID NOT NULL REFERENCES host_bank_accounts(id) ON DELETE RESTRICT,
    
    -- Payout Details
    payout_amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payout_method VARCHAR(20) CHECK (payout_method IN ('bank_transfer', 'stripe_express', 'paypal', 'manual')) DEFAULT 'bank_transfer',
    
    -- Status and Timing
    status VARCHAR(20) CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')) DEFAULT 'pending',
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Processing Details
    stripe_payout_id VARCHAR(255),
    external_payout_id VARCHAR(255),
    failure_reason TEXT,
    
    -- Metadata
    payout_period_start DATE, -- Start of earning period
    payout_period_end DATE,   -- End of earning period
    transaction_count INTEGER DEFAULT 0, -- Number of transactions included
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Junction table linking payouts to specific transactions
CREATE TABLE IF NOT EXISTS payout_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payout_id UUID NOT NULL REFERENCES host_payouts(id) ON DELETE CASCADE,
    transaction_id UUID NOT NULL REFERENCES financial_transactions(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL, -- Amount from this transaction included in payout
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(payout_id, transaction_id)
);

-- Tax Documents (1099s, etc.)
CREATE TABLE IF NOT EXISTS tax_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Document Details
    document_type VARCHAR(20) CHECK (document_type IN ('1099k', '1099misc', 'annual_summary')) NOT NULL,
    tax_year INTEGER NOT NULL,
    total_earnings DECIMAL(12,2) NOT NULL,
    total_transactions INTEGER NOT NULL,
    
    -- File Information
    document_url TEXT, -- Link to generated PDF
    generated_at TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    
    -- Status
    status VARCHAR(20) CHECK (status IN ('draft', 'generated', 'sent', 'filed')) DEFAULT 'draft',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Payout Settings per host
CREATE TABLE IF NOT EXISTS payout_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Payout Preferences
    payout_frequency VARCHAR(20) CHECK (payout_frequency IN ('daily', 'weekly', 'biweekly', 'monthly')) DEFAULT 'weekly',
    minimum_payout_amount DECIMAL(10,2) DEFAULT 25.00,
    auto_payout_enabled BOOLEAN DEFAULT true,
    payout_day_of_week INTEGER CHECK (payout_day_of_week BETWEEN 0 AND 6), -- 0 = Sunday
    payout_day_of_month INTEGER CHECK (payout_day_of_month BETWEEN 1 AND 31),
    
    -- Hold period (how many days to hold funds before payout)
    hold_period_days INTEGER DEFAULT 1, -- 1 day hold period
    
    -- Tax Information
    tax_id VARCHAR(50), -- SSN or EIN (encrypted)
    tax_id_type VARCHAR(10) CHECK (tax_id_type IN ('ssn', 'ein')),
    business_type VARCHAR(20) CHECK (business_type IN ('individual', 'business', 'llc', 'corporation')),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_financial_transactions_user_id ON financial_transactions(user_id);
CREATE INDEX idx_financial_transactions_booking_id ON financial_transactions(booking_id);
CREATE INDEX idx_financial_transactions_status ON financial_transactions(status);
CREATE INDEX idx_financial_transactions_payment_date ON financial_transactions(payment_date);

CREATE INDEX idx_host_payouts_user_id ON host_payouts(user_id);
CREATE INDEX idx_host_payouts_status ON host_payouts(status);
CREATE INDEX idx_host_payouts_requested_at ON host_payouts(requested_at);

CREATE INDEX idx_payout_transactions_payout_id ON payout_transactions(payout_id);
CREATE INDEX idx_payout_transactions_transaction_id ON payout_transactions(transaction_id);

CREATE INDEX idx_host_bank_accounts_user_id ON host_bank_accounts(user_id);
CREATE INDEX idx_host_bank_accounts_is_primary ON host_bank_accounts(is_primary);

-- RLS Policies
ALTER TABLE host_bank_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE financial_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE host_payouts ENABLE ROW LEVEL SECURITY;
ALTER TABLE payout_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE tax_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE payout_settings ENABLE ROW LEVEL SECURITY;

-- Bank accounts - users can only see their own
CREATE POLICY "Users can view own bank accounts" ON host_bank_accounts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own bank accounts" ON host_bank_accounts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own bank accounts" ON host_bank_accounts
    FOR UPDATE USING (auth.uid() = user_id);

-- Financial transactions - users can only see their own
CREATE POLICY "Users can view own transactions" ON financial_transactions
    FOR SELECT USING (auth.uid() = user_id);

-- Host payouts - users can only see their own
CREATE POLICY "Users can view own payouts" ON host_payouts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can request payouts" ON host_payouts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Payout transactions - users can only see their own through payouts
CREATE POLICY "Users can view own payout transactions" ON payout_transactions
    FOR SELECT USING (EXISTS (
        SELECT 1 FROM host_payouts hp 
        WHERE hp.id = payout_transactions.payout_id 
        AND hp.user_id = auth.uid()
    ));

-- Tax documents - users can only see their own
CREATE POLICY "Users can view own tax documents" ON tax_documents
    FOR SELECT USING (auth.uid() = user_id);

-- Payout settings - users can only see and modify their own
CREATE POLICY "Users can view own payout settings" ON payout_settings
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own payout settings" ON payout_settings
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own payout settings" ON payout_settings
    FOR UPDATE USING (auth.uid() = user_id);

-- Functions for financial calculations
CREATE OR REPLACE FUNCTION calculate_host_balance(host_user_id UUID)
RETURNS DECIMAL(10,2) AS $$
DECLARE
    total_earned DECIMAL(10,2);
    total_paid_out DECIMAL(10,2);
BEGIN
    -- Calculate total earnings from completed transactions
    SELECT COALESCE(SUM(net_amount), 0) INTO total_earned
    FROM financial_transactions
    WHERE user_id = host_user_id
    AND status = 'completed';
    
    -- Calculate total amount already paid out
    SELECT COALESCE(SUM(payout_amount), 0) INTO total_paid_out
    FROM host_payouts
    WHERE user_id = host_user_id
    AND status = 'completed';
    
    RETURN total_earned - total_paid_out;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get pending earnings (available for payout)
CREATE OR REPLACE FUNCTION get_pending_earnings(host_user_id UUID)
RETURNS DECIMAL(10,2) AS $$
DECLARE
    pending_amount DECIMAL(10,2);
    hold_days INTEGER;
BEGIN
    -- Get user's hold period
    SELECT COALESCE(hold_period_days, 1) INTO hold_days
    FROM payout_settings
    WHERE user_id = host_user_id;
    
    -- Calculate earnings that are past the hold period and not yet included in payouts
    SELECT COALESCE(SUM(ft.net_amount), 0) INTO pending_amount
    FROM financial_transactions ft
    WHERE ft.user_id = host_user_id
    AND ft.status = 'completed'
    AND ft.processed_date <= NOW() - INTERVAL '1 day' * hold_days
    AND NOT EXISTS (
        SELECT 1 FROM payout_transactions pt
        JOIN host_payouts hp ON pt.payout_id = hp.id
        WHERE pt.transaction_id = ft.id
        AND hp.status IN ('pending', 'processing', 'completed')
    );
    
    RETURN pending_amount;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to automatically create financial transaction when booking is confirmed
CREATE OR REPLACE FUNCTION create_financial_transaction_on_booking()
RETURNS TRIGGER AS $$
DECLARE
    platform_fee_rate DECIMAL(5,4) := 0.03; -- 3% platform fee
    processing_fee_rate DECIMAL(5,4) := 0.029; -- 2.9% + $0.30 Stripe fee
    processing_fee_fixed DECIMAL(4,2) := 0.30;
    gross_amount DECIMAL(10,2);
    calculated_platform_fee DECIMAL(10,2);
    calculated_processing_fee DECIMAL(10,2);
    net_amount DECIMAL(10,2);
BEGIN
    -- Only create transaction when booking moves to confirmed status
    IF OLD.status != 'confirmed' AND NEW.status = 'confirmed' THEN
        gross_amount := NEW.total_amount;
        calculated_platform_fee := gross_amount * platform_fee_rate;
        calculated_processing_fee := (gross_amount * processing_fee_rate) + processing_fee_fixed;
        net_amount := gross_amount - calculated_platform_fee - calculated_processing_fee;
        
        INSERT INTO financial_transactions (
            booking_id,
            property_id,
            user_id,
            transaction_type,
            gross_amount,
            platform_fee,
            payment_processing_fee,
            net_amount,
            status,
            payment_date,
            processed_date
        ) VALUES (
            NEW.id,
            NEW.property_id,
            (SELECT user_id FROM properties WHERE id = NEW.property_id),
            'booking_payment',
            gross_amount,
            calculated_platform_fee,
            calculated_processing_fee,
            net_amount,
            'completed',
            NOW(),
            NOW()
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_create_financial_transaction
    AFTER UPDATE ON bookings
    FOR EACH ROW
    EXECUTE FUNCTION create_financial_transaction_on_booking();

COMMENT ON TABLE host_bank_accounts IS 'Host bank account information for payouts';
COMMENT ON TABLE financial_transactions IS 'All financial transactions including platform fees';
COMMENT ON TABLE host_payouts IS 'Payout requests and processing status';
COMMENT ON TABLE payout_transactions IS 'Links payouts to specific transactions';
COMMENT ON TABLE tax_documents IS 'Tax documents like 1099s for hosts';
COMMENT ON TABLE payout_settings IS 'Host payout preferences and settings';
