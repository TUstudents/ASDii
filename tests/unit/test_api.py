"""
Unit tests for the API class.
"""

import unittest
import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from asdii.core.api import API


class TestAPI(unittest.TestCase):
    """Test cases for the API class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock RDKit Mol object
        self.mock_mol = MagicMock()
        
        # Create an API object with mock mol
        self.api = API(
            name="Test API",
            smiles="C1=CC=CC=C1",
            mol=self.mock_mol,
            molecular_weight=100.0,
            melting_point=150.0,
            glass_transition_temp=50.0,
            log_p=2.5,
            solubility_parameters={
                'dispersive': 18.0,
                'polar': 4.0,
                'hydrogen': 6.0,
                'total': 19.5
            }
        )
    
    def test_init(self):
        """Test the initialization of API objects."""
        # Test with all parameters
        self.assertEqual(self.api.name, "Test API")
        self.assertEqual(self.api.smiles, "C1=CC=CC=C1")
        self.assertEqual(self.api.mol, self.mock_mol)
        self.assertEqual(self.api.molecular_weight, 100.0)
        self.assertEqual(self.api.melting_point, 150.0)
        self.assertEqual(self.api.glass_transition_temp, 50.0)
        self.assertEqual(self.api.log_p, 2.5)
        self.assertEqual(self.api.solubility_parameters['dispersive'], 18.0)
        self.assertEqual(self.api.solubility_parameters['polar'], 4.0)
        self.assertEqual(self.api.solubility_parameters['hydrogen'], 6.0)
        self.assertEqual(self.api.solubility_parameters['total'], 19.5)
        
        # Test with minimal parameters
        api_minimal = API(name="Minimal API")
        self.assertEqual(api_minimal.name, "Minimal API")
        self.assertIsNone(api_minimal.smiles)
        self.assertIsNone(api_minimal.mol)
        self.assertIsNone(api_minimal.molecular_weight)
        self.assertIsNone(api_minimal.melting_point)
        self.assertIsNone(api_minimal.glass_transition_temp)
        self.assertIsNone(api_minimal.log_p)
        self.assertEqual(api_minimal.solubility_parameters, {})
    
    @patch('asdii.core.api.Chem')
    def test_from_smiles(self, mock_chem):
        """Test creating an API from a SMILES string."""
        # Set up mock
        mock_mol = MagicMock()
        mock_chem.MolFromSmiles.return_value = mock_mol
        mock_chem.MolToSmiles.return_value = "C1=CC=CC=C1"
        
        # Test with name
        api = API.from_smiles("C1=CC=CC=C1", name="Benzene")
        self.assertEqual(api.name, "Benzene")
        self.assertEqual(api.smiles, "C1=CC=CC=C1")
        self.assertEqual(api.mol, mock_mol)
        
        # Test without name
        api = API.from_smiles("C1=CC=CC=C1")
        self.assertEqual(api.name, "C1=CC=CC=C1")
        self.assertEqual(api.smiles, "C1=CC=CC=C1")
        self.assertEqual(api.mol, mock_mol)
        
        # Test invalid SMILES
        mock_chem.MolFromSmiles.return_value = None
        with self.assertRaises(ValueError):
            API.from_smiles("invalid_smiles")
    
    @patch('asdii.core.api.Chem')
    def test_from_mol(self, mock_chem):
        """Test creating an API from a Mol object."""
        # Set up mock
        mock_mol = MagicMock()
        mock_chem.MolToSmiles.return_value = "C1=CC=CC=C1"
        
        # Test with name
        api = API.from_mol(mock_mol, name="Benzene")
        self.assertEqual(api.name, "Benzene")
        self.assertEqual(api.smiles, "C1=CC=CC=C1")
        self.assertEqual(api.mol, mock_mol)
        
        # Test without name
        api = API.from_mol(mock_mol)
        self.assertEqual(api.name, "C1=CC=CC=C1")
        self.assertEqual(api.smiles, "C1=CC=CC=C1")
        self.assertEqual(api.mol, mock_mol)
    
    @patch('asdii.core.api.MaterialsDatabase')
    def test_from_name(self, mock_db_class):
        """Test creating an API from a name."""
        # Set up mock
        mock_db = MagicMock()
        mock_db_class.return_value = mock_db
        mock_db.get_api.return_value = {
            'smiles': "C1=CC=CC=C1",
            'molecular_weight': 78.11,
            'melting_point': 5.5,
            'glass_transition_temp': -35.0,
            'log_p': 2.13,
            'solubility_parameters': {
                'dispersive': 18.0,
                'polar': 0.0,
                'hydrogen': 2.0,
                'total': 18.1
            }
        }
        
        # Test existing API
        api = API.from_name("Benzene")
        self.assertEqual(api.name, "Benzene")
        self.assertEqual(api.smiles, "C1=CC=CC=C1")
        self.assertEqual(api.molecular_weight, 78.11)
        self.assertEqual(api.melting_point, 5.5)
        self.assertEqual(api.glass_transition_temp, -35.0)
        self.assertEqual(api.log_p, 2.13)
        self.assertEqual(api.solubility_parameters['dispersive'], 18.0)
        
        # Test non-existing API
        mock_db.get_api.return_value = None
        with self.assertRaises(ValueError):
            API.from_name("NonExistingAPI")
    
    @patch('asdii.core.api.Descriptors')
    @patch('asdii.core.api.Lipinski')
    def test_calculate_missing_properties(self, mock_lipinski, mock_descriptors):
        """Test calculating missing properties."""
        # Set up mocks
        mock_descriptors.MolWt.return_value = 78.11
        mock_descriptors.MolLogP.return_value = 2.13
        mock_lipinski.NumHDonors.return_value = 0
        mock_lipinski.NumHAcceptors.return_value = 0
        mock_descriptors.NumRotatableBonds.return_value = 0
        
        # Create API with missing properties
        api = API(
            name="TestAPI",
            smiles="C1=CC=CC=C1",
            mol=self.mock_mol
        )
        
        # Call method
        api._calculate_missing_properties()
        
        # Check properties
        self.assertEqual(api.molecular_weight, 78.11)
        self.assertEqual(api.log_p, 2.13)
        self.assertEqual(api.h_bond_donors, 0)
        self.assertEqual(api.h_bond_acceptors, 0)
        self.assertEqual(api.rotatable_bonds, 0)
    
    @patch('asdii.core.api.calculate_solubility_parameters')
    def test_calculate_solubility_parameters(self, mock_calc):
        """Test calculating solubility parameters."""
        # Set up mock
        mock_calc.return_value = {
            'dispersive': 18.0,
            'polar': 0.0,
            'hydrogen': 2.0,
            'total': 18.1
        }
        
        # Call method
        params = self.api.calculate_solubility_parameters()
        
        # Check result
        self.assertEqual(params['dispersive'], 18.0)
        self.assertEqual(params['polar'], 0.0)
        self.assertEqual(params['hydrogen'], 2.0)
        self.assertEqual(params['total'], 18.1)
        
        # Check that the object was updated
        self.assertEqual(self.api.solubility_parameters['dispersive'], 18.0)
        self.assertEqual(self.api.solubility_parameters['polar'], 0.0)
        self.assertEqual(self.api.solubility_parameters['hydrogen'], 2.0)
        self.assertEqual(self.api.solubility_parameters['total'], 18.1)
        
        # Test without mol
        api_no_mol = API(name="No Mol")
        with self.assertRaises(ValueError):
            api_no_mol.calculate_solubility_parameters()
    
    def test_predict_amorphization_tendency(self):
        """Test predicting amorphization tendency."""
        # Test with all required properties
        tendency = self.api.predict_amorphization_tendency()
        self.assertIsInstance(tendency, float)
        self.assertTrue(0.0 <= tendency <= 1.0)
        
        # Test with missing properties
        api_missing = API(name="Missing")
        with self.assertRaises(ValueError):
            api_missing.predict_amorphization_tendency()
    
    def test_str_and_repr(self):
        """Test string representation."""
        # Test __str__
        str_rep = str(self.api)
        self.assertIn("Test API", str_rep)
        self.assertIn("100.00", str_rep)  # MW
        self.assertIn("150.0", str_rep)   # MP
        self.assertIn("50.0", str_rep)    # Tg
        self.assertIn("2.50", str_rep)    # LogP
        
        # Test __repr__
        repr_rep = repr(self.api)
        self.assertIn("API(", repr_rep)
        self.assertIn("Test API", repr_rep)
        self.assertIn("C1=CC=CC=C1", repr_rep)


if __name__ == '__main__':
    unittest.main()