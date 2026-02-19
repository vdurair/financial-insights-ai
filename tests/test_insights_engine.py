"""
Unit tests for insights engine module.
"""

import unittest
import pandas as pd
import sys
sys.path.insert(0, '../src')

from insights_engine import InsightsEngine


class TestInsightsEngine(unittest.TestCase):
    """Test cases for insights engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'amount': [1500.0, -50.0, -100.0],
            'category': ['Income', 'Food & Dining', 'Utilities'],
            'description': ['Salary', 'Restaurant', 'Electric Bill']
        })
        self.engine = InsightsEngine(self.df)
    
    def test_get_summary_statistics(self):
        """Test summary statistics calculation."""
        stats = self.engine.get_summary_statistics()
        self.assertEqual(stats['total_income'], 1500.0)
        self.assertEqual(stats['total_expenses'], 150.0)
        self.assertEqual(stats['net_flow'], 1350.0)
    
    def test_get_category_breakdown(self):
        """Test category breakdown calculation."""
        breakdown = self.engine.get_category_breakdown()
        self.assertIn('Food & Dining', breakdown)
        self.assertIn('Utilities', breakdown)
    
    def test_get_top_transactions(self):
        """Test getting top transactions."""
        top = self.engine.get_top_transactions(n=2)
        self.assertEqual(len(top), 2)
        self.assertEqual(top.iloc[0]['amount'], 1500.0)
    
    def test_get_insights_returns_list(self):
        """Test that insights are returned as a list."""
        insights = self.engine.get_insights()
        self.assertIsInstance(insights, list)
        self.assertTrue(len(insights) > 0)


if __name__ == '__main__':
    unittest.main()
