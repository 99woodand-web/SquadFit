# exercise_db.py - Comprehensive Exercise Database (150+ exercises)
# Organized by muscle group, equipment, and difficulty
# Categories: Chest, Back, Legs, Shoulders, Arms, Core, Cardio

# ============================================================================
# MUSCLE GROUPS:
#   Chest, Back, Legs, Shoulders, Biceps, Triceps, Core, Cardio
# EQUIPMENT:
#   Barbell, Dumbbells, Cable, Machine, Bodyweight, Kettlebell, Bands
# TRACK:
#   strength (sets/reps/weight), cardio (distance/duration/pace)
# DIFFICULTY:
#   Beginner, Intermediate, Advanced
# ============================================================================

STRENGTH_EXERCISES = {
    # ========================================================================
    # CHEST EXERCISES (15)
    # ========================================================================
    "c01": {"name": "Flat Bench Press", "muscle": "Chest", "equip": "Barbell",
            "equip_tags": ["barbell", "bench"], "sets": 4, "reps": 10, "compound": True,
            "tip": "Keep shoulder blades squeezed, feet flat on floor", "track": "strength",
            "difficulty": "Intermediate", "alternatives": ["c02", "c03", "c04"]},
    "c02": {"name": "Incline Bench Press", "muscle": "Chest", "equip": "Barbell",
            "equip_tags": ["barbell", "bench"], "sets": 3, "reps": 10, "compound": True,
            "tip": "Set bench 30-45 degrees, press to upper chest", "track": "strength",
            "difficulty": "Intermediate", "alternatives": ["c03", "c04", "c01"]},
    "c03": {"name": "Dumbbell Flat Press", "muscle": "Chest", "equip": "Dumbbells",
            "equip_tags": ["dumbbells", "bench"], "sets": 3, "reps": 10, "compound": True,
            "tip": "Full range of motion, squeeze at top", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["c01", "c04", "c05"]},
    "c04": {"name": "Dumbbell Incline Press", "muscle": "Chest", "equip": "Dumbbells",
            "equip_tags": ["dumbbells", "bench"], "sets": 3, "reps": 10, "compound": True,
            "tip": "30-45 degree incline, control the negative", "track": "strength",
            "difficulty": "Intermediate", "alternatives": ["c02", "c03", "c05"]},
    "c05": {"name": "Cable Fly", "muscle": "Chest", "equip": "Cable",
            "equip_tags": ["cable"], "sets": 3, "reps": 12, "compound": False,
            "tip": "Slight bend in elbows, squeeze chest at center", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["c06", "c07", "c08"]},
    "c16": {"name": "Cable Crossover", "muscle": "Chest", "equip": "Cable",
            "equip_tags": ["cable"], "sets": 3, "reps": 12, "compound": False,
            "tip": "Step forward, cross hands at center, squeeze chest", "track": "strength",
            "difficulty": "Intermediate", "alternatives": ["c05", "c06", "c15"]},
    "c06": {"name": "Pec Deck Machine", "muscle": "Chest", "equip": "Machine",
            "equip_tags": ["machine"], "sets": 3, "reps": 12, "compound": False,
            "tip": "Control the movement, squeeze at peak contraction", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["c05", "c07", "c08"]},
    "c07": {"name": "Push-Up", "muscle": "Chest", "equip": "Bodyweight",
            "equip_tags": [], "sets": 3, "reps": 15, "compound": True,
            "tip": "Full range, core tight, hands shoulder-width", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["c08", "c03", "c09"]},
    "c08": {"name": "Incline Push-Up", "muscle": "Chest", "equip": "Bodyweight",
            "equip_tags": [], "sets": 3, "reps": 12, "compound": True,
            "tip": "Hands on elevated surface, easier variation", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["c07", "c09", "c03"]},
    "c09": {"name": "Dumbbell Floor Fly", "muscle": "Chest", "equip": "Dumbbells",
            "equip_tags": ["dumbbells"], "sets": 3, "reps": 12, "compound": False,
            "tip": "Floor limits range, protects shoulders", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["c05", "c06", "c07"]},
    "c10": {"name": "Decline Bench Press", "muscle": "Chest", "equip": "Barbell",
            "equip_tags": ["barbell", "bench"], "sets": 3, "reps": 10, "compound": True,
            "tip": "Targets lower chest, secure legs", "track": "strength",
            "difficulty": "Intermediate", "alternatives": ["c01", "c03", "c11"]},
    "c11": {"name": "Smith Machine Press", "muscle": "Chest", "equip": "Machine",
            "equip_tags": ["machine"], "sets": 3, "reps": 10, "compound": True,
            "tip": "Fixed path, good for isolation", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["c01", "c03", "c12"]},
    "c12": {"name": "Chest Dip", "muscle": "Chest", "equip": "Bodyweight",
            "equip_tags": [], "sets": 3, "reps": 12, "compound": True,
            "tip": "Lean forward, elbows out for chest emphasis", "track": "strength",
            "difficulty": "Intermediate", "alternatives": ["c07", "c01", "c13"]},
    "c13": {"name": "Landmine Press", "muscle": "Chest", "equip": "Barbell",
            "equip_tags": ["barbell"], "sets": 3, "reps": 10, "compound": True,
            "tip": "Press at 45-degree angle, core braced", "track": "strength",
            "difficulty": "Intermediate", "alternatives": ["c01", "c02", "c04"]},
    "c14": {"name": "Dumbbell Pullover", "muscle": "Chest", "equip": "Dumbbells",
            "equip_tags": ["dumbbells", "bench"], "sets": 3, "reps": 12, "compound": False,
            "tip": "Slight bend in elbows, stretch at bottom", "track": "strength",
            "difficulty": "Intermediate", "alternatives": ["c05", "c09", "c15"]},
    "c15": {"name": "Machine Chest Press", "muscle": "Chest", "equip": "Machine",
            "equip_tags": ["machine"], "sets": 3, "reps": 12, "compound": True,
            "tip": "Adjust seat height, full range of motion", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["c01", "c03", "c06"]},

    # ========================================================================
    # BACK EXERCISES (15)
    # ========================================================================
    "b01": {"name": "Barbell Bent-Over Row", "muscle": "Back", "equip": "Barbell",
            "equip_tags": ["barbell"], "sets": 4, "reps": 10, "compound": True,
            "tip": "Hinge forward 45 degrees, pull to lower chest", "track": "strength",
            "difficulty": "Intermediate", "alternatives": ["b02", "b03", "b04"]},
    "b02": {"name": "Dumbbell Single-Arm Row", "muscle": "Back", "equip": "Dumbbells",
            "equip_tags": ["dumbbells", "bench"], "sets": 3, "reps": 10, "compound": True,
            "tip": "Support on bench, pull to hip", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["b01", "b03", "b05"]},
    "b03": {"name": "Cable Seated Row", "muscle": "Back", "equip": "Cable",
            "equip_tags": ["cable"], "sets": 3, "reps": 12, "compound": True,
            "tip": "Chest up, squeeze shoulder blades together", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["b01", "b02", "b04"]},
    "b04": {"name": "Lat Pulldown", "muscle": "Back", "equip": "Cable",
            "equip_tags": ["cable"], "sets": 3, "reps": 12, "compound": True,
            "tip": "Pull to upper chest, control the negative", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["b05", "b06", "b07"]},
    "b05": {"name": "Pull-Up", "muscle": "Back", "equip": "Bodyweight",
            "equip_tags": [], "sets": 3, "reps": 8, "compound": True,
            "tip": "Full dead hang, pull chin over bar", "track": "strength",
            "difficulty": "Advanced", "alternatives": ["b04", "b06", "b07"]},
    "b06": {"name": "Chin-Up", "muscle": "Back", "equip": "Bodyweight",
            "equip_tags": [], "sets": 3, "reps": 8, "compound": True,
            "tip": "Palms facing you, more bicep involvement", "track": "strength",
            "difficulty": "Advanced", "alternatives": ["b05", "b04", "b07"]},
    "b07": {"name": "Assisted Pull-Up", "muscle": "Back", "equip": "Machine",
            "equip_tags": ["machine"], "sets": 3, "reps": 10, "compound": True,
            "tip": "Use assistance band or machine", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["b04", "b05", "b08"]},
    "b08": {"name": "Barbell Deadlift", "muscle": "Back", "equip": "Barbell",
            "equip_tags": ["barbell"], "sets": 4, "reps": 5, "compound": True,
            "tip": "Brace core, drive through heels", "track": "strength",
            "difficulty": "Advanced", "alternatives": ["b09", "b10", "b11"]},
    "b09": {"name": "Romanian Deadlift", "muscle": "Back", "equip": "Barbell",
            "equip_tags": ["barbell"], "sets": 3, "reps": 10, "compound": True,
            "tip": "Hinge at hips, feel hamstring stretch", "track": "strength",
            "difficulty": "Intermediate", "alternatives": ["b08", "b10", "b11"]},
    "b10": {"name": "Dumbbell Romanian Deadlift", "muscle": "Back", "equip": "Dumbbells",
            "equip_tags": ["dumbbells"], "sets": 3, "reps": 10, "compound": True,
            "tip": "Control the stretch, keep back straight", "track": "strength",
            "difficulty": "Intermediate", "alternatives": ["b09", "b08", "b11"]},
    "b11": {"name": "Cable Straight-Arm Pulldown", "muscle": "Back", "equip": "Cable",
            "equip_tags": ["cable"], "sets": 3, "reps": 12, "compound": False,
            "tip": "Keep arms straight, squeeze lats", "track": "strength",
            "difficulty": "Intermediate", "alternatives": ["b04", "b03", "b12"]},
    "b12": {"name": "Dumbbell Reverse Fly", "muscle": "Back", "equip": "Dumbbells",
            "equip_tags": ["dumbbells"], "sets": 3, "reps": 12, "compound": False,
            "tip": "Hinge forward, squeeze rear delts", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["b03", "b11", "b13"]},
    "b13": {"name": "T-Bar Row", "muscle": "Back", "equip": "Barbell",
            "equip_tags": ["barbell"], "sets": 3, "reps": 10, "compound": True,
            "tip": "Chest supported, pull to chest", "track": "strength",
            "difficulty": "Intermediate", "alternatives": ["b01", "b02", "b03"]},
    "b14": {"name": "Seal Row", "muscle": "Back", "equip": "Dumbbells",
            "equip_tags": ["dumbbells", "bench"], "sets": 3, "reps": 10, "compound": True,
            "tip": "Lie face down on incline bench, row dumbbells", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["b02", "b01", "b03"]},
    "b15": {"name": "Machine Row", "muscle": "Back", "equip": "Machine",
            "equip_tags": ["machine"], "sets": 3, "reps": 12, "compound": True,
            "tip": "Adjust chest pad, full range of motion", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["b03", "b01", "b02"]},

    # ========================================================================
    # LEGS EXERCISES (20)
    # ========================================================================
    "l01": {"name": "Barbell Back Squat", "muscle": "Legs", "equip": "Barbell",
            "equip_tags": ["barbell"], "sets": 4, "reps": 8, "compound": True,
            "tip": "Break at hips, knees track toes", "track": "strength",
            "difficulty": "Intermediate", "alternatives": ["l02", "l03", "l04"]},
    "l02": {"name": "Goblet Squat", "muscle": "Legs", "equip": "Dumbbells",
            "equip_tags": ["dumbbells"], "sets": 3, "reps": 12, "compound": True,
            "tip": "Hold dumbbell at chest, squat deep", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["l01", "l03", "l05"]},
    "l03": {"name": "Leg Press", "muscle": "Legs", "equip": "Machine",
            "equip_tags": ["machine"], "sets": 3, "reps": 12, "compound": True,
            "tip": "Feet shoulder-width, full range of motion", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["l01", "l02", "l04"]},
    "l04": {"name": "Front Squat", "muscle": "Legs", "equip": "Barbell",
            "equip_tags": ["barbell"], "sets": 3, "reps": 8, "compound": True,
            "tip": "Elbows high, upright torso", "track": "strength",
            "difficulty": "Advanced", "alternatives": ["l01", "l02", "l05"]},
    "l05": {"name": "Dumbbell Bulgarian Split Squat", "muscle": "Legs", "equip": "Dumbbells",
            "equip_tags": ["dumbbells", "bench"], "sets": 3, "reps": 10, "compound": True,
            "tip": "Rear foot elevated, lean forward for glutes", "track": "strength",
            "difficulty": "Intermediate", "alternatives": ["l06", "l01", "l07"]},
    "l06": {"name": "Walking Lunge", "muscle": "Legs", "equip": "Dumbbells",
            "equip_tags": ["dumbbells"], "sets": 3, "reps": 12, "compound": True,
            "tip": "Long stride, knee tracks forward", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["l05", "l07", "l01"]},
    "l07": {"name": "Reverse Lunge", "muscle": "Legs", "equip": "Dumbbells",
            "equip_tags": ["dumbbells"], "sets": 3, "reps": 10, "compound": True,
            "tip": "Step back, knee kisses floor", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["l06", "l05", "l01"]},
    "l08": {"name": "Leg Extension", "muscle": "Legs", "equip": "Machine",
            "equip_tags": ["machine"], "sets": 3, "reps": 12, "compound": False,
            "tip": "Squeeze quads at top, control negative", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["l09", "l03", "l01"]},
    "l09": {"name": "Leg Curl (Seated)", "muscle": "Legs", "equip": "Machine",
            "equip_tags": ["machine"], "sets": 3, "reps": 12, "compound": False,
            "tip": "Squeeze hamstrings at peak, controlled movement", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["l10", "l11", "l12"]},
    "l20": {"name": "Leg Curl (Lying)", "muscle": "Legs", "equip": "Machine",
            "equip_tags": ["machine"], "sets": 3, "reps": 12, "compound": False,
            "tip": "Lie face down, curl heels to glutes", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["l09", "l10", "l11"]},
    "l21": {"name": "Hip Abduction Machine", "muscle": "Legs", "equip": "Machine",
            "equip_tags": ["machine"], "sets": 3, "reps": 15, "compound": False,
            "tip": "Push legs outward, control the return", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["l22", "l16"]},
    "l22": {"name": "Hip Adduction Machine", "muscle": "Legs", "equip": "Machine",
            "equip_tags": ["machine"], "sets": 3, "reps": 15, "compound": False,
            "tip": "Squeeze legs together, hold briefly", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["l21", "l16"]},
    "l10": {"name": "Romanian Deadlift", "muscle": "Legs", "equip": "Barbell",
            "equip_tags": ["barbell"], "sets": 3, "reps": 10, "compound": True,
            "tip": "Hinge at hips, feel hamstring stretch", "track": "strength",
            "difficulty": "Intermediate", "alternatives": ["l11", "l09", "l12"]},
    "l11": {"name": "Dumbbell Romanian Deadlift", "muscle": "Legs", "equip": "Dumbbells",
            "equip_tags": ["dumbbells"], "sets": 3, "reps": 10, "compound": True,
            "tip": "Control the stretch, keep back straight", "track": "strength",
            "difficulty": "Intermediate", "alternatives": ["l10", "l09", "l12"]},
    "l12": {"name": "Nordic Ham Curl", "muscle": "Legs", "equip": "Bodyweight",
            "equip_tags": [], "sets": 3, "reps": 6, "compound": False,
            "tip": "Control the eccentric, use hands to assist", "track": "strength",
            "difficulty": "Advanced", "alternatives": ["l09", "l10", "l11"]},
    "l13": {"name": "Hip Thrust", "muscle": "Legs", "equip": "Barbell",
            "equip_tags": ["barbell", "bench"], "sets": 3, "reps": 10, "compound": True,
            "tip": "Drive through heels, squeeze glutes at top", "track": "strength",
            "difficulty": "Intermediate", "alternatives": ["l14", "l15", "l16"]},
    "l14": {"name": "Glute Bridge", "muscle": "Legs", "equip": "Bodyweight",
            "equip_tags": [], "sets": 3, "reps": 15, "compound": False,
            "tip": "Squeeze glutes, hold at top", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["l13", "l15", "l16"]},
    "l15": {"name": "Cable Pull-Through", "muscle": "Legs", "equip": "Cable",
            "equip_tags": ["cable"], "sets": 3, "reps": 12, "compound": False,
            "tip": "Hinge at hips, squeeze glutes", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["l13", "l14", "l16"]},
    "l16": {"name": "Banded Glute Kickback", "muscle": "Legs", "equip": "Bands",
            "equip_tags": ["bands"], "sets": 3, "reps": 15, "compound": False,
            "tip": "Kick back and squeeze, control return", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["l14", "l15", "l13"]},
    "l17": {"name": "Calf Raise (Standing)", "muscle": "Legs", "equip": "Machine",
            "equip_tags": ["machine"], "sets": 4, "reps": 15, "compound": False,
            "tip": "Full stretch at bottom, pause at top", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["l18", "l19"]},
    "l18": {"name": "Calf Raise (Seated)", "muscle": "Legs", "equip": "Machine",
            "equip_tags": ["machine"], "sets": 3, "reps": 15, "compound": False,
            "tip": "Targets soleus, full range of motion", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["l17", "l19"]},
    "l19": {"name": "Single-Leg Calf Raise", "muscle": "Legs", "equip": "Bodyweight",
            "equip_tags": [], "sets": 3, "reps": 12, "compound": False,
            "tip": "Use wall for balance, full range", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["l17", "l18"]},

    # ========================================================================
    # SHOULDERS EXERCISES (12)
    # ========================================================================
    "s01": {"name": "Military Press", "muscle": "Shoulders", "equip": "Barbell",
            "equip_tags": ["barbell"], "sets": 4, "reps": 8, "compound": True,
            "tip": "Brace core, press straight up", "track": "strength",
            "difficulty": "Intermediate", "alternatives": ["s02", "s03", "s04"]},
    "s02": {"name": "Dumbbell Shoulder Press", "muscle": "Shoulders", "equip": "Dumbbells",
            "equip_tags": ["dumbbells"], "sets": 3, "reps": 10, "compound": True,
            "tip": "Full range, don't arch back", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["s01", "s03", "s04"]},
    "s03": {"name": "Cable Lateral Raise", "muscle": "Shoulders", "equip": "Cable",
            "equip_tags": ["cable"], "sets": 3, "reps": 12, "compound": False,
            "tip": "Cable behind back for constant tension", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["s04", "s05", "s06"]},
    "s04": {"name": "Dumbbell Lateral Raise", "muscle": "Shoulders", "equip": "Dumbbells",
            "equip_tags": ["dumbbells"], "sets": 3, "reps": 12, "compound": False,
            "tip": "Raise to shoulder height, slight forward lean", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["s03", "s05", "s06"]},
    "s05": {"name": "Cable Face Pull", "muscle": "Shoulders", "equip": "Cable",
            "equip_tags": ["cable"], "sets": 3, "reps": 15, "compound": False,
            "tip": "Pull to face, external rotate at end", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["s06", "s03", "s04"]},
    "s06": {"name": "Band Face Pull", "muscle": "Shoulders", "equip": "Bands",
            "equip_tags": ["bands"], "sets": 3, "reps": 15, "compound": False,
            "tip": "Anchor at eye level, pull apart", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["s05", "s03", "s04"]},
    "s07": {"name": "Arnold Press", "muscle": "Shoulders", "equip": "Dumbbells",
            "equip_tags": ["dumbbells"], "sets": 3, "reps": 10, "compound": True,
            "tip": "Rotate palms during press", "track": "strength",
            "difficulty": "Intermediate", "alternatives": ["s01", "s02", "s03"]},
    "s08": {"name": "Dumbbell Front Raise", "muscle": "Shoulders", "equip": "Dumbbells",
            "equip_tags": ["dumbbells"], "sets": 3, "reps": 12, "compound": False,
            "tip": "Alternate arms, control the negative", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["s04", "s03", "s09"]},
    "s09": {"name": "Cable Rear Delt Fly", "muscle": "Shoulders", "equip": "Cable",
            "equip_tags": ["cable"], "sets": 3, "reps": 12, "compound": False,
            "tip": "Crossover cables, squeeze rear delts", "track": "strength",
            "difficulty": "Intermediate", "alternatives": ["s05", "s06", "s04"]},
    "s10": {"name": "Machine Shoulder Press", "muscle": "Shoulders", "equip": "Machine",
            "equip_tags": ["machine"], "sets": 3, "reps": 10, "compound": True,
            "tip": "Adjust seat, full range of motion", "track": "strength",
            "difficulty": "Beginner", "alternatives": ["s01", "s02", "s03"]},
    "s11": {"name": "Handstand Push-Up", "muscle": "Shoulders", "equip": "Bodyweight",
            "equip_tags": [], "sets": 3, "reps": 5, "compound": True,
            "tip": "Wall-supported, full range", "track": "strength",
            "difficulty": "Advanced", "alternatives": ["s01", "s02", "s10"]},
    "s12": {"name": "Upright Row", "muscle": "Shoulders", "equip": "Barbell",
            "equip_tags": ["barbell"], "sets": 3, "reps": 10, "compound": True,
            "tip": "Pull to chin, elbows high", "track": "strength",
            "difficulty": "Intermediate", "alternatives": ["s01", "s02", "s04"]},

    # ========================================================================
    # BICEPS EXERCISES (8)
    # ========================================================================
    "bi01": {"name": "Barbell Curl", "muscle": "Biceps", "equip": "Barbell",
             "equip_tags": ["barbell"], "sets": 3, "reps": 10, "compound": False,
             "tip": "Keep elbows pinned, control negative", "track": "strength",
             "difficulty": "Beginner", "alternatives": ["bi02", "bi03", "bi04"]},
    "bi02": {"name": "Dumbbell Curl", "muscle": "Biceps", "equip": "Dumbbells",
             "equip_tags": ["dumbbells"], "sets": 3, "reps": 10, "compound": False,
             "tip": "Supinate at top, full range", "track": "strength",
             "difficulty": "Beginner", "alternatives": ["bi01", "bi03", "bi04"]},
    "bi03": {"name": "Hammer Curl", "muscle": "Biceps", "equip": "Dumbbells",
             "equip_tags": ["dumbbells"], "sets": 3, "reps": 12, "compound": False,
             "tip": "Neutral grip targets brachialis", "track": "strength",
             "difficulty": "Beginner", "alternatives": ["bi02", "bi01", "bi05"]},
    "bi04": {"name": "Cable Curl", "muscle": "Biceps", "equip": "Cable",
             "equip_tags": ["cable"], "sets": 3, "reps": 12, "compound": False,
             "tip": "Constant tension, squeeze at top", "track": "strength",
             "difficulty": "Beginner", "alternatives": ["bi01", "bi02", "bi03"]},
    "bi05": {"name": "Preacher Curl", "muscle": "Biceps", "equip": "Barbell",
             "equip_tags": ["barbell"], "sets": 3, "reps": 10, "compound": False,
             "tip": "Full stretch at bottom, squeeze at top", "track": "strength",
             "difficulty": "Intermediate", "alternatives": ["bi01", "bi02", "bi06"]},
    "bi06": {"name": "Incline Dumbbell Curl", "muscle": "Biceps", "equip": "Dumbbells",
             "equip_tags": ["dumbbells", "bench"], "sets": 3, "reps": 10, "compound": False,
             "tip": "45-degree incline, full stretch", "track": "strength",
             "difficulty": "Intermediate", "alternatives": ["bi02", "bi05", "bi07"]},
    "bi07": {"name": "Concentration Curl", "muscle": "Biceps", "equip": "Dumbbells",
             "equip_tags": ["dumbbells"], "sets": 3, "reps": 12, "compound": False,
             "tip": "Elbow on thigh, full contraction", "track": "strength",
             "difficulty": "Beginner", "alternatives": ["bi02", "bi03", "bi04"]},
    "bi08": {"name": "Chin-Up (Bicep Focus)", "muscle": "Biceps", "equip": "Bodyweight",
             "equip_tags": [], "sets": 3, "reps": 8, "compound": True,
             "tip": "Close grip, palms facing you", "track": "strength",
             "difficulty": "Advanced", "alternatives": ["bi02", "bi04", "bi05"]},

    # ========================================================================
    # TRICEPS EXERCISES (8)
    # ========================================================================
    "tr01": {"name": "Tricep Pushdown", "muscle": "Triceps", "equip": "Cable",
             "equip_tags": ["cable"], "sets": 3, "reps": 12, "compound": False,
             "tip": "Elbows pinned, full lockout", "track": "strength",
             "difficulty": "Beginner", "alternatives": ["tr02", "tr03", "tr04"]},
    "tr02": {"name": "Overhead Tricep Extension", "muscle": "Triceps", "equip": "Cable",
             "equip_tags": ["cable"], "sets": 3, "reps": 12, "compound": False,
             "tip": "Arms overhead, full stretch", "track": "strength",
             "difficulty": "Beginner", "alternatives": ["tr01", "tr03", "tr05"]},
    "tr03": {"name": "Dumbbell Overhead Extension", "muscle": "Triceps", "equip": "Dumbbells",
             "equip_tags": ["dumbbells"], "sets": 3, "reps": 10, "compound": False,
             "tip": "Both hands on one dumbbell, full range", "track": "strength",
             "difficulty": "Beginner", "alternatives": ["tr02", "tr01", "tr04"]},
    "tr04": {"name": "Skull Crusher", "muscle": "Triceps", "equip": "Barbell",
             "equip_tags": ["barbell", "bench"], "sets": 3, "reps": 10, "compound": False,
             "tip": "Lower to forehead, elbows fixed", "track": "strength",
             "difficulty": "Intermediate", "alternatives": ["tr02", "tr03", "tr05"]},
    "tr05": {"name": "Close-Grip Bench Press", "muscle": "Triceps", "equip": "Barbell",
             "equip_tags": ["barbell", "bench"], "sets": 3, "reps": 8, "compound": True,
             "tip": "Hands inside shoulder width, elbows tucked", "track": "strength",
             "difficulty": "Intermediate", "alternatives": ["tr01", "tr04", "tr06"]},
    "tr06": {"name": "Dumbbell Kickback", "muscle": "Triceps", "equip": "Dumbbells",
             "equip_tags": ["dumbbells"], "sets": 3, "reps": 12, "compound": False,
             "tip": "Hinge forward, full lockout", "track": "strength",
             "difficulty": "Beginner", "alternatives": ["tr01", "tr02", "tr03"]},
    "tr07": {"name": "Tricep Dip", "muscle": "Triceps", "equip": "Bodyweight",
             "equip_tags": [], "sets": 3, "reps": 10, "compound": True,
             "tip": "Upright torso, elbows back", "track": "strength",
             "difficulty": "Intermediate", "alternatives": ["tr01", "tr05", "tr08"]},
    "tr08": {"name": "Diamond Push-Up", "muscle": "Triceps", "equip": "Bodyweight",
             "equip_tags": [], "sets": 3, "reps": 12, "compound": False,
             "tip": "Hands together, elbows tight", "track": "strength",
             "difficulty": "Intermediate", "alternatives": ["tr07", "tr01", "tr05"]},

    # ========================================================================
    # CORE EXERCISES (12)
    # ========================================================================
    "co01": {"name": "Plank", "muscle": "Core", "equip": "Bodyweight",
             "equip_tags": [], "sets": 3, "reps": 45, "compound": False,
             "tip": "Body in straight line, brace core", "track": "strength",
             "difficulty": "Beginner", "alternatives": ["co02", "co03", "co04"]},
    "co02": {"name": "Side Plank", "muscle": "Core", "equip": "Bodyweight",
             "equip_tags": [], "sets": 3, "reps": 30, "compound": False,
             "tip": "Stack feet, keep hips high", "track": "strength",
             "difficulty": "Beginner", "alternatives": ["co01", "co03", "co05"]},
    "co03": {"name": "Bicycle Crunch", "muscle": "Core", "equip": "Bodyweight",
             "equip_tags": [], "sets": 3, "reps": 20, "compound": False,
             "tip": "Elbow to opposite knee, slow and controlled", "track": "strength",
             "difficulty": "Beginner", "alternatives": ["co04", "co06", "co01"]},
    "co04": {"name": "Hanging Leg Raise", "muscle": "Core", "equip": "Bodyweight",
             "equip_tags": [], "sets": 3, "reps": 10, "compound": False,
             "tip": "Hang from bar, lift knees to chest", "track": "strength",
             "difficulty": "Intermediate", "alternatives": ["co05", "co03", "co07"]},
    "co05": {"name": "Ab Roller Rollout", "muscle": "Core", "equip": "Bodyweight",
             "equip_tags": [], "sets": 3, "reps": 10, "compound": False,
             "tip": "Kneeling, full extension", "track": "strength",
             "difficulty": "Intermediate", "alternatives": ["co04", "co06", "co07"]},
    "co06": {"name": "Crunch", "muscle": "Core", "equip": "Bodyweight",
             "equip_tags": [], "sets": 3, "reps": 20, "compound": False,
             "tip": "Lower back stays down, squeeze at top", "track": "strength",
             "difficulty": "Beginner", "alternatives": ["co03", "co01", "co07"]},
    "co07": {"name": "Russian Twist", "muscle": "Core", "equip": "Bodyweight",
             "equip_tags": [], "sets": 3, "reps": 20, "compound": False,
             "tip": "Feet off floor, rotate fully", "track": "strength",
             "difficulty": "Intermediate", "alternatives": ["co03", "co06", "co08"]},
    "co08": {"name": "Dead Bug", "muscle": "Core", "equip": "Bodyweight",
             "equip_tags": [], "sets": 3, "reps": 10, "compound": False,
             "tip": "Opposite arm and leg, back flat", "track": "strength",
             "difficulty": "Beginner", "alternatives": ["co01", "co03", "co06"]},
    "co09": {"name": "Mountain Climber", "muscle": "Core", "equip": "Bodyweight",
             "equip_tags": [], "sets": 3, "reps": 30, "compound": True,
             "tip": "Fast pace, core tight", "track": "strength",
             "difficulty": "Beginner", "alternatives": ["co03", "co06", "co10"]},
    "co10": {"name": "Cable Woodchop", "muscle": "Core", "equip": "Cable",
             "equip_tags": ["cable"], "sets": 3, "reps": 12, "compound": False,
             "tip": "Rotate through core, not arms", "track": "strength",
             "difficulty": "Intermediate", "alternatives": ["co07", "co03", "co11"]},
    "co11": {"name": "Turkish Get-Up", "muscle": "Core", "equip": "Dumbbells",
             "equip_tags": ["dumbbells"], "sets": 3, "reps": 5, "compound": True,
             "tip": "Full body movement, slow and controlled", "track": "strength",
             "difficulty": "Advanced", "alternatives": ["co04", "co05", "co01"]},
    "co12": {"name": "L-Sit Hold", "muscle": "Core", "equip": "Bodyweight",
             "equip_tags": [], "sets": 3, "reps": 15, "compound": False,
             "tip": "Parallel bars, legs straight", "track": "strength",
             "difficulty": "Advanced", "alternatives": ["co04", "co01", "co05"]},
}

# ============================================================================
# CARDIO EXERCISES (18)
# ============================================================================
CARDIO_EXERCISES = {
    "cr01": {"name": "Outdoor Run", "muscle": "Cardio", "equip": "Bodyweight",
             "equip_tags": [], "track": "cardio", "cardio_sub": "running", "sets": 1, "reps": 1,
             "tip": "Start easy, build pace gradually",
             "alternatives": ["cr02", "cr03"]},
    "cr02": {"name": "Treadmill Run", "muscle": "Cardio", "equip": "Machine",
             "equip_tags": ["machine"], "track": "cardio", "cardio_sub": "running", "sets": 1, "reps": 1,
             "tip": "Use incline for hill simulation",
             "alternatives": ["cr01", "cr03"]},
    "cr03": {"name": "Interval Sprints", "muscle": "Cardio", "equip": "Bodyweight",
             "equip_tags": [], "track": "cardio", "cardio_sub": "crossfit", "sets": 1, "reps": 1,
             "tip": "All-out effort on work intervals",
             "alternatives": ["cr01", "cr04"]},
    "cr04": {"name": "Tempo Run", "muscle": "Cardio", "equip": "Bodyweight",
             "equip_tags": [], "track": "cardio", "cardio_sub": "running", "sets": 1, "reps": 1,
             "tip": "Comfortably hard pace, 80-85% max HR",
             "alternatives": ["cr01", "cr05"]},
    "cr05": {"name": "Long Slow Distance", "muscle": "Cardio", "equip": "Bodyweight",
             "equip_tags": [], "track": "cardio", "cardio_sub": "running", "sets": 1, "reps": 1,
             "tip": "Easy conversational pace, build endurance",
             "alternatives": ["cr01", "cr04"]},
    "cr06": {"name": "Road Cycling", "muscle": "Cardio", "equip": "Bike",
             "equip_tags": ["bike"], "track": "cardio", "cardio_sub": "running", "sets": 1, "reps": 1,
             "tip": "Maintain steady cadence 80-100 RPM",
             "alternatives": ["cr07", "cr08"]},
    "cr07": {"name": "Stationary Bike", "muscle": "Cardio", "equip": "Machine",
             "equip_tags": ["machine"], "track": "cardio", "cardio_sub": "running", "sets": 1, "reps": 1,
             "tip": "Adjust resistance for intervals",
             "alternatives": ["cr06", "cr08"]},
    "cr08": {"name": "Spin Class", "muscle": "Cardio", "equip": "Machine",
             "equip_tags": ["machine"], "track": "cardio", "cardio_sub": "running", "sets": 1, "reps": 1,
             "tip": "Follow instructor, vary resistance",
             "alternatives": ["cr07", "cr06"]},
    "cr09": {"name": "Rowing Machine", "muscle": "Cardio", "equip": "Machine",
             "equip_tags": ["machine"], "track": "cardio", "cardio_sub": "crossfit", "sets": 1, "reps": 1,
             "tip": "Drive with legs first, then pull",
             "alternatives": ["cr07", "cr10"]},
    "cr10": {"name": "Jump Rope", "muscle": "Cardio", "equip": "Bodyweight",
             "equip_tags": [], "track": "cardio", "cardio_sub": "crossfit", "sets": 1, "reps": 1,
             "tip": "Light on feet, consistent rhythm",
             "alternatives": ["cr09", "cr03"]},
    "cr11": {"name": "Stair Climber", "muscle": "Cardio", "equip": "Machine",
             "equip_tags": ["machine"], "track": "cardio", "cardio_sub": "running", "sets": 1, "reps": 1,
             "tip": "Don't lean on handles, steady pace",
             "alternatives": ["cr07", "cr06"]},
    "cr12": {"name": "Elliptical", "muscle": "Cardio", "equip": "Machine",
             "equip_tags": ["machine"], "track": "cardio", "cardio_sub": "running", "sets": 1, "reps": 1,
             "tip": "Low impact, good for recovery",
             "alternatives": ["cr07", "cr09"]},
    "cr13": {"name": "Swimming", "muscle": "Cardio", "equip": "Bodyweight",
             "equip_tags": [], "track": "cardio", "cardio_sub": "running", "sets": 1, "reps": 1,
             "tip": "Full body, focus on stroke technique",
             "alternatives": ["cr01", "cr09"]},
    "cr14": {"name": "Burpees", "muscle": "Cardio", "equip": "Bodyweight",
             "equip_tags": [], "track": "cardio", "cardio_sub": "crossfit", "sets": 3, "reps": 10,
             "tip": "Explosive movement, full range",
             "alternatives": ["cr03", "cr10"]},
    "cr15": {"name": "Box Jump", "muscle": "Cardio", "equip": "Bodyweight",
             "equip_tags": [], "track": "cardio", "cardio_sub": "crossfit", "sets": 3, "reps": 8,
             "tip": "Soft landing, full hip extension",
             "alternatives": ["cr14", "cr03"]},
    "cr16": {"name": "Battle Ropes", "muscle": "Cardio", "equip": "Bodyweight",
             "equip_tags": [], "track": "cardio", "cardio_sub": "crossfit", "sets": 3, "reps": 30,
             "tip": "Alternating waves, core tight",
             "alternatives": ["cr14", "cr09"]},
    "cr17": {"name": "High Knees", "muscle": "Cardio", "equip": "Bodyweight",
             "equip_tags": [], "track": "cardio", "cardio_sub": "crossfit", "sets": 3, "reps": 30,
             "tip": "Knees to waist height, fast turnover",
             "alternatives": ["cr03", "cr14"]},
    "cr18": {"name": "Sled Push", "muscle": "Cardio", "equip": "Machine",
             "equip_tags": ["machine"], "track": "cardio", "cardio_sub": "crossfit", "sets": 4, "reps": 40,
             "tip": "Low stance, drive through legs",
             "alternatives": ["cr14", "cr15"]},
}

# ============================================================================
# WORKOUT SPLITS (Enhanced with 4-6 exercises per day)
# ============================================================================
WORKOUT_SPLITS = {
    "Build Muscle": {
        "name": "Hypertrophy Split",
        "days": {
            "Monday": {"focus": "Chest & Triceps", "muscles": ["Chest", "Triceps"],
                       "exercises": ["c01", "c02", "c03", "tr01", "tr05"]},
            "Tuesday": {"focus": "Back & Biceps", "muscles": ["Back", "Biceps"],
                        "exercises": ["b01", "b02", "b04", "bi02", "bi03"]},
            "Wednesday": {"focus": "Legs", "muscles": ["Legs"],
                          "exercises": ["l01", "l05", "l10", "l13", "l17"]},
            "Thursday": {"focus": "Shoulders & Core", "muscles": ["Shoulders", "Core"],
                         "exercises": ["s01", "s04", "s05", "co01", "co04"]},
            "Friday": {"focus": "Chest & Back", "muscles": ["Chest", "Back"],
                       "exercises": ["c01", "c05", "b01", "b04", "b12"]},
            "Saturday": {"focus": "Arms & Core", "muscles": ["Biceps", "Triceps", "Core"],
                         "exercises": ["bi02", "bi03", "tr01", "co03", "co06"]},
            "Sunday": {"focus": "Rest", "muscles": []},
        }
    },
    "Get Stronger": {
        "name": "Strength Split",
        "days": {
            "Monday": {"focus": "Heavy Chest", "muscles": ["Chest"],
                       "exercises": ["c01", "c02", "c10", "c05", "c07"]},
            "Tuesday": {"focus": "Heavy Back", "muscles": ["Back"],
                        "exercises": ["b08", "b01", "b04", "b02", "b12"]},
            "Wednesday": {"focus": "Heavy Legs", "muscles": ["Legs"],
                          "exercises": ["l01", "l04", "l10", "l13", "l17"]},
            "Thursday": {"focus": "Heavy Shoulders", "muscles": ["Shoulders"],
                         "exercises": ["s01", "s07", "s04", "s05", "s08"]},
            "Friday": {"focus": "Heavy Compound", "muscles": ["Chest", "Back", "Legs"],
                       "exercises": ["b08", "l01", "c01", "b01", "co01"]},
            "Saturday": {"focus": "Active Recovery", "muscles": ["Cardio"],
                         "exercises": ["cr01", "cr09", "cr10"]},
            "Sunday": {"focus": "Rest", "muscles": []},
        }
    },
    "Lose Weight": {
        "name": "Fat Loss Circuit",
        "days": {
            "Monday": {"focus": "Upper Body", "muscles": ["Chest", "Back", "Shoulders"],
                       "exercises": ["c01", "b01", "s01", "tr01", "co09"]},
            "Tuesday": {"focus": "HIIT Cardio", "muscles": ["Cardio"],
                        "exercises": ["cr14", "cr17", "cr03", "cr10"]},
            "Wednesday": {"focus": "Lower Body", "muscles": ["Legs"],
                          "exercises": ["l01", "l05", "l10", "l13", "l17"]},
            "Thursday": {"focus": "Active Recovery", "muscles": ["Cardio"],
                         "exercises": ["cr01", "cr09"]},
            "Friday": {"focus": "Full Body", "muscles": ["Chest", "Back", "Legs"],
                       "exercises": ["c01", "b01", "l01", "s01", "co09"]},
            "Saturday": {"focus": "HIIT Cardio", "muscles": ["Cardio"],
                         "exercises": ["cr14", "cr03", "cr16", "cr10"]},
            "Sunday": {"focus": "Rest", "muscles": []},
        }
    },
    "Run Faster": {
        "name": "Running Program",
        "days": {
            "Monday": {"focus": "Easy Run", "muscles": ["Cardio"],
                       "exercises": ["cr01", "co01", "co04"]},
            "Tuesday": {"focus": "Speed Work", "muscles": ["Cardio"],
                        "exercises": ["cr03", "cr17", "cr14"]},
            "Wednesday": {"focus": "Cross Training", "muscles": ["Legs"],
                          "exercises": ["l01", "l10", "l17", "co01"]},
            "Thursday": {"focus": "Tempo Run", "muscles": ["Cardio"],
                         "exercises": ["cr04", "cr10"]},
            "Friday": {"focus": "Rest", "muscles": []},
            "Saturday": {"focus": "Long Run", "muscles": ["Cardio"],
                         "exercises": ["cr05", "co01"]},
            "Sunday": {"focus": "Recovery", "muscles": ["Cardio"],
                       "exercises": ["cr01", "co01", "co02"]},
        }
    },
    "Cycle More": {
        "name": "Cycling Program",
        "days": {
            "Monday": {"focus": "Endurance Ride", "muscles": ["Cardio"],
                       "exercises": ["cr06", "l17"]},
            "Tuesday": {"focus": "Interval Training", "muscles": ["Cardio"],
                        "exercises": ["cr07", "cr14", "cr10"]},
            "Wednesday": {"focus": "Recovery Ride", "muscles": ["Cardio"],
                          "exercises": ["cr06"]},
            "Thursday": {"focus": "Hill Repeats", "muscles": ["Cardio"],
                         "exercises": ["cr07", "cr15", "l17"]},
            "Friday": {"focus": "Rest", "muscles": []},
            "Saturday": {"focus": "Long Ride", "muscles": ["Cardio"],
                         "exercises": ["cr06", "l17"]},
            "Sunday": {"focus": "Active Recovery", "muscles": ["Cardio"],
                       "exercises": ["cr09", "co01"]},
        }
    },
}

# ============================================================================
# BASELINE WEIGHTS BY EXPERIENCE
# ============================================================================
BASELINES = {
    "Beginner": {"barbell": 20, "dumbbell": 5, "machine": 15},
    "Regular": {"barbell": 50, "dumbbell": 14, "machine": 40},
    "Athlete": {"barbell": 80, "dumbbell": 24, "machine": 70},
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_all_exercises():
    """Get all exercises (strength + cardio) as a single dict."""
    all_ex = {}
    all_ex.update(STRENGTH_EXERCISES)
    all_ex.update(CARDIO_EXERCISES)
    return all_ex

def get_exercises_by_muscle(muscle):
    """Get exercises targeting a specific muscle group."""
    all_ex = get_all_exercises()
    return {eid: ex for eid, ex in all_ex.items() if ex.get("muscle") == muscle}

def get_exercises_by_equipment(equipment_list):
    """Filter exercises by available equipment."""
    all_ex = get_all_exercises()
    result = {}
    for eid, ex in all_ex.items():
        tags = ex.get("equip_tags", [])
        equip = ex.get("equip", "").lower()
        if not tags or equip in [e.lower() for e in equipment_list] or \
           any(t in [e.lower() for e in equipment_list] for t in tags):
            result[eid] = ex
    return result

def get_exercises_by_track(track):
    """Get exercises by track (strength or cardio)."""
    if track == "strength":
        return STRENGTH_EXERCISES
    elif track == "cardio":
        return CARDIO_EXERCISES
    return {}

def get_exercises_by_difficulty(difficulty):
    """Get exercises by difficulty level."""
    all_ex = get_all_exercises()
    return {eid: ex for eid, ex in all_ex.items() if ex.get("difficulty") == difficulty}

def get_compound_exercises():
    """Get all compound exercises."""
    all_ex = get_all_exercises()
    return {eid: ex for eid, ex in all_ex.items() if ex.get("compound")}

def get_exercises_by_profile(environment_mode):
    """Filter exercises by training environment."""
    all_ex = get_all_exercises()
    filtered = []
    for eid, ex in all_ex.items():
        tags = ex.get("equip_tags", [])
        equip = ex.get("equip", "").lower()
        if environment_mode == "home_gym":
            if not tags or equip in ["barbell", "dumbbells", "bodyweight", "bands"] or \
               any(t in ["barbell", "dumbbells", "bodyweight", "bands"] for t in tags):
                filtered.append({"id": eid, **ex})
        elif environment_mode == "cardio_only":
            if ex.get("track") == "cardio" or ex.get("muscle") == "Cardio":
                filtered.append({"id": eid, **ex})
        else:
            filtered.append({"id": eid, **ex})
    return filtered

def get_alternatives(exercise_id, available_equipment=None):
    """Get alternative exercises for equipment swapping."""
    all_ex = get_all_exercises()
    if exercise_id not in all_ex:
        return []
    ex = all_ex[exercise_id]
    alts = ex.get("alternatives", [])
    if available_equipment is None:
        return alts
    available = []
    for alt_id in alts:
        if alt_id in all_ex:
            alt_ex = all_ex[alt_id]
            tags = alt_ex.get("equip_tags", [])
            equip = alt_ex.get("equip", "").lower()
            if not tags or equip in [e.lower() for e in available_equipment] or \
               any(t in [e.lower() for e in available_equipment] for t in tags):
                available.append(alt_id)
    return available

def get_split_for_profile(profile_type, goal):
    """Get workout split based on profile and goal."""
    return WORKOUT_SPLITS.get(goal, WORKOUT_SPLITS.get("Build Muscle"))

def search_exercises(query):
    """Search exercises by name (case-insensitive)."""
    all_ex = get_all_exercises()
    query_lower = query.lower()
    return {eid: ex for eid, ex in all_ex.items() if query_lower in ex.get('name', '').lower()}

def get_muscle_groups():
    """Get all unique muscle groups."""
    all_ex = get_all_exercises()
    return sorted(set(ex.get('muscle', 'Other') for ex in all_ex.values()))

def get_equipment_types():
    """Get all unique equipment types."""
    all_ex = get_all_exercises()
    return sorted(set(ex.get('equip', 'Other') for ex in all_ex.values()))
