"""
Unit tests for the analyzer module.

These tests verify that the analyzer correctly calculates scores
and clamps them to the [0.0, 1.0] range.
"""
import unittest
from mamdani_tracker.analyzer import (
    clamp,
    calculate_priority_score,
    calculate_feasibility_score,
    calculate_impact_score,
    calculate_urgency_score,
    calculate_overall_score
)


class TestAnalyzerFunctions(unittest.TestCase):
    """Test cases for analyzer score calculation functions."""
    
    def test_clamp_within_range(self):
        """Test that clamp keeps values within [0, 1]."""
        self.assertEqual(clamp(0.5), 0.5)
        self.assertEqual(clamp(0.0), 0.0)
        self.assertEqual(clamp(1.0), 1.0)
    
    def test_clamp_below_range(self):
        """Test that clamp raises values below 0 to 0."""
        self.assertEqual(clamp(-0.5), 0.0)
        self.assertEqual(clamp(-100), 0.0)
    
    def test_clamp_above_range(self):
        """Test that clamp lowers values above 1 to 1."""
        self.assertEqual(clamp(1.5), 1.0)
        self.assertEqual(clamp(100), 1.0)
    
    def test_priority_score_range(self):
        """Test that priority scores are always in [0, 1]."""
        # High public interest, low budget = high priority
        score1 = calculate_priority_score(10, 10.0)
        self.assertGreaterEqual(score1, 0.0)
        self.assertLessEqual(score1, 1.0)
        
        # Low public interest, high budget = low priority
        score2 = calculate_priority_score(1, 1000.0)
        self.assertGreaterEqual(score2, 0.0)
        self.assertLessEqual(score2, 1.0)
        
        # Medium values
        score3 = calculate_priority_score(5, 100.0)
        self.assertGreaterEqual(score3, 0.0)
        self.assertLessEqual(score3, 1.0)
    
    def test_feasibility_score_range(self):
        """Test that feasibility scores are always in [0, 1]."""
        # Low budget, low complexity = high feasibility
        score1 = calculate_feasibility_score(10.0, 1)
        self.assertGreaterEqual(score1, 0.0)
        self.assertLessEqual(score1, 1.0)
        
        # High budget, high complexity = low feasibility
        score2 = calculate_feasibility_score(1000.0, 5)
        self.assertGreaterEqual(score2, 0.0)
        self.assertLessEqual(score2, 1.0)
        
        # Medium values
        score3 = calculate_feasibility_score(100.0, 3)
        self.assertGreaterEqual(score3, 0.0)
        self.assertLessEqual(score3, 1.0)
    
    def test_impact_score_range(self):
        """Test that impact scores are always in [0, 1]."""
        # High public interest, significant budget = high impact
        score1 = calculate_impact_score(10, 500.0)
        self.assertGreaterEqual(score1, 0.0)
        self.assertLessEqual(score1, 1.0)
        
        # Low public interest, minimal budget = low impact
        score2 = calculate_impact_score(1, 1.0)
        self.assertGreaterEqual(score2, 0.0)
        self.assertLessEqual(score2, 1.0)
        
        # Medium values
        score3 = calculate_impact_score(5, 100.0)
        self.assertGreaterEqual(score3, 0.0)
        self.assertLessEqual(score3, 1.0)
    
    def test_urgency_score_range(self):
        """Test that urgency scores are always in [0, 1]."""
        # No deadline
        score1 = calculate_urgency_score(None)
        self.assertGreaterEqual(score1, 0.0)
        self.assertLessEqual(score1, 1.0)
        
        # Immediate deadline
        score2 = calculate_urgency_score(0)
        self.assertGreaterEqual(score2, 0.0)
        self.assertLessEqual(score2, 1.0)
        
        # Near deadline (30 days)
        score3 = calculate_urgency_score(30)
        self.assertGreaterEqual(score3, 0.0)
        self.assertLessEqual(score3, 1.0)
        
        # Far deadline (1 year)
        score4 = calculate_urgency_score(365)
        self.assertGreaterEqual(score4, 0.0)
        self.assertLessEqual(score4, 1.0)
        
        # Very far deadline
        score5 = calculate_urgency_score(1000)
        self.assertGreaterEqual(score5, 0.0)
        self.assertLessEqual(score5, 1.0)
    
    def test_overall_score_range(self):
        """Test that overall scores are always in [0, 1]."""
        # All high scores
        score1 = calculate_overall_score(0.9, 0.9, 0.9, 0.9)
        self.assertGreaterEqual(score1, 0.0)
        self.assertLessEqual(score1, 1.0)
        
        # All low scores
        score2 = calculate_overall_score(0.1, 0.1, 0.1, 0.1)
        self.assertGreaterEqual(score2, 0.0)
        self.assertLessEqual(score2, 1.0)
        
        # Mixed scores
        score3 = calculate_overall_score(0.8, 0.3, 0.6, 0.4)
        self.assertGreaterEqual(score3, 0.0)
        self.assertLessEqual(score3, 1.0)
    
    def test_overall_score_weighted_average(self):
        """Test that overall score is a weighted average."""
        # All equal scores should produce that score
        score = calculate_overall_score(0.5, 0.5, 0.5, 0.5)
        self.assertAlmostEqual(score, 0.5, places=2)
    
    def test_edge_cases(self):
        """Test edge cases and extreme values."""
        # Zero budget
        score1 = calculate_priority_score(5, 0.0)
        self.assertGreaterEqual(score1, 0.0)
        self.assertLessEqual(score1, 1.0)
        
        # Very high budget
        score2 = calculate_feasibility_score(10000.0, 3)
        self.assertGreaterEqual(score2, 0.0)
        self.assertLessEqual(score2, 1.0)
        
        # Negative deadline (already passed)
        score3 = calculate_urgency_score(-10)
        self.assertGreaterEqual(score3, 0.0)
        self.assertLessEqual(score3, 1.0)


if __name__ == '__main__':
    unittest.main()
