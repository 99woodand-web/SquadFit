# exercise_selection_view.py - Exercise browsing with search, muscle tabs, equipment filters
import json
import os
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import ListProperty, StringProperty
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle

from exercise_db import get_all_exercises, get_muscle_groups, get_equipment_types


class ExerciseSelectionScreen(BoxLayout):
    """Screen for browsing and selecting exercises with search and filters."""

    selected_exercises = ListProperty([])
    current_muscle_filter = StringProperty("All")
    current_equip_filter = StringProperty("All")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.exercise_checkboxes = {}
        self.all_exercises = get_all_exercises()
        self._built = False
        self._suppress_checkbox_events = False  # Flag to prevent _on_checkbox during bulk updates
        Clock.schedule_once(self._init_ui, 0.1)

    def _init_ui(self, dt):
        """Initialize UI elements after KV is loaded."""
        self._load_selected()
        self._build_muscle_tabs()
        self._build_equip_tabs()
        self._build_exercise_list()
        self._built = True

    def _load_selected(self):
        """Load previously selected exercises from profile."""
        try:
            if os.path.exists("user_profile.json"):
                with open("user_profile.json", "r") as f:
                    profile = json.load(f)
                raw = profile.get("selected_exercises", [])
                # Only keep exercise IDs that exist in the current database
                valid_ids = set(self.all_exercises.keys())
                unique = []
                seen = set()
                for eid in raw:
                    if eid in valid_ids and eid not in seen:
                        seen.add(eid)
                        unique.append(eid)
                self.selected_exercises = unique
        except Exception:
            pass

    # ═══════════════════════════════════════════════════════════════
    #  MUSCLE GROUP TABS
    # ═══════════════════════════════════════════════════════════════
    def _build_muscle_tabs(self):
        """Build horizontal scrollable muscle group filter tabs."""
        if not hasattr(self.ids, 'muscle_tabs'):
            return
        container = self.ids.muscle_tabs
        container.clear_widgets()

        muscles = ["All"] + get_muscle_groups()
        for muscle in muscles:
            # Highlight active tab - only the SELECTED muscle gets green
            is_active = (muscle == self.current_muscle_filter)
            btn = Button(
                text=muscle.upper(),
                font_size='10sp',
                bold=True,
                size_hint_x=None,
                width=dp(70),
                background_normal='',
                background_down='',
                background_color=(0, 0, 0, 0),
                color=(0.07, 0.07, 0.07, 1) if is_active else (0.8, 0.8, 0.8, 1)
            )
            from kivy.app import App
            app = App.get_running_app()
            active_color = list(app.accent_color)
            inactive_color = list(app.card_bg)
            bg = active_color if is_active else inactive_color

            with btn.canvas.before:
                Color(*bg)
                RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(12)])

            def _redraw(inst, color=bg):
                inst.canvas.before.clear()
                with inst.canvas.before:
                    Color(*color)
                    RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(12)])

            btn.bind(pos=lambda inst, val, c=bg: _redraw(inst, c))
            btn.bind(size=lambda inst, val, c=bg: _redraw(inst, c))
            btn.bind(on_press=lambda x, m=muscle: self._on_muscle_tab(m))
            container.add_widget(btn)

    def _on_muscle_tab(self, muscle):
        """Handle muscle group tab selection."""
        self.current_muscle_filter = muscle
        self._build_muscle_tabs()  # Rebuild to highlight active tab
        self._build_exercise_list()

    # ═══════════════════════════════════════════════════════════════
    #  EQUIPMENT FILTER
    # ═══════════════════════════════════════════════════════════════
    def _build_equip_tabs(self):
        """Build equipment filter buttons with active state."""
        if not hasattr(self.ids, 'equip_tabs'):
            return
        container = self.ids.equip_tabs
        container.clear_widgets()

        from kivy.app import App
        app = App.get_running_app()

        equip_map = [
            ("All", "All"),
            ("BB", "Barbell"),
            ("DB", "Dumbbells"),
            ("CABLE", "Cable"),
            ("MACH", "Machine"),
            ("BW", "Bodyweight"),
        ]

        for label, equip_key in equip_map:
            is_active = (equip_key == self.current_equip_filter)
            btn = Button(
                text=label,
                font_size='10sp',
                bold=True,
                background_normal='',
                background_down='',
                background_color=(0, 0, 0, 0),
                color=(0.07, 0.07, 0.07, 1) if is_active else (0.8, 0.8, 0.8, 1)
            )
            active_color = list(app.accent_color)
            inactive_color = list(app.card_bg)
            bg = active_color if is_active else inactive_color

            with btn.canvas.before:
                Color(*bg)
                RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(12)])

            def _redraw(inst, color=bg):
                inst.canvas.before.clear()
                with inst.canvas.before:
                    Color(*color)
                    RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(12)])

            btn.bind(pos=lambda inst, val, c=bg: _redraw(inst, c))
            btn.bind(size=lambda inst, val, c=bg: _redraw(inst, c))
            btn.bind(on_press=lambda x, e=equip_key: self.filter_by_equipment(e))
            container.add_widget(btn)

    def filter_by_equipment(self, equip):
        """Filter exercises by equipment type."""
        self.current_equip_filter = equip
        self._build_equip_tabs()  # Rebuild to highlight active tab
        self._build_exercise_list()

    # ═══════════════════════════════════════════════════════════════
    #  SEARCH
    # ═══════════════════════════════════════════════════════════════
    def filter_exercises(self):
        """Called when search text changes."""
        self._build_exercise_list()

    def clear_search(self):
        """Clear search input and reset filters."""
        if hasattr(self.ids, 'search_input'):
            self.ids.search_input.text = ""
        self.current_muscle_filter = "All"
        self.current_equip_filter = "All"
        self._build_muscle_tabs()
        self._build_exercise_list()

    # ═══════════════════════════════════════════════════════════════
    #  EXERCISE LIST
    # ═══════════════════════════════════════════════════════════════
    def _build_exercise_list(self):
        """Build the scrollable exercise list with current filters."""
        if not hasattr(self.ids, 'exercise_container'):
            return

        container = self.ids.exercise_container
        container.clear_widgets()
        self.exercise_checkboxes = {}

        # Get search query
        query = ""
        if hasattr(self.ids, 'search_input'):
            query = self.ids.search_input.text.strip().lower()

        # Filter exercises
        filtered = {}
        for eid, ex in self.all_exercises.items():
            # Muscle filter
            if self.current_muscle_filter != "All":
                if ex.get('muscle', '') != self.current_muscle_filter:
                    continue

            # Equipment filter
            if self.current_equip_filter != "All":
                equip = ex.get('equip', '')
                tags = ex.get('equip_tags', [])
                if equip != self.current_equip_filter and \
                   self.current_equip_filter.lower() not in [t.lower() for t in tags]:
                    continue

            # Search filter
            if query:
                name = ex.get('name', '').lower()
                muscle = ex.get('muscle', '').lower()
                equip = ex.get('equip', '').lower()
                if query not in name and query not in muscle and query not in equip:
                    continue

            filtered[eid] = ex

        # Group by muscle
        muscle_groups = {}
        for eid, ex in filtered.items():
            muscle = ex.get('muscle', 'Other')
            muscle_groups.setdefault(muscle, []).append((eid, ex))

        # Build UI
        for muscle in sorted(muscle_groups.keys()):
            exercises = muscle_groups[muscle]

            # Muscle header
            header = BoxLayout(size_hint_y=None, height=dp(30))
            header.add_widget(Label(
                text=f"{muscle.upper()} ({len(exercises)})",
                font_size='12sp', bold=True,
                color=(0.2, 1.0, 0.6, 1),
                halign='left',
                text_size=(dp(280), None)
            ))
            container.add_widget(header)

            # Exercise rows
            for eid, ex in exercises:
                row = self._build_exercise_row(eid, ex)
                container.add_widget(row)

            # Spacer
            container.add_widget(BoxLayout(size_hint_y=None, height=dp(6)))

        # Update count
        self._update_count()

    def _build_exercise_row(self, exercise_id, exercise):
        """Build a single exercise row with fixed-width columns for alignment."""
        from kivy.app import App
        app = App.get_running_app()

        row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(44),
            spacing=dp(4),
            padding=[dp(4), dp(2)]
        )

        # Column 1: Checkbox (fixed width)
        is_selected = exercise_id in self.selected_exercises
        checkbox = CheckBox(
            size_hint_x=None,
            width=dp(32),
            color=(0.2, 1.0, 0.6, 1),
            active=is_selected
        )
        bind_fn = lambda inst, val, eid=exercise_id: self._on_checkbox(eid, val)
        checkbox.bind(active=bind_fn)
        checkbox._active_bind = bind_fn
        self.exercise_checkboxes[exercise_id] = checkbox
        row.add_widget(checkbox)

        # Column 2: Exercise name (takes remaining space, left-aligned)
        name = exercise.get('name', 'Unknown')
        name_label = Label(
            text=name,
            font_size='13sp', bold=True,
            color=(0.95, 0.95, 0.95, 1),
            halign='left',
            valign='middle',
            padding=[dp(4), 0],
            size_hint_x=0.55
        )
        row.add_widget(name_label)

        # Column 3: Equipment (fixed width, left-aligned)
        equip = exercise.get('equip', '')
        equip_label = Label(
            text=equip,
            font_size='11sp',
            color=(0.6, 0.6, 0.6, 1),
            halign='left',
            valign='middle',
            size_hint_x=0.25
        )
        row.add_widget(equip_label)

        # Column 4: Difficulty badge (fixed width)
        difficulty = exercise.get('difficulty', '')
        diff_label = Label(
            text=difficulty[:3].upper() if difficulty else "",
            font_size='9sp', bold=True,
            color=(0.4, 0.8, 1.0, 1) if difficulty == 'Beginner' else
                   (0.2, 1.0, 0.6, 1) if difficulty == 'Intermediate' else
                   (1.0, 0.4, 0.4, 1),
            halign='center',
            valign='middle',
            size_hint_x=0.15
        )
        row.add_widget(diff_label)

        # Background card
        with row.canvas.before:
            Color(*app.card_bg)
            RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(8)])

        def _redraw_bg(inst):
            inst.canvas.before.clear()
            with inst.canvas.before:
                Color(*app.card_bg)
                RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(8)])

        row.bind(pos=lambda inst, val: _redraw_bg(inst))
        row.bind(size=lambda inst, val: _redraw_bg(inst))

        return row

    def _on_checkbox(self, exercise_id, is_selected):
        """Handle checkbox change."""
        if self._suppress_checkbox_events:
            return
        if is_selected:
            if exercise_id not in self.selected_exercises:
                self.selected_exercises.append(exercise_id)
        else:
            while exercise_id in self.selected_exercises:
                self.selected_exercises.remove(exercise_id)
        self._update_count()

    def _force_set_all_checkboxes(self, visible_ids):
        """Set all visible checkboxes to active without triggering _on_checkbox."""
        self._suppress_checkbox_events = True
        for eid in visible_ids:
            if eid in self.exercise_checkboxes:
                self.exercise_checkboxes[eid].active = True
        self._suppress_checkbox_events = False

    def _deduplicate_selection(self):
        """Remove duplicates from selected_exercises using a set."""
        seen = set()
        unique = []
        for eid in self.selected_exercises:
            if eid not in seen:
                seen.add(eid)
                unique.append(eid)
        self.selected_exercises = unique

    def _update_count(self):
        """Update the selected count label."""
        self._deduplicate_selection()
        total = len(self.all_exercises)
        selected = len(self.selected_exercises)
        # Also save to profile to prevent stale duplicates
        self._save_selection_silent()
        if hasattr(self.ids, 'lbl_selected_count'):
            self.ids.lbl_selected_count.text = f"Selected: {selected} / {total} exercises"

    def _save_selection_silent(self):
        """Save selection without user feedback."""
        try:
            profile = {}
            if os.path.exists("user_profile.json"):
                with open("user_profile.json", "r") as f:
                    profile = json.load(f)
            profile["selected_exercises"] = self.selected_exercises
            with open("user_profile.json", "w") as f:
                json.dump(profile, f, indent=2)
        except Exception:
            pass

    # ═══════════════════════════════════════════════════════════════
    #  SELECT ALL / NONE
    # ═══════════════════════════════════════════════════════════════
    def select_all(self):
        """Select all currently visible exercises."""
        query = ""
        if hasattr(self.ids, 'search_input'):
            query = self.ids.search_input.text.strip().lower()

        # Collect all visible exercise IDs
        visible_ids = set()
        for eid, ex in self.all_exercises.items():
            if self.current_muscle_filter != "All":
                if ex.get('muscle', '') != self.current_muscle_filter:
                    continue
            if self.current_equip_filter != "All":
                equip = ex.get('equip', '')
                tags = ex.get('equip_tags', [])
                if equip != self.current_equip_filter and \
                   self.current_equip_filter.lower() not in [t.lower() for t in tags]:
                    continue
            if query:
                name = ex.get('name', '').lower()
                muscle = ex.get('muscle', '').lower()
                equip = ex.get('equip', '').lower()
                if query not in name and query not in muscle and query not in equip:
                    continue
            visible_ids.add(eid)

        # Merge with existing selection using set to prevent duplicates
        combined = set(self.selected_exercises) | visible_ids
        self.selected_exercises = list(combined)

        # Update checkboxes without triggering _on_checkbox
        self._force_set_all_checkboxes(visible_ids)
        self._update_count()

    def deselect_all(self):
        """Deselect all exercises."""
        self.selected_exercises = []
        self._suppress_checkbox_events = True
        for checkbox in self.exercise_checkboxes.values():
            checkbox.active = False
        self._suppress_checkbox_events = False
        self._update_count()

    # ═══════════════════════════════════════════════════════════════
    #  SAVE / BACK
    # ═══════════════════════════════════════════════════════════════
    def save_selection(self):
        """Save selected exercises to profile."""
        try:
            profile = {}
            if os.path.exists("user_profile.json"):
                with open("user_profile.json", "r") as f:
                    profile = json.load(f)
            profile["selected_exercises"] = self.selected_exercises
            with open("user_profile.json", "w") as f:
                json.dump(profile, f, indent=2)
            print(f"[Exercise Selection] Saved {len(self.selected_exercises)} exercises")
        except Exception as e:
            print(f"[Exercise Selection] Error saving: {e}")

    def save_as_template(self):
        """Save selected exercises as a workout template."""
        if not self.selected_exercises:
            print("[Exercise Selection] No exercises selected to save as template")
            return

        from template_view import TemplateView
        from exercise_db import get_all_exercises

        all_ex = get_all_exercises()
        exercises_data = []
        for ex_id in self.selected_exercises:
            ex = all_ex.get(ex_id)
            if ex:
                exercises_data.append({
                    'exercise_id': ex_id,
                    'exercise_name': ex.get('name', ''),
                    'target_sets': ex.get('sets', 3),
                    'target_reps': ex.get('reps', 10),
                    'category': ex.get('muscle', ''),
                    'equipment': ex.get('equip', ''),
                })

        session_data = {
            'day_type': 'Gym',
            'focus': 'Custom Workout',
            'exercises': exercises_data
        }

        tv = TemplateView()
        tv.show_save_popup(session_data, on_save_callback=lambda: print("[Exercise Selection] Template saved!"))

    def go_back(self):
        """Save and go back to previous screen."""
        self.save_selection()
        try:
            from kivy.app import App
            app = App.get_running_app()
            if hasattr(app, 'sm'):
                app.sm.current = 'calendar'
        except Exception as e:
            print(f"[Navigation Error] {e}")
