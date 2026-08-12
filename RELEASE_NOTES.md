# SquadFit — Release Notes (next APK)

Built by **Andy** 🏋️ — build from commit `c85cbad` on `main`.

## Eight fixes in this build

1. **Plan dialog polish** (onboarding) — "* Goal / * Equipment" summary text reduced to the same size as the text below it so it no longer wraps; buttons shortened to **UPDATE** and **KEEP** so the labels fit.

2. **AI Coach de-duplication** — removed the repeated **MUSCLE RECOVERY STATUS** rows (grey text + bars) that duplicated the "Train: …" percentages. The dashboard now shows each muscle percentage once, in the bigger, clearer format.

3. **Progress tab icons** — the selected tab's icon is now bright green on the dark background (grey when inactive). No more black icons vanishing when tapped, including the cup and calendar tabs.

4. **Charts "no data" message** — "No exercise data yet. Complete workouts to see progress charts!" now wraps and centers instead of spilling off the left edge.

5. **PRs "no data" message** — "No personal records yet. Complete workouts to start tracking PRs!" now wraps and centers properly too.

6. **Routine list scroll reset** — selecting My Program (or switching days/modes) now starts the workout list at the top instead of halfway down a long routine.

7. **Save-program popup** — heading renamed to **SAVE**, field label renamed to **Program Name**, and the preview line is now the fixed **"Saving custom routine"** instead of an over-long "Saving 13 exercises from: …" that overflowed the window.

8. **Weekly volume card** — the **WEEKLY VOLUME TRACKER** title is no longer clipped at the top; the card now sizes itself to fit all seven muscle rows.

## Also in this build (from the previous commit)

- **Stats page fix** — Progress reloads your workout data every time you open it (previously built once at startup and could show empty).
- **New app icon** — your uploaded image is now the launcher icon, in-app loading screen, and presplash.
- **Cog icon** — the settings cog is now a material icon button, perfectly level with the flask and chart icons.

## How to build

1. `git push origin main` (already done — `main` is at `c85cbad`)
2. GitHub → **Actions** → **Build APK** → **Run workflow**
3. Download the **squadfit-apk** artifact, install on the Pixel 8a.

---

*Made with 💚 by Andy*
