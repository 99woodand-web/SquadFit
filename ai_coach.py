# ai_coach.py - AI Coaching Engine
# Muscle recovery tracking, plateau detection, deload suggestions,
# progressive overload recommendations, and daily workout generation.
#
# NO database modifications. NO breaking changes. Pure analysis layer.

import os
import json
from datetime import datetime, timedelta
from collections import defaultdict
from exercise_db import (
    get_all_exercises, get_exercises_by_muscle, get_exercises_by_equipment,
    WORKOUT_SPLITS, STRENGTH_EXERCISES, CARDIO_EXERCISES
)


# ═══════════════════════════════════════════════════════════════════════════════
#  MUSCLE RECOVERY MODEL
#  Each muscle group starts at 100% recovery and depletes when trained.
#  Recovery rate: ~30% per day for small muscles, ~25% for large compounds.
# ═══════════════════════════════════════════════════════════════════════════════

MUSCLE_GROUPS = ["Chest", "Back", "Legs", "Shoulders", "Biceps", "Triceps", "Core"]

# How much recovery is lost per set trained (rough sports science model)
DEPLETION_PER_SET = {
    "Chest": 2, "Back": 2, "Legs": 3, "Shoulders": 2,
    "Biceps": 1.5, "Triceps": 1.5, "Core": 1, "Cardio": 1
}

# Daily recovery rate (% per day since last trained)
RECOVERY_RATE_PER_DAY = {
    "Chest": 25, "Back": 25, "Legs": 22, "Shoulders": 28,
    "Biceps": 35, "Triceps": 35, "Core": 40, "Cardio": 50
}

# Compound exercises that fatigue multiple muscle groups
COMPOUND_MUSCLE_MAP = {
    "Flat Bench Press": ["Chest", "Triceps", "Shoulders"],
    "Incline Bench Press": ["Chest", "Triceps", "Shoulders"],
    "Barbell Back Squat": ["Legs", "Core"],
    "Romanian Deadlift": ["Legs", "Back"],
    "Barbell Bent-Over Row": ["Back", "Biceps"],
    "Military Press": ["Shoulders", "Triceps"],
    "Dumbbell Shoulder Press": ["Shoulders", "Triceps"],
    "Close-Grip Bench Press": ["Triceps", "Chest"],
    "Pull-Up": ["Back", "Biceps"],
    "Chin-Up": ["Back", "Biceps"],
    "Barbell Deadlift": ["Back", "Legs"],
    "Dumbbell Bulgarian Split Squat": ["Legs"],
    "Hip Thrust": ["Legs"],
    "Lat Pulldown": ["Back", "Biceps"],
    "Cable Seated Row": ["Back", "Biceps"],
    "Dumbbell Single-Arm Row": ["Back", "Biceps"],
    "Dumbbell Curl": ["Biceps"],
    "Hammer Curl": ["Biceps"],
    "Tricep Pushdown": ["Triceps"],
    "Skull Crusher": ["Triceps"],
    "Plank": ["Core"],
    "Hanging Leg Raise": ["Core"],
    "Bicycle Crunch": ["Core"],
    "Crunch": ["Core"],
}


# ═══════════════════════════════════════════════════════════════════════════════
#  FORM TIPS DATABASE
# ═══════════════════════════════════════════════════════════════════════════════

FORM_TIPS = {
    "Flat Bench Press": [
        "Retract shoulder blades and arch upper back slightly",
        "Keep feet flat on floor, drive through heels",
        "Lower bar to mid-chest, press in a slight arc",
        "Keep wrists straight, bar over forearms",
        "Breathe in on descent, exhale on press"
    ],
    "Incline Bench Press": [
        "Set bench to 30-45 degrees",
        "Press to upper chest, not straight up",
        "Control the eccentric - 2-3 seconds down",
        "Don't flare elbows past 75 degrees"
    ],
    "Barbell Back Squat": [
        "Break at hips first, then knees",
        "Knees track over toes, don't cave inward",
        "Chest up, brace core like someone will punch you",
        "Descend until hip crease is below knee (parallel minimum)",
        "Drive through midfoot, squeeze glutes at top"
    ],
    "Romanian Deadlift": [
        "Start from standing, push hips BACK",
        "Slight bend in knees, don't squat",
        "Feel the stretch in hamstrings, not lower back",
        "Bar stays close to legs throughout",
        "Only go as low as flexibility allows"
    ],
    "Barbell Bent-Over Row": [
        "Hinge forward 45 degrees, back flat",
        "Pull to lower chest/upper abdomen",
        "Squeeze shoulder blades at the top",
        "Don't use momentum - control the weight"
    ],
    "Military Press": [
        "Brace core hard before pressing",
        "Press straight up, head moves slightly forward",
        "Don't lean back excessively",
        "Full lockout at top"
    ],
    "Dumbbell Curl": [
        "Elbows pinned to sides throughout",
        "Supinate (twist) at the top for max contraction",
        "Control the negative - don't just drop",
        "Avoid swinging your body"
    ],
    "Hammer Curl": [
        "Neutral grip (palms facing each other)",
        "Targets the brachialis for thicker arms",
        "Keep elbows stationary"
    ],
    "Tricep Pushdown": [
        "Elbows locked at your sides",
        "Full lockout at the bottom, squeeze",
        "Control the return - don't let the weight pull you"
    ],
    "Plank": [
        "Body in a straight line from head to heels",
        "Squeeze glutes, brace abs like bracing for impact",
        "Don't let hips sag or pike up",
        "Breathe normally, don't hold your breath"
    ],
    "Hanging Leg Raise": [
        "Hang from bar with straight arms",
        "Curl pelvis up, don't just swing legs",
        "Control the descent - no swinging",
        "Bend knees if straight leg is too hard"
    ],
    "Dumbbell Bulgarian Split Squat": [
        "Rear foot elevated on bench",
        "Lean forward slightly for more glute emphasis",
        "Front knee tracks over toes",
        "Lower until back knee nearly touches floor"
    ],
    "Hip Thrust": [
        "Upper back on bench, feet flat",
        "Drive through heels, squeeze glutes HARD at top",
        "Chin tucked, don't hyperextend lower back",
        "Pause 1-2 seconds at the top"
    ],
    "Lat Pulldown": [
        "Pull to upper chest, not behind neck",
        "Lean back slightly (10-15 degrees)",
        "Lead with elbows, squeeze lats at bottom",
        "Control the negative - 2 seconds up"
    ],
    "Cable Face Pull": [
        "Pull to face level, external rotate at end",
        "Squeeze rear delts and mid-traps",
        "Keep elbows high"
    ],
    "Dumbbell Lateral Raise": [
        "Slight forward lean",
        "Raise to shoulder height, no higher",
        "Lead with elbows, not hands",
        "Control the negative"
    ],
    "Push-Up": [
        "Hands shoulder-width apart",
        "Full range - chest touches floor",
        "Core tight, body in straight line",
        "Don't flare elbows past 45 degrees"
    ],
    "Pull-Up": [
        "Full dead hang at bottom",
        "Pull chin OVER the bar",
        "Drive elbows down and back",
        "Control the descent"
    ],
    "Cable Fly": [
        "Slight bend in elbows, maintain throughout",
        "Squeeze chest at center, don't clank weights",
        "Feel the stretch at the bottom"
    ],
    "Leg Press": [
        "Feet shoulder-width on platform",
        "Don't lock knees at top",
        "Full range of motion",
        "Lower back stays against pad"
    ],
    "Leg Extension": [
        "Squeeze quads hard at the top",
        "Control the negative - 2-3 seconds",
        "Don't use momentum"
    ],
    "Leg Curl": [
        "Squeeze hamstrings at peak contraction",
        "Don't lift hips off pad",
        "Control the return"
    ],
    "Ab Roller Rollout": [
        "Start on knees, core braced",
        "Roll out as far as you can maintain form",
        "Pull back using abs, not hip flexors",
        "Keep arms straight throughout"
    ],
    "Russian Twist": [
        "Feet off floor for advanced, on floor for beginner",
        "Rotate through entire torso, not just arms",
        "Keep chest up, back straight"
    ],
}


class AICoachEngine:
    """
    The core AI coaching engine that analyzes workout history and provides
    intelligent recommendations for recovery, progressive overload, deload,
    and daily workout generation.
    """

    def __init__(self):
        self.workout_history = self._load_workout_history()
        self.completions = self._load_completions()
        self.all_exercises = get_all_exercises()

    # ═══════════════════════════════════════════════════════════════
    #  DATA LOADING
    # ═══════════════════════════════════════════════════════════════

    def _load_workout_history(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'workout_history.json')
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    return data
                return {}
        except Exception:
            pass
        return {}

    def _load_completions(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'workout_completions.json')
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    content = f.read().strip()
                    if content:
                        data = json.loads(content)
                        return data if isinstance(data, list) else []
        except Exception:
            pass
        return []

    # ═══════════════════════════════════════════════════════════════
    #  MUSCLE RECOVERY ANALYSIS
    # ═══════════════════════════════════════════════════════════════

    def calculate_muscle_recovery(self):
        """
        Calculate recovery percentage for each muscle group based on
        when they were last trained and how much volume was performed.

        Returns: dict of {muscle: {"recovery": 0-100, "last_trained": date_str, "status": str}}
        """
        today = datetime.now()
        results = {}

        for muscle in MUSCLE_GROUPS:
            last_trained = None
            total_depletion = 0

            # Scan completions for exercises that target this muscle
            for completion in self.completions:
                comp_date_str = completion.get('date', '')
                if not comp_date_str:
                    continue

                try:
                    comp_date = datetime.strptime(comp_date_str[:10], '%Y-%m-%d')
                except (ValueError, TypeError):
                    continue

                sets = completion.get('sets', [])
                for s in sets:
                    ex_name = s.get('exercise', '')
                    # Check if this exercise targets the current muscle
                    muscles_hit = COMPOUND_MUSCLE_MAP.get(ex_name, [])
                    if not muscles_hit:
                        # Try to find the muscle from the exercise database
                        for eid, ex in self.all_exercises.items():
                            if ex.get('name', '') == ex_name:
                                if ex.get('muscle', '') == muscle:
                                    muscles_hit = [muscle]
                                break

                    if muscle in muscles_hit:
                        if last_trained is None or comp_date > last_trained:
                            last_trained = comp_date
                        total_depletion += DEPLETION_PER_SET.get(muscle, 10)

            # Calculate recovery
            if last_trained is None:
                recovery = 100
                status = "Fresh"
                days_ago = None
            else:
                days_ago = (today - last_trained).days
                recovery_rate = RECOVERY_RATE_PER_DAY.get(muscle, 30)
                raw_recovery = 100 - total_depletion + (days_ago * recovery_rate)
                recovery = min(100, max(0, raw_recovery))

                if recovery >= 90:
                    status = "Fully Recovered"
                elif recovery >= 70:
                    status = "Mostly Recovered"
                elif recovery >= 40:
                    status = "Partially Recovered"
                elif recovery >= 20:
                    status = "Still Fatigued"
                else:
                    status = "Very Fatigued"

            results[muscle] = {
                "recovery": int(recovery),
                "last_trained": last_trained.strftime('%Y-%m-%d') if last_trained else "Never",
                "days_ago": days_ago,
                "status": status
            }

        return results

    # ═══════════════════════════════════════════════════════════════
    #  "TRAIN TODAY" RECOMMENDATION
    # ═══════════════════════════════════════════════════════════════

    def get_today_recommendation(self):
        """
        Based on recovery scores, recommend which muscles to train today.
        Picks the 2-3 most recovered muscle groups for optimal training.

        Returns: dict with "muscles" list and "reasoning" string
        """
        recovery = self.calculate_muscle_recovery()

        # Sort by recovery (highest first)
        sorted_muscles = sorted(
            [(m, r["recovery"]) for m, r in recovery.items()],
            key=lambda x: x[1], reverse=True
        )

        # Pick top 2-3 recovered muscles (exclude very low recovery)
        recommended = []
        reasoning_parts = []

        for muscle, score in sorted_muscles:
            if muscle == "Cardio":
                continue  # Handle cardio separately
            if score >= 80 and len(recommended) < 3:
                recommended.append(muscle)
                reasoning_parts.append(f"{muscle} is at {score}% recovery")

        if not recommended:
            # Fallback: pick the least fatigued
            for muscle, score in sorted_muscles:
                if muscle != "Cardio" and score >= 30:
                    recommended.append(muscle)
                    reasoning_parts.append(f"{muscle} is the least fatigued at {score}%")
                    if len(recommended) >= 2:
                        break

        if not recommended:
            recommended = ["Chest", "Back"]
            reasoning_parts.append("No strong data yet - defaulting to upper body")

        reasoning = f"Train {', '.join(recommended)} today. " + "; ".join(reasoning_parts) + "."

        return {
            "muscles": recommended,
            "reasoning": reasoning,
            "recovery": recovery
        }

    # ═══════════════════════════════════════════════════════════════
    #  PROGRESSIVE OVERLOAD ENGINE
    # ═══════════════════════════════════════════════════════════════

    def get_progressive_overload_suggestions(self):
        """
        Analyze workout history and suggest rep increases where
        the user has consistently hit their targets.
        Now reps-only (no weight tracking).

        Returns: list of dicts with exercise, current_reps, suggested_reps, reasoning
        """
        suggestions = []

        for ex_name, sessions in self.workout_history.items():
            if len(sessions) < 2:
                continue

            # Get recent sessions with numeric reps (reps-only mode)
            recent = []
            for s in sessions:
                r = s.get('reps', s.get('distance', '0'))
                try:
                    # Handle '10 reps' or plain '10'
                    reps_num = int(str(r).replace(' reps', '').replace(' km', '').strip())
                    if reps_num > 0:
                        recent.append(reps_num)
                except (ValueError, TypeError):
                    # Try total reps if multiple sets
                    try:
                        reps_num = int(r)
                        if reps_num > 0:
                            recent.append(reps_num)
                    except:
                        pass

            if len(recent) < 2:
                continue

            last_reps = recent[-1]
            avg_reps = sum(recent) / len(recent)

            if last_reps >= 15:
                # Hit 15+ reps consistently — suggest adding sets or harder variation
                suggestions.append({
                    'exercise': ex_name,
                    'current_reps': last_reps,
                    'suggested_reps': last_reps,
                    'reasoning': f"{last_reps} reps — strong endurance. Try a harder variation or add a set."
                })
            elif last_reps >= 12 and avg_reps >= 10:
                # Consistently hitting 12+, try harder variation
                suggestions.append({
                    'exercise': ex_name,
                    'current_reps': last_reps,
                    'suggested_reps': last_reps + 2,
                    'reasoning': f"Avg {int(avg_reps)} reps over {len(recent)} sessions. Push for {last_reps + 2} reps."
                })
            elif avg_reps < 8:
                # Low reps — focus on building up
                suggestions.append({
                    'exercise': ex_name,
                    'current_reps': last_reps,
                    'suggested_reps': last_reps + 1,
                    'reasoning': f"Avg {int(avg_reps)} reps. Add 1 rep per set to build volume."
                })

        return suggestions

    # ═══════════════════════════════════════════════════════════════
    #  PLATEAU DETECTION
    # ═══════════════════════════════════════════════════════════════

    def detect_plateaus(self):
        """
        Detect if any exercises have plateaued (no progress in 2+ weeks).

        Returns: list of dicts with exercise, plateau_weeks, recommendation
        """
        plateaus = []
        today = datetime.now()

        for ex_name, sessions in self.workout_history.items():
            if len(sessions) < 4:
                continue

            # Get sessions with numeric weights, sorted by date
            dated_sessions = []
            for s in sessions:
                w = s.get('weight', 0)
                date_str = s.get('date', '')
                if isinstance(w, (int, float)) and w > 0 and date_str:
                    try:
                        date = datetime.fromisoformat(date_str.replace('Z', '+00:00').replace('+00:00', ''))
                        dated_sessions.append({'weight': w, 'date': date})
                    except (ValueError, TypeError):
                        pass

            if len(dated_sessions) < 4:
                continue

            dated_sessions.sort(key=lambda x: x['date'])

            # Check if weight has been the same for 2+ weeks
            recent_weights = [s['weight'] for s in dated_sessions[-6:]]
            if len(set(recent_weights)) == 1:
                # All same weight
                weeks = (today - dated_sessions[0]['date']).days // 7
                if weeks >= 2:
                    # Check if it's a major compound (needs deload attention)
                    is_compound = False
                    for eid, ex in self.all_exercises.items():
                        if ex.get('name', '') == ex_name and ex.get('compound', False):
                            is_compound = True
                            break

                    plateaus.append({
                        'exercise': ex_name,
                        'weight': recent_weights[0],
                        'weeks_stalled': weeks,
                        'is_compound': is_compound,
                        'recommendation': 'deload' if (is_compound and weeks >= 3) else 'vary_rep_range'
                    })

        return plateaus

    # ═══════════════════════════════════════════════════════════════
    #  DELOAD WEEK SUGGESTIONS
    # ═══════════════════════════════════════════════════════════════

    def get_deload_suggestion(self):
        """
        If plateau detected on major compounds for 3+ weeks, suggest a deload.

        Returns: dict with should_deload, exercises, reasoning
        """
        plateaus = self.detect_plateaus()
        compound_plateaus = [p for p in plateaus if p['is_compound'] and p['weeks_stalled'] >= 3]

        if compound_plateaus:
            exercises = [p['exercise'] for p in compound_plateaus]
            return {
                'should_deload': True,
                'exercises': exercises,
                'weeks_stalled': max(p['weeks_stalled'] for p in compound_plateaus),
                'reasoning': f"Plateau detected on {', '.join(exercises)} for {max(p['weeks_stalled'] for p in compound_plateaus)}+ weeks. A deload week (reduce weight by 40-50%, keep reps the same) will help break through and prevent overtraining."
            }

        return {
            'should_deload': False,
            'exercises': [],
            'reasoning': 'No deload needed right now. Keep pushing!'
        }

    # ═══════════════════════════════════════════════════════════════
    #  DAILY WORKOUT GENERATION
    # ═══════════════════════════════════════════════════════════════

    def _get_selected_exercises(self):
        """Load the user's selected exercises from profile."""
        import json
        import os
        try:
            if os.path.exists("user_profile.json"):
                with open("user_profile.json", "r") as f:
                    profile = json.load(f)
                return profile.get("selected_exercises", [])
        except Exception:
            pass
        return []

    def generate_daily_workout(self, environment="commercial"):
        """
        Generate a complete workout for today based on recovery status
        and available equipment.
        Only uses exercises the user has selected in 'My Exercises'.

        Returns: dict with workout_name, exercises list, reasoning
        """
        recommendation = self.get_today_recommendation()
        target_muscles = recommendation['muscles']

        # Load user's selected exercises
        selected_ids = self._get_selected_exercises()

        # Get exercises for target muscles
        candidate_exercises = []
        for muscle in target_muscles:
            exercises = get_exercises_by_muscle(muscle)
            for eid, ex in exercises.items():
                # If user has a selection, only use those exercises
                if selected_ids and eid not in selected_ids:
                    continue
                candidate_exercises.append({
                    'id': eid,
                    'name': ex.get('name', ''),
                    'muscle': ex.get('muscle', ''),
                    'equip': ex.get('equip', ''),
                    'compound': ex.get('compound', False),
                    'sets': ex.get('sets', 3),
                    'reps': ex.get('reps', 10),
                    'tip': ex.get('tip', ''),
                    'track': ex.get('track', 'strength')
                })

        # Fallback: if selected exercises don't cover today's muscles, use all exercises
        if not candidate_exercises and selected_ids:
            for muscle in target_muscles:
                exercises = get_exercises_by_muscle(muscle)
                for eid, ex in exercises.items():
                    candidate_exercises.append({
                        'id': eid,
                        'name': ex.get('name', ''),
                        'muscle': ex.get('muscle', ''),
                        'equip': ex.get('equip', ''),
                        'compound': ex.get('compound', False),
                        'sets': ex.get('sets', 3),
                        'reps': ex.get('reps', 10),
                        'tip': ex.get('tip', ''),
                        'track': ex.get('track', 'strength')
                    })

        # Prioritize: compound first, then isolation
        compound = [e for e in candidate_exercises if e['compound']]
        isolation = [e for e in candidate_exercises if not e['compound']]

        # Pick 3-4 compound + 2-3 isolation = 5-6 total
        selected = []
        for e in compound[:3]:
            selected.append(e)
        for e in isolation[:3]:
            if len(selected) < 6:
                selected.append(e)

        if not selected:
            selected = candidate_exercises[:5]

        # Get progressive overload suggestions
        overload = self.get_progressive_overload_suggestions()
        overload_map = {s['exercise']: s for s in overload}

        # Enrich with overload data (reps-based)
        for ex in selected:
            if ex['name'] in overload_map:
                ol = overload_map[ex['name']]
                ex['suggested_reps'] = ol.get('suggested_reps', ex.get('reps', 10))
                ex['overload_reasoning'] = ol.get('reasoning', '')

        # Add superset pairing — pair isolation exercises as A1/A2
        iso_indices = [i for i, e in enumerate(selected) if not e.get('compound')]
        if len(iso_indices) >= 2:
            selected[iso_indices[0]]['superset_id'] = 'A'
            selected[iso_indices[1]]['superset_id'] = 'A'
            if len(iso_indices) >= 4:
                selected[iso_indices[2]]['superset_id'] = 'B'
                selected[iso_indices[3]]['superset_id'] = 'B'
        else:
            # No isolation? Pair last 2 compound exercises as a superset
            comp_indices = [i for i, e in enumerate(selected) if e.get('compound')]
            if len(comp_indices) >= 2:
                selected[comp_indices[-2]]['superset_id'] = 'A'
                selected[comp_indices[-1]]['superset_id'] = 'A'

        workout_name = " & ".join(target_muscles) + " Focus"

        return {
            'name': workout_name,
            'exercises': selected,
            'reasoning': recommendation['reasoning'],
            'recovery': recommendation['recovery']
        }

    # ═══════════════════════════════════════════════════════════════
    #  FORM TIPS
    # ═══════════════════════════════════════════════════════════════

    def get_form_tips(self, exercise_name):
        """Get form tips for a specific exercise."""
        tips = FORM_TIPS.get(exercise_name, [])

        if not tips:
            # Try to find tips from the exercise database
            for eid, ex in self.all_exercises.items():
                if ex.get('name', '') == exercise_name:
                    db_tip = ex.get('tip', '')
                    if db_tip:
                        tips = [db_tip]
                    break

        if not tips:
            tips = ["Focus on proper form and controlled movement."]

        return tips

    # ═══════════════════════════════════════════════════════════════
    #  WEEKLY VOLUME ANALYSIS
    # ═══════════════════════════════════════════════════════════════

    def get_weekly_volume(self):
        """
        Calculate total sets per muscle group for this week.

        Returns: dict of {muscle: {"sets": int, "target": int, "status": str}}
        """
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())

        volume = defaultdict(int)

        for completion in self.completions:
            comp_date_str = completion.get('date', '')
            try:
                comp_date = datetime.strptime(comp_date_str[:10], '%Y-%m-%d')
            except (ValueError, TypeError):
                continue

            if comp_date < week_start:
                continue

            sets = completion.get('sets', [])
            for s in sets:
                ex_name = s.get('exercise', '')
                muscles = COMPOUND_MUSCLE_MAP.get(ex_name, [])

                if not muscles:
                    for eid, ex in self.all_exercises.items():
                        if ex.get('name', '') == ex_name:
                            muscles = [ex.get('muscle', '')]
                            break

                for muscle in muscles:
                    if muscle in MUSCLE_GROUPS:
                        volume[muscle] += 1

        # Targets: 12-20 sets per muscle per week (sports science standard)
        targets = {
            "Chest": 16, "Back": 18, "Legs": 16, "Shoulders": 14,
            "Biceps": 10, "Triceps": 10, "Core": 8
        }

        result = {}
        for muscle in MUSCLE_GROUPS:
            sets = volume.get(muscle, 0)
            target = targets.get(muscle, 12)
            if sets >= target:
                status = "Optimal"
            elif sets >= target * 0.7:
                status = "Adequate"
            elif sets > 0:
                status = "Low"
            else:
                status = "No volume"

            result[muscle] = {
                "sets": sets,
                "target": target,
                "status": status,
                "percentage": min(100, int((sets / target) * 100)) if target > 0 else 0
            }

        return result

    # ═══════════════════════════════════════════════════════════════
    #  COMPREHENSIVE DASHBOARD DATA
    # ═══════════════════════════════════════════════════════════════

    def get_dashboard_data(self):
        """
        Aggregate all AI coaching data for the dashboard view.

        Returns: dict with recovery, recommendations, plateaus, volume, etc.
        """
        recovery = self.calculate_muscle_recovery()
        today_rec = self.get_today_recommendation()
        overload = self.get_progressive_overload_suggestions()
        plateaus = self.detect_plateaus()
        deload = self.get_deload_suggestion()
        volume = self.get_weekly_volume()
        workout = self.generate_daily_workout()

        # Summary stats
        total_workouts = len(self.completions)
        total_sets = sum(c.get('completed_sets', 0) for c in self.completions)

        return {
            'recovery': recovery,
            'today_recommendation': today_rec,
            'progressive_overload': overload[:5],  # Top 5
            'plateaus': plateaus,
            'deload': deload,
            'weekly_volume': volume,
            'generated_workout': workout,
            'total_workouts': total_workouts,
            'total_sets': total_sets
        }
