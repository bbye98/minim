"""
Metadata containers and tag managers for various media formats.
"""

from . import id3
from ._vorbis import VorbisComment
from .id3._core import ID3v1, ID3v2

__all__ = ["id3", "ID3v1", "ID3v2", "VorbisComment"]  # noqa: RUF022
