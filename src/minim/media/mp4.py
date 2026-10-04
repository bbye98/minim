"""
MPEG-4 Part 14 (MP4) audio file handler and stream information reporter.
"""

from __future__ import annotations

from dataclasses import dataclass

from ._shared import Audio
from .metadata._shared import AudioStreamInfo, AudioTags


# @dataclass(frozen=True, kw_only=True, repr=False, slots=True)
# class MP4StreamInfo(AudioStreamInfo):
#     """
#     MP4 :code:`moov > trak > mdia > minf > stbl > stsd > alac/mp4a` or
#     audio stream information.
#     """


# class MP4ItemListBox(AudioTags):
#     """
#     MP4 :code:`moov > udta > meta > ilst` box or metadata container.
#     """


# class MP4Audio(Audio):
#     """
#     MP4 audio file.

#     .. note::

#        Metadata structures and ancillary information are loaded from
#        the audio file when the object is instantiated.

#        .. seealso::

#           :meth:`load_metadata` – Load metadata structures and ancillary
#           information from the audio file.
#     """
