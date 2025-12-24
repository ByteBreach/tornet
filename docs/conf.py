import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "TorNet"
author = "mrfidal"
release = "2.0.1"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]

templates_path = ["_templates"]
exclude_patterns = []

html_theme = "sphinx_rtd_theme"

html_title = "TorNet Documentation"
