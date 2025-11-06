"""
AI Analysis Engine for ranking promise likelihood
"""
from typing import List, Dict
import re


class PromiseAnalyzer:
    """
    Analyzes political promises and ranks them by likelihood of implementation
    """

    def __init__(self):
        # Political context factors for NYC (2025)
        self.political_context = {
            'city_council_progressive': 0.65,  # Progressive majority
            'state_legislature_progressive': 0.70,  # Democratic majority
            'budget_surplus': 0.45,  # Moderate budget constraints
            'public_support_progressive': 0.60  # Public sentiment
        }

        # Category weights for different types of promises
        self.category_weights = {
            'Housing': {
                'political_priority': 0.9,
                'budget_impact': 0.8,
                'complexity': 0.7
            },
            'Transportation': {
                'political_priority': 0.7,
                'budget_impact': 0.6,
                'complexity': 0.8
            },
            'Education': {
                'political_priority': 0.85,
                'budget_impact': 0.7,
                'complexity': 0.6
            },
            'Public Safety': {
                'political_priority': 0.95,
                'budget_impact': 0.65,
                'complexity': 0.5
            },
            'Environment': {
                'political_priority': 0.7,
                'budget_impact': 0.6,
                'complexity': 0.7
            },
            'Economic Development': {
                'political_priority': 0.8,
                'budget_impact': 0.75,
                'complexity': 0.65
            }
        }

    def analyze_promise(self, promise) -> Dict:
        """
        Comprehensive analysis of a promise
        Returns: dict with likelihood_score, analysis_text, and factor scores
        """
        # Extract factors from promise
        budget_score = self._analyze_budget_requirement(promise)
        complexity_score = self._analyze_complexity(promise)
        political_score = self._analyze_political_alignment(promise)
        public_support_score = self._analyze_public_support(promise)
        category_score = self._analyze_category_priority(promise)

        # Calculate weighted likelihood score
        weights = {
            'budget': 0.20,
            'complexity': 0.15,
            'political': 0.30,
            'public_support': 0.20,
            'category': 0.15
        }

        likelihood_score = (
            budget_score * weights['budget'] +
            complexity_score * weights['complexity'] +
            political_score * weights['political'] +
            public_support_score * weights['public_support'] +
            category_score * weights['category']
        )

        # Generate analysis text
        analysis_text = self._generate_analysis_text(
            promise, likelihood_score, budget_score, complexity_score,
            political_score, public_support_score, category_score
        )

        return {
            'likelihood_score': round(likelihood_score, 3),
            'analysis_text': analysis_text,
            'budget_score': round(budget_score, 3),
            'complexity_score': round(complexity_score, 3),
            'political_score': round(political_score, 3),
            'public_support_score': round(public_support_score, 3),
            'category_score': round(category_score, 3)
        }

    def _analyze_budget_requirement(self, promise) -> float:
        """
        Analyze budget requirements and return a score (0-1)
        Higher score = more feasible budget-wise
        """
        text = f"{promise.title} {promise.description}".lower()

        # Keyword analysis for budget impact
        high_cost_keywords = [
            'billion', 'construct', 'build new', 'universal', 'citywide',
            'infrastructure', 'expansion', 'major project'
        ]
        medium_cost_keywords = [
            'million', 'program', 'initiative', 'fund', 'establish',
            'improve', 'renovate', 'upgrade'
        ]
        low_cost_keywords = [
            'policy', 'reform', 'regulation', 'enforce', 'review',
            'study', 'plan', 'coordinate'
        ]

        if any(keyword in text for keyword in high_cost_keywords):
            budget_level = 'Very High'
            score = 0.3  # Less likely due to high cost
        elif any(keyword in text for keyword in medium_cost_keywords):
            budget_level = 'Medium'
            score = 0.6
        elif any(keyword in text for keyword in low_cost_keywords):
            budget_level = 'Low'
            score = 0.9
        else:
            budget_level = 'Medium'
            score = 0.6

        # Adjust based on current budget climate
        score *= (0.7 + self.political_context['budget_surplus'] * 0.6)

        # Store budget level in promise
        promise.budget_required = budget_level

        return min(score, 1.0)

    def _analyze_complexity(self, promise) -> float:
        """
        Analyze legislative/implementation complexity
        Higher score = simpler to implement
        """
        text = f"{promise.title} {promise.description}".lower()

        # Complexity indicators
        high_complexity = [
            'state legislature', 'constitutional', 'multi-year',
            'comprehensive reform', 'requires federal', 'overhaul'
        ]
        medium_complexity = [
            'city council', 'legislation', 'zoning', 'regulations',
            'multi-agency', 'partnership'
        ]
        low_complexity = [
            'executive order', 'directive', 'mayoral', 'appoint',
            'enforce existing', 'task force'
        ]

        if any(keyword in text for keyword in high_complexity):
            complexity_level = 'Complex'
            score = 0.3
        elif any(keyword in text for keyword in medium_complexity):
            complexity_level = 'Moderate'
            score = 0.65
        elif any(keyword in text for keyword in low_complexity):
            complexity_level = 'Simple'
            score = 0.95
        else:
            complexity_level = 'Moderate'
            score = 0.65

        promise.legislative_complexity = complexity_level

        return score

    def _analyze_political_alignment(self, promise) -> float:
        """
        Analyze alignment with current political climate
        """
        text = f"{promise.title} {promise.description}".lower()

        # Progressive policy indicators (likely to align with Mamdani)
        progressive_keywords = [
            'affordable housing', 'public housing', 'rent control',
            'green new deal', 'climate', 'medicare for all',
            'free transit', 'workers rights', 'union', 'tenant protection',
            'defund', 'police reform', 'social services', 'equity'
        ]

        # Conservative/moderate indicators (might face opposition)
        moderate_keywords = [
            'business tax', 'developer', 'private partnership',
            'market-based', 'public-private'
        ]

        progressive_score = sum(1 for keyword in progressive_keywords if keyword in text)
        moderate_score = sum(1 for keyword in moderate_keywords if keyword in text)

        # Base score on progressive alignment
        if progressive_score > moderate_score:
            base_score = 0.75 + (progressive_score * 0.05)
        elif moderate_score > progressive_score:
            base_score = 0.45 - (moderate_score * 0.05)
        else:
            base_score = 0.60

        # Adjust for political context
        score = base_score * self.political_context['city_council_progressive']

        promise.political_alignment = min(score, 1.0)

        return min(score, 1.0)

    def _analyze_public_support(self, promise) -> float:
        """
        Estimate public support based on promise type and current sentiment
        """
        text = f"{promise.title} {promise.description}".lower()

        # High public support issues in NYC
        high_support = [
            'affordable housing', 'rent', 'subway', 'transit',
            'climate', 'education', 'schools', 'parks',
            'healthcare', 'jobs'
        ]

        # Controversial issues
        controversial = [
            'defund police', 'sanctuary city', 'tax increase',
            'close rikers', 'supervised injection'
        ]

        support_count = sum(1 for keyword in high_support if keyword in text)
        controversy_count = sum(1 for keyword in controversial if keyword in text)

        if support_count > 0:
            score = 0.70 + (support_count * 0.08)
        elif controversy_count > 0:
            score = 0.50 - (controversy_count * 0.10)
        else:
            score = 0.60

        promise.public_support = min(score, 1.0)

        return min(score, 1.0)

    def _analyze_category_priority(self, promise) -> float:
        """
        Score based on category priority in current political climate
        """
        category = promise.category if promise.category else 'Other'

        if category in self.category_weights:
            weights = self.category_weights[category]
            score = (
                weights['political_priority'] * 0.5 +
                (1 - weights['budget_impact']) * 0.3 +
                (1 - weights['complexity']) * 0.2
            )
        else:
            score = 0.5

        return score

    def _generate_analysis_text(self, promise, likelihood_score, budget_score,
                                complexity_score, political_score,
                                public_support_score, category_score) -> str:
        """
        Generate human-readable analysis text
        """
        # Determine likelihood category
        if likelihood_score >= 0.75:
            likelihood_label = "Very Likely"
            confidence = "high confidence"
        elif likelihood_score >= 0.60:
            likelihood_label = "Likely"
            confidence = "moderate-high confidence"
        elif likelihood_score >= 0.45:
            likelihood_label = "Moderate Chance"
            confidence = "moderate confidence"
        elif likelihood_score >= 0.30:
            likelihood_label = "Unlikely"
            confidence = "moderate confidence"
        else:
            likelihood_label = "Very Unlikely"
            confidence = "high confidence"

        # Build analysis
        analysis = f"**{likelihood_label}** to be enacted ({confidence})\n\n"

        # Key factors
        analysis += "**Key Factors:**\n"

        # Budget
        if budget_score > 0.7:
            analysis += f"✓ Budget Feasibility: High (Score: {budget_score:.2f}) - {promise.budget_required} cost with current NYC budget climate\n"
        elif budget_score > 0.5:
            analysis += f"± Budget Feasibility: Moderate (Score: {budget_score:.2f}) - {promise.budget_required} cost may require budget negotiations\n"
        else:
            analysis += f"✗ Budget Feasibility: Low (Score: {budget_score:.2f}) - {promise.budget_required} cost presents significant fiscal challenges\n"

        # Complexity
        if complexity_score > 0.7:
            analysis += f"✓ Implementation Complexity: {promise.legislative_complexity} (Score: {complexity_score:.2f}) - Can likely be achieved through executive action\n"
        elif complexity_score > 0.5:
            analysis += f"± Implementation Complexity: {promise.legislative_complexity} (Score: {complexity_score:.2f}) - Requires council approval and coordination\n"
        else:
            analysis += f"✗ Implementation Complexity: {promise.legislative_complexity} (Score: {complexity_score:.2f}) - Requires state/federal cooperation\n"

        # Political alignment
        if political_score > 0.7:
            analysis += f"✓ Political Alignment: Strong (Score: {political_score:.2f}) - Aligns well with progressive council majority\n"
        elif political_score > 0.5:
            analysis += f"± Political Alignment: Moderate (Score: {political_score:.2f}) - May face some political resistance\n"
        else:
            analysis += f"✗ Political Alignment: Weak (Score: {political_score:.2f}) - Likely to face significant political opposition\n"

        # Public support
        if public_support_score > 0.7:
            analysis += f"✓ Public Support: High (Score: {public_support_score:.2f}) - Strong public backing expected\n"
        elif public_support_score > 0.5:
            analysis += f"± Public Support: Moderate (Score: {public_support_score:.2f}) - Mixed public opinion\n"
        else:
            analysis += f"✗ Public Support: Low (Score: {public_support_score:.2f}) - May face public opposition\n"

        return analysis

    def rank_all_promises(self, promises: List) -> List:
        """
        Rank all promises by likelihood score
        Returns sorted list of promises with rankings
        """
        # Sort by likelihood score (descending)
        sorted_promises = sorted(promises, key=lambda p: p.likelihood_score, reverse=True)

        # Assign ranks
        for idx, promise in enumerate(sorted_promises, 1):
            promise.likelihood_rank = idx

        return sorted_promises
