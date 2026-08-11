# calendar_view.py - Settings with background selector only
import os
import json
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, BooleanProperty, StringProperty
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from database_sync import SupabaseDataPipeline

def _refresh_canvas(inst):
    """Helper to redraw a button's rounded canvas after position/size changes."""
    if hasattr(inst, '_bg_color'):
        inst.canvas.before.clear()
        with inst.canvas.before:
            Color(*inst._bg_color)
            RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(14)])

class CalendarViewScreen(BoxLayout):
    selected_day_index = NumericProperty(0)
    shift_mode_active = BooleanProperty(False)
    workout_mode = StringProperty('ai')  # 'ai' or 'routine'

    # Enhanced weekly split with 4-6 exercises per day from exercise database
    weekly_routine_split = {
        0: {"name": "Chest & Triceps", "exercises": ["Flat Bench Press", "Incline Bench Press", "Dumbbell Flat Press", "Tricep Pushdown", "Close-Grip Bench Press"]},
        1: {"name": "Back & Biceps", "exercises": ["Barbell Bent-Over Row", "Dumbbell Single-Arm Row", "Lat Pulldown", "Dumbbell Curl", "Hammer Curl"]},
        2: {"name": "Legs", "exercises": ["Barbell Back Squat", "Dumbbell Bulgarian Split Squat", "Romanian Deadlift", "Hip Thrust", "Calf Raise (Standing)"]},
        3: {"name": "Shoulders & Core", "exercises": ["Military Press", "Dumbbell Lateral Raise", "Cable Face Pull", "Plank", "Hanging Leg Raise"]},
        4: {"name": "Chest & Back", "exercises": ["Flat Bench Press", "Cable Fly", "Barbell Bent-Over Row", "Lat Pulldown", "Dumbbell Reverse Fly"]},
        5: {"name": "Arms & Core", "exercises": ["Dumbbell Curl", "Hammer Curl", "Tricep Pushdown", "Bicycle Crunch", "Crunch"]},
        6: {"name": "Rest Day", "exercises": ["No training scheduled."]}
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_pipeline = SupabaseDataPipeline()
        Clock.schedule_once(self._init_calendar, 0.1)

    def _init_calendar(self, dt):
        from datetime import datetime
        # Load saved mode preference
        self._load_mode_preference()
        # Try to load from generated plan first
        self._load_from_generated_plan()
        today = datetime.now().weekday()
        self.load_selected_day_schedule(today)
        self.load_user_name()
        # Draw toggle buttons
        Clock.schedule_once(lambda dt: self._update_toggle_visuals(), 0.3)

    def _load_from_generated_plan(self):
        """Load weekly schedule from generated plan if available."""
        import json
        import os
        try:
            if os.path.exists('calendar_data.json'):
                with open('calendar_data.json', 'r') as f:
                    plan = json.load(f)
                if 'days' in plan:
                    # Convert plan days to our format
                    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    for i, day_name in enumerate(day_order):
                        if day_name in plan['days']:
                            day_data = plan['days'][day_name]
                            self.weekly_routine_split[i] = {
                                "name": day_data.get('name', 'Rest Day'),
                                "exercises": day_data.get('exercises', [])
                            }
                    print(f"[Calendar] Loaded plan: {plan.get('goal_name', 'Unknown')}")
        except Exception as e:
            print(f"[Calendar] Could not load generated plan: {e}")

    def reload_from_plan(self):
        """Reload the calendar from the generated plan."""
        self._load_from_generated_plan()
        from datetime import datetime
        today = datetime.now().weekday()
        self.load_selected_day_schedule(today)

    def _load_mode_preference(self):
        """Load workout mode preference from profile."""
        try:
            if os.path.exists("user_profile.json"):
                with open("user_profile.json", "r") as f:
                    profile = json.load(f)
                self.workout_mode = profile.get("workout_mode", "ai")
        except Exception:
            self.workout_mode = "ai"

    def set_workout_mode(self, mode):
        """Switch between AI Coach and My Routine mode."""
        self.workout_mode = mode
        # Update button visuals
        self._update_toggle_visuals()
        # Save preference
        try:
            profile = {}
            if os.path.exists("user_profile.json"):
                with open("user_profile.json", "r") as f:
                    profile = json.load(f)
            profile["workout_mode"] = mode
            with open("user_profile.json", "w") as f:
                json.dump(profile, f, indent=2)
        except Exception as e:
            print(f"[Calendar] Could not save mode: {e}")
        # Refresh the day display
        self.load_selected_day_schedule(self.selected_day_index)

    def _update_toggle_visuals(self):
        """Update the toggle button colours based on current mode."""
        from kivy.app import App
        app = App.get_running_app()
        accent = app.accent_color
        card = app.card_bg
        for btn_id, mode_name in [('btn_mode_ai', 'ai'), ('btn_mode_routine', 'routine')]:
            btn = self.ids.get(btn_id)
            if not btn:
                continue
            is_active = (self.workout_mode == mode_name)
            btn.color = (0.07, 0.07, 0.07, 1) if is_active else (0.6, 0.6, 0.6, 1)
            btn.canvas.before.clear()
            with btn.canvas.before:
                Color(*(accent if is_active else card))
                RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(20)])
            btn.bind(pos=lambda inst, val, a=accent, c=card, m=mode_name: self._redraw_toggle(inst, a, c, m))
            btn.bind(size=lambda inst, val, a=accent, c=card, m=mode_name: self._redraw_toggle(inst, a, c, m))

    def _redraw_toggle(self, inst, accent, card, mode_name):
        is_active = (self.workout_mode == mode_name)
        inst.canvas.before.clear()
        with inst.canvas.before:
            Color(*(accent if is_active else card))
            RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(20)])

    def _get_mode_display_data(self, day_index):
        """Get workout data based on the current mode."""
        if self.workout_mode == 'routine':
            # My Routine mode: show Saved Routines hint
            return {"name": "Saved Routines", "exercises": []}
        else:
            # AI mode: use the default AI-generated split
            return self.weekly_routine_split.get(day_index, {"name": "Rest Day", "exercises": []})

    def load_user_name(self):
        try:
            if os.path.exists("user_profile.json"):
                with open("user_profile.json", "r") as f:
                    profile = json.load(f)
                name = profile.get("name", "")
                if name and hasattr(self.ids, 'lbl_user_name'):
                    self.ids.lbl_user_name.text = f"Welcome, {name}"
        except:
            pass

    def open_settings_popup(self):
        """Open settings popup with background selector."""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        from kivy.uix.label import Label
        from kivy.metrics import dp
        from kivy.app import App

        app = App.get_running_app()
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(18))

        # Title
        content.add_widget(Label(text="SETTINGS", font_size='18sp', bold=True, color=(0.2, 1.0, 0.6, 1), size_hint_y=None, height=dp(30)))

        from kivy.graphics import Color, RoundedRectangle

        def make_rounded_btn(text, bg_color, txt_color, on_press_fn, height=dp(42)):
            btn = Button(text=text, bold=True, font_size='14sp', size_hint_y=None, height=height,
                         background_normal='', background_down='', background_color=(0,0,0,0), color=txt_color,
                         border=(0, 0, 0, 0))
            with btn.canvas.before:
                Color(*bg_color)
                RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(14)])
            btn.bind(pos=lambda inst, val: _refresh_canvas(inst))
            btn.bind(size=lambda inst, val: _refresh_canvas(inst))
            btn.bind(on_press=on_press_fn)
            return btn

        def _tag(btn, color_tuple):
            btn._bg_color = color_tuple
            return btn

        # Profile button
        btn_profile = _tag(make_rounded_btn("My Profile", (0.18, 0.18, 0.18, 1), (0.2, 1.0, 0.6, 1), lambda x: self._popup_dismiss_and_navigate('onboarding')), (0.18, 0.18, 0.18, 1))
        content.add_widget(btn_profile)

        btn_aicoach = _tag(make_rounded_btn("AI Coach", (0.18, 0.18, 0.18, 1), (0.0, 0.8, 1.0, 1), lambda x: self._popup_dismiss_and_navigate('aicoach')), (0.18, 0.18, 0.18, 1))
        content.add_widget(btn_aicoach)

        btn_routines = _tag(make_rounded_btn("Saved Routines", (0.18, 0.18, 0.18, 1), (0.0, 0.8, 1.0, 1), lambda x: self._show_template_loader()), (0.18, 0.18, 0.18, 1))
        content.add_widget(btn_routines)

        # Theme section
        content.add_widget(Label(text="BACKGROUND", font_size='12sp', bold=True, color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=dp(22)))

        # Background selector row
        bg_box = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(42))
        bg_charcoal_color = (0.2, 1.0, 0.6, 1) if app.theme_manager.current_bg == 'charcoal' else (0.18, 0.18, 0.18, 1)
        btn_charcoal = _tag(make_rounded_btn("Deep Charcoal", bg_charcoal_color, (0.07, 0.07, 0.07, 1) if app.theme_manager.current_bg == 'charcoal' else (0.8, 0.8, 0.8, 1), lambda x: self._set_theme_bg('charcoal')), bg_charcoal_color)
        bg_box.add_widget(btn_charcoal)

        bg_navy_color = (0.2, 1.0, 0.6, 1) if app.theme_manager.current_bg == 'navy' else (0.18, 0.18, 0.18, 1)
        btn_navy = _tag(make_rounded_btn("Deep Navy", bg_navy_color, (0.07, 0.07, 0.07, 1) if app.theme_manager.current_bg == 'navy' else (0.8, 0.8, 0.8, 1), lambda x: self._set_theme_bg('navy')), bg_navy_color)
        bg_box.add_widget(btn_navy)
        content.add_widget(bg_box)

        btn_logout = _tag(make_rounded_btn("Log Out", (0.18, 0.18, 0.18, 1), (1, 0.4, 0.4, 1), lambda x: self._show_logout_confirm(x)), (0.18, 0.18, 0.18, 1))
        content.add_widget(btn_logout)

        btn_close = _tag(make_rounded_btn("Close", (0.12, 0.12, 0.12, 1), (0.6, 0.6, 0.6, 1), lambda x: self.settings_popup.dismiss(), dp(38)), (0.12, 0.12, 0.12, 1))
        content.add_widget(btn_close)

        self.settings_popup = Popup(title="", content=content, size_hint=(0.85, None), height=dp(380), auto_dismiss=True, background_color=(0.1, 0.1, 0.1, 0.95), separator_height=0)
        self.settings_popup.open()

    def _set_theme_bg(self, bg_key):
        from kivy.app import App
        app = App.get_running_app()
        app.theme_manager.set_background(bg_key)
        if hasattr(self, 'settings_popup'):
            self.settings_popup.dismiss()
        self.open_settings_popup()

    def _popup_dismiss_and_navigate(self, screen_name):
        if hasattr(self, 'settings_popup'):
            self.settings_popup.dismiss()
        from kivy.app import App
        app = App.get_running_app()
        if hasattr(app, 'sm'):
            app.sm.current = screen_name

    def _show_template_loader(self):
        """Show the template selection popup."""
        if hasattr(self, 'settings_popup'):
            self.settings_popup.dismiss()

        from template_view import TemplateView
        tv = TemplateView()
        tv.show_load_popup(self._on_template_selected)

    def _on_template_selected(self, template):
        """Handle template selection - navigate to workout with template data."""
        from kivy.app import App
        app = App.get_running_app()
        if hasattr(app, 'sm'):
            workout_screen = app.sm.get_screen('workout')
            if hasattr(workout_screen, 'children') and workout_screen.children:
                workout_widget = workout_screen.children[0]
                if hasattr(workout_widget, 'load_exercises'):
                    # Extract exercise names from template
                    exercise_names = [e.get('exercise_name', e.get('exercise_id', '')) for e in template.exercises]
                    workout_widget.load_exercises(exercise_names, template.name)
            app.sm.current = 'workout'

    def _show_logout_confirm(self, btn):
        if hasattr(self, 'settings_popup'):
            self.settings_popup.dismiss()

        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        from kivy.uix.label import Label

        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
        content.add_widget(Label(text="LOG OUT", font_size='18sp', bold=True, color=(1, 0.4, 0.4, 1), size_hint_y=None, height=dp(30)))
        content.add_widget(Label(text="Are you sure you want to log out?", font_size='14sp', color=(1, 1, 1, 1), size_hint_y=None, height=dp(25)))

        btn_box = BoxLayout(spacing=dp(15), size_hint_y=None, height=dp(45))

        btn_yes = Button(text="YES, LOG OUT", bold=True, font_size='13sp', background_normal='', background_down='', background_color=(0,0,0,0), color=(1, 1, 1, 1))
        btn_yes._bg_color = (1, 0.4, 0.4, 1)
        with btn_yes.canvas.before:
            Color(1, 0.4, 0.4, 1)
            RoundedRectangle(pos=btn_yes.pos, size=btn_yes.size, radius=[dp(14)])
        btn_yes.bind(pos=lambda inst, val: _refresh_canvas(inst))
        btn_yes.bind(size=lambda inst, val: _refresh_canvas(inst))
        btn_yes.bind(on_press=lambda x: self._do_logout())
        btn_box.add_widget(btn_yes)

        btn_cancel = Button(text="CANCEL", bold=True, font_size='13sp', background_normal='', background_down='', background_color=(0,0,0,0), color=(0.07, 0.07, 0.07, 1))
        btn_cancel._bg_color = (0.2, 1.0, 0.6, 1)
        with btn_cancel.canvas.before:
            Color(0.2, 1.0, 0.6, 1)
            RoundedRectangle(pos=btn_cancel.pos, size=btn_cancel.size, radius=[dp(14)])
        btn_cancel.bind(pos=lambda inst, val: _refresh_canvas(inst))
        btn_cancel.bind(size=lambda inst, val: _refresh_canvas(inst))
        btn_box.add_widget(btn_cancel)

        content.add_widget(btn_box)

        self.logout_popup = Popup(title="", content=content, size_hint=(0.8, None), height=dp(180), auto_dismiss=True, background_color=(0.1, 0.1, 0.1, 0.95), separator_height=0)
        btn_cancel.bind(on_press=self.logout_popup.dismiss)
        self.logout_popup.open()

    def _do_logout(self):
        if hasattr(self, 'logout_popup'):
            self.logout_popup.dismiss()
        from kivy.app import App
        app = App.get_running_app()
        if hasattr(app, 'logout'):
            app.logout()

    def load_selected_day_schedule(self, day_index):
        if self.shift_mode_active:
            self.execute_routine_reschedule(day_index)
            return

        self.selected_day_index = day_index
        day_data = self._get_mode_display_data(day_index)
        self.ids.lbl_routine_name.text = day_data["name"]

        exercise_string = ""
        for exercise in day_data["exercises"]:
            exercise_string += f"- {exercise}\n"
        self.ids.lbl_routine_exercises_preview.text = exercise_string
        self._highlight_day(day_index)

    def _highlight_day(self, day_index):
        try:
            day_buttons = ['btn_mon', 'btn_tue', 'btn_wed', 'btn_thu', 'btn_fri', 'btn_sat', 'btn_sun']
            for i, btn_name in enumerate(day_buttons):
                if hasattr(self.ids, btn_name):
                    btn = self.ids[btn_name]
                    btn.state = 'down' if i == day_index else 'normal'
        except:
            pass

    def activate_quick_shift_mode(self):
        self.shift_mode_active = True
        self.ids.lbl_target_split_title.text = "SELECT TARGET DAY NODE ABOVE TO MOVE"

    def execute_routine_reschedule(self, target_day_index):
        old_day = self.selected_day_index
        routine_to_move = self.weekly_routine_split[old_day]
        target_day_original_content = self.weekly_routine_split[target_day_index]
        self.weekly_routine_split[target_day_index] = routine_to_move
        self.weekly_routine_split[old_day] = target_day_original_content
        self.shift_mode_active = False
        self.ids.lbl_target_split_title.text = "TODAY'S SCHEDULED SPLIT"
        self.load_selected_day_schedule(target_day_index)

    def initiate_active_gym_session(self):
        if hasattr(self, 'settings_popup'):
            self.settings_popup.dismiss()
        if hasattr(self, 'logout_popup'):
            self.logout_popup.dismiss()

        day_data = self._get_mode_display_data(self.selected_day_index)

        if "Rest" in day_data.get("name", ""):
            self.ids.lbl_target_split_title.text = "REST DAY - No workout scheduled!"
            return

        self.current_workout = day_data
        self._navigate_to_workout(day_data)

    def _navigate_to_workout(self, day_data):
        try:
            from kivy.app import App
            app = App.get_running_app()

            if hasattr(app, 'sm'):
                workout_screen = app.sm.get_screen('workout')

                if hasattr(workout_screen, 'children') and workout_screen.children:
                    workout_widget = workout_screen.children[0]

                    if hasattr(workout_widget, 'load_exercises'):
                        exercises = day_data.get('exercises', [])
                        name = day_data.get('name', 'Workout')
                        workout_widget.load_exercises(exercises, name)

                app.sm.current = 'workout'
        except Exception as e:
            print(f"[Calendar ERROR] {e}")

    def quick_start_last_workout(self):
        """Load the last completed workout and start it immediately."""
        import os, json
        from datetime import datetime

        completions_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'workout_completions.json')
        try:
            if not os.path.exists(completions_path):
                self.ids.lbl_target_split_title.text = "No previous workouts yet!"
                return

            with open(completions_path, 'r') as f:
                content = f.read().strip()
                if not content:
                    self.ids.lbl_target_split_title.text = "No previous workouts yet!"
                    return
                completions = json.loads(content)

            if not isinstance(completions, list) or not completions:
                self.ids.lbl_target_split_title.text = "No previous workouts yet!"
                return

            # Find the most recent completion that has exercises
            last = None
            for c in reversed(completions):
                if c.get('exercises'):
                    last = c
                    break

            # If no exercises in completions, try to find them from workout_history
            if not last:
                last = completions[-1]  # Use most recent completion
                history_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'workout_history.json')
                if os.path.exists(history_path):
                    with open(history_path, 'r') as f:
                        history = json.load(f)
                    if isinstance(history, dict):
                        # Try each completion date from newest to oldest
                        found = False
                        for comp in reversed(completions):
                            target_date = comp.get('date', '')[:10]
                            exercise_names = []
                            for ex_name, sessions in history.items():
                                for s in sessions:
                                    if s.get('date', '')[:10] == target_date:
                                        exercise_names.append(ex_name)
                                        break
                            if exercise_names:
                                last = comp
                                found = True
                                break
                        if not found:
                            self.ids.lbl_target_split_title.text = "No exercise data found!"
                            return
                    else:
                        self.ids.lbl_target_split_title.text = "No exercise data found!"
                        return
                else:
                    self.ids.lbl_target_split_title.text = "No exercise data found!"
                    return
            else:
                exercise_names = last['exercises']
                workout_name = last.get('workout_name', 'Last Workout')

            # Navigate to workout screen
            from kivy.app import App
            app = App.get_running_app()
            if hasattr(app, 'sm'):
                workout_screen = app.sm.get_screen('workout')
                if hasattr(workout_screen, 'children') and workout_screen.children:
                    workout_widget = workout_screen.children[0]
                    if hasattr(workout_widget, 'load_exercises'):
                        workout_widget.load_exercises(exercise_names, f"Quick: {workout_name}")
                app.sm.current = 'workout'

        except Exception as e:
            print(f"[Calendar] Quick Start error: {e}")
            self.ids.lbl_target_split_title.text = "Error loading last workout!"

    def go_to_progress(self):
        """Navigate to the progress tracking screen."""
        try:
            from kivy.app import App
            app = App.get_running_app()
            if hasattr(app, 'sm'):
                app.sm.current = 'progress'
        except Exception as e:
            print(f"[Navigation Error] {e}")
