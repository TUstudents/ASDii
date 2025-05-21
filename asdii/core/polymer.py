"""
Implementation of the Polymer class.

This module provides the Polymer class which represents a polymer used as a carrier
in an amorphous solid dispersion formulation.
"""

from typing import Dict, List, Optional, Union, Any
import logging
import numpy as np

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, AllChem
except ImportError:
    logging.warning("RDKit not found. Some Polymer functionality will be limited.")
    Chem = None
    Descriptors = None
    AllChem = None

from asdii.database.materials_db import MaterialsDatabase
from asdii.calculators.solubility import calculate_solubility_parameters


class Polymer:
    """
    Represents a polymer used as a carrier in an ASD formulation.
    
    Attributes:
        name (str): Name of the polymer
        type (str): Type/class of the polymer (e.g., 'cellulosic', 'vinyl')
        molecular_weight (float): Average molecular weight in g/mol
        glass_transition_temp (float): Glass transition temperature in Celsius
        solubility_parameters (dict): Hansen solubility parameters
        functional_groups (dict): Dictionary of functional groups and their counts
        monomer_smiles (str): SMILES representation of the monomer structure
        monomer_mol (rdkit.Chem.Mol): RDKit molecule object of the monomer
        hydrophilicity (float): Measure of hydrophilicity (0-1)
        hygroscopicity (float): Measure of hygroscopicity (0-1)
        descriptors (dict): Dictionary of polymer descriptors
    """
    
    def __init__(
        self, 
        name: str, 
        type: Optional[str] = None, 
        monomer_smiles: Optional[str] = None, 
        **properties: Dict[str, Any]
    ) -> None:
        """
        Initialize a Polymer object.
        
        Args:
            name (str): Name of the polymer
            type (str, optional): Type/class of the polymer
            monomer_smiles (str, optional): SMILES representation of the monomer
            **properties: Additional properties of the polymer
                molecular_weight (float): Average molecular weight in g/mol
                glass_transition_temp (float): Glass transition temperature in Celsius
                solubility_parameters (dict): Hansen solubility parameters
                functional_groups (dict): Dictionary of functional groups and their counts
                hydrophilicity (float): Measure of hydrophilicity (0-1)
                hygroscopicity (float): Measure of hygroscopicity (0-1)
                descriptors (dict): Dictionary of polymer descriptors
        """
        self.name = name
        self.type = type
        self.monomer_smiles = monomer_smiles
        self.monomer_mol = None
        
        # Initialize properties
        self.molecular_weight = properties.get('molecular_weight', None)
        self.glass_transition_temp = properties.get('glass_transition_temp', None)
        self.solubility_parameters = properties.get('solubility_parameters', {})
        self.functional_groups = properties.get('functional_groups', {})
        self.hydrophilicity = properties.get('hydrophilicity', None)
        self.hygroscopicity = properties.get('hygroscopicity', None)
        self.descriptors = properties.get('descriptors', {})
        
        # Set additional properties
        for key, value in properties.items():
            if not hasattr(self, key):
                setattr(self, key, value)
        
        # Generate RDKit molecule for monomer if SMILES is provided and RDKit is available
        if self.monomer_smiles and Chem:
            self.monomer_mol = Chem.MolFromSmiles(self.monomer_smiles)
    
    @classmethod
    def from_name(cls, name: str) -> 'Polymer':
        """
        Create a Polymer object from a name by looking up in the database.
        
        Args:
            name (str): Name of the polymer
            
        Returns:
            Polymer: A Polymer object
            
        Raises:
            ValueError: If the polymer is not found in the database
        """
        # Get the polymer from the database
        db = MaterialsDatabase()
        polymer_data = db.get_polymer(name)
        
        if polymer_data is None:
            raise ValueError(f"Polymer '{name}' not found in the database.")
        
        # Create a Polymer object from the database data
        return cls(name=name, **polymer_data)
    
    @classmethod
    def from_monomer(
        cls, 
        monomer_smiles: str, 
        name: Optional[str] = None, 
        degree_of_polymerization: int = 100
    ) -> 'Polymer':
        """
        Create a Polymer object from a monomer SMILES.
        
        Args:
            monomer_smiles (str): SMILES representation of the monomer
            name (str, optional): Name of the polymer. If not provided, a generic name is created.
            degree_of_polymerization (int, optional): Average degree of polymerization
            
        Returns:
            Polymer: A Polymer object
            
        Raises:
            ValueError: If RDKit is not available or the SMILES string is invalid
        """
        if not Chem:
            raise ValueError("RDKit is required to create a Polymer from a monomer SMILES.")
        
        # Parse the monomer SMILES
        monomer_mol = Chem.MolFromSmiles(monomer_smiles)
        if monomer_mol is None:
            raise ValueError(f"Invalid monomer SMILES string: {monomer_smiles}")
        
        # Create a name if not provided
        if name is None:
            name = f"Poly({Chem.MolToSmiles(monomer_mol)})"
        
        # Estimate molecular weight
        monomer_mw = Descriptors.MolWt(monomer_mol)
        estimated_mw = monomer_mw * degree_of_polymerization
        
        # Create a Polymer object
        polymer = cls(
            name=name,
            monomer_smiles=monomer_smiles,
            molecular_weight=estimated_mw,
            degree_of_polymerization=degree_of_polymerization
        )
        
        # Calculate properties
        polymer.calculate_properties()
        
        return polymer
    
    @classmethod
    def load_common_polymers(cls) -> List['Polymer']:
        """
        Load a list of common polymers used in ASD formulations.
        
        Returns:
            list: List of Polymer objects
        """
        # Get common polymers from the database
        db = MaterialsDatabase()
        common_polymers_data = db.get_common_polymers()
        
        # Create Polymer objects
        polymers = []
        for name, data in common_polymers_data.items():
            polymers.append(cls(name=name, **data))
        
        return polymers
    
    def calculate_properties(self) -> Dict[str, Any]:
        """
        Calculate basic polymer properties.
        
        Returns:
            dict: Dictionary of calculated properties
        """
        properties = {}
        
        # If we have a monomer molecule, calculate properties
        if self.monomer_mol and Chem:
            # If molecular weight is not provided, estimate it
            if self.molecular_weight is None and hasattr(self, 'degree_of_polymerization'):
                monomer_mw = Descriptors.MolWt(self.monomer_mol)
                self.molecular_weight = monomer_mw * self.degree_of_polymerization
                properties['molecular_weight'] = self.molecular_weight
            
            # Calculate functional groups
            functional_groups = self.calculate_functional_groups()
            properties['functional_groups'] = functional_groups
            
            # Estimate hydrophilicity if not provided
            if self.hydrophilicity is None:
                # Simple estimate based on functional groups
                # This is a placeholder and should be replaced with a more accurate model
                h_acceptors = Chem.Lipinski.NumHAcceptors(self.monomer_mol)
                h_donors = Chem.Lipinski.NumHDonors(self.monomer_mol)
                h_bond_capacity = h_acceptors + h_donors
                
                self.hydrophilicity = min(1.0, h_bond_capacity / 10.0)
                properties['hydrophilicity'] = self.hydrophilicity
        
        # Estimate hygroscopicity based on hydrophilicity if not provided
        if self.hygroscopicity is None and self.hydrophilicity is not None:
            # Simple estimate: hygroscopicity correlates with hydrophilicity
            # This is a placeholder and should be replaced with a more accurate model
            self.hygroscopicity = 0.8 * self.hydrophilicity + 0.1
            properties['hygroscopicity'] = self.hygroscopicity
        
        return properties
    
    def calculate_solubility_parameters(self) -> Dict[str, float]:
        """
        Calculate Hansen solubility parameters for the polymer.
        
        Returns:
            dict: Dictionary of solubility parameters (δd, δp, δh, δt)
            
        Raises:
            ValueError: If the monomer is not valid or the calculation fails
        """
        if not self.monomer_mol:
            raise ValueError("A valid monomer molecule is required to calculate solubility parameters.")
        
        # For polymers, we can estimate solubility parameters from the monomer
        # This is a simplified approach and should be refined
        solubility_parameters = calculate_solubility_parameters(self.monomer_mol)
        
        # Update the object property
        self.solubility_parameters = solubility_parameters
        
        return solubility_parameters
    
    def calculate_functional_groups(self) -> Dict[str, int]:
        """
        Identify and count functional groups in the polymer.
        
        Returns:
            dict: Dictionary of functional groups and their counts
            
        Raises:
            ValueError: If the monomer is not valid or RDKit is not available
        """
        if not self.monomer_mol or not Chem:
            raise ValueError("A valid monomer molecule and RDKit are required to calculate functional groups.")
        
        # Define SMARTS patterns for common functional groups
        functional_groups_smarts = {
            'hydroxyl': '[#8H1]',
            'carboxyl': '[#6](=[#8])[#8H1]',
            'ester': '[#6](=[#8])[#8][#6]',
            'amide': '[#6](=[#8])[#7]',
            'amine': '[#7;!$(N=*);!$(NC=O)]',
            'carbonyl': '[#6]=O',
            'ether': '[#8;$(O[#6]);!$(OC=O)]',
            'aromatic': 'a',
            'alkyl': '[CX4]',
            'alkene': '[CX3]=[CX3]',
            'alkyne': '[CX2]#[CX2]',
            'halogen': '[F,Cl,Br,I]',
        }
        
        # Count functional groups
        counts = {}
        for name, smarts in functional_groups_smarts.items():
            pattern = Chem.MolFromSmarts(smarts)
            if pattern:
                count = len(self.monomer_mol.GetSubstructMatches(pattern))
                counts[name] = count
        
        # Update the object property
        self.functional_groups = counts
        
        return counts
    
    def predict_api_compatibility(self, api: 'API') -> float:
        """
        Predict the compatibility of the polymer with a given API.
        
        This is a simplified implementation that uses a rule-based approach.
        In a more advanced implementation, this could use a machine learning model.
        
        Args:
            api (API): API object
            
        Returns:
            float: Compatibility score (0-1)
            
        Raises:
            ValueError: If required properties are not available
        """
        if (not api.solubility_parameters or
            not self.solubility_parameters):
            raise ValueError("Solubility parameters are required for both API and polymer.")
        
        # Calculate Hansen distance in solubility parameter space
        api_hsp = api.solubility_parameters
        polymer_hsp = self.solubility_parameters
        
        # Check if we have all required parameters
        if ('dispersive' not in api_hsp or
            'polar' not in api_hsp or
            'hydrogen' not in api_hsp or
            'dispersive' not in polymer_hsp or
            'polar' not in polymer_hsp or
            'hydrogen' not in polymer_hsp):
            raise ValueError("Complete Hansen solubility parameters are required.")
        
        # Calculate Hansen distance
        distance_squared = (
            4 * (polymer_hsp['dispersive'] - api_hsp['dispersive'])**2 +
            (polymer_hsp['polar'] - api_hsp['polar'])**2 +
            (polymer_hsp['hydrogen'] - api_hsp['hydrogen'])**2
        )
        hansen_distance = np.sqrt(distance_squared)
        
        # Convert to compatibility score (0-1)
        # Typically, Hansen distances < 5 indicate good compatibility
        max_distance = 10.0  # Maximum distance to consider
        compatibility = max(0.0, 1.0 - hansen_distance / max_distance)
        
        return compatibility
    
    def __repr__(self) -> str:
        """Return a string representation of the Polymer object."""
        type_str = f", type='{self.type}'" if self.type else ""
        return f"Polymer(name='{self.name}'{type_str})"
    
    def __str__(self) -> str:
        """Return a user-friendly string representation of the Polymer object."""
        properties = []
        if self.molecular_weight:
            properties.append(f"MW: {self.molecular_weight:.0f} g/mol")
        if self.glass_transition_temp:
            properties.append(f"Tg: {self.glass_transition_temp:.1f}°C")
        if self.hydrophilicity:
            properties.append(f"Hydrophilicity: {self.hydrophilicity:.2f}")
        
        props_str = ", ".join(properties)
        type_str = f" ({self.type})" if self.type else ""
        return f"{self.name}{type_str} - {props_str}"