# noqa: INP001, D100
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import pathlib
import sys

DOC_ROOT = pathlib.Path(__file__).parent
PROJECT_ROOT = DOC_ROOT.parent

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, str(PROJECT_ROOT))
from fastkml import about  # noqa: E402

# General information about the project.
project = "FastKML"
copyright = "2014 -2024, Christian Ledermann & Ian Lee"  # noqa: A001
author = "Christian Ledermann"
# The short X.Y version.
version = ".".join(about.__version__.split(".")[:2])
# The full version, including alpha/beta/rc tags.
release = about.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.viewcode",
]
autosummary_generate = True


templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

root_doc = "index"


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

html_theme = "alabaster"
html_static_path = ["_static"]
try:
    import sphinx_rtd_theme

    html_theme = "sphinx_rtd_theme"
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
except ImportError:
    pass

html_context = {
    "display_github": True,  # Integrate GitHub
    "github_user": "cleder",  # Username
    "github_repo": "fastkml",  # Repo name
    "github_version": "main",  # Version
    "conf_py_path": "/docs/",  # Path in the checkout to the docs root
}
