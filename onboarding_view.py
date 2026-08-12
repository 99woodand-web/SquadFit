# onboarding_view.py
# Onboarding screen for new users to set up their profile

from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty
import json
import os
_POPUP_BG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'popup_bg.png')

class OnboardingScreen(BoxLayout):
    """Onboarding screen for new users to set up their profile."""
    
    # User inputs
    user_name = StringProperty("")
    user_age = NumericProperty(30)
    user_weight = NumericProperty(75)
    user_height = NumericProperty(175)
    user_gender = StringProperty("male")
    user_goal = StringProperty("general_fitness")
    user_environment = StringProperty("commercial")
    user_experience = StringProperty("regular")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load existing profile if it exists
        self.load_existing_profile()
    
    def load_existing_profile(self):
        """Load existing profile data if available."""
        if os.path.exists("user_profile.json"):
            try:
                with open("user_profile.json", "r") as f:
                    profile = json.load(f)
                
                self.user_name = profile.get("name", "")
                self.user_age = profile.get("age", 30)
                self.user_weight = profile.get("weight_kg", 75)
                self.user_height = profile.get("height_cm", 175)
                self.user_gender = profile.get("gender", "male")
                self.user_goal = profile.get("goal", "general_fitness")
                self.user_environment = profile.get("environment", "commercial")
                
                # Update UI after widget is created
                self.update_sliders_from_profile()
                print(f"[Onboarding] Loaded existing profile: {self.user_name}")
            except Exception as e:
                print(f"[Onboarding] Error loading profile: {e}")
    
    def update_sliders_from_profile(self):
        """Update slider values from loaded profile."""
        try:
            if self.ids:
                self.ids.slider_age.value = self.user_age
                self.ids.slider_weight.value = self.user_weight
                self.ids.slider_height.value = self.user_height
                self.ids.txt_name.text = self.user_name
                self.update_labels()
        except Exception as e:
            print(f"[Onboarding] Error updating sliders: {e}")
    
    def update_labels(self):
        """Update all labels with current values."""
        try:
            if self.ids:
                self.ids.lbl_age.text = f"AGE: {int(self.user_age)} years"
                self.ids.lbl_weight.text = f"WEIGHT: {int(self.user_weight)} kg"
                self.ids.lbl_height.text = f"HEIGHT: {int(self.user_height)} cm"
        except Exception as e:
            pass
    
    def set_name(self, name):
        """Set user's name."""
        self.user_name = name.strip()
    
    def on_age_change(self, value):
        """Handle age slider change."""
        self.user_age = int(value)
        self.update_labels()
    
    def on_weight_change(self, value):
        """Handle weight slider change."""
        self.user_weight = float(value)
        self.update_labels()
    
    def on_height_change(self, value):
        """Handle height slider change."""
        self.user_height = float(value)
        self.update_labels()
    
    def set_gender(self, gender):
        """Set user's gender."""
        self.user_gender = gender
    
    def set_goal(self, goal):
        """Set user's fitness goal."""
        self.user_goal = goal
    
    def set_environment(self, env):
        """Set training environment."""
        self.user_environment = env
    
    def calculate_bmi(self):
        """Calculate BMI from current weight and height."""
        height_m = self.user_height / 100
        if height_m > 0:
            return self.user_weight / (height_m ** 2)
        return 0
    
    def calculate_bmr(self):
        """Calculate BMR using Mifflin-St Jeor equation."""
        if self.user_gender == "male":
            return (10 * self.user_weight) + (6.25 * self.user_height) - (5 * self.user_age) + 5
        else:
            return (10 * self.user_weight) + (6.25 * self.user_height) - (5 * self.user_age) - 161
    
    def complete_onboarding(self):
        """Save profile and navigate to calendar."""
        print(f"[Onboarding] Saving profile...")
        print(f"  Name: {self.user_name}")
        print(f"  Age: {self.user_age}")
        print(f"  Weight: {self.user_weight} kg")
        print(f"  Height: {self.user_height} cm")
        print(f"  Gender: {self.user_gender}")
        print(f"  Goal: {self.user_goal}")
        print(f"  Environment: {self.user_environment}")

        # Check if goal or environment changed
        old_profile = self._load_old_profile()
        new_profile = {
            "goal": self.user_goal,
            "environment": self.user_environment
        }

        from plan_regenerator import detect_goal_change, generate_change_preview
        changes = detect_goal_change(old_profile, new_profile)

        if changes["needs_regeneration"]:
            # Show confirmation dialog
            preview = generate_change_preview(changes)
            self._show_regeneration_dialog(changes, preview)
        else:
            # No changes - just save and navigate
            self.save_profile()
            self.navigate_to_calendar()
    
    def save_profile(self):
        """Save profile data to local file."""
        profile = {
            "name": self.user_name,
            "age": self.user_age,
            "weight_kg": self.user_weight,
            "height_cm": self.user_height,
            "gender": self.user_gender,
            "goal": self.user_goal,
            "environment": self.user_environment,
            "experience": self.user_experience,
            "bmi": self.calculate_bmi(),
            "bmr": self.calculate_bmr(),
            "onboarding_complete": True
        }
        
        try:
            with open("user_profile.json", "w") as f:
                json.dump(profile, f, indent=2)
            print("[Onboarding] Profile saved to user_profile.json")
        except Exception as e:
            print(f"[Onboarding] Error saving profile: {e}")
    
    def _load_old_profile(self):
        """Load the previous profile to detect changes."""
        import os
        try:
            if os.path.exists("user_profile.json"):
                with open("user_profile.json", "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _show_regeneration_dialog(self, changes, preview):
        """Show a confirmation dialog for plan regeneration."""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        from kivy.uix.label import Label
        from kivy.metrics import dp
        from kivy.graphics import Color, RoundedRectangle

        content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(20))

        # Title
        content.add_widget(Label(
            text="UPDATE WORKOUT PLAN?",
            font_size='18sp', bold=True,
            color=(0.0, 0.8, 1.0, 1),
            size_hint_y=None, height=dp(30)
        ))

        # Changes summary
        changes_text = "\n".join([f"  * {c}" for c in preview["changes"]])
        content.add_widget(Label(
            text=f"Your settings have changed:\n{changes_text}",
            font_size='13sp', color=(0.8, 0.8, 0.8, 1),
            halign='left', valign='top', size_hint_y=None, height=dp(50),
            text_size=(dp(280), None)
        ))

        # New plan preview
        new = preview["new"]
        content.add_widget(Label(
            text=f"New plan: {new['goal_name']}\n"
                 f"Equipment: {new['environment_name']}\n"
                 f"Exercises per day: {new['exercises_per_day']}\n"
                 f"Rep range: {new['rep_range']}\n"
                 f"Rest between sets: {new['rest_between_sets']}\n"
                 f"Cardio mix: {new['cardio_mix']}",
            font_size='12sp', color=(0.7, 0.7, 0.7, 1),
            halign='left', valign='top', size_hint_y=None, height=dp(100),
            text_size=(dp(280), None)
        ))

        # Buttons
        btn_box = BoxLayout(spacing=dp(15), size_hint_y=None, height=dp(50))

        def _tag(btn, color_tuple):
            btn._bg_color = color_tuple
            return btn

        def _refresh_canvas(inst):
            if hasattr(inst, '_bg_color'):
                inst.canvas.before.clear()
                with inst.canvas.before:
                    Color(*inst._bg_color)
                    RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(14)])

        btn_yes = Button(
            text="GENERATE PLAN", bold=True, font_size='12sp',
            background_normal='', background_down='', background_color=(0,0,0,0),
            color=(0.07, 0.07, 0.07, 1),
            text_size=(dp(130), None)
        )
        btn_yes = _tag(btn_yes, (0.2, 1.0, 0.6, 1))
        btn_yes.bind(pos=lambda inst, val: _refresh_canvas(inst))
        btn_yes.bind(size=lambda inst, val: _refresh_canvas(inst))
        btn_yes.bind(on_press=lambda x: self._confirm_regenerate(changes))
        btn_box.add_widget(btn_yes)

        btn_cancel = Button(
            text="KEEP CURRENT", bold=True, font_size='12sp',
            background_normal='', background_down='', background_color=(0,0,0,0),
            color=(0.8, 0.8, 0.8, 1),
            text_size=(dp(130), None)
        )
        btn_cancel = _tag(btn_cancel, (0.25, 0.25, 0.25, 1))
        btn_cancel.bind(pos=lambda inst, val: _refresh_canvas(inst))
        btn_cancel.bind(size=lambda inst, val: _refresh_canvas(inst))
        btn_cancel.bind(on_press=lambda x: self._cancel_regenerate())
        btn_box.add_widget(btn_cancel)

        content.add_widget(btn_box)

        self.regeneration_popup = Popup(
            title="", content=content,
            size_hint=(0.88, None), height=dp(340),
            auto_dismiss=True,
            background=_POPUP_BG,
            background_color=(0.1, 0.1, 0.1, 1)
        )
        self.regeneration_popup.open()

    def _confirm_regenerate(self, changes):
        """User confirmed - regenerate the plan and save."""
        if hasattr(self, 'regeneration_popup'):
            self.regeneration_popup.dismiss()

        # Save the new profile
        self.save_profile()

        # Generate and save the new plan
        from plan_regenerator import PlanRegenerator
        regenerator = PlanRegenerator()
        new_plan = regenerator.generate_new_plan(
            changes["new_goal"],
            changes["new_environment"],
            self.user_experience
        )
        regenerator.save_plan(new_plan)

        print(f"[Onboarding] Plan regenerated: {new_plan['goal_name']}")

        # Navigate to calendar
        self.navigate_to_calendar()

    def _cancel_regenerate(self):
        """User cancelled - keep current plan, just save settings."""
        if hasattr(self, 'regeneration_popup'):
            self.regeneration_popup.dismiss()

        self.save_profile()
        self.navigate_to_calendar()

    def navigate_to_calendar(self):
        """Navigate to calendar screen."""
        try:
            from kivy.app import App
            app = App.get_running_app()
            if hasattr(app, 'sm'):
                # Refresh calendar if it exists
                if hasattr(app.sm, 'get_screen'):
                    try:
                        cal_screen = app.sm.get_screen('calendar')
                        if hasattr(cal_screen, 'children') and cal_screen.children:
                            cal_widget = cal_screen.children[0]
                            if hasattr(cal_widget, 'reload_from_plan'):
                                cal_widget.reload_from_plan()
                    except:
                        pass
                app.sm.current = 'calendar'
                print("[Onboarding] Navigated to Calendar")
        except Exception as e:
            print(f"[Navigation Error] {e}")
    

