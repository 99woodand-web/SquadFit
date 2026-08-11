# workout_view.py - Single-page scrollable Active Workout Sheet
# All exercises visible at once, checkmark to log sets, floating rest timer
import os
import json
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle, Line


class WorkoutConsoleScreen(BoxLayout):
    """Single-page scrollable workout sheet with all exercises visible."""

    workout_active = BooleanProperty(False)
    rest_time_left = NumericProperty(0)
    screen_mode = StringProperty("active")  # 'active' or 'history'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timer_event = None
        self.rest_timer_event = None
        self.workout_elapsed = 0
        self.exercises_data = []       # List of exercise dicts with all info
        self.logged_sets = []          # All logged set data
        self.set_widgets = {}          # Maps (ex_idx, set_idx) -> widget references
        self.exercise_cards = []       # List of card widgets in order
        self.total_sets = 0
        self.completed_sets = 0
        self.workout_name = "Workout"
        self._scroll_anim = None
        self._workout_history = self._load_workout_history()
        self._history_date = None      # Date when workout was completed
        self._history_sets = []        # Sets from completed session
        self._history_elapsed = 0      # Duration of completed session

    # ═══════════════════════════════════════════════════════════════
    #  WORKOUT HISTORY - Load/save previous performances
    # ═══════════════════════════════════════════════════════════════
    def _load_workout_history(self):
        """Load workout history from local JSON file."""
        import json, os
        history_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'workout_history.json')
        try:
            if os.path.exists(history_path):
                with open(history_path, 'r') as f:
                    data = json.load(f)
                # Handle both formats: flat list OR grouped dict
                if isinstance(data, list):
                    grouped = {}
                    for entry in data:
                        if isinstance(entry, dict):
                            ex_name = entry.get('exercise', '')
                            if ex_name:
                                if ex_name not in grouped:
                                    grouped[ex_name] = []
                                grouped[ex_name].append(entry)
                    return grouped
                elif isinstance(data, dict):
                    return data
        except Exception as e:
            print(f"[Workout] History load error: {e}")
        return {}

    def _save_workout_history(self):
        """Save current workout data to history file."""
        import json, os
        history_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'workout_history.json')
        try:
            # Ensure history is a dict before saving
            if not isinstance(self._workout_history, dict):
                self._workout_history = {}
            # Group logged sets by exercise name
            for set_data in self.logged_sets:
                ex_name = set_data.get('exercise', '')
                if not ex_name:
                    continue
                if ex_name not in self._workout_history:
                    self._workout_history[ex_name] = []
                self._workout_history[ex_name].append(set_data)
            with open(history_path, 'w') as f:
                json.dump(self._workout_history, f, indent=2)
        except Exception as e:
            print(f"[Workout] History save error: {e}")

    def _get_last_performance(self, exercise_name):
        """Get the most recent performance for an exercise."""
        # Ensure history is always a dict
        if not isinstance(self._workout_history, dict):
            self._workout_history = {}
        sessions = self._workout_history.get(exercise_name, [])
        if not sessions:
            return None
        # Return the most recent session's data
        last = sessions[-1]
        return last

    # ═══════════════════════════════════════════════════════════════
    #  HISTORY MODE - Detect completed workouts and enable read-only
    # ═══════════════════════════════════════════════════════════════
    def _check_history_for_today(self, workout_name):
        """
        Check if this workout was already completed today.
        Returns (is_completed, elapsed_seconds, sets_list) if found.
        """
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Check the workout_completions.json file
        completions_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'workout_completions.json')
        try:
            if os.path.exists(completions_path):
                with open(completions_path, 'r') as f:
                    content = f.read().strip()
                    if not content:
                        return False, 0, []
                    completions = json.loads(content)
                if not isinstance(completions, list):
                    return False, 0, []
                # Look for today's completion with matching workout name
                for entry in completions:
                    if entry.get('date') == today and entry.get('workout_name') == workout_name:
                        return True, entry.get('elapsed', 0), entry.get('sets', [])
        except Exception as e:
            print(f"[Workout] History check error: {e}")
        return False, 0, []

    def _save_completion(self):
        """Save workout completion record for today."""
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        
        completions_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'workout_completions.json')
        try:
            completions = []
            if os.path.exists(completions_path):
                with open(completions_path, 'r') as f:
                    content = f.read().strip()
                    if content:
                        completions = json.loads(content)
            if not isinstance(completions, list):
                completions = []
            
            # Remove any existing entry for today's workout name
            completions = [
                c for c in completions
                if not (c.get('date') == today and c.get('workout_name') == self.workout_name)
            ]
            
            # Save exercise names for Quick Start
            exercise_names = [ex.get('name', '') for ex in self.exercises_data if ex.get('name')]

            # Add new completion
            completions.append({
                'date': today,
                'workout_name': self.workout_name,
                'elapsed': self.workout_elapsed,
                'sets': self.logged_sets,
                'completed_sets': self.completed_sets,
                'total_sets': self.total_sets,
                'exercises': exercise_names
            })
            
            with open(completions_path, 'w') as f:
                json.dump(completions, f, indent=2)
            print(f"[Workout] Saved completion for {self.workout_name} on {today}")
        except Exception as e:
            print(f"[Workout] Save completion error: {e}")

    def enter_history_mode(self, elapsed, sets):
        """Switch to read-only history mode."""
        self.screen_mode = 'history'
        self.workout_active = False
        self.workout_elapsed = elapsed
        self.completed_sets = len(sets)
        self._history_sets = sets
        self._history_elapsed = elapsed
        
        # Stop any running timers
        if self.timer_event:
            self.timer_event.cancel()
        if self.rest_timer_event:
            self.rest_timer_event.cancel()
        
        # Hide rest banner
        if hasattr(self.ids, 'rest_banner'):
            self.ids.rest_banner.opacity = 0
            self.ids.rest_banner.disabled = True
            self.ids.rest_banner.height = 0
        
        # Update timer display to static
        mins = elapsed // 60
        secs = elapsed % 60
        if hasattr(self.ids, 'lbl_timer_clock'):
            self.ids.lbl_timer_clock.text = f"{mins:02d}:{secs:02d}"
        
        # Update status bar
        if hasattr(self.ids, 'lbl_sync_status'):
            self.ids.lbl_sync_status.text = "Viewing completed workout"
        if hasattr(self.ids, 'lbl_sets_completed'):
            self.ids.lbl_sets_completed.text = f"Sets: {self.completed_sets}/{self.total_sets}"
        
        # Mark all logged sets as completed visually
        self._apply_history_state()
        
        print(f"[Workout] Entered history mode: {elapsed}s, {len(sets)} sets")

    def _apply_history_state(self):
        """Apply read-only visual state to all set rows."""
        for key, info in self.set_widgets.items():
            # Check if this set was in the completed session
            ex_idx = info['exercise_idx']
            set_idx = info['set_idx']
            was_logged = False
            for s in self._history_sets:
                if s.get('exercise') == self.exercises_data[ex_idx].get('name', '') and \
                   s.get('set') == set_idx + 1:
                    was_logged = True
                    break
            
            if was_logged:
                # Mark as completed
                info['logged'] = True
                info['check'].text = "DONE"
                info['check'].color = (0.3, 0.3, 0.3, 1)
                info['check'].disabled = True
                info['check'].canvas.before.clear()
                with info['check'].canvas.before:
                    Color(0.3, 0.3, 0.3, 1)
                    RoundedRectangle(pos=info['check'].pos, size=info['check'].size, radius=[dp(12)])
                info['row'].canvas.before.clear()
                with info['row'].canvas.before:
                    Color(0.15, 0.15, 0.15, 0.5)
                    RoundedRectangle(pos=info['row'].pos, size=info['row'].size, radius=[dp(10)])
                info['input'].color = (0.4, 0.4, 0.4, 1)
            else:
                # Not logged - disable the checkmark
                info['check'].disabled = True
                info['check'].canvas.before.clear()
                with info['check'].canvas.before:
                    Color(0.2, 0.2, 0.2, 1)
                    RoundedRectangle(pos=info['check'].pos, size=info['check'].size, radius=[dp(12)])
                info['check'].color = (0.3, 0.3, 0.3, 1)

    def toggle_edit_mode(self):
        """Switch from history mode back to active edit mode."""
        self.screen_mode = 'active'
        self.workout_active = True
        self.logged_sets = list(self._history_sets)  # Restore previous sets
        self.completed_sets = len(self.logged_sets)
        
        # Restart the workout timer
        self.timer_event = Clock.schedule_interval(self._tick_workout, 1)
        
        # Update status
        if hasattr(self.ids, 'lbl_sync_status'):
            self.ids.lbl_sync_status.text = "Editing workout - tap + to log more sets"
        if hasattr(self.ids, 'lbl_sets_completed'):
            self.ids.lbl_sets_completed.text = f"Sets: {self.completed_sets}/{self.total_sets}"
        
        # Re-enable all checkmarks that aren't logged
        for key, info in self.set_widgets.items():
            if not info['logged']:
                info['check'].disabled = False
                info['check'].canvas.before.clear()
                from kivy.app import App
                app = App.get_running_app()
                with info['check'].canvas.before:
                    Color(*app.accent_color)
                    RoundedRectangle(pos=info['check'].pos, size=info['check'].size, radius=[dp(12)])
                info['check'].color = (0.07, 0.07, 0.07, 1)
        
        print(f"[Workout] Switched to edit mode - {self.completed_sets} sets already logged")

    # ═══════════════════════════════════════════════════════════════
    #  LOAD EXERCISES - Build the entire scrollable sheet
    # ═══════════════════════════════════════════════════════════════
    def load_exercises(self, exercise_list, workout_name="Workout"):
        """Build the full scrollable workout sheet from exercise list."""
        self.workout_name = workout_name
        self.exercises_data = []
        self.logged_sets = []
        self.set_widgets = {}
        self.completed_sets = 0
        self.workout_active = False
        self.workout_elapsed = 0

        if self.timer_event:
            self.timer_event.cancel()
        if self.rest_timer_event:
            self.rest_timer_event.cancel()
        if self._scroll_anim:
            self._scroll_anim.cancel(self)
            self._scroll_anim = None

        from exercise_db import get_all_exercises, exercise_uses_weight, exercise_uses_barbell_by_name
        all_ex = get_all_exercises()

        # Build exercise data list
        for ex_name in exercise_list:
            ex_info = None
            for eid, ex in all_ex.items():
                if ex.get('name', '').lower() == ex_name.lower():
                    ex_info = ex.copy()
                    ex_info['id'] = eid
                    break
            if not ex_info:
                ex_info = {
                    'name': ex_name, 'muscle': 'Unknown', 'equip': 'Unknown',
                    'track': 'strength', 'sets': 3, 'reps': 10,
                    'equip_tags': [], 'tip': 'Focus on proper form'
                }
            self.exercises_data.append(ex_info)

        # Calculate total sets
        self.total_sets = sum(ex.get('sets', 3) for ex in self.exercises_data)

        # Build the UI
        self._build_workout_sheet()

        # Update header
        if hasattr(self.ids, 'lbl_workout_title'):
            self.ids.lbl_workout_title.text = workout_name.upper()
        if hasattr(self.ids, 'lbl_timer_clock'):
            self.ids.lbl_timer_clock.text = "00:00"

        # Check if this workout was already completed today
        is_completed, elapsed, sets = self._check_history_for_today(workout_name)
        if is_completed:
            self.screen_mode = 'history'
            self._history_date = None
            self._history_sets = sets
            self._history_elapsed = elapsed
            print(f"[Workout] Found completed workout for today - entering history mode")
            # Enter history mode after a short delay to let UI build
            Clock.schedule_once(lambda dt: self.enter_history_mode(elapsed, sets), 0.3)
        else:
            self.screen_mode = 'active'
            self.workout_active = False
            print(f"[Workout] Built sheet: {len(self.exercises_data)} exercises, {self.total_sets} total sets")

    def _build_workout_sheet(self):
        """Dynamically build all exercise cards inside the ScrollView."""
        from kivy.app import App
        app = App.get_running_app()

        # Find the scroll container
        if not hasattr(self.ids, 'exercise_scroll'):
            return
        scroll = self.ids.exercise_scroll
        scroll.clear_widgets()

        self.exercise_cards = []

        container = BoxLayout(
            orientation='vertical', spacing=dp(12),
            size_hint_y=None, padding=[0, dp(8), 0, dp(8)]
        )
        container.bind(minimum_height=container.setter('height'))

        for ex_idx, ex in enumerate(self.exercises_data):
            card = self._build_exercise_card(ex_idx, ex)
            self.exercise_cards.append(card)
            container.add_widget(card)

        scroll.add_widget(container)

    def _build_exercise_card(self, ex_idx, ex):
        """Build a single exercise card with all its set rows."""
        from kivy.app import App
        app = App.get_running_app()

        track = ex.get('track', 'strength')
        name = ex.get('name', 'Exercise')
        muscle = ex.get('muscle', '')
        equip = ex.get('equip', '')
        num_sets = ex.get('sets', 3)
        default_reps = ex.get('reps', 10)

        # Check equipment type
        uses_weight = track == 'strength' and equip.lower() not in ['bodyweight', 'none', '']
        uses_barbell = 'barbell' in [t.lower() for t in ex.get('equip_tags', [])] or 'barbell' in equip.lower()
        is_cardio = track == 'cardio'

        # ─── Card wrapper ───
        card = BoxLayout(
            orientation='vertical', spacing=dp(8),
            padding=dp(14), size_hint_y=None
        )
        card.bind(minimum_height=card.setter('height'))

        # Calculate card height: header(~40) + sets * row_height(~50) + spacing
        row_h = dp(50) if not is_cardio else dp(56)
        card_height = dp(44) + (num_sets * row_h) + ((num_sets - 1) * dp(6))
        card.height = card_height

        with card.canvas.before:
            Color(*app.card_bg)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(16)])
        card.bind(pos=lambda inst, val: self._draw_card_bg(inst))
        card.bind(size=lambda inst, val: self._draw_card_bg(inst))

        # ─── Exercise header ───
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(36))
        header.add_widget(Label(
            text=name, font_size='16sp', bold=True, color=(1, 1, 1, 1),
            halign='left', text_size=(dp(280), None), valign='middle'
        ))
        form_btn = Button(
            text="FORM", font_size='10sp', bold=True, size_hint=(None, None),
            size=(dp(55), dp(28)), background_normal='', background_down='',
            background_color=(0, 0, 0, 0), color=app.accent_color
        )
        with form_btn.canvas.before:
            Color(app.accent_color[0], app.accent_color[1], app.accent_color[2], 0.15)
            RoundedRectangle(pos=form_btn.pos, size=form_btn.size, radius=[dp(12)])
        form_btn.bind(pos=lambda inst, val: self._draw_btn_bg(inst, 0.15))
        form_btn.bind(size=lambda inst, val: self._draw_btn_bg(inst, 0.15))
        _ex_idx = ex_idx
        form_btn.bind(on_press=lambda x, i=_ex_idx: self._show_form_tip(i))
        header.add_widget(form_btn)
        card.add_widget(header)

        # Subtitle line
        subtitle = f"{muscle} | {equip}" if not is_cardio else f"{muscle} | Cardio"
        card.add_widget(Label(
            text=subtitle, font_size='11sp', color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None, height=dp(18), halign='left', text_size=(dp(280), None)
        ))

        # ─── LAST TIME YOU DID... ───
        last_perf = self._get_last_performance(name)
        if last_perf:
            last_text = self._format_last_performance(last_perf)
            last_label = Label(
                text=last_text, font_size='11sp', bold=True,
                color=(app.accent_color[0], app.accent_color[1], app.accent_color[2], 0.8),
                size_hint_y=None, height=dp(18), halign='left',
                text_size=(dp(280), None)
            )
            card.add_widget(last_label)
            # Increase card height for the extra line
            card.height += dp(18)
        else:
            no_data_label = Label(
                text="First time — set your baseline!", font_size='11sp', italic=True,
                color=(0.4, 0.4, 0.4, 1),
                size_hint_y=None, height=dp(18), halign='left',
                text_size=(dp(280), None)
            )
            card.add_widget(no_data_label)
            card.height += dp(18)

        # ─── SWAP EXERCISE BUTTON ───
        swap_row = BoxLayout(size_hint_y=None, height=dp(28))
        swap_btn = Button(
            text="SWAP EXERCISE", font_size='10sp', bold=True,
            size_hint=(None, None), size=(dp(100), dp(26)),
            background_normal='', background_down='',
            background_color=(0, 0, 0, 0),
            color=(1.0, 0.43, 0.0, 1)  # Safety orange for swap
        )
        with swap_btn.canvas.before:
            Color(1.0, 0.43, 0.0, 0.15)
            RoundedRectangle(pos=swap_btn.pos, size=swap_btn.size, radius=[dp(10)])
        swap_btn.bind(pos=lambda inst, val: self._draw_swap_bg(inst))
        swap_btn.bind(size=lambda inst, val: self._draw_swap_bg(inst))
        swap_btn.bind(on_press=lambda x, i=ex_idx: self._show_swap_options(i))
        swap_row.add_widget(swap_btn)
        swap_row.add_widget(Label())  # spacer
        card.add_widget(swap_row)
        card.height += dp(28)

        # ─── Column headers ───
        col_header = BoxLayout(size_hint_y=None, height=dp(22), spacing=dp(6))
        col_header.add_widget(Label(text="SET", font_size='10sp', bold=True, color=(0.4, 0.4, 0.4, 1)))
        if is_cardio:
            col_header.add_widget(Label(text="DISTANCE", font_size='10sp', bold=True, color=(0.4, 0.4, 0.4, 1)))
            col_header.add_widget(Label(text="PACE", font_size='10sp', bold=True, color=(0.4, 0.4, 0.4, 1)))
        elif uses_weight:
            col_header.add_widget(Label(text="WEIGHT", font_size='10sp', bold=True, color=(0.4, 0.4, 0.4, 1)))
            col_header.add_widget(Label(text="REPS", font_size='10sp', bold=True, color=(0.4, 0.4, 0.4, 1)))
        else:
            col_header.add_widget(Label(text="REPS", font_size='10sp', bold=True, color=(0.4, 0.4, 0.4, 1)))
        col_header.add_widget(Label(text="", size_hint_x=None, width=dp(48)))
        card.add_widget(col_header)

        # ─── Set rows ───
        for set_idx in range(num_sets):
            row = self._build_set_row(ex_idx, set_idx, ex, uses_weight, uses_barbell, is_cardio, default_reps)
            card.add_widget(row)

        return card

    def _build_set_row(self, ex_idx, set_idx, ex, uses_weight, uses_barbell, is_cardio, default_reps):
        """Build a single set row with inputs and checkmark."""
        from kivy.app import App
        app = App.get_running_app()

        row_key = (ex_idx, set_idx)
        row_h = dp(50) if not is_cardio else dp(56)

        row = BoxLayout(
            orientation='horizontal', spacing=dp(6),
            size_hint_y=None, height=row_h
        )
        with row.canvas.before:
            Color(0.12, 0.12, 0.12, 1)
            RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(10)])
        row.bind(pos=lambda inst, val: self._draw_row_bg(inst))
        row.bind(size=lambda inst, val: self._draw_row_bg(inst))

        # Set number label
        set_label = Label(
            text=f"{set_idx + 1}", font_size='14sp', bold=True,
            color=(0.6, 0.6, 0.6, 1), size_hint_x=None, width=dp(30)
        )
        row.add_widget(set_label)

        # Target info
        target = ""
        if is_cardio:
            target = "Run"
        elif uses_weight:
            target = f"-- kg"
        else:
            target = f"{default_reps}"
        target_label = Label(
            text=target, font_size='12sp', color=(0.4, 0.4, 0.4, 1),
            size_hint_x=None, width=dp(60)
        )
        row.add_widget(target_label)

        # Input field (editable label that acts as input)
        if is_cardio:
            input_label = Label(
                text="0.00 km", font_size='15sp', bold=True,
                color=(1, 1, 1, 1), size_hint_x=1
            )
        elif uses_weight:
            input_label = Label(
                text=f"{ex.get('reps', 10)} reps", font_size='15sp', bold=True,
                color=(1, 1, 1, 1), size_hint_x=1
            )
        else:
            input_label = Label(
                text=f"{default_reps} reps", font_size='15sp', bold=True,
                color=(1, 1, 1, 1), size_hint_x=1
            )
        row.add_widget(input_label)

        # Checkmark button
        check_btn = Button(
            text="+", font_size='20sp', bold=True,
            size_hint=(None, None), size=(dp(44), dp(40)),
            background_normal='', background_down='',
            background_color=(0, 0, 0, 0),
            color=(0.07, 0.07, 0.07, 1)
        )
        with check_btn.canvas.before:
            Color(*app.accent_color)
            RoundedRectangle(pos=check_btn.pos, size=check_btn.size, radius=[dp(12)])
        check_btn.bind(pos=lambda inst, val: self._draw_check_bg(inst))
        check_btn.bind(size=lambda inst, val: self._draw_check_bg(inst))
        check_btn.bind(on_press=lambda x, k=row_key: self._log_set_checkmark(k))
        row.add_widget(check_btn)

        # Store references
        self.set_widgets[row_key] = {
            'row': row,
            'label': set_label,
            'target': target_label,
            'input': input_label,
            'check': check_btn,
            'logged': False,
            'exercise_idx': ex_idx,
            'set_idx': set_idx
        }

        return row

    # ═══════════════════════════════════════════════════════════════
    #  CANVAS DRAWING HELPERS
    # ═══════════════════════════════════════════════════════════════
    def _draw_card_bg(self, inst):
        from kivy.app import App
        app = App.get_running_app()
        inst.canvas.before.clear()
        with inst.canvas.before:
            Color(*app.card_bg)
            RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(16)])

    def _draw_row_bg(self, inst):
        inst.canvas.before.clear()
        with inst.canvas.before:
            Color(0.12, 0.12, 0.12, 1)
            RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(10)])

    def _draw_row_bg_done(self, inst):
        inst.canvas.before.clear()
        with inst.canvas.before:
            Color(0.15, 0.15, 0.15, 0.5)
            RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(10)])

    def _draw_check_bg(self, inst):
        from kivy.app import App
        app = App.get_running_app()
        inst.canvas.before.clear()
        with inst.canvas.before:
            Color(*app.accent_color)
            RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(12)])

    def _draw_check_bg_done(self, inst):
        inst.canvas.before.clear()
        with inst.canvas.before:
            Color(0.3, 0.3, 0.3, 1)
            RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(12)])

    def _draw_btn_bg(self, inst, alpha):
        from kivy.app import App
        app = App.get_running_app()
        inst.canvas.before.clear()
        with inst.canvas.before:
            Color(app.accent_color[0], app.accent_color[1], app.accent_color[2], alpha)
            RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(12)])

    # ═══════════════════════════════════════════════════════════════
    #  CHECKMARK LOG SET
    # ═══════════════════════════════════════════════════════════════
    def _log_set_checkmark(self, row_key):
        """Log a set when checkmark is tapped. Non-blocking, stays on page."""
        if not self.workout_active:
            if hasattr(self.ids, 'lbl_sync_status'):
                self.ids.lbl_sync_status.text = "Press START first!"
            return

        info = self.set_widgets.get(row_key)
        if not info or info['logged']:
            return

        ex_idx = info['exercise_idx']
        set_idx = info['set_idx']
        ex = self.exercises_data[ex_idx]
        track = ex.get('track', 'strength')

        # Mark as logged visually
        info['logged'] = True
        info['check'].text = "DONE"
        info['check'].color = (0.3, 0.3, 0.3, 1)
        info['check'].canvas.before.clear()
        with info['check'].canvas.before:
            Color(0.3, 0.3, 0.3, 1)
            RoundedRectangle(pos=info['check'].pos, size=info['check'].size, radius=[dp(12)])
        info['check'].disabled = True

        # Dim the row
        info['row'].canvas.before.clear()
        with info['row'].canvas.before:
            Color(0.15, 0.15, 0.15, 0.5)
            RoundedRectangle(pos=info['row'].pos, size=info['row'].size, radius=[dp(10)])
        info['input'].color = (0.4, 0.4, 0.4, 1)

        # Record the set data
        set_data = {
            'exercise': ex.get('name', 'Unknown'),
            'set': set_idx + 1,
            'type': track,
        }
        if track == 'cardio':
            set_data['distance'] = info['input'].text
            set_data['pace'] = '--'
        elif track == 'strength':
            equip = ex.get('equip', '').lower()
            if 'bodyweight' in equip or 'none' in equip:
                set_data['reps'] = info['input'].text
                set_data['weight'] = 'BW'
            else:
                set_data['reps'] = info['input'].text
                set_data['weight'] = 'logged'
        self.logged_sets.append(set_data)

        self.completed_sets += 1
        if hasattr(self.ids, 'lbl_sync_status'):
            self.ids.lbl_sync_status.text = f"Set logged! ({self.completed_sets}/{self.total_sets})"
        if hasattr(self.ids, 'lbl_sets_completed'):
            self.ids.lbl_sets_completed.text = f"Sets: {self.completed_sets}"

        print(f"[Workout] Logged set {set_idx+1} of {ex.get('name', '?')}")

        # Start rest timer
        self._start_floating_rest()

        # Check if this was the LAST set of this exercise
        num_sets = ex.get('sets', 3)
        is_final_set = (set_idx >= num_sets - 1)

        if is_final_set and ex_idx < len(self.exercises_data) - 1:
            # Final set of a non-last exercise → smooth scroll to next card
            Clock.schedule_once(
                lambda dt, i=ex_idx: self.smooth_scroll_to_next_exercise(i), 0.3
            )
        elif is_final_set and ex_idx >= len(self.exercises_data) - 1:
            # Final set of the VERY LAST exercise → center on FINISH button
            Clock.schedule_once(
                lambda dt: self.smooth_scroll_to_finish(), 0.3
            )
        else:
            # Mid-exercise → just ensure next set is visible
            self._scroll_to_next_incomplete(ex_idx, set_idx)

    def _start_floating_rest(self):
        """Start the floating rest timer banner."""
        self.rest_time_left = 90
        if self.rest_timer_event:
            self.rest_timer_event.cancel()
        self.rest_timer_event = Clock.schedule_interval(self._tick_rest, 1)

        # Show the floating banner
        if hasattr(self.ids, 'rest_banner'):
            self.ids.rest_banner.opacity = 1
            self.ids.rest_banner.disabled = False
            self.ids.rest_banner.height = dp(60)
            self.ids.rest_banner.size_hint_y = None

    def _tick_rest(self, dt):
        if self.rest_time_left > 0:
            self.rest_time_left -= 1
            mins = self.rest_time_left // 60
            secs = self.rest_time_left % 60
            if hasattr(self.ids, 'lbl_rest_timer'):
                self.ids.lbl_rest_timer.text = f"REST {mins:02d}:{secs:02d}"
        else:
            if self.rest_timer_event:
                self.rest_timer_event.cancel()
            # Hide banner
            if hasattr(self.ids, 'rest_banner'):
                self.ids.rest_banner.opacity = 0
                self.ids.rest_banner.disabled = True
                self.ids.rest_banner.height = 0
                self.ids.rest_banner.size_hint_y = None
            if hasattr(self.ids, 'lbl_sync_status'):
                self.ids.lbl_sync_status.text = "Rest over! Next set ready"

    def _scroll_to_next_incomplete(self, current_ex_idx, current_set_idx):
        """Auto-scroll the ScrollView to the next incomplete set."""
        for key, info in sorted(self.set_widgets.items()):
            ex_i, set_i = key
            if not info['logged']:
                if hasattr(self.ids, 'exercise_scroll'):
                    scroll = self.ids.exercise_scroll
                    widget = info['row']
                    Clock.schedule_once(lambda dt, w=widget, s=scroll: self._do_scroll(s, w), 0.1)
                return

    def _do_scroll(self, scroll, widget):
        """Scroll to make widget visible using Kivy's built-in scroll_to."""
        try:
            scroll.scroll_to(widget)
        except:
            pass

    # ═══════════════════════════════════════════════════════════════
    #  SMOOTH AUTO-SCROLL ON EXERCISE COMPLETION
    # ═══════════════════════════════════════════════════════════════
    def smooth_scroll_to_next_exercise(self, completed_ex_idx):
        """
        Smoothly animate the ScrollView to the top of the NEXT exercise card.
        Called when the final set of an exercise is completed.
        
        Uses Kivy Animation with out_quad easing for natural deceleration.
        Non-blocking: user can touch and override mid-animation.
        """
        next_ex_idx = completed_ex_idx + 1
        if next_ex_idx >= len(self.exercise_cards):
            return  # No next exercise (edge case handled by finish flow)

        scroll = self.ids.get('exercise_scroll')
        if not scroll or not hasattr(scroll, 'children') or not scroll.children:
            return

        # The scroll view's child is the container BoxLayout
        container = scroll.children[0]
        next_card = self.exercise_cards[next_ex_idx]

        # Calculate the target scroll_y value
        # scroll_y = 1.0 means top, 0.0 means bottom
        target_scroll_y = self._calculate_scroll_target(scroll, container, next_card)

        if target_scroll_y is None:
            return

        # Cancel any existing scroll animation
        if self._scroll_anim:
            self._scroll_anim.cancel(self)

        # Create smooth animation with out_quad easing
        self._scroll_anim = Animation(
            scroll_y=target_scroll_y,
            duration=0.6,
            t='out_quad'
        )
        self._scroll_anim.start(scroll)

        print(f"[Workout] Smooth scroll: exercise {completed_ex_idx} → {next_ex_idx} (target_y={target_scroll_y:.2f})")

    def smooth_scroll_to_finish(self):
        """
        Smoothly scroll to the bottom of the workout sheet
        to reveal the FINISH button area. Called after the
        final set of the last exercise.
        """
        scroll = self.ids.get('exercise_scroll')
        if not scroll:
            return

        # Cancel any existing animation
        if self._scroll_anim:
            self._scroll_anim.cancel(self)

        # scroll_y = 0.0 is the absolute bottom
        self._scroll_anim = Animation(
            scroll_y=0.0,
            duration=0.6,
            t='out_quad'
        )
        self._scroll_anim.start(scroll)

        print("[Workout] Smooth scroll: to FINISH button")

    def _calculate_scroll_target(self, scroll, container, target_widget):
        """
        Calculate the scroll_y value (0.0-1.0) that places
        the target widget near the top of the visible scroll area.
        
        Kivy ScrollView scroll_y:
          1.0 = content top visible (scrolled all the way up)
          0.0 = content bottom visible (scrolled all the way down)
          scroll_y * (content_h - view_h) = offset from content bottom
        
        To bring widget_top to viewport position target_viewport_y:
          scroll_y = (widget_top - target_viewport_y) / (content_h - view_h)
        """
        try:
            content_height = container.height
            view_height = scroll.height

            if content_height <= view_height:
                return 0.5  # Content fits, no scrolling needed

            max_scroll = content_height - view_height
            if max_scroll <= 0:
                return 0.5

            # Widget's top edge in container coordinates
            widget_top = target_widget.y + target_widget.height

            # Place widget at 15% from the top of the viewport
            target_viewport_y = view_height * 0.15

            # Correct Kivy formula
            scroll_y = (widget_top - target_viewport_y) / max_scroll

            # Clamp to valid range
            return max(0.0, min(1.0, scroll_y))
        except Exception as e:
            print(f"[Workout] Scroll calc error: {e}")
            return None

    # ═══════════════════════════════════════════════════════════════
    #  WORKOUT TIMER
    # ═══════════════════════════════════════════════════════════════
    def start_workout_timer(self):
        """Start the overall workout timer."""
        self.workout_active = True
        self.workout_elapsed = 0
        if self.timer_event:
            self.timer_event.cancel()
        self.timer_event = Clock.schedule_interval(self._tick_workout, 1)

        if hasattr(self.ids, 'btn_start'):
            self.ids.btn_start.opacity = 0
            self.ids.btn_start.disabled = True
            self.ids.btn_start.height = 0
            self.ids.btn_start.size_hint_y = None
        if hasattr(self.ids, 'lbl_sync_status'):
            self.ids.lbl_sync_status.text = "Workout started! Tap + to log sets"

    def _tick_workout(self, dt):
        self.workout_elapsed += 1
        mins = self.workout_elapsed // 60
        secs = self.workout_elapsed % 60
        if hasattr(self.ids, 'lbl_timer_clock'):
            self.ids.lbl_timer_clock.text = f"{mins:02d}:{secs:02d}"

    # ═══════════════════════════════════════════════════════════════
    #  FINISH WORKOUT
    # ═══════════════════════════════════════════════════════════════
    def finish_workout(self):
        """Show summary and end workout. Checks milestones first."""
        # Guard: Don't finish if no sets were logged
        if not self.logged_sets:
            if hasattr(self.ids, 'lbl_sync_status'):
                self.ids.lbl_sync_status.text = "Log at least one set before finishing!"
            return

        if self.timer_event:
            self.timer_event.cancel()
        if self.rest_timer_event:
            self.rest_timer_event.cancel()

        self.workout_active = False

        # Save workout history for "Last time you did..."
        self._save_workout_history()

        # Save completion record for today
        self._save_completion()

        # Hide rest banner
        if hasattr(self.ids, 'rest_banner'):
            self.ids.rest_banner.opacity = 0
            self.ids.rest_banner.disabled = True
            self.ids.rest_banner.height = 0

        # ─── SHOW SUMMARY DIRECTLY ───
        self._show_workout_summary()

    def _show_workout_summary(self):
        """Display the final workout summary popup."""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.app import App
        app = App.get_running_app()

        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(15))
        content.add_widget(Label(
            text="WORKOUT COMPLETE!", font_size='20sp', bold=True,
            color=tuple(app.accent_color), size_hint_y=None, height=dp(35)
        ))

        mins = self.workout_elapsed // 60
        secs = self.workout_elapsed % 60
        content.add_widget(Label(
            text=f"Duration: {mins}m {secs}s | Sets: {self.completed_sets}/{self.total_sets}",
            font_size='14sp', color=(1, 1, 1, 1), size_hint_y=None, height=dp(25)
        ))
        content.add_widget(Label(
            text=self.workout_name, font_size='13sp', color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None, height=dp(22)
        ))

        if self.logged_sets:
            lines = []
            for s in self.logged_sets[:10]:
                if s.get('type') == 'cardio':
                    lines.append(f"  {s['exercise']}: {s.get('distance', 'N/A')}")
                elif s.get('weight') == 'BW':
                    lines.append(f"  {s['exercise']}: {s.get('reps', '?')} reps (BW)")
                else:
                    lines.append(f"  {s['exercise']}: Set {s.get('set', '?')}")
            if len(self.logged_sets) > 10:
                lines.append(f"  ... +{len(self.logged_sets) - 10} more")
            summary_label = Label(
                text="\n".join(lines), font_size='11sp', color=(0.6, 0.6, 0.6, 1),
                halign='left', text_size=(dp(280), None),
                size_hint_y=None, height=min(dp(140), dp(16) * len(lines))
            )
            content.add_widget(summary_label)

        # Save as Template button
        btn_template = Button(
            text="SAVE ROUTINE", bold=True, font_size='12sp',
            size_hint_y=None, height=dp(42),
            background_normal='', background_down='',
            background_color=(0, 0, 0, 0), color=(0.0, 0.8, 1.0, 1),
            border=(0, 0, 0, 0)
        )
        with btn_template.canvas.before:
            Color(0.0, 0.8, 1.0, 0.15)
            RoundedRectangle(pos=btn_template.pos, size=btn_template.size, radius=[dp(21)])
        btn_template.bind(pos=lambda inst, val: self._draw_cyan_pill(inst))
        btn_template.bind(size=lambda inst, val: self._draw_cyan_pill(inst))
        btn_template.bind(on_press=lambda x: self._save_as_template(popup))
        content.add_widget(btn_template)

        btn = Button(
            text="BACK TO CALENDAR", bold=True, font_size='14sp',
            size_hint_y=None, height=dp(50),
            background_normal='', background_down='',
            background_color=(0, 0, 0, 0), color=(0.07, 0.07, 0.07, 1)
        )
        with btn.canvas.before:
            Color(*app.accent_color)
            RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(25)])
        btn.bind(pos=lambda inst, val: self._draw_accent_pill(inst))
        btn.bind(size=lambda inst, val: self._draw_accent_pill(inst))
        content.add_widget(btn)

        popup = Popup(
            title="", content=content, size_hint=(0.85, None), height=dp(380),
            auto_dismiss=False, background_color=(0.1, 0.1, 0.1, 0.95)
        )
        btn.bind(on_press=lambda x: self._close_and_return(popup))
        popup.open()

    def _draw_accent_pill(self, inst):
        from kivy.app import App
        app = App.get_running_app()
        inst.canvas.before.clear()
        with inst.canvas.before:
            Color(*app.accent_color)
            RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(25)])

    def _draw_cyan_pill(self, inst):
        inst.canvas.before.clear()
        with inst.canvas.before:
            Color(0.0, 0.8, 1.0, 0.15)
            RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(21)])

    def _save_as_template(self, summary_popup):
        """Show save template popup."""
        summary_popup.dismiss()

        # Build session data from current workout
        session_data = {
            "day_type": "Gym",
            "focus": self.workout_name,
            "exercises": []
        }
        for ex in self.exercises_data:
            session_data["exercises"].append({
                "exercise_id": ex.get('id', ''),
                "exercise_name": ex.get('name', ''),
                "target_sets": ex.get('sets', 3),
                "target_reps": ex.get('reps', 10),
                "category": ex.get('muscle', ''),
                "equipment": ex.get('equip', ''),
            })

        from template_view import TemplateView
        tv = TemplateView()
        tv.show_save_popup(session_data, on_save_callback=lambda: self._on_template_saved())

    def _on_template_saved(self):
        """Called after template is saved."""
        if hasattr(self.ids, 'lbl_sync_status'):
            self.ids.lbl_sync_status.text = "Template saved!"
        self.go_back_to_calendar()

    def _close_and_return(self, popup):
        popup.dismiss()
        self.go_back_to_calendar()

    def go_back_to_calendar(self):
        try:
            from kivy.app import App
            app = App.get_running_app()
            if hasattr(app, 'sm'):
                app.sm.current = 'calendar'
        except Exception as e:
            print(f"[Nav Error] {e}")

    # ═══════════════════════════════════════════════════════════════
    #  FORM HELP
    # ═══════════════════════════════════════════════════════════════
    def _show_form_tip(self, ex_idx):
        """Show form tips for a specific exercise."""
        if ex_idx >= len(self.exercises_data):
            return
        ex = self.exercises_data[ex_idx]

        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.button import Button

        content = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(15))
        content.add_widget(Label(
            text="FORM GUIDANCE", font_size='18sp', bold=True,
            color=(0.0, 0.8, 1.0, 1), size_hint_y=None, height=dp(30)
        ))
        content.add_widget(Label(
            text=ex.get('name', 'Exercise'), font_size='16sp', bold=True,
            color=(1, 1, 1, 1), size_hint_y=None, height=dp(25)
        ))
        content.add_widget(Label(
            text=f"Muscle: {ex.get('muscle', '?')} | Equipment: {ex.get('equip', '?')}",
            font_size='13sp', color=(0.7, 0.7, 0.7, 1), size_hint_y=None, height=dp(20)
        ))
        content.add_widget(Label(
            text=ex.get('tip', 'Focus on proper form and controlled movement.'),
            font_size='15sp', bold=True, color=(0.2, 1.0, 0.6, 1),
            halign='center', text_size=(dp(280), None), size_hint_y=None, height=dp(50)
        ))
        cues = "- Keep your core braced\n- Breathe out on exertion\n- Control the negative\n- Stop if sharp pain"
        content.add_widget(Label(
            text=cues, font_size='13sp', color=(0.8, 0.8, 0.8, 1),
            halign='left', text_size=(dp(280), None), size_hint_y=None, height=dp(75)
        ))

        btn = Button(
            text="GOT IT", bold=True, font_size='14sp',
            size_hint_y=None, height=dp(45),
            background_normal='', background_down='',
            background_color=(0, 0, 0, 0), color=(0.07, 0.07, 0.07, 1)
        )
        with btn.canvas.before:
            from kivy.app import App
            app = App.get_running_app()
            Color(0.0, 0.9, 1.0, 1)
            RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(14)])
        btn.bind(pos=lambda inst, val: self._draw_cyan_pill(inst))
        btn.bind(size=lambda inst, val: self._draw_cyan_pill(inst))
        content.add_widget(btn)

        popup = Popup(
            title="", content=content, size_hint=(0.9, None), height=dp(370),
            auto_dismiss=False, background_color=(0.1, 0.1, 0.1, 0.95)
        )
        btn.bind(on_press=popup.dismiss)
        popup.open()

    def _draw_cyan_pill(self, inst):
        inst.canvas.before.clear()
        with inst.canvas.before:
            Color(0.0, 0.9, 1.0, 1)
            RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(14)])

    def toggle_handsfree_microphone(self):
        pass

    # ═══════════════════════════════════════════════════════════════
    #  LAST TIME YOU DID... - Format previous performance
    # ═══════════════════════════════════════════════════════════════
    def _format_last_performance(self, perf):
        """Format the last performance into a readable string."""
        ptype = perf.get('type', 'strength')
        if ptype == 'cardio':
            dist = perf.get('distance', '?')
            return f"Last time: {dist}"
        elif perf.get('weight') == 'BW':
            reps = perf.get('reps', '?')
            return f"Last time: {reps} reps (bodyweight)"
        else:
            weight = perf.get('weight', '?')
            reps = perf.get('reps', '?')
            return f"Last time: {weight} x {reps} reps"

    def _draw_swap_bg(self, inst):
        inst.canvas.before.clear()
        with inst.canvas.before:
            Color(1.0, 0.43, 0.0, 0.15)
            RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(10)])

    # ═══════════════════════════════════════════════════════════════
    #  SMART EXERCISE SUBSTITUTION
    # ═══════════════════════════════════════════════════════════════
    def _show_swap_options(self, ex_idx):
        """Show alternative exercises for the given exercise."""
        if ex_idx >= len(self.exercises_data):
            return

        ex = self.exercises_data[ex_idx]
        ex_id = ex.get('id', '')
        ex_name = ex.get('name', 'Exercise')

        from exercise_db import get_alternatives, get_all_exercises
        all_ex = get_all_exercises()

        # Get user's available equipment from profile
        available_equip = ['barbell', 'dumbbells', 'bench', 'bodyweight', 'machine', 'cables']
        try:
            import json, os
            profile_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_profile.json')
            if os.path.exists(profile_path):
                with open(profile_path, 'r') as f:
                    profile = json.load(f)
                env = profile.get('environment', 'commercial')
                if env == 'home_gym':
                    available_equip = ['barbell', 'dumbbells', 'bench', 'bodyweight']
                elif env == 'cardio_only':
                    available_equip = ['none', 'cardio']
        except:
            pass

        # Get alternatives
        alt_ids = get_alternatives(ex_id, available_equip) if ex_id else []
        alternatives = []
        for aid in alt_ids:
            if aid in all_ex:
                alternatives.append((aid, all_ex[aid]))

        if not alternatives:
            # No alternatives found - show message
            from kivy.uix.popup import Popup
            from kivy.uix.label import Label
            from kivy.uix.button import Button

            content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(15))
            content.add_widget(Label(
                text="NO ALTERNATIVES", font_size='16sp', bold=True,
                color=(1.0, 0.43, 0.0, 1), size_hint_y=None, height=dp(30)
            ))
            content.add_widget(Label(
                text=f"No alternatives found for {ex_name} with your current equipment.",
                font_size='13sp', color=(0.7, 0.7, 0.7, 1),
                size_hint_y=None, height=dp(40)
            ))
            btn = Button(
                text="OK", bold=True, font_size='14sp',
                size_hint_y=None, height=dp(42),
                background_normal='', background_down='',
                background_color=(0, 0, 0, 0), color=(0.07, 0.07, 0.07, 1)
            )
            with btn.canvas.before:
                from kivy.app import App
                app = App.get_running_app()
                Color(*app.accent_color)
                RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(14)])
            btn.bind(pos=lambda inst, val: self._draw_accent_pill(inst))
            btn.bind(size=lambda inst, val: self._draw_accent_pill(inst))
            content.add_widget(btn)
            popup = Popup(
                title="", content=content, size_hint=(0.85, None), height=dp(170),
                auto_dismiss=False, background_color=(0.1, 0.1, 0.1, 0.95)
            )
            btn.bind(on_press=popup.dismiss)
            popup.open()
            return

        # Build alternatives popup
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.button import Button

        content = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(15))
        content.add_widget(Label(
            text="SWAP EXERCISE", font_size='16sp', bold=True,
            color=(1.0, 0.43, 0.0, 1), size_hint_y=None, height=dp(28)
        ))
        content.add_widget(Label(
            text=f"Replacing: {ex_name}", font_size='13sp',
            color=(0.7, 0.7, 0.7, 1), size_hint_y=None, height=dp(22)
        ))

        for alt_id, alt_ex in alternatives[:5]:  # Max 5 alternatives
            alt_name = alt_ex.get('name', 'Unknown')
            alt_muscle = alt_ex.get('muscle', '')
            alt_equip = alt_ex.get('equip', '')

            alt_btn = Button(
                text=f"{alt_name}", font_size='13sp', bold=True,
                size_hint_y=None, height=dp(42),
                background_normal='', background_down='',
                background_color=(0, 0, 0, 0),
                color=(1, 1, 1, 1)
            )
            with alt_btn.canvas.before:
                Color(0.18, 0.18, 0.18, 1)
                RoundedRectangle(pos=alt_btn.pos, size=alt_btn.size, radius=[dp(12)])
            alt_btn.bind(pos=lambda inst, val: self._draw_row_bg(inst))
            alt_btn.bind(size=lambda inst, val: self._draw_row_bg(inst))
            _ex_idx = ex_idx
            _alt_name = alt_name
            alt_btn.bind(on_press=lambda x, i=_ex_idx, n=_alt_name: self._apply_swap(i, n))
            content.add_widget(alt_btn)

        cancel_btn = Button(
            text="CANCEL", bold=True, font_size='13sp',
            size_hint_y=None, height=dp(38),
            background_normal='', background_down='',
            background_color=(0, 0, 0, 0), color=(0.6, 0.6, 0.6, 1)
        )
        content.add_widget(cancel_btn)

        popup = Popup(
            title="", content=content, size_hint=(0.85, None),
            height=min(dp(350), dp(120) + len(alternatives) * dp(46)),
            auto_dismiss=False, background_color=(0.1, 0.1, 0.1, 0.95)
        )
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def _apply_swap(self, ex_idx, new_exercise_name):
        """Replace an exercise in the current workout."""
        if ex_idx >= len(self.exercises_data):
            return

        # Close any open popup
        from kivy.uix.popup import Popup
        for child in self.window.children if hasattr(self, 'window') else []:
            if isinstance(child, Popup):
                child.dismiss()

        # Update the exercise data
        from exercise_db import get_all_exercises
        all_ex = get_all_exercises()
        new_ex = None
        for eid, ex in all_ex.items():
            if ex.get('name', '').lower() == new_exercise_name.lower():
                new_ex = ex.copy()
                new_ex['id'] = eid
                break

        if new_ex:
            self.exercises_data[ex_idx] = new_ex
            print(f"[Workout] Swapped exercise {ex_idx} to: {new_exercise_name}")

            # Rebuild the entire sheet to reflect the change
            self._rebuild_sheet()

    def _rebuild_sheet(self):
        """Rebuild the workout sheet after an exercise swap."""
        self.set_widgets = {}
        self.exercise_cards = []
        self._build_workout_sheet()

        # Update progress counters (keep logged sets count)
        self.total_sets = sum(ex.get('sets', 3) for ex in self.exercises_data)
        if hasattr(self.ids, 'lbl_sets_completed'):
            self.ids.lbl_sets_completed.text = f"Sets: {self.completed_sets}/{self.total_sets}"

    # ═══════════════════════════════════════════════════════════════
    #  EXERCISE SWAP (legacy alias)
    # ═══════════════════════════════════════════════════════════════
    def trigger_alternative_exercise_swap(self):
        pass
