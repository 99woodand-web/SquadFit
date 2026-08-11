"""
animations.py — Micro-animation utilities for Squad Fit
Provides press effects, card feedback, and smooth transition helpers.
"""

from kivy.animation import Animation
from kivy.metrics import dp


# =============================================================================
#  PRESS EFFECT — Scale down on press, spring back on release
# =============================================================================
def press_effect(widget, scale=0.96, duration=0.08):
    """
    Apply a subtle scale-down press effect to any widget.
    Call on_press: root.press_down(self)
    Call on_release: root.press_up(self)
    """
    anim = Animation(
        scale_x=scale, scale_y=scale,
        duration=duration, t='out_quad'
    )
    anim.start(widget)


def release_effect(widget, duration=0.15):
    """
    Spring the widget back to full size after press.
    Call on_release: root.press_up(self)
    """
    anim = Animation(
        scale_x=1.0, scale_y=1.0,
        duration=duration, t='out_elastic'
    )
    anim.start(widget)


# =============================================================================
#  CARD PRESS — Opacity flash + scale for card-style widgets
# =============================================================================
def card_press_down(widget, opacity_target=0.85, scale=0.97, duration=0.06):
    """Darken and shrink card on press."""
    anim = Animation(
        opacity=opacity_target,
        scale_x=scale, scale_y=scale,
        duration=duration, t='out_quad'
    )
    anim.start(widget)


def card_press_up(widget, duration=0.2):
    """Restore card after press."""
    anim = Animation(
        opacity=1.0,
        scale_x=1.0, scale_y=1.0,
        duration=duration, t='out_elastic'
    )
    anim.start(widget)


# =============================================================================
#  BUTTON FEEDBACK — Quick opacity flash on tap
# =============================================================================
def button_flash(widget, flash_opacity=0.6, duration=0.08):
    """Subtle quick opacity flash when a button is tapped."""
    anim = Animation(opacity=flash_opacity, duration=duration, t='out_quad')

    def _restore(*args):
        Animation(opacity=1.0, duration=0.12, t='out_quad').start(widget)

    anim.bind(on_complete=_restore)
    anim.start(widget)


# =============================================================================
#  SCREEN TRANSITION HELPERS
# =============================================================================
def slide_in_from_right(screen_manager, duration=0.25):
    """Smooth slide-in from right for forward navigation."""
    from kivy.uix.screenmanager import SlideTransition
    sm = screen_manager
    sm.transition = SlideTransition(direction='left', duration=duration)
    sm.transition.transition_progress = 0


def slide_in_from_left(screen_manager, duration=0.25):
    """Smooth slide-in from left for back navigation."""
    from kivy.uix.screenmanager import SlideTransition
    sm = screen_manager
    sm.transition = SlideTransition(direction='right', duration=duration)
    sm.transition.transition_progress = 0


def fade_transition(screen_manager, duration=0.3):
    """Clean fade transition for modals and overlays."""
    from kivy.uix.screenmanager import FadeTransition
    sm = screen_manager
    sm.transition = FadeTransition(duration=duration)


# =============================================================================
#  FADE IN / OUT — For revealing and hiding elements
# =============================================================================
def fade_in(widget, duration=0.3, delay=0):
    """Fade a widget in from transparent."""
    widget.opacity = 0
    anim = Animation(opacity=1.0, duration=duration, t='out_quad')
    if delay > 0:
        anim.cancel_all(widget)
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: anim.start(widget), delay)
    else:
        anim.start(widget)


def fade_out(widget, duration=0.2):
    """Fade a widget out to transparent."""
    anim = Animation(opacity=0, duration=duration, t='in_quad')
    anim.start(widget)


# =============================================================================
#  SLIDE UP — For banners and floating elements
# =============================================================================
def slide_up(widget, target_y, duration=0.3, t='out_quad'):
    """Slide a widget up to a target Y position."""
    anim = Animation(y=target_y, duration=duration, t=t)
    anim.start(widget)


def slide_down(widget, target_y, duration=0.3, t='in_quad'):
    """Slide a widget down to a target Y position."""
    anim = Animation(y=target_y, duration=duration, t=t)
    anim.start(widget)


# =============================================================================
#  PULSE — For attention-drawing elements (like timers)
# =============================================================================
def pulse(widget, scale=1.05, duration=0.3, repeats=1):
    """Quick scale pulse animation for drawing attention."""
    anim = Animation(
        scale_x=scale, scale_y=scale,
        duration=duration, t='in_out_sine'
    ) + Animation(
        scale_x=1.0, scale_y=1.0,
        duration=duration, t='in_out_sine'
    )
    if repeats > 1:
        anim.repeat = repeats - 1
    anim.start(widget)


# =============================================================================
#  STAGGER — Animate a list of widgets with delay between each
# =============================================================================
def stagger_in(widgets, delay_between=0.05, duration=0.25):
    """Animate widgets appearing one after another with a stagger delay."""
    for i, widget in enumerate(widgets):
        widget.opacity = 0
        delay = i * delay_between
        from kivy.clock import Clock
        Clock.schedule_once(
            lambda dt, w=widget: Animation(
                opacity=1.0, duration=duration, t='out_quad'
            ).start(w),
            delay
        )
