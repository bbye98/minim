import pathlib
import sys

sys.path.insert(0, f"{pathlib.Path(__file__).resolve().parents[2]}/src")

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "minim"
copyright = "2023, Benjamin Ye"
author = "Benjamin Ye"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_nb",
    "numpydoc",
    "sphinx_copybutton",
    "sphinx_togglebutton",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.duration",
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode"
]
exclude_patterns = ["_build"]
templates_path = ["_templates"]
toc_object_entries_show_parents = "hide"

autodoc_member_order = "bysource"
autosummary_generate = True
intersphinx_mapping = {
    "numpy": ("https://numpy.org/doc/stable/", None),
    "python": ("https://docs.python.org/3/", None)
}
myst_enable_extensions = ["colon_fence"]
myst_heading_anchors = 3
nb_execution_timeout = -1
numpydoc_show_class_members = False
togglebutton_hint = togglebutton_hint_hide = ""

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_favicon = "../../assets/favicon.ico"
html_logo = "../../assets/icon.svg"
html_show_sourcelink = False
html_static_path = ["_static"]
html_theme = "furo"
html_theme_options = {
    "sidebar_hide_name": True,
}