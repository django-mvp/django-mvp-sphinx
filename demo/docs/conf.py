"""Sphinx settings for the demo project's user guide."""

import sys
from pathlib import Path

# The link helpers page documents demo/links.py, so the build has to import it.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

project = "django-mvp-sphinx demo"
extensions = [
    "mvp_sphinx.navigation",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]
autosummary_generate = False
