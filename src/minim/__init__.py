from importlib.util import find_spec
from pathlib import Path

import yaml

__all__ = ["api"]
__version__ = "2.0.0"

ILLEGAL_CHARS = {ord(c): "_" for c in '"*/:<>?\\|'}
FOUND = {lib: find_spec(lib) is not None for lib in {"playwright"}}
HOME_DIR = Path.home()

# Load (or create) local token storage file
MINIM_DIR = HOME_DIR / ".minim"
if not MINIM_DIR.exists():
    MINIM_DIR.mkdir()
CONFIG_FILE = MINIM_DIR / "config.yaml"
if CONFIG_FILE.exists():
    with CONFIG_FILE.open() as f:
        config = yaml.safe_load(f)
else:
    config = {"version": __version__}
    with CONFIG_FILE.open("w") as f:
        yaml.safe_dump(config, f)
