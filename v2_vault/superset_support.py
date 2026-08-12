# superset_support.py - Superset pairing logic
# Handles A1/A2 exercise pairing for the workout view

def detect_supersets(exercises_data):
    """
    Detect superset pairs in the exercise list.
    
    Returns a dict mapping exercise index -> superset info:
    {
        0: {'letter': 'A', 'position': 1, 'pair_size': 2},
        1: {'letter': 'A', 'position': 2, 'pair_size': 2},
        2: {'letter': 'B', 'position': 1, 'pair_size': 2},
        3: {'letter': 'B', 'position': 2, 'pair_size': 2},
    }
    """
    superset_map = {}
    current_letter = None
    current_pair = []
    
    for idx, ex in enumerate(exercises_data):
        superset_id = ex.get('superset_id')
        
        if superset_id is not None:
            # Same superset as previous exercise
            if current_letter == superset_id:
                current_pair.append(idx)
            else:
                # New superset - close previous if any
                if len(current_pair) == 2:
                    for i, pi in enumerate(current_pair):
                        superset_map[pi] = {
                            'letter': chr(ord('A') + len([k for k in superset_map.values() if k['letter'] == chr(ord('A') + len(superset_map))]) // 2),
                            'position': i + 1,
                            'pair_size': 2
                        }
                elif len(current_pair) == 1:
                    # Single exercise with superset_id - treat as standalone
                    superset_map.pop(current_pair[0], None)
                
                current_letter = superset_id
                current_pair = [idx]
        else:
            # Standalone exercise - close any open superset
            if len(current_pair) == 2:
                for i, pi in enumerate(current_pair):
                    superset_map[pi] = {
                        'letter': chr(ord('A') + len([k for k in superset_map.values() if k['letter'] == chr(ord('A') + len(superset_map))]) // 2),
                        'position': i + 1,
                        'pair_size': 2
                    }
            current_letter = None
            current_pair = []
    
    # Close any open superset at the end
    if len(current_pair) == 2:
        letter = chr(ord('A') + len([k for k in superset_map.values() if k['letter'] == chr(ord('A') + len(superset_map))]) // 2)
        for i, pi in enumerate(current_pair):
            superset_map[pi] = {
                'letter': letter,
                'position': i + 1,
                'pair_size': 2
            }
    
    return superset_map


def assign_superset_ids(exercises, pairs):
    """
    Assign superset_id to exercises based on user-specified pairs.
    
    Args:
        exercises: List of exercise dicts
        pairs: List of tuples, e.g., [(0, 1), (2, 3)] for A1/A2, B1/B2
    
    Returns:
        Modified exercises list with superset_id assigned
    """
    for pair_idx, (i, j) in enumerate(pairs):
        letter = chr(ord('A') + pair_idx)
        if i < len(exercises):
            exercises[i]['superset_id'] = letter
        if j < len(exercises):
            exercises[j]['superset_id'] = letter
    
    return exercises
