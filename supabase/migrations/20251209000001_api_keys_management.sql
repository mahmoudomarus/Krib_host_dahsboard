-- API Keys Management System
-- Stores hashed API keys for external platform integrations
-- Similar to how OpenAI manages their API keys

-- Create api_keys table
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Key identification (prefix is visible, hash is for validation)
    key_prefix VARCHAR(12) NOT NULL,  -- First 12 chars shown to user (e.g., "krib_prod_a1b2")
    key_hash VARCHAR(64) NOT NULL UNIQUE,  -- SHA-256 hash of full key
    
    -- Service/Platform information
    name VARCHAR(100) NOT NULL,  -- Display name (e.g., "Krib AI Agent Production")
    description TEXT,  -- Optional description
    
    -- Permissions
    permissions TEXT[] NOT NULL DEFAULT '{}',  -- Array of permission strings
    tier VARCHAR(20) NOT NULL DEFAULT 'standard',  -- read_only, standard, full_access
    
    -- Rate limiting
    rate_limit_per_minute INTEGER NOT NULL DEFAULT 100,
    
    -- Ownership (which admin created this key)
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Status
    is_active BOOLEAN NOT NULL DEFAULT true,
    
    -- Usage tracking
    last_used_at TIMESTAMP WITH TIME ZONE,
    total_requests BIGINT NOT NULL DEFAULT 0,
    
    -- Expiration (optional)
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    revoked_at TIMESTAMP WITH TIME ZONE
);

-- Create index for fast key lookup by hash
CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_api_keys_prefix ON api_keys(key_prefix);
CREATE INDEX IF NOT EXISTS idx_api_keys_active ON api_keys(is_active) WHERE is_active = true;

-- API key usage logs for analytics and debugging
CREATE TABLE IF NOT EXISTS api_key_usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_key_id UUID REFERENCES api_keys(id) ON DELETE CASCADE,
    
    -- Request details
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    response_time_ms INTEGER,
    
    -- Client info
    ip_address INET,
    user_agent TEXT,
    
    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for usage analytics
CREATE INDEX IF NOT EXISTS idx_api_key_usage_key_id ON api_key_usage_logs(api_key_id);
CREATE INDEX IF NOT EXISTS idx_api_key_usage_created ON api_key_usage_logs(created_at);

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_api_keys_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at
DROP TRIGGER IF EXISTS trigger_api_keys_updated_at ON api_keys;
CREATE TRIGGER trigger_api_keys_updated_at
    BEFORE UPDATE ON api_keys
    FOR EACH ROW
    EXECUTE FUNCTION update_api_keys_updated_at();

-- Function to increment usage counter
CREATE OR REPLACE FUNCTION increment_api_key_usage(p_key_hash VARCHAR)
RETURNS VOID AS $$
BEGIN
    UPDATE api_keys 
    SET 
        total_requests = total_requests + 1,
        last_used_at = NOW()
    WHERE key_hash = p_key_hash AND is_active = true;
END;
$$ LANGUAGE plpgsql;

-- RLS Policies (only admins can manage API keys)
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_key_usage_logs ENABLE ROW LEVEL SECURITY;

-- Policy: Only service role can read/write api_keys (backend only)
CREATE POLICY "Service role full access to api_keys"
    ON api_keys
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role full access to api_key_usage_logs"
    ON api_key_usage_logs
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Comments for documentation
COMMENT ON TABLE api_keys IS 'Stores hashed API keys for external platform integrations. Keys are never stored in plaintext.';
COMMENT ON COLUMN api_keys.key_prefix IS 'First 12 characters of the key shown to users for identification';
COMMENT ON COLUMN api_keys.key_hash IS 'SHA-256 hash of the full API key for validation';
COMMENT ON COLUMN api_keys.permissions IS 'Array of permission strings this key has access to';
COMMENT ON COLUMN api_keys.tier IS 'Permission tier: read_only, standard, full_access';

