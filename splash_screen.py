"""
splash_screen.py — Professional splash screen with animated loading dots
Shows on app launch for ~2.5 seconds before transitioning to main app.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp


class SplashScreen(BoxLayout):
    """
    Splash screen displayed on app startup.
    Animates three pulsing dots while the app loads.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._animation_event = None

    def on_kv_post(self, dt=None):
        """Start the dot animation after the layout is built."""
        Clock.schedule_once(self._start_animation, 0.1)

    def _start_animation(self, dt=None):
        """Begin the pulsing dot animation sequence."""
        self._animate_dots()

    def _animate_dots(self):
        """Create a pulsing animation for the three loading dots."""
        try:
            dot1 = self.ids.dot1
            dot2 = self.ids.dot2
            dot3 = self.ids.dot3
        except AttributeError:
            return

        # Reset all dots
        dot1.opacity = 0.2
        dot2.opacity = 0.2
        dot3.opacity = 0.2

        # Staggered pulse animation
        delay = 0.3
        duration = 0.4

        # Dot 1 pulses first
        anim1 = Animation(opacity=1.0, duration=duration, t='in_out_sine') + \
                Animation(opacity=0.2, duration=duration, t='in_out_sine')

        # Dot 2 pulses after delay
        anim2 = Animation(opacity=0.2, duration=delay) + \
                Animation(opacity=1.0, duration=duration, t='in_out_sine') + \
                Animation(opacity=0.2, duration=duration, t='in_out_sine')

        # Dot 3 pulses after 2x delay
        anim3 = Animation(opacity=0.2, duration=delay * 2) + \
                Animation(opacity=1.0, duration=duration, t='in_out_sine') + \
                Animation(opacity=0.2, duration=duration, t='in_out_sine')

        # Chain: after all three pulse, repeat
        total_duration = delay * 2 + duration * 3

        def _repeat(*args):
            Clock.schedule_once(lambda dt: self._animate_dots(), 0.2)

        anim3.bind(on_complete=_repeat)

        anim1.start(dot1)
        anim2.start(dot2)
        anim3.start(dot3)

    def stop_animation(self):
        """Stop all animations before transitioning."""
        if self._animation_event:
            self._animation_event.cancel()
        try:
            Animation.cancel_all(self.ids.dot1)
            Animation.cancel_all(self.ids.dot2)
            Animation.cancel_all(self.ids.dot3)
        except AttributeError:
            pass
