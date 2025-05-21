"""
Implementation of the MaterialsDatabase class.

This module provides the MaterialsDatabase class which manages a database of APIs
and polymers for use in ASD formulations.
"""

from typing import Dict, List, Optional, Union, Any
import logging
import os
import json
import pkg_resources


class MaterialsDatabase:
    """
    Manages a database of APIs and polymers.
    
    Attributes:
        apis (dict): Dictionary of API objects indexed by name
        polymers (dict): Dictionary of Polymer objects indexed by name
    """
    
    def __init__(self, database_path: Optional[str] = None) -> None:
        """
        Initialize a MaterialsDatabase object.
        
        Args:
            database_path (str, optional): Path to the database file
        """
        self.apis = {}
        self.polymers = {}
        
        # Load default databases
        self._load_default_apis()
        self._load_default_polymers()
        
        # Load custom database if provided
        if database_path:
            self.load_database(database_path)
    
    def _load_default_apis(self) -> None:
        """
        Load default API database from package data.
        """
        try:
            # Try to load from package data
            api_data_path = pkg_resources.resource_filename('asdii', 'data/common_apis.json')
            
            # If file exists, load it
            if os.path.exists(api_data_path):
                with open(api_data_path, 'r') as f:
                    api_data = json.load(f)
                    self.apis.update(api_data)
            else:
                # Use built-in data
                self.apis.update(self._get_builtin_apis())
                
        except Exception as e:
            logging.warning(f"Failed to load default API database: {e}")
            # Use built-in data as fallback
            self.apis.update(self._get_builtin_apis())
    
    def _load_default_polymers(self) -> None:
        """
        Load default polymer database from package data.
        """
        try:
            # Try to load from package data
            polymer_data_path = pkg_resources.resource_filename('asdii', 'data/common_polymers.json')
            
            # If file exists, load it
            if os.path.exists(polymer_data_path):
                with open(polymer_data_path, 'r') as f:
                    polymer_data = json.load(f)
                    self.polymers.update(polymer_data)
            else:
                # Use built-in data
                self.polymers.update(self._get_builtin_polymers())
                
        except Exception as e:
            logging.warning(f"Failed to load default polymer database: {e}")
            # Use built-in data as fallback
            self.polymers.update(self._get_builtin_polymers())
    
    def _get_builtin_apis(self) -> Dict[str, Dict[str, Any]]:
        """
        Get built-in API data.
        
        Returns:
            dict: Dictionary of API data
        """
        # This is a minimal set of common APIs with key properties
        # In a production implementation, this should be expanded
        
        return {
            'ibuprofen': {
                'smiles': 'CC(C)CC1=CC=C(C=C1)C(C)C(=O)O',
                'molecular_weight': 206.29,
                'melting_point': 76.0,
                'glass_transition_temp': -45.0,
                'log_p': 3.97,
                'solubility_parameters': {
                    'dispersive': 18.2,
                    'polar': 3.8,
                    'hydrogen': 8.0,
                    'total': 20.0
                }
            },
            'indomethacin': {
                'smiles': 'COC1=C(C=C2C(=C1)C(=O)OC2C3=CC=C(C=C3)Cl)CC(=O)O',
                'molecular_weight': 357.79,
                'melting_point': 162.0,
                'glass_transition_temp': 41.0,
                'log_p': 4.27,
                'solubility_parameters': {
                    'dispersive': 19.5,
                    'polar': 5.3,
                    'hydrogen': 9.8,
                    'total': 22.3
                }
            },
            'ketoconazole': {
                'smiles': 'CC(=O)N1CCN(CC1)C2=CC=C(C=C2)OCC3COC(O3)(CN4C=CN=C4)C5=C(C=C(C=C5)Cl)Cl',
                'molecular_weight': 531.43,
                'melting_point': 146.0,
                'glass_transition_temp': 45.0,
                'log_p': 4.20,
                'solubility_parameters': {
                    'dispersive': 18.8,
                    'polar': 7.2,
                    'hydrogen': 10.0,
                    'total': 22.6
                }
            },
            'felodipine': {
                'smiles': 'CCOC(=O)C1=C(NC(=C(C1C2=CC=CC=C2Cl)C(=O)OC)C)C',
                'molecular_weight': 384.26,
                'melting_point': 145.0,
                'glass_transition_temp': 43.0,
                'log_p': 3.86,
                'solubility_parameters': {
                    'dispersive': 19.1,
                    'polar': 7.8,
                    'hydrogen': 9.5,
                    'total': 22.7
                }
            },
            'griseofulvin': {
                'smiles': 'COC1=CC(=CC(=C1OC)OC)C2C(=O)CC3(C(=O)C=COC3=C2Cl)C',
                'molecular_weight': 352.77,
                'melting_point': 220.0,
                'glass_transition_temp': 89.0,
                'log_p': 2.18,
                'solubility_parameters': {
                    'dispersive': 18.5,
                    'polar': 5.5,
                    'hydrogen': 7.8,
                    'total': 20.8
                }
            }
        }
    
    def _get_builtin_polymers(self) -> Dict[str, Dict[str, Any]]:
        """
        Get built-in polymer data.
        
        Returns:
            dict: Dictionary of polymer data
        """
        # This is a minimal set of common polymers with key properties
        # In a production implementation, this should be expanded
        
        return {
            'PVP K30': {
                'type': 'vinyl',
                'monomer_smiles': 'C1CCNC(=O)C1',
                'molecular_weight': 50000,
                'glass_transition_temp': 149.0,
                'solubility_parameters': {
                    'dispersive': 17.0,
                    'polar': 8.0,
                    'hydrogen': 12.0,
                    'total': 22.2
                },
                'hydrophilicity': 0.85,
                'hygroscopicity': 0.80
            },
            'HPMC': {
                'type': 'cellulosic',
                'molecular_weight': 22000,
                'glass_transition_temp': 175.0,
                'solubility_parameters': {
                    'dispersive': 18.0,
                    'polar': 8.6,
                    'hydrogen': 11.9,
                    'total': 23.3
                },
                'hydrophilicity': 0.70,
                'hygroscopicity': 0.65
            },
            'HPMCAS': {
                'type': 'cellulosic',
                'molecular_weight': 18000,
                'glass_transition_temp': 120.0,
                'solubility_parameters': {
                    'dispersive': 18.5,
                    'polar': 9.5,
                    'hydrogen': 10.0,
                    'total': 23.0
                },
                'hydrophilicity': 0.60,
                'hygroscopicity': 0.50
            },
            'Soluplus': {
                'type': 'graft copolymer',
                'molecular_weight': 90000,
                'glass_transition_temp': 70.0,
                'solubility_parameters': {
                    'dispersive': 17.5,
                    'polar': 7.0,
                    'hydrogen': 9.0,
                    'total': 20.9
                },
                'hydrophilicity': 0.55,
                'hygroscopicity': 0.45
            },
            'Eudragit L100': {
                'type': 'acrylic',
                'molecular_weight': 125000,
                'glass_transition_temp': 150.0,
                'solubility_parameters': {
                    'dispersive': 16.8,
                    'polar': 9.0,
                    'hydrogen': 8.0,
                    'total': 20.6
                },
                'hydrophilicity': 0.50,
                'hygroscopicity': 0.40
            },
            'PVPVA 64': {
                'type': 'vinyl',
                'molecular_weight': 45000,
                'glass_transition_temp': 100.0,
                'solubility_parameters': {
                    'dispersive': 16.5,
                    'polar': 7.5,
                    'hydrogen': 10.5,
                    'total': 21.0
                },
                'hydrophilicity': 0.65,
                'hygroscopicity': 0.60
            },
            'PEG 6000': {
                'type': 'polyether',
                'monomer_smiles': 'C(CO)O',
                'molecular_weight': 6000,
                'glass_transition_temp': -20.0,
                'solubility_parameters': {
                    'dispersive': 17.0,
                    'polar': 3.0,
                    'hydrogen': 9.0,
                    'total': 19.4
                },
                'hydrophilicity': 0.90,
                'hygroscopicity': 0.85
            },
            'PVA': {
                'type': 'vinyl',
                'monomer_smiles': 'C(CO)O',
                'molecular_weight': 30000,
                'glass_transition_temp': 85.0,
                'solubility_parameters': {
                    'dispersive': 16.0,
                    'polar': 10.8,
                    'hydrogen': 17.6,
                    'total': 26.2
                },
                'hydrophilicity': 0.75,
                'hygroscopicity': 0.70
            }
        }
    
    def load_database(self, database_path: str) -> bool:
        """
        Load a database from a file.
        
        Args:
            database_path (str): Path to the database file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(database_path, 'r') as f:
                data = json.load(f)
                
                # Update APIs if present
                if 'apis' in data:
                    self.apis.update(data['apis'])
                
                # Update polymers if present
                if 'polymers' in data:
                    self.polymers.update(data['polymers'])
                
                return True
        except Exception as e:
            logging.error(f"Failed to load database from {database_path}: {e}")
            return False
    
    def save_database(self, database_path: Optional[str] = None) -> bool:
        """
        Save the database to a file.
        
        Args:
            database_path (str, optional): Path to the database file
            
        Returns:
            bool: True if successful, False otherwise
        """
        if database_path is None:
            # Use default path
            try:
                database_path = pkg_resources.resource_filename('asdii', 'data/custom_database.json')
            except Exception as e:
                logging.error(f"Failed to get default database path: {e}")
                return False
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(database_path), exist_ok=True)
            
            # Save database
            with open(database_path, 'w') as f:
                data = {
                    'apis': self.apis,
                    'polymers': self.polymers
                }
                json.dump(data, f, indent=2)
                
            return True
        except Exception as e:
            logging.error(f"Failed to save database to {database_path}: {e}")
            return False
    
    def add_api(self, name: str, api_data: Dict[str, Any]) -> bool:
        """
        Add an API to the database.
        
        Args:
            name (str): Name of the API
            api_data (dict): API data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate required fields
            required_fields = ['smiles', 'molecular_weight']
            for field in required_fields:
                if field not in api_data:
                    logging.error(f"Missing required field for API: {field}")
                    return False
            
            # Add API to database
            self.apis[name] = api_data
            
            return True
        except Exception as e:
            logging.error(f"Failed to add API {name}: {e}")
            return False
    
    def add_polymer(self, name: str, polymer_data: Dict[str, Any]) -> bool:
        """
        Add a polymer to the database.
        
        Args:
            name (str): Name of the polymer
            polymer_data (dict): Polymer data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate required fields
            required_fields = ['molecular_weight', 'glass_transition_temp']
            for field in required_fields:
                if field not in polymer_data:
                    logging.error(f"Missing required field for polymer: {field}")
                    return False
            
            # Add polymer to database
            self.polymers[name] = polymer_data
            
            return True
        except Exception as e:
            logging.error(f"Failed to add polymer {name}: {e}")
            return False
    
    def get_api(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get an API from the database by name.
        
        Args:
            name (str): Name of the API
            
        Returns:
            dict or None: API data if found, None otherwise
        """
        # Case-insensitive search
        for api_name, api_data in self.apis.items():
            if api_name.lower() == name.lower():
                return api_data
        
        return None
    
    def get_polymer(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a polymer from the database by name.
        
        Args:
            name (str): Name of the polymer
            
        Returns:
            dict or None: Polymer data if found, None otherwise
        """
        # Case-insensitive search
        for polymer_name, polymer_data in self.polymers.items():
            if polymer_name.lower() == name.lower():
                return polymer_data
        
        return None
    
    def search_apis(self, query: str) -> Dict[str, Dict[str, Any]]:
        """
        Search for APIs in the database.
        
        Args:
            query (str): Search query
            
        Returns:
            dict: Dictionary of matching API data
        """
        results = {}
        query_lower = query.lower()
        
        for name, data in self.apis.items():
            # Search in name
            if query_lower in name.lower():
                results[name] = data
                continue
            
            # Search in SMILES
            if 'smiles' in data and query_lower in data['smiles'].lower():
                results[name] = data
                continue
            
            # Advanced search in properties (simplified)
            # In a production implementation, this should be more sophisticated
            for key, value in data.items():
                if isinstance(value, str) and query_lower in value.lower():
                    results[name] = data
                    break
        
        return results
    
    def search_polymers(self, query: str) -> Dict[str, Dict[str, Any]]:
        """
        Search for polymers in the database.
        
        Args:
            query (str): Search query
            
        Returns:
            dict: Dictionary of matching polymer data
        """
        results = {}
        query_lower = query.lower()
        
        for name, data in self.polymers.items():
            # Search in name
            if query_lower in name.lower():
                results[name] = data
                continue
            
            # Search in type
            if 'type' in data and query_lower in data['type'].lower():
                results[name] = data
                continue
            
            # Advanced search in properties (simplified)
            # In a production implementation, this should be more sophisticated
            for key, value in data.items():
                if isinstance(value, str) and query_lower in value.lower():
                    results[name] = data
                    break
        
        return results
    
    def get_common_polymers(self) -> Dict[str, Dict[str, Any]]:
        """
        Get a dictionary of common polymers used in ASD formulations.
        
        Returns:
            dict: Dictionary of polymer data
        """
        return self.polymers
    
    def __str__(self) -> str:
        """Return a string representation of the MaterialsDatabase object."""
        return f"MaterialsDatabase(APIs: {len(self.apis)}, Polymers: {len(self.polymers)})"