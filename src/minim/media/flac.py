from __future__ import annotations
from dataclasses import dataclass
import string
import struct
from typing import TYPE_CHECKING, NamedTuple

from .._utility import (
    ASCII_CHARS_REGEX,
    set_obj_attr,
    prepare_isrc,
    validate_number,
    validate_type,
)
from .._types import BytesLike, ORDERED_COLLECTION_TYPES
from ._shared import as_buffer, Audio
from .metadata import APICFrame, AudioStreamInfo, VorbisComment

if TYPE_CHECKING:
    from .._types import PathLike, Collection, OrderedCollection

    from typing import Self


__all__ = [
    "FLACAudio",
    "FLACMetadataBlock",
    "FLACStreamInfo",
    "FLACApplication",
    "FLACSeekTable",
    "FLACSeekPoint",
    "FLACCueSheet",
    "FLACCueSheetTrack",
    "FLACCueSheetTrackIndex",
]


@dataclass(frozen=True, kw_only=True, slots=True)
class FLACStreamInfo(AudioStreamInfo):
    """
    FLAC :code:`STREAMINFO` metadata block data.

    Parameters
    ----------
    num_channels : int; keyword-only
        Number of channels.

    sample_rate : int; keyword-only
        Sample rate in hertz.

    bit_depth : int; keyword-only
        Bits per sample.

    num_samples : int; keyword-only
        Total number of samples.

    min_block_size : int; keyword-only
        Minimum block size in samples.

        **Valid range**: :code:`16` to :code:`65_535`.

    max_block_size : int; keyword-only
        Maximum block size in samples.

        **Valid range**: :code:`16` to :code:`65_535`.

    min_frame_size : int; keyword-only
        Minimum frame size in bytes.

        **Valid range**: :code:`0` to :code:`16_777_215`.

    max_frame_size : int; keyword-only
        Maximum frame size in bytes.

        **Valid range**: :code:`0` to :code:`16_777_215`.

    md5 : str; keyword-only
        MD5 hash of the unencoded audio data.
    """

    _HEX_DIGITS = set(string.hexdigits)
    _STRUCT_HH = struct.Struct(">HH")
    _STRUCT_Q = struct.Struct(">Q")

    _NUM_CHANNELS_RANGE = (1, 8)
    _SAMPLE_RATE_RANGE = (1, 655_350)
    _BIT_DEPTH_RANGE = (1, 32)

    #: Minimum block size in samples.
    min_block_size: int
    #: Maximum block size in samples.
    max_block_size: int
    #: Minimum frame size in bytes.
    min_frame_size: int
    #: Maximum frame size in bytes.
    max_frame_size: int
    #: MD5 hash of the unencoded audio data.
    md5: str

    def __post_init__(self) -> None:
        super(FLACStreamInfo, self).__post_init__()
        validate_number("min_block_size", self.min_block_size, int, 16, 65_535)
        validate_number("max_block_size", self.max_block_size, int, 16, 65_535)
        if self.min_block_size > self.max_block_size:
            raise ValueError(
                "`min_block_size` must be less than or equal to "
                "`max_block_size`."
            )

        min_frame_size = self.min_frame_size
        max_frame_size = self.max_frame_size
        validate_number("min_frame_size", min_frame_size, int, 0, 16_777_215)
        validate_number("max_frame_size", max_frame_size, int, 0, 16_777_215)
        if (
            min_frame_size
            and max_frame_size
            and min_frame_size > max_frame_size
        ):
            raise ValueError(
                "When both known, `min_frame_size` must be less than "
                "or equal to `max_frame_size`."
            )

        md5 = self.md5
        validate_type("md5", md5, str)
        if len(md5) != 32 or not all(c in self._HEX_DIGITS for c in md5):
            raise ValueError(
                "`md5` must be a 32-character hexadecimal string."
            )

    @classmethod
    def from_stream(cls, stream: BytesLike, /) -> FLACStreamInfo:
        """
        Instantiate a :class:`FLACStreamInfo` object from a bytes-like
        object.

        Parameters
        ----------
        bytestream : bytes, bytearray, memoryview, or mmap.mmap; \
        positional-only; optional
            Bytes-like object containing :code:`STREAMINFO` metadata
            block data.

        Returns
        -------
        stream_info : minim.media.flac.FLACStreamInfo
            :code:`STREAMINFO` metadata block data.
        """
        stream = as_buffer(stream)
        min_block_size = int.from_bytes(stream[:2], byteorder="big")
        max_block_size = int.from_bytes(stream[2:4], byteorder="big")
        if max_block_size < min_block_size:
            raise ValueError(
                "`min_block_size` must be less than or equal to "
                "`max_block_size`."
            )

        min_frame_size = int.from_bytes(stream[4:7], byteorder="big")
        max_frame_size = int.from_bytes(stream[7:10], byteorder="big")
        if (
            min_frame_size
            and max_frame_size
            and min_frame_size > max_frame_size
        ):
            raise ValueError(
                "When both known, `min_frame_size` must be less than "
                "or equal to `max_frame_size`."
            )

        sample_rate = int.from_bytes(stream[10:13], byteorder="big") >> 4
        validate_number(
            "sample_rate", sample_rate, int, *cls._SAMPLE_RATE_RANGE
        )

        num_channels = ((stream[12] & 0x0E) >> 1) + 1
        validate_number(
            "num_channels", num_channels, int, *cls._NUM_CHANNELS_RANGE
        )

        bit_depth = ((stream[12] & 0x01) << 4) + ((stream[13] & 0xF0) >> 4) + 1
        validate_number("bit_depth", bit_depth, int, *cls._BIT_DEPTH_RANGE)

        obj = cls.__new__(cls)
        set_obj_attr(obj, "min_block_size", min_block_size)
        set_obj_attr(obj, "max_block_size", max_block_size)
        set_obj_attr(obj, "min_frame_size", min_frame_size)
        set_obj_attr(obj, "max_frame_size", max_frame_size)
        set_obj_attr(obj, "sample_rate", sample_rate)
        set_obj_attr(obj, "num_channels", num_channels)
        set_obj_attr(obj, "bit_depth", bit_depth)
        set_obj_attr(
            obj,
            "num_samples",
            ((stream[13] & 0x0F) << 32)
            + int.from_bytes(stream[14:18], byteorder="big"),
        )
        set_obj_attr(obj, "md5", stream[18:34].hex())
        return obj

    def serialize(self) -> bytes:
        """
        Serialize the :code:`STREAMINFO` metadata block data to a
        bytestream.

        Returns
        -------
        bytestream : bytes
            Bytestream containing :code:`STREAMINFO` metadata block
            data.
        """
        return b"".join(
            (
                self.min_block_size.to_bytes(2, byteorder="big"),
                self.max_block_size.to_bytes(2, byteorder="big"),
                self.min_frame_size.to_bytes(3, byteorder="big"),
                self.max_frame_size.to_bytes(3, byteorder="big"),
                (
                    (self.sample_rate << 4)
                    | ((self.num_channels - 1) << 1)
                    | ((self.bit_depth - 1) >> 4)
                ).to_bytes(2, byteorder="big"),
                (
                    ((self.bit_depth - 1) << 4)
                    | ((self.num_samples >> 32) & 0x0F)
                ).to_bytes(2, byteorder="big"),
                (self.num_samples & 0xFFFFFFFF).to_bytes(4, byteorder="big"),
                bytes.fromhex(self.md5),
            )
        )


@dataclass(frozen=True, kw_only=True, slots=True)
class FLACApplication:
    """
    FLAC :code:`APPLICATION` metadata block data.

    Parameters
    ----------
    app_id : bytes, bytearray, or str; keyword-only
        Four-character binary or eight-character hexadecimal application
        ID.

        .. seealso::

           `FLAC Application Metadata Block IDs
           <https://www.iana.org/assignments/flac/flac.xhtml>`_ –
           Registry of eight-character hexadecimal IDs for third-party
           applications.

    app_data : bytes or bytearray; keyword-only; default: :code:`b""`
        Application data.
    """

    #: Application ID.
    app_id: bytes | bytearray | str
    #: Application data.
    app_data: bytes | bytearray = b""

    def __post_init__(self) -> None:
        app_id = self.app_id
        validate_type("app_id", app_id, bytes | bytearray | str)
        if isinstance(app_id, str):
            try:
                app_id = bytes.fromhex(app_id)
            except ValueError as e:
                raise ValueError(
                    "`app_id` must be a valid hexadecimal string."
                ) from e
        if len(app_id) != 4:
            raise ValueError("A binary `app_id` must have length 4.")

    @classmethod
    def from_stream(cls, stream: BytesLike, /) -> FLACApplication:
        """
        Instantiate a :class:`FLACApplication` object from a bytes-like
        object.

        Parameters
        ----------
        bytestream : bytes, bytearray, memoryview, or mmap.mmap; \
        positional-only; optional
            Bytes-like object containing :code:`APPLICATION` metadata
            block data.

        Returns
        -------
        app : minim.media.flac.FLACApplication
            :code:`APPLICATION` metadata block data.
        """
        stream = as_buffer(stream)
        obj = cls.__new__(cls)
        set_obj_attr(obj, "app_id", stream[:4].tobytes())
        set_obj_attr(obj, "app_data", stream[4:].tobytes())
        return obj

    def serialize(self) -> bytes:
        """
        Serialize the :code:`APPLICATION` metadata block data to a
        bytestream.

        Returns
        -------
        bytestream : bytes
            Bytestream containing :code:`APPLICATION` metadata block
            data.
        """
        return self.app_id + self.app_data


@dataclass(frozen=True, kw_only=True, slots=True)
class FLACSeekTable:
    """
    FLAC :code:`SEEKTABLE` metadata block data.

    Parameters
    ----------
    seek_points : OrderedCollection[FLACSeekPoint, ...]; keyword-only
        Seek points.
    """

    #: Seek points.
    seek_points: tuple[FLACSeekPoint, ...]

    def __post_init__(self) -> None:
        seek_points = self.seek_points
        if not isinstance(seek_points, tuple):
            if not isinstance(seek_points, list):
                raise ValueError(
                    f"`seek_points` must be a(n) tuple | list, not "
                    f"a(n) {type(seek_points).__name__}."
                )
            seek_points = self.seek_points = tuple(seek_points)
        self._validate_seek_points(seek_points)

    @classmethod
    def from_stream(cls, stream: BytesLike, /) -> FLACSeekTable:
        """
        Instantiate a :class:`FLACSeekTable` object from a bytes-like
        object.

        Parameters
        ----------
        bytestream : bytes, bytearray, memoryview, or mmap.mmap; \
        positional-only; optional
            Bytes-like object containing :code:`SEEKTABLE` metadata
            block data.

        Returns
        -------
        app : minim.media.flac.FLACSeekTable
            :code:`SEEKTABLE` metadata block data.
        """
        stream = as_buffer(stream)
        if (length := len(stream)) % 18:
            raise ValueError(
                f"Invalid SEEKTABLE block length of {length}, which is "
                "not divisible by 18."
            )

        _from_unpack = FLACSeekPoint._from_unpack
        seek_points = tuple(
            _from_unpack(data)
            for data in FLACSeekPoint._STRUCT.iter_unpack(stream)
        )
        cls._validate_seek_points(seek_points, custom=False)

        obj = cls.__new__(cls)
        set_obj_attr(obj, "seek_points", seek_points)
        return obj

    @staticmethod
    def _validate_seek_points(
        seek_points: tuple[FLACSeekPoint, ...], /, *, custom: bool = True
    ) -> None:
        """
        Validate seek points (:code:`SEEKPOINT`) in a :code:`SEEKTABLE`
        metadata block.

        Parameters
        ----------
        seek_points : tuple[FLACSeekPoint, ...]; positional-only
            Seek points.

        custom : bool; keyword-only; default: :code:`True`
            Whether the seek points are user-defined and should have
            their types validated.
        """
        if custom:
            validate_type("seek_points[0]", seek_points[0], FLACSeekPoint)
        seen_sample_numbers = {seek_points[0].sample_number}
        for seek_point_idx, seek_point in enumerate(seek_points[1:]):
            if custom:
                validate_type(
                    f"seek_points[{seek_point_idx}]", seek_point, FLACSeekPoint
                )
            sample_number = seek_point.sample_number
            if sample_number == 0xFFFFFFFFFFFFFFFF:
                continue

            if sample_number in seen_sample_numbers:
                raise ValueError(
                    f"Duplicate sample number {sample_number} "
                    f"found in seek point {seek_point_idx + 1} "
                    "of SEEKTABLE block."
                )
            seen_sample_numbers.add(sample_number)

            if sample_number < seek_points[seek_point_idx].sample_number:
                raise ValueError(
                    f"Seek point {seek_point_idx + 1} is out "
                    "of order in SEEKTABLE block."
                )

    def serialize(self) -> bytes:
        """
        Serialize the :code:`SEEKTABLE` metadata block data to a
        bytestream.

        Returns
        -------
        bytestream : bytes
            Bytestream containing :code:`SEEKTABLE` metadata block data.
        """
        return b"".join(
            seek_point.serialize() for seek_point in self.seek_points
        )


class FLACSeekPoint(
    NamedTuple(
        "FLACSeekPointTuple",
        [("sample_number", int), ("byte_offset", int), ("num_samples", int)],
    )
):
    """
    FLAC :code:`SEEKPOINT` data.

    Parameters
    ----------
    sample_number : int
        Sample number of the first sample in the target frame.

    byte_offset : int
        Byte offset of the target frame header relative to the first
        frame header.

    num_samples : int
        Number of samples in the target frame.
    """

    _STRUCT = struct.Struct(">QQH")

    __slots__ = ()

    #: :code:`self[0]` – Sample number of the first sample in the target
    #: frame.
    sample_number: int
    #: :code:`self[1]` – Byte offset of the target frame header relative
    #: to the first frame header.
    byte_offset: int
    #: :code:`self[2]` – Number of samples in the target frame.
    num_samples: int

    def __new__(
        cls, sample_number: int, byte_offset: int, num_samples: int
    ) -> Self:
        validate_number("sample_number", sample_number, int, 0)
        validate_number("byte_offset", byte_offset, int, 0)
        validate_number("num_samples", num_samples, int, 0)
        return tuple.__new__(cls, (sample_number, byte_offset, num_samples))

    @classmethod
    def _from_unpack(cls, data: tuple[int, int, int], /) -> FLACSeekPoint:
        """
        Instantiate a :class:`FLACSeekPoint` object using data unpacked
        from a bytes-like object.

        Parameters
        ----------
        data : tuple[int, int, int]; positional-only
            Unpacked :class:`FLACSeekPoint` data.

        Returns
        -------
        seek_point : minim.media.flac.FLACSeekPoint
            :code:`SEEKPOINT` data.
        """
        return tuple.__new__(cls, data)

    @classmethod
    def from_stream(cls, stream: bytes, /) -> FLACSeekPoint:
        """
        Instantiate a :class:`FLACSeekPoint` object from a bytes-like
        object.

        Parameters
        ----------
        bytestream : bytes, bytearray, memoryview, or mmap.mmap; \
        positional-only; optional
            Bytes-like object containing :code:`SEEKPOINT` data.

        Returns
        -------
        seek_point : minim.media.flac.FLACSeekPoint
            :code:`SEEKPOINT` data.
        """
        return tuple.__new__(cls, cls._STRUCT.unpack_from(as_buffer(stream)))

    def serialize(self) -> bytes:
        """
        Serialize the :code:`SEEKPOINT` data to a bytestream.

        Returns
        -------
        bytestream : bytes
            Bytestream containing :code:`SEEKPOINT` data.
        """
        return self._STRUCT.pack(*self)


@dataclass(frozen=True, kw_only=True, slots=True)
class FLACCueSheet:
    """
    FLAC :code:`CUESHEET` metadata block data.

    Parameters
    ----------
    media_catalog_number : str; keyword-only
        Media catalog number.

    num_lead_in_samples : int; keyword-only
        Number of lead-in samples for CD-DA cue sheets.

    is_cd : bool; keyword-only
        Whether the cue sheet is for CD-DA.

    tracks : OrderedCollection[minim.media.flac.FLACCueSheetTrack, ...]; \
    keyword-only
        Tracks.
    """

    _STRUCT = struct.Struct(">128sQB258sB")

    #: Media catalog number.
    media_catalog_number: str
    #: Number of lead-in samples for CD-DA cue sheets.
    num_lead_in_samples: int
    #: Whether the cue sheet is for CD-DA.
    is_cd: bool
    #: Tracks.
    tracks: tuple[FLACCueSheetTrack, ...]

    def __post_init__(self) -> None:
        media_catalog_number = self.media_catalog_number
        validate_type("media_catalog_number", media_catalog_number, str)
        if len(media_catalog_number) > 128:
            raise ValueError(
                "`media_catalog_number` must be 128 characters or fewer."
            )
        if not ASCII_CHARS_REGEX.match(media_catalog_number):
            raise ValueError(
                "`media_catalog_number` must contain only ASCII "
                "characters 0x20 (' ') through 0x7D ('}')."
            )

        is_cd = self.is_cd
        validate_number(
            "num_lead_in_samples",
            self.num_lead_in_samples,
            int,
            0,
            None if is_cd else 0,
        )
        validate_type("is_cd", is_cd, bool)

        tracks = self.tracks
        if not isinstance(tracks, tuple):
            if not isinstance(tracks, list):
                raise ValueError(
                    f"`tracks` must be a(n) tuple | list, not "
                    f"a(n) {type(tracks).__name__}."
                )
            tracks = self.tracks = tuple(tracks)

        if not (num_tracks := len(tracks)) or is_cd and num_tracks > 100:
            raise ValueError(
                f"Invalid number of tracks ({num_tracks}) in CUESHEET block."
            )

        self._validate_tracks(tracks, is_cd=is_cd)

    @classmethod
    def from_stream(cls, stream: BytesLike, /) -> FLACCueSheet:
        """ 
        Instantiate a :class:`FLACCueSheet` object from a bytes-like 
        object.

        Parameters
        ----------
        bytestream : bytes, bytearray, memoryview, or mmap.mmap; \
        positional-only; optional
            Bytes-like object containing :code:`CUESHEET` metadata block 
            data.

        Returns
        -------
        track : minim.media.flac.FLACCueSheetTrack
            :code:`CUESHEET` metadata block data.
        """
        stream = as_buffer(stream)
        (
            media_catalog_number,
            num_lead_in_samples,
            is_cd,
            reserved,
            num_tracks,
        ) = cls._STRUCT.unpack_from(stream)
        if is_cd & 0x7F or reserved != 258 * b"\x00":
            raise ValueError(
                "Non-zero bits found in reserved section of CUESHEET block."
            )

        media_catalog_number = media_catalog_number.rstrip(b"\x00").decode(
            encoding="utf-8"
        )
        if not ASCII_CHARS_REGEX.match(media_catalog_number):
            raise ValueError(
                "`media_catalog_number` must contain only ASCII "
                "characters 0x20 (' ') through 0x7D ('}')."
            )

        if not num_tracks:
            raise ValueError(
                f"Invalid number of tracks ({num_tracks}) in CUESHEET block."
            )

        is_cd = bool(is_cd & 0x80)
        if is_cd:
            if num_tracks > 100:
                raise ValueError(
                    f"Invalid number of tracks ({num_tracks}) in "
                    "CUESHEET block."
                )
        else:
            if num_lead_in_samples:
                raise ValueError(
                    "Number of lead-in samples must be 0, not "
                    f"{num_lead_in_samples}, for non-CD-DA CUESHEET "
                    "block."
                )

        offset = 396
        tracks = []
        for _ in range(num_tracks):
            track = FLACCueSheetTrack.from_stream(stream[offset:])
            num_track_indices = track.num_indices
            offset += 36 + 12 * num_track_indices
            tracks.append(track)
        tracks = tuple(tracks)
        cls._validate_tracks(tracks, is_cd=is_cd, custom=False)

        obj = cls.__new__(cls)
        set_obj_attr(obj, "media_catalog_number", media_catalog_number)
        set_obj_attr(obj, "num_lead_in_samples", num_lead_in_samples)
        set_obj_attr(obj, "is_cd", is_cd)
        set_obj_attr(obj, "tracks", tracks)
        return obj

    @staticmethod
    def _validate_tracks(
        tracks: tuple[FLACCueSheetTrack, ...],
        /,
        is_cd: bool,
        *,
        custom: bool = True,
    ) -> None:
        """
        Validate tracks (:code:`CUESHEET_TRACK`) in a :code:`CUESHEET`
        metadata block.

        Parameters
        ----------
        tracks : tuple[minim.media.flac.FLACCueSheetTrack, ...]; \
        positional-only
            Tracks.

        is_cd : bool
            Whether the cue sheet is for CD-DA.

        custom : bool; keyword-only; default: :code:`True`
            Whether the tracks are user-defined and should have their
            types validated.
        """
        seen_track_numbers = set()
        for track_idx, track in enumerate(tracks):
            if custom:
                validate_type(f"tracks[{track_idx}]", track, FLACCueSheetTrack)
            track_number = track.number
            if track_number in seen_track_numbers:
                raise ValueError(
                    "CUESHEET block has multiple tracks with track "
                    f"number {track_number}."
                )

            if not track_number or (
                is_cd and not (1 <= track_number <= 99 or track_number == 170)
            ):
                raise ValueError(
                    f"Invalid CUESHEET track number {track_number} for "
                    f"{'' if is_cd else 'non-'}CD-DA track at sample "
                    f"offset {track.sample_offset}."
                )
            seen_track_numbers.add(track_number)

            num_track_indices = track.num_indices
            if (
                is_lead_out := (
                    is_cd
                    and track_number == 170
                    or not is_cd
                    and track_number == 255
                )
            ) and num_track_indices:
                raise ValueError(
                    "Lead-out CUESHEET tracks cannot have any track indices."
                )
            elif not is_lead_out and not num_track_indices:
                raise ValueError(
                    "Non-lead-out CUESHEET tracks must have at least "
                    "one track index."
                )

            if is_cd:
                for track_index in track.indices:
                    if track_index.sample_offset % 588:
                        raise ValueError(
                            "Sample offsets for CD-DA track indices in "
                            "CUESHEET block must be divisible by 588."
                        )

        if track.number != (lead_out_track_number := 170 if is_cd else 255):
            raise ValueError(
                "The last track in a CUESHEET block must be a lead-out "
                f"track with track number {lead_out_track_number}."
            )

    @property
    def num_tracks(self) -> int:
        """
        Number of tracks (:code:`CUESHEET_TRACK`).
        """
        return len(self.tracks)

    def serialize(self) -> bytes:
        """
        Serialize :code:`CUESHEET` metadata block data to a bytestream.

        Returns
        -------
        bytestream : bytes
            Bytestream containing :code:`CUESHEET` metadata block data.
        """
        return self._STRUCT.pack(
            self.media_catalog_number.encode(encoding="utf-8"),
            self.num_lead_in_samples,
            self.is_cd << 7,
            258 * b"\x00",
            self.num_tracks,
        ) + b"".join(track.serialize() for track in self.tracks)


@dataclass(frozen=True, kw_only=True, slots=True)
class FLACCueSheetTrack:
    """
    FLAC :code:`CUESHEET_TRACK` data.

    Parameters
    ----------
    sample_offset : int; keyword-only
        Sample offset of the track relative to the beginning of the FLAC
        audio stream.

    number : int; keyword-only
        Track number.

    isrc : str; keyword-only
        International Standard Recording Code (ISRC).

    is_audio : bool; keyword-only
        Whether the track contains audio data.

    has_pre_emphasis : bool; keyword-only
        Whether the track has pre-emphasis.

    tracks : OrderedCollection[minim.media.flac.FLACCueSheetTrackIndex]; \
    keyword-only
        Track indices.
    """

    _STRUCT = struct.Struct(">QB12sB13sB")

    #: Sample offset of the track relative to the beginning of the FLAC
    #: audio stream.
    sample_offset: int
    #: Track number.
    number: int
    #: International Standard Recording Code (ISRC).
    isrc: str
    #: Whether the track contains audio data.
    is_audio: bool
    #: Whether the track has pre-emphasis.
    has_pre_emphasis: bool
    #: Track indices.
    indices: tuple[FLACCueSheetTrackIndex, ...]

    def __post_init__(self) -> None:
        validate_number("sample_offset", self.sample_offset, int, 0)
        validate_number("number", self.number, int, 0)
        validate_type("isrc", self.isrc, str)
        self.isrc = prepare_isrc(self.isrc)
        validate_type("is_audio", self.is_audio, bool)
        validate_type("has_pre_emphasis", self.has_pre_emphasis, bool)

        indices = self.indices
        if not isinstance(indices, tuple):
            if not isinstance(indices, list):
                raise ValueError(
                    f"`indices` must be a(n) tuple | list, not a(n) "
                    f"{type(indices).__name__}."
                )
            indices = self.indices = tuple(indices)

        self._validate_indices(indices)

    @classmethod
    def from_stream(cls, stream: BytesLike, /) -> FLACCueSheetTrack:
        """ 
        Instantiate a :class:`FLACCueSheetTrack` object from a 
        bytes-like object.

        Parameters
        ----------
        bytestream : bytes, bytearray, memoryview, or mmap.mmap; \
        positional-only; optional
            Bytes-like object containing :code:`CUESHEET_TRACK` data.

        Returns
        -------
        track : minim.media.flac.FLACCueSheetTrack
            :code:`CUESHEET_TRACK` data.
        """
        stream = as_buffer(stream)
        (
            sample_offset,
            number,
            isrc,
            flags,
            reserved,
            num_indices,
        ) = cls._STRUCT.unpack_from(stream)
        if flags & 0x3F or reserved != 13 * b"\x00":
            raise ValueError(
                "Non-zero bits found in reserved section of "
                "CUESHEET_TRACK data."
            )

        _from_unpack = FLACCueSheetTrackIndex._from_unpack
        indices = tuple(
            _from_unpack(data)
            for data in FLACCueSheetTrackIndex._STRUCT.iter_unpack(
                stream[36 : 36 + 12 * num_indices]
            )
        )
        cls._validate_indices(indices, custom=False)

        obj = cls.__new__(cls)
        set_obj_attr(obj, "sample_offset", sample_offset)
        set_obj_attr(obj, "number", number)
        set_obj_attr(
            obj,
            "isrc",
            ""
            if isrc == 12 * b"\x00"
            else prepare_isrc(isrc.decode(encoding="utf-8")),
        )
        set_obj_attr(obj, "is_audio", bool(flags & 0x80))
        set_obj_attr(obj, "has_pre_emphasis", bool(flags & 0x40))
        set_obj_attr(obj, "indices", indices)
        return obj

    @staticmethod
    def _validate_indices(
        indices: tuple[FLACCueSheetTrackIndex, ...], /, *, custom: bool = True
    ) -> None:
        """
        Validate track indices (:code:`CUESHEET_TRACK_INDEX`) in a
        :code:`CUESHEET_TRACK`.

        Parameters
        ----------
        indices : tuple[minim.media.flac.FLACCueSheetTrackIndex, ...]; \
        positional-only
            Track indices.

        custom : bool; keyword-only; default: :code:`True`
            Whether the track indices are user-defined and should have 
            their types validated.
        """
        prev_index_number = -1
        for index_idx, index in enumerate(indices):
            if custom:
                validate_type(
                    f"indices[{index_idx}]", index, FLACCueSheetTrackIndex
                )
            index_number = index.number
            if index_number != prev_index_number + 1 and not (
                prev_index_number == -1 and index_number == 1
            ):
                raise ValueError(
                    "CUESHEET_TRACK_INDEX numbers must start at 0 or 1 "
                    "and increase sequentially in a CUESHEET_TRACK."
                )
            prev_index_number = index_number

    @property
    def num_indices(self) -> int:
        """
        Number of track indices (:code:`CUESHEET_TRACK_INDEX`).
        """
        return len(self.indices)

    def serialize(self) -> bytes:
        """
        Serialize :code:`CUESHEET_TRACK` data to a bytestream.

        Returns
        -------
        bytestream : bytes
            Bytestream containing :code:`CUESHEET_TRACK` data.
        """
        return self._STRUCT.pack(
            self.sample_offset,
            self.number,
            self.isrc.encode(encoding="utf-8") if self.isrc else 12 * b"\x00",
            (self.is_audio << 7) | (self.has_pre_emphasis << 6),
            13 * b"\x00",
            self.num_indices,
        ) + b"".join(index.serialize() for index in self.indices)


class FLACCueSheetTrackIndex(
    NamedTuple(
        "FLACCueSheetTrackIndexTuple",
        [("sample_offset", int), ("number", int)],
    )
):
    """
    FLAC :code:`CUESHEET_TRACK_INDEX` data.

    Parameters
    ----------
    sample_offset : int
        Sample offset of the index point relative to the track offset.

    number : int
        Track index number.
    """

    _STRUCT = struct.Struct(">QB3s")

    __slots__ = ()

    #: :code:`self[0]` – Sample offset of the index point relative to
    #: the track offset.
    sample_offset: int
    #: :code:`self[1]` – Track index number.
    number: int

    def __new__(cls, sample_offset: int, number: int) -> Self:
        validate_number("sample_offset", sample_offset, int, 0)
        validate_number("number", number, int, 0)
        return tuple.__new__(cls, (sample_offset, number))

    @classmethod
    def _from_unpack(
        cls, data: tuple[int, int, bytes], /
    ) -> FLACCueSheetTrackIndex:
        """
        Instantiate a :class:`FLACCueSheetTrackIndex` object using data
        unpacked from a bytes-like object.

        Parameters
        ----------
        data : tuple[int, int, bytes]; positional-only
            Unpacked :class:`FLACCueSheetTrackIndex` data.

        Returns
        -------
        track_index : minim.media.flac.FLACCueSheetTrackIndex
            :code:`CUESHEET_TRACK_INDEX` data.
        """
        if data[2] != 3 * b"\x00":
            raise ValueError(
                "Non-zero bits found in reserved section of "
                "CUESHEET_TRACK_INDEX data."
            )

        return tuple.__new__(cls, data[:2])

    @classmethod
    def from_stream(cls, stream: BytesLike, /) -> FLACCueSheetTrackIndex:
        """ 
        Instantiate a :class:`FLACCueSheetTrackIndex` object from a 
        bytes-like object.

        Parameters
        ----------
        bytestream : bytes, bytearray, memoryview, or mmap.mmap; \
        positional-only; optional
            Bytes-like object containing :code:`CUESHEET_TRACK_INDEX` 
            data.

        Returns
        -------
        track_index : minim.media.flac.FLACCueSheetTrackIndex
            :code:`CUESHEET_TRACK_INDEX` data.
        """
        *data, reserved = cls._STRUCT.unpack_from(as_buffer(stream))
        if reserved != 3 * b"\x00":
            raise ValueError(
                "Non-zero bits found in reserved section of "
                "CUESHEET_TRACK_INDEX data."
            )

        return tuple.__new__(cls, data)

    def serialize(self) -> bytes:
        """
        Serialize the :code:`CUESHEET_TRACK_INDEX` data to a bytestream.

        Returns
        -------
        bytestream : bytes
            Bytestream containing :code:`CUESHEET_TRACK_INDEX` data.
        """
        return self._STRUCT.pack(*self, 3 * b"\x00")


@dataclass(frozen=True, kw_only=True, slots=True)
class FLACMetadataBlock:
    """
    FLAC metadata block.

    .. important::

        At least one of :code:`type` or :code:`data` must be specified.

    Parameters
    ----------
    type : int; keyword-only; optional
        Metadata block type.

        **Valid values**:

        * :code:`0` – :code:`STREAMINFO`.
        * :code:`1` – :code:`PADDING`.
        * :code:`2` – :code:`APPLICATION`.
        * :code:`3` – :code:`SEEKTABLE`.
        * :code:`4` – :code:`VORBIS_COMMENT`.
        * :code:`5` – :code:`CUESHEET`.
        * :code:`6` – :code:`PICTURE`.

    length : int; keyword-only; optional
        Metadata block length in bytes.

    data : bytes, bytearray, minim.media.flac.FLACStreamInfo, \
    minim.media.flac.FLACApplication, minim.media.flac.FLACSeekTable, \
    minim.media.flac.FLACCueSheet, minim.media.metadata.VorbisComment, \
    or minim.media.metadata.APICFrame; keyword-only; optional
        Metadata block data. If :code:`type=1`, specify :code:`None`.
    """

    _TYPES = {
        0: "STREAMINFO",
        1: "PADDING",
        2: "APPLICATION",
        3: "SEEKTABLE",
        4: "VORBIS_COMMENT",
        5: "CUESHEET",
        6: "PICTURE",
    }

    #: Metadata block type.
    type: int | None = None
    #: Metadata block length in bytes.
    length: int | None = None
    #: Metadata block data.
    data: (
        FLACStreamInfo
        | FLACApplication
        | FLACSeekTable
        | VorbisComment
        | FLACCueSheet
        | APICFrame
        | None
    ) = None

    def __post_init__(self) -> None:
        if (type_ := self.type) is None:
            match self.data:
                case FLACStreamInfo():
                    self.type = 0
                    if self.length is None:
                        self.length = 34
                    elif self.length != 34:
                        raise ValueError(
                            "STREAMINFO block length must be 34, not "
                            f"{self.length}."
                        )
                case None:
                    self.type = 1
                    if self.length is None:
                        raise ValueError(
                            "At least one of `type` or `length` must "
                            "be provided."
                        )
                    validate_number("length", self.length, int, 0)
                case FLACApplication():
                    self.type = 2
                    actual_length = 4 + len(self.data["app_data"])
                    if self.length is None:
                        self.length = actual_length
                    elif self.length != actual_length:
                        raise ValueError(
                            "APPLICATION block length does not match "
                            "the length of the block data."
                        )
                case FLACSeekTable():
                    self.type = 3
                    actual_length = 18 * len(self.data.seek_points)
                    if self.length is None:
                        self.length = actual_length
                    elif self.length != actual_length:
                        raise ValueError(
                            "SEEKTABLE block length does not match the "
                            "length of the block data."
                        )
                case VorbisComment():
                    self.type = 4
                    actual_length = len(self.data.serialize())
                    if self.length is None:
                        self.length = actual_length
                    elif self.length != actual_length:
                        raise ValueError(
                            "VORBIS_COMMENT block length does not "
                            "match the length of the block data."
                        )
                case FLACCueSheet():
                    self.type = 5
                    actual_length = len(self.data.serialize())
                    if self.length is None:
                        self.length = actual_length
                    elif self.length != actual_length:
                        raise ValueError(
                            "CUESHEET block length does not match the "
                            "length of the block data."
                        )
                case APICFrame():
                    self.type = 6
                    actual_length = len(self.data.serialize())
                    if self.length is None:
                        self.length = actual_length
                    elif self.length != actual_length:
                        raise ValueError(
                            "PICTURE block length does not match the "
                            "length of the block data."
                        )
                case _:
                    raise TypeError(
                        f"Invalid type {type(self.data).__name__} for `data`."
                    )
        else:
            validate_number("type", type_, int, 0, 6)
            match type_:
                case 0:  # STREAMINFO
                    if not isinstance(self.data, FLACStreamInfo):
                        raise TypeError(
                            "STREAMINFO block data must be an instance "
                            "of FLACStreamInfo, not "
                            f"{type(self.data).__name__}."
                        )

                    if self.length is None:
                        self.length = 34
                    elif self.length != 34:
                        raise ValueError(
                            "STREAMINFO block length must be 34, not "
                            f"{self.length}."
                        )
                case 1:  # PADDING
                    validate_number("length", self.length, int, 0)
                    if self.data is not None:
                        raise ValueError("PADDING block data must be None.")
                case 2:  # APPLICATION
                    app = self.data
                    if not isinstance(app, FLACApplication):
                        raise TypeError(
                            "APPLICATION block data must be an "
                            "instance of FLACApplication, not "
                            f"{type(self.data).__name__}."
                        )

                    actual_length = 4 + len(app["app_data"])
                    if self.length is None:
                        self.length = actual_length
                    elif self.length != actual_length:
                        raise ValueError(
                            "APPLICATION block length does not match "
                            "the length of the block data."
                        )
                case 3:  # SEEKTABLE
                    if not isinstance(self.data, FLACSeekTable):
                        raise TypeError(
                            "SEEKTABLE block data must be an instance "
                            "of FLACSeekTable, not "
                            f"{type(self.data).__name__}."
                        )

                    actual_length = 18 * len(self.data.seek_points)
                    if self.length is None:
                        self.length = actual_length
                    elif self.length != actual_length:
                        raise ValueError(
                            "SEEKTABLE block length does not match the "
                            "length of the block data."
                        )
                case 4:  # VORBIS_COMMENT
                    if not isinstance(self.data, VorbisComment):
                        raise TypeError(
                            "VORBIS_COMMENT block data must be an "
                            "instance of VorbisComment, not "
                            f"{type(self.data).__name__}."
                        )

                    actual_length = len(self.data.serialize())
                    if self.length is None:
                        self.length = actual_length
                    elif self.length != actual_length:
                        raise ValueError(
                            "VORBIS_COMMENT block length does not "
                            "match the length of the block data."
                        )
                case 5:  # CUESHEET
                    if not isinstance(self.data, FLACCueSheet):
                        raise TypeError(
                            "CUESHEET block data must be an instance "
                            "of FLACCueSheet, not "
                            f"{type(self.data).__name__}."
                        )

                    actual_length = len(self.data.serialize())
                    if self.length is None:
                        self.length = actual_length
                    elif self.length != actual_length:
                        raise ValueError(
                            "CUESHEET block length does not match the "
                            "length of the block data."
                        )
                case 6:  # PICTURE
                    if not isinstance(self.data, APICFrame):
                        raise TypeError(
                            "PICTURE block data must be an instance of "
                            f"APICFrame, not {type(self.data).__name__}."
                        )

                    actual_length = len(self.data.serialize())
                    if self.length is None:
                        self.length = actual_length
                    elif self.length != actual_length:
                        raise ValueError(
                            "PICTURE block length does not match the "
                            "length of the block data."
                        )

    @classmethod
    def from_stream(
        cls, stream: BytesLike, /, type_: int, length: int | None = None
    ) -> FLACMetadataBlock:
        """
        Instantiate a :class:`FLACMetadataBlock` object from a 
        bytes-like object.

        Parameters
        ----------
        bytestream : bytes, bytearray, memoryview, or mmap.mmap; \
        positional-only; optional
            Bytes-like object containing metadata block data.

        type_ : int
            Metadata block type.

        length : int; optional
            Metadata block length.

        Returns
        -------
        block : minim.media.flac.FLACMetadataBlock
            Metadata block.
        """
        validate_number("type_", type_, int, 0, 6)

        stream = as_buffer(stream)
        if length is None:
            length = len(stream)

        match type_:
            case 0:  # STREAMINFO
                data = FLACStreamInfo.from_stream(stream)
            case 1:  # PADDING
                data = None
            case 2:  # APPLICATION
                data = FLACApplication.from_stream(stream)
            case 3:  # SEEKTABLE
                data = FLACSeekTable.from_stream(stream)
            case 4:  # VORBIS_COMMENT
                data = VorbisComment.from_stream(stream)
            case 5:  # CUESHEET
                data = FLACCueSheet.from_stream(stream)
            case 6:  # PICTURE
                data = APICFrame.from_stream(stream, format="XIPH")

        obj = cls.__new__(cls)
        set_obj_attr(obj, "type", type_)
        set_obj_attr(obj, "length", length)
        set_obj_attr(obj, "data", data)
        return obj

    def serialize(self) -> bytes:
        """
        Serialize only the metadata block data to a bytestream. The
        metadata block header should be prefixed by the calling scope
        since this class does not know whether the metadata block is the
        last metadata block before the audio data.

        Returns
        -------
        bytestream : bytes
            Bytestream containing metadata block data.
        """
        match self.type:
            case 1:  # PADDING
                return bytes(self.length)
            case 6:  # PICTURE
                return self.data.serialize(format="XIPH")
            case _:
                return self.data.serialize()


class FLACMetadataView:
    """
    View of FLAC metadata blocks.
    """

    def __init__(self, blocks: list[FLACMetadataBlock], /) -> None:
        self._blocks = blocks

    def __getitem__(self, index: int, /) -> FLACMetadataBlock:
        return self._blocks[index]

    def __len__(self):
        return len(self._blocks)

    def __iter__(self):
        return iter(self._blocks)


class FLACAudio(Audio):
    """
    FLAC audio file.
    """

    __slots__ = ("_audio_offset",)

    @property
    def format_metadata(self) -> FLACMetadataView:
        """
        Structural metadata instrinsic to the file format or container.

        .. tip::

           :code:`FLACMetadataView` is a read-only view into the list
           containing the FLAC metadata blocks.
        """
        return FLACMetadataView(self._format_metadata)

    def load_metadata(self) -> None:
        """
        Load audio metadata.
        """
        self.open()
        file_path = self._file_path
        view = self._view

        offset = 4
        if view[:offset] != b"fLaC":
            raise ValueError(f"{file_path} is not a valid FLAC file.")

        self._format_metadata = []
        seen_vorbis_comment = False
        block_header = 0x7F
        while not block_header & 0x80:
            block_header = view[offset]
            offset += 1

            end_offset = offset + 3
            block_length = int.from_bytes(
                view[offset:end_offset], byteorder="big"
            )
            offset = end_offset

            end_offset = offset + block_length
            block_data = view[offset:end_offset]
            offset = end_offset

            match block_type := block_header & 0x7F:
                case 0:  # STREAMINFO
                    if self._format_metadata:
                        raise RuntimeError(
                            "STREAMINFO block is not the first "
                            "metadata block or appears multiple times "
                            f"in '{file_path}'."
                        )

                    metadata_block = FLACMetadataBlock.from_stream(
                        block_data, type_=block_type, length=block_length
                    )
                    self._format_metadata.append(metadata_block)
                    self._stream_info = metadata_block.data
                case 1:  # PADDING
                    if (
                        self._format_metadata
                        and (prev_block := self._format_metadata[-1]).type == 1
                    ):
                        set_obj_attr(
                            prev_block,
                            "length",
                            prev_block.length + block_length + 4,
                        )
                    else:
                        self._format_metadata.append(
                            FLACMetadataBlock.from_stream(
                                block_data,
                                type_=block_type,
                                length=block_length,
                            )
                        )
                case (
                    2 | 3 | 5 | 6
                ):  # APPLICATION / SEEKTABLE / CUESHEET / PICTURE
                    self._format_metadata.append(
                        FLACMetadataBlock.from_stream(
                            block_data, type_=block_type, length=block_length
                        )
                    )
                case 4:  # VORBIS_COMMENT
                    if seen_vorbis_comment:
                        raise RuntimeError(
                            "VORBIS_COMMENT block appears multiple "
                            f"times in '{file_path}'."
                        )

                    metadata_block = FLACMetadataBlock.from_stream(
                        block_data,
                        type_=block_type,
                        length=block_length,
                    )
                    self._format_metadata.append(metadata_block)
                    self._tags = metadata_block.data
                case 127:  # INVALID
                    raise ValueError(
                        "Metadata block with invalid block type found "
                        f"in '{file_path}'."
                    )
                case _:  # RESERVED
                    raise ValueError(
                        "Metadata block with reserved block type "
                        f"{block_type} found in '{file_path}'."
                    )

        if not self._format_metadata or self._format_metadata[0].type != 0:
            raise RuntimeError(
                f"STREAMINFO block was not found in '{file_path}'."
            )

        block_data = None
        self._audio_offset = offset
        self.close()

    def add_metadata(
        self,
        metadata: FLACMetadataBlock | OrderedCollection[FLACMetadataBlock],
        /,
        *,
        index: int | None = None,
    ) -> None:
        """
        Add audio metadata.

        Parameters
        ----------
        metadata : minim.media.flac.FLACMetadataBlock or \
        OrderedCollection[minim.media.flac.FLACMetadataBlock]; \
        positional-only
            Metadata blocks. 
            
            .. note::
            
               :code:`PADDING` blocks are automatically merged with 
               adjacent metadata blocks of the same type. The 4-byte 
               headers of merged blocks are reclaimed as usable space 
               within the resulting contiguous block.

        index : int; keyword-only; optional
            Index at which to insert the new metadata blocks. If 
            :code:`None`, existing :code:`PADDING` blocks of sufficient 
            size are overwritten to avoid file restructuring. If no 
            suitable :code:`PADDING` blocks are available, the new data
            is appended to the end of the existing metadata blocks.
        """
        if not isinstance(metadata, ORDERED_COLLECTION_TYPES):
            metadata = [metadata]

        for block in metadata:
            if not isinstance(block, FLACMetadataBlock):
                raise TypeError(
                    "`metadata` must be an FLACMetadataBlock instance "
                    "or an ordered collection of FLACMetadataBlock "
                    "instances."
                )

            if block.type == 0:
                raise ValueError(
                    "STREAMINFO metadata blocks cannot be added, "
                    "moved, or removed."
                )

        num_metadata_blocks = len(self._format_metadata)
        if index is not None:
            if index < 0:
                index += num_metadata_blocks
            if not 0 <= index <= num_metadata_blocks:
                raise ValueError(
                    f"Metadata block index {index} is out of range."
                )

        for new_block in metadata:
            placed_idx = None
            is_padding = new_block.type == 1

            # Try to insert new non-PADDING blocks inside existing
            # PADDING blocks
            if index is None and not is_padding:
                for idx, block in enumerate(self._format_metadata):
                    if block.type == 1:
                        if block.length == new_block.length:
                            self._format_metadata[idx] = new_block
                            placed_idx = idx
                            break
                        elif block.length >= (
                            new_block_length := new_block.length + 4
                        ):
                            self._format_metadata[idx] = new_block
                            self._format_metadata.insert(
                                idx + 1,
                                FLACMetadataBlock(
                                    type=1,
                                    length=block.length - new_block_length,
                                ),
                            )
                            placed_idx = idx
                            num_metadata_blocks += 1
                            break

            # If the new block did not fit in any existing PADDING
            # blocks, add it at the user-specified index or at the end
            if placed_idx is None:
                placed_idx = num_metadata_blocks if index is None else index
                self._format_metadata.insert(placed_idx, new_block)
                num_metadata_blocks += 1
                if index is not None:
                    index += 1

            # If the new block is PADDING, check adjacent blocks to
            # merge
            if is_padding:
                if (
                    next_idx := placed_idx + 1
                ) < num_metadata_blocks and self._format_metadata[
                    next_idx
                ].type == 1:  # right
                    self._format_metadata[placed_idx] = FLACMetadataBlock(
                        type=1,
                        length=(
                            self._format_metadata[placed_idx].length
                            + self._format_metadata.pop(next_idx).length
                            + 4
                        ),
                    )
                    num_metadata_blocks -= 1

                if (next_idx := placed_idx - 1) >= 0 and self._format_metadata[
                    next_idx
                ].type == 1:  # left
                    block = self._format_metadata.pop(placed_idx)
                    placed_idx -= 1
                    self._format_metadata[placed_idx] = FLACMetadataBlock(
                        type=1,
                        length=(
                            self._format_metadata[placed_idx].length
                            + block.length
                            + 4
                        ),
                    )
                    num_metadata_blocks -= 1
                    if index is not None:
                        index -= 1

    def move_metadata(
        self,
        *,
        to_index: int,
        from_indices: int | Collection[int] | None = None,
        from_types: int | Collection[int] | None = None,
    ) -> None:
        """ """
        ...  # TODO

    def remove_metadata(
        self,
        *,
        indices: int | Collection[int] | None = None,
        types: int | Collection[int] | None = None,
    ) -> None:
        """
        Remove audio metadata.

        .. note::

           To minimize disk I/O overhead, removed metadata blocks are
           transparently replaced with :code:`PADDING` blocks of
           equivalent length. This preserves the existing file offsets
           and avoids a full rewrite of the audio stream. To reclaim
           disk space by stripping all :code:`PADDING` blocks, specify
           :code:`remove_padding=True` when calling
           :meth:`save_metadata`.

        .. important::

           At most one of `indices` or `types` must be provided.

        Parameters
        ----------
        indices : int or Collection[int]; keyword-only; optional
            Indices of metadata blocks to remove.

        types : int or Collection[int]; keyword-only; optional
            Types of metadata blocks to remove.

            **Valid values**:

            * :code:`0` – :code:`STREAMINFO`.
            * :code:`1` – :code:`PADDING`.
            * :code:`2` – :code:`APPLICATION`.
            * :code:`3` – :code:`SEEKTABLE`.
            * :code:`4` – :code:`VORBIS_COMMENT`.
            * :code:`5` – :code:`CUESHEET`.
            * :code:`6` – :code:`PICTURE`.
        """
        has_indices = indices is not None
        has_types = types is not None
        if has_indices and has_types:
            raise ValueError(
                "At most one of `indices` or `types` can be specified."
            )

        if has_indices:
            num_metadata_blocks = len(self._format_metadata)
            if isinstance(indices, int):
                indices = {
                    (indices + num_metadata_blocks) if indices < 0 else indices
                }
            elif not isinstance(indices, set):
                indices = set(
                    (idx + num_metadata_blocks) if idx < 0 else idx
                    for idx in indices
                )

            if 0 in indices:
                raise ValueError(
                    "STREAMINFO metadata blocks cannot be added, "
                    "moved, or removed."
                )

            for block_idx in indices:
                if not 0 <= block_idx < num_metadata_blocks:
                    raise ValueError(
                        f"Metadata block index {block_idx} is out of range."
                    )
                self._format_metadata[block_idx] = FLACMetadataBlock(
                    type=1, length=self._format_metadata[block_idx].length
                )

        elif has_types:
            if isinstance(types, int):
                types = {types}
            elif not isinstance(types, set):
                types = set(types)
            types.discard(1)

            if 0 in types:
                raise ValueError(
                    "STREAMINFO metadata blocks cannot be added, "
                    "moved, or removed."
                )

            for block_idx, block in enumerate(self._format_metadata):
                if block.type in types:
                    self._format_metadata[block_idx] = FLACMetadataBlock(
                        type=1, length=block.length
                    )
        else:
            raise ValueError(
                "At least one of `indices` or `types` must be specified."
            )

    def save_metadata(
        self,
        file_path: PathLike | None = None,
        /,
        *,
        remove_padding: bool = False,
    ) -> None:
        """ """
        ...  # TODO

        # if (
        #     4 + sum(block.length + 4 for block in self._format_metadata)
        #     > self._audio_offset
        # ):
        #     ...
        # else:
        #     ...
