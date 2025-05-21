"""
Implementation of solubility parameter calculators.

This module provides functions to calculate solubility parameters of APIs, polymers,
and ASD formulations, such as Hansen solubility parameters and Flory-Huggins
interaction parameters.
"""

from typing import Dict, List, Optional, Union, Any
import logging
import numpy as np

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, AllChem
except ImportError:
    logging.warning("RDKit not found. Some solubility parameter calculations will be limited.")
    Chem = None
    Descriptors = None
    AllChem = None


def calculate_solubility_parameters(mol: Any) -> Dict[str, float]:
    """
    Calculate Hansen solubility parameters for a molecule.
    
    Args:
        mol (rdkit.Chem.Mol): RDKit molecule object
        
    Returns:
        dict: Dictionary of solubility parameters:
            'dispersive': Dispersive component (δd)
            'polar': Polar component (δp)
            'hydrogen': Hydrogen bonding component (δh)
            'total': Total solubility parameter (δt)
            
    Raises:
        ValueError: If RDKit is not available or molecule is invalid
    """
    if not Chem or mol is None:
        raise ValueError("RDKit and a valid molecule are required to calculate solubility parameters.")
    
    # This implementation uses a simplified group contribution method
    # A more sophisticated method should be implemented in a production library
    
    # For now, we'll use a simplified approach based on molecular properties
    
    # Calculate molecular properties
    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    h_donors = Descriptors.NumHDonors(mol)
    h_acceptors = Descriptors.NumHAcceptors(mol)
    tpsa = Descriptors.TPSA(mol)
    
    # Estimate Hansen parameters
    # These are very simplified estimates and should be replaced with proper GCM
    
    # Dispersive component (related to molecular weight and logP)
    # Typically in the range 15-30 MPa^0.5
    dispersive = 15.0 + 10.0 * (1 - np.exp(-0.005 * mw)) + 2.0 * logp
    dispersive = max(15.0, min(30.0, dispersive))
    
    # Polar component (related to TPSA)
    # Typically in the range 0-20 MPa^0.5
    polar = 0.25 * tpsa
    polar = max(0.0, min(20.0, polar))
    
    # Hydrogen bonding component (related to H-donors and H-acceptors)
    # Typically in the range 0-30 MPa^0.5
    hydrogen = 2.0 * h_donors + 1.0 * h_acceptors
    hydrogen = max(0.0, min(30.0, hydrogen))
    
    # Calculate total solubility parameter
    total = np.sqrt(dispersive**2 + polar**2 + hydrogen**2)
    
    # Return the solubility parameters
    return {
        'dispersive': dispersive,
        'polar': polar,
        'hydrogen': hydrogen,
        'total': total
    }


def calculate_hansen_distance(
    params1: Dict[str, float],
    params2: Dict[str, float]
) -> float:
    """
    Calculate the Hansen distance between two sets of solubility parameters.
    
    Args:
        params1 (dict): First set of Hansen solubility parameters
        params2 (dict): Second set of Hansen solubility parameters
        
    Returns:
        float: Hansen distance
        
    Raises:
        ValueError: If required parameters are missing
    """
    # Check if required parameters are present
    required_params = ['dispersive', 'polar', 'hydrogen']
    for param in required_params:
        if param not in params1 or param not in params2:
            raise ValueError(f"Missing solubility parameter: {param}")
    
    # Calculate Hansen distance
    # Ra^2 = 4(δd1 - δd2)^2 + (δp1 - δp2)^2 + (δh1 - δh2)^2
    distance_squared = (
        4 * (params1['dispersive'] - params2['dispersive'])**2 +
        (params1['polar'] - params2['polar'])**2 +
        (params1['hydrogen'] - params2['hydrogen'])**2
    )
    
    return np.sqrt(distance_squared)


def calculate_hildebrand_parameter(hansen_params: Dict[str, float]) -> float:
    """
    Calculate the Hildebrand solubility parameter from Hansen parameters.
    
    Args:
        hansen_params (dict): Hansen solubility parameters
        
    Returns:
        float: Hildebrand solubility parameter
        
    Raises:
        ValueError: If required parameters are missing
    """
    # Check if required parameters are present
    required_params = ['dispersive', 'polar', 'hydrogen']
    for param in required_params:
        if param not in hansen_params:
            raise ValueError(f"Missing solubility parameter: {param}")
    
    # Calculate Hildebrand parameter
    # δt^2 = δd^2 + δp^2 + δh^2
    hildebrand = np.sqrt(
        hansen_params['dispersive']**2 +
        hansen_params['polar']**2 +
        hansen_params['hydrogen']**2
    )
    
    return hildebrand


def calculate_flory_huggins_parameter(
    params1: Dict[str, float],
    params2: Dict[str, float],
    temperature: float = 298.15  # Kelvin
) -> float:
    """
    Calculate the Flory-Huggins interaction parameter (χ) from solubility parameters.
    
    Args:
        params1 (dict): First set of Hansen solubility parameters
        params2 (dict): Second set of Hansen solubility parameters
        temperature (float, optional): Temperature in Kelvin
        
    Returns:
        float: Flory-Huggins interaction parameter
        
    Raises:
        ValueError: If required parameters are missing
    """
    # Calculate Hildebrand parameters
    delta1 = calculate_hildebrand_parameter(params1)
    delta2 = calculate_hildebrand_parameter(params2)
    
    # Calculate molar volume (simplified approach)
    # In a more sophisticated implementation, this should be calculated or provided
    v_ref = 100.0  # cm^3/mol (reference volume)
    
    # Calculate Flory-Huggins parameter
    # χ = v_ref * (δ1 - δ2)^2 / (R * T)
    r_gas = 8.314  # J/(mol*K)
    chi = v_ref * (delta1 - delta2)**2 / (r_gas * temperature)
    
    return chi


def predict_miscibility(
    params1: Dict[str, float],
    params2: Dict[str, float],
    method: str = 'hansen',
    temperature: float = 298.15  # Kelvin
) -> float:
    """
    Predict the miscibility of two components based on their solubility parameters.
    
    Args:
        params1 (dict): First set of Hansen solubility parameters
        params2 (dict): Second set of Hansen solubility parameters
        method (str, optional): Method for miscibility prediction:
            'hansen': Hansen distance approach
            'flory_huggins': Flory-Huggins interaction parameter
        temperature (float, optional): Temperature in Kelvin (for Flory-Huggins method)
        
    Returns:
        float: Miscibility score (0-1)
        
    Raises:
        ValueError: If method is not valid or required parameters are missing
    """
    if method == 'hansen':
        # Calculate Hansen distance
        distance = calculate_hansen_distance(params1, params2)
        
        # Convert to miscibility score (0-1)
        # Typically, Hansen distances < 5 indicate good miscibility
        max_distance = 10.0  # Maximum distance to consider
        miscibility = max(0.0, 1.0 - distance / max_distance)
        
    elif method == 'flory_huggins':
        # Calculate Flory-Huggins parameter
        chi = calculate_flory_huggins_parameter(params1, params2, temperature)
        
        # Convert to miscibility score (0-1)
        # Typically, χ < 0.5 indicates good miscibility
        # χ > 0.5 indicates poor miscibility
        miscibility = max(0.0, 1.0 - chi / 5.0)
        
    else:
        raise ValueError(f"Invalid method: {method}. Valid methods are: 'hansen', 'flory_huggins'")
    
    return miscibility


def estimate_solubility_parameters_from_structure(mol: Any) -> Dict[str, float]:
    """
    Estimate Hansen solubility parameters from molecular structure using
    a simplified group contribution method.
    
    Args:
        mol (rdkit.Chem.Mol): RDKit molecule object
        
    Returns:
        dict: Dictionary of solubility parameters
        
    Raises:
        ValueError: If RDKit is not available or molecule is invalid
    """
    # This is a placeholder for a more sophisticated group contribution method
    # In a production implementation, a proper GCM should be used
    # For now, we'll redirect to the simplified approach
    
    return calculate_solubility_parameters(mol)


def estimate_solubility_parameters_from_name(name: str) -> Dict[str, float]:
    """
    Estimate Hansen solubility parameters from a compound name by looking up
    in a database or by converting to structure.
    
    Args:
        name (str): Compound name
        
    Returns:
        dict: Dictionary of solubility parameters
        
    Raises:
        ValueError: If compound is not found or calculation fails
    """
    # This is a placeholder for database lookup functionality
    # In a production implementation, this should query a database
    
    # For common solvents and polymers, we could have a built-in database
    common_solvents = {
        'water': {'dispersive': 15.5, 'polar': 16.0, 'hydrogen': 42.3, 'total': 47.8},
        'ethanol': {'dispersive': 15.8, 'polar': 8.8, 'hydrogen': 19.4, 'total': 26.5},
        'acetone': {'dispersive': 15.5, 'polar': 10.4, 'hydrogen': 7.0, 'total': 20.0},
        'dichloromethane': {'dispersive': 18.2, 'polar': 6.3, 'hydrogen': 6.1, 'total': 20.2},
        'chloroform': {'dispersive': 17.8, 'polar': 3.1, 'hydrogen': 5.7, 'total': 19.0},
        'hexane': {'dispersive': 14.9, 'polar': 0.0, 'hydrogen': 0.0, 'total': 14.9},
        'toluene': {'dispersive': 18.0, 'polar': 1.4, 'hydrogen': 2.0, 'total': 18.2},
        'dmso': {'dispersive': 18.4, 'polar': 16.4, 'hydrogen': 10.2, 'total': 26.7},
    }
    
    common_polymers = {
        'pvp': {'dispersive': 17.0, 'polar': 8.0, 'hydrogen': 12.0, 'total': 22.2},
        'hpmc': {'dispersive': 18.0, 'polar': 8.6, 'hydrogen': 11.9, 'total': 23.3},
        'hpmcas': {'dispersive': 18.5, 'polar': 9.5, 'hydrogen': 10.0, 'total': 23.0},
        'pva': {'dispersive': 16.0, 'polar': 10.8, 'hydrogen': 17.6, 'total': 26.2},
        'peg': {'dispersive': 17.0, 'polar': 3.0, 'hydrogen': 9.0, 'total': 19.4},
        'soluplus': {'dispersive': 17.5, 'polar': 7.0, 'hydrogen': 9.0, 'total': 20.9},
        'eudragit': {'dispersive': 16.8, 'polar': 9.0, 'hydrogen': 8.0, 'total': 20.6},
        'pvpva': {'dispersive': 16.5, 'polar': 7.5, 'hydrogen': 10.5, 'total': 21.0}
    }
    
    # Check in common solvents
    name_lower = name.lower()
    if name_lower in common_solvents:
        return common_solvents[name_lower]
    
    # Check in common polymers
    if name_lower in common_polymers:
        return common_polymers[name_lower]
    
    # If not found, attempt to convert to structure and calculate
    if Chem:
        try:
            # Try to get compound from name (this is a simplistic approach)
            mol = Chem.MolFromSmiles(name)
            if mol:
                return calculate_solubility_parameters(mol)
        except Exception as e:
            logging.warning(f"Failed to convert {name} to structure: {e}")
    
    raise ValueError(f"Compound '{name}' not found in database and could not be converted to structure.")


def calculate_solubility_parameters_for_mixture(
    params1: Dict[str, float],
    params2: Dict[str, float],
    fraction1: float
) -> Dict[str, float]:
    """
    Calculate the solubility parameters for a mixture of two components.
    
    Args:
        params1 (dict): Solubility parameters for component 1
        params2 (dict): Solubility parameters for component 2
        fraction1 (float): Volume fraction of component 1 (0-1)
        
    Returns:
        dict: Dictionary of solubility parameters for the mixture
        
    Raises:
        ValueError: If required parameters are missing or fraction is invalid
    """
    # Check if fraction is valid
    if not 0 <= fraction1 <= 1:
        raise ValueError("Fraction must be between 0 and 1.")
    
    # Check if required parameters are present
    required_params = ['dispersive', 'polar', 'hydrogen']
    for param in required_params:
        if param not in params1 or param not in params2:
            raise ValueError(f"Missing solubility parameter: {param}")
    
    # Calculate fraction of component 2
    fraction2 = 1 - fraction1
    
    # Calculate mixture parameters
    # Simple volume fraction weighted average
    mixture_params = {}
    for param in required_params:
        mixture_params[param] = fraction1 * params1[param] + fraction2 * params2[param]
    
    # Calculate total parameter
    mixture_params['total'] = np.sqrt(
        mixture_params['dispersive']**2 +
        mixture_params['polar']**2 +
        mixture_params['hydrogen']**2
    )
    
    return mixture_params