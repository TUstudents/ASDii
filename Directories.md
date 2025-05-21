# ASDii Directory Structure

The following directory structure follows the standard Python package layout as outlined in the SOP document. This structure organizes the code in a logical, maintainable way and facilitates future extensions.

```
ASDii/
├── asdii/                     # Main library source code package
│   ├── __init__.py            # Package initialization, version
│   ├── data/                  # Default data files (databases, models)
│   │   ├── __init__.py
│   │   ├── common_apis.json   # Database of common APIs with properties
│   │   ├── common_polymers.json # Database of common polymers with properties
│   │   └── trained_models/    # Pretrained prediction models
│   │
│   ├── core/                  # Core data structures/classes
│   │   ├── __init__.py
│   │   ├── api.py             # API class implementation
│   │   ├── polymer.py         # Polymer class implementation
│   │   ├── formulation.py     # ASDFormulation class implementation
│   │   └── process.py         # ProcessParameters class implementation
│   │
│   ├── calculators/           # Modules for specific calculations
│   │   ├── __init__.py
│   │   ├── descriptors.py     # Molecular descriptor calculators
│   │   ├── solubility.py      # Solubility parameter calculators
│   │   ├── thermal.py         # Thermal property calculators
│   │   ├── miscibility.py     # Miscibility calculators
│   │   └── mobility.py        # Molecular mobility calculators
│   │
│   ├── predictors/            # Modules for predictive logic
│   │   ├── __init__.py
│   │   ├── formation.py       # ASD formation predictors
│   │   ├── stability.py       # Stability predictors
│   │   ├── loading.py         # Drug loading optimizers
│   │   └── process.py         # Process parameter optimizers
│   │
│   ├── database/              # Database management
│   │   ├── __init__.py
│   │   ├── materials_db.py    # MaterialsDatabase implementation
│   │   ├── literature_db.py   # Literature database
│   │   └── db_utils.py        # Database utilities
│   │
│   ├── screening/             # Screening tools
│   │   ├── __init__.py
│   │   ├── polymer_screener.py # PolymerScreener implementation
│   │   ├── api_screener.py    # API screening tools
│   │   └── formulation_screener.py # Formulation screening tools
│   │
│   ├── reporting/             # Report generation
│   │   ├── __init__.py
│   │   ├── report_generator.py # ReportGenerator implementation
│   │   └── templates/         # Report templates
│   │       ├── formulation_report.md
│   │       ├── screening_report.md
│   │       └── stability_report.md
│   │
│   ├── visualization/         # Visualization tools
│   │   ├── __init__.py
│   │   ├── structure_viz.py   # Molecular structure visualization
│   │   ├── property_viz.py    # Property visualization
│   │   ├── stability_viz.py   # Stability visualization
│   │   └── phase_viz.py       # Phase diagram visualization
│   │
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       ├── smiles_parser.py   # SMILES parsing utilities
│       ├── file_io.py         # File I/O utilities
│       ├── unit_converter.py  # Unit conversion utilities
│       └── validation.py      # Validation utilities
│
├── docs/                      # Sphinx documentation
│   ├── source/
│   │   ├── conf.py
│   │   ├── index.rst
│   │   ├── installation.rst
│   │   ├── quickstart.rst
│   │   ├── tutorials/
│   │   ├── api_reference/
│   │   └── examples/
│   └── Makefile
│
├── examples/                  # Example scripts
│   ├── basic_usage.py
│   ├── polymer_screening.py
│   ├── loading_optimization.py
│   └── stability_prediction.py
│
├── notebooks/                 # Jupyter notebook tutorials
│   ├── 01_Getting_Started.ipynb
│   ├── 02_API_and_Polymer_Properties.ipynb
│   ├── 03_Formulation_Assessment.ipynb
│   ├── 04_Polymer_Screening.ipynb
│   └── 05_Advanced_Stability_Prediction.ipynb
│
├── tests/                     # Pytest unit and integration tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── fixtures/              # Test fixtures
│   │   ├── __init__.py
│   │   ├── api_fixtures.py
│   │   ├── polymer_fixtures.py
│   │   └── formulation_fixtures.py
│   ├── unit/                  # Unit tests
│   │   ├── __init__.py
│   │   ├── test_api.py
│   │   ├── test_polymer.py
│   │   ├── test_formulation.py
│   │   ├── test_calculations.py
│   │   └── test_predictions.py
│   └── integration/           # Integration tests
│       ├── __init__.py
│       ├── test_workflows.py
│       └── test_validation.py
│
├── .gitignore
├── LICENSE
├── pyproject.toml             # Project configuration (PEP 621)
├── README.md
└── requirements.txt           # Dependencies
```

## File Descriptions

### Package Root

- **__init__.py**: Package initialization file that exposes key classes and functions, defines version.
- **pyproject.toml**: Project configuration using PEP 621 format, includes build system, dependencies, and metadata.
- **LICENSE**: MIT license file.
- **README.md**: Project overview, installation instructions, and usage examples.

### Core Module

- **api.py**: Implements the `API` class for representing active pharmaceutical ingredients.
- **polymer.py**: Implements the `Polymer` class for representing carrier polymers.
- **formulation.py**: Implements the `ASDFormulation` class for representing ASD formulations.
- **process.py**: Implements the `ProcessParameters` class for representing manufacturing processes.

### Calculators Module

- **descriptors.py**: Implementations of molecular descriptor calculators.
- **solubility.py**: Implementations of solubility parameter calculators (Hildebrand, Hansen, etc.).
- **thermal.py**: Implementations of thermal property calculators (Tg, melting point, etc.).
- **miscibility.py**: Implementations of miscibility calculators (Flory-Huggins, etc.).
- **mobility.py**: Implementations of molecular mobility calculators (WLF, Adam-Gibbs, etc.).

### Predictors Module

- **formation.py**: Implementations of ASD formation predictors.
- **stability.py**: Implementations of stability predictors.
- **loading.py**: Implementations of drug loading optimizers.
- **process.py**: Implementations of process parameter optimizers.

### Database Module

- **materials_db.py**: Implementation of the `MaterialsDatabase` class for managing API and polymer data.
- **literature_db.py**: Implementation of a database for literature data on ASDs.
- **db_utils.py**: Utility functions for database operations.

### Screening Module

- **polymer_screener.py**: Implementation of the `PolymerScreener` class for screening polymers.
- **api_screener.py**: Tools for screening APIs for amorphization tendency.
- **formulation_screener.py**: Tools for screening multiple formulations.

### Reporting Module

- **report_generator.py**: Implementation of report generation tools.
- **templates/**: Markdown templates for various types of reports.

### Visualization Module

- **structure_viz.py**: Tools for visualizing molecular structures.
- **property_viz.py**: Tools for visualizing molecular and formulation properties.
- **stability_viz.py**: Tools for visualizing stability predictions.
- **phase_viz.py**: Tools for generating phase diagrams.

### Utils Module

- **smiles_parser.py**: Utilities for parsing SMILES strings.
- **file_io.py**: Utilities for file input/output operations.
- **unit_converter.py**: Utilities for converting between different units.
- **validation.py**: Utilities for validating inputs and outputs.

### Documentation

- **docs/**: Sphinx documentation source files and build scripts.

### Examples and Notebooks

- **examples/**: Example Python scripts demonstrating library usage.
- **notebooks/**: Jupyter notebooks with tutorials and case studies.

### Tests

- **tests/**: Unit and integration tests using pytest.
- **fixtures/**: Test fixtures for APIs, polymers, and formulations.

## Development Workflow

1. Start with implementing the core data structures in the `core/` module.
2. Implement basic property calculators in the `calculators/` module.
3. Create simple predictors in the `predictors/` module.
4. Develop database functionality in the `database/` module.
5. Implement screening tools in the `screening/` module.
6. Add reporting and visualization tools.
7. Create examples and notebooks.
8. Write tests for all implemented functionality.
9. Generate documentation.

## Future Extensions

The directory structure is designed to accommodate future extensions:

1. New predictive models can be added to the `predictors/` module.
2. Additional property calculators can be added to the `calculators/` module.
3. New visualization tools can be added to the `visualization/` module.
4. More advanced screening tools can be added to the `screening/` module.
5. Integration with external tools can be added in new modules.