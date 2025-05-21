"""
Unit tests for the ASDFormulation class.
"""

import unittest
import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from asdii.core.api import API
from asdii.core.polymer import Polymer
from asdii.core.formulation import ASDFormulation


class TestASDFormulation(unittest.TestCase):
    """Test cases for the ASDFormulation class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock API and polymer
        self.mock_api = MagicMock(spec=API)
        self.mock_api.name = "Test API"
        self.mock_api.glass_transition_temp = 50.0
        self.mock_api.melting_point = 150.0
        self.mock_api.solubility_parameters = {
            'dispersive': 18.0,
            'polar': 4.0,
            'hydrogen': 6.0,
            'total': 19.5
        }
        
        self.mock_polymer = MagicMock(spec=Polymer)
        self.mock_polymer.name = "Test Polymer"
        self.mock_polymer.glass_transition_temp = 120.0
        self.mock_polymer.solubility_parameters = {
            'dispersive': 17.0,
            'polar': 8.0,
            'hydrogen': 10.0,
            'total': 21.2
        }
        self.mock_polymer.hygroscopicity = 0.5
        
        # Create a formulation
        self.formulation = ASDFormulation(
            api=self.mock_api,
            polymer=self.mock_polymer,
            drug_loading=0.3,
            process_method="hot_melt_extrusion",
            temperature=180.0,
            screw_speed=100.0
        )
    
    def test_init(self):
        """Test the initialization of ASDFormulation objects."""
        # Test with all parameters
        self.assertEqual(self.formulation.api, self.mock_api)
        self.assertEqual(self.formulation.polymer, self.mock_polymer)
        self.assertEqual(self.formulation.drug_loading, 0.3)
        self.assertEqual(self.formulation.process_method, "hot_melt_extrusion")
        self.assertEqual(self.formulation.process_parameters['temperature'], 180.0)
        self.assertEqual(self.formulation.process_parameters['screw_speed'], 100.0)
        
        # Test with invalid drug loading
        with self.assertRaises(ValueError):
            ASDFormulation(
                api=self.mock_api,
                polymer=self.mock_polymer,
                drug_loading=1.5
            )
    
    @patch('asdii.core.formulation.predict_glass_transition')
    def test_predict_glass_transition_temp(self, mock_predict):
        """Test predicting glass transition temperature."""
        # Set up mock
        mock_predict.return_value = 95.0
        
        # Call method
        tg = self.formulation.predict_glass_transition_temp()
        
        # Check result
        self.assertEqual(tg, 95.0)
        
        # Check that mock was called with correct arguments
        mock_predict.assert_called_once_with(
            self.mock_api.glass_transition_temp,
            self.mock_polymer.glass_transition_temp,
            0.3,
            method='gordon_taylor'
        )
        
        # Check that the object was updated
        self.assertEqual(self.formulation.predicted_tg, 95.0)
        
        # Test with missing properties
        self.mock_api.glass_transition_temp = None
        with self.assertRaises(ValueError):
            self.formulation.predict_glass_transition_temp()
    
    def test_predict_miscibility(self):
        """Test predicting miscibility."""
        # Call method
        miscibility = self.formulation.predict_miscibility()
        
        # Check result is in range 0-1
        self.assertIsInstance(miscibility, float)
        self.assertTrue(0.0 <= miscibility <= 1.0)
        
        # Check that the object was updated
        self.assertEqual(self.formulation.predicted_miscibility, miscibility)
        
        # Test with missing solubility parameters
        original_params = self.mock_api.solubility_parameters
        self.mock_api.solubility_parameters = {}
        with self.assertRaises(ValueError):
            self.formulation.predict_miscibility()
        
        # Restore original parameters
        self.mock_api.solubility_parameters = original_params
    
    def test_predict_stability(self):
        """Test predicting stability."""
        # Make sure predicted_tg and predicted_miscibility are set
        self.formulation.predicted_tg = 95.0
        self.formulation.predicted_miscibility = 0.8
        
        # Call method
        stability = self.formulation.predict_stability()
        
        # Check result structure
        self.assertIsInstance(stability, dict)
        self.assertIn('score', stability)
        self.assertIn('thermodynamic', stability)
        self.assertIn('kinetic', stability)
        self.assertIn('major_factors', stability)
        self.assertIn('shelf_life_estimate', stability)
        
        # Check that values are in range 0-1
        self.assertTrue(0.0 <= stability['score'] <= 1.0)
        self.assertTrue(0.0 <= stability['thermodynamic'] <= 1.0)
        self.assertTrue(0.0 <= stability['kinetic'] <= 1.0)
        
        # Check that major_factors is a list
        self.assertIsInstance(stability['major_factors'], list)
    
    def test_predict_dissolution_profile(self):
        """Test predicting dissolution profile."""
        # Call method
        time_points, dissolution = self.formulation.predict_dissolution_profile()
        
        # Check result structure
        self.assertIsInstance(time_points, list)
        self.assertIsInstance(dissolution, list)
        self.assertEqual(len(time_points), len(dissolution))
        
        # Check that dissolution values are in range 0-100
        for value in dissolution:
            self.assertTrue(0.0 <= value <= 100.0)
    
    def test_optimize_drug_loading(self):
        """Test optimizing drug loading."""
        # Call method
        optimal_loading = self.formulation.optimize_drug_loading()
        
        # Check result is in range 0-1
        self.assertIsInstance(optimal_loading, float)
        self.assertTrue(0.0 <= optimal_loading <= 1.0)
    
    def test_optimize_process_parameters(self):
        """Test optimizing process parameters."""
        # Call method
        optimal_params = self.formulation.optimize_process_parameters()
        
        # Check result structure
        self.assertIsInstance(optimal_params, dict)
        self.assertIn('temperature', optimal_params)
        self.assertIn('screw_speed', optimal_params)
        self.assertIn('residence_time', optimal_params)
        
        # Test without process_method
        self.formulation.process_method = None
        with self.assertRaises(ValueError):
            self.formulation.optimize_process_parameters()
    
    def test_generate_report(self):
        """Test generating a report."""
        # Make sure predicted_tg, predicted_miscibility, and predicted_stability are set
        self.formulation.predicted_tg = 95.0
        self.formulation.predicted_miscibility = 0.8
        self.formulation.predicted_stability = {
            'score': 0.75,
            'thermodynamic': 0.8,
            'kinetic': 0.7,
            'shelf_life_estimate': 24,
            'major_factors': [
                ('Glass transition temperature', 0.8),
                ('API-polymer miscibility', 0.8),
                ('Drug loading', 0.7)
            ]
        }
        
        # Test markdown format
        report_md = self.formulation.generate_report(format='markdown')
        self.assertIsInstance(report_md, str)
        self.assertIn("# ASD Formulation Report", report_md)
        self.assertIn("Test API", report_md)
        self.assertIn("Test Polymer", report_md)
        
        # Test JSON format
        report_json = self.formulation.generate_report(format='json')
        self.assertIsInstance(report_json, dict)
        self.assertIn('formulation', report_json)
        self.assertIn('api', report_json)
        self.assertIn('polymer', report_json)
        self.assertIn('stability', report_json)
    
    def test_str_and_repr(self):
        """Test string representation."""
        # Make sure predicted_stability is set
        self.formulation.predicted_stability = {
            'score': 0.75,
            'thermodynamic': 0.8,
            'kinetic': 0.7,
            'shelf_life_estimate': 24,
            'major_factors': [
                ('Glass transition temperature', 0.8),
                ('API-polymer miscibility', 0.8),
                ('Drug loading', 0.7)
            ]
        }
        
        # Test __str__
        str_rep = str(self.formulation)
        self.assertIn("Test API", str_rep)
        self.assertIn("30.0%", str_rep)  # Drug loading
        self.assertIn("Test Polymer", str_rep)
        self.assertIn("hot_melt_extrusion", str_rep)
        self.assertIn("0.75", str_rep)  # Stability
        
        # Test __repr__
        repr_rep = repr(self.formulation)
        self.assertIn("ASDFormulation(", repr_rep)
        self.assertIn("Test API", repr_rep)
        self.assertIn("Test Polymer", repr_rep)
        self.assertIn("0.30", repr_rep)  # Drug loading
        self.assertIn("process='hot_melt_extrusion'", repr_rep)


if __name__ == '__main__':
    unittest.main()