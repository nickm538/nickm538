"""
Promise analyzer module - calculates priority and feasibility scores.

All scores are clamped to [0.0, 1.0] range to ensure consistent output.
"""
import logging

logger = logging.getLogger(__name__)


def clamp(value, min_val=0.0, max_val=1.0):
    """Clamp a value to the specified range."""
    return max(min_val, min(max_val, value))


def calculate_priority_score(public_interest, budget_required):
    """
    Calculate priority score based on public interest and budget.
    
    Args:
        public_interest (int): Public interest level (1-10)
        budget_required (float): Budget required in millions
        
    Returns:
        float: Priority score clamped to [0.0, 1.0]
    """
    try:
        # Normalize public interest (1-10 scale to 0-1)
        interest_normalized = (public_interest - 1) / 9.0
        
        # Budget penalty: higher budget slightly reduces priority
        # Assume max budget of 1000 million for normalization
        budget_penalty = min(budget_required / 1000.0, 1.0) * 0.3
        
        # Base score from public interest minus budget penalty
        base_score = interest_normalized - budget_penalty
        
        # Ensure non-negative and clamp to [0, 1]
        score = clamp(max(0.0, base_score))
        
        logger.debug(f"Priority score: public_interest={public_interest}, budget={budget_required}, score={score}")
        return score
    except Exception as e:
        logger.error(f"Error calculating priority score: {e}")
        return 0.5  # Return neutral score on error


def calculate_feasibility_score(budget_required, legislative_complexity):
    """
    Calculate feasibility score based on budget and legislative complexity.
    
    Args:
        budget_required (float): Budget required in millions
        legislative_complexity (int): Complexity level (1-5)
        
    Returns:
        float: Feasibility score clamped to [0.0, 1.0]
    """
    try:
        # Ensure legislative_complexity is in expected range [1, 5]
        legislative_complexity = max(1, min(5, legislative_complexity))
        
        # Budget factor: lower budget = higher feasibility
        # Assume max budget of 1000 million
        budget_factor = 1.0 - min(budget_required / 1000.0, 1.0)
        
        # Legislative factor: lower complexity = higher feasibility
        # Convert 1-5 scale to 0-1 (inverted)
        legislative_factor = (5 - legislative_complexity) / 4.0
        
        # Average the two factors
        score = (budget_factor + legislative_factor) / 2.0
        
        # Clamp to [0, 1]
        score = clamp(score)
        
        logger.debug(f"Feasibility score: budget={budget_required}, complexity={legislative_complexity}, score={score}")
        return score
    except Exception as e:
        logger.error(f"Error calculating feasibility score: {e}")
        return 0.5


def calculate_impact_score(public_interest, budget_required):
    """
    Calculate impact score based on public interest and budget allocation.
    
    Args:
        public_interest (int): Public interest level (1-10)
        budget_required (float): Budget required in millions
        
    Returns:
        float: Impact score clamped to [0.0, 1.0]
    """
    try:
        # Higher public interest = higher impact
        interest_factor = (public_interest - 1) / 9.0
        
        # Larger budget can mean larger impact (but diminishing returns)
        # Use log scale for budget impact
        import math
        if budget_required > 0:
            budget_factor = min(math.log10(budget_required + 1) / 3.0, 1.0)
        else:
            budget_factor = 0.0
        
        # Weight interest more heavily (70/30)
        score = (interest_factor * 0.7) + (budget_factor * 0.3)
        
        # Clamp to [0, 1]
        score = clamp(score)
        
        logger.debug(f"Impact score: public_interest={public_interest}, budget={budget_required}, score={score}")
        return score
    except Exception as e:
        logger.error(f"Error calculating impact score: {e}")
        return 0.5


def calculate_urgency_score(deadline_days):
    """
    Calculate urgency score based on deadline.
    
    Args:
        deadline_days (int or None): Days until deadline (None = no deadline)
        
    Returns:
        float: Urgency score clamped to [0.0, 1.0]
    """
    try:
        if deadline_days is None or deadline_days < 0:
            # No deadline or already passed = low urgency
            return 0.3
        
        # Urgency increases as deadline approaches
        # Use exponential decay: more urgent as days decrease
        # Assume 365 days as baseline (1 year)
        if deadline_days == 0:
            return 1.0
        elif deadline_days <= 30:
            score = 0.9  # Very urgent (within a month)
        elif deadline_days <= 90:
            score = 0.7  # Urgent (within a quarter)
        elif deadline_days <= 180:
            score = 0.5  # Moderate urgency
        elif deadline_days <= 365:
            score = 0.4  # Low-moderate urgency
        else:
            score = 0.3  # Low urgency
        
        # Clamp to [0, 1]
        score = clamp(score)
        
        logger.debug(f"Urgency score: deadline_days={deadline_days}, score={score}")
        return score
    except Exception as e:
        logger.error(f"Error calculating urgency score: {e}")
        return 0.3


def calculate_overall_score(priority, feasibility, impact, urgency):
    """
    Calculate overall score as weighted average of component scores.
    
    Args:
        priority (float): Priority score
        feasibility (float): Feasibility score
        impact (float): Impact score
        urgency (float): Urgency score
        
    Returns:
        float: Overall score clamped to [0.0, 1.0]
    """
    try:
        # Weighted average: priority=30%, feasibility=25%, impact=25%, urgency=20%
        weights = {
            'priority': 0.30,
            'feasibility': 0.25,
            'impact': 0.25,
            'urgency': 0.20
        }
        
        score = (
            priority * weights['priority'] +
            feasibility * weights['feasibility'] +
            impact * weights['impact'] +
            urgency * weights['urgency']
        )
        
        # Clamp to [0, 1]
        score = clamp(score)
        
        logger.debug(f"Overall score: priority={priority}, feasibility={feasibility}, "
                    f"impact={impact}, urgency={urgency}, overall={score}")
        return score
    except Exception as e:
        logger.error(f"Error calculating overall score: {e}")
        return 0.5


def analyze_promise(promise):
    """
    Analyze a promise and update its score fields.
    
    Args:
        promise: Promise model instance
        
    Returns:
        promise: Updated promise with calculated scores
    """
    try:
        # Ensure required fields have sane defaults
        if promise.public_interest is None:
            promise.public_interest = 5
        if promise.budget_required is None:
            promise.budget_required = 0.0
        if promise.legislative_complexity is None:
            promise.legislative_complexity = 3
        
        # Calculate individual scores
        promise.priority_score = calculate_priority_score(
            promise.public_interest, 
            promise.budget_required
        )
        
        promise.feasibility_score = calculate_feasibility_score(
            promise.budget_required,
            promise.legislative_complexity
        )
        
        promise.impact_score = calculate_impact_score(
            promise.public_interest,
            promise.budget_required
        )
        
        promise.urgency_score = calculate_urgency_score(
            promise.deadline_days
        )
        
        # Calculate overall score
        promise.overall_score = calculate_overall_score(
            promise.priority_score,
            promise.feasibility_score,
            promise.impact_score,
            promise.urgency_score
        )
        
        logger.info(f"Analyzed promise '{promise.title}': overall_score={promise.overall_score:.2f}")
        return promise
        
    except Exception as e:
        logger.error(f"Error analyzing promise '{promise.title}': {e}")
        # Set neutral scores on error
        promise.priority_score = 0.5
        promise.feasibility_score = 0.5
        promise.impact_score = 0.5
        promise.urgency_score = 0.5
        promise.overall_score = 0.5
        return promise
