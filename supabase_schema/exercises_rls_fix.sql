-- Fix RLS Advisory: exercises table has RLS enabled but no policies
-- This allows authenticated users to READ exercises, but only admins to modify them

-- Allow all authenticated users to read exercises
CREATE POLICY "Authenticated users can read exercises" 
ON public.exercises
FOR SELECT 
TO authenticated
USING (true);

-- Allow only admin/service role to insert/update/delete exercises
CREATE POLICY "Only admins can modify exercises" 
ON public.exercises
FOR ALL 
TO service_role
USING (true);

-- Also allow anon (public) to read exercises for login screen
CREATE POLICY "Public can read exercises" 
ON public.exercises
FOR SELECT 
TO anon
USING (true);
