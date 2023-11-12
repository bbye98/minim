import base64
import configparser
import datetime
import hashlib
import json
import logging
import os
import re
import pathlib
import secrets
import subprocess
import tempfile
import time
from typing import Any, Union
import urllib
import warnings
import webbrowser

import requests

try:
    from playwright.sync_api import sync_playwright
    FOUND_PLAYWRIGHT = True
except ModuleNotFoundError:
    FOUND_PLAYWRIGHT = False

_ = subprocess.run(["ffmpeg", "-version"], capture_output=True)
FOUND_FFMPEG = _.returncode == 0
FFMPEG_CODECS = {}
if FOUND_FFMPEG:
    FFMPEG_CODECS["aac"] = (
        "libfdk_aac" if FOUND_FFMPEG and b"--enable-libfdk-aac" in _.stdout
        else "aac"
    )
    FFMPEG_CODECS["vorbis"] = (
        "libvorbis" if FOUND_FFMPEG and b"--enable-libvorbis" in _.stdout 
        else "vorbis -strict experimental"
    )
else:
    wmsg = ("FFmpeg was not found, so certain key features in Minim "
            "are unavailable. To install FFmpeg, visit "
            "https://ffmpeg.org/download.html.")
    warnings.warn(wmsg)

VERSION = "1.0.0"
DIR_HOME = pathlib.Path.home()
DIR_TEMP = pathlib.Path(tempfile.gettempdir())
ILLEGAL_CHARACTERS = {ord(c): '_' for c in '<>:"/\\|?*'}

config = configparser.ConfigParser()
config.read(DIR_HOME / "minim.cfg")
if not config.has_section("minim"):
    config["minim"] = {"version": VERSION}
    with open(DIR_HOME / "minim.cfg", "w") as f:
        config.write(f)

from . import audio, itunes, qobuz, spotify, tidal, utility # noqa: E402

__all__ = [
    "base64", "datetime", "hashlib", "json", "logging", "os", "re", "requests",
    "secrets", "subprocess", "time", "urllib", "warnings", "webbrowser",
    "audio", "itunes", "qobuz", "spotify", "tidal", "utility",
    "FOUND_PLAYWRIGHT", "FOUND_FFMPEG", "FFMPEG_CODECS", "VERSION",
    "DIR_HOME", "DIR_TEMP", "ILLEGAL_CHARACTERS",
    "Any", "Union", "sync_playwright", "config"
]