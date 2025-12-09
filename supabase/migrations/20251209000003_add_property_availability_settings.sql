-- Migration: Add Property Availability Settings
-- Description: Add minimum/maximum nights and availability date range to properties

-- Add availability settings columns to properties table
ALTER TABLE public.properties 
ADD COLUMN IF NOT EXISTS minimum_nights INT NOT NULL DEFAULT 1,
ADD COLUMN IF NOT EXISTS maximum_nights INT NOT NULL DEFAULT 365,
ADD COLUMN IF NOT EXISTS available_from DATE,
ADD COLUMN IF NOT EXISTS available_to DATE,
ADD COLUMN IF NOT EXISTS check_in_time TIME DEFAULT '15:00:00',
ADD COLUMN IF NOT EXISTS check_out_time TIME DEFAULT '11:00:00';

-- Add check constraints
ALTER TABLE public.properties
ADD CONSTRAINT check_minimum_nights CHECK (minimum_nights >= 1 AND minimum_nights <= 365),
ADD CONSTRAINT check_maximum_nights CHECK (maximum_nights >= 1 AND maximum_nights <= 365),
ADD CONSTRAINT check_nights_range CHECK (minimum_nights <= maximum_nights);

-- Create index for availability queries
CREATE INDEX IF NOT EXISTS idx_properties_availability 
ON public.properties (available_from, available_to) 
WHERE status = 'active';

-- Comment on columns
COMMENT ON COLUMN public.properties.minimum_nights IS 'Minimum stay duration in nights';
COMMENT ON COLUMN public.properties.maximum_nights IS 'Maximum stay duration in nights';
COMMENT ON COLUMN public.properties.available_from IS 'Date from which property is available for booking';
COMMENT ON COLUMN public.properties.available_to IS 'Date until which property is available for booking';
COMMENT ON COLUMN public.properties.check_in_time IS 'Standard check-in time';
COMMENT ON COLUMN public.properties.check_out_time IS 'Standard check-out time';

-- Update existing properties to have sensible defaults
UPDATE public.properties 
SET 
    minimum_nights = 1,
    maximum_nights = 365,
    check_in_time = '15:00:00',
    check_out_time = '11:00:00'
WHERE minimum_nights IS NULL;

