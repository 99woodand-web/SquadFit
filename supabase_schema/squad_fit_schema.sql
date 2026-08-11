-- ============================================================================
-- SQUAD FIT - Complete Supabase SQL Schema
-- Social Gym Platform with User Accounts, Friend Actions & Leaderboard Points
-- ============================================================================
-- NOTE: This script uses IF NOT EXISTS / OR REPLACE to safely run multiple times
-- ============================================================================

-- ============================================================================
-- 1. ENABLE REQUIRED EXTENSIONS
-- ============================================================================
-- UUID generation for primary keys
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- For full-text search (optional, for exercise search)
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================================
-- 2. USER PROFILES TABLE
-- Extended profile data linked to Supabase Auth users
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    username TEXT UNIQUE NOT NULL,
    display_name TEXT,
    avatar_url TEXT,
    bio TEXT DEFAULT '',
    
    -- Biometric Data
    weight_kg NUMERIC(5,1) DEFAULT 75.0,
    height_cm NUMERIC(5,1) DEFAULT 175.0,
    age INTEGER DEFAULT 25,
    gender TEXT CHECK (gender IN ('male', 'female', 'other', 'prefer_not_to_say')),
    
    -- Training Configuration
    training_environment TEXT CHECK (training_environment IN ('commercial_gym', 'home_gym', 'cardio_only')) DEFAULT 'commercial_gym',
    experience_level TEXT CHECK (experience_level IN ('beginner', 'regular', 'athlete')) DEFAULT 'regular',
    fitness_goal TEXT CHECK (fitness_goal IN ('build_muscle', 'get_stronger', 'lose_weight', 'run_faster', 'cycle_more', 'general_fitness')) DEFAULT 'general_fitness',
    days_per_week INTEGER DEFAULT 4 CHECK (days_per_week BETWEEN 1 AND 7),
    
    -- Equipment Ownership (for home gym users)
    has_barbell BOOLEAN DEFAULT FALSE,
    has_dumbbells BOOLEAN DEFAULT FALSE,
    has_bench BOOLEAN DEFAULT FALSE,
    has_pull_up_bar BOOLEAN DEFAULT FALSE,
    has_ab_roller BOOLEAN DEFAULT FALSE,
    has_resistance_bands BOOLEAN DEFAULT FALSE,
    has_cables BOOLEAN DEFAULT FALSE,
    has_machine BOOLEAN DEFAULT FALSE,
    
    -- Calculated Metrics (updated by triggers or app)
    bmi NUMERIC(4,1),
    bmr NUMERIC(5,0),
    tdee NUMERIC(5,0),
    
    -- Social Stats
    total_workouts INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    total_volume_kg NUMERIC(10,1) DEFAULT 0,
    
    -- Leaderboard Points
    points INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    rank_title TEXT DEFAULT 'Newcomer',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Auto-create profile on user signup
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO user_profiles (id, username, display_name)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'username', split_part(NEW.email, '@', 1)),
        COALESCE(NEW.raw_user_meta_data->>'display_name', split_part(NEW.email, '@', 1))
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION handle_new_user();

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_profiles;
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================================================
-- 3. FRIENDSHIPS TABLE
-- Manages friend connections between users
-- ============================================================================
CREATE TABLE IF NOT EXISTS friendships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    requester_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    addressee_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    status TEXT CHECK (status IN ('pending', 'accepted', 'blocked')) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Prevent self-friendship and duplicate requests
    CONSTRAINT no_self_friendship CHECK (requester_id != addressee_id),
    CONSTRAINT unique_friendship UNIQUE (requester_id, addressee_id)
);

-- Index for fast friend lookups
CREATE INDEX IF NOT EXISTS idx_friendships_requester ON friendships(requester_id);
CREATE INDEX IF NOT EXISTS idx_friendships_addressee ON friendships(addressee_id);
CREATE INDEX IF NOT EXISTS idx_friendships_status ON friendships(status);

-- ============================================================================
-- 4. EXERCISES TABLE
-- Complete exercise library with equipment tags
-- ============================================================================
CREATE TABLE IF NOT EXISTS exercises (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    exercise_code TEXT UNIQUE NOT NULL,  -- e.g., 'g1', 'h5', 'c1'
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    muscle TEXT NOT NULL,
    equipment TEXT NOT NULL,
    track_type TEXT CHECK (track_type IN ('strength', 'cardio')) NOT NULL,
    
    -- Equipment requirements
    equipment_tags TEXT[] DEFAULT '{}',
    
    -- Default values
    default_sets INTEGER DEFAULT 3,
    default_reps INTEGER DEFAULT 10,
    is_compound BOOLEAN DEFAULT FALSE,
    
    -- Form tips and alternatives
    tip TEXT DEFAULT '',
    alternatives TEXT[] DEFAULT '{}',
    
    -- Stats tracking
    total_performed INTEGER DEFAULT 0,
    avg_weight_kg NUMERIC(5,1) DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for filtering by category/muscle
CREATE INDEX IF NOT EXISTS idx_exercises_category ON exercises(category);
CREATE INDEX IF NOT EXISTS idx_exercises_muscle ON exercises(muscle);
CREATE INDEX IF NOT EXISTS idx_exercises_track ON exercises(track_type);

-- ============================================================================
-- 5. WORKOUT SESSIONS TABLE
-- Records complete workout sessions
-- ============================================================================
CREATE TABLE IF NOT EXISTS workout_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    
    -- Session Details
    session_date DATE NOT NULL DEFAULT CURRENT_DATE,
    day_of_week TEXT CHECK (day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),
    focus TEXT,  -- e.g., 'Push Day', 'Leg Day'
    
    -- Session Stats
    duration_minutes INTEGER DEFAULT 0,
    total_volume_kg NUMERIC(10,1) DEFAULT 0,
    total_sets INTEGER DEFAULT 0,
    total_reps INTEGER DEFAULT 0,
    avg_rpe NUMERIC(3,1) DEFAULT 0,
    
    -- Completion Status
    status TEXT CHECK (status IN ('planned', 'in_progress', 'completed', 'skipped')) DEFAULT 'planned',
    completion_pct NUMERIC(5,2) DEFAULT 0,
    
    -- Social
    is_public BOOLEAN DEFAULT TRUE,
    notes TEXT DEFAULT '',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Index for date-based queries
CREATE INDEX IF NOT EXISTS idx_sessions_user_date ON workout_sessions(user_id, session_date DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON workout_sessions(status);

-- ============================================================================
-- 6. WORKOUT SETS TABLE (Dual-Track: Strength + Cardio)
-- Individual set/log entries within a session
-- ============================================================================
CREATE TABLE IF NOT EXISTS workout_sets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES workout_sessions(id) ON DELETE CASCADE,
    exercise_id UUID NOT NULL REFERENCES exercises(id) ON DELETE CASCADE,
    
    -- Set Position
    set_number INTEGER NOT NULL DEFAULT 1,
    
    -- Strength Track Fields
    weight_kg NUMERIC(6,2),
    reps INTEGER,
    rpe NUMERIC(3,1),  -- Rate of Perceived Exertion (1-10)
    
    -- Cardio Track Fields
    duration_seconds INTEGER,
    distance_km NUMERIC(6,2),
    pace_per_km TEXT,  -- e.g., "5:30"
    cadence_rpm INTEGER,
    heart_rate_avg INTEGER,
    
    -- Common Fields
    is_warmup BOOLEAN DEFAULT FALSE,
    is_drop_set BOOLEAN DEFAULT FALSE,
    is_failure BOOLEAN DEFAULT FALSE,
    is_pr BOOLEAN DEFAULT FALSE,  -- Personal Record flag
    
    -- Volume Calculated
    volume_kg NUMERIC(10,2) GENERATED ALWAYS AS (
        CASE 
            WHEN weight_kg IS NOT NULL AND reps IS NOT NULL 
            THEN weight_kg * reps 
            ELSE NULL 
        END
    ) STORED,
    
    notes TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for exercise history queries
CREATE INDEX IF NOT EXISTS idx_sets_session ON workout_sets(session_id);
CREATE INDEX IF NOT EXISTS idx_sets_exercise ON workout_sets(exercise_id);
CREATE INDEX IF NOT EXISTS idx_sets_pr ON workout_sets(is_pr) WHERE is_pr = TRUE;

-- ============================================================================
-- 7. PERSONAL RECORDS TABLE
-- Tracks all-time bests for each exercise
-- ============================================================================
CREATE TABLE IF NOT EXISTS personal_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    exercise_id UUID NOT NULL REFERENCES exercises(id) ON DELETE CASCADE,
    
    -- Record Types
    record_type TEXT CHECK (record_type IN ('max_weight', 'max_volume', 'max_reps', 'best_time', 'longest_distance')) NOT NULL,
    
    -- Record Values
    value NUMERIC(10,2) NOT NULL,
    unit TEXT NOT NULL,  -- 'kg', 'reps', 'km', 'seconds'
    
    -- Context
    session_id UUID REFERENCES workout_sessions(id),
    set_id UUID REFERENCES workout_sets(id),
    achieved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- One record per type per exercise
    CONSTRAINT unique_pr UNIQUE (user_id, exercise_id, record_type)
);

-- Index for PR lookups
CREATE INDEX IF NOT EXISTS idx_prs_user ON personal_records(user_id);
CREATE INDEX IF NOT EXISTS idx_prs_exercise ON personal_records(exercise_id);

-- ============================================================================
-- 8. SOCIAL FEED TABLE
-- Posts and activity updates visible to friends
-- ============================================================================
CREATE TABLE IF NOT EXISTS social_feed (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    
    -- Post Content
    post_type TEXT CHECK (post_type IN ('workout_complete', 'pr_achieved', 'milestone', 'challenge', 'custom')) NOT NULL,
    content TEXT,
    
    -- Linked Data
    session_id UUID REFERENCES workout_sessions(id),
    exercise_id UUID REFERENCES exercises(id),
    pr_id UUID REFERENCES personal_records(id),
    
    -- Metrics for display
    metrics JSONB DEFAULT '{}',  -- Flexible data for different post types
    
    -- Visibility
    visibility TEXT CHECK (visibility IN ('friends', 'public', 'private')) DEFAULT 'friends',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for feed queries
CREATE INDEX IF NOT EXISTS idx_feed_user ON social_feed(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_feed_type ON social_feed(post_type);
CREATE INDEX IF NOT EXISTS idx_feed_visibility ON social_feed(visibility);

-- ============================================================================
-- 9. LIKES TABLE
-- Social interactions on feed posts
-- ============================================================================
CREATE TABLE IF NOT EXISTS likes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    post_id UUID NOT NULL REFERENCES social_feed(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- One like per user per post
    CONSTRAINT unique_like UNIQUE (user_id, post_id)
);

-- Index for like counts
CREATE INDEX IF NOT EXISTS idx_likes_post ON likes(post_id);

-- ============================================================================
-- 10. COMMENTS TABLE
-- Social comments on feed posts
-- ============================================================================
CREATE TABLE IF NOT EXISTS comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    post_id UUID NOT NULL REFERENCES social_feed(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES comments(id) ON DELETE CASCADE,  -- For nested replies
    
    content TEXT NOT NULL,
    is_edited BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for comment threads
CREATE INDEX IF NOT EXISTS idx_comments_post ON comments(post_id, created_at);
CREATE INDEX IF NOT EXISTS idx_comments_parent ON comments(parent_id);

-- ============================================================================
-- 11. CHALLENGES TABLE
-- Weekly/monthly challenges for friends
-- ============================================================================
CREATE TABLE IF NOT EXISTS challenges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    creator_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    
    -- Challenge Details
    title TEXT NOT NULL,
    description TEXT,
    challenge_type TEXT CHECK (challenge_type IN ('total_volume', 'workout_count', 'pr_count', 'consistency', 'custom')) NOT NULL,
    
    -- Targets
    target_value NUMERIC(10,2),
    target_unit TEXT,
    
    -- Timeframe
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    
    -- Status
    status TEXT CHECK (status IN ('upcoming', 'active', 'completed')) DEFAULT 'upcoming',
    is_public BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- 12. CHALLENGE PARTICIPANTS TABLE
-- Users participating in challenges
-- ============================================================================
CREATE TABLE IF NOT EXISTS challenge_participants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    challenge_id UUID NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    
    -- Progress
    current_value NUMERIC(10,2) DEFAULT 0,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_participant UNIQUE (challenge_id, user_id)
);

-- ============================================================================
-- 13. LEADERBOARD TABLE (Materialized View for Performance)
-- ============================================================================
DROP MATERIALIZED VIEW IF EXISTS leaderboard_weekly;
CREATE MATERIALIZED VIEW leaderboard_weekly AS
SELECT 
    up.id as user_id,
    up.username,
    up.display_name,
    up.avatar_url,
    up.level,
    up.rank_title,
    COUNT(DISTINCT ws.id) as workouts_this_week,
    COALESCE(SUM(ws.total_volume_kg), 0) as total_volume,
    COALESCE(SUM(ws.total_sets), 0) as total_sets,
    COUNT(DISTINCT pr.id) as prs_this_week,
    -- Points calculation: 10 per workout + 1 per 100kg volume + 50 per PR
    (COUNT(DISTINCT ws.id) * 10 + 
     COALESCE(SUM(ws.total_volume_kg), 0) / 100 + 
     COUNT(DISTINCT pr.id) * 50)::INTEGER as weekly_points
FROM user_profiles up
LEFT JOIN workout_sessions ws ON up.id = ws.user_id 
    AND ws.session_date >= DATE_TRUNC('week', CURRENT_DATE)
    AND ws.status = 'completed'
LEFT JOIN personal_records pr ON up.id = pr.user_id
    AND pr.achieved_at >= DATE_TRUNC('week', CURRENT_DATE)
GROUP BY up.id, up.username, up.display_name, up.avatar_url, up.level, up.rank_title
ORDER BY weekly_points DESC;

-- Refresh leaderboard periodically (run daily via cron or pg_cron)
-- REFRESH MATERIALIZED VIEW CONCURRENTLY leaderboard_weekly;

-- ============================================================================
-- 14. CALENDAR EVENTS TABLE
-- Workout scheduling and planning
-- ============================================================================
CREATE TABLE IF NOT EXISTS calendar_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    
    -- Event Details
    event_date DATE NOT NULL,
    day_of_week TEXT GENERATED ALWAYS AS (
        TO_CHAR(event_date, 'Day')
    ) STORED,
    
    -- Workout Plan
    focus TEXT,  -- e.g., 'Push Day', 'Rest Day'
    planned_exercises JSONB DEFAULT '[]',  -- Array of exercise IDs
    is_completed BOOLEAN DEFAULT FALSE,
    
    -- Rescheduling
    original_date DATE,  -- If moved from another day
    was_rescheduled BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- One event per user per date
    CONSTRAINT unique_user_event UNIQUE (user_id, event_date)
);

-- Index for calendar queries
CREATE INDEX IF NOT EXISTS idx_calendar_user_date ON calendar_events(user_id, event_date);

-- ============================================================================
-- 15. BODY MEASUREMENTS TABLE
-- Track progress photos and measurements
-- ============================================================================
CREATE TABLE IF NOT EXISTS body_measurements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    
    -- Measurements
    weight_kg NUMERIC(5,1),
    body_fat_pct NUMERIC(4,1),
    chest_cm NUMERIC(5,1),
    waist_cm NUMERIC(5,1),
    hips_cm NUMERIC(5,1),
    bicep_left_cm NUMERIC(4,1),
    bicep_right_cm NUMERIC(4,1),
    thigh_left_cm NUMERIC(4,1),
    thigh_right_cm NUMERIC(4,1),
    
    -- Progress Photos (Supabase Storage URLs)
    photo_front_url TEXT,
    photo_side_url TEXT,
    photo_back_url TEXT,
    
    -- Notes
    notes TEXT DEFAULT '',
    
    measured_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for measurement history
CREATE INDEX IF NOT EXISTS idx_measurements_user ON body_measurements(user_id, measured_at DESC);

-- ============================================================================
-- 16. NOTIFICATIONS TABLE
-- In-app notifications for social interactions
-- ============================================================================
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    
    -- Notification Content
    notification_type TEXT CHECK (notification_type IN ('friend_request', 'friend_accept', 'like', 'comment', 'pr_celebration', 'challenge_invite', 'workout_reminder')) NOT NULL,
    title TEXT NOT NULL,
    message TEXT,
    
    -- Reference Data
    from_user_id UUID REFERENCES user_profiles(id),
    post_id UUID REFERENCES social_feed(id),
    challenge_id UUID REFERENCES challenges(id),
    
    -- Status
    is_read BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for unread notifications
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, is_read, created_at DESC);

-- ============================================================================
-- 17. ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE friendships ENABLE ROW LEVEL SECURITY;
ALTER TABLE workout_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE workout_sets ENABLE ROW LEVEL SECURITY;
ALTER TABLE personal_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE social_feed ENABLE ROW LEVEL SECURITY;
ALTER TABLE likes ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE challenges ENABLE ROW LEVEL SECURITY;
ALTER TABLE challenge_participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE calendar_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE body_measurements ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- User Profiles: Users can read public profiles, update only their own
CREATE POLICY "Public profiles are viewable by everyone" ON user_profiles
    FOR SELECT USING (true);

CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = id);

-- Friendships: Users can see their own friendships
CREATE POLICY "Users can view own friendships" ON friendships
    FOR SELECT USING (auth.uid() = requester_id OR auth.uid() = addressee_id);

CREATE POLICY "Users can create friend requests" ON friendships
    FOR INSERT WITH CHECK (auth.uid() = requester_id);

CREATE POLICY "Users can update own friendships" ON friendships
    FOR UPDATE USING (auth.uid() = requester_id OR auth.uid() = addressee_id);

-- Workout Sessions: Users can see own + friends' public sessions
CREATE POLICY "Users can view own sessions" ON workout_sessions
    FOR SELECT USING (
        auth.uid() = user_id OR 
        (is_public = true AND user_id IN (
            SELECT addressee_id FROM friendships WHERE requester_id = auth.uid() AND status = 'accepted'
            UNION
            SELECT requester_id FROM friendships WHERE addressee_id = auth.uid() AND status = 'accepted'
        ))
    );

CREATE POLICY "Users can manage own sessions" ON workout_sessions
    FOR ALL USING (auth.uid() = user_id);

-- Workout Sets: Linked to session permissions
CREATE POLICY "Users can view sets for accessible sessions" ON workout_sets
    FOR SELECT USING (
        session_id IN (
            SELECT id FROM workout_sessions WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can manage own sets" ON workout_sets
    FOR ALL USING (
        session_id IN (
            SELECT id FROM workout_sessions WHERE user_id = auth.uid()
        )
    );

-- Personal Records: Public to friends
CREATE POLICY "Users can view own and friends' PRs" ON personal_records
    FOR SELECT USING (
        auth.uid() = user_id OR
        user_id IN (
            SELECT addressee_id FROM friendships WHERE requester_id = auth.uid() AND status = 'accepted'
            UNION
            SELECT requester_id FROM friendships WHERE addressee_id = auth.uid() AND status = 'accepted'
        )
    );

CREATE POLICY "Users can manage own PRs" ON personal_records
    FOR ALL USING (auth.uid() = user_id);

-- Social Feed: Based on visibility settings
CREATE POLICY "Users can view feed based on visibility" ON social_feed
    FOR SELECT USING (
        user_id = auth.uid() OR
        (visibility = 'public') OR
        (visibility = 'friends' AND user_id IN (
            SELECT addressee_id FROM friendships WHERE requester_id = auth.uid() AND status = 'accepted'
            UNION
            SELECT requester_id FROM friendships WHERE addressee_id = auth.uid() AND status = 'accepted'
        ))
    );

CREATE POLICY "Users can manage own posts" ON social_feed
    FOR ALL USING (auth.uid() = user_id);

-- Likes: Users can see likes on accessible posts
CREATE POLICY "Users can view likes" ON likes
    FOR SELECT USING (true);

CREATE POLICY "Users can manage own likes" ON likes
    FOR ALL USING (auth.uid() = user_id);

-- Comments: Users can see comments on accessible posts
CREATE POLICY "Users can view comments" ON comments
    FOR SELECT USING (true);

CREATE POLICY "Users can manage own comments" ON comments
    FOR ALL USING (auth.uid() = user_id);

-- Challenges: Public by default
CREATE POLICY "Users can view challenges" ON challenges
    FOR SELECT USING (is_public = true OR creator_id = auth.uid());

CREATE POLICY "Users can create challenges" ON challenges
    FOR INSERT WITH CHECK (auth.uid() = creator_id);

-- Challenge Participants: Users can see participants in their challenges
CREATE POLICY "Users can view challenge participants" ON challenge_participants
    FOR SELECT USING (true);

CREATE POLICY "Users can join challenges" ON challenge_participants
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own progress" ON challenge_participants
    FOR UPDATE USING (auth.uid() = user_id);

-- Calendar Events: Private to user
CREATE POLICY "Users can manage own calendar" ON calendar_events
    FOR ALL USING (auth.uid() = user_id);

-- Body Measurements: Private to user
CREATE POLICY "Users can manage own measurements" ON body_measurements
    FOR ALL USING (auth.uid() = user_id);

-- Notifications: Private to user
CREATE POLICY "Users can view own notifications" ON notifications
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "System can create notifications" ON notifications
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can update own notifications" ON notifications
    FOR UPDATE USING (auth.uid() = user_id);

-- ============================================================================
-- 18. HELPER FUNCTIONS
-- ============================================================================

-- Function to calculate and update user level based on points
CREATE OR REPLACE FUNCTION calculate_user_level(user_points INTEGER)
RETURNS TABLE(level INTEGER, rank_title TEXT) AS $$
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
$$ LANGUAGE plpgsql;

-- Function to check if users are friends
CREATE OR REPLACE FUNCTION are_friends(user1_id UUID, user2_id UUID)
RETURNS BOOLEAN AS $$
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
$$ LANGUAGE plpgsql;

-- Function to get mutual friends count
CREATE OR REPLACE FUNCTION mutual_friends_count(user1_id UUID, user2_id UUID)
RETURNS INTEGER AS $$
BEGIN
    RETURN (
        SELECT COUNT(DISTINCT friend_id)
        FROM (
            SELECT addressee_id as friend_id FROM friendships WHERE requester_id = user1_id AND status = 'accepted'
            UNION
            SELECT requester_id as friend_id FROM friendships WHERE addressee_id = user1_id AND status = 'accepted'
        ) user1_friends
        WHERE friend_id IN (
            SELECT addressee_id FROM friendships WHERE requester_id = user2_id AND status = 'accepted'
            UNION
            SELECT requester_id FROM friendships WHERE addressee_id = user2_id AND status = 'accepted'
        )
    );
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 19. SEED DATA - Sample Exercises
-- ============================================================================

-- Strength Exercises
INSERT INTO exercises (exercise_code, name, category, muscle, equipment, track_type, equipment_tags, default_sets, default_reps, is_compound, tip, alternatives) VALUES
-- Barbell
('g1', 'Flat Bench Press', 'Chest', 'Chest', 'Barbell', 'strength', ARRAY['barbell', 'bench'], 4, 10, true, 'Keep shoulder blades squeezed, feet flat on floor', ARRAY['h1', 'h2', 'g3']),
('g2', 'Incline Bench Press', 'Chest', 'Chest', 'Barbell', 'strength', ARRAY['barbell', 'bench'], 3, 10, true, 'Set bench 30-45 degrees', ARRAY['h2', 'g3']),
('g5', 'Conventional Deadlift', 'Back', 'Back', 'Barbell', 'strength', ARRAY['barbell'], 4, 5, true, 'Brace core, drive through heels', ARRAY['h5', 'h6', 'g6']),
('g9', 'Barbell Back Squat', 'Legs', 'Legs', 'Barbell', 'strength', ARRAY['barbell'], 4, 8, true, 'Break at hips, knees track toes', ARRAY['h9', 'h10', 'g10']),
('g13', 'Military Press', 'Shoulders', 'Shoulders', 'Barbell', 'strength', ARRAY['barbell'], 3, 10, true, 'Brace core, press straight up', ARRAY['h13', 'h14', 'g14']),
('g20', 'Romanian Deadlift', 'Legs', 'Legs', 'Barbell', 'strength', ARRAY['barbell'], 3, 10, true, 'Hinge at hips, feel hamstring stretch', ARRAY['h11', 'g11']),
('g21', 'Barbell Bent-Over Row', 'Back', 'Back', 'Barbell', 'strength', ARRAY['barbell'], 3, 10, true, 'Hinge forward 45 degrees, pull to lower chest', ARRAY['h6', 'h7', 'g7']),

-- Dumbbell
('g8', 'Dumbbell Curl', 'Arms', 'Biceps', 'Dumbbells', 'strength', ARRAY['dumbbells'], 3, 12, false, 'No swinging, full ROM', ARRAY['h8']),
('g14', 'Lateral Raise', 'Shoulders', 'Shoulders', 'Dumbbells', 'strength', ARRAY['dumbbells'], 3, 15, false, 'Raise to shoulder height', ARRAY['h14']),
('g23', 'Dumbbell Seated Shoulder Press', 'Shoulders', 'Shoulders', 'Dumbbells', 'strength', ARRAY['dumbbells', 'bench'], 3, 10, true, 'Sit upright, press overhead', ARRAY['h13', 'g13']),
('g25', 'Dumbbell Bulgarian Split Squat', 'Legs', 'Legs', 'Dumbbells', 'strength', ARRAY['dumbbells', 'bench'], 3, 10, true, 'Rear foot elevated, lunge deep', ARRAY['h10', 'g9']),

-- Bodyweight
('h1', 'Push-Up', 'Chest', 'Chest', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 15, false, 'Full range, core tight', ARRAY['h2', 'g1']),
('h5', 'Pull-Up', 'Back', 'Back', 'Bodyweight', 'strength', ARRAY['pull_up_bar'], 3, 8, true, 'Full dead hang, pull to chin', ARRAY['h6', 'g5']),
('h9', 'Goblet Squat', 'Legs', 'Legs', 'Dumbbells', 'strength', ARRAY['dumbbells'], 3, 12, false, 'Hold weight at chest', ARRAY['h10', 'g9']),
('h10', 'Walking Lunge', 'Legs', 'Legs', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 20, false, '90-degree knee bend', ARRAY['h9', 'g9']),
('h13', 'Pike Push-Up', 'Shoulders', 'Shoulders', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 10, false, 'Hips high, press up', ARRAY['g13']),
('h16', 'Crunch', 'Core', 'Core', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 20, false, 'Lower back stays down', ARRAY[]::text[]),
('h21', 'Kneeling Ab Roller Rollout', 'Core', 'Core', 'Ab Roller', 'strength', ARRAY['ab_roller'], 3, 10, false, 'Keep core tight, don''t arch back', ARRAY['h16']),

-- Cardio
('c1', 'Outdoor Run', 'Cardio', 'Cardio', 'Bodyweight', 'cardio', ARRAY[]::text[], 1, 1, false, 'Start easy, build pace gradually', ARRAY['c2', 'c3']),
('c2', 'Treadmill Run', 'Cardio', 'Cardio', 'Treadmill', 'cardio', ARRAY['treadmill'], 1, 1, false, 'Use incline for hill simulation', ARRAY['c1', 'c3']),
('c3', 'Interval Sprints', 'Cardio', 'Cardio', 'Bodyweight', 'cardio', ARRAY[]::text[], 8, 1, false, 'All-out effort on work intervals', ARRAY['c1', 'c4']),
('c11', 'Road Cycling', 'Cardio', 'Cardio', 'Bike', 'cardio', ARRAY['bike'], 1, 1, false, 'Maintain steady cadence 80-100 RPM', ARRAY['c12', 'c13']),
('c12', 'Stationary Bike', 'Cardio', 'Cardio', 'Bike', 'cardio', ARRAY['bike'], 1, 1, false, 'Adjust resistance for intervals', ARRAY['c11', 'c13']),
('c17', 'Jump Rope', 'Cardio', 'Cardio', 'Bodyweight', 'cardio', ARRAY[]::text[], 5, 1, false, 'Stay on balls of feet, keep elbows in', ARRAY['c3']),
('c18', 'Burpees', 'Cardio', 'Cardio', 'Bodyweight', 'cardio', ARRAY[]::text[], 5, 15, false, 'Explosive movement, full extension', ARRAY['c3', 'c7'])
ON CONFLICT (exercise_code) DO NOTHING;

-- ============================================================================
-- 20. VIEWS FOR EASY QUERIES
-- ============================================================================

-- View: User's weekly stats
DROP VIEW IF EXISTS user_weekly_stats;
CREATE VIEW user_weekly_stats AS
SELECT 
    ws.user_id,
    DATE_TRUNC('week', ws.session_date) as week_start,
    COUNT(DISTINCT ws.id) as workouts,
    SUM(ws.total_volume_kg) as total_volume,
    SUM(ws.total_sets) as total_sets,
    SUM(ws.total_reps) as total_reps,
    AVG(ws.avg_rpe) as avg_rpe
FROM workout_sessions ws
WHERE ws.status = 'completed'
GROUP BY ws.user_id, DATE_TRUNC('week', ws.session_date);

-- View: Friend activity feed
DROP VIEW IF EXISTS friend_feed;
CREATE VIEW friend_feed AS
SELECT 
    sf.*,
    up.username,
    up.display_name,
    up.avatar_url,
    (SELECT COUNT(*) FROM likes l WHERE l.post_id = sf.id) as like_count,
    (SELECT COUNT(*) FROM comments c WHERE c.post_id = sf.id) as comment_count
FROM social_feed sf
JOIN user_profiles up ON sf.user_id = up.id
WHERE sf.visibility IN ('public', 'friends')
ORDER BY sf.created_at DESC;

-- ============================================================================
-- SCHEMA COMPLETE!
-- ============================================================================
-- Run this SQL in your Supabase SQL Editor to set up the complete database.
-- 
-- Next steps:
-- 1. Go to Supabase Dashboard > SQL Editor
-- 2. Paste this entire script
-- 3. Click "Run" to execute
-- 4. Update config.py with your Supabase URL and anon key
-- 5. Test authentication flow in the app
-- ============================================================================
