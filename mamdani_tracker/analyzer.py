"""
Analyzer module for scoring political promises.

This module computes feasibility, impact, and priority scores for promises
with proper bounds checking and consistent calculations.
"""
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """
    Clamp a value between min_val and max_val.
    
    Args:
        value: The value to clamp
        min_val: Minimum allowed value (default 0.0)
        max_val: Maximum allowed value (default 1.0)
    
    Returns:
        Clamped value between min_val and max_val
    """
    return max(min_val, min(max_val, value))


def analyze_promise(promise_data: Dict) -> Dict[str, float]:
    """
    Analyze a promise and compute scores.
    
    This function computes:
    - feasibility_score: How achievable the promise is (0.0 to 1.0)
    - impact_score: Expected societal impact (0.0 to 1.0)
    - priority_score: Overall priority rating (0.0 to 1.0)
    - budget_required: Estimated budget in millions (always >= 0.0)
    - legislative_complexity: Complexity of legislative process (0.0 to 1.0)
    
    Args:
        promise_data: Dictionary containing promise information
    
    Returns:
        Dictionary with computed scores, all properly clamped
    """
    title = promise_data.get('title', '').lower()
    description = promise_data.get('description', '').lower()
    category = promise_data.get('category', '').lower()
    
    # Initialize scores with safe defaults
    feasibility_score = 0.5
    impact_score = 0.5
    priority_score = 0.5
    budget_required = 0.0
    legislative_complexity = 0.5
    
    # Simple keyword-based analysis
    # Feasibility: affected by complexity keywords
    complexity_keywords = ['comprehensive', 'overhaul', 'reform', 'transform', 'revolutionary']
    simple_keywords = ['maintain', 'continue', 'support', 'increase', 'decrease']
    
    complexity_count = sum(1 for kw in complexity_keywords if kw in title or kw in description)
    simple_count = sum(1 for kw in simple_keywords if kw in title or kw in description)
    
    # Base feasibility starts at 0.5
    if simple_count > complexity_count:
        feasibility_score = 0.7 + (simple_count * 0.05)
    elif complexity_count > 0:
        feasibility_score = 0.5 - (complexity_count * 0.1)
    
    # Impact: based on scope keywords
    high_impact_keywords = ['national', 'universal', 'all', 'every', 'healthcare', 'education']
    moderate_impact_keywords = ['local', 'community', 'regional', 'targeted']
    
    high_impact_count = sum(1 for kw in high_impact_keywords if kw in title or kw in description)
    moderate_impact_count = sum(1 for kw in moderate_impact_keywords if kw in title or kw in description)
    
    if high_impact_count > 0:
        impact_score = 0.7 + (high_impact_count * 0.05)
    elif moderate_impact_count > 0:
        impact_score = 0.5 + (moderate_impact_count * 0.05)
    
    # Budget estimation
    budget_keywords = {
        'healthcare': 100.0,
        'infrastructure': 200.0,
        'education': 50.0,
        'defense': 150.0,
        'tax': 75.0,
        'climate': 180.0,
    }
    
    for keyword, cost in budget_keywords.items():
        if keyword in title or keyword in description:
            budget_required += cost
    
    # Ensure budget is never negative
    budget_required = max(0.0, budget_required)
    
    # Legislative complexity
    if 'constitution' in title or 'constitution' in description:
        legislative_complexity = 0.9
    elif 'law' in title or 'act' in title or 'legislation' in description:
        legislative_complexity = 0.7
    elif 'executive' in title or 'order' in description:
        legislative_complexity = 0.3
    else:
        legislative_complexity = 0.5
    
    # Priority is a weighted combination of impact and feasibility
    priority_score = (impact_score * 0.6) + (feasibility_score * 0.4)
    
    # Clamp all scores to [0.0, 1.0] range
    result = {
        'feasibility_score': clamp(feasibility_score),
        'impact_score': clamp(impact_score),
        'priority_score': clamp(priority_score),
        'budget_required': max(0.0, budget_required),  # Budget can be > 1.0, but never negative
        'legislative_complexity': clamp(legislative_complexity),
    }
    
    logger.debug(f"Analyzed promise: {title[:50]}... Scores: {result}")
    
    return result


def update_promise_scores(promise) -> None:
    """
    Update promise object with analyzed scores.
    
    Args:
        promise: Promise model instance to update
    """
    promise_data = {
        'title': promise.title or '',
        'description': promise.description or '',
        'category': promise.category or '',
    }
    
    scores = analyze_promise(promise_data)
    
    promise.feasibility_score = scores['feasibility_score']
    promise.impact_score = scores['impact_score']
    promise.priority_score = scores['priority_score']
    promise.budget_required = scores['budget_required']
    promise.legislative_complexity = scores['legislative_complexity']
    
    logger.info(f"Updated scores for promise {promise.id}: {promise.title[:50]}...")
