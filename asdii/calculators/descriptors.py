"""
Implementation of molecular descriptor calculators.

This module provides functions to calculate molecular descriptors for APIs and
polymers, which can be used to predict properties and behavior in ASD formulations.
"""

from typing import Dict, List, Optional, Union, Any
import logging
import numpy as np

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, Lipinski, MolSurf, GraphDescriptors
    from rdkit.Chem.QED import qed
except ImportError:
    logging.warning("RDKit not found. Molecular descriptor calculations will be limited.")
    Chem = None
    Descriptors = None
    Lipinski = None
    MolSurf = None
    GraphDescriptors = None
    qed = None

try:
    from mordred import Calculator, descriptors as md_descriptors
    MORDRED_AVAILABLE = True
except ImportError:
    logging.warning("Mordred not found. Advanced descriptor calculations will be limited.")
    Calculator = None
    md_descriptors = None
    MORDRED_AVAILABLE = False


def calculate_molecular_descriptors(mol: Any, level: str = 'basic') -> Dict[str, float]:
    """
    Calculate molecular descriptors for a molecule.
    
    Args:
        mol (rdkit.Chem.Mol): RDKit molecule object
        level (str, optional): Level of descriptor calculation:
            'basic': Basic descriptors using RDKit only
            'extended': Extended descriptors using RDKit only
            'comprehensive': Comprehensive descriptors using Mordred if available
    
    Returns:
        dict: Dictionary of molecular descriptors
        
    Raises:
        ValueError: If RDKit is not available or molecule is invalid
    """
    if not Chem or mol is None:
        raise ValueError("RDKit and a valid molecule are required to calculate descriptors.")
    
    descriptors = {}
    
    # Calculate basic descriptors
    if level in ['basic', 'extended', 'comprehensive']:
        # Molecular weight and size
        descriptors['molecular_weight'] = Descriptors.MolWt(mol)
        descriptors['heavy_atom_count'] = mol.GetNumHeavyAtoms()
        descriptors['atom_count'] = Descriptors.HeavyAtomCount(mol) + Descriptors.NumHAtoms(mol)
        descriptors['ring_count'] = Descriptors.RingCount(mol)
        descriptors['aromatic_ring_count'] = Descriptors.NumAromaticRings(mol)
        descriptors['rotatable_bond_count'] = Descriptors.NumRotatableBonds(mol)
        descriptors['hetero_atom_count'] = Descriptors.NumHeteroatoms(mol)
        
        # Lipinski descriptors
        descriptors['h_bond_donor_count'] = Descriptors.NumHDonors(mol)
        descriptors['h_bond_acceptor_count'] = Descriptors.NumHAcceptors(mol)
        descriptors['log_p'] = Descriptors.MolLogP(mol)
        
        # Surface area and volume
        descriptors['tpsa'] = Descriptors.TPSA(mol)
        descriptors['labute_asa'] = MolSurf.LabuteASA(mol)
        
        # Simple counts
        descriptors['sp3_atom_ratio'] = Descriptors.FractionCSP3(mol)
        descriptors['formal_charge'] = sum([atom.GetFormalCharge() for atom in mol.GetAtoms()])
    
    # Calculate extended descriptors
    if level in ['extended', 'comprehensive']:
        # Electronic properties
        descriptors['molar_refractivity'] = Descriptors.MolMR(mol)
        descriptors['num_valence_electrons'] = Descriptors.NumValenceElectrons(mol)
        
        # Connectivity and shape
        descriptors['balaban_j'] = GraphDescriptors.BalabanJ(mol)
        descriptors['bertz_ct'] = GraphDescriptors.BertzCT(mol)
        descriptors['chi0v'] = GraphDescriptors.Chi0v(mol)
        descriptors['chi1v'] = GraphDescriptors.Chi1v(mol)
        
        # Drug-likeness
        try:
            descriptors['qed'] = qed(mol)
        except Exception as e:
            logging.warning(f"Failed to calculate QED: {e}")
        
        # Calculated properties
        try:
            descriptors['exact_mw'] = Descriptors.ExactMolWt(mol)
            descriptors['num_radical_electrons'] = Descriptors.NumRadicalElectrons(mol)
            descriptors['max_abs_partial_charge'] = Descriptors.MaxAbsPartialCharge(mol)
            descriptors['max_partial_charge'] = Descriptors.MaxPartialCharge(mol)
            descriptors['min_partial_charge'] = Descriptors.MinPartialCharge(mol)
        except Exception as e:
            logging.warning(f"Failed to calculate some descriptors: {e}")
    
    # Calculate comprehensive descriptors using Mordred
    if level == 'comprehensive' and MORDRED_AVAILABLE:
        try:
            # Initialize Mordred calculator with all descriptors
            calc = Calculator(md_descriptors, ignore_3D=True)
            
            # Calculate descriptors
            mordred_descriptors = calc(mol)
            
            # Convert to dictionary
            for descriptor, value in mordred_descriptors.items():
                # Skip descriptors that couldn't be calculated
                if value is None or np.isnan(value):
                    continue
                
                # Add descriptor to results
                descriptor_name = str(descriptor)
                descriptors[f"mordred_{descriptor_name}"] = float(value)
        except Exception as e:
            logging.warning(f"Failed to calculate Mordred descriptors: {e}")
    
    return descriptors


def calculate_fragment_descriptors(mol: Any) -> Dict[str, int]:
    """
    Calculate fragment-based descriptors for a molecule.
    
    Args:
        mol (rdkit.Chem.Mol): RDKit molecule object
    
    Returns:
        dict: Dictionary of fragment counts
        
    Raises:
        ValueError: If RDKit is not available or molecule is invalid
    """
    if not Chem or mol is None:
        raise ValueError("RDKit and a valid molecule are required to calculate fragment descriptors.")
    
    # Define common functional groups as SMARTS patterns
    functional_groups = {
        'alcohol': '[OX2H]',
        'phenol': '[OX2H][cX3]:[c]',
        'carboxylic_acid': '[CX3](=[OX1])[OX2H]',
        'carboxylic_ester': '[CX3](=[OX1])[OX2][CX4]',
        'ether': '[OD2]([#6])[#6]',
        'aldehyde': '[CX3H1](=O)[#6]',
        'ketone': '[CX3](=O)[#6][#6]',
        'primary_amine': '[NX3;H2][#6]',
        'secondary_amine': '[NX3;H1]([#6])[#6]',
        'tertiary_amine': '[NX3]([#6])([#6])[#6]',
        'amide': '[NX3][CX3](=[OX1])',
        'nitro': '[NX3](=[OX1])(=[OX1])',
        'nitrile': '[NX1]#[CX2]',
        'halogen': '[F,Cl,Br,I]',
        'sulfide': '[#16X2]([#6])[#6]',
        'sulfoxide': '[#16X3](=[OX1])([#6])[#6]',
        'sulfone': '[#16X4](=[OX1])(=[OX1])([#6])[#6]',
        'aromatic_ring': '[a;r6]',
        'heterocyclic_ring': '[a;!c;r6]',
        'aliphatic_ring': '[A;r6]',
        'amide': '[NX3][CX3](=[OX1])',
        'primary_amide': '[NX3H2][CX3](=[OX1])',
        'sulfonamide': '[#16X4]([#8X1])(=[#8X1])(=[#8X1])[#7X3H1]',
        'phosphate': '[#15;$([#15X4]([OX2H])([OX2H])=[OX1])]'
    }
    
    # Count occurrences of each functional group
    fragment_counts = {}
    for name, smarts in functional_groups.items():
        pattern = Chem.MolFromSmarts(smarts)
        if pattern:
            count = len(mol.GetSubstructMatches(pattern))
            fragment_counts[name] = count
    
    return fragment_counts


def calculate_molecular_properties(mol: Any) -> Dict[str, Any]:
    """
    Calculate physicochemical properties of a molecule.
    
    Args:
        mol (rdkit.Chem.Mol): RDKit molecule object
    
    Returns:
        dict: Dictionary of molecular properties
        
    Raises:
        ValueError: If RDKit is not available or molecule is invalid
    """
    if not Chem or mol is None:
        raise ValueError("RDKit and a valid molecule are required to calculate properties.")
    
    properties = {}
    
    # Drug-like properties
    properties['molecular_weight'] = Descriptors.MolWt(mol)
    properties['log_p'] = Descriptors.MolLogP(mol)
    properties['log_d'] = properties['log_p']  # Approximation, should be pH-dependent
    properties['h_bond_donors'] = Descriptors.NumHDonors(mol)
    properties['h_bond_acceptors'] = Descriptors.NumHAcceptors(mol)
    properties['rotatable_bonds'] = Descriptors.NumRotatableBonds(mol)
    properties['tpsa'] = Descriptors.TPSA(mol)
    
    # Lipinski's Rule of Five
    violations = 0
    if properties['molecular_weight'] > 500:
        violations += 1
    if properties['log_p'] > 5:
        violations += 1
    if properties['h_bond_donors'] > 5:
        violations += 1
    if properties['h_bond_acceptors'] > 10:
        violations += 1
    properties['lipinski_violations'] = violations
    
    # Drug-likeness classification
    if violations <= 1:
        properties['drug_likeness'] = 'High'
    elif violations <= 2:
        properties['drug_likeness'] = 'Medium'
    else:
        properties['drug_likeness'] = 'Low'
    
    # BCS Classification prediction (simplified)
    # This is a placeholder and should be replaced with a more accurate model
    if properties['log_p'] < 2:
        if properties['molecular_weight'] < 350:
            properties['predicted_bcs_class'] = 'Class I (High solubility, High permeability)'
        else:
            properties['predicted_bcs_class'] = 'Class III (High solubility, Low permeability)'
    else:
        if properties['molecular_weight'] < 400:
            properties['predicted_bcs_class'] = 'Class II (Low solubility, High permeability)'
        else:
            properties['predicted_bcs_class'] = 'Class IV (Low solubility, Low permeability)'
    
    # Calculate QED (Quantitative Estimate of Drug-likeness)
    try:
        properties['qed'] = qed(mol)
    except Exception as e:
        logging.warning(f"Failed to calculate QED: {e}")
    
    return properties


def predict_glass_transition_from_structure(mol: Any) -> float:
    """
    Predict the glass transition temperature of a molecule from its structure.
    
    Args:
        mol (rdkit.Chem.Mol): RDKit molecule object
    
    Returns:
        float: Predicted glass transition temperature in Celsius
        
    Raises:
        ValueError: If RDKit is not available or molecule is invalid
    """
    if not Chem or mol is None:
        raise ValueError("RDKit and a valid molecule are required to predict glass transition temperature.")
    
    # This is a simplified QSPR model for Tg prediction
    # A more sophisticated model should be implemented in a production library
    
    # Calculate descriptors
    mw = Descriptors.MolWt(mol)
    rotatable_bonds = Descriptors.NumRotatableBonds(mol)
    h_donors = Descriptors.NumHDonors(mol)
    h_acceptors = Descriptors.NumHAcceptors(mol)
    aromatic_rings = Descriptors.NumAromaticRings(mol)
    rigid_bonds = mol.GetNumBonds() - rotatable_bonds
    
    # Simplified model
    # Higher MW, more rigid bonds, more hydrogen bonding -> higher Tg
    # More rotatable bonds -> lower Tg
    
    # Base Tg contribution from molecular weight
    tg = -50 + 0.5 * mw
    
    # Adjust for flexibility/rigidity
    tg -= 7 * rotatable_bonds
    tg += 5 * rigid_bonds
    
    # Adjust for hydrogen bonding potential
    tg += 10 * h_donors
    tg += 5 * h_acceptors
    
    # Adjust for aromatic rings
    tg += 15 * aromatic_rings
    
    # Normalize
    tg = max(-150, min(250, tg))
    
    return tg


def predict_amorphization_tendency(mol: Any) -> float:
    """
    Predict the tendency of a molecule to form an amorphous state.
    
    Args:
        mol (rdkit.Chem.Mol): RDKit molecule object
    
    Returns:
        float: Amorphization tendency score (0-1)
        
    Raises:
        ValueError: If RDKit is not available or molecule is invalid
    """
    if not Chem or mol is None:
        raise ValueError("RDKit and a valid molecule are required to predict amorphization tendency.")
    
    # This is a simplified model for amorphization tendency prediction
    # A more sophisticated model should be implemented in a production library
    
    # Calculate descriptors
    mw = Descriptors.MolWt(mol)
    rotatable_bonds = Descriptors.NumRotatableBonds(mol)
    h_donors = Descriptors.NumHDonors(mol)
    h_acceptors = Descriptors.NumHAcceptors(mol)
    aromatic_rings = Descriptors.NumAromaticRings(mol)
    sp3_ratio = Descriptors.FractionCSP3(mol)
    tpsa = Descriptors.TPSA(mol)
    
    # Molecular weight factor (higher MW tends to favor amorphization)
    mw_factor = min(1.0, mw / 500.0)
    
    # Rotatable bonds factor (higher flexibility can favor amorphization)
    rb_factor = min(1.0, rotatable_bonds / 10.0)
    
    # Hydrogen bonding factor (moderate hydrogen bonding favors amorphization)
    hb_total = h_donors + h_acceptors
    hb_factor = 1.0 - abs(hb_total - 5) / 10.0
    hb_factor = max(0.0, min(1.0, hb_factor))
    
    # Aromatic rings factor (aromatic rings can promote π-stacking and crystallization)
    ar_factor = max(0.0, 1.0 - aromatic_rings / 5.0)
    
    # sp3 carbon ratio factor (higher sp3 ratio tends to disrupt crystal packing)
    sp3_factor = sp3_ratio
    
    # TPSA factor (very high or very low TPSA may favor crystallization)
    tpsa_factor = 1.0 - abs(tpsa - 100) / 150.0
    tpsa_factor = max(0.0, min(1.0, tpsa_factor))
    
    # Combine factors with weights
    weights = [0.25, 0.20, 0.15, 0.15, 0.15, 0.10]
    factors = [mw_factor, rb_factor, hb_factor, ar_factor, sp3_factor, tpsa_factor]
    
    tendency = sum(w * f for w, f in zip(weights, factors))
    tendency = max(0.0, min(1.0, tendency))
    
    return tendency