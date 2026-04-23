from __future__ import annotations
from dataclasses import dataclass
import string
import struct
import warnings

from ..._utility import prepare_isrc, validate_number, validate_type
from .._metadata import VorbisComment
from ._shared import AudioStreamInfo, Audio

_SEEK_TABLE_STRUCT = struct.Struct(">QQH")
_CUE_SHEET_STRUCT = struct.Struct(">128sQB258sB")
_CUE_SHEET_TRACK_STRUCT = struct.Struct(">QB12sB13sB")
_CUE_SHEET_TRACK_INDEX_STRUCT = struct.Struct(">QB3s")

_seek_table_pack = _SEEK_TABLE_STRUCT.pack
_seek_table_unpack_from = _SEEK_TABLE_STRUCT.unpack_from
_cue_sheet_pack = _CUE_SHEET_STRUCT.pack
_cue_sheet_unpack_from = _CUE_SHEET_STRUCT.unpack_from
_cue_sheet_track_pack = _CUE_SHEET_TRACK_STRUCT.pack
_cue_sheet_track_unpack_from = _CUE_SHEET_TRACK_STRUCT.unpack_from
_cue_sheet_track_index_pack = _CUE_SHEET_TRACK_INDEX_STRUCT.pack
_cue_sheet_track_index_unpack_from = _CUE_SHEET_TRACK_INDEX_STRUCT.unpack_from


@dataclass(frozen=True, slots=True)
class FLACMetadataBlock:
    """
    FLAC metadata block.
    """

    block_type: int
    block_data: (
        dict[str, bytes] | FLACCueSheet | FLACStreamInfo | VorbisComment | None
    ) = None
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
                validate_number("block_size", self.block_size, int, 0)
                if self._custom and self.block_data is not None:
                    raise ValueError("PADDING block data must be None.")
            case 2:  # APPLICATION
                if self._custom:
                    app = self.block_data
                    if not isinstance(app, dict):
                        raise TypeError(
                            "APPLICATION block data must be a "
                            f"dictionary, not {type(app).__name__}."
                        )

                    if app.keys() != {"app_id", "app_data"}:
                        raise ValueError(
                            "APPLICATION block data must have keys "
                            "'app_id' and 'app_data'."
                        )

                    validate_type("block_data['app_id']", app["app_id"], bytes)
                    validate_type(
                        "block_data['app_data']", app["app_data"], bytes
                    )
                    if len(app["app_id"]) != 4:
                        raise ValueError(
                            "APPLICATION block data 'app_id' must be 4 "
                            f"bytes, not {len(app['app_id'])} bytes."
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
                            "of order in SEEKTABLE block."
                        )
            case 4:  # VORBIS_COMMENT
                if self._custom:
                    if not isinstance(self.block_data, VorbisComment):
                        raise TypeError(
                            "VORBIS_COMMENT block data must be an "
                            "instance of VorbisComment, not "
                            f"{type(self.block_data).__name__}."
                        )

                    actual_block_size = len(self.block_data.serialize())
                    if self.block_size is None:
                        self.block_size = actual_block_size
                    elif self.block_size != actual_block_size:
                        raise ValueError(
                            "VORBIS_COMMENT block size does not match "
                            "the size of the block data."
                        )
            case 5:  # CUESHEET
                pass
            case 6:  # PICTURE
                pass

    def serialize(self) -> bytes:
        """
        Serialize (only) the metadata block data to a bytestream.
        """
        match self.block_type:
            case 0 | 4:  # STREAMINFO / VORBIS_COMMENT
                return self.block_data.serialize()
            case 1:  # PADDING
                return bytes(self.block_size)
            case 2:  # APPLICATION
                return self.block_data["app_id"] + self.block_data["app_data"]
            case 3:  # SEEKTABLE
                return b"".join(
                    _seek_table_pack(*seek_point)
                    for seek_point in self.block_data
                )
            case 5:  # CUESHEET
                pass
            case 6:  # PICTURE
                pass


@dataclass(frozen=True, slots=True)
class FLACStreamInfo(AudioStreamInfo):
    """
    FLAC :code:`STREAMINFO` metadata block data.
    """

    _HEX_DIGITS = set(string.hexdigits)
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
        if len(self.md5) != 32 or not all(
            c in self._HEX_DIGITS for c in self.md5
        ):
            raise ValueError(
                "'md5' must be a 32-character hexadecimal string."
            )

    def serialize(self) -> bytes:
        """
        Serialize the :code:`STREAMINFO` metadata block data to a
        bytestream.
        """
        return (
            self.minimum_block_size.to_bytes(2, byteorder="big")
            + self.maximum_block_size.to_bytes(2, byteorder="big")
            + self.minimum_frame_size.to_bytes(3, byteorder="big")
            + self.maximum_frame_size.to_bytes(3, byteorder="big")
            + (
                (self.sample_rate << 4)
                | ((self.num_channels - 1) << 1)
                | ((self.bits_per_sample - 1) >> 4)
            ).to_bytes(2, byteorder="big")
            + (
                ((self.bits_per_sample - 1) << 4)
                | ((self.total_samples >> 32) & 0x0F)
            ).to_bytes(2, byteorder="big")
            + (self.total_samples & 0xFFFFFFFF).to_bytes(4, byteorder="big")
            + bytes.fromhex(self.md5)
        )


@dataclass(frozen=True, slots=True)
class FLACCueSheet:
    """
    FLAC :code:`CUESHEET` metadata block data.
    """

    media_catalog_number: str
    num_lead_in_samples: int
    is_cd: bool
    num_tracks: int
    tracks: tuple[FLACCueSheetTrack, ...]

    # def __post_init__(self) -> None: ...

    def serialize(self) -> bytes:
        """
        Serialize a CUESHEET block to a bytestream.
        """
        return _cue_sheet_pack(
            self.media_catalog_number.encode(),
            self.num_lead_in_samples,
            self.is_cd << 7,
            258 * b"\x00",
            self.num_tracks,
        ) + b"".join(track.serialize() for track in self.tracks)


@dataclass(frozen=True, slots=True)
class FLACCueSheetTrack:
    """
    FLAC :code:`CUESHEET` metadata block track data.
    """

    offset: int
    number: int
    isrc: str
    is_audio: bool
    has_pre_emphasis: bool
    num_indices: int
    indices: tuple[tuple[int, int], ...]

    # def __post_init__(self) -> None: ...

    def serialize(self) -> bytes:
        """
        Serialize a track in a CUESHEET block to a bytestream.
        """
        return _cue_sheet_track_pack(
            self.offset,
            self.number,
            self.isrc.encode() if self.isrc else 12 * b"\x00",
            (self.is_audio << 7) | (self.has_pre_emphasis << 6),
            13 * b"\x00",
            self.num_indices,
        ) + b"".join(
            _cue_sheet_track_index_pack(*index, 3 * b"\x00")
            for index in self.indices
        )


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

    def load(self) -> None:
        """ """
        self.open()
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
            )
            offset = end_offset

            end_offset = offset + block_size
            block_data = view[offset:end_offset]
            offset = end_offset

            match block_type := block_header & 0x7F:
                case 0:  # STREAMINFO
                    if self._metadata:
                        raise RuntimeError(
                            "STREAMINFO block is not the first "
                            "metadata block or already exists."
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
                                    block_data[4:10], byteorder="big"
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
                                "app_id": block_data[:4].tobytes(),
                                "app_data": block_data[4:].tobytes(),
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
                            block_data=tuple(
                                _seek_table_unpack_from(
                                    block_data, 18 * seek_point_index
                                )
                                for seek_point_index in range(num_seek_points)
                            ),
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
                    (
                        media_catalog_number,
                        num_lead_in_samples,
                        is_cd,
                        reserved,
                        num_tracks,
                    ) = _cue_sheet_unpack_from(block_data)
                    if is_cd & 0x7F or reserved != 258 * b"\x00":
                        raise ValueError(
                            "Non-zero bits found in reserved section "
                            "of CUESHEET block."
                        )

                    if not num_tracks:
                        raise ValueError(
                            f"Invalid number of tracks ({num_tracks}) "
                            "in CUESHEET block."
                        )

                    is_cd &= 0x80
                    if is_cd:
                        if num_tracks > 100:
                            raise ValueError(
                                "Invalid number of tracks "
                                f"({num_tracks}) in CUESHEET block."
                            )
                    else:
                        if num_lead_in_samples:
                            raise ValueError(
                                "Number of lead-in samples must be 0, "
                                f"not {num_lead_in_samples}, for "
                                "non-CD-DA CUESHEET block."
                            )

                    offset = 396
                    seen_track_numbers = set()
                    tracks = []
                    for _ in range(num_tracks):
                        (
                            track_offset,
                            track_number,
                            isrc,
                            flags,
                            reserved,
                            num_track_indices,
                        ) = _cue_sheet_track_unpack_from(block_data, offset)

                        if track_number in seen_track_numbers:
                            raise ValueError(
                                "CUESHEET block already has a track "
                                f"with track number {track_number}."
                            )
                        if not track_number or (
                            is_cd
                            and not (
                                1 <= track_number <= 99 or track_number == 170
                            )
                        ):
                            raise ValueError(
                                "Invalid CUESHEET track number "
                                f"{track_number} for "
                                f"{'' if is_cd else 'non-'}CD-DA track "
                                f"at offset {track_offset}."
                            )
                        seen_track_numbers.add(track_number)

                        isrc = (
                            ""
                            if isrc == 12 * b"\x00"
                            else prepare_isrc(isrc.decode())
                        )
                        is_audio = bool(flags & 0x80)
                        has_pre_emphasis = bool(flags & 0x40)
                        if flags & 0x3F or reserved != 13 * b"\x00":
                            raise ValueError(
                                "Non-zero bits found in the reserved "
                                "section of a CUESHEET track."
                            )

                        is_lead_out = (
                            is_cd
                            and track_number == 170
                            or not is_cd
                            and track_number == 255
                        )
                        if is_lead_out and num_track_indices:
                            raise ValueError(
                                "Lead-out CUESHEET tracks cannot have "
                                "any track indices."
                            )
                        elif not is_lead_out and not num_track_indices:
                            raise ValueError(
                                "Non-lead-out CUESHEET tracks must "
                                "have at least one track index."
                            )

                        offset += 36
                        prev_index_number = -1
                        track_indices = []
                        for _ in range(num_track_indices):
                            index_offset, index_number, reserved = (
                                _cue_sheet_track_index_unpack_from(
                                    block_data, offset
                                )
                            )

                            if is_cd and not index_offset % 588:
                                raise ValueError(
                                    "Offsets for CD-DA track indices "
                                    "in CUESHEET block must be "
                                    "divisible by 588 samples."
                                )

                            if index_number != prev_index_number + 1 and not (
                                prev_index_number == -1 and index_number == 1
                            ):
                                raise ValueError(
                                    "Track index numbers must start at "
                                    "0 or 1 and increase sequentially "
                                    "in a CUESHEET track."
                                )
                            prev_index_number = index_number

                            if reserved != 3 * b"\x00":
                                raise ValueError(
                                    "Non-zero bits found in the reserved "
                                    "section of a CUESHEET track index."
                                )

                            offset += 12
                            track_indices.append((index_offset, index_number))

                        tracks.append(
                            FLACCueSheetTrack(
                                offset=track_offset,
                                number=track_number,
                                isrc=isrc,
                                is_audio=is_audio,
                                has_pre_emphasis=has_pre_emphasis,
                                num_indices=num_track_indices,
                                indices=tuple(track_indices),
                            )
                        )

                    self._metadata.append(
                        FLACMetadataBlock(
                            block_type=block_type,
                            block_size=block_size,
                            block_data=FLACCueSheet(
                                media_catalog_number=media_catalog_number.rstrip(
                                    b"\x00"
                                ).decode(),
                                num_lead_in_samples=num_lead_in_samples,
                                is_cd=is_cd,
                                num_tracks=num_tracks,
                                tracks=tuple(tracks),
                            ),
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

        del block_data
        self.close()

    def save(self) -> None: ...  # TODO
