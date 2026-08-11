# theme_manager.py - Simplified (background only, fixed green accent)
import json
import os
from kivy.animation import Animation
from kivy.clock import Clock

# Background color configurations
BACKGROUND_CONFIGS = {
    "charcoal": {
        "name": "Deep Charcoal",
        "canvas_bg": [0.07, 0.07, 0.07, 1],       # #121212
        "card_bg": [0.12, 0.12, 0.12, 0.80],      # #1E1E1E @ 80% glassmorphism
        "card_bg_light": [0.18, 0.18, 0.18, 0.80], # #2E2E2E @ 80%
        "input_bg": [0.15, 0.15, 0.15, 0.75],     # #262626 @ 75%
    },
    "navy": {
        "name": "Deep Navy",
        "canvas_bg": [0.04, 0.07, 0.17, 1],       # #0B132B
        "card_bg": [0.11, 0.15, 0.25, 0.80],      # #1C2541 @ 80% glassmorphism
        "card_bg_light": [0.15, 0.20, 0.32, 0.80], # #263452 @ 80%
        "input_bg": [0.13, 0.18, 0.30, 0.75],     # #21304D @ 75%
    },
}

# Fixed accent color - the original neon green
ACCENT_COLOR = [0.2, 1.0, 0.6, 1]  # #33FF99 - Original bright green
ACCENT_DIM = [0.1, 0.5, 0.3, 1]


class ThemeManager:
    """Simple theme manager - background switching only."""

    def __init__(self, app=None):
        self.app = app
        self.current_bg = "charcoal"
        self._load_saved_theme()
        self._apply_theme()

    def _load_saved_theme(self):
        try:
            if os.path.exists("theme_settings.json"):
                with open("theme_settings.json", "r") as f:
                    saved = json.load(f)
                self.current_bg = saved.get("background", "charcoal")
        except Exception as e:
            print(f"[ThemeManager] Could not load saved theme: {e}")

    def _save_theme(self):
        try:
            with open("theme_settings.json", "w") as f:
                json.dump({"background": self.current_bg}, f, indent=2)
        except Exception as e:
            print(f"[ThemeManager] Could not save theme: {e}")

    def _apply_theme(self, animate=True):
        if not self.app:
            return

        bg = BACKGROUND_CONFIGS.get(self.current_bg, BACKGROUND_CONFIGS["charcoal"])

        if animate and hasattr(self.app, 'sm'):
            # Smooth fade transition: dim → apply new theme → brighten
            self._smooth_transition(bg)
        else:
            # Instant apply (no animation)
            self._apply_colors(bg)

        self._save_theme()
        print(f"[ThemeManager] Applied: {bg['name']}")

    def _smooth_transition(self, target_bg):
        """Fade out slightly, apply new theme, fade back in."""
        sm = self.app.sm
        if not sm or not sm.current_screen:
            self._apply_colors(target_bg)
            return

        screen = sm.current_screen

        # Phase 1: Fade out (0.15s)
        anim_out = Animation(opacity=0.7, duration=0.15, t='in_quad')

        def _apply_mid(*args):
            # Apply new colors at the dimmest point
            self._apply_colors(target_bg)

        def _fade_in(*args):
            # Phase 2: Fade back in (0.2s)
            Animation(opacity=1.0, duration=0.2, t='out_quad').start(screen)

        anim_out.bind(on_complete=_apply_mid)
        _apply_mid()  # Apply immediately, then animate
        Clock.schedule_once(lambda dt: Animation(opacity=1.0, duration=0.2, t='out_quad').start(screen), 0.15)

    def _apply_colors(self, bg):
        """Apply color values to the app."""
        if hasattr(self.app, 'canvas_bg'):
            self.app.canvas_bg = bg["canvas_bg"]
        if hasattr(self.app, 'card_bg'):
            self.app.card_bg = bg["card_bg"]
        if hasattr(self.app, 'card_bg_light'):
            self.app.card_bg_light = bg["card_bg_light"]
        if hasattr(self.app, 'input_bg'):
            self.app.input_bg = bg["input_bg"]
        if hasattr(self.app, 'accent_color'):
            self.app.accent_color = ACCENT_COLOR
        if hasattr(self.app, 'accent_color_dim'):
            self.app.accent_color_dim = ACCENT_DIM

    def set_background(self, bg_key):
        if bg_key in BACKGROUND_CONFIGS:
            self.current_bg = bg_key
            self._apply_theme()

    def get_bg_color(self, variant="canvas"):
        bg = BACKGROUND_CONFIGS.get(self.current_bg, BACKGROUND_CONFIGS["charcoal"])
        if variant == "card":
            return bg["card_bg"]
        elif variant == "card_light":
            return bg["card_bg_light"]
        elif variant == "input":
            return bg["input_bg"]
        return bg["canvas_bg"]
