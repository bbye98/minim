import configparser
from pathlib import Path
import tempfile

HOME_DIR = Path.home()
TEMP_DIR = Path(tempfile.gettempdir())
ILLEGAL_CHARACTERS = {ord(c): '_' for c in '<>:"/\|?*'}

config = configparser.ConfigParser()
config.read(HOME_DIR / "minim.cfg")

__all__ = ["audio", "itunes", "spotify", "tidal", "utility"]