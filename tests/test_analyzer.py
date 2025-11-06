"""
Test module for the analyzer component.

This is a skeleton for testing the promise analysis logic.
"""
import unittest
from mamdani_tracker.analyzer import analyze_promise, clamp, update_promise_scores


class TestAnalyzer(unittest.TestCase):
    """Test cases for the analyzer module."""
    
    def test_clamp_within_range(self):
        """Test that clamp keeps values within specified range."""
        self.assertEqual(clamp(0.5), 0.5)
        self.assertEqual(clamp(0.0), 0.0)
        self.assertEqual(clamp(1.0), 1.0)
    
    def test_clamp_above_range(self):
        """Test that clamp caps values above max."""
        self.assertEqual(clamp(1.5), 1.0)
        self.assertEqual(clamp(2.0), 1.0)
    
    def test_clamp_below_range(self):
        """Test that clamp raises values below min."""
        self.assertEqual(clamp(-0.5), 0.0)
        self.assertEqual(clamp(-1.0), 0.0)
    
    def test_analyze_promise_returns_dict(self):
        """Test that analyze_promise returns a dictionary."""
        promise_data = {
            'title': 'Test promise',
            'description': 'This is a test',
            'category': 'test'
        }
        result = analyze_promise(promise_data)
        
        self.assertIsInstance(result, dict)
        self.assertIn('feasibility_score', result)
        self.assertIn('impact_score', result)
        self.assertIn('priority_score', result)
        self.assertIn('budget_required', result)
        self.assertIn('legislative_complexity', result)
    
    def test_analyze_promise_scores_in_range(self):
        """Test that all scores are within valid ranges."""
        promise_data = {
            'title': 'Universal healthcare for all citizens',
            'description': 'Comprehensive reform to provide healthcare',
            'category': 'healthcare'
        }
        result = analyze_promise(promise_data)
        
        # Check all scores are between 0 and 1
        self.assertGreaterEqual(result['feasibility_score'], 0.0)
        self.assertLessEqual(result['feasibility_score'], 1.0)
        
        self.assertGreaterEqual(result['impact_score'], 0.0)
        self.assertLessEqual(result['impact_score'], 1.0)
        
        self.assertGreaterEqual(result['priority_score'], 0.0)
        self.assertLessEqual(result['priority_score'], 1.0)
        
        self.assertGreaterEqual(result['legislative_complexity'], 0.0)
        self.assertLessEqual(result['legislative_complexity'], 1.0)
        
        # Budget can be > 1 but should never be negative
        self.assertGreaterEqual(result['budget_required'], 0.0)
    
    def test_analyze_promise_budget_never_negative(self):
        """Test that budget is never negative."""
        promise_data = {
            'title': 'Simple promise',
            'description': 'No budget keywords',
            'category': 'other'
        }
        result = analyze_promise(promise_data)
        
        self.assertGreaterEqual(result['budget_required'], 0.0)
    
    def test_analyze_promise_empty_data(self):
        """Test analyzer handles empty data gracefully."""
        promise_data = {}
        result = analyze_promise(promise_data)
        
        # Should return defaults without crashing
        self.assertIsInstance(result, dict)
        self.assertGreaterEqual(result['feasibility_score'], 0.0)
        self.assertLessEqual(result['feasibility_score'], 1.0)


class TestPromiseScoreUpdate(unittest.TestCase):
    """Test cases for updating promise scores."""
    
    def test_update_promise_scores_mock(self):
        """Test updating promise scores with a mock object."""
        # Create a mock promise object
        class MockPromise:
            def __init__(self):
                self.id = 1
                self.title = 'Test promise'
                self.description = 'Test description'
                self.category = 'test'
                self.feasibility_score = 0.0
                self.impact_score = 0.0
                self.priority_score = 0.0
                self.budget_required = 0.0
                self.legislative_complexity = 0.0
        
        mock_promise = MockPromise()
        update_promise_scores(mock_promise)
        
        # Verify scores were updated
        self.assertGreater(mock_promise.feasibility_score, 0.0)
        self.assertGreater(mock_promise.impact_score, 0.0)
        self.assertGreater(mock_promise.priority_score, 0.0)


if __name__ == '__main__':
    unittest.main()
