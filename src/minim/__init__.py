import configparser
from pathlib import Path
import tempfile
import warnings

warnings.formatwarning = lambda message, *args, **kwargs: f"Warning: {message}"

HOME_DIR = Path.home()
TEMP_DIR = Path(tempfile.gettempdir())

config = configparser.ConfigParser()
config.read(HOME_DIR / "minim.cfg")

__all__ = ["audio", "itunes", "spotify", "tidal", "utility"]