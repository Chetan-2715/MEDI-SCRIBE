import { User, AuthResponse } from '../types';
import { supabase } from '../lib/supabase';

// In a real app, this would be your Node.js backend URL
const API_URL = import.meta.env.VITE_API_URL;
const MOCK_MODE = false;

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const authService = {
  async sendOtp(email: string, fullName?: string): Promise<void> {
    if (MOCK_MODE) {
      await delay(1000);
      return;
    }

    const options: any = { shouldCreateUser: true };
    if (fullName) {
      options.data = { full_name: fullName };
    }

    const { error } = await supabase.auth.signInWithOtp({
      email,
      options
    });

    if (error) {
      throw new Error(error.message);
    }
  },

  async verifyOtp(email: string, otp: string): Promise<AuthResponse> {
    if (MOCK_MODE) {
      await delay(1000);
      return {
        user: { id: 'mock-id', name: 'Mock User', email },
        token: 'mock-token'
      };
    }

    const { data, error } = await supabase.auth.verifyOtp({
      email,
      token: otp,
      type: 'email'
    });

    if (error || !data.user || !data.session) {
      throw new Error(error?.message || 'Verification failed');
    }

    // Sync profile if needed (e.g. ensure public.profiles has row)
    // We can do this silently here or rely on database triggers.
    // For now, let's just make sure we return the user.
    // If metadata name is missing, we might want to fetch from profiles table?
    // But let's stick to auth metadata as primary for now to keep it simple as requested.

    // Check if we need to sync to profiles table immediately?
    // The user requirement says "If auth.users has a new user, auto-create a row in profiles".
    // We can do this via a Postgres Trigger (best) or here.
    // Since I cannot easily edit DB triggers from here without SQL interface, I will try to upsert to profiles here.

    const user = data.user;
    const fullName = user.user_metadata?.full_name;

    if (user.email) {
      try {
        // Optimistically upsert profile to ensure it exists
        // We only update name if it's present in metadata
        const updates: any = {
          id: user.id,
          email: user.email,
          updated_at: new Date().toISOString(),
        };
        if (fullName) updates.full_name = fullName;

        await supabase.from('profiles').upsert(updates);
      } catch (err) {
        console.warn('Profile sync failed (likely RLS), proceeding with login:', err);
      }
    }

    const appUser: User = {
      id: user.id,
      email: user.email || '',
      name: fullName || '', // If empty, UI handles "Complete Profile"
    };

    return {
      user: appUser,
      token: data.session.access_token
    };
  },

  async updateProfile(userId: string, fullName: string): Promise<User> {
    // 1. Update Auth Metadata
    const { data: authData, error: authError } = await supabase.auth.updateUser({
      data: { full_name: fullName }
    });
    if (authError) throw new Error(authError.message);

    // 2. Update Public Profile
    const { error: profileError } = await supabase
      .from('profiles')
      .upsert({
        id: userId,
        full_name: fullName,
        updated_at: new Date().toISOString()
      });

    if (profileError) {
      console.warn('Failed to update profiles table (RLS), but auth metadata updated:', profileError.message);
      // We don't throw here so the user can still progress with their updated auth state
    }

    const user = authData.user;
    return {
      id: user.id,
      email: user.email || '',
      name: user.user_metadata?.full_name || fullName,
    };
  },

  async getUser(): Promise<User | null> {
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return null;

    return {
      id: user.id,
      email: user.email || '',
      name: user.user_metadata?.full_name || '',
    };
  },

  async deleteAccount(token: string): Promise<void> {
    if (MOCK_MODE) {
      return;
    }

    const response = await fetch(`${API_URL}/auth/delete`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to delete account');
    }

    // Also sign out from client side
    await supabase.auth.signOut();
  },

  async logout(): Promise<void> {
    await supabase.auth.signOut();
  }
};
