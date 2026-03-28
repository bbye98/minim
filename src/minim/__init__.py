"""
A Python library for semi-automated music tagging, featuring API clients
for major music services and integrated media file handlers.
"""

from importlib.util import find_spec
from pathlib import Path

__all__ = ["api"]
__version__ = "2.0.0-alpha"
REPOSITORY_URL = "https://github.com/bbye98/minim"

FOUND = {lib: find_spec(lib) is not None for lib in {"playwright"}}
ILLEGAL_CHARS = {ord(c): "_" for c in '"*/:<>?\\|'}
HOME_DIR = Path.home()
MINIM_DIR = HOME_DIR / ".minim"
if not MINIM_DIR.exists():
    MINIM_DIR.mkdir()
