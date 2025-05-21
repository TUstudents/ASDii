ASDii Documentation
==================

.. image:: https://img.shields.io/badge/python-3.9+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python

.. image:: https://img.shields.io/badge/license-MIT-green.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License

Welcome to ASDii's documentation. ASDii (Amorphous Solid Dispersion Intelligent Insights) is a Python library designed to assist pharmaceutical scientists in the development of stable amorphous solid dispersion (ASD) formulations. It provides computational tools to predict ASD formation, stability, and optimal formulation parameters before conducting costly experiments.

Features
--------

- Prediction of ASD formation feasibility
- Assessment of long-term stability
- Optimization of drug loading capacities
- API-polymer compatibility screening
- Process parameter recommendations
- Thermodynamic and kinetic stability modeling
- Property calculation and visualization tools

Getting Started
--------------

Installation
~~~~~~~~~~~

.. code-block:: bash

   pip install asdii

Quick Example
~~~~~~~~~~~~

.. code-block:: python

   from asdii import API, Polymer, ASDFormulation

   # Create API and polymer instances
   ibuprofen = API.from_smiles("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O")
   pvp = Polymer.from_name("PVP K30")

   # Create and analyze a formulation
   formulation = ASDFormulation(ibuprofen, pvp, drug_loading=0.3)
   stability_result = formulation.predict_stability()
   print(stability_result)

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quickstart
   tutorials/index
   examples/index

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/core
   api/calculators
   api/predictors
   api/screening
   api/database
   api/utils
   api/visualization

.. toctree::
   :maxdepth: 1
   :caption: Development

   contributing
   changelog

.. toctree::
   :maxdepth: 1
   :caption: Background

   theory/asd
   theory/solubility_parameters
   theory/glass_transition
   theory/stability

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`