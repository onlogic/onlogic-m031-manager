"""
Configuration file for Sphinx documentation

PDF generation: 

cd /docs/ 

then run:

sphinx-build -b pdf source build/pdf


pip install sphinx rst2pdf sphinx_rtd_theme

"""
import os
import sys

# Add the project source directory to the path
sys.path.insert(0, os.path.abspath('../..'))  # This will include the src directory

# -- Project information -----------------------------------------------------
project = 'OnLogicM031Manager'
copyright = '2025, nick.hanna@onlogic.com, fwengineeringteam@onlogic.com'
author = 'nick.hanna@onlogic.com, fwengineeringteam@onlogic.com'
version = release = '0.0.1'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',       # Generate API documentation
    'sphinx.ext.autosummary',   # Generate summary tables
    'sphinx.ext.viewcode',      # Add links to source code
    'sphinx.ext.napoleon',      # Support for Google-style docstrings
    'rst2pdf.pdfbuilder',       # PDF generation
]

# Napoleon settings for Google-style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True

# Add any paths that contain templates here, relative to this directory
templates_path = ['_templates']

# List of patterns to exclude from source files
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Options for PDF output --------------------------------------------------
pdf_documents = [(
    'index',
    'OnLogicM031Manager',
    'OnLogic M031 Manager Documentation',
    'nick.hanna@onlogic.com, fwengineeringteam@onlogic.com'
)]
pdf_stylesheets = ['sphinx', 'a4']
pdf_toc_depth = 3
pdf_use_index = True
pdf_use_modindex = True