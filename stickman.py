# stickman.py - Stick-figure exercise engine for Squad Fit.
# Faithful 1:1 port of stickman_preview.html (22 movement archetypes).
# Each archetype is a pose(ph) function returning a dict of joints + an
# equipment prop. StickmanWidget renders and animates any archetype.
#
# Integration:  from stickman import StickmanWidget, archetype_for

import math

from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.metrics import dp

# ── figure model (units; standing height ≈ 1.48 + head) ─────────────
T    = 0.48   # torso length (hip -> shoulder)
L1   = 0.46   # thigh length
L2   = 0.46   # shin length
HEAD = 0.13   # head radius
UA   = 0.38   # upper arm length
FA   = 0.31   # forearm length

NEON   = (0.75, 1.00, 0.15)   # working-muscle highlight
DIM    = (0.45, 0.48, 0.55)   # everything else
BAR    = (0.85, 0.85, 0.90)   # bar / light metal
PLATE  = (0.55, 0.30, 0.35)   # weight plate
KETTLE = (0.55, 0.30, 0.35)   # kettlebell body
BAND   = (0.30, 0.75, 0.90)   # cable line
STEEL  = (0.55, 0.58, 0.66)   # machine frame
PAD    = (0.28, 0.40, 0.55)   # machine pad

STAND = {'ankle': (0.0, 0.04)}


def _dim(c):
    return (c[0] * 0.5, c[1] * 0.5, c[2] * 0.5)


# ── joint solvers ────────────────────────────────────────────────────
def _solve_joint(p1, p2, l1, l2, forward):
    """Two-circle IK: the knee/elbow at the intersection of two limb circles."""
    ax, ay = p1
    bx, by = p2
    dx, dy = bx - ax, by - ay
    d = math.hypot(dx, dy)
    d = max(min(d, l1 + l2 - 1e-6), abs(l1 - l2) + 1e-6)
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, l1 * l1 - a * a))
    mx = ax + a * dx / d
    my = ay + a * dy / d
    x1 = mx + h * (-dy / d)
    y1 = my + h * (dx / d)
    x2 = mx - h * (-dy / d)
    y2 = my - h * (dx / d)
    if forward:
        return (x1, y1) if x1 >= x2 else (x2, y2)
    return (x1, y1) if x1 <= x2 else (x2, y2)


def _knee_ik(hip, ankle):
    return _solve_joint(hip, ankle, L1, L2, True)


def _knee_up(hip, ankle):
    """Knee that always points UP (e.g. glute bridge)."""
    ax, ay = hip
    bx, by = ankle
    dx, dy = bx - ax, by - ay
    d = math.hypot(dx, dy)
    d = max(min(d, L1 + L2 - 1e-6), abs(L1 - L2) + 1e-6)
    a = (L1 * L1 - L2 * L2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, L1 * L1 - a * a))
    mx = ax + a * dx / d
    my = ay + a * dy / d
    x1 = mx + h * (-dy / d)
    y1 = my + h * (dx / d)
    x2 = mx - h * (-dy / d)
    y2 = my - h * (dx / d)
    return (x1, y1) if y1 >= y2 else (x2, y2)


def _elbow_ik(shoulder, hand, forward):
    return _solve_joint(shoulder, hand, UA, FA, forward)


def _shoulder_at(hip, lean):
    return (hip[0] + T * math.sin(lean), hip[1] + T * math.cos(lean))


def _head_at(shoulder, lean, tip=0.0):
    return (shoulder[0] + HEAD * 1.05 * math.sin(lean + tip),
            shoulder[1] + HEAD * 1.05 * math.cos(lean + tip))


def _osc(ph):
    """Smooth 0 -> 1 -> 0 over one cycle (phase 0..1)."""
    return 0.5 - 0.5 * math.cos(2 * math.pi * ph)


def _foot_ang(ph):
    """Foot angle over a gait cycle: heel-strike -> flat (pause) -> toe-off."""
    if ph < 0.5:
        t = ph * 2
        if t < 0.25:
            return 0.30 * (1 - t / 0.25)
        if t < 0.70:
            return 0.0
        return -0.40 * ((t - 0.70) / 0.30)
    t = (ph - 0.5) * 2
    return -0.40 + 0.70 * t


# ── archetype poses (each returns a dict of joints + props) ──────────
def pose_squat(ph):
    d = _osc(ph)
    lean = 0.30 * d
    hip = (-0.10 * d, 0.96 - 0.46 * d)
    ankle = STAND['ankle']
    knee = _knee_ik(hip, ankle)
    shoulder = _shoulder_at(hip, lean)
    head = _head_at(shoulder, lean)
    plate = (shoulder[0] - 0.10, shoulder[1] + 0.02)
    elbow = _elbow_ik(shoulder, plate, False)
    return dict(ankle=ankle, knee=knee, hip=hip, shoulder=shoulder, head=head,
                elbow=elbow, hand=plate, plate=plate, equipment='barbell',
                highlight='legs', root='standing')


def pose_hinge(ph):
    d = _osc(ph)
    lean = 0.10 + 1.05 * d
    hip = (-0.30 * d, 0.96 - 0.26 * d)
    ankle = STAND['ankle']
    knee = _knee_ik(hip, ankle)
    shoulder = _shoulder_at(hip, lean)
    head = _head_at(shoulder, lean)
    hand = (shoulder[0], shoulder[1] - (UA + FA))
    elbow = (shoulder[0], shoulder[1] - UA)
    return dict(ankle=ankle, knee=knee, hip=hip, shoulder=shoulder, head=head,
                elbow=elbow, hand=hand, plate=hand, equipment='barbell',
                highlight='legs', root='standing')


def pose_push_h(ph):
    d = _osc(ph)
    bench = 0.34
    hip = (0.0, bench)
    knee = (-L1, bench)
    ankle = (-L1 - L2, bench)
    shoulder = (T, bench)
    head = (T + HEAD * 1.1, bench + 0.02)
    hand = (0.38 + 0.09 * d, 0.42 + 0.61 * d)
    elbow = _elbow_ik(shoulder, hand, False)
    return dict(ankle=ankle, knee=knee, hip=hip, shoulder=shoulder, head=head,
                elbow=elbow, hand=hand, plate=hand, equipment='barbell',
                highlight='torso', root='lying')


def pose_push_v(ph):
    d = _osc(ph)
    grip = 0.26
    hip = (0.0, 0.96)
    near_ankle = (0.07, 0.04)
    near_knee = (0.07, 0.04 + L2)
    far_ankle = (-0.07, 0.04)
    far_knee = (-0.07, 0.04 + L2)
    shoulder = (0.0, hip[1] + T)
    head = (0.0, shoulder[1] + HEAD * 1.05)
    ua = (160 - 136 * d) * math.pi / 180
    sin_fa = (grip - UA * math.sin(ua)) / FA
    fa = math.asin(max(-1.0, min(1.0, sin_fa)))
    near_elbow = (shoulder[0] + UA * math.sin(ua), shoulder[1] + UA * math.cos(ua))
    near_hand = (grip, near_elbow[1] + FA * math.cos(fa))
    far_elbow = (shoulder[0] - UA * math.sin(ua), shoulder[1] + UA * math.cos(ua))
    far_hand = (-grip, far_elbow[1] + FA * math.cos(fa))
    bar_y = near_hand[1]
    return dict(ankle=near_ankle, knee=near_knee, ankle2=far_ankle, knee2=far_knee,
                hip=hip, shoulder=shoulder, head=head, elbow=near_elbow, hand=near_hand,
                elbow2=far_elbow, hand2=far_hand,
                bar=((-grip - 0.22, bar_y), (grip + 0.22, bar_y)),
                equipment='barbell', highlight='arms', root='standing')


def pose_pull_h(ph):
    d = _osc(ph)
    lean = 0.85
    hip = (-0.15, 0.88)
    ankle = STAND['ankle']
    knee = _knee_ik(hip, ankle)
    shoulder = _shoulder_at(hip, lean)
    head = _head_at(shoulder, lean)
    ua = (180 + 105 * d) * math.pi / 180
    fa = (180 - 38 * d) * math.pi / 180
    elbow = (shoulder[0] + UA * math.sin(ua), shoulder[1] + UA * math.cos(ua))
    hand = (elbow[0] + FA * math.sin(fa), elbow[1] + FA * math.cos(fa))
    return dict(ankle=ankle, knee=knee, hip=hip, shoulder=shoulder, head=head,
                elbow=elbow, hand=hand, plate=hand, equipment='dumbbell',
                highlight='torso', root='standing')


def pose_pull_v(ph):
    d = _osc(ph)
    seat = 0.42
    hip = (0.0, seat)
    knee = (0.30, seat)
    ankle = (0.30, 0.04)
    shoulder = (0.0, seat + T)
    head = (0.0, seat + T + HEAD * 1.1)
    ua = (165 * d) * math.pi / 180
    fa = (-12 * d) * math.pi / 180
    elbow = (shoulder[0] + UA * math.sin(ua), shoulder[1] + UA * math.cos(ua))
    hand = (elbow[0] + FA * math.sin(fa), elbow[1] + FA * math.cos(fa))
    return dict(ankle=ankle, knee=knee, hip=hip, shoulder=shoulder, head=head,
                elbow=elbow, hand=hand, plate=hand, equipment='cable',
                anchor=(0.02, shoulder[1] + 1.0), highlight='torso', root='seated')


def pose_curl(ph):
    theta = 2.6 * _osc(ph)
    ankle = (0.0, 0.04)
    knee = (0.0, 0.04 + L2)
    hip = (0.0, 0.04 + L2 + L1)
    shoulder = (0.0, hip[1] + T)
    head = (0.0, shoulder[1] + HEAD * 1.05)
    elbow = (shoulder[0] + UA * math.sin(0.12), shoulder[1] - UA * math.cos(0.12))
    hand = (elbow[0] + FA * math.sin(theta), elbow[1] - FA * math.cos(theta))
    return dict(ankle=ankle, knee=knee, hip=hip, shoulder=shoulder, head=head,
                elbow=elbow, hand=hand, plate=hand, equipment='dumbbell',
                highlight='arms', root='standing')


def pose_tricep(ph):
    d = _osc(ph)
    hip = (0.0, 0.96)
    ankle = STAND['ankle']
    knee = _knee_ik(hip, ankle)
    shoulder = (0.0, hip[1] + T)
    head = (0.0, shoulder[1] + HEAD * 1.05)
    elbow = (0.02, shoulder[1] + UA)
    ang = (220 + 140 * d) * math.pi / 180
    hand = (elbow[0] + FA * math.sin(ang), elbow[1] + FA * math.cos(ang))
    return dict(ankle=ankle, knee=knee, hip=hip, shoulder=shoulder, head=head,
                elbow=elbow, hand=hand, plate=hand, equipment='dumbbell',
                highlight='arms', root='standing')


def pose_core_flex(ph):
    d = _osc(ph)
    hip = (0.0, 0.02)
    ang = (270 + 90 * d) * math.pi / 180
    knee = (hip[0] + L1 * math.sin(ang), hip[1] + L1 * math.cos(ang))
    ankle = (hip[0] + (L1 + L2) * math.sin(ang), hip[1] + (L1 + L2) * math.cos(ang))
    shoulder = (0.40, 0.02)
    head = (0.55, 0.03)
    hand = (0.20, 0.02)
    elbow = (0.28, 0.02)
    return dict(ankle=ankle, knee=knee, hip=hip, shoulder=shoulder, head=head,
                elbow=elbow, hand=hand, plate=None, equipment='bodyweight',
                highlight='torso', root='floor')


def pose_plank(ph):
    bob = 0.012 * math.sin(2 * math.pi * ph * 2)
    shoulder = (0.48, 0.38 + bob)
    toe = (-0.952, 0.0)
    ankle = (-0.892, 0.10)
    body = T + L1 + L2
    dirx = (ankle[0] - shoulder[0]) / body
    diry = (ankle[1] - shoulder[1]) / body
    hip = (shoulder[0] + T * dirx, shoulder[1] + T * diry)
    knee = (hip[0] + L1 * dirx, hip[1] + L1 * diry)
    head = (shoulder[0] + 0.15, shoulder[1] + 0.01)
    elbow = (shoulder[0], 0.0)
    hand = (elbow[0] + FA, 0.0)
    return dict(ankle=ankle, toe=toe, knee=knee, hip=hip, shoulder=shoulder,
                head=head, elbow=elbow, hand=hand, plate=None, equipment='bodyweight',
                highlight='torso', root='plank')


def pose_lateral(ph):
    d = _osc(ph)
    hip = (0.0, 0.96)
    near_ankle = (0.07, 0.04)
    near_knee = (0.07, 0.04 + L2)
    far_ankle = (-0.07, 0.04)
    far_knee = (-0.07, 0.04 + L2)
    shoulder = (0.0, hip[1] + T)
    head = (0.0, shoulder[1] + HEAD * 1.05)
    near_hand = (0.06 + 0.50 * d, shoulder[1] - 0.66 + 0.66 * d)
    near_elbow = _elbow_ik(shoulder, near_hand, True)
    far_hand = (-0.06 - 0.50 * d, shoulder[1] - 0.66 + 0.66 * d)
    far_elbow = _elbow_ik(shoulder, far_hand, False)
    return dict(ankle=near_ankle, knee=near_knee, ankle2=far_ankle, knee2=far_knee,
                hip=hip, shoulder=shoulder, head=head, elbow=near_elbow, hand=near_hand,
                elbow2=far_elbow, hand2=far_hand, plate=near_hand, plate2=far_hand,
                equipment='dumbbell', highlight='arms', root='standing')


def _leg_at(ph):
    stride = 0.40
    lift = 0.14
    foot_y = 0.04
    if ph < 0.5:
        t = ph * 2
        x = stride * 0.5 * (1 - 2 * t)
        y = foot_y
        if t < 0.25:
            ang = 0.30 * (1 - t / 0.25)
        elif t < 0.70:
            ang = 0.0
        else:
            ang = -0.40 * ((t - 0.70) / 0.30)
    else:
        u = (ph - 0.5) * 2
        x = -stride * 0.5 + stride * u
        y = foot_y + lift * math.sin(math.pi * u)
        ang = -0.40 + 0.70 * u
    return dict(x=x, y=y, ang=ang)


def pose_carry(ph):
    near = _leg_at(ph)
    far = _leg_at((ph + 0.5) % 1)
    bob = -0.02 * math.sin(4 * math.pi * ph)
    lean = 0.08
    hip = (0.0, 0.93 + bob)
    near_ankle = (near['x'] + 0.02, near['y'])
    far_ankle = (far['x'] - 0.02, far['y'])
    near_knee = _knee_ik(hip, near_ankle)
    far_knee = _knee_ik(hip, far_ankle)
    shoulder = _shoulder_at(hip, lean)
    head = _head_at(shoulder, lean)
    hand = (0.05, shoulder[1] - (UA + FA))
    elbow = (0.05, shoulder[1] - UA)
    return dict(ankle=near_ankle, knee=near_knee, ankle2=far_ankle, knee2=far_knee,
                hip=hip, shoulder=shoulder, head=head, elbow=elbow, hand=hand,
                plate=hand, equipment='dumbbell', foot_ang=near['ang'],
                foot_ang2=far['ang'], highlight='full', root='standing')


def pose_cycle(ph):
    theta = 2 * math.pi * ph
    bb = (0.02, 0.20)
    r = 0.12
    hip = (-0.18, 0.88)
    pedal1 = (bb[0] + r * math.cos(theta), bb[1] - r * math.sin(theta))
    pedal2 = (bb[0] + r * math.cos(theta + math.pi), bb[1] - r * math.sin(theta + math.pi))
    near_knee = _knee_ik(hip, pedal1)
    far_knee = _knee_ik(hip, pedal2)
    lean = 0.85
    shoulder = _shoulder_at(hip, lean)
    head = _head_at(shoulder, lean)
    hand = (0.40, 0.62)
    elbow = _elbow_ik(shoulder, hand, False)
    return dict(ankle=pedal1, knee=near_knee, ankle2=pedal2, knee2=far_knee,
                hip=hip, shoulder=shoulder, head=head, elbow=elbow, hand=hand,
                bike=dict(bb=bb, pedal1=pedal1, pedal2=pedal2, spin=theta,
                          wheels=[(-0.32, 0.22), (0.32, 0.22)], wheel_r=0.22,
                          seat=hip, seat_j=(-0.18, 0.78), head_j=(0.30, 0.70), bars=hand),
                equipment='bike', highlight='legs', root='seated')


def pose_calf(ph):
    rise = 0.08 * _osc(ph)
    hip = (0.0, 0.96 + rise)
    knee = (0.0, 0.50 + rise)
    ankle = (0.0, 0.04 + rise)
    shoulder = (0.0, hip[1] + T)
    head = (0.0, shoulder[1] + HEAD * 1.05)
    hand = (0.03, shoulder[1] - (UA + FA))
    elbow = (0.03, shoulder[1] - UA)
    return dict(ankle=ankle, knee=knee, hip=hip, shoulder=shoulder, head=head,
                elbow=elbow, hand=hand, plate=None, equipment='bodyweight',
                foot_ang=-0.5 * _osc(ph), highlight='legs', root='standing')


def pose_crunch(ph):
    a = 0.85 * _osc(ph)
    hip = (0.0, 0.02)
    knee = (0.10, 0.44)
    ankle = (-0.10, 0.04)
    shoulder = (hip[0] + T * math.cos(a), hip[1] + T * math.sin(a))
    head = (hip[0] + (T + HEAD * 1.05) * math.cos(a),
            hip[1] + (T + HEAD * 1.05) * math.sin(a))
    elbow = (shoulder[0] - 0.10, shoulder[1] + 0.02)
    hand = (shoulder[0] - 0.26, shoulder[1] + 0.06)
    return dict(ankle=ankle, knee=knee, hip=hip, shoulder=shoulder, head=head,
                elbow=elbow, hand=hand, plate=None, equipment='bodyweight',
                highlight='torso', root='floor')


def pose_pushup(ph):
    d = _osc(ph)
    hand = (0.40, 0.0)
    toe = (-0.756, 0.0)
    ankle = (-0.716, 0.10)
    body = 1.40
    sy = 0.69 - 0.39 * d
    dy = sy - ankle[1]
    sx = ankle[0] + math.sqrt(body * body - dy * dy)
    shoulder = (sx, sy)
    dirx = (ankle[0] - sx) / body
    diry = (ankle[1] - sy) / body
    hip = (sx + T * dirx, sy + T * diry)
    knee = (sx + (T + L1) * dirx, sy + (T + L1) * diry)
    head = (sx + 0.10, sy + 0.12)
    elbow = _elbow_ik(shoulder, hand, False)
    return dict(ankle=ankle, toe=toe, knee=knee, hip=hip, shoulder=shoulder,
                head=head, elbow=elbow, hand=hand, plate=None, equipment='bodyweight',
                highlight='torso', root='plank')


def pose_bridge(ph):
    a = 1.1 * _osc(ph)
    shoulder = (0.0, 0.02)
    head = (-0.15, 0.03)
    hip = (shoulder[0] + T * math.cos(a), shoulder[1] + T * math.sin(a))
    ankle = (0.70, 0.04)
    knee = _knee_up(hip, ankle)
    elbow = (0.20, 0.02)
    hand = (0.30, 0.02)
    return dict(ankle=ankle, knee=knee, hip=hip, shoulder=shoulder, head=head,
                elbow=elbow, hand=hand, plate=None, equipment='bodyweight',
                highlight='legs', root='floor')


def pose_kb_swing(ph):
    hinge = _osc(ph)
    hip = (-0.30 * hinge, 0.96 - 0.20 * hinge)
    ankle = STAND['ankle']
    knee = _knee_ik(hip, ankle)
    lean = 0.10 + 0.95 * hinge
    shoulder = _shoulder_at(hip, lean)
    head = _head_at(shoulder, lean)
    a = -0.5 + 1.8 * (1 - hinge)
    hand = (shoulder[0] + (UA + FA) * math.sin(a),
            shoulder[1] - (UA + FA) * math.cos(a))
    elbow = (shoulder[0] + UA * math.sin(a), shoulder[1] - UA * math.cos(a))
    return dict(ankle=ankle, knee=knee, hip=hip, shoulder=shoulder, head=head,
                elbow=elbow, hand=hand, plate=hand, equipment='kettlebell',
                highlight='legs', root='standing')


def pose_leg_ext(ph):
    d = _osc(ph)
    seat = 0.55
    hip = (0.0, seat)
    knee = (0.30, seat - 0.06)
    a = math.pi / 2 * d
    ankle = (knee[0] + L2 * math.sin(a), knee[1] - L2 * math.cos(a))
    shoulder = (0.0, seat + T)
    head = (0.0, shoulder[1] + HEAD * 1.05)
    hand = (-0.03, seat + 0.08)
    elbow = _elbow_ik(shoulder, hand, False)
    return dict(ankle=ankle, knee=knee, hip=hip, shoulder=shoulder, head=head,
                elbow=elbow, hand=hand, foot_ang=a, equipment='machine',
                highlight='legs', root='seated',
                machine=dict(seat=(0.0, seat), back=(-0.07, seat + 0.02), pivot=knee,
                             pad=ankle, stack=(-0.34, 0.40 + 0.18 * d),
                             stack_top=0.60, n=4))


def pose_leg_curl(ph):
    d = _osc(ph)
    bench = 0.34
    hip = (0.0, bench)
    knee = (-L1, bench)
    a = math.pi / 2 * d
    ankle = (knee[0] - L2 * math.cos(a), bench + L2 * math.sin(a))
    shoulder = (T, bench)
    head = (T + HEAD * 1.1, bench + 0.02)
    hand = (T + 0.14, bench + 0.08)
    elbow = _elbow_ik(shoulder, hand, False)
    return dict(ankle=ankle, knee=knee, hip=hip, shoulder=shoulder, head=head,
                elbow=elbow, hand=hand, equipment='machine',
                highlight='legs', root='lying',
                machine=dict(pivot=knee, pad=ankle, stack=(-0.66, 0.40 + 0.18 * d),
                             stack_top=0.60, n=4))


def pose_cable_row(ph):
    d = _osc(ph)
    seat = 0.30
    hip = (0.0, seat)
    knee = (0.30, seat)
    ankle = (0.30, 0.06)
    shoulder = (0.0, seat + T)
    head = (0.0, seat + T + HEAD * 1.05)
    hand = (0.42 - 0.34 * d, 0.72 - 0.22 * d)
    elbow = _elbow_ik(shoulder, hand, False)
    return dict(ankle=ankle, knee=knee, hip=hip, shoulder=shoulder, head=head,
                elbow=elbow, hand=hand, equipment='cable', anchor=(0.55, 0.30),
                highlight='torso', root='seated',
                machine=dict(seat=(0.0, seat), footplate=(0.34, 0.06)))


def pose_row_machine(ph):
    d = _osc(ph)
    seat = 0.30
    hip = (0.15 - 0.60 * d, seat)
    ankle = (0.40, 0.12)
    k_bent = _knee_ik(hip, ankle)
    dist = math.hypot(ankle[0] - hip[0], ankle[1] - hip[1]) or 1e-6
    k_straight = (hip[0] + (ankle[0] - hip[0]) * L1 / dist,
                  hip[1] + (ankle[1] - hip[1]) * L1 / dist)
    knee = (k_bent[0] + (k_straight[0] - k_bent[0]) * d,
            k_bent[1] + (k_straight[1] - k_bent[1]) * d)
    lean = 0.30 - 0.50 * d
    shoulder = _shoulder_at(hip, lean)
    head = _head_at(shoulder, lean)
    hand = (0.44 - 0.49 * d, 0.40 + 0.08 * d)
    elbow = _elbow_ik(shoulder, hand, False)
    return dict(ankle=ankle, knee=knee, hip=hip, shoulder=shoulder, head=head,
                elbow=elbow, hand=hand, equipment='machine', highlight='full',
                root='seated',
                machine=dict(rail=((0.52, 0.06), (-0.48, 0.06)), fly=(0.46, 0.30),
                             seat=(hip[0], seat), footplate=(0.40, 0.12),
                             chain=(hand, (0.46, 0.30))))


ARCHETYPES = [
    dict(id='squat',       name='Squat',            subtitle='legs · barbell',       pose=pose_squat),
    dict(id='hinge',       name='Hinge (Deadlift)', subtitle='legs · barbell',       pose=pose_hinge),
    dict(id='push_h',      name='Bench Press',      subtitle='chest · barbell',      pose=pose_push_h),
    dict(id='push_v',      name='Overhead Press',   subtitle='shoulders · barbell',  pose=pose_push_v),
    dict(id='pull_h',      name='Bent-Over Row',    subtitle='back · dumbbell',      pose=pose_pull_h),
    dict(id='pull_v',      name='Lat Pulldown',     subtitle='back · cable',         pose=pose_pull_v),
    dict(id='curl',        name='Bicep Curl',       subtitle='arms · dumbbell',      pose=pose_curl),
    dict(id='tricep',      name='Tricep Extension', subtitle='arms · dumbbell',      pose=pose_tricep),
    dict(id='core_flex',   name='Leg Raise',        subtitle='core · bodyweight',    pose=pose_core_flex),
    dict(id='plank',       name='Plank',            subtitle='core · hold',          pose=pose_plank),
    dict(id='lateral',     name='Lateral Raise',    subtitle='shoulders · dumbbell', pose=pose_lateral),
    dict(id='carry',       name="Farmer's Carry",   subtitle='full body · dumbbells', pose=pose_carry),
    dict(id='cycle',       name='Cycling',          subtitle='cardio · legs',        pose=pose_cycle),
    dict(id='calf',        name='Calf Raise',       subtitle='calves · bodyweight',  pose=pose_calf),
    dict(id='crunch',      name='Crunch',           subtitle='core · bodyweight',    pose=pose_crunch),
    dict(id='pushup',      name='Push-Up',          subtitle='chest · bodyweight',   pose=pose_pushup),
    dict(id='bridge',      name='Glute Bridge',     subtitle='glutes · bodyweight',  pose=pose_bridge),
    dict(id='kb_swing',    name='Kettlebell Swing', subtitle='glutes · kettlebell',  pose=pose_kb_swing),
    dict(id='leg_ext',     name='Leg Extension',    subtitle='quads · machine',      pose=pose_leg_ext),
    dict(id='leg_curl',    name='Leg Curl',         subtitle='hamstrings · machine', pose=pose_leg_curl),
    dict(id='cable_row',   name='Seated Cable Row', subtitle='back · machine',       pose=pose_cable_row),
    dict(id='row_machine', name='Rowing Machine',   subtitle='cardio · full body',   pose=pose_row_machine),
]

ARCHETYPE_BY_ID = {a['id']: a for a in ARCHETYPES}

CYCLES = {'plank': 3.0, 'carry': 1.0, 'cycle': 1.2}


def archetype_for(name='', equip='', muscle=''):
    """Map an exercise name/equip/muscle to the closest stick-figure archetype.

    Order matters: most specific matches come first.
    """
    n = (name or '').lower()

    def has(*words):
        return any(w in n for w in words)

    # cardio / machines
    if has('rowing machine', 'rower'):
        return 'row_machine'
    if has('cycling', 'spin bike', 'exercise bike', 'bike', 'jump rope', 'swimming', 'swim'):
        return 'cycle'
    if has('farmer', 'sled'):
        return 'carry'
    if has('run', 'walk', 'treadmill', 'elliptical', 'jog', 'sprint', 'stair',
           'burpee', 'high knee'):
        return 'carry'

    # core
    if has('plank', 'shoulder tap', 'hollow', 'superman', 'dragon flag', 'l-sit',
           'ab roller', 'mountain climber'):
        return 'plank'
    if has('crunch', 'sit-up', 'sit up', 'bicycle', 'russian twist', 'dead bug', 'woodchop'):
        return 'crunch'
    if has('leg raise', 'legraise'):
        return 'core_flex'
    if has('bridge', 'hip thrust'):
        return 'bridge'

    # bodyweight press / lower
    if has('push-up', 'push up', 'pushup'):
        return 'pushup'
    if has('calf'):
        return 'calf'

    # isolation machines
    if has('leg extension', 'leg ext'):
        return 'leg_ext'
    if has('leg curl'):
        return 'leg_curl'
    if has('abduction', 'adduction'):
        return 'leg_ext'
    if has('seated row', 'seated cable row'):
        return 'cable_row'

    # kettlebell / explosive hip
    if has('kettlebell swing', 'swing', 'clean', 'snatch'):
        return 'kb_swing'

    # arms / shoulders
    if has('lateral raise', 'front raise', 'halo'):
        return 'lateral'
    if has('tricep', 'triceps', 'pushdown', 'skull crusher', 'kickback', 'overhead extension'):
        return 'tricep'
    if has('curl'):
        return 'curl'

    # pulls
    if has('pulldown', 'pull-up', 'pull up', 'pullup', 'chin-up', 'chin up'):
        return 'pull_v'
    if has('face pull', 'pull-apart', 'pull apart'):
        return 'pull_h'
    if has('pull-through', 'pull through'):
        return 'hinge'
    if has('row'):
        return 'pull_h'

    # hinges / lower
    if has('deadlift', 'good morning', 'romanian'):
        return 'hinge'
    if has('squat', 'lunge', 'leg press', 'hack squat', 'wall sit', 'step-up', 'step up'):
        return 'squat'

    # presses
    if has('overhead press', 'shoulder press', 'military press', 'arnold press', 'push press'):
        return 'push_v'
    if has('bench press', 'chest press', 'floor press', 'fly', 'dip', 'pec deck',
           'crossover', 'pullover'):
        return 'push_h'
    if has('press'):
        return 'push_h'

    # fallbacks by muscle
    if muscle == 'Core':
        return 'plank'
    if muscle == 'Cardio':
        return 'cycle'
    return 'squat'


class StickmanWidget(Widget):
    """Renders and animates a single stick-figure archetype."""

    def __init__(self, archetype='squat', animate=True, **kwargs):
        super().__init__(**kwargs)
        self._archetype = archetype
        self._animate = animate
        self._t = 0.0
        self._shown = False
        self._scale = 1.0
        self._cx = 0.0
        self._gy = 0.0
        self.bind(pos=self._redraw, size=self._redraw)
        if animate:
            Clock.schedule_interval(self._tick, 1.0 / 40.0)

    def set_archetype(self, archetype):
        self._archetype = archetype
        self._t = 0.0
        self._redraw()

    def stop(self):
        Clock.unschedule(self._tick)

    # ── animation / lifecycle ──
    def _tick(self, dt):
        win = self.get_root_window()
        if win is None:
            if self._shown:
                self.stop()
            return
        self._shown = True
        self._t += dt
        self._redraw()

    def _redraw(self, *args):
        self.canvas.clear()
        if self.width < 20 or self.height < 20:
            return
        a = ARCHETYPE_BY_ID.get(self._archetype, ARCHETYPES[0])
        cycle = CYCLES.get(a['id'], 2.6)
        ph = (self._t % cycle) / cycle
        p = a['pose'](ph)

        self._scale = self.height * 0.92 / 2.05
        self._gy = self.y + self.height * 0.06

        if a['id'] == 'carry':
            stride = 0.40
            fig_half = 0.6 * self._scale
            span = self.width + 2 * fig_half
            dist_px = (2 * stride * (self._t / cycle)) * self._scale
            self._cx = self.x - fig_half + (dist_px % span)
            p['no_ground'] = True
            with self.canvas:
                Color(0.30, 0.30, 0.35, 1)
                Line(points=[self.x, self._gy, self.x + self.width, self._gy], width=1)
        else:
            self._cx = self.x + self.width / 2.0

        with self.canvas:
            self._draw_figure(p)

    # ── coordinate mapping ──
    def _X(self, x):
        return self._cx + x * self._scale

    def _Y(self, y):
        return self._gy + y * self._scale

    # ── primitives (emit into the active canvas) ──
    def _seg(self, a, b, color, width):
        Color(*color)
        Line(points=[self._X(a[0]), self._Y(a[1]), self._X(b[0]), self._Y(b[1])],
             width=dp(width), cap='round', joint='round')

    def _dot(self, pt, color, radius):
        Color(*color)
        Ellipse(pos=(self._X(pt[0]) - radius, self._Y(pt[1]) - radius),
                size=(2 * radius, 2 * radius))

    def _circle(self, pt, color, radius, width):
        Color(*color)
        Line(circle=(self._X(pt[0]), self._Y(pt[1]), radius), width=dp(width))

    def _fill_rect(self, x, y_top, w, h, color):
        Color(*color)
        Rectangle(pos=(self._X(x), self._Y(y_top - h)),
                  size=(w * self._scale, h * self._scale))

    # ── props ──
    def _draw_bike(self, b):
        light = (0.85, 0.85, 0.90)
        wr = b.get('wheel_r', 0.22)
        a = -b['spin'] * 2
        for w in b['wheels']:
            self._circle(w, (0.59, 0.61, 0.67), wr * self._scale, 2.5)
            self._seg((w[0] - wr * math.cos(a), w[1] - wr * math.sin(a)),
                      (w[0] + wr * math.cos(a), w[1] + wr * math.sin(a)),
                      (0.59, 0.61, 0.67), 1.5)
            self._dot(w, (0.6, 0.62, 0.68), 0.03 * self._scale)
        # saddle + handlebars (drop bars)
        self._seg((b['seat'][0] - 0.09, b['seat'][1]), (b['seat'][0] + 0.10, b['seat'][1]), light, 5)
        self._seg(b['head_j'], (0.38, 0.72), STEEL, 2.5)
        self._seg((0.38, 0.72), b['bars'], STEEL, 2.5)
        self._seg((b['bars'][0] - 0.06, b['bars'][1]), (b['bars'][0] + 0.04, b['bars'][1]), light, 3)
        # crank arms + pedals
        self._seg(b['bb'], b['pedal1'], STEEL, 3)
        self._seg(b['bb'], b['pedal2'], STEEL, 3)
        self._seg((b['pedal1'][0] - 0.05, b['pedal1'][1]), (b['pedal1'][0] + 0.05, b['pedal1'][1]), light, 3.5)
        self._seg((b['pedal2'][0] - 0.05, b['pedal2'][1]), (b['pedal2'][0] + 0.05, b['pedal2'][1]), light, 3.5)

    def _draw_machine(self, m):
        if 'seat' in m:
            if 'rail' in m:
                self._seg((m['seat'][0] - 0.08, m['seat'][1]), (m['seat'][0] + 0.08, m['seat'][1]), PAD, 6)
            else:
                self._seg((m['seat'][0] - 0.10, m['seat'][1]), (m['seat'][0] + 0.10, m['seat'][1]), PAD, 7)
                self._seg((m['seat'][0] + 0.08, m['seat'][1]), (m['seat'][0] + 0.08, 0.04), STEEL, 2.5)
        if 'back' in m:
            self._seg((m['back'][0] - 0.02, m['back'][1] - 0.05),
                      (m['back'][0] + 0.05, m['back'][1] + 0.30), PAD, 8)
        if 'footplate' in m:
            fp = m['footplate']
            self._seg((fp[0], fp[1]), (fp[0], fp[1] + 0.18), PAD, 7)
            self._seg((fp[0] - 0.03, fp[1]), (fp[0] + 0.10, fp[1]), STEEL, 2.5)
        if 'pivot' in m and 'pad' in m:
            pivot, pad = m['pivot'], m['pad']
            self._seg(pivot, pad, STEEL, 3)
            ang = math.atan2(pad[1] - pivot[1], pad[0] - pivot[0])
            self._seg((pad[0] - 0.11 * math.cos(ang + math.pi / 2),
                       pad[1] - 0.11 * math.sin(ang + math.pi / 2)),
                      (pad[0] + 0.11 * math.cos(ang + math.pi / 2),
                       pad[1] + 0.11 * math.sin(ang + math.pi / 2)), PAD, 5)
        if 'stack' in m:
            n = m.get('n', 4)
            hh = 0.035
            Color(0.275, 0.29, 0.345, 1)
            for i in range(n):
                Rectangle(pos=(self._X(m['stack'][0] - 0.11), self._Y(m['stack'][1] - i * hh - hh * 0.72)),
                          size=(0.22 * self._scale, hh * 0.72 * self._scale))
            top = m.get('stack_top', m['stack'][1])
            self._seg((m['stack'][0] + 0.05, top), (m['stack'][0] + 0.05, 0.04), STEEL, 2.5)
            if 'pivot' in m:
                self._seg(m['stack'], m['pivot'], BAND + (0.8,), 1.5)
        if 'rail' in m:
            self._seg(m['rail'][0], m['rail'][1], STEEL, 2.5)
            if 'fly' in m:
                self._circle(m['fly'], (0.59, 0.61, 0.67), 0.12 * self._scale, 2)
                self._dot(m['fly'], (0.6, 0.62, 0.68), 0.02 * self._scale)
        if 'chain' in m:
            self._seg(m['chain'][0], m['chain'][1], BAND + (0.8,), 1.5)

    # ── figure ──
    def _draw_figure(self, p):
        h = p['highlight']
        leg_c = NEON if h in ('legs', 'full') else DIM
        arm_c = NEON if h in ('arms', 'full') else DIM
        tor_c = NEON if h in ('torso', 'full') else DIM

        # ground + props
        if not p.get('no_ground'):
            self._seg((-0.9, 0.0), (0.9, 0.0), (0.30, 0.30, 0.35), 1)
        if p['root'] == 'lying':
            self._fill_rect(-0.95, 0.34, 1.9, 0.08, (0.235, 0.235, 0.275))
        if p['root'] == 'seated' and 'bike' not in p and 'machine' not in p:
            self._fill_rect(-0.20, 0.42, 0.42, 0.34, (0.235, 0.235, 0.275))

        # far limbs first (dimmer), then near limbs
        if p.get('knee2') is not None and p.get('ankle2') is not None:
            self._seg(p['ankle2'], p['knee2'], _dim(leg_c), 5)
            self._seg(p['knee2'], p['hip'], _dim(leg_c), 5)
            if p['root'] in ('standing', 'seated'):
                fa2 = p.get('foot_ang2', 0.0)
                self._seg((p['ankle2'][0] - 0.09 * math.cos(fa2), p['ankle2'][1] - 0.09 * math.sin(fa2)),
                          (p['ankle2'][0] + 0.15 * math.cos(fa2), p['ankle2'][1] + 0.15 * math.sin(fa2)),
                          _dim(leg_c), 5)
        if p.get('elbow2') is not None and p.get('hand2') is not None:
            self._seg(p['shoulder'], p['elbow2'], _dim(arm_c), 5)
            self._seg(p['elbow2'], p['hand2'], _dim(arm_c), 5)

        if p.get('bike'):
            self._draw_bike(p['bike'])
        if p.get('machine'):
            self._draw_machine(p['machine'])

        # legs
        if leg_c == NEON:
            self._seg(p['ankle'], p['knee'], NEON + (0.25,), 16)
            self._seg(p['knee'], p['hip'], NEON + (0.25,), 16)
        self._seg(p['ankle'], p['knee'], leg_c, 7)
        self._seg(p['knee'], p['hip'], leg_c, 7)
        if p['root'] in ('standing', 'seated'):
            fa = p.get('foot_ang', 0.0)
            self._seg((p['ankle'][0] - 0.09 * math.cos(fa), p['ankle'][1] - 0.09 * math.sin(fa)),
                      (p['ankle'][0] + 0.15 * math.cos(fa), p['ankle'][1] + 0.15 * math.sin(fa)),
                      leg_c, 6)
        if p['root'] == 'plank':
            self._seg(p['ankle'], p['toe'], leg_c, 6)

        # torso
        if tor_c == NEON:
            self._seg(p['hip'], p['shoulder'], NEON + (0.25,), 16)
        self._seg(p['hip'], p['shoulder'], tor_c, 7)

        # arms
        if arm_c == NEON:
            self._seg(p['shoulder'], p['elbow'], NEON + (0.25,), 14)
            self._seg(p['elbow'], p['hand'], NEON + (0.25,), 14)
        self._seg(p['shoulder'], p['elbow'], arm_c, 6)
        self._seg(p['elbow'], p['hand'], arm_c, 6)

        # head
        self._dot(p['head'], DIM, HEAD * self._scale)

        # equipment
        if p.get('plate'):
            pr = (0.09 if p['equipment'] == 'barbell' else
                  (0.08 if p['equipment'] == 'kettlebell' else 0.07)) * self._scale
            fill = KETTLE if p['equipment'] == 'kettlebell' else PLATE
            self._dot(p['plate'], fill, pr)
            self._circle(p['plate'], BAR, pr, 1.5)
            if p['equipment'] == 'kettlebell':
                # handle on top (upper semicircle)
                Color(*BAR)
                Line(ellipse=(self._X(p['plate'][0]) - pr * 0.55, self._Y(p['plate'][1]) - pr * 0.55,
                              2 * pr * 0.55, 2 * pr * 0.55, 180, 360), width=dp(1.5))
            else:
                self._dot(p['plate'], BAR, 0.035 * self._scale)
        if p.get('plate2'):
            pr = (0.09 if p['equipment'] == 'barbell' else
                  (0.08 if p['equipment'] == 'kettlebell' else 0.07)) * self._scale
            self._dot(p['plate2'], PLATE, pr)
            self._circle(p['plate2'], BAR, pr, 1.5)
            self._dot(p['plate2'], BAR, 0.035 * self._scale)
        if p.get('bar'):
            self._seg(p['bar'][0], p['bar'][1], BAR, 5)
            pr = 0.08 * self._scale
            self._dot(p['bar'][0], PLATE, pr)
            self._dot(p['bar'][1], PLATE, pr)
            self._circle(p['bar'][0], BAR, pr, 1.5)
            self._circle(p['bar'][1], BAR, pr, 1.5)
            self._dot(p['bar'][0], BAR, 0.035 * self._scale)
            self._dot(p['bar'][1], BAR, 0.035 * self._scale)
        if p['equipment'] == 'cable' and p.get('anchor'):
            self._seg(p['anchor'], p['hand'], BAND + (0.8,), 2)

        # joints
        self._dot(p['hip'], leg_c, dp(5))
        self._dot(p['knee'], leg_c, dp(5))
        if p.get('knee2') is not None and p.get('ankle2') is not None:
            self._dot(p['knee2'], _dim(leg_c), dp(4))
        self._dot(p['shoulder'], tor_c, dp(4))
        self._dot(p['elbow'], arm_c, dp(3.5))
        if p.get('elbow2') is not None and p.get('hand2') is not None:
            self._dot(p['elbow2'], _dim(arm_c), dp(3))
