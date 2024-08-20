import configparser
from importlib.util import find_spec
import pathlib
import shutil
import subprocess
import tempfile
import warnings

__all__ = [
    "audio",
    "discogs",
    "itunes",
    "qobuz",
    "spotify",
    "tidal",
    "utility",
    "FOUND_FFMPEG",
    "FOUND_FLASK",
    "FOUND_PLAYWRIGHT",
    "VERSION",
    "REPOSITORY_URL",
    "DIR_HOME",
    "DIR_TEMP",
    "ILLEGAL_CHARACTERS",
]

FOUND_FFMPEG = shutil.which("ffmpeg") is not None
FOUND_FLASK = find_spec("flask") is not None
FOUND_PLAYWRIGHT = find_spec("playwright") is not None

VERSION = "1.0.0"
REPOSITORY_URL = "https://github.com/bbye98/minim"

if FOUND_FFMPEG:
    _ = subprocess.run(["ffmpeg", "-version"], capture_output=True)
    FFMPEG_CODECS = {
        "aac": "libfdk_aac" if b"--enable-libfdk-aac" in _.stdout else "aac",
        "vorbis": (
            "libvorbis"
            if b"--enable-libvorbis" in _.stdout
            else "vorbis -strict experimental"
        ),
    }
    __all__.append("FFMPEG_CODECS")
else:
    wmsg = (
        "FFmpeg was not found, so certain key features in Minim "
        "are unavailable. To install FFmpeg, visit "
        "https://ffmpeg.org/download.html or use "
        "'conda install ffmpeg' if Conda is available."
    )
    warnings.warn(wmsg)

DIR_HOME = pathlib.Path.home()
DIR_TEMP = pathlib.Path(tempfile.gettempdir())
ILLEGAL_CHARACTERS = {ord(c): "_" for c in '<>:"/\\|?*'}

_config = configparser.ConfigParser()
_config.read(DIR_HOME / "minim.cfg")
if not _config.has_section("minim"):
    _config["minim"] = {"version": VERSION}
    with open(DIR_HOME / "minim.cfg", "w") as f:
        _config.write(f)

from . import audio, discogs, itunes, qobuz, spotify, tidal, utility  # noqa: E402
