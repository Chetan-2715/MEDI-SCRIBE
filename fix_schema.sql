-- 1. Remove the foreign key constraint that binds profiles to Supabase Auth
-- This allows us to create users in 'profiles' that don't exist in 'auth.users'
ALTER TABLE public.profiles 
DROP CONSTRAINT IF EXISTS profiles_id_fkey;

-- 2. Add the password_hash column for storing bcrypt hashes
ALTER TABLE public.profiles 
ADD COLUMN IF NOT EXISTS password_hash TEXT;

-- 3. Add google_sub column to store unique Google User IDs
ALTER TABLE public.profiles 
ADD COLUMN IF NOT EXISTS google_sub TEXT;

-- 4. Add avatar_url if it doesn't strictly exist (it was in your schema, but good to ensure)
ALTER TABLE public.profiles 
ADD COLUMN IF NOT EXISTS avatar_url TEXT;

-- 5. Create an index on email for faster login lookups
CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles(email);

-- NOTE:
-- Since you are now using Custom Auth, the RLS policies based on `auth.uid()` 
-- (like "Users can view own profile") will NO LONGER WORK for these new users.
-- You must ensure your Backend connects using the 'SERVICE_ROLE_KEY' 
-- (SUPABASE_KEY in backend .env) to bypass these RLS policies.
