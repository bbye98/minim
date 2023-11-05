import configparser
from pathlib import Path
import tempfile

VERSION = "1.0.0"
HOME_DIR = Path.home()
TEMP_DIR = Path(tempfile.gettempdir())
ILLEGAL_CHARACTERS = {ord(c): '_' for c in '<>:"/\\|?*'}

config = configparser.ConfigParser()
config.read(HOME_DIR / "minim.cfg")
if not config.has_section("minim"):
    config["minim"] = {"version": VERSION}
    with open(HOME_DIR / "minim.cfg", "w") as f:
        config.write(f)

from . import audio, itunes, qobuz, spotify, tidal, utility

__all__ = ["audio", "itunes", "qobuz", "spotify", "tidal", "utility"]