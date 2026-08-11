-- ============================================================================
-- FIX: Add INSERT policy for user_profiles table
-- Run this if you get 401 Unauthorized when creating a new account
-- ============================================================================

-- Allow users to INSERT their own profile (needed for registration)
CREATE POLICY "Users can insert own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Also allow the service role to insert (for the trigger)
-- This is already handled by SECURITY DEFINER on the trigger function

-- ============================================================================
-- VERIFICATION
-- ============================================================================
-- After running this, try registering again in the app
-- You should see "Account created!" instead of 401 error
