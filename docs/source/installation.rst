Installation
============

Requirements
-----------

ASDii requires Python 3.9 or later. The following packages are required:

- NumPy: Numerical operations
- SciPy: Scientific computing
- Pandas: Data manipulation
- RDKit: Cheminformatics and molecular property calculation
- Scikit-learn: Machine learning models
- Matplotlib: Visualization
- Seaborn: Enhanced visualization
- Mordred: Molecular descriptor calculation
- PyYAML: YAML file handling

Basic Installation
-----------------

The simplest way to install ASDii is using pip:

.. code-block:: bash

   pip install asdii

This will install ASDii and all its required dependencies.

Development Installation
-----------------------

To install ASDii for development:

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/example/asdii.git
      cd asdii

2. Install in development mode:

   .. code-block:: bash

      pip install -e ".[dev]"

This will install ASDii in development mode along with additional development dependencies like pytest, black, and Sphinx.

Optional Dependencies
--------------------

ASDii has several optional dependency groups:

.. code-block:: bash

   # Development tools
   pip install "asdii[dev]"

   # Jupyter notebook support
   pip install "asdii[notebooks]"

   # Machine learning extensions
   pip install "asdii[ml]"

Verify Installation
------------------

To verify that ASDii is correctly installed:

.. code-block:: python

   import asdii
   print(asdii.__version__)

You should see the version number of the installed ASDii package.