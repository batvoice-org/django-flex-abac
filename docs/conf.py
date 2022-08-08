# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'django-flex-abac'
copyright = '2021, Batvoice AI'
author = 'Batvoice AI'

# The full version, including alpha/beta/rc tags
release = '0.0.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.autodoc',
    'sphinxcontrib.httpdomain'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

import sys
import os
# # sys.path.append(os.path.abspath('../../'))
# sys.path.append('/home/nestor/batvoice/poc/django-flex-rbac')
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'example.settings')

import os
import sys
import django
from django.conf import settings
import warnings

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '_ext')))
# sys.path.append(os.path.abspath('../..'))

# settings.configure(
#     INSTALLED_APPS=[
#         'django.contrib.contenttypes',
#         'polymorphic',
#     ],
# )
# django.setup()
# from polymorphic.base import ManagerInheritanceWarning
# warnings.filterwarnings('ignore', category=ManagerInheritanceWarning)
#
sys.path.append('/home/nestor/batvoice/poc/django-flex-rbac')

import configparser
config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'setup.cfg')))
with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'VERSION')), "r") as f:
    version = f.read()

settings.configure(
    INSTALLED_APPS=[
        'flex_abac',
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'treebeard',
        'polymorphic',
    ],
)
django.setup()

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

rst_prolog = """
:github_url: https://github.com/batvoice-org/django-flex-rbac
"""

html_theme_options = {
    'display_version': True,
}