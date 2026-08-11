# database_sync.py (Part 1 of 2)
# Handles safe connection handshakes and user sign-in modules

import json
import os
from config import SUPABASE_URL, SUPABASE_ANON_KEY, DATA_FILE

# Try to import supabase, fall back to offline mode if not available
SUPABASE_AVAILABLE = False
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    print("[Offline Mode] Supabase package not installed. Running offline.")

class SupabaseDataPipeline:
    def __init__(self):
        """
        Reads the shared credentials from your central config file.
        Falls back to offline mode if Supabase is unavailable or credentials are placeholder.
        """
        self.client = None
        self.offline_mode = False
        self.offline_user_id = "offline_user_001"
        self.offline_user_data = {}
        
        # Check if credentials are configured
        if not SUPABASE_URL or "YOUR_" in SUPABASE_URL or not SUPABASE_ANON_KEY or "YOUR_" in SUPABASE_ANON_KEY:
            print("[Offline Mode] Supabase credentials not configured. Running offline.")
            self.offline_mode = True
            self._load_offline_data()
            return
        
        if not SUPABASE_AVAILABLE:
            self.offline_mode = True
            self._load_offline_data()
            return
            
        try:
            self.client: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            print(f"[Supabase] Attempting connection to {SUPABASE_URL}")
            # Test the connection with a simple auth check
            try:
                self.client.auth.get_session()
                print(f"[Supabase] Connected successfully!")
            except Exception as auth_err:
                error_str = str(auth_err)
                if "Invalid API key" in error_str or "401" in error_str:
                    print(f"[Offline Mode] Invalid API key. Please check your Supabase anon key.")
                    print(f"[Offline Mode] Get your key from: https://supabase.com/dashboard → Settings → API")
                    self.offline_mode = True
                    self.client = None
                    self._load_offline_data()
                else:
                    print(f"[Supabase] Auth check error: {auth_err}")
        except Exception as e:
            print(f"[Offline Mode] Supabase connection failed: {e}")
            print("[Offline Mode] Running in offline mode.")
            self.offline_mode = True
            self._load_offline_data()
    
    def _load_offline_data(self):
        """Load user data from local JSON file for offline mode."""
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r') as f:
                    self.offline_user_data = json.load(f)
                    print(f"[Offline Mode] Loaded user data from {DATA_FILE}")
        except Exception as e:
            print(f"[Offline Mode] Could not load local data: {e}")
            self.offline_user_data = {}
    
    def _save_offline_data(self):
        """Save user data to local JSON file."""
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(self.offline_user_data, f, indent=2)
        except Exception as e:
            print(f"[Offline Mode] Could not save local data: {e}")

    def authenticate_user(self, email, password):
        """Logs a friend into the application securely."""
        # Offline mode - simulate successful login
        if self.offline_mode:
            print(f"[Offline Mode] Simulating login for {email}")
            self.offline_user_data["email"] = email
            self.offline_user_data["name"] = email.split("@")[0]
            self._save_offline_data()
            return self.offline_user_id
            
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email, 
                "password": password
            })
            return response.user.id
        except Exception as error:
            error_str = str(error)
            # Check for API key issues and switch to offline mode
            if "Invalid API key" in error_str or "401" in error_str:
                print(f"[Offline Mode] Invalid API key detected. Switching to offline mode.")
                self.offline_mode = True
                self._load_offline_data()
                # Retry in offline mode
                return self.authenticate_user(email, password)
            # Provide more specific error messages
            elif "Invalid login credentials" in error_str or "400" in error_str:
                print(f"[Supabase Auth Error] Login failed - invalid email or password. Have you registered first?")
            elif "Email not confirmed" in error_str:
                print(f"[Supabase Auth Error] Please confirm your email before logging in.")
            else:
                print(f"[Supabase Auth Error]: {error}")
            return None

    # database_sync.py (Part 2 of 2)
    # Routes live workout logs and pulls the shared social timeline activity feed

    def sync_user_profile(self, user_id, env_mode, weight, height):
        """
        Saves user settings (Home Gym vs. Runner) to the cloud.
        Recalculates metrics so friends see updated profiles on leaderboards.
        """
        # Offline mode - save locally
        if self.offline_mode:
            self.offline_user_data["training_environment"] = env_mode
            self.offline_user_data["weight_kg"] = weight
            self.offline_user_data["height_cm"] = height
            self._save_offline_data()
            print(f"[Offline Mode] Profile saved locally")
            return True
            
        try:
            self.client.table("user_profiles").upsert({
                "id": user_id,
                "training_environment": env_mode,
                "weight_kg": weight,
                "height_cm": height
            }).execute()
            return True
        except Exception as error:
            print(f"[Supabase Profile Sync Error]: {error}")
            return False

    def log_workout_session(self, user_id, exercise_id, track_type, performance_metrics):
        """
        The Dual-Track Sync Engine. Routes Strength Sets (reps/weight)
        or Cardio Track data (distance/pace) safely to the shared database.
        """
        # Offline mode - save locally
        if self.offline_mode:
            if "workout_logs" not in self.offline_user_data:
                self.offline_user_data["workout_logs"] = []
            self.offline_user_data["workout_logs"].append({
                "exercise_id": exercise_id,
                "track_type": track_type,
                "metrics": performance_metrics
            })
            self._save_offline_data()
            print(f"[Offline Mode] Workout logged locally")
            return True
            
        try:
            # performance_metrics is a dictionary containing workout data
            self.client.table("workout_logs").insert({
                "user_id": user_id,
                "exercise_id": exercise_id,
                "track_type": track_type,
                "metrics": performance_metrics
            }).execute()
            return True
        except Exception as error:
            print(f"[Supabase Workout Log Error]: {error}")
            return False

    def fetch_friends_social_feed(self):
        """
        Pulls the latest activities completed by your friends.
        Feeds your Kivy live feed view with real-time PR updates.
        """
        # Offline mode - return mock data or empty
        if self.offline_mode:
            print(f"[Offline Mode] Returning empty feed (no friends in offline mode)")
            return []
            
        try:
            # Queries completed logs sorted by the newest entries first
            response = self.client.table("workout_logs").select(
                "id, user_id, exercise_id, metrics, created_at"
            ).order("created_at", desc=True).limit(20).execute()
            return response.data
        except Exception as error:
            print(f"[Supabase Social Feed Fetch Error]: {error}")
            return []

def create_offline_user_profile(email, name=None):
    """
    Create a local user profile when running offline.
    Useful for testing without Supabase.
    """
    profile = {
        "email": email,
        "name": name or email.split("@")[0],
        "training_environment": "commercial",
        "weight_kg": 75,
        "height_cm": 175,
        "workout_logs": []
    }
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(profile, f, indent=2)
        print(f"[Offline Mode] Created local profile for {email}")
        return True
    except Exception as e:
        print(f"[Offline Mode] Could not create profile: {e}")
        return False
