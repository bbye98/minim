"""
MPEG-4 Part 14 (MP4) file handlers and stream information reporters.
"""

from ._boxes import MP4Box, UnknownMP4Box
from ._core import MP4Audio, MP4MetadataView

_mp4_boxes = {
    cls.__name__: cls
    for cls in sorted(
        set(MP4Box._REGISTRY.values()), key=lambda cls: cls.__name__
    )
}
globals().update(_mp4_boxes)

__all__ = ["MP4Audio", "MP4MetadataView", *_mp4_boxes, "UnknownMP4Box"]
