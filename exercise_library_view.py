"""exercise_library_view.py — Browse all 24 stick-figure movement patterns."""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.app import App
from kivy.graphics import Color, RoundedRectangle, Rectangle

from stickman import StickmanWidget, ARCHETYPES


# One-line coaching cue per movement pattern.
CUES = {
    'squat': "Sit your hips back and down, knees tracking over toes, chest up.",
    'hinge': "Push your hips back, keep a flat back, drive through your heels.",
    'push_h': "Lower the bar to mid-chest, elbows ~45°, press up and slightly back.",
    'fly': "Keep arms nearly straight and hug a big tree, squeezing at the top.",
    'push_v': "Press overhead, brace your core, avoid arching your lower back.",
    'pull_h': "Hinge forward, pull to your waist and squeeze your shoulder blades.",
    'pull_v': "Pull the bar to your upper chest, control it on the way back.",
    'pull_up': "Hang fully, pull your chin over the bar, lower under control.",
    'curl': "Pin your elbows to your sides, curl up, lower slowly.",
    'tricep': "Keep your elbows still, extend fully and squeeze the triceps.",
    'core_flex': "Raise your legs without swinging, lower them slowly.",
    'plank': "Body in a straight line, brace your core, don't let your hips sag.",
    'lateral': "Raise to shoulder height with a soft elbow, lower slowly.",
    'carry': "Stand tall, brace your core, take short quick steps.",
    'cycle': "Smooth pedal strokes, steady cadence, keep your hips stable.",
    'calf': "Rise onto your toes, pause at the top, lower below level.",
    'crunch': "Curl your shoulders up, exhale at the top, don't pull your neck.",
    'pushup': "Body straight, lower your chest to the floor, push back up.",
    'bridge': "Drive your hips up, squeeze your glutes at the top, lower slowly.",
    'kb_swing': "Hinge and snap your hips, swing the bell to chest height.",
    'leg_ext': "Extend your knees fully, pause, lower slowly.",
    'leg_curl': "Curl your heels toward your glutes, pause, lower slowly.",
    'cable_row': "Row to your abdomen, chest up, squeeze your back.",
    'row_machine': "Push with your legs, then pull with your arms, reverse smoothly.",
}


class ExerciseLibraryScreen(Screen):
    """Scrollable grid of every stick-figure movement pattern."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._figures = []
        self._build()

    # ── lifecycle: pause the grid animations when we leave the screen ──
    def on_pre_enter(self):
        for f in self._figures:
            f.start(10)

    def on_pre_leave(self):
        for f in self._figures:
            f.stop()

    def _bg(self, inst, color, radius):
        inst.canvas.before.clear()
        with inst.canvas.before:
            Color(*color)
            RoundedRectangle(pos=inst.pos, size=inst.size, radius=radius)

    def _build(self):
        app = App.get_running_app()

        root = BoxLayout(orientation='vertical',
                         padding=[dp(12), dp(8), dp(12), dp(8)], spacing=dp(8))
        with root.canvas.before:
            Color(*app.canvas_bg)
            Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda i, v: self._root_bg(i))
        root.bind(size=lambda i, v: self._root_bg(i))

        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=None,
                           height=dp(44), spacing=dp(10))
        back = Button(text="BACK", font_size='13sp', bold=True,
                      size_hint=(None, None), size=(dp(70), dp(36)),
                      background_normal='', background_down='',
                      background_color=(0, 0, 0, 0), color=app.accent_color)
        back_bg = (app.accent_color[0], app.accent_color[1], app.accent_color[2], 0.15)
        back.bind(pos=lambda i, v: self._bg(i, back_bg, [dp(12)]))
        back.bind(size=lambda i, v: self._bg(i, back_bg, [dp(12)]))
        back.bind(on_release=lambda x: self._go_back())
        header.add_widget(back)

        title = Label(text="EXERCISE LIBRARY", font_size='18sp', bold=True,
                      color=(0.2, 1.0, 0.6, 1), halign='left', valign='middle')
        title.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        header.add_widget(title)
        root.add_widget(header)

        sub = Label(text=f"{len(ARCHETYPES)} movement patterns  ·  tap one to watch",
                    font_size='12sp', color=(0.5, 0.5, 0.5, 1),
                    size_hint_y=None, height=dp(20), halign='left', valign='middle')
        sub.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        root.add_widget(sub)

        # Grid of cards
        grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None,
                          padding=[0, dp(4), 0, dp(8)])
        grid.bind(minimum_height=grid.setter('height'))
        for a in ARCHETYPES:
            grid.add_widget(self._make_card(a))

        scroll = ScrollView(do_scroll_x=False)
        scroll.add_widget(grid)
        root.add_widget(scroll)

        self.add_widget(root)

    def _root_bg(self, inst):
        inst.canvas.before.clear()
        with inst.canvas.before:
            Color(*App.get_running_app().canvas_bg)
            Rectangle(pos=inst.pos, size=inst.size)

    def _make_card(self, a):
        app = App.get_running_app()
        card = FloatLayout(size_hint_y=None, height=dp(196))

        inner = BoxLayout(orientation='vertical', spacing=dp(2),
                          padding=[dp(8), dp(8), dp(8), dp(8)],
                          pos_hint={'x': 0, 'y': 0}, size_hint=(1, 1))
        inner.bind(pos=lambda i, v: self._bg(i, app.card_bg, [dp(14)]))
        inner.bind(size=lambda i, v: self._bg(i, app.card_bg, [dp(14)]))

        fig = StickmanWidget(archetype=a['id'], animate=False,
                             size_hint_y=None, height=dp(118))
        self._figures.append(fig)
        inner.add_widget(fig)

        name = Label(text=a['name'], font_size='14sp', bold=True,
                     color=(1, 1, 1, 1), size_hint_y=None, height=dp(22),
                     halign='center', valign='middle')
        name.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        inner.add_widget(name)

        sub = Label(text=a['subtitle'], font_size='11sp',
                    color=(0.55, 0.55, 0.55, 1), size_hint_y=None, height=dp(18),
                    halign='center', valign='middle')
        sub.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        inner.add_widget(sub)

        card.add_widget(inner)

        # Transparent tap overlay (Button natively ignores scroll-drags)
        btn = Button(text='', background_normal='', background_down='',
                     background_color=(0, 0, 0, 0),
                     size_hint=(1, 1), pos_hint={'x': 0, 'y': 0})
        btn.bind(on_release=lambda x, aid=a['id']: self._open_detail(aid))
        card.add_widget(btn)

        return card

    def _open_detail(self, aid):
        a = next((x for x in ARCHETYPES if x['id'] == aid), ARCHETYPES[0])
        app = App.get_running_app()

        content = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(16))
        content.add_widget(Label(
            text=a['name'], font_size='20sp', bold=True,
            color=(1, 1, 1, 1), size_hint_y=None, height=dp(30),
            halign='center', valign='middle',
            text_size=(dp(280), None)
        ))
        content.add_widget(Label(
            text=a['subtitle'], font_size='13sp', color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None, height=dp(20), halign='center', valign='middle',
            text_size=(dp(280), None)
        ))

        fig = StickmanWidget(archetype=a['id'], fps=30, size_hint_y=None, height=dp(240))
        content.add_widget(fig)

        cue = CUES.get(a['id'], "Focus on controlled movement and proper form.")
        content.add_widget(Label(
            text=cue, font_size='15sp', bold=True, color=(0.2, 1.0, 0.6, 1),
            halign='center', text_size=(dp(280), None), size_hint_y=None, height=dp(64)
        ))

        btn = Button(
            text="CLOSE", bold=True, font_size='14sp',
            size_hint_y=None, height=dp(44),
            background_normal='', background_down='',
            background_color=(0, 0, 0, 0), color=(0.07, 0.07, 0.07, 1)
        )
        btn.bind(pos=lambda i, v: self._bg(i, (0.2, 1.0, 0.6, 1), [dp(14)]))
        btn.bind(size=lambda i, v: self._bg(i, (0.2, 1.0, 0.6, 1), [dp(14)]))
        content.add_widget(btn)

        popup = Popup(title="", content=content, size_hint=(0.9, None),
                      height=dp(470), auto_dismiss=True,
                      background_color=(0.1, 0.1, 0.1, 1), separator_height=0)
        btn.bind(on_release=popup.dismiss)
        popup.open()

    def _go_back(self):
        app = App.get_running_app()
        if hasattr(app, 'sm'):
            app.sm.current = 'calendar'
