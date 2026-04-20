from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
import warnings

from .._metadata import VorbisComment
from ._shared import AudioStreamInfo, Audio

if TYPE_CHECKING:
    from typing import Any


@dataclass(frozen=True, slots=True)
class FLACMetadataBlock:
    """
    FLAC metadata block.
    """

    block_type: int
    block_size: int
    block_data: Any


@dataclass(frozen=True, slots=True)
class FLACStreamInfo(AudioStreamInfo):
    """
    FLAC :code:`STREAMINFO` metadata block data.
    """

    minimum_block_size: int
    maximum_block_size: int
    minimum_frame_size: int
    maximum_frame_size: int
    md5: str


@dataclass(frozen=True, slots=True)
class FLACCueSheet:
    """
    FLAC :code:`CUESHEET` metadata block data.
    """

    media_catalog_number: str
    num_lead_in_samples: int
    is_cd: bool
    num_tracks: int
    tracks: tuple[FLACCueSheetTrack]


@dataclass(frozen=True, slots=True)
class FLACCueSheetTrack:
    """
    FLAC :code:`CUESHEET` metadata block track data.
    """

    offset: int
    track: int
    isrc: str
    is_audio: bool
    has_pre_emphasis: bool
    num_index_points: int
    index_points: tuple[tuple[int, int]]


class FLACAudio(Audio):
    """
    FLAC audio file.
    """

    METADATA_BLOCK_TYPES = {
        0: "STREAMINFO",
        1: "PADDING",
        2: "APPLICATION",
        3: "SEEKTABLE",
        4: "VORBIS_COMMENT",
        5: "CUESHEET",
        6: "PICTURE",
        127: "INVALID",
    }

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
                            block_data=FLACStreamInfo(
                                minimum_block_size=minimum_block_size,
                                maximum_block_size=maximum_block_size,
                                minimum_frame_size=int.from_bytes(
                                    block_data[4:7], byteorder="big"
                                ),
                                maximum_frame_size=int.from_bytes(
                                    block_data[7:10], byteorder="big"
                                ),
                                sample_rate=int.from_bytes(
                                    block_data[10:13], byteorder="big"
                                )
                                >> 4,
                                num_channels=((block_data[12] & 0x0E) >> 1)
                                + 1,
                                bits_per_sample=(
                                    ((block_data[12] & 0x01) << 4)
                                    + ((block_data[13] & 0xF0) >> 4)
                                    + 1
                                ),
                                total_samples=(
                                    ((block_data[13] & 0x0F) << 32)
                                    + int.from_bytes(
                                        block_data[14:18], byteorder="big"
                                    )
                                ),
                                md5=block_data[18:].hex(),
                            ),
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

                    seek_points = tuple(
                        (
                            int.from_bytes(
                                block_data[
                                    (i := 18 * seek_point_index) : (j := i + 8)
                                ],
                                byteorder="big",
                            ),
                            int.from_bytes(
                                block_data[j : (k := j + 8)],
                                byteorder="big",
                            ),
                            int.from_bytes(
                                block_data[k : k + 2], byteorder="big"
                            ),
                        )
                        for seek_point_index in range(num_seek_points)
                    )
                    seen_sample_numbers = {seek_points[0][0]}
                    for seek_point_idx, (sample_number, _, _) in enumerate(
                        seek_points[1:]
                    ):
                        if sample_number == 0xFFFFFFFFFFFFFFFF:
                            continue

                        if sample_number in seen_sample_numbers:
                            raise ValueError(
                                "Duplicate sample number "
                                f"{sample_number} found in seek point "
                                f"{seek_point_idx + 1} of SEEKTABLE "
                                f"block in '{file_path}'."
                            )
                        seen_sample_numbers.add(sample_number)

                        if sample_number < seek_points[seek_point_idx][0]:
                            raise ValueError(
                                f"Seek point {seek_point_idx + 1} is "
                                "out of order in SEEKTABLE block in "
                                f"'{file_path}'."
                            )

                    self._metadata.append(
                        FLACMetadataBlock(
                            block_type=block_type,
                            block_size=block_size,
                            block_data=seek_points,
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
                    if any(block_data[137:395]):
                        raise ValueError(
                            "Non-zero bits found in reserved section of "
                            f"CUESHEET block in '{file_path}'."
                        )

                    is_cd = bool(block_data[136] & 0x01)
                    num_lead_in_samples = int.from_bytes(
                        block_data[129:136], byteorder="big"
                    )
                    num_tracks = block_data[395]

                    if not num_tracks:
                        raise ValueError(
                            f"Invalid number of tracks ({num_tracks}) "
                            f"in CUESHEET block in '{file_path}'."
                        )

                    if is_cd:
                        if num_tracks > 100:
                            raise ValueError(
                                f"Invalid number of tracks ({num_tracks}) "
                                f"in CUESHEET block in '{file_path}'."
                            )
                    else:
                        if num_lead_in_samples:
                            raise ValueError(
                                "The number of lead-in samples must be "
                                "0 for non-CD CUESHEET block in "
                                f"'{file_path}'."
                            )

                    offset = 396
                    cue_sheet = FLACCueSheet(
                        media_catalog_number=block_data[:128]
                        .tobytes()
                        .rstrip(b"\x00")
                        .decode(),
                        num_lead_in_samples=num_lead_in_samples,
                        is_cd=is_cd,
                        num_tracks=num_tracks,
                        tracks=tuple(
                            FLACCueSheetTrack(
                                offset=int.from_bytes(
                                    block_data[
                                        offset : (offset := offset + 8)
                                    ],
                                    byteorder="big",
                                ),
                                track=block_data[offset],
                                isrc=block_data[
                                    offset + 1 : (offset := offset + 13)
                                ]
                                .tobytes()
                                .rstrip(b"\x00")
                                .decode(),
                                is_audio=bool(block_data[offset] & 0x80),
                                has_pre_emphasis=bool(
                                    block_data[offset] & 0x40
                                ),
                                num_index_points=(
                                    num_index_points := block_data[
                                        (offset := offset + 15) - 1
                                    ]
                                ),
                                index_points=tuple(
                                    (
                                        int.from_bytes(
                                            block_data[
                                                offset : (offset := offset + 8)
                                            ],
                                            byteorder="big",
                                        ),
                                        block_data[(offset := offset + 4) - 3],
                                    )
                                    for _ in range(num_index_points)
                                ),
                            )
                            for track_index in range(num_tracks)
                        ),
                    )

                    # TODO: Validate cue sheet

                    self._metadata.append(
                        FLACMetadataBlock(
                            block_type=block_type,
                            block_size=block_size,
                            block_data=cue_sheet,
                        )
                    )
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
