# Squad Fit — Project Notes & Build Playbook

*Compiled from the full chat history (Aug 6 → Aug 12) and the git history.
This is a reference doc — it changes nothing in the app.*

---

## 1. What Squad Fit is

A mobile-first, hands-free gym tracker built over one week with **Python 3.10 + Kivy/KivyMD**
(dark theme, neon-green accents), with **Supabase** for auth + cloud sync so friends can
share workouts, see PRs, and use a leaderboard. Target: Android (Pixel 8a).

Key architecture files: `main.py` (app + screen manager), `calendar_view.*`, `workout_view.*`,
`progress_view.*`, `ai_coach_view.*` + `ai_coach.py`, `template_view.py` (Program Lab),
`exercise_db.py`, `exercise_selection_view.py`, `database_sync.py` (Supabase),
`config.py` (Supabase creds), `stretch_view.py` (cool-down), `theme_manager.py`,
`plan_regenerator.py`, `splash_screen.*`, `login_view.*`, `onboarding_view.*`.

---

## 2. What's built (v1 feature inventory)

- **AI Coach** — weekly plan generation from goal/equipment, muscle-recovery %, reps-based
  progressive overload, exercise swap.
- **Program Lab** (was "My Routines") — save/load/assign routines to calendar days;
  "Program Library" popup with "Select a routine".
- **Calendar** — 7-day strip, day cards, green completion dots (mode-aware: AI vs My Program),
  defaults to today, allows doing any day's workout on any day.
- **Workout console** — timer, rest timer with vibration, supersets (A1/A2), exercise
  search/swap, "last time" indicator, **reps-only logging** (weights removed by decision).
- **Progress/Stats** — line charts per exercise, PRs, weekly volume, calendar heatmap,
  CSV export. *(Fixed Aug 12: now reloads data on screen entry.)*
- **Extras** — edit past workouts, post-workout cool-down/stretch timer, factory reset with
  backup, starter templates, theme (Charcoal/Navy), Supabase auth.

---

## 3. Key decisions & philosophy

- **Reps-only tracking** — weights/kgs removed to keep logging frictionless; weight code
  parked in `v2_vault/weight_tracking.py`.

### The "reps over weight" philosophy (explicit — Aug 13)

Squad Fit is **volume-first**: the currency of progress is reps + sets, not load.
This is a deliberate, evidence-backed choice, not an omission.

- **Why:** hypertrophy science (Renaissance Periodization / Israetel school) programmes by
  *weekly sets per muscle group* — that's what the AI Coach volume tracker targets are
  (Chest 16, Back 18, Legs 16, Shoulders 14, Biceps 10, Triceps 10, Core 8). Under this
  model, load is just a tool to make a set hard; what matters is enough sets close to failure.
- **What the app records:** each set logs **reps only**; the "PR" is *best total reps*
  across all sets in a session; weekly volume = total sets per muscle. There is no weight
  field on the set row.
- **Known gap (accepted for v1):** without a recorded load, the app cannot express
  progressive overload by weight, and it can't distinguish strength / hypertrophy /
  endurance rep ranges (1–5 / 6–12 / 15+ — everything defaults to ~10). "Heavier with
  fewer reps" (the strength rep range) is therefore not representable today.
- **How strength fits in later (3 options, in order of preference):**
  1. **B-lite (chosen direction)** — optional weight field per set + Epley-estimated 1RM
     (`weight × (1 + reps/30)`) so a real strength PR exists without forcing weight entry.
  2. **Goal-tagged rep ranges** — each exercise or profile declares strength/hypertrophy/
     endurance, defaulting reps to 5 / 10 / 15.
  3. Stay pure volume-first and own it (hypertrophy only, no 1RM).
- **Elevator answer:** "We track weekly sets per muscle — that's the hypertrophy variable.
  Weight is a v2 add-on."
- **Keep it lean** — deliberate move: don't add features that hinder the core purpose.
  Unused features parked in `v2_parked/` / `v2_vault/` and excluded from the APK
  (`source.exclude_dirs` in buildozer.spec).
- AI Coach and Program Lab live in their own section ("Training Hub" via flask icon);
  the cog is settings/profile only.
- Factory reset is more generous than most apps (they don't offer it) — with backup.

---

## 4. Parked → v2 / future ideas

**Already parked in the repo** (excluded from APK builds):
- `v2_parked/`: app_engine, body-map muscle view, data_models, milestone engine + dialog,
  spacing/theme/typography modules, weekly-schedule manager (multi-week profiles), workout_ui.kv
- `v2_vault/`: settings_view, superset_support (supersets were later added in v1), weight_tracking

**Discussed for the future (not built):**
- Body measurements tracking
- Video demo library — **superseded Aug 13 by the stick-figure approach** (see §8): zero-cost,
  consistent, on-brand exercise demos drawn procedurally instead of licensed/filmed video
- Social/community expansion (Supabase leaderboards exist; deeper social parked)
- Wearable sync — Samsung Watch / Garmin; Terra API or Health Connect bridge; Strava
- Plyometrics section (not for v1)
- Huge 10,000+ exercise libraries — user considers this overkill; machine/equipment library
  was a favourite idea ("commercial gym machines is a winner")
- PR badges / streaks polish

---

## 5. Local development

```bash
# run the app (from Git Bash)
cd /c/Temp/Buffswos/SquadFit && /c/Temp/Buffswos/.venv/Scripts/python.exe main.py
```

- Local venv uses **Kivy 2.3.1 / KivyMD 2.0.0** — note the APK pins *older* versions (below).
- Smoke test: `py main.py --smoke-test`
- App data lives in local JSON files at the project root (workout_completions.json, etc.);
  these are gitignored.

---

## 6. Android build playbook — what worked (the long road, Aug 11)

The APK build is a **manual GitHub Actions workflow** (`workflow_dispatch` only — it does NOT
auto-build on push). Sequence each time:
1. Commit changes locally
2. `git push origin main`
3. GitHub → repo → **Actions** → **Build APK** → **Run workflow** (branch `main`)
4. Wait ~1–2 hrs; download the **squadfit-apk** artifact (retention 30 days) and install on phone.

### The working recipe (verified, do NOT change)

**`buildozer.spec` (current, working):**
```ini
requirements = python3==3.10.11,hostpython3==3.10.11,kivy==2.2.0,kivymd==1.1.1
android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a          # not armeabi-v7a (Pixel 8a needs 64-bit)
fullscreen = 1                     # NOT fullscreen=auto (unsupported in buildozer 1.5.0)
p4a.bootstrap = sdl2
presplash_color = #121212
icon.filename = assets/icon.png    # icon.mode = crop
source.exclude_dirs = ... v2_parked, supabase_schema ...
source.exclude_patterns = *.pyc, crash.log, user_*.json, workout_*.json ...
```

**Workflow `.github/workflows/build-apk.yml` (current, working):**
- `runs-on: ubuntu-22.04`, `timeout-minutes: 120`
- `JAVA_HOME=/usr/lib/jvm/temurin-17-jdk-amd64` (Gradle **requires Java 17**; system Java 11 broke it)
- Install system deps incl. `openjdk-17-jdk`, `libtinfo-dev`, `cmake`, `libffi-dev`, etc.
- **Force system Python to 3.10** (symlink swap `/usr/bin/python3 -> python3.10`) — p4a demands
  hostpython3 and python3 match
- `pip install cython==0.29.37` then `buildozer==1.5.0`
- `buildozer -v android debug` → upload `./bin/*.apk` as artifact (actions/upload-artifact@v4)

### Lessons learned (each one cost a build)

1. **Python version matching is the #1 gotcha.** Error `python3 should have same version as
   hostpython3, 3.10.12 != 3.14.2`. Fix: pin BOTH `python3==3.10.11` and `hostpython3==3.10.11`
   in requirements, and force the runner's system python to 3.10.
2. **Avoid Python 3.14 on the runner.** Cython/Tempita break (`ModuleNotFoundError: cgi` —
   removed in 3.13+). Use ubuntu-22.04's 3.10.
3. **Cython must be pinned to 0.29.37** for buildozer 1.5.0 (3.0.11 broke on 3.14; don't put
   Cython in the app requirements — install it in the workflow instead).
4. **Don't use the Docker buildozer-action** (`ArtemSBulgakov/buildozer-action`) — its Dockerfile
   pulls the dead `openjdk-r/ppa` and apt fails (`'resolute Release' does not have a Release file`).
   The plain ubuntu-22.04 workflow above works.
5. **Kivy 2.3.1 / KivyMD 2.0.0 are NOT available for the Android toolchain** (errors like
   "Could not find a version that satisfies kivy==2.3.1"). Pin **kivy==2.2.0, kivymd==1.1.1**
   in buildozer.spec — this combo builds. (Desktop dev uses 2.3.1/2.0.0 — a known difference.)
6. **JAVA_HOME must be Java 17** (Gradle: "Android Gradle plugin requires Java 17... using Java 11").
7. **fullscreen=auto is unsupported** by buildozer 1.5.0 — use `fullscreen = 1`.
8. **arm64-v8a only** for modern phones (armeabi-v7a builds wasted hours; Pixel 8a needs 64-bit).
9. Remove **cryptography / bcrypt** from requirements — compiled C-extensions that p4a can't
   easily build (Gemini's catch saved a lot of time). Supabase auth still works without them.
10. GitHub caches can serve stale broken states — occasionally replace/recreate the workflow
    file ("Replace build workflow with new file to clear GitHub cache").
11. Node 20 deprecation warnings in Actions are harmless.
12. The `source.exclude_*` entries keep parked folders and local data files out of the APK.

### Build troubleshooting checklist (next time)

| Symptom | Fix |
|---|---|
| `python3 should have same version as hostpython3` | pin both to 3.10.11 + force runner python 3.10 |
| `No module named 'cgi'` / Cython Tempita errors | use ubuntu-22.04 + cython==0.29.37 |
| `kivy==2.3.1 (from versions: none)` | pin kivy==2.2.0, kivymd==1.1.1 |
| Gradle "requires Java 17" | set JAVA_HOME to temurin-17-jdk-amd64 |
| Docker `apt update` / PPA failures | use the plain workflow, not the Docker action |
| `fullscreen=auto` config error | set `fullscreen = 1` |
| Installs but instantly closes on phone | check `com.squadfit` crash log / logcat; ensure arm64-v8a |

---

## 7. Last session's changes (Aug 12, commit 8dddd2e)

- Progress/Stats page now reloads workout data every time it's opened (was loading once at startup)
- New app icon from the user's JPEG → launcher icon, in-app splash, and presplash
  (old presplash backed up as `assets/presplash.original.png`)
- Settings cog switched from a PNG image to an `MDIconButton` material "cog" icon — identical
  widget/positioning to the flask/chart header icons, so it sits perfectly level
- Various label/text polish from the "niggles" list

---

## 8. Aug 13 session

### Committed (`1aeac1d`) — snag-list fixes
- Factory-reset popup taller (380dp) so the black background covers the title
- Weekly volume now counts Monday workouts (week start was "now", not Monday 00:00)
- Removed the duplicate grey recovery `reasoning` text under the `Train:` line (AI Coach)
- PR cards: wrap long exercise names; PR date now **DD/MM/YYYY** (UK)
- Workout sheet resets scroll to the first exercise on every load
- Centred UPDATE/KEEP text in the plan-regeneration dialog
- Rest-timer vibration fixed — old `mActivity.vibrate()` was a silent no-op (Android `Activity`
  has no `vibrate`). Now uses the `Vibrator` service + `VibrationEffect`
  (see `_android_vibrate` in `workout_view.py`).

### Uncommitted (pending a commit — includes local test data, do NOT commit `day_routines.json`)
- **Exercise DB 111 → 151** (`exercise_db.py`): +12 kettlebell (`kb01`–`kb12`), +12 bands
  (`bd01`–`bd12`), +16 bodyweight (`bw01`–`bw16`). Deduped "Romanian Deadlift"/"Dumbbell
  Romanian Deadlift" (the Back variants became **Snatch-Grip Deadlift** / **Dumbbell Deadlift**),
  fixing the name collision that made the starter routine's "Romanian Deadlift" resolve to the
  Back variant. New compounds added to `COMPOUND_MUSCLE_MAP` in `ai_coach.py`.
- `login_view.kv`: darker input fields, neon cursor, brighter labels (visibility/contrast).
- `workout_view.py`: completed set button shows a green **✓** instead of "DONE".

### Stick-figure exercise demos — the chosen direction (no spend)
Decided against licensed videos / filming / 3D. Instead: a **procedurally-drawn 2D side-view
stick figure**, neon-green working limbs, paired with the existing text form tips.
"Simple, informative, zero cost" — agreed benchmark design.

**Prototype files (both standalone, zero app imports):**
- `stickman_demo.py` — Kivy window; run `python stickman_demo.py`
- `stickman_preview.html` — HTML-canvas port (registered in the Preview tab)

**How the animation works (reuse this):**
- 2D **side view**, figure faces right (+x); units are body-scale (standing height ≈ 1.65).
- Legs via **two-circle knee kinematics**: `solve_knee(hip, ankle, L1, L2)` = intersection of a
  thigh circle and a shin circle, pick the forward (+x) solution. Hip driven by a squat-depth
  param (0=stand → 1=bottom); ankle fixed.
- Torso = hip→shoulder with forward lean ∝ depth; head above; one near arm
  (shoulder→elbow→hand) gripping the bar.
- **Barbell = the near plate only** (side view shows the end, not the full bar): lighter steel
  fill + thin outline ring + light sleeve.
- Constants: torso 0.48, thigh 0.46, shin 0.46, head r 0.13, HIP_STAND 0.90, HIP_DROP 0.38,
  HIP_BACK 0.10, LEAN_MAX 0.30 rad, ANKLE (0.0, **0.04** — above the foot line), cycle 2.6 s.
- Colours: NEON `(0.75,1.00,0.15)` legs · DIM `(0.45,0.48,0.55)` body · BAR `(0.85,0.85,0.90)`
  sleeve · PLATE `(0.60,0.62,0.68)` plate.
- **Gotcha (HTML port):** canvas y grows DOWNWARD, so `Y(y) = gy - y*scale`; Kivy grows up and
  uses `+`. Getting this wrong renders the figure upside down.

**Archetype engine (built Aug 13, in `stickman_preview.html`):**
- Rewrote the preview as a **data-driven rig**: shared `kneeIK`/`elbowIK` (two-circle IK),
  `shoulderAt` (hip + torso lean), `headAt`, plus a generic `drawFigure(pose)` that maps a
  `highlight` tag to neon colours (legs / arms / torso / full) and renders equipment props
  (barbell plate, dumbbell, kettlebell, cable line, bodyweight none).
- Each archetype is a small `pose(ph)` (phase 0..1) returning {ankle,knee,hip,shoulder,head,
  elbow,hand,plate,equipment,highlight,root}. **Root types:** `standing` (ground + foot),
  `lying` (bench rect under the body), `seated` (seat box under the hip), `plank` (toes on
  floor), `floor` (flat, no bench).
- **22 archetypes live** (UI = 22 pill buttons): squat, hinge/deadlift, bench press, overhead
  press, bent-over row, lat pulldown, bicep curl, tricep extension, leg raise, plank (hold),
  lateral raise, farmer's carry, cycling (road bike), calf raise, crunch, push-up, glute
  bridge, kettlebell swing, leg extension, leg curl, seated cable row, rowing machine.
- Verified: all 12 render (green highlight + grey body pixels present), no console errors,
  every figure inside the canvas bounds. Note: side-view simplification for lateral raise;
  plank/leg-raise use `floor`/`plank` roots.
- **Polish (same day):** overhead press, lateral raise and farmer's carry are now **front
  view** (two straight legs + both arms) rather than side view. Overhead press drives the
  elbow by a monotonic angle (160°→24°) and solves the forearm so the hand stays on a
  fixed-grip horizontal bar — this removed the IK elbow-flip at the bottom. Farmer's carry
  walks with a real gait: one foot planted while the other swings (sine pulse, never both
  in the air), and the foot **pivots heel→flat→toe-off** (`footAng()`: quick heel plant,
  flat pause, toe push). `footAng`/`footAng2` fields rotate the foot in `drawFigure`; other
  archetypes omit them → flat foot. Far limbs stay dimmed as a depth cue.
- **Aug 14 additions:** farmer's carry is now a true **side-view walk cycle** (contact → down
  → passing → up) that **travels left→right and screen-wraps** off the right edge back to the
  left; the body advances `2×stride`/cycle while the planted foot travels back `stride`, so
  the foot stays glued to the floor (no slide) — see `BIOMECHANICS_NOTES.md` §5. Added a
  **Cycling (road bike)** archetype: seated root, legs pedal a rotating crank (`kneeIK` from
  hip to the two pedals 180° apart, clockwise), two spinning wheels (single spoke each, at 2× crank
  speed) + a diamond frame (chain stay, down tube, seat tube, top tube, fork, seat stay),
  drop handlebars and saddle, rider in an aero tuck (`lean 0.85`) — drawn in `drawBike()`.
  Pedals at `hip[-0.18,0.88]` / `BB[0.02,0.20]` R0.12, wheels r0.22 at `[-0.32,0.22]` /
  `[0.32,0.22]`. (First version was a spin bike with a flywheel; swapped to a road bike per
  user reference.)
- **Aug 14:** road-bike **diamond frame is temporarily commented out** in `drawBike()` (the 6
  tube `seg()` calls) so the rider/wheels/bars read cleaner — uncomment those lines to
  restore the full frame. Handlebar (stem + drop), saddle, crank + pedals kept.
- **Aug 14 batch 2 (5 easy archetypes, all reuse existing roots/props):** calf raise (standing
  heel-lift + `footAng` toes-down), crunch (`floor` root, torso curls via `a=0.85·osc`, fixed
  bent legs with feet on the far side of the hip, arms crossed on chest), push-up (`plank` root,
  straight body pivots around planted
  toes while `elbowIK` bends, elbow `forward=false`), glute bridge (`floor`, hip thrusts up via
  `a=1.1·osc` + `kneeIK` leg), kettlebell swing (hinge + straight-arm swing, arm angle
  `-0.5→1.3` rad). These close most of the earlier "stragglers" list (calf raise, core
  flexion, push-up family, hip thrust, kb swing).
- **Aug 14 batch 3 (4 machine archetypes):** leg extension (seated, knee pivot + shin swings
  down→forward, back pad + rotating pad arm + weight stack), leg curl (lying/prone, heel curls
  up toward the glutes), seated cable row (seated, foot plate + cable pulled to the abdomen),
  rowing machine (sliding seat + leg drive where the knee blends bent→straight via
  `kneeIK → on-line knee` lerp, chain to a flywheel). Added a shared **`drawMachine()`** prop
  (seat/back pad, foot plate, rotating pad arm, weight stack + support post, rowing rail +
  flywheel, chain). These close the leg-isolation stragglers (leg extension/curl) and the
  rowing cardio slot.

**Archetype → exercise mapping (done Aug 13):**
Keyword classifier over all 151 names (fallback: muscle group). Result — the **12 core
patterns + cardio cover ~139/151 (92%)**, and a small set of extras closes the gap:

| Archetype | Count | Archetype | Count |
|---|---|---|---|
| push_h (bench/push-up/fly) | 27 | tricep | 7 |
| cardio (run/bike/row/swim…) | 17 | squat | 13 |
| hinge (deadlift/RDL/hip thrust) | 15 | push_v (overhead press) | 10 |
| pull_h (row/reverse fly) | 14 | core_flex / core_hold | 8 + 8 |
| pull_v (pulldown/pull-up) | 8 | curl | 8 |
| lateral / front_raise | 3 + 1 | carry | 1 |

**Remaining stragglers after batch 3 (5 exercises):** hip abduction/adduction ×2, Turkish
get-up ×1, kettlebell halo ×1, kettlebell windmill ×1. Calf raise, leg extension/curl and
rowing are now built, so ~22 patterns cover ≈97% — the core bet holds (12 patterns ≈ 92%).

**Next steps (in order):**
1. Add a real `archetype` field to each `exercise_db.py` entry (turn the keyword heuristic
   into explicit data) so the app can look up a demo by exercise id.
2. Convert `pose(ph)` functions into **pure key-pose data** (joint angles per key frame) +
   a shared lerp/forward-kinematics driver, so authoring is fully declarative.
3. Port the rig into a **Kivy `StickmanWidget`** (`stickman/` package) and drop it into the
   exercise cards (single import + one widget instance — stays isolated from app logic).
