from importlib.util import find_spec
from pathlib import Path

import yaml

__version__ = "2.0.0"

ILLEGAL_CHARS = {ord(c): "_" for c in '"*/:<>?\\|'}
FOUND = {lib: find_spec(lib) is not None for lib in {"playwright"}}
HOME_DIR = Path.home()

# Load (or create) local token storage file
CONFIG_FILE = HOME_DIR / "minim.yaml"
if CONFIG_FILE.exists():
    with CONFIG_FILE.open() as f:
        config = yaml.safe_load(f)
else:
    config = {"version": __version__}
    with CONFIG_FILE.open("w") as f:
        yaml.safe_dump(config, f)
