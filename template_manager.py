"""
template_manager.py — Workout Template Manager
Save, load, list, and delete workout templates.
Templates store exercise structure (sets/reps) without actual weights.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional


TEMPLATE_FILE = "workout_templates.json"


class WorkoutTemplate:
    """A saved workout template with exercise structure."""

    def __init__(self, name: str, day_type: str = "Gym", focus: str = "",
                 exercises: List[Dict] = None, created: str = ""):
        self.name = name
        self.day_type = day_type  # "Gym", "Home", "Cardio"
        self.focus = focus  # e.g., "Chest & Triceps", "Legs"
        self.exercises = exercises or []  # List of exercise dicts
        self.created = created or datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "day_type": self.day_type,
            "focus": self.focus,
            "exercises": self.exercises,
            "created": self.created,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorkoutTemplate":
        return cls(
            name=data.get("name", "Untitled"),
            day_type=data.get("day_type", "Gym"),
            focus=data.get("focus", ""),
            exercises=data.get("exercises", []),
            created=data.get("created", ""),
        )

    @property
    def exercise_count(self) -> int:
        return len(self.exercises)

    @property
    def total_sets(self) -> int:
        return sum(e.get("target_sets", 3) for e in self.exercises)


class TemplateManager:
    """Manages saving, loading, and deleting workout templates."""

    def __init__(self, filepath: str = TEMPLATE_FILE):
        self.filepath = filepath
        self.templates: List[WorkoutTemplate] = []
        self._load()

    def _load(self):
        """Load templates from file."""
        if not os.path.exists(self.filepath):
            self.templates = []
            return

        try:
            with open(self.filepath, "r") as f:
                data = json.load(f)
            self.templates = [WorkoutTemplate.from_dict(t) for t in data.get("templates", [])]
        except Exception as e:
            print(f"[TemplateManager] Error loading templates: {e}")
            self.templates = []

    def _save(self):
        """Save templates to file."""
        try:
            data = {
                "templates": [t.to_dict() for t in self.templates],
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.filepath, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[TemplateManager] Error saving templates: {e}")

    def save_template(self, name: str, day_type: str, focus: str,
                      exercises: List[Dict]) -> WorkoutTemplate:
        """
        Save a new workout template.

        Args:
            name: Template name (e.g., "Push Day A")
            day_type: "Gym", "Home", or "Cardio"
            focus: Muscle focus (e.g., "Chest & Triceps")
            exercises: List of exercise dicts with exercise_id, target_sets, target_reps

        Returns:
            The created template
        """
        template = WorkoutTemplate(
            name=name,
            day_type=day_type,
            focus=focus,
            exercises=exercises,
        )
        self.templates.append(template)
        self._save()
        print(f"[TemplateManager] Saved template: {name} ({len(exercises)} exercises)")
        return template

    def save_from_session(self, name: str, session_data: Dict) -> WorkoutTemplate:
        """
        Save a completed workout session as a template.
        Strips actual weights, keeping only exercise structure.

        Args:
            name: Template name
            session_data: WorkoutSession dict with exercises

        Returns:
            The created template
        """
        exercises = []
        for ex in session_data.get("exercises", []):
            exercises.append({
                "exercise_id": ex.get("exercise_id", ""),
                "exercise_name": ex.get("exercise_name", ""),
                "target_sets": ex.get("target_sets", 3),
                "target_reps": ex.get("target_reps", 10),
                "category": ex.get("category", ""),
                "equipment": ex.get("equipment", ""),
            })

        return self.save_template(
            name=name,
            day_type=session_data.get("day_type", "Gym"),
            focus=session_data.get("focus", ""),
            exercises=exercises,
        )

    def load_template(self, index: int) -> Optional[WorkoutTemplate]:
        """Load a template by index."""
        if 0 <= index < len(self.templates):
            return self.templates[index]
        return None

    def get_template_names(self) -> List[str]:
        """Get all template names."""
        return [t.name for t in self.templates]

    def get_templates_by_type(self, day_type: str) -> List[WorkoutTemplate]:
        """Get templates filtered by day type."""
        return [t for t in self.templates if t.day_type.lower() == day_type.lower()]

    def delete_template(self, index: int) -> bool:
        """Delete a template by index."""
        if 0 <= index < len(self.templates):
            name = self.templates[index].name
            self.templates.pop(index)
            self._save()
            print(f"[TemplateManager] Deleted template: {name}")
            return True
        return False

    def rename_template(self, index: int, new_name: str) -> bool:
        """Rename a template."""
        if 0 <= index < len(self.templates):
            self.templates[index].name = new_name
            self._save()
            return True
        return False

    @property
    def count(self) -> int:
        return len(self.templates)
