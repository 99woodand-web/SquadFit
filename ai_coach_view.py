# ai_coach_view.py - AI Coach Dashboard Screen
# Builds the coaching dashboard dynamically from AICoachEngine data.
# NO database modifications. NO breaking changes.

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle


class AICoachScreen(BoxLayout):
    """AI Coach dashboard with recovery, recommendations, and coaching tips."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._init_dashboard, 0.2)

    def _init_dashboard(self, dt):
        self._build_dashboard()

    def on_pre_enter(self):
        """Refresh dashboard every time user navigates to this screen."""
        self._build_dashboard()

    def _build_dashboard(self):
        """Build the full AI coaching dashboard."""
        from ai_coach import AICoachEngine
        engine = AICoachEngine()
        data = engine.get_dashboard_data()

        content = self.ids.content_area
        content.clear_widgets()

        # 1. Today's Recommendation
        self._build_recommendation_card(content, data['today_recommendation'], data['generated_workout'])

        # 2. Weekly Volume
        self._build_volume_section(content, data['weekly_volume'])

        # 4. Progressive Overload Suggestions
        if data['progressive_overload']:
            self._build_overload_section(content, data['progressive_overload'])

        # 5. Plateau Alerts
        if data['plateaus']:
            self._build_plateau_section(content, data['plateaus'], data['deload'])

        # 6. Form Tips for Today's Exercises
        self._build_form_tips_section(content, data['generated_workout']['exercises'], engine)

    # ═══════════════════════════════════════════════════════════════
    #  SECTION BUILDERS
    # ═══════════════════════════════════════════════════════════════

    def _build_recommendation_card(self, container, recommendation, workout):
        """Build the 'Train Today' recommendation card."""
        card = self._make_card(container, height=dp(200))

        # Title
        card.add_widget(self._section_label("TODAY'S AI RECOMMENDATION"))

        # Build colored muscle list with recovery percentages inline
        recovery = recommendation.get('recovery', {})
        muscle_parts = []
        for m in recommendation['muscles']:
            pct = recovery.get(m, {}).get('recovery', 50)
            if pct >= 80:
                color_hex = '00FF99'  # green
            elif pct >= 50:
                color_hex = 'FFD700'  # yellow
            else:
                color_hex = 'FF6666'  # red
            muscle_parts.append(f'[color={color_hex}]{m} {pct}%[/color]')
        muscle_text = ', '.join(muscle_parts)

        rec_label = Label(
            text=f"Train: {muscle_text}",
            font_size='12sp', bold=True, markup=True,
            color=(1, 1, 1, 1), halign='left',
            size_hint_y=None, height=dp(28),
            shorten=True, shorten_from='right', max_lines=1,
            text_size=(dp(280), None),
            padding=[dp(4), 0]
        )
        card.add_widget(rec_label)

        # Reasoning
        reasoning = Label(
            text=recommendation['reasoning'],
            font_size='10sp', color=(0.55, 0.55, 0.55, 1),
            halign='left', valign='top',
            size_hint_y=None, height=dp(32),
            text_size=(dp(280), None),
            padding=[dp(4), 0]
        )
        card.add_widget(reasoning)

        # Generated workout preview
        exercises = workout['exercises']
        ex_list = "\n".join([f"  {i+1}. {e['name']} ({e['sets']}x{e['reps']})" for i, e in enumerate(exercises[:6])])
        ex_label = Label(
            text=f"[color=777777]Today's exercises:[/color]\n{ex_list}",
            font_size='10sp', markup=True, color=(0.6, 0.6, 0.6, 1),
            halign='left', valign='top',
            size_hint_y=None, height=dp(70),
            text_size=(dp(280), None),
            padding=[dp(4), 0]
        )
        card.add_widget(ex_label)

    def _build_volume_section(self, container, volume):
        """Build the weekly volume tracker."""
        present = [m for m in ["Chest", "Back", "Legs", "Shoulders", "Biceps", "Triceps", "Core"]
                   if m in volume]
        # Title (20) + rows (26 each) + spacing (6 per gap) + padding (24) + small buffer
        card = self._make_card(container, height=dp(48 + len(present) * 32))

        card.add_widget(self._section_label("WEEKLY VOLUME TRACKER"))

        for muscle in present:
            info = volume[muscle]
            row = self._build_volume_row(muscle, info)
            card.add_widget(row)

    def _build_volume_row(self, muscle, info):
        """Build a single volume tracking row."""
        sets = info['sets']
        target = info['target']
        status = info['status']
        pct = info['percentage']

        row = BoxLayout(
            orientation='horizontal', spacing=dp(8),
            size_hint_y=None, height=dp(26),
            padding=[dp(4), 0]
        )

        row.add_widget(Label(
            text=muscle, font_size='11sp', bold=True,
            color=(0.8, 0.8, 0.8, 1), halign='left',
            size_hint_x=0.22, text_size=(None, None)
        ))

        # Volume bar
        bar_widget = VolumeBarWidget(volume_pct=pct, size_hint_x=0.45)
        row.add_widget(bar_widget)

        # Sets count
        row.add_widget(Label(
            text=f"{sets}/{target}", font_size='11sp',
            color=(0.7, 0.7, 0.7, 1), size_hint_x=0.15
        ))

        # Status
        if status == "Optimal":
            color = (0.2, 1.0, 0.6, 1)
        elif status == "Adequate":
            color = (1.0, 0.84, 0.0, 1)
        else:
            color = (1.0, 0.4, 0.4, 1)

        row.add_widget(Label(
            text=status, font_size='9sp', bold=True,
            color=color, size_hint_x=0.18
        ))

        return row

    def _build_overload_section(self, container, suggestions):
        """Build progressive overload suggestions (reps-based)."""
        card = self._make_card(container, height=dp(60 + len(suggestions) * 50))

        card.add_widget(self._section_label("PROGRESSIVE OVERLOAD"))

        for s in suggestions:
            row = BoxLayout(
                orientation='vertical', spacing=dp(2),
                size_hint_y=None, height=dp(44),
                padding=[dp(4), 0]
            )

            # Exercise + reps suggestion
            current = s.get('current_reps', 0)
            suggested = s.get('suggested_reps', current)
            if suggested > current:
                reps_text = f"{s['exercise']}: {current} reps  ->  [color=00FF99]{suggested} reps[/color]"
            else:
                reps_text = f"{s['exercise']}: {current} reps"

            row.add_widget(Label(
                text=reps_text, font_size='12sp', bold=True, markup=True,
                color=(1, 1, 1, 1), halign='left',
                size_hint_y=None, height=dp(20),
                text_size=(None, None)
            ))

            row.add_widget(Label(
                text=s.get('reasoning', ''), font_size='10sp',
                color=(0.5, 0.5, 0.5, 1), halign='left',
                size_hint_y=None, height=dp(18),
                text_size=(None, None)
            ))

            card.add_widget(row)

    def _build_plateau_section(self, container, plateaus, deload):
        """Build plateau alerts and deload suggestions."""
        card = self._make_card(container, height=dp(80 + len(plateaus) * 40))

        # Deload warning if needed
        if deload['should_deload']:
            card.add_widget(self._section_label("DELOAD ALERT"))
            alert = Label(
                text=f"[color=FF6644]{deload['reasoning']}[/color]",
                font_size='11sp', markup=True, color=(1, 0.4, 0.27, 1),
                halign='left', valign='top',
                size_hint_y=None, height=dp(50),
                text_size=(None, None),
                padding=[dp(4), 0]
            )
            card.add_widget(alert)
        else:
            card.add_widget(self._section_label("PLATEAU DETECTION"))

        for p in plateaus:
            row = Label(
                text=f"{p['exercise']}: Stalled at {p['weight']}kg for {p['weeks_stalled']} weeks",
                font_size='11sp', color=(1.0, 0.84, 0.0, 1),
                halign='left', size_hint_y=None, height=dp(28),
                text_size=(None, None),
                padding=[dp(4), 0]
            )
            card.add_widget(row)

    def _build_form_tips_section(self, container, exercises, engine):
        """Build form tips for today's exercises."""
        if not exercises:
            return

        card = self._make_card(container, height=dp(60 + len(exercises) * 70))

        card.add_widget(self._section_label("FORM TIPS FOR TODAY"))

        for ex in exercises[:4]:  # Show tips for first 4 exercises
            ex_name = ex.get('name', '')
            tips = engine.get_form_tips(ex_name)

            # Exercise name
            card.add_widget(Label(
                text=f"[color=00FF99]{ex_name}[/color]",
                font_size='12sp', bold=True, markup=True,
                color=(0.2, 1.0, 0.6, 1), halign='left',
                size_hint_y=None, height=dp(20),
                text_size=(None, None),
                padding=[dp(4), 0]
            ))

            # Tips
            tips_text = "\n".join([f"  • {t}" for t in tips[:3]])
            card.add_widget(Label(
                text=tips_text,
                font_size='10sp', color=(0.7, 0.7, 0.7, 1),
                halign='left', valign='top',
                size_hint_y=None, height=dp(40),
                text_size=(None, None),
                padding=[dp(4), 0]
            ))

    # ═══════════════════════════════════════════════════════════════
    #  HELPER METHODS
    # ═══════════════════════════════════════════════════════════════

    def _make_card(self, container, height=dp(100)):
        """Create a styled card layout."""
        card = BoxLayout(
            orientation='vertical', spacing=dp(6),
            padding=dp(12), size_hint_y=None, height=height
        )
        with card.canvas.before:
            Color(0.12, 0.12, 0.12, 0.8)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
        card.bind(pos=lambda inst, val: self._redraw_card(inst))
        card.bind(size=lambda inst, val: self._redraw_card(inst))
        container.add_widget(card)
        return card

    def _redraw_card(self, inst):
        inst.canvas.before.clear()
        with inst.canvas.before:
            Color(0.12, 0.12, 0.12, 0.8)
            RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(12)])

    def _section_label(self, text):
        """Create a section header label."""
        return Label(
            text=text, font_size='11sp', bold=True,
            color=(0.5, 0.5, 0.5, 1), halign='left',
            size_hint_y=None, height=dp(20),
            text_size=(dp(280), None),
            padding=[dp(4), 0]
        )

    def go_back(self):
        """Navigate back to calendar."""
        try:
            from kivy.app import App
            app = App.get_running_app()
            if hasattr(app, 'sm'):
                app.sm.current = 'calendar'
        except Exception as e:
            print(f"[Navigation Error] {e}")


# ═══════════════════════════════════════════════════════════════════════════════
#  CUSTOM WIDGETS
# ═══════════════════════════════════════════════════════════════════════════════

class VolumeBarWidget(Widget):
    """Draws a volume tracking bar."""
    volume_pct = 0

    def __init__(self, volume_pct=0, **kwargs):
        super().__init__(**kwargs)
        self.volume_pct = volume_pct
        self.bind(pos=self._draw)
        self.bind(size=self._draw)
        Clock.schedule_once(lambda dt: self._draw(), 0.1)

    def _draw(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Background bar
            Color(0.15, 0.15, 0.15, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(4)])

            # Fill bar
            fill_width = self.width * (min(self.volume_pct, 100) / 100.0)
            if self.volume_pct >= 100:
                Color(0.2, 1.0, 0.6, 0.9)  # Green - optimal
            elif self.volume_pct >= 50:
                Color(1.0, 0.84, 0.0, 0.9)  # Yellow - building
            elif self.volume_pct >= 25:
                Color(1.0, 0.7, 0.3, 0.9)  # Orange - getting there
            else:
                Color(0.9, 0.35, 0.35, 0.8)  # Soft red - just started

            RoundedRectangle(
                pos=self.pos,
                size=(fill_width, self.height),
                radius=[dp(4)]
            )
