"""
Pytest fixtures for the ASDii library tests.
"""

import pytest
from unittest.mock import MagicMock

from asdii.core.api import API
from asdii.core.polymer import Polymer
from asdii.core.formulation import ASDFormulation


@pytest.fixture
def mock_rdkit_mol():
    """Create a mock RDKit Mol object."""
    return MagicMock()


@pytest.fixture
def sample_api(mock_rdkit_mol):
    """Create a sample API object for testing."""
    return API(
        name="Ibuprofen",
        smiles="CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",
        mol=mock_rdkit_mol,
        molecular_weight=206.29,
        melting_point=76.0,
        glass_transition_temp=-45.0,
        log_p=3.97,
        solubility_parameters={
            'dispersive': 18.2,
            'polar': 3.8,
            'hydrogen': 8.0,
            'total': 20.0
        }
    )


@pytest.fixture
def sample_polymer(mock_rdkit_mol):
    """Create a sample Polymer object for testing."""
    return Polymer(
        name="PVP K30",
        type="vinyl",
        monomer_smiles="C1CCNC(=O)C1",
        molecular_weight=50000,
        glass_transition_temp=149.0,
        solubility_parameters={
            'dispersive': 17.0,
            'polar': 8.0,
            'hydrogen': 12.0,
            'total': 22.2
        },
        hydrophilicity=0.85,
        hygroscopicity=0.80
    )


@pytest.fixture
def sample_formulation(sample_api, sample_polymer):
    """Create a sample ASDFormulation object for testing."""
    formulation = ASDFormulation(
        api=sample_api,
        polymer=sample_polymer,
        drug_loading=0.3,
        process_method="hot_melt_extrusion",
        temperature=180.0,
        screw_speed=100.0
    )
    
    # Calculate some properties
    formulation.predicted_tg = 100.0
    formulation.predicted_miscibility = 0.75
    formulation.predicted_stability = {
        'score': 0.8,
        'thermodynamic': 0.85,
        'kinetic': 0.75,
        'confidence': 0.7,
        'major_factors': [
            ('Glass transition temperature', 0.9),
            ('API-polymer miscibility', 0.8),
            ('Drug loading', 0.7)
        ],
        'shelf_life_estimate': 36
    }
    
    return formulation


@pytest.fixture
def common_polymers(mock_rdkit_mol):
    """Create a list of common polymers for testing."""
    return [
        Polymer(
            name="PVP K30",
            type="vinyl",
            molecular_weight=50000,
            glass_transition_temp=149.0,
            solubility_parameters={
                'dispersive': 17.0,
                'polar': 8.0,
                'hydrogen': 12.0,
                'total': 22.2
            },
            hydrophilicity=0.85,
            hygroscopicity=0.80
        ),
        Polymer(
            name="HPMC",
            type="cellulosic",
            molecular_weight=22000,
            glass_transition_temp=175.0,
            solubility_parameters={
                'dispersive': 18.0,
                'polar': 8.6,
                'hydrogen': 11.9,
                'total': 23.3
            },
            hydrophilicity=0.70,
            hygroscopicity=0.65
        ),
        Polymer(
            name="Soluplus",
            type="graft copolymer",
            molecular_weight=90000,
            glass_transition_temp=70.0,
            solubility_parameters={
                'dispersive': 17.5,
                'polar': 7.0,
                'hydrogen': 9.0,
                'total': 20.9
            },
            hydrophilicity=0.55,
            hygroscopicity=0.45
        )
    ]