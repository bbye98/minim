from importlib.util import find_spec
from pathlib import Path

__all__ = ["api"]
__version__ = "2.0.0-alpha"

ILLEGAL_CHARS = {ord(c): "_" for c in '"*/:<>?\\|'}
FOUND = {lib: find_spec(lib) is not None for lib in {"playwright"}}
HOME_DIR = Path.home()

MINIM_DIR = HOME_DIR / ".minim"
if not MINIM_DIR.exists():
    MINIM_DIR.mkdir()
