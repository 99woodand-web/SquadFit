-- ============================================================================
-- SUPABASE SECURITY FIXES
-- Run this SQL to fix all security advisories
-- ============================================================================

-- ============================================================================
-- 1. FIX: Function Search Path Mutable (3 functions)
-- These functions need search_path set to prevent SQL injection
-- ============================================================================

-- Fix calculate_user_level function
CREATE OR REPLACE FUNCTION public.calculate_user_level(user_points INTEGER)
RETURNS TABLE(level INTEGER, rank_title TEXT)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        CASE
            WHEN user_points >= 10000 THEN 10
            WHEN user_points >= 5000 THEN 9
            WHEN user_points >= 2500 THEN 8
            WHEN user_points >= 1500 THEN 7
            WHEN user_points >= 1000 THEN 6
            WHEN user_points >= 500 THEN 5
            WHEN user_points >= 250 THEN 4
            WHEN user_points >= 100 THEN 3
            WHEN user_points >= 50 THEN 2
            ELSE 1
        END,
        CASE
            WHEN user_points >= 10000 THEN 'Legend'
            WHEN user_points >= 5000 THEN 'Champion'
            WHEN user_points >= 2500 THEN 'Elite'
            WHEN user_points >= 1500 THEN 'Warrior'
            WHEN user_points >= 1000 THEN 'Beast'
            WHEN user_points >= 500 THEN 'Strong'
            WHEN user_points >= 250 THEN 'Active'
            WHEN user_points >= 100 THEN 'Regular'
            WHEN user_points >= 50 THEN 'Starter'
            ELSE 'Newcomer'
        END;
END;
$$;

-- Fix are_friends function
CREATE OR REPLACE FUNCTION public.are_friends(user1_id UUID, user2_id UUID)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM friendships
        WHERE status = 'accepted'
        AND (
            (requester_id = user1_id AND addressee_id = user2_id)
            OR
            (requester_id = user2_id AND addressee_id = user1_id)
        )
    );
END;
$$;

-- Fix or create increment_leaderboard_score_on_workout function
CREATE OR REPLACE FUNCTION public.increment_leaderboard_score_on_workout()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    -- Update user's total workouts and points
    UPDATE user_profiles
    SET 
        total_workouts = total_workouts + 1,
        points = points + 10,  -- 10 points per workout
        level = (SELECT level FROM calculate_user_level(points + 10)),
        rank_title = (SELECT rank_title FROM calculate_user_level(points + 10)),
        updated_at = NOW()
    WHERE id = NEW.user_id;
    
    RETURN NEW;
END;
$$;

-- ============================================================================
-- 2. FIX: Move pg_trgm extension out of public schema
-- ============================================================================

-- First, check if the extension is used, then move it
-- Note: This may require recreating indexes that use pg_trgm
DO $$
BEGIN
    -- Drop from public if exists
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_trgm' AND extnamespace = 'public'::regnamespace) THEN
        -- Create in extensions schema if not exists
        CREATE SCHEMA IF NOT EXISTS extensions;
        -- Note: You may need to manually drop and recreate the extension
        -- This is a complex operation - see notes below
        RAISE NOTICE 'pg_trgm extension found in public schema. Manual intervention may be needed.';
    END IF;
END $$;

-- ============================================================================
-- 3. FIX: SECURITY DEFINER functions - Revoke public access
-- ============================================================================

-- Revoke EXECUTE from anon and authenticated for increment_leaderboard_score_on_workout
REVOKE EXECUTE ON FUNCTION public.increment_leaderboard_score_on_workout() FROM anon;
REVOKE EXECUTE ON FUNCTION public.increment_leaderboard_score_on_workout() FROM authenticated;

-- Only allow the trigger to execute this, not direct API calls
-- Revoke from public as well
REVOKE EXECUTE ON FUNCTION public.increment_leaderboard_score_on_workout() FROM public;

-- Revoke EXECUTE from anon and authenticated for rls_auto_enable
REVOKE EXECUTE ON FUNCTION public.rls_auto_enable() FROM anon;
REVOKE EXECUTE ON FUNCTION public.rls_auto_enable() FROM authenticated;
REVOKE EXECUTE ON FUNCTION public.rls_auto_enable() FROM public;

-- ============================================================================
-- 4. FIX: Enable Leaked Password Protection (must be done in Dashboard)
-- ============================================================================
-- NOTE: This cannot be done via SQL. You must:
-- 1. Go to Supabase Dashboard
-- 2. Navigate to Authentication > Providers
-- 3. Find "Email" provider
-- 4. Enable "Leaked password protection" toggle
-- 5. Save changes

-- ============================================================================
-- VERIFICATION - Run these separate queries to verify
-- ============================================================================

-- Query 1: Check functions exist
SELECT proname as function_name FROM pg_proc 
WHERE proname IN ('calculate_user_level', 'are_friends', 'increment_leaderboard_score_on_workout');

-- Query 2: Check permissions revoked
SELECT 
    has_function_privilege('anon', 'public.increment_leaderboard_score_on_workout()', 'EXECUTE') as anon_can_execute,
    has_function_privilege('authenticated', 'public.increment_leaderboard_score_on_workout()', 'EXECUTE') as auth_can_execute;

-- ============================================================================
-- SUMMARY OF FIXES
-- ============================================================================
-- 1. calculate_user_level - Added SET search_path = public
-- 2. are_friends - Added SET search_path = public  
-- 3. increment_leaderboard_score_on_workout - Added SET search_path = public
-- 4. Revoke EXECUTE from anon/authenticated for sensitive functions
-- 5. pg_trgm - Manual step needed (move to extensions schema)
-- 6. Leaked Password Protection - Enable in Dashboard manually
