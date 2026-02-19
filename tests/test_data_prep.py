"""
Unit tests for data preparation module.
"""

import unittest
import pandas as pd
import sys
sys.path.insert(0, '../src')

from data_prep import clean_data, prepare_features


class TestDataPrep(unittest.TestCase):
    """Test cases for data preparation functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02', '2024-01-02'],
            'amount': [100.0, -50.0, -50.0],
            'description': ['Salary', 'Food', 'Food'],
            'category': ['Income', 'Food & Dining', 'Food & Dining']
        })
    
    def test_clean_data_removes_duplicates(self):
        """Test that clean_data removes duplicate rows."""
        cleaned = clean_data(self.df)
        self.assertEqual(len(cleaned), 2)
    
    def test_clean_data_converts_date(self):
        """Test that clean_data converts date to datetime."""
        cleaned = clean_data(self.df)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(cleaned['date']))
    
    def test_prepare_features_adds_time_features(self):
        """Test that prepare_features adds time-based features."""
        df_prepared, features = prepare_features(self.df)
        self.assertIn('month', features)
        self.assertIn('day_of_week', features)
    
    def test_prepare_features_adds_amount_features(self):
        """Test that prepare_features adds amount-based features."""
        df_prepared, features = prepare_features(self.df)
        self.assertIn('amount', features)
        self.assertIn('amount_abs', features)


if __name__ == '__main__':
    unittest.main()
