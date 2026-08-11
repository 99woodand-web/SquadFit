# settings_view.py - Background theme only
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty
from kivy.clock import Clock

try:
    from config import SUPABASE_URL, SUPABASE_ANON_KEY
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


class SettingsScreen(BoxLayout):
    user_environment = StringProperty("commercial")
    user_weight = NumericProperty(75)
    user_height_cm = NumericProperty(175)
    user_age = NumericProperty(30)
    user_gender = StringProperty("male")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_client = None
        if SUPABASE_AVAILABLE:
            try:
                self.db_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            except Exception as e:
                print(f"Supabase connection failed: {e}")

        self.recalculate_biometrics()
        Clock.schedule_once(self._init_theme_buttons, 0.2)

    def _init_theme_buttons(self, dt):
        from kivy.app import App
        app = App.get_running_app()
        if hasattr(app, 'theme_manager'):
            tm = app.theme_manager
            if hasattr(self.ids, 'btn_bg_charcoal'):
                self.ids.btn_bg_charcoal.state = 'down' if tm.current_bg == 'charcoal' else 'normal'
                self.ids.btn_bg_navy.state = 'down' if tm.current_bg == 'navy' else 'normal'

    def set_background_theme(self, bg_key):
        from kivy.app import App
        app = App.get_running_app()
        if hasattr(app, 'theme_manager'):
            app.theme_manager.set_background(bg_key)
            self.ids.btn_bg_charcoal.state = 'down' if bg_key == 'charcoal' else 'normal'
            self.ids.btn_bg_navy.state = 'down' if bg_key == 'navy' else 'normal'
            if hasattr(self.ids, 'lbl_sync_status'):
                self.ids.lbl_sync_status.text = f"Background: {bg_key.title()}"

    def update_profile_environment(self, chosen_env):
        self.user_environment = chosen_env
        if hasattr(self.ids, 'lbl_sync_status'):
            self.ids.lbl_sync_status.text = f"Environment: {chosen_env}"
        if hasattr(self.ids, 'btn_commercial'):
            self.ids.btn_commercial.state = 'down' if chosen_env == 'commercial' else 'normal'
        if hasattr(self.ids, 'btn_home'):
            self.ids.btn_home.state = 'down' if chosen_env == 'home_gym' else 'normal'
        if hasattr(self.ids, 'btn_cardio'):
            self.ids.btn_cardio.state = 'down' if chosen_env == 'cardio_only' else 'normal'
        self._save_local()

    def on_weight_slider_change(self, current_value):
        self.user_weight = current_value
        self.recalculate_biometrics()
        self._save_local()

    def on_height_change(self, height_cm):
        self.user_height_cm = height_cm
        self.recalculate_biometrics()
        self._save_local()

    def on_age_change(self, age):
        self.user_age = age
        self.recalculate_biometrics()
        self._save_local()

    def on_gender_change(self, gender):
        self.user_gender = gender
        self.recalculate_biometrics()
        self._save_local()

    def recalculate_biometrics(self):
        height_meters = self.user_height_cm / 100.0
        if height_meters > 0:
            bmi_score = self.user_weight / (height_meters ** 2)
            bmi_category = self._get_bmi_category(bmi_score)
            if hasattr(self.ids, 'lbl_bmi'):
                self.ids.lbl_bmi.text = f"BMI: {bmi_score:.1f} ({bmi_category})"

        if self.user_gender == "male":
            bmr = (10 * self.user_weight) + (6.25 * self.user_height_cm) - (5 * self.user_age) + 5
        else:
            bmr = (10 * self.user_weight) + (6.25 * self.user_height_cm) - (5 * self.user_age) - 161

        activity_multiplier = 1.375
        tdee_score = bmr * activity_multiplier

        if hasattr(self.ids, 'lbl_tdee'):
            self.ids.lbl_tdee.text = f"TDEE: {int(tdee_score)} kcal"

    def _get_bmi_category(self, bmi):
        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal"
        elif bmi < 30:
            return "Overweight"
        else:
            return "Obese"

    def _save_local(self):
        import json
        settings = {
            "user_environment": self.user_environment,
            "user_weight": self.user_weight,
            "user_height_cm": self.user_height_cm,
            "user_age": self.user_age,
            "user_gender": self.user_gender,
        }
        try:
            with open("settings.json", "w") as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def load_local_settings(self):
        import json
        import os
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as f:
                    settings = json.load(f)
                self.user_environment = settings.get("user_environment", "commercial")
                self.user_weight = settings.get("user_weight", 75)
                self.user_height_cm = settings.get("user_height_cm", 175)
                self.user_age = settings.get("user_age", 30)
                self.user_gender = settings.get("user_gender", "male")
                self.recalculate_biometrics()
                return True
        except Exception as e:
            print(f"Failed to load settings: {e}")
        return False

    def get_available_equipment(self):
        equipment_map = {
            "commercial": ["Barbell", "Dumbbells", "Cables", "Machine", "Bands", "Treadmill", "Rower", "Bike", "Bench"],
            "home_gym": ["Barbell", "Dumbbells", "Bench", "Bodyweight", "Ab Roller", "Bands"],
            "cardio_only": ["Bodyweight", "Treadmill", "Bike", "Rower"],
        }
        return equipment_map.get(self.user_environment, [])

    def get_profile_type(self):
        profile_map = {
            "commercial": "commercial_gym",
            "home_gym": "home_gym",
            "cardio_only": "runner",
        }
        return profile_map.get(self.user_environment, "commercial_gym")
