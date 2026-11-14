"""Sphinx settings for the demo project's user guide."""

import sys
from pathlib import Path

# The link helpers page documents demo/links.py, so the build has to import it.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

project = "django-mvp-sphinx demo"
extensions = [
    "mvp_sphinx.navigation",
    "myst_parser",
    "sphinx_design",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
]
autosummary_generate = False
todo_include_todos = True

# Everything MyST adds on top of CommonMark that needs no extra package.
myst_enable_extensions = [
    "amsmath",
    "attrs_block",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]
myst_heading_anchors = 3
myst_substitutions = {"product": "django-mvp-sphinx"}
suppress_warnings = ["myst.strikethrough"]
