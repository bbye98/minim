import configparser
from importlib.util import find_spec
from pathlib import Path
import tempfile

__version__ = "2.0.0"

FOUND = {lib: find_spec(lib) is not None for lib in {"playwright"}}
HOME_DIR = Path.home()
TEMP_DIR = Path(tempfile.gettempdir())
ILLEGAL_CHARS = {ord(c): "_" for c in '"*/:<>?\\|'}

config_file = HOME_DIR / "minim.ini"
config = configparser.ConfigParser()
config.read(config_file)
if not config.has_section("minim"):
    config["minim"] = {"version": __version__}
    with open(config_file, "w") as f:
        config.write(f)
