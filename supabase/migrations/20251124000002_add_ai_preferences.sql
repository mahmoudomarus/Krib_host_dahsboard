-- Add AI preferences for hosts to control what AI can share

-- Add AI preferences to host_settings table
ALTER TABLE public.host_settings
ADD COLUMN IF NOT EXISTS ai_enabled BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS ai_can_share_pricing BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS ai_can_share_availability BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS ai_can_share_phone BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS ai_can_share_address BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS ai_custom_instructions TEXT,
ADD COLUMN IF NOT EXISTS ai_response_tone TEXT DEFAULT 'professional' CHECK (ai_response_tone IN ('professional', 'friendly', 'casual', 'formal'));

-- Add AI settings to properties for property-specific control
ALTER TABLE public.properties
ADD COLUMN IF NOT EXISTS ai_enabled BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS check_in_instructions TEXT,
ADD COLUMN IF NOT EXISTS parking_details TEXT,
ADD COLUMN IF NOT EXISTS wifi_details TEXT,
ADD COLUMN IF NOT EXISTS special_instructions TEXT;

COMMENT ON COLUMN public.host_settings.ai_enabled IS 'Enable/disable AI responses for all properties';
COMMENT ON COLUMN public.host_settings.ai_can_share_pricing IS 'Allow AI to discuss pricing details';
COMMENT ON COLUMN public.host_settings.ai_can_share_availability IS 'Allow AI to check and share availability';
COMMENT ON COLUMN public.host_settings.ai_can_share_phone IS 'Allow AI to share host phone number';
COMMENT ON COLUMN public.host_settings.ai_can_share_address IS 'Allow AI to share full property address';
COMMENT ON COLUMN public.host_settings.ai_custom_instructions IS 'Custom instructions for AI responses';
COMMENT ON COLUMN public.host_settings.ai_response_tone IS 'Tone of AI responses (professional, friendly, casual, formal)';

COMMENT ON COLUMN public.properties.check_in_instructions IS 'Detailed check-in instructions for guests';
COMMENT ON COLUMN public.properties.parking_details IS 'Parking information (location, cost, restrictions)';
COMMENT ON COLUMN public.properties.wifi_details IS 'WiFi network name and password';
COMMENT ON COLUMN public.properties.special_instructions IS 'Any special instructions for this property';

