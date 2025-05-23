"""Vector math utility functions for bias analysis"""
from typing import List, Dict, Set

def calculate_variance(values: List[float]) -> float:
    """Calculate the statistical variance of a list of values"""
    if not values:
        return 0
    mean = sum(values) / len(values)
    squared_diff_sum = sum((x - mean) ** 2 for x in values)
    return squared_diff_sum / len(values)

def calculate_bias_similarity(category_lists: List[Dict[str, float]]) -> float:
    """Calculate similarity between bias category distributions"""
    # Convert category lists to vectors and calculate cosine similarity
    all_categories: Set[str] = set()
    for cats in category_lists:
        all_categories.update(cats.keys())
        
    vectors: List[List[float]] = []
    for cats in category_lists:
        vector = [cats.get(cat, 0.0) for cat in sorted(all_categories)]
        vectors.append(vector)
        
    # Calculate average pairwise similarity
    similarities: List[float] = []
    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):
            similarities.append(cosine_similarity(vectors[i], vectors[j]))
            
    return sum(similarities) / len(similarities) if similarities else 0.0

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm1 = sum(a * a for a in v1) ** 0.5
    norm2 = sum(b * b for b in v2) ** 0.5
    return dot_product / (norm1 * norm2) if norm1 * norm2 != 0 else 0.0

def analyze_context_overlap(context_lists: List[Dict[str, List[str]]]) -> Dict[str, float]:
    """Analyze how much context overlaps between articles"""
    # Extract all related events and missing context
    all_events: Set[str] = set()
    all_missing: Set[str] = set()
    
    for ctx in context_lists:
        if 'related_events' in ctx:
            all_events.update(ctx.get('related_events', []))
        if 'missing_context' in ctx:
            all_missing.update(ctx.get('missing_context', []))
    
    # Calculate overlap ratios
    events_sum = sum(len(ctx.get('related_events', [])) for ctx in context_lists)
    missing_sum = sum(len(ctx.get('missing_context', [])) for ctx in context_lists)
    
    event_overlap = len(all_events) / (events_sum if events_sum > 0 else 1)
    missing_overlap = len(all_missing) / (missing_sum if missing_sum > 0 else 1)
    
    return {
        'event_overlap': event_overlap,
        'missing_context_overlap': missing_overlap
    }
