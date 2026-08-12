# exercise_search.py - Exercise search helper
# Provides a searchable exercise list for the workout view

def search_exercises(query, all_exercises, max_results=15):
    """
    Search exercises by name, muscle group, or equipment.
    
    Args:
        query: Search string
        all_exercises: Dict of exercise_id -> exercise dict
        max_results: Maximum results to return
    
    Returns:
        List of (exercise_id, exercise_dict) tuples
    """
    if not query or not query.strip():
        return list(all_exercises.items())[:max_results]
    
    query = query.lower().strip()
    results = []
    
    for eid, ex in all_exercises.items():
        name = ex.get('name', '').lower()
        muscle = ex.get('muscle', '').lower()
        equip = ex.get('equip', '').lower()
        
        # Score: name match = 3, muscle match = 2, equip match = 1
        score = 0
        if query in name:
            score = 3
        elif query in muscle:
            score = 2
        elif query in equip:
            score = 1
        
        if score > 0:
            results.append((score, eid, ex))
    
    # Sort by score (highest first), then alphabetically
    results.sort(key=lambda x: (-x[0], x[2].get('name', '')))
    
    return [(eid, ex) for _, eid, ex in results[:max_results]]
