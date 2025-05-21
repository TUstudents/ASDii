"""
ASDii: Amorphous Solid Dispersion Intelligent Insights
=====================================================

ASDii is a Python library designed to assist pharmaceutical scientists in the
development of stable amorphous solid dispersion (ASD) formulations. It provides
computational tools to predict ASD formation, stability, and optimal formulation
parameters before conducting costly experiments.

Core Components
--------------
- API: Representation of active pharmaceutical ingredients
- Polymer: Representation of carrier polymers
- ASDFormulation: Representation of an API-polymer formulation
- ProcessParameters: Representation of manufacturing parameters
- MaterialsDatabase: Database of APIs and polymers
- PolymerScreener: Tool for screening polymers for a given API
- LoadingOptimizer: Tool for optimizing drug loading
- StabilityPredictor: Tool for predicting ASD stability

Example Usage
------------
>>> from asdii import API, Polymer, ASDFormulation
>>> ibuprofen = API.from_smiles("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O")
>>> pvp = Polymer.from_name("PVP K30")
>>> formulation = ASDFormulation(ibuprofen, pvp, drug_loading=0.3)
>>> stability_result = formulation.predict_stability()
>>> print(stability_result)
"""

# Version information
__version__ = "0.1.0"

# Import core classes
from asdii.core.api import API
from asdii.core.polymer import Polymer
from asdii.core.formulation import ASDFormulation
from asdii.core.process import ProcessParameters

# Import database classes
from asdii.database.materials_db import MaterialsDatabase

# Import screening classes
from asdii.screening.polymer_screener import PolymerScreener

# Import predictor classes
from asdii.predictors.stability import StabilityPredictor
from asdii.predictors.loading import LoadingOptimizer

# Define public API
__all__ = [
    # Core classes
    "API",
    "Polymer",
    "ASDFormulation",
    "ProcessParameters",
    
    # Database classes
    "MaterialsDatabase",
    
    # Screening classes
    "PolymerScreener",
    
    # Predictor classes
    "StabilityPredictor",
    "LoadingOptimizer",
    
    # Version info
    "__version__",
]