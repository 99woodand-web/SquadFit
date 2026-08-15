# main.py - Squad Fit App with KivyMD + ThemeManager
import os
import sys
import traceback
import platform

_is_android = platform.system() == 'Linux' and os.path.exists('/system')

# ===================================================================
# ULTRA-ROBUST CRASH HANDLING
# Catches EVERY error and shows it on screen AND in a file
# ===================================================================
_crash_messages = []  # Store errors in memory so we can display them

# Try multiple locations for crash log
_crash_log = None
for _path in ['/sdcard/squadfit_crash.log', '/sdcard/Download/squadfit_crash.log', '/tmp/crash.log']:
    try:
        with open(_path, 'w') as f:
            f.write('')
        _crash_log = _path
        break
    except:
        pass
if not _crash_log:
    try:
        _crash_log = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crash.log')
    except:
        _crash_log = '/tmp/crash.log'

def _log_crash(msg):
    _crash_messages.append(msg)
    try:
        with open(_crash_log, 'a') as f:
            f.write(f"{msg}\n")
    except:
        pass
    # Also print to console
    try:
        print(msg)
    except:
        pass

# Catch ALL unhandled Python exceptions
_original_excepthook = sys.excepthook
def _crash_handler(exc_type, exc_value, exc_tb):
    tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
    _log_crash(f"\nUNHANDLED EXCEPTION:\n{tb_str}")
    # Try to show error on screen
    try:
        _show_error_on_screen(str(exc_value), tb_str)
    except:
        pass
    _original_excepthook(exc_type, exc_value, exc_tb)
sys.excepthook = _crash_handler

def _show_error_on_screen(error_msg, full_trace=''):
    """Show error popup on screen so user can see it even if file logging fails."""
    try:
        from kivy.core.window import Window
        from kivy.uix.label import Label
        from kivy.uix.popup import Popup
        from kivy.uix.scrollview import ScrollView
        truncated = full_trace[:1500] if full_trace else error_msg
        popup = Popup(
            title='APP CRASHED - Error Details',
            content=ScrollView(
                content=Label(text=truncated, font_size='11sp',
                    size_hint_y=None, text_size=(350, None),
                    halign='left', valign='top',
                    color=(1,0.4,0.4,1))
            ),
            size_hint=(0.95, 0.8),
            background_color=(0.1,0.1,0.1,0.95)
        )
        popup.open()
    except:
        pass

_log_crash(f"\n{'='*50}")
_log_crash(f"App starting at {__file__}")
_log_crash(f"Crash log location: {_crash_log}")

# Only set window size on desktop, NOT on Android
if not _is_android:
    try:
        from kivy.core.window import Window
        Window.size = (380, 740)
        _log_crash("Desktop mode: Window.size set to 380x740")
    except Exception as e:
        _log_crash(f"Window size error: {e}")

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, CardTransition
from kivy.lang import Builder
from kivy.properties import ListProperty

# Load all KV files BEFORE importing view classes
_kv_files = [
    "splash_screen.kv",
    "login_view.kv",
    "onboarding_view.kv",
    "calendar_view.kv",
    "workout_view.kv",
    "exercise_selection_view.kv",
    "progress_view.kv",
    "ai_coach_view.kv",
]
for kv_file in _kv_files:
    kv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), kv_file)
    if os.path.exists(kv_path):
        try:
            Builder.load_file(kv_path)
            _log_crash(f"Loaded KV: {kv_file}")
        except Exception as e:
            _log_crash(f"FAILED to load KV {kv_file}: {e}")
    else:
        _log_crash(f"KV file not found: {kv_file}")

# Import views AFTER loading KV
try:
    from login_view import LoginScreenView
    _log_crash("Imported: LoginScreenView")
except Exception as e:
    _log_crash(f"FAILED import LoginScreenView: {e}")
    raise

try:
    from onboarding_view import OnboardingScreen
    _log_crash("Imported: OnboardingScreen")
except Exception as e:
    _log_crash(f"FAILED import OnboardingScreen: {e}")
    raise

try:
    from calendar_view import CalendarViewScreen
    _log_crash("Imported: CalendarViewScreen")
except Exception as e:
    _log_crash(f"FAILED import CalendarViewScreen: {e}")
    raise

try:
    from workout_view import WorkoutConsoleScreen
    _log_crash("Imported: WorkoutConsoleScreen")
except Exception as e:
    _log_crash(f"FAILED import WorkoutConsoleScreen: {e}")
    raise

try:
    from exercise_selection_view import ExerciseSelectionScreen
    _log_crash("Imported: ExerciseSelectionScreen")
except Exception as e:
    _log_crash(f"FAILED import ExerciseSelectionScreen: {e}")
    raise

try:
    from progress_view import ProgressScreen
    _log_crash("Imported: ProgressScreen")
except Exception as e:
    _log_crash(f"FAILED import ProgressScreen: {e}")
    raise

try:
    from ai_coach_view import AICoachScreen
    from stretch_view import StretchView
    _log_crash("Imported: AICoachScreen + StretchView")
except Exception as e:
    _log_crash(f"FAILED import AICoachScreen: {e}")
    raise

try:
    from exercise_library_view import ExerciseLibraryScreen
    _log_crash("Imported: ExerciseLibraryScreen")
except Exception as e:
    _log_crash(f"FAILED import ExerciseLibraryScreen: {e}")
    raise

try:
    from theme_manager import ThemeManager
    _log_crash("Imported: ThemeManager")
except Exception as e:
    _log_crash(f"FAILED import ThemeManager: {e}")
    raise

try:
    from splash_screen import SplashScreen
    _log_crash("Imported: SplashScreen")
except Exception as e:
    _log_crash(f"FAILED import SplashScreen: {e}")
    raise

_log_crash("All imports successful!")

class SplashScreenWrapper(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(SplashScreen())

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(LoginScreenView())

class OnboardingScreenWrapper(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(OnboardingScreen())

class CalendarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(CalendarViewScreen())

class WorkoutScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(WorkoutConsoleScreen())

class ExerciseSelectionScreenWrapper(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(ExerciseSelectionScreen())

class ProgressScreenWrapper(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(ProgressScreen())

    def on_pre_enter(self):
        """Refresh stats every time the user navigates here, so newly
        completed workouts always show up."""
        screen = self.children[0]
        if hasattr(screen, 'switch_tab'):
            screen.switch_tab(screen.current_tab)

class AICoachScreenWrapper(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._coach = AICoachScreen()
        self.add_widget(self._coach)

    def on_pre_enter(self):
        """Refresh the dashboard every time the user navigates here."""
        if hasattr(self._coach, '_build_dashboard'):
            self._coach._build_dashboard()

class SquadFitApp(MDApp):
    # Dynamic color properties - updated by ThemeManager
    canvas_bg = ListProperty([0.07, 0.07, 0.07, 1])
    card_bg = ListProperty([0.12, 0.12, 0.12, 1])
    card_bg_light = ListProperty([0.18, 0.18, 0.18, 1])
    input_bg = ListProperty([0.15, 0.15, 0.15, 1])
    accent_color = ListProperty([0.80, 1.00, 0.00, 1])
    accent_color_dim = ListProperty([0.40, 0.50, 0.00, 1])

    def build(self):
        _log_crash("SquadFitApp.build() called")
        self.title = "Squad Fit"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.primary_hue = "A700"

        # Initialize ThemeManager
        self.theme_manager = ThemeManager(app=self)

        self.sm = ScreenManager()
        self.sm.transition = SlideTransition(direction='left', duration=0.25)

        screens = [
            ("splash", SplashScreenWrapper),
            ("login", LoginScreen),
            ("onboarding", OnboardingScreenWrapper),
            ("calendar", CalendarScreen),
            ("workout", WorkoutScreen),
            ("exercises", ExerciseSelectionScreenWrapper),
            ("library", ExerciseLibraryScreen),
            ("progress", ProgressScreenWrapper),
            ("aicoach", AICoachScreenWrapper),
            ("stretch", StretchView),
        ]

        for name, screen_cls in screens:
            try:
                self.sm.add_widget(screen_cls(name=name))
                _log_crash(f"Screen added: {name}")
            except Exception as e:
                _log_crash(f"FAILED to add screen {name}: {e}")
                _log_crash(traceback.format_exc())
                # Show error on screen immediately
                try:
                    _show_error_on_screen(f"Error loading {name}: {e}", traceback.format_exc())
                except:
                    pass
                # Create a fallback error screen
                error_screen = Screen(name=name)
                from kivy.uix.label import Label
                error_screen.add_widget(Label(
                    text=f"Error loading {name}:\n{str(e)[:200]}",
                    font_size='12sp', halign='center',
                    color=(1, 0.4, 0.4, 1)
                ))
                self.sm.add_widget(error_screen)

        _log_crash("All screens added. Starting splash...")
        self.sm.current = "splash"
        from kivy.clock import Clock
        Clock.schedule_once(self._finish_splash, 2.5)
        return self.sm

    def _finish_splash(self, dt):
        """Transition from splash to the appropriate screen."""
        self.check_onboarding_status()

    def check_onboarding_status(self):
        import json

        if os.path.exists("login_state.json"):
            try:
                with open("login_state.json", "r") as f:
                    state = json.load(f)
                if state.get("logged_in"):
                    if os.path.exists("user_profile.json"):
                        with open("user_profile.json", "r") as f:
                            profile = json.load(f)
                        if profile.get("onboarding_complete"):
                            self.sm.current = "calendar"
                            return
                    self.sm.current = "onboarding"
                    return
            except:
                pass

        self.sm.current = "login"

    def logout(self):
        try:
            if os.path.exists("login_state.json"):
                os.remove("login_state.json")
        except:
            pass
        self.sm.current = "login"

if __name__ == "__main__":
    try:
        _log_crash("Starting SquadFitApp()...")
        SquadFitApp().run()
        _log_crash("App exited normally.")
    except Exception as e:
        _log_crash(f"FATAL CRASH: {e}")
        _log_crash(traceback.format_exc())
        raise
