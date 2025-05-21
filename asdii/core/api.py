"""
Implementation of the API (Active Pharmaceutical Ingredient) class.

This module provides the API class which represents an active pharmaceutical
ingredient in an amorphous solid dispersion formulation.
"""

from typing import Dict, List, Optional, Union, Any
import logging
import numpy as np

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, Lipinski
except ImportError:
    logging.warning("RDKit not found. Some API functionality will be limited.")
    Chem = None
    Descriptors = None
    Lipinski = None

from asdii.database.materials_db import MaterialsDatabase
from asdii.calculators.descriptors import calculate_molecular_descriptors
from asdii.calculators.solubility import calculate_solubility_parameters


class API:
    """
    Represents an Active Pharmaceutical Ingredient (API) in an ASD formulation.
    
    Attributes:
        name (str): Name of the API
        smiles (str): SMILES representation of the API structure
        mol (rdkit.Chem.Mol): RDKit molecule object
        molecular_weight (float): Molecular weight in g/mol
        melting_point (float): Melting point in Celsius
        glass_transition_temp (float): Glass transition temperature in Celsius
        log_p (float): Octanol-water partition coefficient
        solubility_parameters (dict): Hansen solubility parameters
        h_bond_donors (int): Number of hydrogen bond donors
        h_bond_acceptors (int): Number of hydrogen bond acceptors
        rotatable_bonds (int): Number of rotatable bonds
        descriptors (dict): Dictionary of molecular descriptors
    """
    
    def __init__(
        self, 
        name: str, 
        smiles: Optional[str] = None, 
        mol: Optional[Any] = None, 
        **properties: Dict[str, Any]
    ) -> None:
        """
        Initialize an API object.
        
        Args:
            name (str): Name of the API
            smiles (str, optional): SMILES representation of the API structure
            mol (rdkit.Chem.Mol, optional): RDKit molecule object
            **properties: Additional properties of the API
                molecular_weight (float): Molecular weight in g/mol
                melting_point (float): Melting point in Celsius
                glass_transition_temp (float): Glass transition temperature in Celsius
                log_p (float): Octanol-water partition coefficient
                solubility_parameters (dict): Hansen solubility parameters
                h_bond_donors (int): Number of hydrogen bond donors
                h_bond_acceptors (int): Number of hydrogen bond acceptors
                rotatable_bonds (int): Number of rotatable bonds
        """
        self.name = name
        self.smiles = smiles
        self.mol = mol
        
        # Initialize properties
        self.molecular_weight = properties.get('molecular_weight', None)
        self.melting_point = properties.get('melting_point', None)
        self.glass_transition_temp = properties.get('glass_transition_temp', None)
        self.log_p = properties.get('log_p', None)
        self.solubility_parameters = properties.get('solubility_parameters', {})
        self.h_bond_donors = properties.get('h_bond_donors', None)
        self.h_bond_acceptors = properties.get('h_bond_acceptors', None)
        self.rotatable_bonds = properties.get('rotatable_bonds', None)
        self.descriptors = properties.get('descriptors', {})
        
        # Set additional properties
        for key, value in properties.items():
            if not hasattr(self, key):
                setattr(self, key, value)
        
        # Generate RDKit molecule if SMILES is provided and RDKit is available
        if self.smiles and not self.mol and Chem:
            self.mol = Chem.MolFromSmiles(self.smiles)
            
        # Calculate basic properties if not provided and RDKit is available
        if self.mol and Chem:
            self._calculate_missing_properties()
    
    @classmethod
    def from_smiles(cls, smiles: str, name: Optional[str] = None) -> 'API':
        """
        Create an API object from a SMILES string.
        
        Args:
            smiles (str): SMILES representation of the API structure
            name (str, optional): Name of the API. If not provided, the SMILES string is used.
            
        Returns:
            API: An API object
            
        Raises:
            ValueError: If RDKit is not available or the SMILES string is invalid
        """
        if not Chem:
            raise ValueError("RDKit is required to create an API from SMILES.")
        
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError(f"Invalid SMILES string: {smiles}")
        
        # Use SMILES as name if not provided
        if name is None:
            name = smiles
        
        return cls(name=name, smiles=smiles, mol=mol)
    
    @classmethod
    def from_mol(cls, mol: Any, name: Optional[str] = None) -> 'API':
        """
        Create an API object from an RDKit molecule object.
        
        Args:
            mol (rdkit.Chem.Mol): RDKit molecule object
            name (str, optional): Name of the API
            
        Returns:
            API: An API object
            
        Raises:
            ValueError: If RDKit is not available
        """
        if not Chem:
            raise ValueError("RDKit is required to create an API from a molecule object.")
        
        # Generate SMILES from the molecule
        smiles = Chem.MolToSmiles(mol)
        
        # Use the SMILES as name if not provided
        if name is None:
            name = smiles
        
        return cls(name=name, smiles=smiles, mol=mol)
    
    @classmethod
    def from_name(cls, name: str) -> 'API':
        """
        Create an API object from a name by looking up in the database.
        
        Args:
            name (str): Name of the API
            
        Returns:
            API: An API object
            
        Raises:
            ValueError: If the API is not found in the database
        """
        # Get the API from the database
        db = MaterialsDatabase()
        api_data = db.get_api(name)
        
        if api_data is None:
            raise ValueError(f"API '{name}' not found in the database.")
        
        # Create an API object from the database data
        return cls(name=name, **api_data)
    
    def _calculate_missing_properties(self) -> None:
        """
        Calculate basic molecular properties if not provided and RDKit is available.
        """
        if not self.mol or not Chem:
            return
        
        # Calculate molecular weight if not provided
        if self.molecular_weight is None:
            self.molecular_weight = Descriptors.MolWt(self.mol)
        
        # Calculate logP if not provided
        if self.log_p is None:
            self.log_p = Descriptors.MolLogP(self.mol)
        
        # Calculate hydrogen bond donors if not provided
        if self.h_bond_donors is None:
            self.h_bond_donors = Lipinski.NumHDonors(self.mol)
        
        # Calculate hydrogen bond acceptors if not provided
        if self.h_bond_acceptors is None:
            self.h_bond_acceptors = Lipinski.NumHAcceptors(self.mol)
        
        # Calculate rotatable bonds if not provided
        if self.rotatable_bonds is None:
            self.rotatable_bonds = Descriptors.NumRotatableBonds(self.mol)
    
    def calculate_properties(self) -> Dict[str, Any]:
        """
        Calculate basic molecular properties.
        
        Returns:
            dict: Dictionary of calculated properties
            
        Raises:
            ValueError: If RDKit is not available or the molecule is not valid
        """
        if not self.mol or not Chem:
            raise ValueError("RDKit is required to calculate properties.")
        
        properties = {
            'molecular_weight': Descriptors.MolWt(self.mol),
            'log_p': Descriptors.MolLogP(self.mol),
            'h_bond_donors': Lipinski.NumHDonors(self.mol),
            'h_bond_acceptors': Lipinski.NumHAcceptors(self.mol),
            'rotatable_bonds': Descriptors.NumRotatableBonds(self.mol),
            'heavy_atoms': self.mol.GetNumHeavyAtoms(),
            'rings': Descriptors.RingCount(self.mol),
            'aromatic_rings': Descriptors.NumAromaticRings(self.mol),
            'tpsa': Descriptors.TPSA(self.mol),
        }
        
        # Update the object properties
        for key, value in properties.items():
            setattr(self, key, value)
        
        return properties
    
    def calculate_solubility_parameters(self) -> Dict[str, float]:
        """
        Calculate Hansen solubility parameters.
        
        Returns:
            dict: Dictionary of solubility parameters (δd, δp, δh, δt)
            
        Raises:
            ValueError: If the molecule is not valid or the calculation fails
        """
        if not self.mol:
            raise ValueError("A valid molecule is required to calculate solubility parameters.")
        
        # Calculate solubility parameters using the imported function
        solubility_parameters = calculate_solubility_parameters(self.mol)
        
        # Update the object property
        self.solubility_parameters = solubility_parameters
        
        return solubility_parameters
    
    def calculate_descriptors(self) -> Dict[str, float]:
        """
        Calculate molecular descriptors.
        
        Returns:
            dict: Dictionary of molecular descriptors
            
        Raises:
            ValueError: If the molecule is not valid or the calculation fails
        """
        if not self.mol:
            raise ValueError("A valid molecule is required to calculate descriptors.")
        
        # Calculate descriptors using the imported function
        descriptors = calculate_molecular_descriptors(self.mol)
        
        # Update the object property
        self.descriptors = descriptors
        
        return descriptors
    
    def predict_amorphization_tendency(self) -> float:
        """
        Predict the tendency of the API to form an amorphous state.
        
        This is a simplified implementation that uses a rule-based approach.
        In a more advanced implementation, this could use a machine learning model.
        
        Returns:
            float: Score indicating amorphization tendency (0-1)
            
        Raises:
            ValueError: If required properties are not available
        """
        if (self.molecular_weight is None or
            self.melting_point is None or
            self.log_p is None or
            self.h_bond_donors is None or
            self.h_bond_acceptors is None or
            self.rotatable_bonds is None):
            raise ValueError("Required properties are not available for prediction.")
        
        # Simplified rule-based prediction
        # These rules are illustrative and should be replaced with validated models
        
        # Molecular weight factor: higher MW tends to favor amorphization
        mw_factor = min(1.0, self.molecular_weight / 500.0)
        
        # Melting point factor: higher melting point often correlates with crystallization tendency
        mp_factor = max(0.0, 1.0 - (self.melting_point - 100) / 200.0) if self.melting_point else 0.5
        
        # LogP factor: mid-range logP values often favor amorphization
        logp_factor = 1.0 - abs(self.log_p - 2.5) / 5.0
        logp_factor = max(0.0, min(1.0, logp_factor))
        
        # Hydrogen bonding factor: moderate hydrogen bonding favors amorphization
        hb_total = self.h_bond_donors + self.h_bond_acceptors
        hb_factor = 1.0 - abs(hb_total - 5) / 10.0
        hb_factor = max(0.0, min(1.0, hb_factor))
        
        # Rotatable bonds factor: higher flexibility can favor amorphization
        rb_factor = min(1.0, self.rotatable_bonds / 10.0)
        
        # Combine factors with weights
        # These weights are illustrative and should be optimized based on real data
        weights = [0.3, 0.2, 0.2, 0.15, 0.15]
        factors = [mw_factor, mp_factor, logp_factor, hb_factor, rb_factor]
        
        tendency = sum(w * f for w, f in zip(weights, factors))
        
        return tendency
    
    def visualize(self) -> Any:
        """
        Generate a 2D visualization of the API structure.
        
        Returns:
            matplotlib.figure.Figure: Figure object with the API structure
            
        Raises:
            ValueError: If RDKit is not available or the molecule is not valid
        """
        if not self.mol or not Chem:
            raise ValueError("RDKit is required to visualize the structure.")
        
        try:
            from rdkit.Chem import Draw
            import matplotlib.pyplot as plt
            from matplotlib.figure import Figure
            
            # Generate 2D coordinates if needed
            mol = Chem.Mol(self.mol)
            if not mol.GetNumConformers():
                mol = Chem.AddHs(mol)
                Chem.AllChem.EmbedMolecule(mol)
                mol = Chem.RemoveHs(mol)
            
            # Create the image
            fig = plt.figure(figsize=(4, 4))
            img = Draw.MolToImage(mol)
            plt.imshow(img)
            plt.axis('off')
            plt.title(self.name)
            
            return fig
            
        except ImportError:
            raise ValueError("Required visualization libraries are not available.")
    
    def __repr__(self) -> str:
        """Return a string representation of the API object."""
        return f"API(name='{self.name}', smiles='{self.smiles}')"
    
    def __str__(self) -> str:
        """Return a user-friendly string representation of the API object."""
        properties = []
        if self.molecular_weight:
            properties.append(f"MW: {self.molecular_weight:.2f} g/mol")
        if self.melting_point:
            properties.append(f"MP: {self.melting_point:.1f}°C")
        if self.glass_transition_temp:
            properties.append(f"Tg: {self.glass_transition_temp:.1f}°C")
        if self.log_p:
            properties.append(f"LogP: {self.log_p:.2f}")
        
        props_str = ", ".join(properties)
        return f"{self.name} ({props_str})"