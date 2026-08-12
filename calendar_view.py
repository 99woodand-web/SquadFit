# calendar_view.py - Settings with background selector only
import os
import json
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, BooleanProperty, StringProperty
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from database_sync import SupabaseDataPipeline

import os
_POPUP_BG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'popup_bg.png')

def _refresh_canvas(inst):
    """Helper to redraw a button's rounded canvas after position/size changes."""
    if hasattr(inst, '_bg_color'):
        inst.canvas.before.clear()
        with inst.canvas.before:
            Color(*inst._bg_color)
            RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(14)])

class CalendarViewScreen(BoxLayout):
    selected_day_index = NumericProperty(-1)  # -1 = not yet set; _init_calendar sets to today
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
        # Ensure starter templates exist for "My Program" mode
        from template_manager import TemplateManager
        TemplateManager().ensure_defaults()
        # Load saved mode preference
        self._load_mode_preference()
        # Try to load from generated plan first
        self._load_from_generated_plan()
        today = datetime.now().weekday()
        self.selected_day_index = today
        self.load_selected_day_schedule(today)
        self.load_user_name()
        # Ensure today's button is highlighted after layout settles
        Clock.schedule_once(lambda dt: self._highlight_day(today), 0.5)
        # Draw toggle buttons
        Clock.schedule_once(lambda dt: self._update_toggle_visuals(), 0.3)
        # Update completion dots on day buttons — delay to let layout settle
        Clock.schedule_once(lambda dt: self._update_completion_dots(), 1.0)
        # Redraw dots whenever any day button moves/resizes
        day_button_ids = ['btn_mon', 'btn_tue', 'btn_wed', 'btn_thu', 'btn_fri', 'btn_sat', 'btn_sun']
        for btn_name in day_button_ids:
            btn = self.ids.get(btn_name)
            if btn:
                btn.bind(pos=lambda inst, val: self._update_completion_dots())
                btn.bind(size=lambda inst, val: self._update_completion_dots())

    def _load_from_generated_plan(self):
        """Load weekly schedule from generated plan if available."""
        import json
        import os
        try:
            plan_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'calendar_data.json')
            if os.path.exists(plan_path):
                with open(plan_path, 'r') as f:
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
        """Switch between AI Coach and My Program mode."""
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
        # If switching to routine mode and current day has no routine, open picker
        if mode == 'routine':
            day_routines = self._load_day_routines()
            if not day_routines.get(str(self.selected_day_index)):
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: self.load_routine_for_current_day(), 0.3)

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
            # My Program mode: load the routine assigned to this day
            return self._get_routine_for_day(day_index)
        else:
            # AI mode: use the default AI-generated split
            return self.weekly_routine_split.get(day_index, {"name": "Rest Day", "exercises": []})

    def _get_routine_for_day(self, day_index):
        """Get the saved routine assigned to a specific day."""
        import json, os
        day_routines = self._load_day_routines()
        template_name = day_routines.get(str(day_index), '')
        if template_name:
            # Find the template by name
            from template_manager import TemplateManager
            tm = TemplateManager()
            for t in tm.templates:
                if t.name == template_name:
                    exercise_names = [e.get('exercise_name', e.get('exercise_id', '')) for e in t.exercises]
                    return {"name": t.name, "exercises": exercise_names}
        # No routine assigned — show a helpful message
        return {"name": "Tap to assign routine", "exercises": ["Switch to My Program mode", "and tap EDIT to pick a routine", "for this day."]}

    def _load_day_routines(self):
        """Load per-day routine assignments."""
        import json, os
        try:
            filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'day_routines.json')
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save_day_routines(self, data):
        """Save per-day routine assignments."""
        import json, os
        try:
            filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'day_routines.json')
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[Calendar] Error saving day routines: {e}")

    def assign_routine_to_day(self, day_index, template_name):
        """Assign a saved routine to a specific day."""
        day_routines = self._load_day_routines()
        day_routines[str(day_index)] = template_name
        self._save_day_routines(day_routines)
        self.load_selected_day_schedule(day_index)
        print(f"[Calendar] Assigned '{template_name}' to day {day_index}")

    def load_routine_for_current_day(self):
        """Open template picker and assign the selected routine to the current day."""
        from template_view import TemplateView
        tv = TemplateView()
        tv.show_load_popup(self._on_routine_assigned)

    def _on_routine_assigned(self, template):
        """Handle routine selection — assign to current day and display."""
        exercise_names = [e.get('exercise_name', e.get('exercise_id', '')) for e in template.exercises]
        self.assign_routine_to_day(self.selected_day_index, template.name)

    def assign_routine_to_today(self):
        """Quick assign — assign selected routine to today's day."""
        from datetime import datetime
        today = datetime.now().weekday()
        from template_view import TemplateView
        tv = TemplateView()
        tv.show_load_popup(lambda t: self.assign_routine_to_day(today, t.name))

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

    def open_features_popup(self):
        """Open the Ai Coach + Program Lab menu."""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        from kivy.uix.label import Label
        from kivy.metrics import dp
        from kivy.uix.widget import Widget

        def make_popup_btn(text, bg_color, txt, on_fn, height=dp(40)):
            """Button with background_color (Kivy's native bg) — reliable on mobile."""
            btn = Button(text=text, bold=True, font_size='14sp', size_hint_y=None, height=height,
                         background_normal='', background_down='',
                         background_color=bg_color, color=txt, border=(0,0,0,0))
            btn.bind(on_press=on_fn)
            return btn

        # Grey rounded rect contains title + buttons
        inner = BoxLayout(orientation='vertical', spacing=dp(6), padding=[dp(14), dp(8), dp(14), dp(10)])
        with inner.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.15, 0.15, 0.15, 1)
            RoundedRectangle(pos=inner.pos, size=inner.size, radius=[dp(14)])
        inner.bind(pos=lambda inst, val: self._redraw_settings_inner(inst))
        inner.bind(size=lambda inst, val: self._redraw_settings_inner(inst))

        inner.add_widget(Label(text="TRAINING HUB", font_size='16sp', bold=True, color=(0.2, 1.0, 0.6, 1), size_hint_y=None, height=dp(30)))
        inner.add_widget(make_popup_btn("Ai Coach", (0.22, 0.22, 0.22, 1), (0.0, 0.8, 1.0, 1), lambda x: self._popup_dismiss_and_navigate('aicoach')))
        inner.add_widget(make_popup_btn("Program Lab", (0.22, 0.22, 0.22, 1), (0.0, 0.8, 1.0, 1), lambda x: self._popup_dismiss_and_navigate('exercises')))
        inner.add_widget(make_popup_btn("Close", (0.12, 0.12, 0.12, 1), (0.6, 0.6, 0.6, 1), lambda x: self.features_popup.dismiss(), dp(36)))

        # Outer wrapper — spacer pushes grey rect down from popup top
        outer = BoxLayout(orientation='vertical', padding=[0, dp(6), 0, 0])
        outer.add_widget(inner)

        self.features_popup = Popup(title="", content=outer, size_hint=(0.75, None), height=dp(270),
            auto_dismiss=True, background=_POPUP_BG, background_color=(0.1, 0.1, 0.1, 1), separator_height=0)
        self.features_popup.open()

    def open_settings_popup(self):
        """Open settings popup — profile + theme only."""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        from kivy.uix.label import Label
        from kivy.uix.widget import Widget
        from kivy.metrics import dp
        from kivy.app import App
        from kivy.graphics import Color, RoundedRectangle

        app = App.get_running_app()
        charcoal_selected = app.theme_manager.current_bg == 'charcoal'
        navy_selected = app.theme_manager.current_bg == 'navy'

        def make_popup_btn(text, bg_color, txt, on_fn, height=dp(40)):
            btn = Button(text=text, bold=True, font_size='14sp', size_hint_y=None, height=height,
                         background_normal='', background_down='',
                         background_color=bg_color, color=txt, border=(0,0,0,0))
            btn.bind(on_press=on_fn)
            return btn

        # Grey rounded rect contains title + buttons
        inner = BoxLayout(orientation='vertical', spacing=dp(6), padding=[dp(14), dp(10), dp(14), dp(10)])
        with inner.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.15, 0.15, 0.15, 1)
            RoundedRectangle(pos=inner.pos, size=inner.size, radius=[dp(14)])
        inner.bind(pos=lambda inst, val: self._redraw_settings_inner(inst))
        inner.bind(size=lambda inst, val: self._redraw_settings_inner(inst))

        inner.add_widget(Label(text="SETTINGS", font_size='16sp', bold=True, color=(0.2, 1.0, 0.6, 1), size_hint_y=None, height=dp(30)))
        inner.add_widget(make_popup_btn("Update Profile", (0.22, 0.22, 0.22, 1), (0.2, 1.0, 0.6, 1), lambda x: self._popup_dismiss_and_navigate('onboarding')))

        # Theme buttons — actual colours
        bg_box = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(40))
        charcoal_color = (0.40, 0.40, 0.40, 1) if charcoal_selected else (0.25, 0.25, 0.25, 1)
        btn_charcoal = make_popup_btn("Charcoal", charcoal_color, (1, 1, 1, 1) if charcoal_selected else (0.8, 0.8, 0.8, 1), lambda x: self._set_theme_bg('charcoal'))
        bg_box.add_widget(btn_charcoal)
        navy_color = (0.22, 0.35, 0.65, 1) if navy_selected else (0.12, 0.22, 0.45, 1)
        btn_navy = make_popup_btn("Navy", navy_color, (1, 1, 1, 1) if navy_selected else (0.8, 0.8, 0.8, 1), lambda x: self._set_theme_bg('navy'))
        bg_box.add_widget(btn_navy)
        inner.add_widget(bg_box)

        inner.add_widget(make_popup_btn("Log Out", (0.22, 0.22, 0.22, 1), (1, 0.4, 0.4, 1), lambda x: self._show_logout_confirm(x)))
        inner.add_widget(make_popup_btn("Factory Reset", (0.22, 0.22, 0.22, 1), (1.0, 0.33, 0.0, 1), lambda x: self._show_factory_reset_confirm()))
        inner.add_widget(make_popup_btn("Close", (0.12, 0.12, 0.12, 1), (0.6, 0.6, 0.6, 1), lambda x: self.settings_popup.dismiss(), dp(36)))

        # Outer wrapper — spacer pushes grey rect down from popup top
        outer = BoxLayout(orientation='vertical', padding=[0, dp(14), 0, 0])
        outer.add_widget(inner)

        self.settings_popup = Popup(title="", content=outer, size_hint=(0.75, None), height=dp(340),
            auto_dismiss=True, background=_POPUP_BG, background_color=(0.1, 0.1, 0.1, 1), separator_height=0)
        self.settings_popup.open()

    def _set_theme_bg(self, bg_key):
        from kivy.app import App
        app = App.get_running_app()
        app.theme_manager.set_background(bg_key)
        if hasattr(self, 'settings_popup'):
            self.settings_popup.dismiss()
        self.open_settings_popup()

    def _popup_dismiss_and_navigate(self, screen_name):
        # Dismiss whichever popup is open
        for attr in ('features_popup', 'settings_popup'):
            if hasattr(self, attr):
                popup = getattr(self, attr)
                if popup:
                    popup.dismiss()
        from kivy.app import App
        app = App.get_running_app()
        if hasattr(app, 'sm'):
            app.sm.current = screen_name

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

        self.logout_popup = Popup(title="", content=content, size_hint=(0.8, None), height=dp(180), auto_dismiss=True, background=_POPUP_BG, background_color=(0.1, 0.1, 0.1, 1), separator_height=0)
        btn_cancel.bind(on_press=self.logout_popup.dismiss)
        self.logout_popup.open()

    def _do_logout(self):
        if hasattr(self, 'logout_popup'):
            self.logout_popup.dismiss()
        from kivy.app import App
        app = App.get_running_app()
        if hasattr(app, 'logout'):
            app.logout()

    def _show_factory_reset_confirm(self):
        """Show factory reset confirmation with backup option."""
        if hasattr(self, 'settings_popup'):
            self.settings_popup.dismiss()

        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        from kivy.uix.label import Label

        content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(20))
        content.add_widget(Label(
            text="FACTORY RESET", font_size='18sp', bold=True,
            color=(1, 0.33, 0, 1), size_hint_y=None, height=dp(28)
        ))
        content.add_widget(Label(
            text="This will permanently delete:", font_size='13sp',
            color=(1, 1, 1, 1), size_hint_y=None, height=dp(20)
        ))
        files_list = "- Workout history\n- Workout completions\n- Saved routines\n- Calendar plan\n- Day assignments"
        content.add_widget(Label(
            text=files_list, font_size='12sp',
            color=(0.7, 0.7, 0.7, 1), size_hint_y=None, height=dp(80),
            halign='left', valign='top', text_size=(None, None)
        ))

        # Backup + Reset button
        btn_box1 = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(40))
        btn_backup = Button(
            text="BACKUP & RESET", bold=True, font_size='12sp',
            background_normal='', background_down='', background_color=(0,0,0,0),
            color=(1, 1, 1, 1)
        )
        with btn_backup.canvas.before:
            Color(0.0, 0.7, 0.3, 1)
            RoundedRectangle(pos=btn_backup.pos, size=btn_backup.size, radius=[dp(12)])
        btn_backup.bind(pos=lambda inst, val: self._draw_reset_bg(inst, (0.0, 0.7, 0.3, 1)))
        btn_backup.bind(size=lambda inst, val: self._draw_reset_bg(inst, (0.0, 0.7, 0.3, 1)))
        btn_backup.bind(on_press=lambda x: self._do_factory_reset(backup=True))
        btn_box1.add_widget(btn_backup)
        content.add_widget(btn_box1)

        # Reset only button
        btn_box2 = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(40))
        btn_reset = Button(
            text="RESET (NO BACKUP)", bold=True, font_size='12sp',
            background_normal='', background_down='', background_color=(0,0,0,0),
            color=(1, 1, 1, 1)
        )
        with btn_reset.canvas.before:
            Color(0.8, 0.2, 0.2, 1)
            RoundedRectangle(pos=btn_reset.pos, size=btn_reset.size, radius=[dp(12)])
        btn_reset.bind(pos=lambda inst, val: self._draw_reset_bg(inst, (0.8, 0.2, 0.2, 1)))
        btn_reset.bind(size=lambda inst, val: self._draw_reset_bg(inst, (0.8, 0.2, 0.2, 1)))
        btn_reset.bind(on_press=lambda x: self._do_factory_reset(backup=False))
        btn_box2.add_widget(btn_reset)
        content.add_widget(btn_box2)

        # Cancel button
        btn_cancel = Button(
            text="CANCEL", bold=True, font_size='12sp',
            background_normal='', background_down='', background_color=(0,0,0,0),
            color=(0.6, 0.6, 0.6, 1), size_hint_y=None, height=dp(36)
        )
        content.add_widget(btn_cancel)

        self._factory_reset_popup = Popup(
            title="", content=content, size_hint=(0.82, None), height=dp(320),
            auto_dismiss=True, background=_POPUP_BG, background_color=(0.1, 0.1, 0.1, 1),
            separator_height=0
        )
        btn_cancel.bind(on_press=self._factory_reset_popup.dismiss)
        self._factory_reset_popup.open()

    def _draw_reset_bg(self, inst, color):
        inst.canvas.before.clear()
        with inst.canvas.before:
            Color(*color)
            RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(12)])

    def _do_factory_reset(self, backup=True):
        """Execute factory reset — optionally backup first."""
        import json, os, shutil
        from datetime import datetime
        from kivy.app import App
        app = App.get_running_app()

        app_dir = os.path.dirname(os.path.abspath(__file__))
        data_files = [
            'workout_completions.json',
            'workout_history.json',
            'workout_templates.json',
            'day_routines.json',
            'calendar_data.json',
            'user_profile.json',
            'user_data.json',
            'login_state.json',
            'theme_settings.json',
        ]

        # Backup if requested
        if backup:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = os.path.join(app_dir, f'backup_{timestamp}')
            try:
                os.makedirs(backup_dir, exist_ok=True)
                backed_up = 0
                for fname in data_files:
                    src = os.path.join(app_dir, fname)
                    if os.path.exists(src):
                        shutil.copy2(src, backup_dir)
                        backed_up += 1
                print(f"[Factory Reset] Backed up {backed_up} files to {backup_dir}")
            except Exception as e:
                print(f"[Factory Reset] Backup failed: {e}")

        # Wipe all data files
        wiped = 0
        for fname in data_files:
            fpath = os.path.join(app_dir, fname)
            try:
                if os.path.exists(fpath):
                    if fname.endswith('.json'):
                        # Write empty structure instead of deleting
                        with open(fpath, 'w') as f:
                            if fname == 'workout_templates.json':
                                json.dump({"templates": [], "last_updated": ""}, f)
                            elif 'completion' in fname or 'history' in fname:
                                json.dump([], f)
                            else:
                                json.dump({}, f)
                    else:
                        os.remove(fpath)
                    wiped += 1
            except Exception as e:
                print(f"[Factory Reset] Failed to wipe {fname}: {e}")

        print(f"[Factory Reset] Wiped {wiped} files")

        # Dismiss popup and reload
        if hasattr(self, '_factory_reset_popup'):
            self._factory_reset_popup.dismiss()

        # Force-flush the completions file
        try:
            comp_path = os.path.join(app_dir, 'workout_completions.json')
            with open(comp_path, 'w') as f:
                json.dump([], f)
                f.flush()
                os.fsync(f.fileno())
        except Exception:
            pass

        # Reload calendar
        self.weekly_routine_split = {
            0: {"name": "Chest & Triceps", "exercises": ["Flat Bench Press", "Incline Bench Press", "Dumbbell Flat Press", "Tricep Pushdown", "Close-Grip Bench Press"]},
            1: {"name": "Back & Biceps", "exercises": ["Barbell Bent-Over Row", "Dumbbell Single-Arm Row", "Lat Pulldown", "Dumbbell Curl", "Hammer Curl"]},
            2: {"name": "Legs", "exercises": ["Barbell Back Squat", "Dumbbell Bulgarian Split Squat", "Romanian Deadlift", "Hip Thrust", "Calf Raise (Standing)"]},
            3: {"name": "Shoulders & Core", "exercises": ["Military Press", "Dumbbell Lateral Raise", "Cable Face Pull", "Plank", "Hanging Leg Raise"]},
            4: {"name": "Chest & Back", "exercises": ["Flat Bench Press", "Cable Fly", "Barbell Bent-Over Row", "Lat Pulldown", "Dumbbell Reverse Fly"]},
            5: {"name": "Arms & Core", "exercises": ["Dumbbell Curl", "Hammer Curl", "Tricep Pushdown", "Bicycle Crunch", "Crunch"]},
            6: {"name": "Rest Day", "exercises": ["No training scheduled."]}
        }
        today = datetime.now().weekday()
        self.load_selected_day_schedule(today)
        self._update_completion_dots()
        self._update_toggle_visuals()
        print("[Factory Reset] Calendar reset to defaults")

        # Ensure starter templates exist so "My Program" isn't empty
        from template_manager import TemplateManager
        tm = TemplateManager()
        tm.ensure_defaults()

    def _get_week_dates(self):
        """Get the date (YYYY-MM-DD) for each day of this week (Mon-Sun)."""
        from datetime import datetime, timedelta
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        return [(monday + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]

    def _get_completed_days(self):
        """Return a set of day indices (0-6) with completed workouts.
        Green dot shows if ANY mode (AI or My Program) completed that day.
        """
        import json, os
        from datetime import datetime, timedelta
        completed = set()
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        week_end = monday + timedelta(days=7)
        completions_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'workout_completions.json')
        try:
            if not os.path.exists(completions_path):
                return completed
            with open(completions_path, 'r') as f:
                content = f.read().strip()
                if not content:
                    return completed
            completions = json.loads(content)
            if not isinstance(completions, list):
                return completed
            for entry in completions:
                dow = entry.get('day_of_week', -1)
                if dow < 0:
                    try:
                        entry_dt = datetime.strptime(entry.get('date', ''), '%Y-%m-%d')
                        dow = entry_dt.weekday()
                    except (ValueError, TypeError):
                        continue
                try:
                    entry_dt = datetime.strptime(entry.get('date', ''), '%Y-%m-%d')
                    if monday.date() <= entry_dt.date() < week_end.date():
                        completed.add(dow)
                except (ValueError, TypeError):
                    pass
        except Exception:
            pass
        return completed

    def _get_day_completion(self, day_index):
        """Get completion info for a specific day. Returns dict or None.
        Only shows COMPLETED for the CURRENT mode's workout.
        """
        import json, os
        from datetime import datetime, timedelta
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        week_end = monday + timedelta(days=7)
        completions_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'workout_completions.json')
        try:
            if not os.path.exists(completions_path):
                return None
            with open(completions_path, 'r') as f:
                content = f.read().strip()
                if not content:
                    return None
            completions = json.loads(content)
            if not isinstance(completions, list):
                return None
            best = None
            for entry in completions:
                # Only show COMPLETED for the current mode
                entry_mode = entry.get('workout_mode', 'ai')
                if entry_mode != self.workout_mode:
                    continue
                dow = entry.get('day_of_week', -1)
                if dow < 0:
                    try:
                        entry_dt = datetime.strptime(entry.get('date', ''), '%Y-%m-%d')
                        dow = entry_dt.weekday()
                    except (ValueError, TypeError):
                        continue
                if dow == day_index:
                    try:
                        entry_dt = datetime.strptime(entry.get('date', ''), '%Y-%m-%d')
                        if monday.date() <= entry_dt.date() < week_end.date():
                            if best is None or entry_dt > datetime.strptime(best.get('date', ''), '%Y-%m-%d'):
                                best = entry
                    except (ValueError, TypeError):
                        pass
            return best
        except Exception:
            pass
        return None

    def _update_completion_dots(self):
        """Draw green dots under completed day buttons."""
        from kivy.app import App
        from kivy.graphics import Color, Ellipse
        from kivy.metrics import dp
        app = App.get_running_app()
        completed = self._get_completed_days()
        day_buttons = ['btn_mon', 'btn_tue', 'btn_wed', 'btn_thu', 'btn_fri', 'btn_sat', 'btn_sun']
        for i, btn_name in enumerate(day_buttons):
            btn = self.ids.get(btn_name)
            if not btn:
                continue
            self._draw_day_btn(btn, i in completed)

    def _draw_day_btn(self, btn, has_dot):
        """Redraw a day button's canvas (background + optional green dot)."""
        from kivy.app import App
        from kivy.graphics import Color, Ellipse
        from kivy.metrics import dp
        app = App.get_running_app()
        btn.canvas.before.clear()
        with btn.canvas.before:
            Color(*(app.accent_color if btn.state == 'down' else app.card_bg))
            RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(12)])
            if has_dot:
                Color(0.07, 0.85, 0.45, 1)
                Ellipse(
                    pos=(btn.center_x - dp(3), btn.y - dp(4)),
                    size=(dp(6), dp(6))
                )

    def load_selected_day_schedule(self, day_index):
        if self.shift_mode_active:
            self.execute_routine_reschedule(day_index)
            return

        self.selected_day_index = day_index
        day_data = self._get_mode_display_data(day_index)
        self.ids.lbl_routine_name.text = day_data["name"]

        # Build exercise list
        exercise_string = ""
        for exercise in day_data["exercises"]:
            exercise_string += f"- {exercise}\n"

        # Check if this day's workout is completed
        completion = self._get_day_completion(day_index)
        if completion:
            elapsed = completion.get('elapsed', 0)
            sets_done = len(completion.get('sets', []))
            mins = elapsed // 60
            secs = elapsed % 60
            exercise_string += f"\n[color=00D973]  [b]COMPLETED[/b]"
            exercise_string += f"\n[color=888888]  {sets_done} sets · {mins:02d}:{secs:02d}[/color]"

        self.ids.lbl_routine_exercises_preview.text = exercise_string

        # Always start the routine list at the top when (re)loading a day
        if hasattr(self.ids, 'routine_scroll'):
            self.ids.routine_scroll.scroll_y = 1

        self._highlight_day(day_index)
        # Refresh completion dots
        self._update_completion_dots()

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

        # Calculate the actual date for this day
        from datetime import datetime, timedelta
        today = datetime.now()
        # Get Monday of this week
        monday = today - timedelta(days=today.weekday())
        # Add the day index to get the actual date
        workout_date = (monday + timedelta(days=self.selected_day_index)).strftime('%Y-%m-%d')

        self.current_workout = day_data
        self._navigate_to_workout(day_data, workout_date=workout_date)

    def _navigate_to_workout(self, day_data, workout_date=None):
        try:
            from kivy.app import App
            app = App.get_running_app()

            if hasattr(app, 'sm'):
                workout_screen = app.sm.get_screen('workout')
                workout_widget = workout_screen.children[0]

                if hasattr(workout_widget, 'load_exercises'):
                    exercises = day_data.get('exercises', [])
                    name = day_data.get('name', 'Workout')
                    workout_widget.load_exercises(exercises, name, workout_date=workout_date)

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

    def _redraw_popup_bg(self, inst):
        """Redraw popup content's solid background to prevent overlay blur."""
        inst.canvas.before.clear()
        with inst.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0.1, 0.1, 0.1, 1)
            Rectangle(pos=inst.pos, size=inst.size)

    def _redraw_settings_inner(self, inst):
        """Redraw the grey background behind settings options."""
        inst.canvas.before.clear()
        with inst.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.15, 0.15, 0.15, 1)
            RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(14)])
