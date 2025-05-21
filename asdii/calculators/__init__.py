"""
Property calculators for the ASDii library.

This package provides calculators for various properties of APIs, polymers,
and ASD formulations.
"""

from asdii.calculators.descriptors import calculate_molecular_descriptors, calculate_fragment_descriptors, calculate_molecular_properties
from asdii.calculators.solubility import calculate_solubility_parameters, calculate_hansen_distance, calculate_flory_huggins_parameter
from asdii.calculators.thermal import predict_glass_transition, predict_melting_point_depression

__all__ = [
    # Descriptors
    'calculate_molecular_descriptors',
    'calculate_fragment_descriptors',
    'calculate_molecular_properties',
    
    # Solubility
    'calculate_solubility_parameters',
    'calculate_hansen_distance',
    'calculate_flory_huggins_parameter',
    
    # Thermal
    'predict_glass_transition',
    'predict_melting_point_depression'
]