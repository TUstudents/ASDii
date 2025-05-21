"""
Implementation of thermal property calculators.

This module provides functions to calculate thermal properties of APIs, polymers,
and ASD formulations, such as glass transition temperature.
"""

from typing import Dict, List, Optional, Union, Any
import numpy as np


def predict_glass_transition(
    tg_api: float,
    tg_polymer: float,
    drug_loading: float,
    method: str = 'gordon_taylor',
    k: Optional[float] = None
) -> float:
    """
    Predict the glass transition temperature of an ASD formulation.
    
    Args:
        tg_api (float): Glass transition temperature of the API in Celsius
        tg_polymer (float): Glass transition temperature of the polymer in Celsius
        drug_loading (float): Drug loading as weight fraction (0-1)
        method (str, optional): Method for Tg prediction:
            'gordon_taylor': Gordon-Taylor equation
            'fox': Fox equation
            'couchman_karasz': Couchman-Karasz equation
        k (float, optional): Gordon-Taylor parameter.
            If not provided, it will be estimated based on the Tg values.
    
    Returns:
        float: Predicted glass transition temperature in Celsius
        
    Raises:
        ValueError: If method is not valid or required parameters are missing
    """
    # Convert temperatures to Kelvin for calculations
    tg_api_k = tg_api + 273.15
    tg_polymer_k = tg_polymer + 273.15
    
    # Calculate weight fractions
    w1 = drug_loading  # API
    w2 = 1 - drug_loading  # Polymer
    
    # Calculate Tg based on selected method
    if method == 'gordon_taylor':
        # Gordon-Taylor equation: Tg = (w1*Tg1 + K*w2*Tg2) / (w1 + K*w2)
        
        # Estimate K if not provided
        if k is None:
            # Simple estimation: K = Tg1/Tg2
            # This is a simplified approach and should be refined
            k = tg_api_k / tg_polymer_k
        
        # Calculate Tg using Gordon-Taylor equation
        tg_mix_k = (w1 * tg_api_k + k * w2 * tg_polymer_k) / (w1 + k * w2)
        
    elif method == 'fox':
        # Fox equation: 1/Tg = w1/Tg1 + w2/Tg2
        
        # Calculate Tg using Fox equation
        if w1 == 0:
            tg_mix_k = tg_polymer_k
        elif w2 == 0:
            tg_mix_k = tg_api_k
        else:
            tg_mix_k = 1 / (w1 / tg_api_k + w2 / tg_polymer_k)
        
    elif method == 'couchman_karasz':
        # Couchman-Karasz equation: ln(Tg) = (w1*Cp1*ln(Tg1) + w2*Cp2*ln(Tg2)) / (w1*Cp1 + w2*Cp2)
        
        # Estimate heat capacity ratios
        # This is a simplified approach and should be refined
        cp1 = 1.0  # Heat capacity of API (placeholder)
        cp2 = 2.0  # Heat capacity of polymer (placeholder)
        
        # Calculate Tg using Couchman-Karasz equation
        if w1 == 0:
            tg_mix_k = tg_polymer_k
        elif w2 == 0:
            tg_mix_k = tg_api_k
        else:
            numerator = w1 * cp1 * np.log(tg_api_k) + w2 * cp2 * np.log(tg_polymer_k)
            denominator = w1 * cp1 + w2 * cp2
            tg_mix_k = np.exp(numerator / denominator)
        
    else:
        raise ValueError(f"Invalid method: {method}. Valid methods are: 'gordon_taylor', 'fox', 'couchman_karasz'")
    
    # Convert back to Celsius
    tg_mix = tg_mix_k - 273.15
    
    return tg_mix


def predict_melting_point_depression(
    tm_pure: float,
    tg_polymer: float,
    drug_loading: float,
    interaction_parameter: Optional[float] = None
) -> float:
    """
    Predict the melting point depression of an API in an ASD formulation.
    
    Args:
        tm_pure (float): Melting point of the pure API in Celsius
        tg_polymer (float): Glass transition temperature of the polymer in Celsius
        drug_loading (float): Drug loading as weight fraction (0-1)
        interaction_parameter (float, optional): Flory-Huggins interaction parameter.
            If not provided, a neutral value (0.5) will be used.
    
    Returns:
        float: Predicted melting point in Celsius
        
    Raises:
        ValueError: If required parameters are missing
    """
    # This is a simplified implementation of the Flory-Huggins theory
    # for melting point depression
    
    # Convert temperatures to Kelvin
    tm_pure_k = tm_pure + 273.15
    tg_polymer_k = tg_polymer + 273.15
    
    # Calculate volume fractions (approximated as weight fractions for simplicity)
    phi_api = drug_loading
    phi_polymer = 1 - drug_loading
    
    # Estimate interaction parameter if not provided
    if interaction_parameter is None:
        interaction_parameter = 0.5  # Neutral value
    
    # Calculate entropy of fusion (estimated)
    # This is a simplified approach and should be refined
    # Typically, the entropy of fusion is around 50-60 J/mol/K for small molecules
    delta_s_fusion = 55.0  # J/mol/K
    
    # Calculate melting point depression
    # The equation is derived from the Flory-Huggins theory
    r = 100  # Approximate degree of polymerization of the polymer
    
    # Calculate the depression factor
    depression_factor = (
        np.log(phi_api) + (1 - 1/r) * phi_polymer + interaction_parameter * phi_polymer**2
    )
    
    # Calculate depression in Kelvin
    delta_t = -tm_pure_k * depression_factor / delta_s_fusion
    
    # Calculate new melting point
    tm_mix_k = tm_pure_k + delta_t
    tm_mix = tm_mix_k - 273.15
    
    return tm_mix


def predict_crystallization_temperature(
    tg: float,
    tm: float,
    cooling_rate: float = 10.0
) -> float:
    """
    Predict the crystallization temperature during cooling.
    
    Args:
        tg (float): Glass transition temperature in Celsius
        tm (float): Melting point in Celsius
        cooling_rate (float, optional): Cooling rate in °C/min
    
    Returns:
        float: Predicted crystallization temperature in Celsius
    """
    # This is a simplified empirical model
    # Crystallization typically occurs between Tg and Tm
    # The position depends on cooling rate and material properties
    
    # Convert temperatures to Kelvin
    tg_k = tg + 273.15
    tm_k = tm + 273.15
    
    # Calculate reduced temperature range
    t_range = tm_k - tg_k
    
    # Estimate crystallization temperature
    # For slow cooling, crystallization occurs closer to Tm
    # For fast cooling, crystallization occurs closer to Tg
    # This is a simplified approach and should be refined
    
    # Cooling rate factor (0-1)
    # 0 for very slow cooling, 1 for very fast cooling
    rate_factor = min(1.0, cooling_rate / 100.0)
    
    # Position in the range (0 at Tm, 1 at Tg)
    position = 0.3 + 0.6 * rate_factor
    
    # Calculate crystallization temperature
    tc_k = tm_k - position * t_range
    tc = tc_k - 273.15
    
    return tc


def is_within_gordon_taylor_fragility(tg_measured: float, tg_predicted: float, tolerance: float = 5.0) -> bool:
    """
    Check if the measured Tg value falls within the predicted range for a Gordon-Taylor model.
    If the API-polymer mixture follows the Gordon-Taylor equation, the measured Tg should be
    close to the predicted value.
    
    Args:
        tg_measured (float): Measured glass transition temperature in Celsius
        tg_predicted (float): Predicted glass transition temperature in Celsius
        tolerance (float, optional): Tolerance in Celsius
    
    Returns:
        bool: True if the measured Tg is within the predicted range
    """
    return abs(tg_measured - tg_predicted) <= tolerance