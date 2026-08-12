# weight_tracking.py - Vaulted for v2
# Weight tracking functions removed from v1 to simplify the workout experience.
# These can be reintroduced if weight tracking is added back in v2.


def exercise_uses_weight(exercise_id):
    """Check if an exercise uses external weights."""
    from exercise_db import get_all_exercises
    all_ex = get_all_exercises()
    if exercise_id in all_ex:
        equip = all_ex[exercise_id].get('equip', '')
        return equip in ['Barbell', 'Dumbbells', 'Cable', 'Machine']
    return False


def exercise_uses_weight_by_name(exercise_name):
    """Check if an exercise uses weights by name."""
    from exercise_db import get_all_exercises
    all_ex = get_all_exercises()
    for eid, ex in all_ex.items():
        if ex.get('name', '').lower() == exercise_name.lower():
            return ex.get('equip', '') in ['Barbell', 'Dumbbells', 'Cable', 'Machine']
    return False


def exercise_uses_barbell_by_name(exercise_name):
    """Check if an exercise uses a barbell."""
    from exercise_db import get_all_exercises
    all_ex = get_all_exercises()
    for eid, ex in all_ex.items():
        if ex.get('name', '').lower() == exercise_name.lower():
            return ex.get('equip', '') == 'Barbell'
    return False
