from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
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
        self._file_path = Path(file_path).expanduser().resolve(strict=True)
        self.open()

    @abstractmethod
    def open(self) -> None:
        """ """
        self.close()
        self._file = open(self._file_path, "rb")
        self._mmap = mmap.mmap(self._file.fileno(), 0, access=mmap.ACCESS_READ)
        self._memoryview = memoryview(self._mmap)

    # @property
    # @abstractmethod
    # def info(self) -> dict[str, Any]:
    #     """ """
    #     return self._info

    # @property
    # @abstractmethod
    # def metadata(self) -> dict[str, Any]:
    #     """ """
    #     return self._metadata

    @property
    def tags(self) -> AudioTags:
        """ """
        return self._tags

    def close(self) -> None:
        """ """
        if hasattr(self, "_memoryview"):
            self._memoryview.release()
            del self._memoryview
        if hasattr(self, "_mmap") and not self._mmap.closed:
            self._mmap.close()
            del self._mmap
        if hasattr(self, "_file") and not self._file.closed:
            self._file.close()
            del self._file


@dataclass
class FLACMetadataBlock:
    """
    FLAC metadata block.
    """

    block_type: int
    block_size: int
    block_data: Any


class FLACAudio(Audio):
    """
    FLAC audio file.
    """

    # __slots__ = ()

    def open(self) -> None:
        """ """
        super().open()
        file_path = self._file_path
        view = self._memoryview

        offset = 4
        if view[:offset] != b"fLaC":
            raise ValueError(f"{file_path} is not a valid FLAC file.")

        self._metadata = []
        block_header = 0x7F
        while not block_header & 0x80:
            block_header = view[offset]
            offset += 1

            end_offset = offset + 3
            block_size = int.from_bytes(
                view[offset:end_offset], byteorder="big"
            )  # memoryview
            offset = end_offset

            end_offset = offset + block_size
            block_data = view[offset:end_offset]
            offset = end_offset

            match block_type := block_header & 0x7F:
                case 0:  # STREAMINFO
                    if self._metadata:
                        raise RuntimeError(
                            "The STREAMINFO block is not the first "
                            f"metadata block in '{file_path}'."
                        )

                    if block_size != 34:
                        raise ValueError(
                            f"Invalid STREAMINFO block size in '{file_path}'."
                        )

                    minimum_block_size = int.from_bytes(
                        block_data[:2], byteorder="big"
                    )
                    maximum_block_size = int.from_bytes(
                        block_data[2:4], byteorder="big"
                    )
                    if minimum_block_size < 16:
                        raise ValueError(
                            "Invalid minimum stream block size of "
                            f"{minimum_block_size} in '{file_path}'."
                        )
                    if maximum_block_size < 16:
                        raise ValueError(
                            "Invalid maximum stream block size of "
                            f"{maximum_block_size} in '{file_path}'."
                        )

                    self._metadata.append(
                        FLACMetadataBlock(
                            block_type=block_type,
                            block_size=block_size,
                            block_data={
                                "minimum_block_size": minimum_block_size,
                                "maximum_block_size": maximum_block_size,
                                "minimum_frame_size": int.from_bytes(
                                    block_data[4:7], byteorder="big"
                                ),
                                "maximum_frame_size": int.from_bytes(
                                    block_data[7:10], byteorder="big"
                                ),
                                "sample_rate": int.from_bytes(
                                    block_data[10:13], byteorder="big"
                                )
                                >> 4,
                                "num_channels": ((block_data[12] & 0x0E) >> 1)
                                + 1,
                                "bits_per_sample": (
                                    (block_data[12] & 0x01) << 4
                                )
                                + ((block_data[13] & 0xF0) >> 4)
                                + 1,
                                "total_samples": (
                                    (block_data[13] & 0x0F) << 32
                                )
                                + int.from_bytes(
                                    block_data[14:18], byteorder="big"
                                ),
                                "md5": block_data[18:].hex(),
                            },
                        )
                    )
                case 1:  # PADDING
                    self._metadata.append(
                        FLACMetadataBlock(
                            block_type=block_type,
                            block_size=block_size,
                            block_data=None,
                        )
                    )
                case 2:  # APPLICATION
                    self._metadata.append(
                        FLACMetadataBlock(
                            block_type=block_type,
                            block_size=block_size,
                            block_data={
                                "app_id": block_data[:4],  # memoryview
                                "app_data": block_data[4:],  # memoryview
                            },
                        )
                    )
                case 3:  # SEEKTABLE
                    num_seek_points, remainder = divmod(block_size, 18)
                    if remainder:
                        raise ValueError(
                            f"Invalid SEEKTABLE block size in '{file_path}'."
                        )

                    self._metadata.append(
                        FLACMetadataBlock(
                            block_type=block_type,
                            block_size=block_size,
                            block_data=[
                                (
                                    int.from_bytes(
                                        block_data[
                                            (i := 18 * seek_point_index) : (
                                                j := i + 8
                                            )
                                        ]
                                    ),
                                    int.from_bytes(
                                        block_data[j : (k := j + 8)]
                                    ),
                                    int.from_bytes(block_data[k : k + 2]),
                                )
                                for seek_point_index in range(num_seek_points)
                            ],
                        )
                    )
                case 4:  # VORBIS_COMMENT
                    self._tags = VorbisComment(block_data)
                    self._metadata.append(
                        FLACMetadataBlock(
                            block_type=block_type,
                            block_size=block_size,
                            block_data=self._tags._fields,
                        )
                    )
                case 5:  # CUESHEET
                    pass
                case 6:  # PICTURE
                    pass
                case 127:
                    raise ValueError(
                        "Metadata block with invalid block type found "
                        f"in '{file_path}'."
                    )
                case _:
                    warnings.warn(
                        "Skipping metadata block with block type "
                        f"{block_type} (reserved) found in "
                        f"'{file_path}'."
                    )

        if not self._metadata or self._metadata[0].block_type != 0:
            raise RuntimeError(
                f"A STREAMINFO block was not found in '{file_path}'."
            )
