from . import id3
from .id3._core import ID3v2
from ._vorbis import VorbisComment


__all__ = ["id3", "ID3v2", "VorbisComment"]
