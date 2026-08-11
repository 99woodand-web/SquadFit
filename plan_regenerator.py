# plan_regenerator.py - Workout Plan Regeneration Engine
# Detects goal/environment changes and generates new weekly plans.
# NO database modifications. NO breaking changes.

import os
import json
from datetime import datetime
from exercise_db import (
    get_all_exercises, get_exercises_by_muscle, get_exercises_by_equipment,
    WORKOUT_SPLITS, get_split_for_profile
)


# ═══════════════════════════════════════════════════════════════════════════════
#  GOAL DEFINITIONS
#  Each goal defines: split type, exercises per day, rest days, cardio mix
# ═══════════════════════════════════════════════════════════════════════════════

GOAL_CONFIGS = {
    "build_muscle": {
        "name": "Hypertrophy Split",
        "split_type": "push_pull_legs",
        "exercises_per_day": 5,
        "rest_days": [6],  # Sunday
        "cardio_mix": 0.1,  # 10% cardio
        "rep_range": "8-12",
        "rest_between_sets": "60-90s",
        "description": "Focus on muscle growth with moderate weight and higher volume"
    },
    "get_stronger": {
        "name": "Strength Split",
        "split_type": "heavy_compounds",
        "exercises_per_day": 5,
        "rest_days": [6],  # Sunday
        "cardio_mix": 0.05,  # 5% cardio
        "rep_range": "3-6",
        "rest_between_sets": "2-3min",
        "description": "Heavy compound lifts with longer rest periods"
    },
    "lose_weight": {
        "name": "Fat Loss Circuit",
        "split_type": "full_body_circuit",
        "exercises_per_day": 6,
        "rest_days": [6],  # Sunday
        "cardio_mix": 0.4,  # 40% cardio
        "rep_range": "12-15",
        "rest_between_sets": "30-45s",
        "description": "High-rep circuits with cardio intervals"
    },
    "general_fitness": {
        "name": "Balanced Fitness",
        "split_type": "full_body",
        "exercises_per_day": 5,
        "rest_days": [6],  # Sunday
        "cardio_mix": 0.25,  # 25% cardio
        "rep_range": "10-15",
        "rest_between_sets": "60-90s",
        "description": "Mix of strength, cardio, and flexibility"
    },
    "run_faster": {
        "name": "Running Program",
        "split_type": "cardio_focused",
        "exercises_per_day": 4,
        "rest_days": [4],  # Friday
        "cardio_mix": 0.7,  # 70% cardio
        "rep_range": "duration",
        "rest_between_sets": "varies",
        "description": "Running-focused with cross-training"
    },
    "cycle_more": {
        "name": "Cycling Program",
        "split_type": "cardio_focused",
        "exercises_per_day": 4,
        "rest_days": [4],  # Friday
        "cardio_mix": 0.7,  # 70% cardio
        "rep_range": "duration",
        "rest_between_sets": "varies",
        "description": "Cycling-focused with leg strength"
    }
}

# Equipment profiles for different environments
EQUIPMENT_PROFILES = {
    "commercial": {
        "name": "Commercial Gym",
        "available": ["Barbell", "Dumbbells", "Cable", "Machine", "Bands", "Bike", "Bench"],
        "description": "Full gym with all equipment"
    },
    "home_gym": {
        "name": "Home Gym",
        "available": ["Barbell", "Dumbbells", "Bench", "Bodyweight", "Bands"],
        "description": "Limited equipment - barbell, dumbbells, bench"
    },
    "cardio_only": {
        "name": "Cardio Only",
        "available": ["Bodyweight", "Bike", "Machine"],
        "description": "Running and cycling focus"
    }
}


class PlanRegenerator:
    """
    Generates new weekly workout plans based on user goals and equipment.
    """

    def __init__(self):
        self.all_exercises = get_all_exercises()
        self.user_profile = self._load_profile()

    def _load_profile(self):
        """Load user profile from file."""
        try:
            if os.path.exists("user_profile.json"):
                with open("user_profile.json", "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return {
            "goal": "build_muscle",
            "environment": "commercial",
            "experience": "Regular"
        }

    def get_current_plan_summary(self):
        """Get a summary of the current weekly plan."""
        calendar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'calendar_data.json')
        try:
            if os.path.exists(calendar_path):
                with open(calendar_path, 'r') as f:
                    data = json.load(f)
                return data
        except Exception:
            pass
        return None

    def generate_new_plan(self, goal, environment, experience="Regular"):
        """
        Generate a complete weekly workout plan based on goal and environment.

        Returns: dict with weekly schedule, exercises, and metadata
        """
        config = GOAL_CONFIGS.get(goal, GOAL_CONFIGS["build_muscle"])
        equip_profile = EQUIPMENT_PROFILES.get(environment, EQUIPMENT_PROFILES["commercial"])

        # Get available exercises based on equipment
        available = self._get_available_exercises(equip_profile["available"])

        # Generate the weekly schedule
        days = self._generate_weekly_schedule(config, available, goal)

        plan = {
            "goal": goal,
            "goal_name": config["name"],
            "environment": environment,
            "environment_name": equip_profile["name"],
            "experience": experience,
            "generated_at": datetime.now().isoformat(),
            "config": {
                "exercises_per_day": config["exercises_per_day"],
                "rep_range": config["rep_range"],
                "rest_between_sets": config["rest_between_sets"],
                "cardio_mix": config["cardio_mix"],
                "description": config["description"]
            },
            "days": days
        }

        return plan

    def _get_available_exercises(self, equipment_list):
        """Filter exercises by available equipment."""
        available = []
        for eid, ex in self.all_exercises.items():
            equip = ex.get("equip", "")
            tags = ex.get("equip_tags", [])

            # Check if exercise is available with current equipment
            if equip in equipment_list or equip == "Bodyweight":
                available.append({
                    "id": eid,
                    "name": ex.get("name", ""),
                    "muscle": ex.get("muscle", ""),
                    "equip": equip,
                    "compound": ex.get("compound", False),
                    "sets": ex.get("sets", 3),
                    "reps": ex.get("reps", 10),
                    "tip": ex.get("tip", ""),
                    "track": ex.get("track", "strength"),
                    "difficulty": ex.get("difficulty", "Intermediate")
                })
            elif any(t in equipment_list for t in tags):
                available.append({
                    "id": eid,
                    "name": ex.get("name", ""),
                    "muscle": ex.get("muscle", ""),
                    "equip": equip,
                    "compound": ex.get("compound", False),
                    "sets": ex.get("sets", 3),
                    "reps": ex.get("reps", 10),
                    "tip": ex.get("tip", ""),
                    "track": ex.get("track", "strength"),
                    "difficulty": ex.get("difficulty", "Intermediate")
                })

        return available

    def _generate_weekly_schedule(self, config, available, goal):
        """Generate a 7-day workout schedule."""
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        split_type = config["split_type"]
        exercises_per_day = config["exercises_per_day"]
        rest_days = config["rest_days"]
        cardio_mix = config["cardio_mix"]

        schedule = {}

        # Group exercises by muscle
        muscle_groups = {}
        for ex in available:
            muscle = ex["muscle"]
            if muscle not in muscle_groups:
                muscle_groups[muscle] = []
            muscle_groups[muscle].append(ex)

        # Generate based on split type
        if split_type == "push_pull_legs":
            schedule = self._generate_ppl(muscle_groups, exercises_per_day, rest_days, cardio_mix, available)
        elif split_type == "heavy_compounds":
            schedule = self._generate_strength(muscle_groups, exercises_per_day, rest_days, cardio_mix, available)
        elif split_type == "full_body_circuit":
            schedule = self._generate_circuit(muscle_groups, exercises_per_day, rest_days, cardio_mix, available)
        elif split_type == "full_body":
            schedule = self._generate_full_body(muscle_groups, exercises_per_day, rest_days, cardio_mix, available)
        elif split_type == "cardio_focused":
            schedule = self._generate_cardio(muscle_groups, exercises_per_day, rest_days, cardio_mix, available)
        else:
            schedule = self._generate_ppl(muscle_groups, exercises_per_day, rest_days, cardio_mix, available)

        # Convert to day name keys
        named_schedule = {}
        for i, day_name in enumerate(day_names):
            if i in schedule:
                named_schedule[day_name] = schedule[i]
            else:
                named_schedule[day_name] = {
                    "name": "Rest Day",
                    "exercises": [],
                    "focus": "Rest"
                }

        return named_schedule

    def _generate_ppl(self, muscle_groups, ex_per_day, rest_days, cardio_mix, available):
        """Generate Push/Pull/Legs split."""
        chest = muscle_groups.get("Chest", [])
        shoulders = muscle_groups.get("Shoulders", [])
        triceps = muscle_groups.get("Triceps", [])
        back = muscle_groups.get("Back", [])
        biceps = muscle_groups.get("Biceps", [])
        legs = muscle_groups.get("Legs", [])
        core = muscle_groups.get("Core", [])
        cardio = [e for e in available if e["track"] == "cardio"]

        schedule = {}

        # Monday: Push (Chest + Shoulders + Triceps)
        push_exercises = self._pick_exercises(
            chest[:3] + shoulders[:2] + triceps[:1], ex_per_day
        )
        schedule[0] = {
            "name": "Push Day",
            "focus": "Chest, Shoulders, Triceps",
            "exercises": [e["name"] for e in push_exercises]
        }

        # Tuesday: Pull (Back + Biceps)
        pull_exercises = self._pick_exercises(
            back[:3] + biceps[:2], ex_per_day
        )
        schedule[1] = {
            "name": "Pull Day",
            "focus": "Back, Biceps",
            "exercises": [e["name"] for e in pull_exercises]
        }

        # Wednesday: Legs
        leg_exercises = self._pick_exercises(
            legs[:4] + core[:1], ex_per_day
        )
        schedule[2] = {
            "name": "Leg Day",
            "focus": "Quads, Hamstrings, Glutes",
            "exercises": [e["name"] for e in leg_exercises]
        }

        # Thursday: Push (variation)
        push2_exercises = self._pick_exercises(
            chest[:2] + shoulders[:2] + triceps[:1], ex_per_day
        )
        schedule[3] = {
            "name": "Push Day",
            "focus": "Chest, Shoulders, Triceps",
            "exercises": [e["name"] for e in push2_exercises]
        }

        # Friday: Pull (variation)
        pull2_exercises = self._pick_exercises(
            back[:2] + biceps[:2], ex_per_day
        )
        schedule[4] = {
            "name": "Pull Day",
            "focus": "Back, Biceps",
            "exercises": [e["name"] for e in pull2_exercises]
        }

        # Saturday: Legs (variation)
        leg2_exercises = self._pick_exercises(
            legs[:3] + core[:2], ex_per_day
        )
        schedule[5] = {
            "name": "Leg Day",
            "focus": "Quads, Hamstrings, Glutes",
            "exercises": [e["name"] for e in leg2_exercises]
        }

        # Sunday: Rest
        schedule[6] = {
            "name": "Rest Day",
            "focus": "Rest",
            "exercises": []
        }

        return schedule

    def _generate_strength(self, muscle_groups, ex_per_day, rest_days, cardio_mix, available):
        """Generate heavy compound strength split."""
        chest = muscle_groups.get("Chest", [])
        back = muscle_groups.get("Back", [])
        legs = muscle_groups.get("Legs", [])
        shoulders = muscle_groups.get("Shoulders", [])

        schedule = {}

        # Monday: Heavy Chest
        schedule[0] = {
            "name": "Heavy Chest",
            "focus": "Chest & Triceps",
            "exercises": [e["name"] for e in self._pick_exercises(chest[:3] + muscle_groups.get("Triceps", [])[:2], ex_per_day)]
        }

        # Tuesday: Heavy Back
        schedule[1] = {
            "name": "Heavy Back",
            "focus": "Back & Biceps",
            "exercises": [e["name"] for e in self._pick_exercises(back[:3] + muscle_groups.get("Biceps", [])[:2], ex_per_day)]
        }

        # Wednesday: Heavy Legs
        schedule[2] = {
            "name": "Heavy Legs",
            "focus": "Legs & Core",
            "exercises": [e["name"] for e in self._pick_exercises(legs[:4] + muscle_groups.get("Core", [])[:1], ex_per_day)]
        }

        # Thursday: Heavy Shoulders
        schedule[3] = {
            "name": "Heavy Shoulders",
            "focus": "Shoulders & Arms",
            "exercises": [e["name"] for e in self._pick_exercises(shoulders[:3] + muscle_groups.get("Biceps", [])[:1] + muscle_groups.get("Triceps", [])[:1], ex_per_day)]
        }

        # Friday: Full Body Compound
        compounds = [e for e in available if e["compound"]][:5]
        schedule[4] = {
            "name": "Full Body Compounds",
            "focus": "Squat, Bench, Deadlift",
            "exercises": [e["name"] for e in compounds[:ex_per_day]]
        }

        # Saturday: Active Recovery
        schedule[5] = {
            "name": "Active Recovery",
            "focus": "Light Cardio & Mobility",
            "exercises": [e["name"] for e in [e for e in available if e["track"] == "cardio"][:3]]
        }

        schedule[6] = {"name": "Rest Day", "focus": "Rest", "exercises": []}

        return schedule

    def _generate_circuit(self, muscle_groups, ex_per_day, rest_days, cardio_mix, available):
        """Generate fat loss circuit split."""
        all_muscles = list(muscle_groups.values())
        cardio = [e for e in available if e["track"] == "cardio"]

        schedule = {}

        # Monday: Upper Body Circuit
        upper = []
        for muscle in ["Chest", "Back", "Shoulders", "Biceps", "Triceps"]:
            upper.extend(muscle_groups.get(muscle, [])[:1])
        schedule[0] = {
            "name": "Upper Body Circuit",
            "focus": "Full Upper Body",
            "exercises": [e["name"] for e in self._pick_exercises(upper, ex_per_day)]
        }

        # Tuesday: HIIT Cardio
        schedule[1] = {
            "name": "HIIT Cardio",
            "focus": "High Intensity Intervals",
            "exercises": [e["name"] for e in cardio[:ex_per_day]]
        }

        # Wednesday: Lower Body Circuit
        lower = muscle_groups.get("Legs", [])[:4] + muscle_groups.get("Core", [])[:2]
        schedule[2] = {
            "name": "Lower Body Circuit",
            "focus": "Full Lower Body",
            "exercises": [e["name"] for e in self._pick_exercises(lower, ex_per_day)]
        }

        # Thursday: Active Recovery
        schedule[3] = {
            "name": "Active Recovery",
            "focus": "Light Movement",
            "exercises": [e["name"] for e in cardio[:2]]
        }

        # Friday: Full Body Circuit
        full = []
        for muscle in ["Chest", "Back", "Legs", "Shoulders", "Core"]:
            full.extend(muscle_groups.get(muscle, [])[:1])
        schedule[4] = {
            "name": "Full Body Circuit",
            "focus": "Total Body Blast",
            "exercises": [e["name"] for e in self._pick_exercises(full, ex_per_day)]
        }

        # Saturday: Cardio
        schedule[5] = {
            "name": "Cardio Day",
            "focus": "Steady State Cardio",
            "exercises": [e["name"] for e in cardio[:3]]
        }

        schedule[6] = {"name": "Rest Day", "focus": "Rest", "exercises": []}

        return schedule

    def _generate_full_body(self, muscle_groups, ex_per_day, rest_days, cardio_mix, available):
        """Generate balanced full body split."""
        schedule = {}

        # Alternate between 3 full body days
        for day_idx in [0, 2, 4]:  # Mon, Wed, Fri
            full = []
            for muscle in ["Chest", "Back", "Legs", "Shoulders", "Core"]:
                full.extend(muscle_groups.get(muscle, [])[:1])
            full.extend(muscle_groups.get("Biceps", [])[:1] + muscle_groups.get("Triceps", [])[:1])

            schedule[day_idx] = {
                "name": "Full Body",
                "focus": "All Major Muscle Groups",
                "exercises": [e["name"] for e in self._pick_exercises(full, ex_per_day)]
            }

        # Tuesday: Cardio
        cardio = [e for e in available if e["track"] == "cardio"]
        schedule[1] = {
            "name": "Cardio & Core",
            "focus": "Cardiovascular Fitness",
            "exercises": [e["name"] for e in cardio[:3] + muscle_groups.get("Core", [])[:2]][:ex_per_day]
        }

        # Thursday: Upper/Lower Split
        upper = muscle_groups.get("Chest", [])[:2] + muscle_groups.get("Back", [])[:2] + muscle_groups.get("Shoulders", [])[:1]
        schedule[3] = {
            "name": "Upper Body",
            "focus": "Push & Pull",
            "exercises": [e["name"] for e in self._pick_exercises(upper, ex_per_day)]
        }

        # Saturday: Active Recovery
        schedule[5] = {
            "name": "Active Recovery",
            "focus": "Light Movement",
            "exercises": [e["name"] for e in cardio[:2]]
        }

        schedule[6] = {"name": "Rest Day", "focus": "Rest", "exercises": []}

        return schedule

    def _generate_cardio(self, muscle_groups, ex_per_day, rest_days, cardio_mix, available):
        """Generate cardio-focused (running/cycling) split."""
        cardio = [e for e in available if e["track"] == "cardio"]
        legs = muscle_groups.get("Legs", [])
        core = muscle_groups.get("Core", [])

        schedule = {}

        # Monday: Easy Run
        schedule[0] = {
            "name": "Easy Run",
            "focus": "Aerobic Base",
            "exercises": [e["name"] for e in cardio[:2] + core[:1]][:ex_per_day]
        }

        # Tuesday: Speed Work
        schedule[1] = {
            "name": "Speed Work",
            "focus": "Intervals & Sprints",
            "exercises": [e["name"] for e in cardio[:3]][:ex_per_day]
        }

        # Wednesday: Cross Training
        schedule[2] = {
            "name": "Cross Training",
            "focus": "Leg Strength & Core",
            "exercises": [e["name"] for e in legs[:3] + core[:1]][:ex_per_day]
        }

        # Thursday: Tempo Run
        schedule[3] = {
            "name": "Tempo Run",
            "focus": "Threshold Training",
            "exercises": [e["name"] for e in cardio[:2]][:ex_per_day]
        }

        # Friday: Rest
        schedule[4] = {"name": "Rest Day", "focus": "Rest", "exercises": []}

        # Saturday: Long Run
        schedule[5] = {
            "name": "Long Run",
            "focus": "Endurance",
            "exercises": [e["name"] for e in cardio[:2] + core[:1]][:ex_per_day]
        }

        # Sunday: Recovery
        schedule[6] = {
            "name": "Recovery",
            "focus": "Easy Movement",
            "exercises": [e["name"] for e in cardio[:1] + core[:1]][:ex_per_day]
        }

        return schedule

    def _pick_exercises(self, candidates, count):
        """Pick the best exercises from candidates, prioritizing compounds."""
        if not candidates:
            return []

        # Sort: compounds first, then by muscle variety
        compounds = [e for e in candidates if e.get("compound", False)]
        isolations = [e for e in candidates if not e.get("compound", False)]

        selected = []
        for ex in compounds:
            if len(selected) < count:
                selected.append(ex)

        for ex in isolations:
            if len(selected) < count:
                # Avoid duplicate muscles
                muscles_so_far = [e["muscle"] for e in selected]
                if ex["muscle"] not in muscles_so_far or len(selected) < 3:
                    selected.append(ex)

        # Fill remaining if needed
        remaining = [e for e in candidates if e not in selected]
        for ex in remaining:
            if len(selected) < count:
                selected.append(ex)

        return selected[:count]

    def save_plan(self, plan):
        """Save the generated plan to calendar_data.json."""
        try:
            with open("calendar_data.json", "w") as f:
                json.dump(plan, f, indent=2)
            print(f"[PlanRegenerator] Saved plan: {plan['goal_name']}")
            return True
        except Exception as e:
            print(f"[PlanRegenerator] Error saving plan: {e}")
            return False

    def load_plan(self):
        """Load the current plan from calendar_data.json."""
        try:
            if os.path.exists("calendar_data.json"):
                with open("calendar_data.json", "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return None


def detect_goal_change(old_profile, new_profile):
    """
    Detect if the user's goal or environment has changed.

    Returns: dict with changed fields and whether regeneration is needed
    """
    changes = {
        "goal_changed": old_profile.get("goal") != new_profile.get("goal"),
        "environment_changed": old_profile.get("environment") != new_profile.get("environment"),
        "needs_regeneration": False,
        "old_goal": old_profile.get("goal", "build_muscle"),
        "new_goal": new_profile.get("goal", "build_muscle"),
        "old_environment": old_profile.get("environment", "commercial"),
        "new_environment": new_profile.get("environment", "commercial")
    }

    changes["needs_regeneration"] = changes["goal_changed"] or changes["environment_changed"]

    return changes


def generate_change_preview(changes):
    """
    Generate a preview of what will change when the user confirms.

    Returns: dict with old plan summary, new plan summary, and comparison
    """
    regenerator = PlanRegenerator()

    old_config = GOAL_CONFIGS.get(changes["old_goal"], GOAL_CONFIGS["build_muscle"])
    new_config = GOAL_CONFIGS.get(changes["new_goal"], GOAL_CONFIGS["build_muscle"])

    old_equip = EQUIPMENT_PROFILES.get(changes["old_environment"], EQUIPMENT_PROFILES["commercial"])
    new_equip = EQUIPMENT_PROFILES.get(changes["new_environment"], EQUIPMENT_PROFILES["commercial"])

    preview = {
        "old": {
            "goal_name": old_config["name"],
            "environment_name": old_equip["name"],
            "description": old_config["description"]
        },
        "new": {
            "goal_name": new_config["name"],
            "environment_name": new_equip["name"],
            "description": new_config["description"],
            "exercises_per_day": new_config["exercises_per_day"],
            "rep_range": new_config["rep_range"],
            "rest_between_sets": new_config["rest_between_sets"],
            "cardio_mix": f"{int(new_config['cardio_mix'] * 100)}%"
        },
        "changes": []
    }

    if changes["goal_changed"]:
        preview["changes"].append(f"Goal: {old_config['name']} -> {new_config['name']}")
    if changes["environment_changed"]:
        preview["changes"].append(f"Equipment: {old_equip['name']} -> {new_equip['name']}")

    return preview
