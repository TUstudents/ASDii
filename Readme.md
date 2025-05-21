# ASDii: Amorphous Solid Dispersion Intelligent Insights

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: CC BY-NC-SA 4.0](https://licensebuttons.net/l/by-nc-sa/4.0/80x15.png)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

## DISCLAIMER

⚠️ Important Notice:
This library is currently in a pre-alpha, developmental stage and is provided strictly for educational, conceptual exploration, and brainstorming purposes only.
It is NOT intended for productive, commercial, or research decision-making use where accurate quantitative predictions are required. It is broken by design and likely never be fixed.

## Overview

ASDii (Amorphous Solid Dispersion Intelligent Insights) is a Python library designed to assist pharmaceutical scientists in the development of stable amorphous solid dispersion (ASD) formulations. It provides computational tools to predict ASD formation, stability, and optimal formulation parameters before conducting costly experiments.

## Problem Statement

Amorphous solid dispersions are an important formulation technique to improve the solubility and bioavailability of poorly soluble drugs. However, developing stable ASD formulations involves significant trial and error, which is both time-consuming and expensive. ASDii aims to reduce this burden by providing predictive tools that can screen APIs, polymers, drug loading capacities, and process parameters to identify the most promising candidates for experimental validation.

## Key Features

- Prediction of ASD formation feasibility
- Assessment of long-term stability
- Optimization of drug loading capacities
- API-polymer compatibility screening
- Process parameter recommendations
- Thermodynamic and kinetic stability modeling
- Property calculation and visualization tools

## Target Users

ASDii is designed for pharmaceutical scientists, formulation experts, and researchers working with amorphous solid dispersions who need computational tools to guide experimental design and reduce development costs.

## Installation

```bash
pip install asdii
```

## Quick Start

```python
from asdii import API, Polymer, ASDFormulation

# Create API and polymer instances
ibuprofen = API.from_smiles("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O")
pvp = Polymer.from_name("PVP K30")

# Create and analyze a formulation
formulation = ASDFormulation(ibuprofen, pvp, drug_loading=0.3)
stability_result = formulation.predict_stability()
print(stability_result)
```

## Documentation

For detailed documentation, visit [https://asdii.readthedocs.io](https://asdii.readthedocs.io)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use ASDii in your research, please cite:

```
[Citation information will be provided upon publication]
```