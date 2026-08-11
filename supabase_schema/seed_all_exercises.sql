-- ============================================================================
-- SEED ALL EXERCISES FROM exercise_db.py INTO SUPABASE
-- This adds all missing exercises to bring the total to 62
-- ============================================================================

-- ============================================================================
-- STRENGTH EXERCISES (Barbell)
-- ============================================================================

INSERT INTO exercises (id, exercise_code, name, category, muscle, equipment, track_type, equipment_tags, default_sets, default_reps, is_compound, tip, alternatives)
VALUES 
  ('a0000000-0000-0000-0000-000000000001', 'g22', 'Barbell Floor Press', 'Chest', 'Chest', 'Barbell', 'strength', ARRAY['barbell'], 3, 10, true, 'Lie on floor, press from chest', ARRAY['g1', 'h1'])
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- STRENGTH EXERCISES (Dumbbell)
-- ============================================================================

INSERT INTO exercises (id, exercise_code, name, category, muscle, equipment, track_type, equipment_tags, default_sets, default_reps, is_compound, tip, alternatives)
VALUES 
  ('a0000000-0000-0000-0000-000000000002', 'g24', 'Dumbbell Floor Flyes', 'Chest', 'Chest', 'Dumbbells', 'strength', ARRAY['dumbbells'], 3, 12, false, 'Lie on floor, slight elbow bend', ARRAY['h3', 'g3'])
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- STRENGTH EXERCISES (Cable/Machine)
-- ============================================================================

INSERT INTO exercises (id, exercise_code, name, category, muscle, equipment, track_type, equipment_tags, default_sets, default_reps, is_compound, tip, alternatives)
VALUES 
  ('a0000000-0000-0000-0000-000000000003', 'g3', 'Cable Fly', 'Chest', 'Chest', 'Cables', 'strength', ARRAY['cables'], 3, 12, false, 'Slight elbow bend, squeeze at peak', ARRAY['h1', 'g1']),
  ('a0000000-0000-0000-0000-000000000004', 'g4', 'Tricep Pushdown', 'Arms', 'Triceps', 'Cables', 'strength', ARRAY['cables'], 3, 12, false, 'Elbows pinned to sides', ARRAY['h4']),
  ('a0000000-0000-0000-0000-000000000005', 'g6', 'Lat Pulldown', 'Back', 'Back', 'Machine', 'strength', ARRAY['machine'], 3, 10, false, 'Lean back slightly, pull to chest', ARRAY['h5', 'h6']),
  ('a0000000-0000-0000-0000-000000000006', 'g7', 'Seated Cable Row', 'Back', 'Back', 'Cables', 'strength', ARRAY['cables'], 3, 12, false, 'Squeeze shoulder blades', ARRAY['h6', 'h7']),
  ('a0000000-0000-0000-0000-000000000007', 'g10', 'Leg Press', 'Legs', 'Legs', 'Machine', 'strength', ARRAY['machine'], 3, 12, false, 'Dont lock knees', ARRAY['h9', 'h10', 'g9']),
  ('a0000000-0000-0000-0000-000000000008', 'g11', 'Leg Curl', 'Legs', 'Legs', 'Machine', 'strength', ARRAY['machine'], 3, 12, false, 'Control the eccentric', ARRAY['h11', 'g20']),
  ('a0000000-0000-0000-0000-000000000009', 'g12', 'Leg Extension', 'Legs', 'Legs', 'Machine', 'strength', ARRAY['machine'], 3, 12, false, 'Full extension, pause at top', ARRAY['h10']),
  ('a0000000-0000-0000-0000-000000000010', 'g15', 'Calf Raise', 'Legs', 'Calves', 'Machine', 'strength', ARRAY['machine'], 3, 15, false, 'Full stretch at bottom', ARRAY['h15'])
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- STRENGTH EXERCISES (Bodyweight/Home)
-- ============================================================================

INSERT INTO exercises (id, exercise_code, name, category, muscle, equipment, track_type, equipment_tags, default_sets, default_reps, is_compound, tip, alternatives)
VALUES 
  ('a0000000-0000-0000-0000-000000000011', 'h2', 'Diamond Push-Up', 'Chest', 'Chest', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 12, false, 'Hands together under chest', ARRAY['h1', 'g1']),
  ('a0000000-0000-0000-0000-000000000012', 'h3', 'Resistance Band Fly', 'Chest', 'Chest', 'Bands', 'strength', ARRAY['bands'], 3, 12, false, 'Control the tension', ARRAY['h1', 'g3']),
  ('a0000000-0000-0000-0000-000000000013', 'h4', 'Tricep Dips', 'Arms', 'Triceps', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 12, false, 'Elbows close to body', ARRAY['g4']),
  ('a0000000-0000-0000-0000-000000000014', 'h5', 'Pull-Up', 'Back', 'Back', 'Bodyweight', 'strength', ARRAY['pull_up_bar'], 3, 8, true, 'Full dead hang, pull to chin', ARRAY['h6', 'g5']),
  ('a0000000-0000-0000-0000-000000000015', 'h6', 'Inverted Row', 'Back', 'Back', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 10, false, 'Keep body straight', ARRAY['h5', 'g7']),
  ('a0000000-0000-0000-0000-000000000016', 'h7', 'Resistance Band Row', 'Back', 'Back', 'Bands', 'strength', ARRAY['bands'], 3, 12, false, 'Squeeze shoulder blades', ARRAY['h6', 'g7']),
  ('a0000000-0000-0000-0000-000000000017', 'h8', 'Hammer Curl', 'Arms', 'Biceps', 'Dumbbells', 'strength', ARRAY['dumbbells'], 3, 12, false, 'Neutral grip, control negative', ARRAY['g8']),
  ('a0000000-0000-0000-0000-000000000018', 'h9', 'Goblet Squat', 'Legs', 'Legs', 'Dumbbells', 'strength', ARRAY['dumbbells'], 3, 12, false, 'Hold weight at chest', ARRAY['h10', 'g9']),
  ('a0000000-0000-0000-0000-000000000019', 'h10', 'Walking Lunge', 'Legs', 'Legs', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 20, false, '90-degree knee bend', ARRAY['h9', 'g9']),
  ('a0000000-0000-0000-0000-000000000020', 'h11', 'Glute Bridge', 'Legs', 'Legs', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 15, false, 'Squeeze glutes at top', ARRAY['g20']),
  ('a0000000-0000-0000-0000-000000000021', 'h12', 'Step-Up', 'Legs', 'Legs', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 12, false, 'Drive through heel', ARRAY['h10']),
  ('a0000000-0000-0000-0000-000000000022', 'h13', 'Pike Push-Up', 'Shoulders', 'Shoulders', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 10, false, 'Hips high, press up', ARRAY['g13']),
  ('a0000000-0000-0000-0000-000000000023', 'h14', 'Resistance Band Press', 'Shoulders', 'Shoulders', 'Bands', 'strength', ARRAY['bands'], 3, 12, false, 'Press overhead', ARRAY['g14']),
  ('a0000000-0000-0000-0000-000000000024', 'h15', 'Single Leg Calf Raise', 'Legs', 'Calves', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 15, false, 'Full range', ARRAY['g15']),
  ('a0000000-0000-0000-0000-000000000025', 'h16', 'Crunch', 'Core', 'Core', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 20, false, 'Lower back stays down', ARRAY[]::text[]),
  ('a0000000-0000-0000-0000-000000000026', 'h20', 'Jump Squat', 'Legs', 'Legs', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 15, false, 'Soft landing', ARRAY['h9']),
  ('a0000000-0000-0000-0000-000000000027', 'h21', 'Kneeling Ab Roller Rollout', 'Core', 'Core', 'Ab Roller', 'strength', ARRAY['ab_roller'], 3, 10, false, 'Keep core tight, dont arch back', ARRAY['h16']),
  ('a0000000-0000-0000-0000-000000000028', 'h22', 'Full Ab Roller Extension', 'Core', 'Core', 'Ab Roller', 'strength', ARRAY['ab_roller'], 3, 8, true, 'Advanced: full extension from feet', ARRAY['h21']),
  ('a0000000-0000-0000-0000-000000000029', 'h23', 'Floor L-Sit', 'Core', 'Core', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 30, false, 'Hold for seconds, use bench for support', ARRAY['h16'])
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- CARDIO EXERCISES
-- ============================================================================

INSERT INTO exercises (id, exercise_code, name, category, muscle, equipment, track_type, equipment_tags, default_sets, default_reps, is_compound, tip, alternatives)
VALUES 
  -- Running
  ('a0000000-0000-0000-0000-000000000030', 'c1', 'Outdoor Run', 'Cardio', 'Cardio', 'Bodyweight', 'cardio', ARRAY[]::text[], 1, 1, false, 'Start easy, build pace gradually', ARRAY['c2', 'c3']),
  ('a0000000-0000-0000-0000-000000000031', 'c2', 'Treadmill Run', 'Cardio', 'Cardio', 'Treadmill', 'cardio', ARRAY['treadmill'], 1, 1, false, 'Use incline for hill simulation', ARRAY['c1', 'c3']),
  ('a0000000-0000-0000-0000-000000000032', 'c3', 'Interval Sprints', 'Cardio', 'Cardio', 'Bodyweight', 'cardio', ARRAY[]::text[], 8, 1, false, 'All-out effort on work intervals', ARRAY['c1', 'c4']),
  ('a0000000-0000-0000-0000-000000000033', 'c4', 'Tempo Run', 'Cardio', 'Cardio', 'Bodyweight', 'cardio', ARRAY[]::text[], 1, 1, false, 'Comfortably hard pace, 80-85% max HR', ARRAY['c1', 'c2']),
  ('a0000000-0000-0000-0000-000000000034', 'c5', 'Long Slow Distance', 'Cardio', 'Cardio', 'Bodyweight', 'cardio', ARRAY[]::text[], 1, 1, false, 'Easy conversational pace, build endurance', ARRAY['c1', 'c2']),
  
  -- Running Drills
  ('a0000000-0000-0000-0000-000000000035', 'c6', 'A-Skips', 'Cardio', 'Cardio', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 1, false, 'High knee drive, rhythmic skipping', ARRAY['c7']),
  ('a0000000-0000-0000-0000-000000000036', 'c7', 'High Knees', 'Cardio', 'Cardio', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 1, false, 'Knees to waist height, fast turnover', ARRAY['c6']),
  ('a0000000-0000-0000-0000-000000000037', 'c8', 'Butt Kicks', 'Cardio', 'Cardio', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 1, false, 'Heel to glute, quick cadence', ARRAY['c7']),
  ('a0000000-0000-0000-0000-000000000038', 'c9', 'Bounding', 'Cardio', 'Cardio', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 1, false, 'Exaggerated running stride, power', ARRAY['c6']),
  ('a0000000-0000-0000-0000-000000000039', 'c10', 'Strides', 'Cardio', 'Cardio', 'Bodyweight', 'strength', ARRAY[]::text[], 6, 1, false, '90% sprint, focus on form', ARRAY['c3']),
  
  -- Cycling
  ('a0000000-0000-0000-0000-000000000040', 'c11', 'Road Cycling', 'Cardio', 'Cardio', 'Bike', 'cardio', ARRAY['bike'], 1, 1, false, 'Maintain steady cadence 80-100 RPM', ARRAY['c12', 'c13']),
  ('a0000000-0000-0000-0000-000000000041', 'c12', 'Stationary Bike', 'Cardio', 'Cardio', 'Bike', 'cardio', ARRAY['bike'], 1, 1, false, 'Adjust resistance for intervals', ARRAY['c11', 'c13']),
  ('a0000000-0000-0000-0000-000000000042', 'c13', 'Spin Class', 'Cardio', 'Cardio', 'Bike', 'cardio', ARRAY['bike'], 1, 1, false, 'Follow instructor, push yourself', ARRAY['c12']),
  ('a0000000-0000-0000-0000-000000000043', 'c14', 'Cycling Intervals', 'Cardio', 'Cardio', 'Bike', 'cardio', ARRAY['bike'], 8, 1, false, 'High cadence sprints', ARRAY['c12']),
  
  -- Rowing
  ('a0000000-0000-0000-0000-000000000044', 'c15', 'Steady State Row', 'Cardio', 'Cardio', 'Rower', 'cardio', ARRAY['rower'], 1, 1, false, 'Consistent stroke rate, power through legs', ARRAY['c16']),
  ('a0000000-0000-0000-0000-000000000045', 'c16', 'Rowing Intervals', 'Cardio', 'Cardio', 'Rower', 'cardio', ARRAY['rower'], 5, 1, false, '2K test pace or slightly slower', ARRAY['c15']),
  
  -- Other Cardio
  ('a0000000-0000-0000-0000-000000000046', 'c17', 'Jump Rope', 'Cardio', 'Cardio', 'Bodyweight', 'strength', ARRAY[]::text[], 5, 1, false, 'Stay on balls of feet, keep elbows in', ARRAY['c3']),
  ('a0000000-0000-0000-0000-000000000047', 'c18', 'Burpees', 'Cardio', 'Cardio', 'Bodyweight', 'strength', ARRAY[]::text[], 5, 15, false, 'Explosive movement, full extension', ARRAY['c3', 'c7']),
  ('a0000000-0000-0000-0000-000000000048', 'c19', 'Mountain Climbers', 'Cardio', 'Cardio', 'Bodyweight', 'strength', ARRAY[]::text[], 4, 1, false, 'Keep hips level, fast pace', ARRAY['c18']),
  ('a0000000-0000-0000-0000-000000000049', 'c20', 'Stair Climber', 'Cardio', 'Cardio', 'Machine', 'cardio', ARRAY['machine'], 1, 1, false, 'Dont lean on rails, drive through legs', ARRAY['c2'])
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- VERIFY COUNT
-- ============================================================================
SELECT COUNT(*) as total_exercises_after FROM exercises;
