# stickman_demo.py - Standalone stick-figure exercise demo (prototype)
# Fully self-contained: no imports from the Squad Fit app.
# Shows a looping barbell back squat with the legs highlighted in neon green.
#
# Run with:  /c/Temp/Buffswos/.venv/Scripts/python.exe stickman_demo.py

import math

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.metrics import dp

# ─────────────────────────────────────────────────────────────
#  FIGURE MODEL (units; standing height ≈ 1.65)
# ─────────────────────────────────────────────────────────────
T          = 0.48   # torso length (hip -> shoulder)
L1         = 0.46   # thigh length
L2         = 0.46   # shin length
HEAD       = 0.13   # head radius
HIP_STAND  = 0.90   # standing hip height
HIP_DROP   = 0.38   # how far the hip lowers at the bottom
HIP_BACK   = 0.10   # how far the hip drifts back at the bottom
LEAN_MAX   = 0.30   # max torso forward lean (radians) at the bottom
ANKLE      = (0.0, 0.04)  # ankle sits above the foot line

NEON = (0.75, 1.00, 0.15, 1)   # working-legs highlight
DIM  = (0.45, 0.48, 0.55, 1)   # everything else
BAR  = (0.85, 0.85, 0.90, 1)   # barbell
PLATE = (0.60, 0.62, 0.68, 1)  # weight plate (lighter than body)
BG   = (0.09, 0.10, 0.12, 1)   # background

CYCLE = 2.6  # seconds for one full squat (down + up)


def solve_knee(hip, ankle, l1, l2):
    """Forward-kinematics: knee = intersection of two circles.

    hip  -> centre of circle radius l1 (thigh)
    ankle-> centre of circle radius l2 (shin)
    Returns the knee point that bends forward (+x, facing right).
    """
    hx, hy = hip
    ax, ay = ankle
    dx, dy = ax - hx, ay - hy
    d = math.hypot(dx, dy)
    d = max(min(d, l1 + l2 - 1e-6), abs(l1 - l2) + 1e-6)
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, l1 * l1 - a * a))
    mx = hx + a * dx / d
    my = hy + a * dy / d
    # two candidate knees; pick the one further forward (+x)
    kx1 = mx + h * (-dy / d)
    ky1 = my + h * (dx / d)
    kx2 = mx - h * (-dy / d)
    ky2 = my - h * (dx / d)
    return (kx1, ky1) if kx1 >= kx2 else (kx2, ky2)


def pose(depth, lean):
    """Compute every joint for a given squat depth (0=stand, 1=bottom)."""
    hip = (-depth * HIP_BACK, HIP_STAND - depth * HIP_DROP)
    knee = solve_knee(hip, ANKLE, L1, L2)
    shoulder = (hip[0] + T * math.sin(lean), hip[1] + T * math.cos(lean))
    head = (shoulder[0] + HEAD * 1.05 * math.sin(lean),
            shoulder[1] + HEAD * 1.05 * math.cos(lean))

    # barbell sits on the upper back, hands grip slightly behind the neck
    bar_end = (shoulder[0] - 0.06, shoulder[1] + 0.02)  # side view: near plate at the neck
    hand = bar_end
    elbow = (shoulder[0] - 0.10, shoulder[1] - 0.20)

    return dict(hip=hip, knee=knee, ankle=ANKLE, shoulder=shoulder,
                head=head, hand=hand, elbow=elbow, bar_end=bar_end)


class StickmanFigure(Widget):
    """Draws and animates a stick figure performing a squat."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._t = 0.0
        self.bind(size=self._redraw, pos=self._redraw)
        Clock.schedule_interval(self._tick, 1.0 / 40.0)

    def _tick(self, dt):
        self._t += dt
        self._redraw()

    def _redraw(self, *args):
        self.canvas.clear()
        if self.width < 20 or self.height < 20:
            return

        # squat depth: smooth down-then-up over the cycle
        ph = (self._t % CYCLE) / CYCLE
        depth = 0.5 - 0.5 * math.cos(2 * math.pi * ph)
        lean = LEAN_MAX * depth
        p = pose(depth, lean)

        # map figure units -> widget pixels
        scale = self.height * 0.92 / 1.85
        cx = self.x + self.width / 2.0
        gy = self.y + self.height * 0.05

        def X(x):
            return cx + x * scale

        def Y(y):
            return gy + y * scale

        def seg(a, b, color, width):
            Color(*color)
            Line(points=[X(a[0]), Y(a[1]), X(b[0]), Y(b[1])],
                 width=width, cap='round', joint='round')

        def dot(pt, color, radius):
            Color(*color)
            Ellipse(pos=(X(pt[0]) - radius, Y(pt[1]) - radius),
                    size=(2 * radius, 2 * radius))

        with self.canvas:
            # ground
            Color(0.30, 0.30, 0.35, 1)
            Line(points=[X(-0.85), Y(0), X(0.85), Y(0)], width=1)

            # legs (highlighted) — soft glow underneath, then crisp line
            seg(p['ankle'], p['knee'], (*NEON[:3], 0.25), 16)   # shin glow
            seg(p['knee'], p['hip'], (*NEON[:3], 0.25), 16)     # thigh glow
            seg(p['ankle'], p['knee'], NEON, 7)                 # shin
            seg(p['knee'], p['hip'], NEON, 7)                   # thigh
            seg((p['ankle'][0] - 0.08, 0), (p['ankle'][0] + 0.16, 0), NEON, 6)  # foot

            # torso + arms (dimmed)
            seg(p['hip'], p['shoulder'], DIM, 7)
            seg(p['shoulder'], p['elbow'], DIM, 6)
            seg(p['elbow'], p['hand'], DIM, 6)

            # head
            r = HEAD * scale
            Color(*DIM)
            Ellipse(pos=(X(p['head'][0]) - r, Y(p['head'][1]) - r),
                    size=(2 * r, 2 * r))

            # barbell end (side view: near plate at the neck)
            be = p['bar_end']
            pr = 0.09 * scale
            Color(*PLATE)
            Ellipse(pos=(X(be[0]) - pr, Y(be[1]) - pr), size=(2 * pr, 2 * pr))
            # thin outline so the plate stands out
            Color(0.85, 0.85, 0.90, 1)
            Line(circle=(X(be[0]), Y(be[1]), pr), width=1.5)
            sr = 0.035 * scale
            Color(*BAR)
            Ellipse(pos=(X(be[0]) - sr, Y(be[1]) - sr), size=(2 * sr, 2 * sr))

            # joints (small fixed pixel size)
            dot(p['hip'], NEON, 5)
            dot(p['knee'], NEON, 5)
            dot(p['shoulder'], DIM, 4)
            dot(p['elbow'], DIM, 3.5)


class StickmanDemoApp(App):
    def build(self):
        root = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))

        with root.canvas.before:
            Color(*BG)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self._on_bg, size=self._on_bg)

        root.add_widget(Label(
            text="STICK-FIGURE DEMO",
            font_size='20sp', bold=True, color=(1, 1, 1, 1),
            size_hint_y=None, height=dp(34)
        ))
        root.add_widget(Label(
            text="Barbell Back Squat  ·  legs highlighted",
            font_size='13sp', color=(0.6, 0.6, 0.65, 1),
            size_hint_y=None, height=dp(24)
        ))

        self.figure = StickmanFigure()
        root.add_widget(self.figure)

        root.add_widget(Label(
            text="This is a self-contained prototype — the Squad Fit app is untouched.",
            font_size='11sp', color=(0.4, 0.4, 0.45, 1),
            size_hint_y=None, height=dp(24)
        ))
        return root

    def _on_bg(self, inst, val):
        self._bg.pos = inst.pos
        self._bg.size = inst.size


if __name__ == '__main__':
    StickmanDemoApp().run()
