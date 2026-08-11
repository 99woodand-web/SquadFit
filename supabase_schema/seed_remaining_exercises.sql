-- ============================================================================
-- SEED REMAINING EXERCISES (ONLY THOSE NOT ALREADY IN SUPABASE)
-- ============================================================================

-- Already exist: g1, g2, g5, g9, g13, g20, g21, g8, g14, g23, g25
-- Already exist: h1, h5, h9, h10, h13, h16, h21
-- Already exist: c1, c2, c3, c11, c12, c17, c18

-- ============================================================================
-- STRENGTH EXERCISES (Barbell) - MISSING
-- ============================================================================

INSERT INTO exercises (id, exercise_code, name, category, muscle, equipment, track_type, equipment_tags, default_sets, default_reps, is_compound, tip, alternatives)
VALUES 
  ('a0000000-0000-0000-0000-000000000001', 'g22', 'Barbell Floor Press', 'Chest', 'Chest', 'Barbell', 'strength', ARRAY['barbell'], 3, 10, true, 'Lie on floor, press from chest', ARRAY['g1', 'h1'])
ON CONFLICT (exercise_code) DO NOTHING;

-- ============================================================================
-- STRENGTH EXERCISES (Dumbbell) - MISSING
-- ============================================================================

INSERT INTO exercises (id, exercise_code, name, category, muscle, equipment, track_type, equipment_tags, default_sets, default_reps, is_compound, tip, alternatives)
VALUES 
  ('a0000000-0000-0000-0000-000000000002', 'g24', 'Dumbbell Floor Flyes', 'Chest', 'Chest', 'Dumbbells', 'strength', ARRAY['dumbbells'], 3, 12, false, 'Lie on floor, slight elbow bend', ARRAY['h3', 'g3'])
ON CONFLICT (exercise_code) DO NOTHING;

-- ============================================================================
-- STRENGTH EXERCISES (Cable/Machine) - ALL MISSING
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
ON CONFLICT (exercise_code) DO NOTHING;

-- ============================================================================
-- STRENGTH EXERCISES (Bodyweight/Home) - MISSING
-- ============================================================================

INSERT INTO exercises (id, exercise_code, name, category, muscle, equipment, track_type, equipment_tags, default_sets, default_reps, is_compound, tip, alternatives)
VALUES 
  ('a0000000-0000-0000-0000-000000000011', 'h2', 'Diamond Push-Up', 'Chest', 'Chest', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 12, false, 'Hands together under chest', ARRAY['h1', 'g1']),
  ('a0000000-0000-0000-0000-000000000012', 'h3', 'Resistance Band Fly', 'Chest', 'Chest', 'Bands', 'strength', ARRAY['bands'], 3, 12, false, 'Control the tension', ARRAY['h1', 'g3']),
  ('a0000000-0000-0000-0000-000000000013', 'h4', 'Tricep Dips', 'Arms', 'Triceps', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 12, false, 'Elbows close to body', ARRAY['g4']),
  ('a0000000-0000-0000-0000-000000000015', 'h6', 'Inverted Row', 'Back', 'Back', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 10, false, 'Keep body straight', ARRAY['h5', 'g7']),
  ('a0000000-0000-0000-0000-000000000016', 'h7', 'Resistance Band Row', 'Back', 'Back', 'Bands', 'strength', ARRAY['bands'], 3, 12, false, 'Squeeze shoulder blades', ARRAY['h6', 'g7']),
  ('a0000000-0000-0000-0000-000000000017', 'h8', 'Hammer Curl', 'Arms', 'Biceps', 'Dumbbells', 'strength', ARRAY['dumbbells'], 3, 12, false, 'Neutral grip, control negative', ARRAY['g8']),
  ('a0000000-0000-0000-0000-000000000018', 'h9b', 'Goblet Squat', 'Legs', 'Legs', 'Dumbbells', 'strength', ARRAY['dumbbells'], 3, 12, false, 'Hold weight at chest', ARRAY['h10', 'g9']),
  ('a0000000-0000-0000-0000-000000000020', 'h11', 'Glute Bridge', 'Legs', 'Legs', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 15, false, 'Squeeze glutes at top', ARRAY['g20']),
  ('a0000000-0000-0000-0000-000000000021', 'h12', 'Step-Up', 'Legs', 'Legs', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 12, false, 'Drive through heel', ARRAY['h10']),
  ('a0000000-0000-0000-0000-000000000023', 'h14', 'Resistance Band Press', 'Shoulders', 'Shoulders', 'Bands', 'strength', ARRAY['bands'], 3, 12, false, 'Press overhead', ARRAY['g14']),
  ('a0000000-0000-0000-0000-000000000024', 'h15', 'Single Leg Calf Raise', 'Legs', 'Calves', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 15, false, 'Full range', ARRAY['g15']),
  ('a0000000-0000-0000-0000-000000000026', 'h20', 'Jump Squat', 'Legs', 'Legs', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 15, false, 'Soft landing', ARRAY['h9']),
  ('a0000000-0000-0000-0000-000000000028', 'h22', 'Full Ab Roller Extension', 'Core', 'Core', 'Ab Roller', 'strength', ARRAY['ab_roller'], 3, 8, true, 'Advanced: full extension from feet', ARRAY['h21']),
  ('a0000000-0000-0000-0000-000000000029', 'h23', 'Floor L-Sit', 'Core', 'Core', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 30, false, 'Hold for seconds, use bench for support', ARRAY['h16'])
ON CONFLICT (exercise_code) DO NOTHING;

-- ============================================================================
-- CARDIO EXERCISES - MISSING
-- ============================================================================

INSERT INTO exercises (id, exercise_code, name, category, muscle, equipment, track_type, equipment_tags, default_sets, default_reps, is_compound, tip, alternatives)
VALUES 
  ('a0000000-0000-0000-0000-000000000033', 'c4', 'Tempo Run', 'Cardio', 'Cardio', 'Bodyweight', 'cardio', ARRAY[]::text[], 1, 1, false, 'Comfortably hard pace, 80-85% max HR', ARRAY['c1', 'c2']),
  ('a0000000-0000-0000-0000-000000000034', 'c5', 'Long Slow Distance', 'Cardio', 'Cardio', 'Bodyweight', 'cardio', ARRAY[]::text[], 1, 1, false, 'Easy conversational pace, build endurance', ARRAY['c1', 'c2']),
  ('a0000000-0000-0000-0000-000000000035', 'c6', 'A-Skips', 'Cardio', 'Cardio', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 1, false, 'High knee drive, rhythmic skipping', ARRAY['c7']),
  ('a0000000-0000-0000-0000-000000000036', 'c7', 'High Knees', 'Cardio', 'Cardio', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 1, false, 'Knees to waist height, fast turnover', ARRAY['c6']),
  ('a0000000-0000-0000-0000-000000000037', 'c8', 'Butt Kicks', 'Cardio', 'Cardio', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 1, false, 'Heel to glute, quick cadence', ARRAY['c7']),
  ('a0000000-0000-0000-0000-000000000038', 'c9', 'Bounding', 'Cardio', 'Cardio', 'Bodyweight', 'strength', ARRAY[]::text[], 3, 1, false, 'Exaggerated running stride, power', ARRAY['c6']),
  ('a0000000-0000-0000-0000-000000000039', 'c10', 'Strides', 'Cardio', 'Cardio', 'Bodyweight', 'strength', ARRAY[]::text[], 6, 1, false, '90% sprint, focus on form', ARRAY['c3']),
  ('a0000000-0000-0000-0000-000000000042', 'c13', 'Spin Class', 'Cardio', 'Cardio', 'Bike', 'cardio', ARRAY['bike'], 1, 1, false, 'Follow instructor, push yourself', ARRAY['c12']),
  ('a0000000-0000-0000-0000-000000000043', 'c14', 'Cycling Intervals', 'Cardio', 'Cardio', 'Bike', 'cardio', ARRAY['bike'], 8, 1, false, 'High cadence sprints', ARRAY['c12']),
  ('a0000000-0000-0000-0000-000000000044', 'c15', 'Steady State Row', 'Cardio', 'Cardio', 'Rower', 'cardio', ARRAY['rower'], 1, 1, false, 'Consistent stroke rate, power through legs', ARRAY['c16']),
  ('a0000000-0000-0000-0000-000000000045', 'c16', 'Rowing Intervals', 'Cardio', 'Cardio', 'Rower', 'cardio', ARRAY['rower'], 5, 1, false, '2K test pace or slightly slower', ARRAY['c15']),
  ('a0000000-0000-0000-0000-000000000048', 'c19', 'Mountain Climbers', 'Cardio', 'Cardio', 'Bodyweight', 'strength', ARRAY[]::text[], 4, 1, false, 'Keep hips level, fast pace', ARRAY['c18']),
  ('a0000000-0000-0000-0000-000000000049', 'c20', 'Stair Climber', 'Cardio', 'Cardio', 'Machine', 'cardio', ARRAY['machine'], 1, 1, false, 'Dont lean on rails, drive through legs', ARRAY['c2'])
ON CONFLICT (exercise_code) DO NOTHING;

-- ============================================================================
-- VERIFY COUNT
-- ============================================================================
SELECT COUNT(*) as total_exercises_after FROM exercises;
