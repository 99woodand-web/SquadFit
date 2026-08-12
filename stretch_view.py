"""Guided cool-down stretch timer."""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.app import App
from kivy.graphics import Color, RoundedRectangle, Ellipse, Line


# 8 guided stretches with duration (seconds) and instructions
STRETCHES = [
    {
        "name": "Neck Rolls",
        "duration": 30,
        "instruction": "Slowly roll your head in a circle.\n5 times each direction.\nKeep shoulders relaxed.",
    },
    {
        "name": "Shoulder Stretch",
        "duration": 30,
        "instruction": "Pull one arm across your chest.\nHold for 15s each side.\nKeep shoulder down.",
    },
    {
        "name": "Chest Opener",
        "duration": 30,
        "instruction": "Clasp hands behind your back.\nLift arms and open your chest.\nHold and breathe deeply.",
    },
    {
        "name": "Standing Quad",
        "duration": 30,
        "instruction": "Grab your ankle behind you.\nPull heel toward glutes.\n15s each leg.",
    },
    {
        "name": "Hamstring Stretch",
        "duration": 30,
        "instruction": "Place heel on a low surface.\nLean forward from the hips.\n15s each leg.",
    },
    {
        "name": "Hip Flexor",
        "duration": 30,
        "instruction": "Step into a lunge position.\nPush hips forward gently.\n15s each side.",
    },
    {
        "name": "Calf Stretch",
        "duration": 30,
        "instruction": "Press back heel into the floor.\nLean against a wall.\n15s each leg.",
    },
    {
        "name": "Deep Breathing",
        "duration": 60,
        "instruction": "Inhale for 4 counts.\nHold for 4 counts.\nExhale for 6 counts.\nRepeat 5 times.",
    },
]


class StretchView(Screen):
    """Full-screen guided cool-down stretch timer."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._current = 0
        self._remaining = 0
        self._timer_event = None
        self._build_ui()

    def _build_ui(self):
        self.main_layout = BoxLayout(
            orientation="vertical", padding=dp(20), spacing=dp(12)
        )
        with self.main_layout.canvas.before:
            Color(0.07, 0.07, 0.07, 1)
            from kivy.graphics import Rectangle
            Rectangle(pos=self.main_layout.pos, size=self.main_layout.size)
        self.main_layout.bind(
            pos=lambda inst, val: self._redraw_bg(inst),
            size=lambda inst, val: self._redraw_bg(inst),
        )

        # Header
        header = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        self.title_label = Label(
            text="COOL DOWN",
            font_size="18sp",
            bold=True,
            color=(0.2, 1.0, 0.6, 1),
            halign="left",
            text_size=(dp(280), None),
        )
        header.add_widget(self.title_label)
        self.main_layout.add_widget(header)

        # Step counter
        self.step_label = Label(
            text="1 / 8",
            font_size="13sp",
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=dp(20),
        )
        self.main_layout.add_widget(self.step_label)

        # Stretch name
        self.name_label = Label(
            text="",
            font_size="24sp",
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(40),
        )
        self.main_layout.add_widget(self.name_label)

        # Timer circle area
        timer_area = FloatLayout(size_hint_y=None, height=dp(180))
        with timer_area.canvas.before:
            Color(0.12, 0.12, 0.12, 1)
            RoundedRectangle(
                pos=timer_area.pos,
                size=timer_area.size,
                radius=[dp(16)],
            )
        timer_area.bind(
            pos=lambda inst, val: self._redraw_timer_bg(inst),
            size=lambda inst, val: self._redraw_timer_bg(inst),
        )
        self.timer_area = timer_area

        self.time_label = Label(
            text="30",
            font_size="56sp",
            bold=True,
            color=(0.2, 1.0, 0.6, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.55},
        )
        timer_area.add_widget(self.time_label)

        self.unit_label = Label(
            text="seconds",
            font_size="12sp",
            color=(0.5, 0.5, 0.5, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.25},
        )
        timer_area.add_widget(self.unit_label)

        self.main_layout.add_widget(timer_area)

        # Instruction text
        self.instruction_label = Label(
            text="",
            font_size="13sp",
            color=(0.65, 0.65, 0.65, 1),
            halign="center",
            text_size=(dp(280), None),
            size_hint_y=None,
            height=dp(80),
            valign="top",
        )
        self.main_layout.add_widget(self.instruction_label)

        # Buttons row
        btn_row = BoxLayout(
            size_hint_y=None, height=dp(50), spacing=dp(12)
        )

        self.skip_btn = Button(
            text="SKIP",
            font_size="13sp",
            bold=True,
            background_normal="",
            background_down="",
            background_color=(0.22, 0.22, 0.22, 1),
            color=(0.7, 0.7, 0.7, 1),
        )
        with self.skip_btn.canvas.before:
            Color(0.22, 0.22, 0.22, 1)
            RoundedRectangle(
                pos=self.skip_btn.pos,
                size=self.skip_btn.size,
                radius=[dp(25)],
            )
        self.skip_btn.bind(
            pos=lambda inst, val: self._draw_pill(inst, (0.22, 0.22, 0.22, 1)),
            size=lambda inst, val: self._draw_pill(inst, (0.22, 0.22, 0.22, 1)),
            on_press=lambda x: self._next_stretch(),
        )
        btn_row.add_widget(self.skip_btn)

        self.finish_btn = Button(
            text="FINISH",
            font_size="13sp",
            bold=True,
            background_normal="",
            background_down="",
            background_color=(0.0, 0.0, 0.0, 0),
            color=(1, 1, 1, 1),
        )
        with self.finish_btn.canvas.before:
            Color(0.07, 0.53, 0.3, 1)
            RoundedRectangle(
                pos=self.finish_btn.pos,
                size=self.finish_btn.size,
                radius=[dp(25)],
            )
        self.finish_btn.bind(
            pos=lambda inst, val: self._draw_pill(inst, (0.07, 0.53, 0.3, 1)),
            size=lambda inst, val: self._draw_pill(inst, (0.07, 0.53, 0.3, 1)),
            on_press=lambda x: self._finish_stretch(),
        )
        btn_row.add_widget(self.finish_btn)

        self.main_layout.add_widget(btn_row)

        self.add_widget(self.main_layout)

    def on_pre_enter(self):
        """Start the stretch sequence."""
        self._current = 0
        self._load_stretch()

    def on_leave(self):
        """Stop timer when leaving."""
        self._stop_timer()

    def _load_stretch(self):
        """Load the current stretch."""
        if self._current >= len(STRETCHES):
            self._finish_stretch()
            return

        stretch = STRETCHES[self._current]
        self.title_label.text = "COOL DOWN"
        self.step_label.text = f"{self._current + 1} / {len(STRETCHES)}"
        self.name_label.text = stretch["name"]
        self.time_label.text = str(stretch["duration"])
        self.unit_label.text = "seconds"
        self.instruction_label.text = stretch["instruction"]
        self._remaining = stretch["duration"]

        self.skip_btn.text = "SKIP" if self._current < len(STRETCHES) - 1 else "FINISH"
        self.skip_btn.unbind(on_press=self.skip_btn.dispatch)
        self.skip_btn.bind(on_press=lambda x: self._next_stretch())

        self._start_timer()

    def _start_timer(self):
        self._stop_timer()
        self._timer_event = Clock.schedule_interval(self._tick, 1)

    def _stop_timer(self):
        if self._timer_event:
            self._timer_event.cancel()
            self._timer_event = None

    def _tick(self, dt):
        self._remaining -= 1
        if self._remaining <= 0:
            self._next_stretch()
            return
        self.time_label.text = str(self._remaining)

    def _next_stretch(self):
        """Move to next stretch."""
        self._stop_timer()
        self._current += 1
        if self._current >= len(STRETCHES):
            self._finish_stretch()
        else:
            self._load_stretch()

    def _finish_stretch(self):
        """Return to calendar."""
        self._stop_timer()
        app = App.get_running_app()
        if hasattr(app, "sm"):
            app.sm.current = "calendar"

    def _draw_pill(self, inst, color):
        inst.canvas.before.clear()
        with inst.canvas.before:
            Color(*color)
            RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(25)])

    def _redraw_bg(self, inst):
        inst.canvas.before.clear()
        with inst.canvas.before:
            Color(0.07, 0.07, 0.07, 1)
            from kivy.graphics import Rectangle
            Rectangle(pos=inst.pos, size=inst.size)

    def _redraw_timer_bg(self, inst):
        inst.canvas.before.clear()
        with inst.canvas.before:
            Color(0.12, 0.12, 0.12, 1)
            RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(16)])
