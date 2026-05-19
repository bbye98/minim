from __future__ import annotations
from datetime import datetime
from pathlib import Path
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from sphinx.application import Sphinx

sys.path.insert(0, f"{Path(__file__).resolve().parents[2]}/src")
from minim import __version__


project = "Minim"
author = "Benjamin Ye"
copyright = f"2023–{datetime.now().year} Benjamin Ye"
version = release = __version__

extensions = [
    "numpydoc",
    "sphinx_copybutton",
    "sphinx_design",
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

html_favicon = "../../assets/favicon.ico"
html_logo = "../../assets/icon.svg"
html_show_sourcelink = False
html_static_path = ["_static"]
html_theme = "shibuya"
html_theme_options = {"accent_color": "gray", "toctree_maxdepth": 6}


autodoc_bases_to_skip = (tuple,)


def skip_inherited_members(
    app: Sphinx, what: str, name: str, obj: Any, skip: bool, options: Any
) -> bool:
    """
    Exclude inherited, un-overridden methods from specific base classes.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Sphinx application.

    what : str
        Type of the object the docstring belongs to.

    name : str
        Fully qualified name of the object.

    obj : Any
        Python object being documented.

    skip : bool
        Whether the member is already intended to be skipped.

    options: Any
        Options given to the directive.

    Returns
    -------
    skip : bool
        Whether to skip the member.
    """
    if what == "class":
        for base_class in autodoc_bases_to_skip:
            if (
                base_member := getattr(base_class, name, None)
            ) is not None and obj is base_member:
                return True
    return skip


def setup(app: Sphinx) -> None:
    """
    Initialize the Sphinx extension and register custom hooks.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Sphinx application.
    """
    app.add_css_file("custom.css")
    app.connect("autodoc-skip-member", skip_inherited_members)
