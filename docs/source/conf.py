from datetime import datetime
import fnmatch
from pathlib import Path
import sys
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from sphinx.application import Sphinx

sys.path.insert(0, f"{Path(__file__).resolve().parents[2]}/src")
from minim import __version__  # noqa: E402

project = "Minim"
author = "Benjamin Ye"
copyright = f"2023–{datetime.now().year} Benjamin Ye"
version = release = __version__

extensions = [
    "myst_nb",
    "numpydoc",
    "sphinx_copybutton",
    "sphinx_inline_tabs",
    "sphinx_togglebutton",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.duration",
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]
exclude_patterns = ["_build"]
templates_path = ["_templates"]
toc_object_entries_show_parents = "hide"

autoclass_content = "both"
autosummary_generate = True
autosummary_ignore_module_all = False
autosummary_imported_members = True
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
}
numpydoc_show_class_members = False
togglebutton_hint = togglebutton_hint_hide = ""

html_favicon = "../../assets/minim/favicon.ico"
html_logo = "../../assets/minim/icon.svg"
html_show_sourcelink = False
html_static_path = ["_static"]
html_theme = "furo"
html_theme_options = {"sidebar_hide_name": True}


def setup(app: "Sphinx") -> None:
    app.add_css_file("authorization_scope_admonition.css")
