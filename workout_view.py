# workout_view.py - Single-page scrollable Active Workout Sheet
# All exercises visible at once, checkmark to log sets, floating rest timer
import os
import json
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle, Line
_POPUP_BG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'popup_bg.png')

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
        self._is_editing = False        # True when editing a past workout
        self.total_sets = 0
        self.completed_sets = 0
        self.workout_name = "Workout"
        self._scroll_anim = None
        self._workout_history = self._load_workout_history()
        self._history_date = None      # Date when workout was completed
        self._history_sets = []        # Sets from completed session
        self._history_elapsed = 0      # Duration of completed session

    def _update_progress_bar(self):
        """Update the bottom progress bar fill width."""
        try:
            fill = self.ids.get('progress_bar_fill')
            if fill and self.total_sets > 0:
                ratio = min(self.completed_sets / self.total_sets, 1.0)
                fill.canvas.before.clear()
                from kivy.graphics import Color, RoundedRectangle
                from kivy.metrics import dp as _dp
                with fill.canvas.before:
                    Color(0.07, 0.82, 0.45, 1)
                    RoundedRectangle(
                        pos=fill.pos,
                        size=(fill.width * ratio, fill.height),
                        radius=[_dp(2)]
                    )
        except Exception:
            pass


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

    def _check_history_for_date(self, workout_name, workout_date=None):
        """
        Check if this workout was already completed on the specified date.
        If no date provided, defaults to today.
        Returns (is_completed, elapsed_seconds, sets_list) if found.
        """
        from datetime import datetime
        if workout_date is None:
            workout_date = datetime.now().strftime('%Y-%m-%d')
        
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
                # Look for the specified date's completion with matching workout name
                for entry in completions:
                    if entry.get('date') == workout_date and entry.get('workout_name') == workout_name:
                        return True, entry.get('elapsed', 0), entry.get('sets', [])
        except Exception as e:
            print(f"[Workout] History check error: {e}")
        return False, 0, []

    def _save_completion(self):
        """Save workout completion record."""
        from datetime import datetime
        # Use the workout's date if editing a past workout, otherwise today
        # Use the scheduled workout date, not today's date
        save_date = self._history_date or getattr(self, '_workout_date', None) or datetime.now().strftime('%Y-%m-%d')
        
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
            
            # Determine day_of_week from the workout date
            try:
                day_of_week = datetime.strptime(save_date, '%Y-%m-%d').weekday()
            except (ValueError, TypeError):
                day_of_week = -1

            # Determine workout mode from the calendar
            workout_mode = 'ai'
            try:
                from kivy.app import App
                app = App.get_running_app()
                if hasattr(app, 'sm'):
                    cal = app.sm.get_screen('calendar')
                    if hasattr(cal, 'children') and cal.children:
                        cw = cal.children[0]
                        if hasattr(cw, 'workout_mode'):
                            workout_mode = cw.workout_mode
            except Exception:
                pass

            # Remove existing entry for same date + same day_of_week + same mode
            # This allows different scheduled days (e.g. Thursday vs Tuesday)
            # to coexist even if done on the same actual day
            completions = [
                c for c in completions
                if not (c.get('date') == save_date
                        and c.get('day_of_week', -1) == day_of_week
                        and c.get('workout_mode', 'ai') == workout_mode)
            ]
            
            # Determine day_of_week from the workout date
            try:
                day_of_week = datetime.strptime(save_date, '%Y-%m-%d').weekday()
            except (ValueError, TypeError):
                day_of_week = -1

            exercise_names = [ex.get('name', '') for ex in self.exercises_data if ex.get('name')]

            # Add new completion
            completions.append({
                'date': save_date,
                'day_of_week': day_of_week,
                'workout_name': self.workout_name,
                'workout_mode': workout_mode,
                'elapsed': self.workout_elapsed,
                'sets': self.logged_sets,
                'completed_sets': self.completed_sets,
                'total_sets': self.total_sets,
                'exercises': exercise_names
            })
            
            with open(completions_path, 'w') as f:
                json.dump(completions, f, indent=2)
            print(f"[Workout] Saved completion for {self.workout_name} on {save_date}")
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
        self._update_progress_bar()
        
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
            logged_val = None
            for s in self._history_sets:
                if s.get('exercise') == self.exercises_data[ex_idx].get('name', '') and \
                   s.get('set') == set_idx + 1:
                    was_logged = True
                    logged_val = s.get('reps') or s.get('distance')
                    break
            
            if was_logged:
                # Mark as completed and show the actual logged value
                info['logged'] = True
                self._set_tick(info['check'], True)
                info['check'].color = (0.2, 1.0, 0.6, 1)
                info['check'].disabled = True
                info['check'].canvas.before.clear()
                with info['check'].canvas.before:
                    Color(0.3, 0.3, 0.3, 1)
                    RoundedRectangle(pos=info['check'].pos, size=info['check'].size, radius=[dp(12)])
                info['row'].canvas.before.clear()
                with info['row'].canvas.before:
                    Color(0.15, 0.15, 0.15, 0.5)
                    RoundedRectangle(pos=info['row'].pos, size=info['row'].size, radius=[dp(10)])
                # Display the actual logged reps/distance, not the default range
                if logged_val:
                    info['input'].text = logged_val
                info['input'].color = (0.4, 0.4, 0.4, 1)
            else:
                # Not logged - disable the checkmark
                info['check'].disabled = True
                self._set_tick(info['check'], False)
                info['check'].canvas.before.clear()
                with info['check'].canvas.before:
                    Color(0.2, 0.2, 0.2, 1)
                    RoundedRectangle(pos=info['check'].pos, size=info['check'].size, radius=[dp(12)])
                info['check'].color = (0.3, 0.3, 0.3, 1)

    def toggle_edit_mode(self):
        """Switch from history mode to edit mode — re-enable all sets for editing."""
        self.screen_mode = 'active'
        self.workout_active = True
        self._is_editing = True
        self.logged_sets = list(self._history_sets)
        self.completed_sets = len(self.logged_sets)

        # Hide the START button — we're editing, not starting fresh
        if hasattr(self.ids, 'btn_start'):
            self.ids.btn_start.opacity = 0
            self.ids.btn_start.disabled = True
            self.ids.btn_start.height = 0
            self.ids.btn_start.size_hint_y = None

        # Don't restart the timer — editing an old workout

        # Update status
        if hasattr(self.ids, 'lbl_sync_status'):
            self.ids.lbl_sync_status.text = "Editing — tap + to change reps"
        if hasattr(self.ids, 'lbl_sets_completed'):
            self.ids.lbl_sets_completed.text = f"Sets: {self.completed_sets}/{self.total_sets}"
        self._update_progress_bar()

        # Re-enable ALL checkmarks and inputs (logged + unlogged)
        from kivy.app import App
        app = App.get_running_app()
        for key, info in self.set_widgets.items():
            info['check'].disabled = False
            self._set_tick(info['check'], False)
            info['check'].text = "EDIT" if info['logged'] else "+"
            info['check'].font_size = '10sp' if info['logged'] else '20sp'
            info['check'].canvas.before.clear()
            with info['check'].canvas.before:
                Color(*app.accent_color)
                RoundedRectangle(pos=info['check'].pos, size=info['check'].size, radius=[dp(12)])
            info['check'].color = (0.07, 0.07, 0.07, 1)
            # Re-enable the input field so reps can be changed
            info['input'].color = (1, 1, 1, 1)
            info['input'].disabled = False
            # Reset row background
            info['row'].canvas.before.clear()
            with info['row'].canvas.before:
                Color(*app.card_bg)
                RoundedRectangle(pos=info['row'].pos, size=info['row'].size, radius=[dp(10)])

    # ═══════════════════════════════════════════════════════════════
    #  LOAD EXERCISES - Build the entire scrollable sheet
    # ═══════════════════════════════════════════════════════════════
    def load_exercises(self, exercise_list, workout_name="Workout", workout_date=None):
        """Build the full scrollable workout sheet from exercise list."""
        self.workout_name = workout_name
        self.exercises_data = []
        self.logged_sets = []
        self.set_widgets = {}
        self.completed_sets = 0
        self.workout_active = False
        self.workout_elapsed = 0
        self._is_editing = False

        if self.timer_event:
            self.timer_event.cancel()
        if self.rest_timer_event:
            self.rest_timer_event.cancel()
        if self._scroll_anim:
            self._scroll_anim.cancel(self)
            self._scroll_anim = None

        # Restore START button (edit mode may have hidden it)
        if hasattr(self.ids, 'btn_start'):
            self.ids.btn_start.opacity = 1
            self.ids.btn_start.disabled = False
            self.ids.btn_start.height = dp(56)
            self.ids.btn_start.size_hint_y = None

        from exercise_db import get_all_exercises
        all_ex = get_all_exercises()

        # Build exercise data list — supports both strings and dicts
        for item in exercise_list:
            # Handle dict (with superset_id) or string (name only)
            if isinstance(item, dict):
                ex_name = item.get('name', '')
                superset_id = item.get('superset_id')
            else:
                ex_name = str(item)
                superset_id = None

            ex_info = None
            for eid, ex in all_ex.items():
                if ex.get('name', '').lower() == ex_name.lower():
                    ex_info = ex.copy()
                    ex_info['id'] = eid
                    break
            if not ex_info:
                ex_info = {
                    'name': ex_name, 'muscle': 'Unknown', 'equip': 'Unknown', 'track': 'strength', 'sets': 3, 'reps': 10,
                    'equip_tags': [], 'tip': 'Focus on proper form'
                }
            # Preserve superset pairing
            if superset_id:
                ex_info['superset_id'] = superset_id
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

        # Store the workout date for saving later (scheduled day, not today)
        self._workout_date = workout_date

        # Check if this workout was already completed on the specified date
        is_completed, elapsed, sets = self._check_history_for_date(workout_name, workout_date)
        if is_completed:
            self.screen_mode = 'history'
            self._history_date = workout_date
            self._history_sets = sets
            self._history_elapsed = elapsed
            print(f"[Workout] Found completed workout for {workout_date} - entering history mode")
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

        # Detect supersets
        superset_map = self._detect_supersets()

        for ex_idx, ex in enumerate(self.exercises_data):
            card = self._build_exercise_card(ex_idx, ex, superset_map)
            self.exercise_cards.append(card)
            container.add_widget(card)

        scroll.add_widget(container)

        # Always start a freshly-loaded workout at the top of the list
        Clock.schedule_once(lambda dt: setattr(scroll, 'scroll_y', 1.0), 0.05)

    def _detect_supersets(self):
        """
        Detect superset pairs in the exercise list.
        Returns dict: {ex_idx: {'letter': 'A', 'position': 1, 'pair_size': 2}}
        """
        superset_map = {}
        current_letter = None
        current_pair = []
        next_letter_idx = 0

        def _close_pair():
            nonlocal next_letter_idx
            if len(current_pair) == 2:
                letter = chr(ord('A') + next_letter_idx)
                next_letter_idx += 1
                for i, pi in enumerate(current_pair):
                    superset_map[pi] = {
                        'letter': letter,
                        'position': i + 1,
                        'pair_size': 2
                    }
            elif len(current_pair) == 1:
                superset_map.pop(current_pair[0], None)

        for idx, ex in enumerate(self.exercises_data):
            sid = ex.get('superset_id')
            if sid is not None:
                if current_letter == sid:
                    current_pair.append(idx)
                else:
                    _close_pair()
                    current_letter = sid
                    current_pair = [idx]
            else:
                _close_pair()
                current_letter = None
                current_pair = []

        _close_pair()
        return superset_map

    def _build_exercise_card(self, ex_idx, ex, superset_map=None):
        """Build a single exercise card with all its set rows."""
        from kivy.app import App
        app = App.get_running_app()

        if superset_map is None:
            superset_map = {}

        track = ex.get('track', 'strength')
        name = ex.get('name', 'Exercise')
        muscle = ex.get('muscle', '')
        equip = ex.get('equip', '')
        num_sets = ex.get('sets', 3)
        default_reps = ex.get('reps', 10)

        is_cardio = track == 'cardio'
        is_strength = track == 'strength'

        # Superset info
        ss_info = superset_map.get(ex_idx)
        is_superset = ss_info is not None
        ss_label = f"{ss_info['letter']}{ss_info['position']}" if is_superset else ""

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
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(36), spacing=dp(6))

        # Superset badge (A1, A2, B1, B2, etc.)
        if is_superset:
            ss_color = (0.2, 0.7, 0.9, 1) if ss_info['position'] == 1 else (0.9, 0.5, 0.2, 1)
            ss_bg = (0.2, 0.7, 0.9, 0.2) if ss_info['position'] == 1 else (0.9, 0.5, 0.2, 0.2)
            ss_badge = Label(
                text=ss_label, font_size='11sp', bold=True,
                color=ss_color, size_hint=(None, None),
                size=(dp(30), dp(28)), halign='center', valign='middle'
            )
            with ss_badge.canvas.before:
                Color(*ss_bg)
                RoundedRectangle(pos=ss_badge.pos, size=ss_badge.size, radius=[dp(8)])
            ss_badge.bind(pos=lambda inst, val: self._draw_ss_bg(inst, ss_bg))
            ss_badge.bind(size=lambda inst, val: self._draw_ss_bg(inst, ss_bg))
            header.add_widget(ss_badge)

        name_label = Label(
            text=name, font_size='16sp', bold=True, color=(1, 1, 1, 1),
            halign='left', valign='middle',
            shorten=True, shorten_from='right', markup=False,
            size_hint_x=1.0
        )
        # Bind text_size to available width so it wraps/truncates correctly
        name_label.bind(width=lambda inst, val: setattr(inst, 'text_size', (val - dp(4), None)))
        header.add_widget(name_label)
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

        # PR badge for all strength exercises
        if is_strength and not is_cardio:
            best_reps = self._get_best_total_reps(name)
            if best_reps > 0:
                pr_label = Label(
                    text=f"PR: {best_reps}", font_size='9sp', bold=True,
                    color=(1.0, 0.84, 0.0, 1), size_hint=(None, None),
                    size=(dp(50), dp(22)), halign='center', valign='middle'
                )
                with pr_label.canvas.before:
                    Color(1.0, 0.84, 0.0, 0.15)
                    RoundedRectangle(pos=pr_label.pos, size=pr_label.size, radius=[dp(8)])
                pr_label.bind(pos=lambda inst, val: self._draw_pr_bg(inst))
                pr_label.bind(size=lambda inst, val: self._draw_pr_bg(inst))
                header.add_widget(pr_label)

        card.add_widget(header)

        # Subtitle line
        subtitle = f"{muscle} | {equip}" if not is_cardio else f"{muscle} | Cardio"
        sub_label = Label(
            text=subtitle, font_size='11sp', color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None, height=dp(18), halign='left', valign='middle'
        )
        sub_label.bind(width=lambda inst, val: setattr(inst, 'text_size', (val - dp(4), None)))
        card.add_widget(sub_label)

        # ─── LAST TIME YOU DID... ───
        last_perf = self._get_last_performance(name)
        if last_perf:
            last_text = self._format_last_performance(last_perf, name)
            last_label = Label(
                text=last_text, font_size='11sp', bold=True,
                color=(app.accent_color[0], app.accent_color[1], app.accent_color[2], 0.8),
                size_hint_y=None, height=dp(18), halign='left', valign='middle'
            )
            last_label.bind(width=lambda inst, val: setattr(inst, 'text_size', (val - dp(4), None)))
            card.add_widget(last_label)
            # Increase card height for the extra line
            card.height += dp(18)
        else:
            no_data_label = Label(
                text="", font_size='11sp',
                color=(0.4, 0.4, 0.4, 1),
                size_hint_y=None, height=dp(0), halign='left', valign='middle'
            )
            no_data_label.bind(width=lambda inst, val: setattr(inst, 'text_size', (val - dp(4), None)))
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

        # ─── Column headers (must match set row widths exactly) ───
        col_header = BoxLayout(size_hint_y=None, height=dp(22), spacing=dp(6))
        col_header.add_widget(Label(text="SET", font_size='10sp', bold=True, color=(0.4, 0.4, 0.4, 1),
                                     size_hint_x=None, width=dp(30), halign='left', padding=[dp(4), 0]))
        if is_cardio:
            col_header.add_widget(Label(text="DISTANCE", font_size='10sp', bold=True, color=(0.4, 0.4, 0.4, 1),
                                         size_hint_x=None, width=dp(60), halign='left'))
            col_header.add_widget(Label(text="PACE", font_size='10sp', bold=True, color=(0.4, 0.4, 0.4, 1),
                                         size_hint_x=1, halign='left'))
        else:
            col_header.add_widget(Label(text="REPS", font_size='10sp', bold=True, color=(0.4, 0.4, 0.4, 1),
                                         size_hint_x=1, halign='left'))
        col_header.add_widget(Label(text="", size_hint_x=None, width=dp(44)))
        card.add_widget(col_header)

        # ─── Set rows ───
        for set_idx in range(num_sets):
            row = self._build_set_row(ex_idx, set_idx, ex, is_cardio, default_reps)
            card.add_widget(row)

        return card

    def _build_set_row(self, ex_idx, set_idx, ex, is_cardio, default_reps):
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

        # Set number label (matches header: width=dp(30), left-aligned)
        set_label = Label(
            text=f"{set_idx + 1}", font_size='14sp', bold=True,
            color=(0.6, 0.6, 0.6, 1), size_hint_x=None, width=dp(30),
            halign='left', padding=[dp(4), 0]
        )
        row.add_widget(set_label)

        # Input field (fills remaining space, left-aligned)
        if is_cardio:
            input_label = Label(
                text="0.00 km", font_size='15sp', bold=True,
                color=(1, 1, 1, 1), size_hint_x=1, halign='left'
            )
        else:
            input_label = Label(
                text=f"{default_reps} reps", font_size='15sp', bold=True,
                color=(1, 1, 1, 1), size_hint_x=1, halign='left'
            )
        row.add_widget(input_label)

        # Checkmark button (matches header spacer: width=dp(44))
        check_btn = Button(
            text="+", font_size='20sp', bold=True,
            size_hint=(None, None), size=(dp(44), dp(40)),
            background_normal='', background_down='',
            background_color=(0, 0, 0, 0),
            color=(0.07, 0.07, 0.07, 1)
        )
        check_btn.ticked = False
        with check_btn.canvas.before:
            Color(*app.accent_color)
            RoundedRectangle(pos=check_btn.pos, size=check_btn.size, radius=[dp(12)])
        check_btn.bind(pos=lambda inst, val: self._draw_check_bg(inst))
        check_btn.bind(size=lambda inst, val: self._draw_check_bg(inst))
        check_btn.bind(pos=lambda inst, val: self._redraw_tick_if_needed(inst))
        check_btn.bind(size=lambda inst, val: self._redraw_tick_if_needed(inst))
        check_btn.bind(on_press=lambda x, k=row_key: self._log_set_checkmark(k))
        row.add_widget(check_btn)

        # Store references
        self.set_widgets[row_key] = {
            'row': row,
            'label': set_label,
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

    def _set_tick(self, btn, show):
        """Show/hide the completed-set tick as canvas lines (no font glyph)."""
        btn.ticked = show
        if show:
            btn.text = ""
        self._draw_tick(btn)

    def _draw_tick(self, btn):
        """Draw (or clear) the green tick on a check button."""
        btn.canvas.after.clear()
        if not getattr(btn, 'ticked', False):
            return
        x, y = btn.pos
        w, h = btn.size
        with btn.canvas.after:
            Color(0.2, 1.0, 0.6, 1)
            Line(
                points=[x + w * 0.40, y + h * 0.52,
                        x + w * 0.50, y + h * 0.42,
                        x + w * 0.63, y + h * 0.64],
                width=dp(1.2), cap='square', joint='miter'
            )

    def _redraw_tick_if_needed(self, inst, *args):
        if getattr(inst, 'ticked', False):
            self._draw_tick(inst)

    def _draw_btn_bg(self, inst, alpha):
        from kivy.app import App
        app = App.get_running_app()
        inst.canvas.before.clear()
        with inst.canvas.before:
            Color(app.accent_color[0], app.accent_color[1], app.accent_color[2], alpha)
            RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(12)])

    def _check_prs(self):
        """Check if any exercises set a new PR. Returns list of PR lines."""
        from collections import defaultdict
        session_totals = defaultdict(int)
        for s in self.logged_sets:
            if s.get('type') == 'strength':
                reps_text = s.get('reps', '0')
                try:
                    reps = int(str(reps_text).replace(' reps', '').strip())
                except (ValueError, TypeError):
                    reps = 0
                session_totals[s.get('exercise', '')] += reps

        pr_lines = []
        for ex_name, total in session_totals.items():
            if total <= 0:
                continue
            best = self._get_best_total_reps(ex_name)
            if best > 0 and total > best:
                pr_lines.append(f"NEW PR! {ex_name}: {total} reps (was {best})")
            elif best == 0 and total > 0:
                pr_lines.append(f"BASELINE SET! {ex_name}: {total} reps")
        return pr_lines

    def _draw_pr_bg(self, inst):
        inst.canvas.before.clear()
        with inst.canvas.before:
            Color(1.0, 0.84, 0.0, 0.15)
            RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(8)])

    def _draw_ss_bg(self, inst, color):
        inst.canvas.before.clear()
        with inst.canvas.before:
            Color(*color)
            RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(8)])

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
        if not info:
            return

        # If already logged, un-mark it so user can edit reps (edit mode only)
        if info['logged']:
            if self._is_editing:
                # In edit mode — show popup to change reps
                self._show_edit_reps_popup(info)
                return
            else:
                # In active mode — already logged, skip
                return

        ex_idx = info['exercise_idx']
        set_idx = info['set_idx']
        ex = self.exercises_data[ex_idx]
        track = ex.get('track', 'strength')

        # Mark as logged visually
        info['logged'] = True
        self._set_tick(info['check'], True)
        info['check'].color = (0.2, 1.0, 0.6, 1)
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
            set_data['reps'] = info['input'].text
        self.logged_sets.append(set_data)

        self.completed_sets += 1
        if hasattr(self.ids, 'lbl_sync_status'):
            self.ids.lbl_sync_status.text = f"Set logged! ({self.completed_sets}/{self.total_sets})"
        if hasattr(self.ids, 'lbl_sets_completed'):
            self.ids.lbl_sets_completed.text = f"Sets: {self.completed_sets}"
        self._update_progress_bar()

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
            # Vibrate at 3 seconds remaining (short buzz)
            if self.rest_time_left == 3:
                self._android_vibrate(200)
        else:
            if self.rest_timer_event:
                self.rest_timer_event.cancel()
            # Vibrate when rest is complete (long buzz)
            self._android_vibrate(500)
            # Hide banner
            if hasattr(self.ids, 'rest_banner'):
                self.ids.rest_banner.opacity = 0
                self.ids.rest_banner.disabled = True
                self.ids.rest_banner.height = 0
                self.ids.rest_banner.size_hint_y = None
            if hasattr(self.ids, 'lbl_sync_status'):
                self.ids.lbl_sync_status.text = "Rest over! Next set ready"

    def _android_vibrate(self, ms):
        """Trigger haptic vibration on Android (no-op on other platforms)."""
        try:
            from kivy.utils import platform
            if platform != 'android':
                return
            from jnius import autoclass
            activity = autoclass('org.kivy.android.PythonActivity').mActivity
            vibrator = activity.getSystemService('vibrator')
            if vibrator is None:
                return
            try:
                # API 26+: use VibrationEffect (required on modern Android)
                VibrationEffect = autoclass('android.os.VibrationEffect')
                vibrator.vibrate(VibrationEffect.createOneShot(int(ms), -1))
            except Exception:
                # Legacy fallback
                vibrator.vibrate(int(ms))
        except Exception:
            pass

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
        
        To bring widget_top near the top of the viewport:
          scroll_y = (widget_top - (view_h * 0.85)) / max_scroll
          (0.85 = place widget top at 15% from viewport top)
        """
        try:
            content_height = container.height
            view_height = scroll.height

            if content_height <= view_height:
                return 0.5  # Content fits, no scrolling needed

            max_scroll = content_height - view_height
            if max_scroll <= 0:
                return 0.5

            # Widget's top edge in container coordinates (from bottom)
            widget_top = target_widget.y + target_widget.height

            # Place widget top 15% from the TOP of the viewport
            # In Kivy coords: 15% from top = 85% from bottom = view_height * 0.85
            target_from_bottom = view_height * 0.85

            # Kivy formula: scroll_y * max_scroll = viewport bottom from content bottom
            # widget_top - scroll_y * max_scroll = widget pos from viewport bottom
            # We want widget pos from viewport bottom = target_from_bottom
            scroll_y = (widget_top - target_from_bottom) / max_scroll

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
        with content.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0.1, 0.1, 0.1, 1)
            Rectangle(pos=content.pos, size=content.size)
        content.bind(pos=lambda inst, val: self._redraw_popup_bg(inst))
        content.bind(size=lambda inst, val: self._redraw_popup_bg(inst))
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

        # Check for PRs
        pr_lines = self._check_prs()
        if pr_lines:
            content.add_widget(Label(
                text="\n".join(pr_lines), font_size='12sp', bold=True,
                color=(1.0, 0.84, 0.0, 1), size_hint_y=None, height=dp(20) * len(pr_lines),
                halign='left', text_size=(dp(280), None)
            ))

        if self.logged_sets:
            lines = []
            for s in self.logged_sets[:10]:
                if s.get('type') == 'cardio':
                    lines.append(f"  {s['exercise']}: {s.get('distance', 'N/A')}")
                else:
                    lines.append(f"  {s['exercise']}: {s.get('reps', '?')} reps")
            if len(self.logged_sets) > 10:
                lines.append(f"  ... +{len(self.logged_sets) - 10} more")
            summary_label = Label(
                text="\n".join(lines), font_size='11sp', color=(0.6, 0.6, 0.6, 1),
                halign='left', text_size=(dp(280), None),
                size_hint_y=None, height=min(dp(140), dp(16) * len(lines))
            )
            content.add_widget(summary_label)

        # Button row: COOL DOWN + BACK TO CALENDAR (or just BACK when editing)
        btn_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        if not self._is_editing:
            cool_btn = Button(
                text="COOL DOWN", bold=True, font_size='13sp',
                background_normal='', background_down='',
                background_color=(0.0, 0.0, 0.0, 0), color=(0.07, 0.07, 0.07, 1)
            )
            with cool_btn.canvas.before:
                Color(0.07, 0.53, 0.3, 1)
                RoundedRectangle(pos=cool_btn.pos, size=cool_btn.size, radius=[dp(25)])
            cool_btn.bind(pos=lambda inst, val: self._draw_pill(inst, (0.07, 0.53, 0.3, 1)))
            cool_btn.bind(size=lambda inst, val: self._draw_pill(inst, (0.07, 0.53, 0.3, 1)))
            btn_row.add_widget(cool_btn)

        cal_btn = Button(
            text="BACK", bold=True, font_size='13sp',
            background_normal='', background_down='',
            background_color=(0, 0, 0, 0), color=(0.07, 0.07, 0.07, 1)
        )
        with cal_btn.canvas.before:
            Color(*app.accent_color)
            RoundedRectangle(pos=cal_btn.pos, size=cal_btn.size, radius=[dp(25)])
        cal_btn.bind(pos=lambda inst, val: self._draw_accent_pill(inst))
        cal_btn.bind(size=lambda inst, val: self._draw_accent_pill(inst))
        btn_row.add_widget(cal_btn)

        content.add_widget(btn_row)

        popup = Popup(
            title="", content=content, size_hint=(0.85, None), height=dp(380),
            auto_dismiss=False, background=_POPUP_BG, background_color=(0.1, 0.1, 0.1, 1),
            separator_height=0
        )
        if not self._is_editing:
            cool_btn.bind(on_press=lambda x: self._go_to_stretch(popup))
        cal_btn.bind(on_press=lambda x: self._close_and_return(popup))
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

    def _redraw_popup_bg(self, inst):
        """Redraw popup content's solid background to prevent overlay blur."""
        inst.canvas.before.clear()
        with inst.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0.1, 0.1, 0.1, 1)
            Rectangle(pos=inst.pos, size=inst.size)

    def _go_to_stretch(self, popup):
        """Navigate to the cool-down stretch timer."""
        popup.dismiss()
        from kivy.app import App
        app = App.get_running_app()
        if hasattr(app, 'sm'):
            app.sm.current = 'stretch'

    def _draw_pill(self, inst, color):
        inst.canvas.before.clear()
        with inst.canvas.before:
            Color(*color)
            RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(25)])

    def _close_and_return(self, popup):
        popup.dismiss()
        self.go_back_to_calendar()

    def go_back_to_calendar(self):
        try:
            from kivy.app import App
            app = App.get_running_app()
            if hasattr(app, 'sm'):
                # Refresh calendar dots and day display when returning
                cal_screen = app.sm.get_screen('calendar')
                if hasattr(cal_screen, 'children') and cal_screen.children:
                    cal_widget = cal_screen.children[0]
                    if hasattr(cal_widget, '_update_completion_dots'):
                        cal_widget._update_completion_dots()
                    if hasattr(cal_widget, 'load_selected_day_schedule'):
                        cal_widget.load_selected_day_schedule(cal_widget.selected_day_index)
                app.sm.current = 'calendar'
        except Exception as e:
            print(f"[Nav Error] {e}")

    # ═══════════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════════
    #  EDIT REPS POPUP
    # ═══════════════════════════════════════════════════════════════
    def _show_edit_reps_popup(self, info):
        """Show a popup to edit reps for a set."""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.app import App
        app = App.get_running_app()

        ex_idx = info['exercise_idx']
        set_idx = info['set_idx']
        ex = self.exercises_data[ex_idx]
        track = ex.get('track', 'strength')
        ex_name = ex.get('name', 'Exercise')

        # Get current value from the label
        current_text = info['input'].text.replace(' reps', '').replace(' km', '').strip()

        content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(20))

        # Title
        content.add_widget(Label(
            text=f"EDIT {ex_name.upper()}", font_size='14sp', bold=True,
            color=app.accent_color, size_hint_y=None, height=dp(30)
        ))
        content.add_widget(Label(
            text=f"Set {set_idx + 1}", font_size='12sp',
            color=(0.6, 0.6, 0.6, 1), size_hint_y=None, height=dp(20)
        ))

        # TextInput
        input_field = TextInput(
            text=current_text, font_size='24sp',
            foreground_color=(1, 1, 1, 1),
            background_color=(0.12, 0.12, 0.12, 1),
            cursor_color=(0.12, 0.12, 0.12, 1),
            selection_color=(0.2, 0.6, 0.4, 0.4),
            size_hint_y=None, height=dp(50),
            halign='center', multiline=False,
            input_filter='int' if track == 'strength' else None,
        )
        content.add_widget(input_field)

        # Unit label
        unit = 'reps' if track == 'strength' else 'km'
        content.add_widget(Label(
            text=unit, font_size='12sp',
            color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=dp(18)
        ))

        # Buttons row
        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))

        cancel_btn = Button(
            text="CANCEL", font_size='13sp', bold=True,
            background_normal='', background_down='',
            background_color=(0.22, 0.22, 0.22, 1),
            color=(0.7, 0.7, 0.7, 1)
        )
        btn_row.add_widget(cancel_btn)

        save_btn = Button(
            text="SAVE", font_size='13sp', bold=True,
            background_normal='', background_down='',
            background_color=(0.07, 0.53, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        btn_row.add_widget(save_btn)

        content.add_widget(btn_row)

        popup = Popup(
            title="", content=content, size_hint=(0.8, None), height=dp(280),
            auto_dismiss=False, background_color=(0.1, 0.1, 0.1, 0.95),
            separator_height=0
        )

        def save_reps(dt=None):
            new_val = input_field.text.strip()
            if not new_val:
                return
            # Update the label text
            info['input'].text = f"{new_val} {unit}"
            # Build new set data
            set_num = info['set_idx'] + 1
            set_data = {
                'exercise': ex_name,
                'set': set_num,
                'type': track,
            }
            if track == 'cardio':
                set_data['distance'] = f"{new_val} km"
                set_data['pace'] = '--'
            else:
                set_data['reps'] = f"{new_val} reps"
            # Find and replace the old entry (case-insensitive, by exercise + set)
            replaced = False
            for i, s in enumerate(self.logged_sets):
                if s.get('set') == set_num and s.get('exercise', '').lower() == ex_name.lower():
                    self.logged_sets[i] = set_data
                    replaced = True
                    break
            if not replaced:
                self.logged_sets.append(set_data)
            self.completed_sets = len(self.logged_sets)
            if hasattr(self.ids, 'lbl_sets_completed'):
                self.ids.lbl_sets_completed.text = f"Sets: {self.completed_sets}/{self.total_sets}"
            self._update_progress_bar()
            # Mark as logged visually
            info['logged'] = True
            self._set_tick(info['check'], True)
            info['check'].color = (0.2, 1.0, 0.6, 1)
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
            popup.dismiss()

        save_btn.bind(on_press=save_reps)
        cancel_btn.bind(on_press=popup.dismiss)
        input_field.bind(on_text_validate=save_reps)
        popup.open()
        # Focus the input and select all text
        input_field.focus = True
        Clock.schedule_once(lambda dt: input_field.select_text(0, len(input_field.text)) if input_field.text else None, 0.2)

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

        # Animated stick-figure demo of the movement
        from stickman import StickmanWidget, archetype_for
        aid = archetype_for(ex.get('name', ''), ex.get('equip', ''), ex.get('muscle', ''))
        stick = StickmanWidget(archetype=aid, size_hint_y=None, height=dp(170))
        content.add_widget(stick)

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
            title="", content=content, size_hint=(0.9, None), height=dp(520),
            auto_dismiss=False, background=_POPUP_BG, background_color=(0.1, 0.1, 0.1, 1),
            separator_height=0
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
    def _get_best_total_reps(self, exercise_name):
        """Get the best total reps across all sets from previous sessions."""
        if not isinstance(self._workout_history, dict):
            return 0
        sessions = self._workout_history.get(exercise_name, [])
        if not sessions:
            return 0
        from collections import defaultdict
        daily_totals = defaultdict(int)
        for s in sessions:
            if s.get('type') == 'strength':
                reps_text = s.get('reps', '0')
                try:
                    reps = int(str(reps_text).replace(' reps', '').strip())
                except (ValueError, TypeError):
                    reps = 0
                date_key = s.get('date', '')[:10]
                daily_totals[date_key] += reps
        if not daily_totals:
            return 0
        return max(daily_totals.values())

    def _format_last_performance(self, perf, ex_name=''):
        """Format the last performance into a readable string."""
        ptype = perf.get('type', 'strength')
        if ptype == 'cardio':
            dist = perf.get('distance', '?')
            return f"Last time: {dist}"
        elif perf.get('type') == 'strength':
            total = self._get_best_total_reps(ex_name)
            if total > 0:
                return f"Best: {total} total reps"
            reps = perf.get('reps', '?')
            return f"Last time: {reps} reps"
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
                auto_dismiss=False, background=_POPUP_BG, background_color=(0.1, 0.1, 0.1, 1),
                separator_height=0
            )
            btn.bind(on_press=popup.dismiss)
            popup.open()
            return

        # Build alternatives popup with search
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.textinput import TextInput
        from exercise_search import search_exercises

        content = BoxLayout(orientation='vertical', spacing=dp(6), padding=dp(15))
        content.add_widget(Label(
            text="SWAP EXERCISE", font_size='16sp', bold=True,
            color=(1.0, 0.43, 0.0, 1), size_hint_y=None, height=dp(24)
        ))
        content.add_widget(Label(
            text=f"Replacing: {ex_name}", font_size='12sp',
            color=(0.7, 0.7, 0.7, 1), size_hint_y=None, height=dp(18)
        ))

        # Search input
        results_list = BoxLayout(orientation='vertical', spacing=dp(4), size_hint_y=None)
        results_list.bind(minimum_height=results_list.setter('height'))

        search_input = TextInput(
            hint_text="Search exercises...", font_size='13sp',
            size_hint_y=None, height=dp(36),
            multiline=False, padding=[dp(10), dp(8)],
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.5, 0.5, 0.5, 1),
            cursor_color=(0.15, 0.15, 0.15, 1),
            border=(0.15, 0.15, 0.15, 1)
        )
        content.add_widget(search_input)

        def update_results(query=''):
            results_list.clear_widgets()
            if query.strip():
                matches = search_exercises(query, all_ex, max_results=12)
            else:
                matches = alternatives[:5]
            for eid, alt_ex in matches:
                alt_name = alt_ex.get('name', 'Unknown')
                alt_btn = Button(
                    text=f"{alt_name}", font_size='12sp', bold=True,
                    size_hint_y=None, height=dp(36),
                    background_normal='', background_down='',
                    background_color=(0, 0, 0, 0),
                    color=(1, 1, 1, 1)
                )
                with alt_btn.canvas.before:
                    Color(0.18, 0.18, 0.18, 1)
                    RoundedRectangle(pos=alt_btn.pos, size=alt_btn.size, radius=[dp(10)])
                alt_btn.bind(pos=lambda inst, val: self._draw_row_bg(inst))
                alt_btn.bind(size=lambda inst, val: self._draw_row_bg(inst))
                _ex_idx = ex_idx
                _alt_name = alt_name
                alt_btn.bind(on_press=lambda x, i=_ex_idx, n=_alt_name: self._apply_swap(i, n))
                results_list.add_widget(alt_btn)

        search_input.bind(text=lambda inst, val: update_results(val))
        update_results()  # Show initial alternatives
        content.add_widget(results_list)

        cancel_btn = Button(
            text="DONE", bold=True, font_size='13sp',
            size_hint_y=None, height=dp(36),
            background_normal='', background_down='',
            background_color=(0, 0, 0, 0), color=(0.6, 0.6, 0.6, 1)
        )
        content.add_widget(cancel_btn)

        popup = Popup(
            title="", content=content, size_hint=(0.88, None),
            height=dp(480),
            auto_dismiss=False, background=_POPUP_BG, background_color=(0.1, 0.1, 0.1, 1),
            separator_height=0
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
        self._update_progress_bar()

    # ═══════════════════════════════════════════════════════════════
    #  EXERCISE SWAP (legacy alias)
    # ═══════════════════════════════════════════════════════════════
    def trigger_alternative_exercise_swap(self):
        pass
