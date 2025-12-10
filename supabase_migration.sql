-- 1. Create profiles table if it doesn't exist (or alter it)
-- Since we are moving away from Supabase Auth, we can drop the trigger if it exists, or just use this table as our source of truth.

create table if not exists public.profiles (
  id uuid primary key default gen_random_uuid(),
  email text unique not null,
  full_name text,
  password_hash text,
  google_sub text,
  avatar_url text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- 2. Add columns if table existed but was different
alter table public.profiles add column if not exists password_hash text;
alter table public.profiles add column if not exists google_sub text;
alter table public.profiles add column if not exists avatar_url text;

-- 3. Enable RLS (Optional, but good practice). 
-- However, since we are doing Custom Auth via Backend, the Backend Service Role execution bypasses RLS.
-- If we want to strictly disallow public access:
alter table public.profiles enable row level security;

-- Policy: Allow Service Role full access (implicit). 
-- Allow nothing to public/anon (except maybe read if you want, but likely not needed).
-- We can create a "block all" policy for anon to be safe.
create policy "No public access" on public.profiles
  for all
  to anon
  using (false);

-- 4. Prescriptions and Medicines tables should use the UUID from profiles (which we generate).
-- They likely reference auth.users.id. We need to drop that constraint if it exists.
-- alter table public.prescriptions drop constraint prescriptions_user_id_fkey; -- if it linked to auth.users
-- alter table public.prescriptions add constraint prescriptions_user_id_fkey foreign key (user_id) references public.profiles(id);

-- IMPORTANT: You must run this SQL in your Supabase Dashboard -> SQL Editor!
