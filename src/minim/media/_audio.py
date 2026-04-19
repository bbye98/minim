from __future__ import annotations
from abc import ABC, abstractmethod
from copy import deepcopy
import hashlib
import mmap
from pathlib import Path
from typing import TYPE_CHECKING
import warnings

from ._metadata import VorbisComment

if TYPE_CHECKING:
    from typing import Any

    from ._metadata import AudioTags


class Audio(ABC):
    """
    Abstract base class for audio files.
    """

    # __slots__ = ()

    def __init__(self, file_path: str | Path, /) -> None:
        """ """
        self._file_path = Path(file_path).expanduser().resolve()
        self._load()

    @abstractmethod
    def _load(self) -> None:
        """ """
        ...

    # @property
    # @abstractmethod
    # def info(self) -> dict[str, Any]:
    #     """ """
    #     return deepcopy(self._info)

    # @property
    # @abstractmethod
    # def metadata(self) -> dict[str, Any]:
    #     """ """
    #     return deepcopy(self._metadata)

    @property
    def tags(self) -> AudioTags:
        """ """
        return self._tags


class FLACAudio(Audio):
    """
    FLAC audio file.
    """

    # __slots__ = ()

    def _load(self) -> None:
        """ """
        file_path = self._file_path
        self._file = open(file_path, "rb")
        mm = self._mmap = mmap.mmap(
            self._file.fileno(), 0, access=mmap.ACCESS_READ
        )
        view = self._memoryview = memoryview(mm)

        offset = 4
        if view[:offset] != b"fLaC":
            raise ValueError(f"{file_path} is not a valid FLAC file.")

        self._metadata = {}
        block_header = 0x7F
        while not block_header & 0x80:
            block_header = view[offset]
            offset += 1

            end_offset = offset + 3
            block_size = int.from_bytes(view[offset:end_offset])
            offset = end_offset

            end_offset = offset + block_size
            block_data = view[offset:end_offset]
            offset = end_offset

            match block_type := block_header & 0x7F:
                case 0:  # STREAMINFO
                    pass
                case 1:  # PADDING
                    pass
                case 2:  # APPLICATION
                    pass
                case 3:  # SEEKTABLE
                    pass
                case 4:  # VORBIS_COMMENT
                    self._tags = VorbisComment(block_data)
                    self._metadata["VORBIS_COMMENT"] = self._tags._fields
                case 5:  # CUESHEET
                    pass
                case 6:  # PICTURE
                    pass
                case 127:
                    raise ValueError(
                        "Metadata block with invalid block "
                        f"type found in '{file_path}'."
                    )
                case _:
                    warnings.warn(
                        "Skipping metadata block with block "
                        f"type {block_type} (reserved) found "
                        f"in '{file_path}'."
                    )

    # def _close(self) -> None:
    #     """ """
    #     self._memoryview.release()
    #     self._mmap.close()
    #     self._file.close()
