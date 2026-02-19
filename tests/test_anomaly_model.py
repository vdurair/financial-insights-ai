"""
Unit tests for anomaly detection module.
"""

import unittest
import numpy as np
import sys
sys.path.insert(0, '../src')

from anomaly_model import AnomalyDetector


class TestAnomalyDetector(unittest.TestCase):
    """Test cases for anomaly detection model."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create synthetic data with some outliers
        normal_data = np.random.normal(100, 20, (100, 1))
        outliers = np.array([[500], [600], [700]])
        self.X_train = np.vstack([normal_data, outliers])
        
        self.detector = AnomalyDetector(contamination=0.05)
    
    def test_fit_model(self):
        """Test that model can be fitted."""
        self.detector.fit(self.X_train)
        self.assertTrue(self.detector.is_fitted)
    
    def test_predict_before_fit_raises_error(self):
        """Test that prediction before fitting raises error."""
        with self.assertRaises(ValueError):
            self.detector.predict(self.X_train)
    
    def test_predict_returns_correct_shape(self):
        """Test that predictions have correct shape."""
        self.detector.fit(self.X_train)
        predictions = self.detector.predict(self.X_train)
        self.assertEqual(predictions.shape[0], self.X_train.shape[0])
    
    def test_anomaly_scores_shape(self):
        """Test that anomaly scores have correct shape."""
        self.detector.fit(self.X_train)
        scores = self.detector.get_anomaly_scores(self.X_train)
        self.assertEqual(scores.shape[0], self.X_train.shape[0])
    
    def test_fit_predict(self):
        """Test fit_predict method."""
        predictions = self.detector.fit_predict(self.X_train)
        self.assertEqual(predictions.shape[0], self.X_train.shape[0])
        self.assertTrue(self.detector.is_fitted)


if __name__ == '__main__':
    unittest.main()
