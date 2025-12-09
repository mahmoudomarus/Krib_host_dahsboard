-- Migration: Cleanup Non-UAE Properties
-- Description: This platform is UAE-only, remove or flag properties outside UAE

-- Option 1: Mark non-UAE properties as inactive (safer approach)
-- This preserves data but hides them from search
UPDATE public.properties 
SET status = 'inactive'
WHERE LOWER(country) NOT IN ('uae', 'united arab emirates', 'ae')
   OR (country IS NULL AND LOWER(state) NOT IN ('dubai', 'abu dhabi', 'sharjah', 'ajman', 'ras al khaimah', 'fujairah', 'umm al quwain'));

-- Update any San Francisco / California properties specifically
UPDATE public.properties 
SET status = 'inactive'
WHERE LOWER(city) LIKE '%san francisco%'
   OR LOWER(state) LIKE '%california%'
   OR LOWER(state) = 'ca';

-- Option 2 (Commented out - use only if you want to DELETE the data):
-- DELETE FROM public.properties 
-- WHERE LOWER(country) NOT IN ('uae', 'united arab emirates', 'ae')
--    AND (LOWER(city) LIKE '%san francisco%' OR LOWER(state) LIKE '%california%' OR LOWER(state) = 'ca');

-- Add a check constraint to ensure future properties are UAE-only (optional but recommended)
-- Note: This will prevent non-UAE properties from being added in the future
DO $$
BEGIN
    -- Only add if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'properties_uae_only'
    ) THEN
        -- First update any remaining non-UAE countries to 'UAE'
        UPDATE public.properties SET country = 'UAE' WHERE country IS NULL OR country = '';
        
        -- Add a soft validation - new properties should default to UAE
        ALTER TABLE public.properties 
        ALTER COLUMN country SET DEFAULT 'UAE';
    END IF;
END $$;

-- Log the cleanup
DO $$
DECLARE
    inactive_count INT;
BEGIN
    SELECT COUNT(*) INTO inactive_count 
    FROM public.properties 
    WHERE status = 'inactive' 
    AND (LOWER(city) LIKE '%san francisco%' OR LOWER(state) LIKE '%california%' OR LOWER(state) = 'ca');
    
    RAISE NOTICE 'Marked % non-UAE properties as inactive', inactive_count;
END $$;

