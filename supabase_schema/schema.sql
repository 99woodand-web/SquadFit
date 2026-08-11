-- ============================================================================
-- SMART GYM - Supabase Database Schema
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- USERS TABLE
-- ============================================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    display_name TEXT,
    avatar_url TEXT,
    age INTEGER,
    weight_kg DECIMAL(5,1),
    height_cm INTEGER,
    gender TEXT CHECK (gender IN ('male', 'female', 'other')),
    experience TEXT CHECK (experience IN ('Beginner', 'Regular', 'Athlete')),
    goal TEXT CHECK (goal IN ('Build Muscle', 'Get Stronger', 'Lose Weight', 'Stay Fit')),
    training_days INTEGER DEFAULT 3,
    equipment TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- WORKOUTS TABLE
-- ============================================================================
CREATE TABLE workouts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    focus TEXT NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    total_volume DECIMAL(10,1) DEFAULT 0,
    duration_minutes INTEGER,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- EXERCISES TABLE (exercise definitions)
-- ============================================================================
CREATE TABLE exercises (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    muscle TEXT NOT NULL,
    equipment TEXT NOT NULL,
    equipment_tags TEXT[] DEFAULT '{}',
    sets INTEGER DEFAULT 3,
    reps INTEGER DEFAULT 10,
    is_compound BOOLEAN DEFAULT FALSE,
    tip TEXT,
    video_url TEXT,
    image_url TEXT
);

-- ============================================================================
-- WORKOUT_EXERCISES TABLE (exercises in a workout)
-- ============================================================================
CREATE TABLE workout_exercises (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workout_id UUID REFERENCES workouts(id) ON DELETE CASCADE,
    exercise_id TEXT REFERENCES exercises(id),
    target_weight DECIMAL(5,1),
    target_reps INTEGER,
    actual_weight DECIMAL(5,1),
    actual_reps INTEGER,
    rpe DECIMAL(3,1),
    set_number INTEGER,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- PERSONAL_RECORDS TABLE
-- ============================================================================
CREATE TABLE personal_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    exercise_id TEXT REFERENCES exercises(id),
    weight DECIMAL(5,1),
    reps INTEGER,
    volume DECIMAL(10,1),
    date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, exercise_id)
);

-- ============================================================================
-- FRIENDS TABLE
-- ============================================================================
CREATE TABLE friends (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    friend_id UUID REFERENCES users(id) ON DELETE CASCADE,
    status TEXT CHECK (status IN ('pending', 'accepted', 'blocked')) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (user_id, friend_id)
);

-- ============================================================================
-- SOCIAL_POSTS TABLE
-- ============================================================================
CREATE TABLE social_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    post_type TEXT CHECK (post_type IN ('workout', 'pr', 'milestone', 'challenge')),
    content TEXT,
    workout_id UUID REFERENCES workouts(id),
    exercise_id TEXT,
    weight DECIMAL(5,1),
    reps INTEGER,
    volume DECIMAL(10,1),
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- LIKES TABLE
-- ============================================================================
CREATE TABLE likes (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    post_id UUID REFERENCES social_posts(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (user_id, post_id)
);

-- ============================================================================
-- COMMENTS TABLE
-- ============================================================================
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    post_id UUID REFERENCES social_posts(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- CHALLENGES TABLE
-- ============================================================================
CREATE TABLE challenges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    challenge_type TEXT CHECK (challenge_type IN ('volume', 'consistency', 'strength', 'custom')),
    target_value DECIMAL(10,1),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- CHALLENGE_PARTICIPANTS TABLE
-- ============================================================================
CREATE TABLE challenge_participants (
    challenge_id UUID REFERENCES challenges(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    current_value DECIMAL(10,1) DEFAULT 0,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (challenge_id, user_id)
);

-- ============================================================================
-- CALENDAR_EVENTS TABLE
-- ============================================================================
CREATE TABLE calendar_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    focus TEXT NOT NULL,
    exercises TEXT[] DEFAULT '{}',
    completed BOOLEAN DEFAULT FALSE,
    week_number INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- BODY_MEASUREMENTS TABLE
-- ============================================================================
CREATE TABLE body_measurements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    weight_kg DECIMAL(5,1),
    body_fat_percentage DECIMAL(4,1),
    chest_cm DECIMAL(5,1),
    waist_cm DECIMAL(5,1),
    hips_cm DECIMAL(5,1),
    bicep_cm DECIMAL(5,1),
    thigh_cm DECIMAL(5,1),
    photo_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- INDEXES
-- ============================================================================
CREATE INDEX idx_workouts_user_date ON workouts(user_id, date);
CREATE INDEX idx_workout_exercises_workout ON workout_exercises(workout_id);
CREATE INDEX idx_personal_records_user_exercise ON personal_records(user_id, exercise_id);
CREATE INDEX idx_social_posts_user ON social_posts(user_id, created_at DESC);
CREATE INDEX idx_calendar_events_user_date ON calendar_events(user_id, date);
CREATE INDEX idx_body_measurements_user ON body_measurements(user_id, date DESC);

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to calculate user stats
CREATE OR REPLACE FUNCTION get_user_stats(p_user_id UUID)
RETURNS TABLE (
    total_workouts BIGINT,
    total_volume DECIMAL,
    current_streak INTEGER,
    personal_records BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(DISTINCT w.id) as total_workouts,
        COALESCE(SUM(w.total_volume), 0) as total_volume,
        -- Streak calculation would be more complex in production
        0 as current_streak,
        (SELECT COUNT(*) FROM personal_records WHERE user_id = p_user_id) as personal_records
    FROM workouts w
    WHERE w.user_id = p_user_id AND w.completed = TRUE;
END;
$$ LANGUAGE plpgsql;

-- Function to get muscle recovery status
CREATE OR REPLACE FUNCTION get_muscle_recovery(p_user_id UUID, p_muscle TEXT)
RETURNS TABLE (
    last_worked DATE,
    days_since INTEGER,
    recovery_status TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        MAX(w.date) as last_worked,
        EXTRACT(DAY FROM NOW() - MAX(w.date))::INTEGER as days_since,
        CASE
            WHEN MAX(w.date) IS NULL THEN 'READY'
            WHEN EXTRACT(DAY FROM NOW() - MAX(w.date)) >= 3 THEN 'READY'
            WHEN EXTRACT(DAY FROM NOW() - MAX(w.date)) >= 2 THEN 'RECOVERING'
            ELSE 'FATIGUED'
        END as recovery_status
    FROM workouts w
    JOIN workout_exercises we ON we.workout_id = w.id
    JOIN exercises e ON e.id = we.exercise_id
    WHERE w.user_id = p_user_id AND e.muscle = p_muscle;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE workouts ENABLE ROW LEVEL SECURITY;
ALTER TABLE workout_exercises ENABLE ROW LEVEL SECURITY;
ALTER TABLE personal_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE friends ENABLE ROW LEVEL SECURITY;
ALTER TABLE social_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE likes ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE challenges ENABLE ROW LEVEL SECURITY;
ALTER TABLE challenge_participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE calendar_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE body_measurements ENABLE ROW LEVEL SECURITY;

-- Users can read their own data
CREATE POLICY users_self_read ON users FOR SELECT USING (auth.uid() = id);
CREATE POLICY users_self_update ON users FOR UPDATE USING (auth.uid() = id);

-- Workouts: users can CRUD their own
CREATE POLICY workouts_self_all ON workouts FOR ALL USING (auth.uid() = user_id);

-- Workout exercises: users can CRUD through their workouts
CREATE POLICY workout_exercises_self ON workout_exercises FOR ALL
    USING (EXISTS (SELECT 1 FROM workouts WHERE workouts.id = workout_exercises.workout_id AND workouts.user_id = auth.uid()));

-- Personal records: users can CRUD their own
CREATE POLICY pr_self ON personal_records FOR ALL USING (auth.uid() = user_id);

-- Friends: users can see their own friendships
CREATE POLICY friends_self ON friends FOR ALL USING (auth.uid() = user_id OR auth.uid() = friend_id);

-- Social posts: everyone can read, users can CRUD their own
CREATE POLICY posts_read ON social_posts FOR SELECT USING (TRUE);
CREATE POLICY posts_self ON social_posts FOR ALL USING (auth.uid() = user_id);

-- Calendar events: users can CRUD their own
CREATE POLICY calendar_self ON calendar_events FOR ALL USING (auth.uid() = user_id);

-- Body measurements: users can CRUD their own
CREATE POLICY measurements_self ON body_measurements FOR ALL USING (auth.uid() = user_id);
