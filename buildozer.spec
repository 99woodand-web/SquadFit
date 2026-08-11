# ============================================================
#          SQUAD FIT - Android Build Configuration
# ============================================================

[app]

# -- App Identity -------------------------------------------
title = Squad Fit
package.name = squadfit
package.domain = com.squadfit

# -- Source -------------------------------------------------
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,ttf,txt,json

# -- Version ------------------------------------------------
version = 0.1.0

# -- Requirements -------------------------------------------
# DO NOT pin Cython here — it conflicts with the target Python.
# p4a manages Cython internally via its host build toolchain.
# Kivy 2.2.0 is the last version with reliable Android wheels.
requirements = python3==3.10.12,kivy==2.2.0,kivymd==1.1.1

# -- Android Configuration ----------------------------------
android.permissions = INTERNET, VIBRATE, ACCESS_NETWORK_STATE
android.api = 31
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = armeabi-v7a
android.release_artifact = apk

# -- Orientation --------------------------------------------
orientation = portrait

# -- Window -------------------------------------------------
fullscreen = auto
android.window_soft_input_mode = adjustResize

# -- Build Options ------------------------------------------
android.enable_androidx = True
p4a.bootstrap = sdl2

# -- Presplash ----------------------------------------------
presplash_color = #121212

# -- Log Level ----------------------------------------------
log_level = 2

# -- Source Exclusions (keep build clean) -------------------
source.exclude_dirs = tests, bin, .git, .freebuff, .venv, __pycache__, v2_parked, supabase_schema
source.exclude_patterns = *.pyc,*.pyo,IMPROVEMENT*,*.backup*,crash.log,user_*.json,login_state.json,workout_*.json,weekly_*.json,theme_*.json,calendar_data.json
