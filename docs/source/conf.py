"""
Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

import os
import sys
import datetime

# Add the project root directory to the path
sys.path.insert(0, os.path.abspath('../../'))

# -- Project information -----------------------------------------------------
project = 'ASDii'
copyright = f'2025, ASDii Team'
author = 'ASDii Team'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.mathjax',
    'sphinx.ext.githubpages',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_title = 'ASDii Documentation'
html_logo = None
html_favicon = None

# -- Options for autodoc -----------------------------------------------------
autodoc_member_order = 'bysource'
autodoc_typehints = 'description'
autodoc_class_signature = 'separated'
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'special-members': '__init__',
    'exclude-members': '__dict__,__weakref__,__module__'
}

# -- Options for napoleon ----------------------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_keyword = True
napoleon_custom_sections = None

# -- Options for intersphinx -------------------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'matplotlib': ('https://matplotlib.org/stable/', None),
    'rdkit': ('https://www.rdkit.org/docs/', None),
}

# -- Options for myst_parser -------------------------------------------------
myst_enable_extensions = [
    'amsmath',
    'colon_fence',
    'deflist',
    'dollarmath',
    'html_image',
    'smartquotes',
    'substitution',
    'tasklist',
]