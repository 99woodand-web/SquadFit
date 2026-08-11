# login_view.py - KivyMD Login
import os
import re
import json
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty, StringProperty
from database_sync import SupabaseDataPipeline

class LoginScreenView(BoxLayout):
    auth_lock = BooleanProperty(False)
    status_message = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.network_pipeline = SupabaseDataPipeline()
        if self.network_pipeline.offline_mode:
            self.status_message = "OFFLINE MODE - All data saved locally"
            if hasattr(self.ids, 'lbl_login_status'):
                self.ids.lbl_login_status.text = "[OFFLINE MODE] Data will be saved locally"

    def validate_password_strength(self, password):
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        if not any(c.isupper() for c in password):
            return False, "Password must contain an uppercase letter"
        if not any(c.islower() for c in password):
            return False, "Password must contain a lowercase letter"
        if not any(c.isdigit() for c in password):
            return False, "Password must contain a number"
        return True, "Password is strong"

    def is_valid_email(self, email_string):
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(email_pattern, email_string.strip()))

    def execute_database_sign_in(self):
        if self.auth_lock:
            return

        email = self.ids.txt_email.text.strip()
        password = self.ids.txt_password.text.strip()

        if not email or not password:
            self.ids.lbl_login_status.text = "Error: Please enter email and password."
            return

        if not self.is_valid_email(email):
            self.ids.lbl_login_status.text = "Error: Please enter a valid email address."
            return

        self.auth_lock = True
        self.ids.lbl_login_status.text = "Connecting to server..."

        user_id = self.network_pipeline.authenticate_user(email, password)

        if user_id:
            self.ids.lbl_login_status.text = "Login successful! Loading..."
            self.save_login_state(email, user_id)
            self.transition_to_main_app(user_id)
        else:
            self.auth_lock = False
            if self.network_pipeline.offline_mode:
                self.ids.lbl_login_status.text = "Offline login failed.\nPlease try again."
            else:
                self.ids.lbl_login_status.text = "Invalid email or password.\nPlease try CREATE ACCOUNT first."

    def save_login_state(self, email, user_id):
        try:
            login_state = {"logged_in": True, "email": email, "user_id": user_id}
            with open("login_state.json", "w") as f:
                json.dump(login_state, f)
        except Exception as e:
            print(f"[Login] Error saving state: {e}")

    def execute_database_registration(self):
        if self.auth_lock:
            return

        email = self.ids.txt_email.text.strip()
        password = self.ids.txt_password.text.strip()

        if not email:
            self.ids.lbl_login_status.text = "Error: Please enter an email address."
            return

        if not self.is_valid_email(email):
            self.ids.lbl_login_status.text = "Error: Please enter a valid email address."
            return

        is_strong, message = self.validate_password_strength(password)
        if not is_strong:
            self.ids.lbl_login_status.text = f"Error: {message}"
            return

        self.auth_lock = True

        if self.network_pipeline.offline_mode:
            self.ids.lbl_login_status.text = "Creating local profile..."
            from database_sync import create_offline_user_profile
            success = create_offline_user_profile(email, email.split("@")[0])
            if success:
                self.ids.lbl_login_status.text = "Account created! (Offline Mode)"
                user_id = self.network_pipeline.authenticate_user(email, password)
                if user_id:
                    self.transition_to_main_app(user_id)
            else:
                self.ids.lbl_login_status.text = "Failed to create account."
            self.auth_lock = False
            return

        self.ids.lbl_login_status.text = "Creating your account..."

        try:
            response = self.network_pipeline.client.auth.sign_up({
                "email": email,
                "password": password
            })

            if response.user:
                self.ids.lbl_login_status.text = "Account created! Let's set up your profile..."
                self.network_pipeline.sync_user_profile(response.user.id, "commercial", 75, 175)
                self.transition_to_onboarding()
            else:
                self.ids.lbl_login_status.text = "Registration error. Please try again."
        except Exception as error:
            error_str = str(error)
            if "already registered" in error_str.lower() or "already exists" in error_str.lower():
                self.ids.lbl_login_status.text = "Email already registered.\nTry logging in instead."
            else:
                self.ids.lbl_login_status.text = "Registration failed.\nPlease try again."
        finally:
            self.auth_lock = False

    def transition_to_main_app(self, user_id):
        if os.path.exists("user_profile.json"):
            try:
                with open("user_profile.json", "r") as f:
                    profile = json.load(f)
                if profile.get("onboarding_complete"):
                    self._navigate('calendar')
                else:
                    self._navigate('onboarding')
            except:
                self._navigate('onboarding')
        else:
            self._navigate('onboarding')

    def transition_to_onboarding(self):
        self._navigate('onboarding')

    def _navigate(self, screen_name):
        try:
            from kivy.app import App
            app = App.get_running_app()
            if hasattr(app, 'sm'):
                app.sm.current = screen_name
        except Exception as e:
            print(f"[Navigation ERROR] {e}")
