from ._core import ID3v2Flags, ID3v2Padding
from ._frames import ID3v2Frame, ID3v2FrameFlags, UnknownID3v2Frame

_id3v2_frames = {
    cls.__name__: cls
    for cls in sorted(
        set(ID3v2Frame._REGISTRY.values()), key=lambda cls: cls.__name__
    )
}
globals().update(_id3v2_frames)

__all__ = [  # noqa: PLE0604
    "ID3v2Flags",
    "ID3v2Padding",
    "ID3v2FrameFlags",
    *_id3v2_frames,
    "UnknownID3v2Frame",
]
