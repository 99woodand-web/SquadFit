"""
CHAMELEON GYM - Configuration Module
Supabase credentials and app settings
"""

# ============================================================================
#  SUPABASE CONFIGURATION
# ============================================================================
# Get your credentials from: https://supabase.com/dashboard → Settings → API
# The anon key should start with 'eyJ' (it's a JWT token)
#
# If you leave these as placeholders, the app runs in OFFLINE MODE
#
SUPABASE_URL = "https://axyfoyzmbzsldobikqnv.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF4eWZveXptYnpzbGRvYmlrcW52Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODYxMjE4OTMsImV4cCI6MjEwMTY5Nzg5M30.rPZlcNroNzVTeuiJ0Q10yCl-jBTaXBfFiAO_S4P7NUU"  # Replace with your real anon key
SUPABASE_KEY = SUPABASE_ANON_KEY  # Alias for database_sync.py compatibility

# ============================================================================
#  APP SETTINGS
# ============================================================================
APP_NAME = "Chameleon Gym"
APP_VERSION = "1.0.0"

# File paths
DATA_FILE = "user_data.json"
HISTORY_FILE = "workout_history.json"
CALENDAR_FILE = "calendar_data.json"
EXERCISE_DB_FILE = "exercises.json"

# ============================================================================
#  ATHLETE PROFILES
# ============================================================================
PROFILE_TYPES = {
    "runner": {
        "name": "Runner/Cyclist",
        "icon": "run",
        "equipment": ["bodyweight", "heart_rate_monitor", "gps_watch"],
        "focus": ["cardio", "endurance", "speed"],
        "tracks": ["cardio"],
    },
    "commercial_gym": {
        "name": "Commercial Gym",
        "icon": "dumbbell",
        "equipment": ["barbell", "dumbbells", "cables", "machine", "bench"],
        "focus": ["strength", "hypertrophy", "power"],
        "tracks": ["strength"],
    },
    "home_gym": {
        "name": "Home Gym",
        "icon": "home",
        "equipment": ["barbell", "dumbbells", "bench", "bodyweight"],
        "focus": ["strength", "maintenance"],
        "tracks": ["strength"],
        "restrictions": True,  # Only show exercises matching owned equipment
    },
}

# Home gym equipment flags
HOME_EQUIPMENT_FLAGS = {
    "barbell": False,
    "dumbbells": False,
    "bench": False,
    "pull_up_bar": False,
    "ab_roller": False,
    "resistance_bands": False,
}

# ============================================================================
#  VISUAL PALETTE
# ============================================================================
COLORS = {
    "bg": "#0D0D0D",        # Deep charcoal background
    "surface": "#1A1A1A",   # Surface
    "surface2": "#252525",  # Elevated surface
    "surface3": "#333333",  # Highest surface
    "text": "#FFFFFF",      # Primary text
    "text2": "#A0A0A0",    # Secondary text
    "text3": "#666666",    # Tertiary text
    "accent": "#00FF87",    # Neon volt green
    "accent2": "#00E676",   # Accent variant
    "success": "#00E676",   # Success green
    "error": "#FF5252",     # Error red
    "warning": "#FFB74D",   # Warning orange
    "info": "#42A5F5",      # Info blue
    "cyan": "#26C6DA",      # Cyan accent
}

# ============================================================================
#  RECOVERY TIMES (hours)
# ============================================================================
RECOVERY_TIMES = {
    "Chest": 72, "Back": 72, "Legs": 72, "Shoulders": 48,
    "Biceps": 48, "Triceps": 48, "Calves": 48, "Core": 48,
    "Cardio": 24, "Glutes": 48, "Hip Flexors": 24,
}

# ============================================================================
#  MUSCLE GROUPS
# ============================================================================
MUSCLE_GROUPS = [
    "Chest", "Back", "Shoulders", "Biceps", "Triceps",
    "Legs", "Calves", "Core", "Cardio", "Glutes"
]

# ============================================================================
#  EQUIPMENT TAGS
# ============================================================================
EQUIPMENT_TAGS = [
    "Barbell", "Dumbbells", "Cables", "Machine", "Bands",
    "Bodyweight", "Treadmill", "Rower", "Bike", "Bench",
    "Pull-Up Bar", "Ab Roller", "Kettlebell"
]
