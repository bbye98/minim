from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
import warnings

from ..._utility import validate_number, validate_type
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
    block_data: dict[str, bytes] | FLACStreamInfo | VorbisComment | None = None
    block_size: int | None = None
    _custom: bool = True

    def __post_init__(self) -> None:
        validate_number("block_type", self.block_type, int, 0, 6)
        match self.block_type:
            case 0:  # STREAMINFO
                if self._custom:
                    if self.block_size is None:
                        self.block_size = 34
                    elif self.block_size != 34:
                        raise ValueError(
                            f"STREAMINFO block size must be 34, not {self.block_size}."
                        )

                    if not isinstance(self.block_data, FLACStreamInfo):
                        raise TypeError(
                            "STREAMINFO block data must be an instance of "
                            f"FLACStreamInfo, not {type(self.block_data).__name__}."
                        )
            case 1:  # PADDING
                if self._custom and self.block_data is not None:
                    raise ValueError("PADDING block data must be None.")
            case 2:  # APPLICATION
                if self._custom:
                    app = self.block_data
                    if not isinstance(app, dict):
                        raise TypeError(
                            "APPLICATION block data must be a dictionary, not "
                            f"{type(app).__name__}."
                        )

                    if app.keys() != {"app_id", "app_data"}:
                        raise ValueError(
                            "APPLICATION block data must have keys 'app_id' and "
                            "'app_data'."
                        )

                    validate_type("block_data['app_id']", app["app_id"], bytes)
                    validate_type(
                        "block_data['app_data']", app["app_data"], bytes
                    )
                    if len(app["app_id"]) != 4:
                        raise ValueError(
                            "APPLICATION block data 'app_id' must be 4 bytes, not "
                            f"{len(app['app_id'])} bytes."
                        )

                    actual_block_size = 4 + len(app["app_data"])
                    if self.block_size is None:
                        self.block_size = actual_block_size
                    elif self.block_size != actual_block_size:
                        raise ValueError(
                            "APPLICATION block size does not match the "
                            "size of the block data."
                        )
            case 3:  # SEEKTABLE
                seek_points = self.block_data
                if self._custom:
                    if not isinstance(seek_points, list):
                        raise TypeError(
                            "SEEKTABLE block data must be a list of "
                            "seek points, not "
                            f"{type(seek_points).__name__}."
                        )

                    actual_block_size = 18 * len(seek_points)
                    if self.block_size is None:
                        self.block_size = actual_block_size
                    elif self.block_size != actual_block_size:
                        raise ValueError(
                            "SEEKTABLE block size does not match the "
                            "size of the block data."
                        )

                seen_sample_numbers = {seek_points[0][0]}
                for seek_point_idx, (sample_number, _, _) in enumerate(
                    seek_points[1:]
                ):
                    if sample_number == 0xFFFFFFFFFFFFFFFF:
                        continue

                    if sample_number in seen_sample_numbers:
                        raise ValueError(
                            f"Duplicate sample number {sample_number} "
                            f"found in seek point {seek_point_idx + 1} "
                            "of SEEKTABLE block."
                        )
                    seen_sample_numbers.add(sample_number)

                    if sample_number < seek_points[seek_point_idx][0]:
                        raise ValueError(
                            f"Seek point {seek_point_idx + 1} is out "
                            "of order in SEEKTABLE block"
                        )
            case 4:  # VORBIS_COMMENT
                if not isinstance(self.block_data, VorbisComment):
                    raise TypeError(
                        "VORBIS_COMMENT block data must be an instance of "
                        f"VorbisComment, not {type(self.block_data).__name__}."
                    )
            case 5:  # CUESHEET
                pass
            case 6:  # PICTURE
                pass

    # def serialize(self) -> bytes: ...


@dataclass(frozen=True, slots=True)
class FLACStreamInfo(AudioStreamInfo):
    """
    FLAC :code:`STREAMINFO` metadata block data.
    """

    _NUM_CHANNELS_RANGE = (1, 8)
    _SAMPLE_RATE_RANGE = (1, 655_350)
    _BITS_PER_SAMPLE_RANGE = (1, 32)

    minimum_block_size: int
    maximum_block_size: int
    minimum_frame_size: int
    maximum_frame_size: int
    md5: str

    def __post_init__(self) -> None:
        super().__post_init__()
        validate_number("minimum_block_size", self.minimum_block_size, int, 16)
        validate_number("maximum_block_size", self.maximum_block_size, int, 16)
        validate_number("minimum_frame_size", self.minimum_frame_size, int, 0)
        validate_number("maximum_frame_size", self.maximum_frame_size, int, 0)
        validate_type("md5", self.md5, str)
        if len(self.md5) != 32:
            raise ValueError(
                "'md5' must be a 32-character hexadecimal string."
            )

    # def serialize(self) -> bytes: ...


@dataclass(frozen=True, slots=True)
class FLACCueSheet:
    """
    FLAC :code:`CUESHEET` metadata block data.
    """

    media_catalog_number: str
    num_lead_in_samples: int
    is_cd: bool
    num_tracks: int
    tracks: list[FLACCueSheetTrack]

    # def serialize(self) -> bytes: ...


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
    index_points: list[tuple[int, int]]

    # def serialize(self) -> bytes: ...


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

                    self._metadata.append(
                        FLACMetadataBlock(
                            block_type=block_type,
                            block_size=block_size,
                            block_data=FLACStreamInfo(
                                minimum_block_size=int.from_bytes(
                                    block_data[:2], byteorder="big"
                                ),
                                maximum_block_size=int.from_bytes(
                                    block_data[2:4], byteorder="big"
                                ),
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
                            _custom=False,
                        )
                    )
                case 1:  # PADDING
                    self._metadata.append(
                        FLACMetadataBlock(
                            block_type=block_type,
                            block_size=block_size,
                            _custom=False,
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
                            _custom=False,
                        )
                    )
                case 3:  # SEEKTABLE
                    num_seek_points, remainder = divmod(block_size, 18)
                    if remainder:
                        raise ValueError(
                            f"Invalid SEEKTABLE block size of {block_size}."
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
                            ],
                            _custom=False,
                        )
                    )
                case 4:  # VORBIS_COMMENT
                    self._tags = VorbisComment(block_data)
                    self._metadata.append(
                        FLACMetadataBlock(
                            block_type=block_type,
                            block_size=block_size,
                            block_data=self._tags,
                            _custom=False,
                        )
                    )
                case 5:  # CUESHEET
                    if any(block_data[137:395]):
                        raise ValueError(
                            "Non-zero bits found in reserved section "
                            "of the CUESHEET block."
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
                            for _ in range(num_tracks)
                        ),
                    )

                    # TODO: Validate cue sheet

                    self._metadata.append(
                        FLACMetadataBlock(
                            block_type=block_type,
                            block_size=block_size,
                            block_data=cue_sheet,
                            _custom=False,
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
