-- Add role column to users table for admin access control
ALTER TABLE public.users 
ADD COLUMN IF NOT EXISTS role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin', 'super_admin'));

-- Create index for role lookups
CREATE INDEX IF NOT EXISTS idx_users_role ON public.users(role);

-- Comment on column
COMMENT ON COLUMN public.users.role IS 'User role: user (default), admin, or super_admin';
