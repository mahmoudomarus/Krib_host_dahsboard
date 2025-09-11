-- Webhook and Notification System Migration
-- This migration adds webhook subscriptions and host notifications functionality

-- Webhook Subscriptions Table
CREATE TABLE IF NOT EXISTS public.webhook_subscriptions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    agent_name VARCHAR(255) NOT NULL,
    webhook_url TEXT NOT NULL,
    api_key VARCHAR(500) NOT NULL,
    events TEXT[] NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_successful_call TIMESTAMP WITH TIME ZONE,
    failed_attempts INTEGER DEFAULT 0,
    max_failed_attempts INTEGER DEFAULT 5
);

-- Host Notifications Table
CREATE TABLE IF NOT EXISTS public.host_notifications (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    host_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('new_booking', 'payment_received', 'guest_message', 'urgent', 'booking_update')),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    booking_id UUID,
    property_id UUID,
    priority VARCHAR(10) DEFAULT 'medium' CHECK (priority IN ('high', 'medium', 'low')),
    action_required BOOLEAN DEFAULT false,
    action_url TEXT,
    is_read BOOLEAN DEFAULT false,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Host Settings Table (for auto-approval and other settings)
CREATE TABLE IF NOT EXISTS public.host_settings (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL UNIQUE,
    auto_approve_bookings BOOLEAN DEFAULT false,
    auto_approve_amount_limit DECIMAL(10,2) DEFAULT 1000.00,
    notification_preferences JSONB DEFAULT '{"email": true, "sms": false, "push": true}'::jsonb,
    webhook_notifications BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_webhook_subscriptions_active ON public.webhook_subscriptions(is_active);
CREATE INDEX idx_webhook_subscriptions_events ON public.webhook_subscriptions USING GIN(events);
CREATE INDEX idx_webhook_subscriptions_agent ON public.webhook_subscriptions(agent_name);

CREATE INDEX idx_host_notifications_host_id ON public.host_notifications(host_id);
CREATE INDEX idx_host_notifications_unread ON public.host_notifications(host_id, is_read);
CREATE INDEX idx_host_notifications_type ON public.host_notifications(type);
CREATE INDEX idx_host_notifications_created_at ON public.host_notifications(created_at DESC);
CREATE INDEX idx_host_notifications_booking_id ON public.host_notifications(booking_id);

CREATE INDEX idx_host_settings_user_id ON public.host_settings(user_id);

-- RLS Policies for webhook_subscriptions (only external services can access)
ALTER TABLE public.webhook_subscriptions ENABLE ROW LEVEL SECURITY;

-- Policy: External services can manage their own webhook subscriptions
CREATE POLICY "External services can manage webhook subscriptions" ON public.webhook_subscriptions
    FOR ALL USING (true);

-- RLS Policies for host_notifications
ALTER TABLE public.host_notifications ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own notifications
CREATE POLICY "Users can view own notifications" ON public.host_notifications
    FOR SELECT USING (auth.uid() = host_id);

-- Policy: Users can update their own notifications (mark as read)
CREATE POLICY "Users can update own notifications" ON public.host_notifications
    FOR UPDATE USING (auth.uid() = host_id);

-- Policy: System can insert notifications for any user
CREATE POLICY "System can insert notifications" ON public.host_notifications
    FOR INSERT WITH CHECK (true);

-- RLS Policies for host_settings
ALTER TABLE public.host_settings ENABLE ROW LEVEL SECURITY;

-- Policy: Users can manage their own settings
CREATE POLICY "Users can manage own settings" ON public.host_settings
    FOR ALL USING (auth.uid() = user_id);

-- Functions

-- Function to get unread notification count for a host
CREATE OR REPLACE FUNCTION public.get_unread_notification_count(host_user_id UUID)
RETURNS INTEGER AS $$
BEGIN
    RETURN (
        SELECT COUNT(*)::INTEGER
        FROM public.host_notifications
        WHERE host_id = host_user_id
        AND is_read = false
        AND (expires_at IS NULL OR expires_at > NOW())
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to clean up expired notifications
CREATE OR REPLACE FUNCTION public.cleanup_expired_notifications()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM public.host_notifications
    WHERE expires_at IS NOT NULL AND expires_at < NOW();
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to disable failed webhook subscriptions
CREATE OR REPLACE FUNCTION public.disable_failed_webhook_subscriptions()
RETURNS INTEGER AS $$
DECLARE
    disabled_count INTEGER;
BEGIN
    UPDATE public.webhook_subscriptions
    SET is_active = false,
        updated_at = NOW()
    WHERE failed_attempts >= max_failed_attempts
    AND is_active = true;
    
    GET DIAGNOSTICS disabled_count = ROW_COUNT;
    RETURN disabled_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update triggers
CREATE TRIGGER update_webhook_subscriptions_updated_at
    BEFORE UPDATE ON public.webhook_subscriptions
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_host_notifications_updated_at
    BEFORE UPDATE ON public.host_notifications
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_host_settings_updated_at
    BEFORE UPDATE ON public.host_settings
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO authenticated;

-- Insert default host settings for existing users
INSERT INTO public.host_settings (user_id, auto_approve_bookings, auto_approve_amount_limit)
SELECT id, false, 1000.00
FROM auth.users
WHERE id NOT IN (SELECT user_id FROM public.host_settings)
ON CONFLICT (user_id) DO NOTHING;

-- Comments for documentation
COMMENT ON TABLE public.webhook_subscriptions IS 'External AI agent webhook subscriptions for real-time notifications';
COMMENT ON TABLE public.host_notifications IS 'In-app notifications for property hosts';
COMMENT ON TABLE public.host_settings IS 'Host preferences and automation settings';

COMMENT ON COLUMN public.webhook_subscriptions.events IS 'Array of event types: booking.created, booking.confirmed, booking.cancelled, payment.received, host.response_needed';
COMMENT ON COLUMN public.webhook_subscriptions.failed_attempts IS 'Number of consecutive failed webhook delivery attempts';
COMMENT ON COLUMN public.webhook_subscriptions.max_failed_attempts IS 'Maximum failed attempts before auto-disabling webhook';

COMMENT ON COLUMN public.host_notifications.type IS 'Notification type: new_booking, payment_received, guest_message, urgent, booking_update';
COMMENT ON COLUMN public.host_notifications.priority IS 'Notification priority: high, medium, low';
COMMENT ON COLUMN public.host_notifications.action_required IS 'Whether the notification requires host action';

COMMENT ON COLUMN public.host_settings.auto_approve_bookings IS 'Enable automatic booking approval for this host';
COMMENT ON COLUMN public.host_settings.auto_approve_amount_limit IS 'Maximum booking amount for auto-approval (AED)';
