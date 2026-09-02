"""
Free Lossless Audio Codec (FLAC) audio file handler and metadata blocks.
"""

from __future__ import annotations

import string
import struct
import warnings
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import FrozenInstanceError, dataclass
from typing import TYPE_CHECKING, Any, ClassVar, NamedTuple

from .._types import COLLECTION_TYPES, ORDERED_COLLECTION_TYPES, BytesLike
from .._utility import (
    ASCII_CHARS_REGEX,
    as_buffer,
    join_values,
    prepare_isrc,
    set_obj_attr,
    validate_number,
    validate_range,
    validate_type,
)
from ._shared import Audio, NULPadding
from .metadata._shared import AudioStreamInfo
from .metadata._vorbis import VorbisComment
from .metadata.id3._frames import ID3v2APICFrame, ID3v2FrameFlags

if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import Self

    from .._types import Collection, OrderedCollection, PathLike


__all__ = [  # noqa: RUF022
    "FLACAudio",
    "FLACStreamInfo",
    "FLACPadding",
    "FLACApplication",
    "FLACSeekTable",
    "FLACSeekPoint",
    "FLACCueSheet",
    "FLACCueSheetTrack",
    "FLACCueSheetTrackIndex",
    "FLACPicture",
    "UnknownFLACMetadataBlock",
    "FLACMetadataView",
]


class FLACMetadataBlock(ABC):
    """
    Abstract base class for FLAC metadata blocks.
    """

    __slots__ = ()

    @classmethod
    @abstractmethod
    def from_stream(cls, stream: BytesLike, /) -> Self:
        """
        Create an instance of a :class:`FLACMetadataBlock` subclass from
        a bytes-like object.

        Parameters
        ----------
        stream : BytesLike; positional-only; optional
            Bytes-like object containing FLAC metadata block data.

        Returns
        -------
        block : minim.media.flac.FLACMetadataBlock
            FLAC metadata block.
        """
        ...

    @property
    @abstractmethod
    def _block_data_length(self) -> int:
        """
        Length of the encoded metadata block data, in bytes.
        """
        ...

    @property
    @abstractmethod
    def _block_type(self) -> int:
        """
        Metadata block type.
        """
        ...

    @property
    def block_data_length(self) -> int:
        """
        :bdg-primary:`get` :bdg-secondary-line:`set`
        Length of the encoded metadata block data, in bytes.
        """
        return self._block_data_length

    @property
    def block_type(self) -> int:
        """
        :bdg-primary:`get` :bdg-secondary-line:`set`
        Metadata block type.
        """
        return self._block_type

    @abstractmethod
    def serialize(self) -> bytes:
        """
        Serialize the FLAC metadata block data to a bytestream.

        Returns
        -------
        stream : bytes
            Bytestream containing the FLAC metadata block data.
        """
        ...


@dataclass(frozen=True, kw_only=True, repr=True, slots=True)
class FLACStreamInfo(AudioStreamInfo, FLACMetadataBlock):
    """
    FLAC audio stream information (:code:`STREAMINFO` metadata block).

    Parameters
    ----------
    num_channels : int; keyword-only
        Number of channels.

    sample_rate : int; keyword-only
        Sample rate, in hertz.

    bit_depth : int; keyword-only
        Bits per sample.

    num_samples : int; keyword-only
        Total number of samples.

    min_block_size : int; keyword-only
        Minimum block size, in samples.

        **Valid range**: :code:`16` to :code:`65_535`.

    max_block_size : int; keyword-only
        Maximum block size, in samples.

        **Valid range**: :code:`16` to :code:`65_535`.

    min_frame_size : int; keyword-only
        Minimum frame size, in bytes.

        **Valid range**: :code:`0` to :code:`16_777_215`.

    max_frame_size : int; keyword-only
        Maximum frame size, in bytes.

        **Valid range**: :code:`0` to :code:`16_777_215`.

    md5 : str; keyword-only
        MD5 hash of the unencoded audio data.

    Raises
    ------
    TypeError
        If any of the arguments are not of the correct type.

    ValueError
        If any of the numeric arguments are outside their allowed
        ranges.
    """

    _HEX_DIGITS: ClassVar[set[str]] = set(string.hexdigits)
    _STRUCT_HH: ClassVar[struct.Struct] = struct.Struct(">HH")
    _STRUCT_Q: ClassVar[struct.Struct] = struct.Struct(">Q")

    _NUM_CHANNELS_RANGE: ClassVar[tuple[int, int]] = (1, 8)
    _SAMPLE_RATE_RANGE: ClassVar[tuple[int, int]] = (1, 655_350)
    _BIT_DEPTH_RANGE: ClassVar[tuple[int, int]] = (1, 32)

    _block_data_length: ClassVar[int] = 34
    _block_type: ClassVar[int] = 0

    #: :bdg-primary:`get` :bdg-secondary-line:`set` Minimum block
    #: size in samples.
    min_block_size: int
    #: :bdg-primary:`get` :bdg-secondary-line:`set` Maximum block
    #: size in samples.
    max_block_size: int
    #: :bdg-primary:`get` :bdg-secondary-line:`set` Minimum frame
    #: size in bytes.
    min_frame_size: int
    #: :bdg-primary:`get` :bdg-secondary-line:`set` Maximum frame
    #: size in bytes.
    max_frame_size: int
    #: :bdg-primary:`get` :bdg-secondary-line:`set` MD5 hash of the
    #: unencoded audio data.
    md5: str

    def __post_init__(self) -> None:
        super().__post_init__()
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
                "`min_frame_size` must be less than or equal to "
                "`max_frame_size`."
            )

        md5 = self.md5
        validate_type("md5", md5, str)
        if len(md5) != 32 or not all(c in self._HEX_DIGITS for c in md5):
            raise ValueError(
                "`md5` must be a 32-character hexadecimal string."
            )

    @classmethod
    def from_stream(cls, stream: BytesLike, /, *, strict: bool = True) -> Self:
        """
        Instantiate a :class:`FLACStreamInfo` object from a bytes-like
        object.

        Parameters
        ----------
        stream : BytesLike; positional-only; optional
            Bytes-like object containing :code:`STREAMINFO` metadata
            block data.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the FLAC
            format specifications.

        Returns
        -------
        stream_info : minim.media.flac.FLACStreamInfo
            :code:`STREAMINFO` metadata block.

        Raises
        ------
        TypeError
            If `stream` is not a bytes-like object.

        ValueError
            If `stream` contains audio stream information that is
            outside the allowed ranges.
        """
        stream = as_buffer(stream)
        min_block_size = int.from_bytes(stream[:2], byteorder="big")
        max_block_size = int.from_bytes(stream[2:4], byteorder="big")
        if strict and max_block_size < min_block_size:
            raise ValueError(
                "`min_block_size` must be less than or equal to "
                "`max_block_size`."
            )

        min_frame_size = int.from_bytes(stream[4:7], byteorder="big")
        max_frame_size = int.from_bytes(stream[7:10], byteorder="big")
        if strict and (
            min_frame_size
            and max_frame_size
            and min_frame_size > max_frame_size
        ):
            raise ValueError(
                "`min_frame_size` must be less than or equal to "
                "`max_frame_size`."
            )

        sample_rate = int.from_bytes(stream[10:13], byteorder="big") >> 4
        if strict:
            validate_range("sample_rate", sample_rate, *cls._SAMPLE_RATE_RANGE)
        num_channels = ((stream[12] & 0x0E) >> 1) + 1
        bit_depth = ((stream[12] & 0x01) << 4) + ((stream[13] & 0xF0) >> 4) + 1
        if strict:
            validate_range("bit_depth", bit_depth, *cls._BIT_DEPTH_RANGE)

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

    @property
    def bitrate(self) -> int:
        """
        :bdg-primary:`get` :bdg-secondary-line:`set`
        Bitrate, in kilobits per second.
        """
        return super().bitrate

    def serialize(self) -> bytes:
        """
        Serialize the :code:`STREAMINFO` metadata block data to a
        bytestream.

        Returns
        -------
        stream : bytes
            Bytestream containing the :code:`STREAMINFO` metadata block
            data.
        """
        return b"".join(
            (
                self.min_block_size.to_bytes(length=2, byteorder="big"),
                self.max_block_size.to_bytes(length=2, byteorder="big"),
                self.min_frame_size.to_bytes(length=3, byteorder="big"),
                self.max_frame_size.to_bytes(length=3, byteorder="big"),
                (
                    (self.sample_rate & 0xFFFFF) << 44
                    | ((self.num_channels - 1) & 0x7) << 41
                    | ((self.bit_depth - 1) & 0x1F) << 36
                    | (self.num_samples & 0xFFFFFFFFF)
                ).to_bytes(8, byteorder="big"),
                bytes.fromhex(self.md5),
            )
        )


class FLACPadding(NULPadding, FLACMetadataBlock):
    """
    FLAC :code:`PADDING` metadata block.
    """

    _block_type: ClassVar[int] = 1

    __slots__ = ()

    @property
    def _block_data_length(self) -> int:
        """
        Padding length, in bytes.
        """
        return self._length

    @property
    def block_data_length(self) -> int:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Padding length, in bytes.
        """
        return self._length

    @block_data_length.setter
    def block_data_length(self, length: int, /) -> None:
        validate_number("length", length, int, 0)
        self._length = length


class FLACApplication(FLACMetadataBlock):
    """
    FLAC :code:`APPLICATION` metadata block.
    """

    _block_type: ClassVar[int] = 2

    def __init__(
        self,
        app_id: bytes | bytearray | str,
        app_data: bytes | bytearray = b"",
    ) -> None:
        """
        Parameters
        ----------
        app_id : bytes, bytearray, or str; keyword-only
            Four-character binary or eight-character hexadecimal
            application ID.

            .. seealso::

               `FLAC Application Metadata Block IDs
               <https://www.iana.org/assignments/flac/flac.xhtml>`_ –
               Registry of eight-character hexadecimal IDs for
               third-party applications.

        app_data : bytes or bytearray; keyword-only; \
        default: :code:`b""`
            Application data.

        Raises
        ------
        TypeError
            If `app_id` or `app_data` are not bytes-like objects.

        ValueError
            If `app_id` is not a hexadecimal string of length 4.
        """
        self.app_id = app_id
        self._app_data = app_data

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(app_id={self._app_id!r}, "
            f"app_data=<{len(self._app_data)} byte(s)>)"
        )

    @classmethod
    def from_stream(cls, stream: BytesLike, /) -> Self:
        """
        Instantiate a :class:`FLACApplication` object from a bytes-like
        object.

        Parameters
        ----------
        stream : BytesLike; positional-only; optional
            Bytes-like object containing :code:`APPLICATION` metadata
            block data.

        Returns
        -------
        app : minim.media.flac.FLACApplication
            :code:`APPLICATION` metadata block.
        """
        stream = as_buffer(stream)
        obj = cls.__new__(cls)
        obj._app_id = stream[:4].tobytes()
        obj._app_data = stream[4:].tobytes()
        return obj

    @property
    def _block_data_length(self) -> int:
        """
        Length of the encoded :code:`APPLICATION` metadata block data,
        in bytes.
        """
        return 4 + len(self._app_data)

    @property
    def app_id(self) -> bytes | bytearray:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Application ID.
        """
        return self._app_id

    @app_id.setter
    def app_id(self, value: bytes | bytearray | str, /) -> None:
        validate_type("app_id", value, bytes | bytearray | str)
        if isinstance(value, str):
            try:
                value = bytes.fromhex(value)
            except ValueError as e:
                raise ValueError(
                    "`app_id` must be a valid hexadecimal string."
                ) from e
        if len(value) != 4:
            raise ValueError("A binary `app_id` must have length 4.")
        self._app_id = value

    @property
    def app_data(self) -> bytes | bytearray:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Application data.
        """
        return self._app_data

    @app_data.setter
    def app_data(self, value: bytes | bytearray, /) -> None:
        validate_type("app_data", value, bytes | bytearray)
        self._app_data = value

    def serialize(self) -> bytes:
        """
        Serialize the :code:`APPLICATION` metadata block data to a
        bytestream.

        Returns
        -------
        stream : bytes
            Bytestream containing the :code:`APPLICATION` metadata block
            data.
        """
        return self._app_id + self._app_data


@dataclass(frozen=True, kw_only=True, repr=False, slots=True)
class FLACSeekTable(FLACMetadataBlock):
    """
    FLAC :code:`SEEKTABLE` metadata block.

    Parameters
    ----------
    seek_points : \
    OrderedCollection[minim.media.flac.FLACSeekPoint, ...]; keyword-only
        Seek points.

    Raises
    ------
    TypeError
        If `seek_points` is not a tuple or list of
        :class:`FLACSeekPoint` objects.

    ValueError
        If `seek_points` contain :class:`FLACSeekPoint` objects with
        invalid data.
    """

    _block_type: ClassVar[int] = 3

    #: :bdg-primary:`get` :bdg-secondary-line:`set` Seek points.
    seek_points: tuple[FLACSeekPoint, ...]

    def __post_init__(self) -> None:
        seek_points = self.seek_points
        if not isinstance(seek_points, tuple):
            if not isinstance(seek_points, list):
                raise TypeError(
                    f"`seek_points` must be a(n) tuple | list, not "
                    f"a(n) {type(seek_points).__name__}."
                )
            seek_points = self.seek_points = tuple(seek_points)
        self._validate_seek_points(seek_points)

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"seek_points=<{len(self.seek_points)} seek point(s)>)"
        )

    @classmethod
    def from_stream(cls, stream: BytesLike, /, *, strict: bool = True) -> Self:
        """
        Instantiate a :class:`FLACSeekTable` object from a bytes-like
        object.

        Parameters
        ----------
        stream : BytesLike; positional-only; optional
            Bytes-like object containing :code:`SEEKTABLE` metadata
            block data.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the FLAC
            format specifications.

        Returns
        -------
        seek_table : minim.media.flac.FLACSeekTable
            :code:`SEEKTABLE` metadata block.

        Raises
        ------
        TypeError
            If `stream` is not a bytes-like object.

        ValueError
            If `stream` contains an invalid :code:`SEEKTABLE` block or
            :code:`SEEKPOINT` data.
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
        cls._validate_seek_points(seek_points, custom=False, strict=strict)

        obj = cls.__new__(cls)
        set_obj_attr(obj, "seek_points", seek_points)
        return obj

    @staticmethod
    def _validate_seek_points(
        seek_points: tuple[FLACSeekPoint, ...],
        /,
        *,
        custom: bool = True,
        strict: bool = True,
    ) -> None:
        """
        Validate seek points (:code:`SEEKPOINT`) in a :code:`SEEKTABLE`
        metadata block.

        Parameters
        ----------
        seek_points : tuple[minim.media.flac.FLACSeekPoint, ...]; \
        positional-only
            Seek points.

        custom : bool; keyword-only; default: :code:`True`
            Whether the seek points are user-defined and should have
            their types validated.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the FLAC
            format specifications.

        Raises
        ------
        TypeError
            If any of `seek_points` are not :class:`FLACSeekPoint`
            objects.

        ValueError
            If `seek_points` contain :class:`FLACSeekPoint` objects that
            have duplicate sample numbers or are out of order.
        """
        if strict:
            if custom:
                validate_type("seek_points[0]", seek_points[0], FLACSeekPoint)
            seen_sample_numbers = {seek_points[0].sample_number}
            for seek_point_idx, seek_point in enumerate(seek_points[1:]):
                if custom:
                    validate_type(
                        f"seek_points[{seek_point_idx + 1}]",
                        seek_point,
                        FLACSeekPoint,
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
        elif custom:
            for seek_point_idx, seek_point in enumerate(seek_points):
                validate_type(
                    f"seek_points[{seek_point_idx}]", seek_point, FLACSeekPoint
                )

    @property
    def _block_data_length(self) -> int:
        """
        Length of encoded :code:`SEEKTABLE` metadata block data, in
        bytes.
        """
        return 18 * len(self.seek_points)

    def serialize(self) -> bytes:
        """
        Serialize the :code:`SEEKTABLE` metadata block data to a
        bytestream.

        Returns
        -------
        stream : bytes
            Bytestream containing the :code:`SEEKTABLE` metadata block
            data.
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

    Raises
    ------
    TypeError
        If any of the arguments are not of the correct type.

    ValueError
        If any of the numeric arguments are outside their allowed
        ranges.
    """

    _STRUCT: ClassVar[struct.Struct] = struct.Struct(">QQH")

    __slots__ = ()

    #: :bdg-primary:`get` :bdg-secondary-line:`set` :code:`self[0]` –
    #: Sample number of the first sample in the target frame.
    sample_number: int
    #: :bdg-primary:`get` :bdg-secondary-line:`set` :code:`self[1]` –
    #: Byte offset of the target frame header relative to the first
    #: frame header.
    byte_offset: int
    #: :bdg-primary:`get` :bdg-secondary-line:`set` :code:`self[2]` –
    #: Number of samples in the target frame.
    num_samples: int

    def __new__(
        cls, sample_number: int, byte_offset: int, num_samples: int
    ) -> Self:
        validate_number("sample_number", sample_number, int, 0)
        validate_number("byte_offset", byte_offset, int, 0)
        validate_number("num_samples", num_samples, int, 0)
        return tuple.__new__(cls, (sample_number, byte_offset, num_samples))

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(sample_number={self.sample_number}, "
            f"byte_offset={self.byte_offset}, "
            f"num_samples={self.num_samples})"
        )

    @classmethod
    def _from_unpack(cls, data: tuple[int, int, int], /) -> Self:
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
    def from_stream(cls, stream: bytes, /) -> Self:
        """
        Instantiate a :class:`FLACSeekPoint` object from a bytes-like
        object.

        Parameters
        ----------
        stream : bytes, bytearray, memoryview, or mmap.mmap; \
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
        stream : bytes
            Bytestream containing the :code:`SEEKPOINT` data.
        """
        return self._STRUCT.pack(*self)


@dataclass(frozen=True, kw_only=True, repr=False, slots=True)
class FLACCueSheet(FLACMetadataBlock):
    """
    FLAC :code:`CUESHEET` metadata block.

    Parameters
    ----------
    media_catalog_number : str; keyword-only
        Media catalog number.

    num_lead_in_samples : int; keyword-only
        Number of lead-in samples for CD-DA cue sheets.

    is_cd : bool; keyword-only
        Whether the cue sheet is for CD-DA.

    tracks : \
    OrderedCollection[minim.media.flac.FLACCueSheetTrack, ...]; \
    keyword-only
        Tracks.

    Raises
    ------
    TypeError
        If any of the arguments are not of the correct type.

    ValueError
        If any of the arguments are outside their allowed ranges or
        contain invalid values.
    """

    _STRUCT: ClassVar[struct.Struct] = struct.Struct(">128sQB258sB")

    _block_type: ClassVar[int] = 5

    #: :bdg-primary:`get` :bdg-secondary-line:`set` Media catalog
    #: number.
    media_catalog_number: str
    #: :bdg-primary:`get` :bdg-secondary-line:`set` Number of lead-in
    #: samples for CD-DA cue sheets.
    num_lead_in_samples: int
    #: :bdg-primary:`get` :bdg-secondary-line:`set` Whether the cue
    #: sheet is for CD-DA.
    is_cd: bool
    #: :bdg-primary:`get` :bdg-secondary-line:`set` Tracks.
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
                raise TypeError(
                    f"`tracks` must be a(n) tuple | list, not "
                    f"a(n) {type(tracks).__name__}."
                )
            tracks = self.tracks = tuple(tracks)

        if not (num_tracks := len(tracks)) or is_cd and num_tracks > 100:
            raise ValueError(
                f"Invalid number of tracks ({num_tracks}) in CUESHEET block."
            )

        self._validate_tracks(tracks, is_cd=is_cd)

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"media_catalog_number={self.media_catalog_number!r}, "
            f"num_lead_in_samples={self.num_lead_in_samples}, "
            f"is_cd={self.is_cd}, tracks=<{len(self.tracks)} track(s)>)"
        )

    @classmethod
    def from_stream(cls, stream: BytesLike, /, *, strict: bool = True) -> Self:
        """
        Instantiate a :class:`FLACCueSheet` object from a bytes-like
        object.

        Parameters
        ----------
        stream : BytesLike; positional-only; optional
            Bytes-like object containing :code:`CUESHEET` metadata block
            data.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the FLAC
            format specifications.

        Returns
        -------
        cue_sheet : minim.media.flac.FLACCueSheet
            :code:`CUESHEET` metadata block.

        Raises
        ------
        TypeError
            If `stream` is not a bytes-like object.

        ValueError
            If `stream` contains an invalid :code:`CUESHEET` block,
            :code:`CUESHEET_TRACK` data, or :code:`CUESHEET_TRACK_INDEX`
            data.
        """
        stream = as_buffer(stream)
        (
            media_catalog_number,
            num_lead_in_samples,
            is_cd,
            reserved,
            num_tracks,
        ) = cls._STRUCT.unpack_from(stream)
        if strict:
            if is_cd & 0x7F or reserved != 258 * b"\x00":
                raise ValueError(
                    "Non-zero bits found in reserved section of CUESHEET block."
                )
            if not num_tracks:
                raise ValueError(
                    f"Invalid number of tracks ({num_tracks}) in CUESHEET block."
                )

        media_catalog_number = media_catalog_number.rstrip(b"\x00").decode(
            encoding="utf-8"
        )
        if strict and not ASCII_CHARS_REGEX.match(media_catalog_number):
            raise ValueError(
                "`media_catalog_number` must contain only ASCII "
                "characters 0x20 (' ') through 0x7D ('}')."
            )

        is_cd = bool(is_cd & 0x80)
        if strict:
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
                        f"{num_lead_in_samples}, for non-CD-DA "
                        "CUESHEET block."
                    )

        offset = 396
        tracks = []
        for _ in range(num_tracks):
            track = FLACCueSheetTrack.from_stream(
                stream[offset:], strict=strict
            )
            offset += 36 + 12 * len(track.indices)
            tracks.append(track)
        tracks = tuple(tracks)
        cls._validate_tracks(tracks, is_cd=is_cd, custom=False, strict=strict)

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
        strict: bool = True,
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

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the FLAC
            format specifications.

        Raises
        ------
        TypeError
            If any of `tracks` are not :class:`FLACCueSheetTrack`
            objects.

        ValueError
            If `tracks` contain :class:`FLACCueSheetTrack` objects with
            duplicate or invalid track numbers, the wrong number of
            track indices, or sample offsets indivisible by 588.
        """
        if strict:
            seen_track_numbers = set()
            for track_idx, track in enumerate(tracks):
                if custom:
                    validate_type(
                        f"tracks[{track_idx}]", track, FLACCueSheetTrack
                    )
                track_number = track.number
                if track_number in seen_track_numbers:
                    raise ValueError(
                        "CUESHEET block has multiple tracks with track "
                        f"number {track_number}."
                    )

                if not track_number or (
                    is_cd
                    and not (1 <= track_number <= 99 or track_number == 170)
                ):
                    raise ValueError(
                        f"Invalid CUESHEET track number {track_number} "
                        f"for {'' if is_cd else 'non-'}CD-DA track at "
                        f"sample offset {track.sample_offset}."
                    )
                seen_track_numbers.add(track_number)

                num_track_indices = len(track.indices)
                if (
                    is_lead_out := (
                        is_cd
                        and track_number == 170
                        or not is_cd
                        and track_number == 255
                    )
                ) and num_track_indices:
                    raise ValueError(
                        "Lead-out CUESHEET tracks cannot have any "
                        "track indices."
                    )
                elif not is_lead_out and not num_track_indices:
                    raise ValueError(
                        "Non-lead-out CUESHEET tracks must have at "
                        "least one track index."
                    )

                if is_cd:
                    for track_index in track.indices:
                        if track_index.sample_offset % 588:
                            raise ValueError(
                                "Sample offsets for CD-DA track "
                                "indices in CUESHEET block must be "
                                "divisible by 588."
                            )

            if track.number != (
                lead_out_track_number := 170 if is_cd else 255
            ):
                raise ValueError(
                    "The last track in a CUESHEET block must be a "
                    "lead-out track with track number "
                    f"{lead_out_track_number}."
                )
        elif custom:
            for track_idx, track in enumerate(tracks):
                validate_type(f"tracks[{track_idx}]", track, FLACCueSheetTrack)

    @property
    def _block_data_length(self) -> int:
        """
        Length of encoded :code:`CUESHEET` metadata block data, in
        bytes.
        """
        return 396 + sum(track._length for track in self.tracks)

    def serialize(self) -> bytes:
        """
        Serialize the :code:`CUESHEET` metadata block data to a
        bytestream.

        Returns
        -------
        stream : bytes
            Bytestream containing the :code:`CUESHEET` metadata block
            data.
        """
        return self._STRUCT.pack(
            self.media_catalog_number.encode(encoding="utf-8"),
            self.num_lead_in_samples,
            self.is_cd << 7,
            258 * b"\x00",
            len(self.tracks),
        ) + b"".join(track.serialize() for track in self.tracks)


@dataclass(frozen=True, kw_only=True, repr=False, slots=True)
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

    tracks : \
    OrderedCollection[minim.media.flac.FLACCueSheetTrackIndex]; \
    keyword-only
        Track indices.

    Raises
    ------
    TypeError
        If any of the arguments are not of the correct type.

    ValueError
        If any of the arguments are outside their allowed ranges or
        contain invalid values.
    """

    _STRUCT: ClassVar[struct.Struct] = struct.Struct(">QB12sB13sB")

    #: :bdg-primary:`get` :bdg-secondary-line:`set` Sample offset of
    #: the track relative to the beginning of the FLAC audio stream.
    sample_offset: int
    #: :bdg-primary:`get` :bdg-secondary-line:`set` Track number.
    number: int
    #: :bdg-primary:`get` :bdg-secondary-line:`set` International
    #: Standard Recording Code (ISRC).
    isrc: str
    #: :bdg-primary:`get` :bdg-secondary-line:`set` Whether the track
    #: contains audio data.
    is_audio: bool
    #: :bdg-primary:`get` :bdg-secondary-line:`set` Whether the track
    #: has pre-emphasis.
    has_pre_emphasis: bool
    #: :bdg-primary:`get` :bdg-secondary-line:`set` Track indices.
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
                raise TypeError(
                    f"`indices` must be a(n) tuple | list, not a(n) "
                    f"{type(indices).__name__}."
                )
            indices = self.indices = tuple(indices)

        self._validate_indices(indices)

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(sample_offset={self.sample_offset}, "
            f"number={self.number}, isrc={self.isrc!r}, "
            f"is_audio={self.is_audio}, "
            f"has_pre_emphasis={self.has_pre_emphasis}, "
            f"indices=<{len(self.indices)} index(es)>)"
        )

    @classmethod
    def from_stream(cls, stream: BytesLike, /, *, strict: bool = True) -> Self:
        """
        Instantiate a :class:`FLACCueSheetTrack` object from a
        bytes-like object.

        Parameters
        ----------
        stream : BytesLike; positional-only; optional
            Bytes-like object containing :code:`CUESHEET_TRACK` data.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the FLAC
            format specifications.

        Returns
        -------
        track : minim.media.flac.FLACCueSheetTrack
            :code:`CUESHEET_TRACK` data.

        Raises
        ------
        TypeError
            If `stream` is not a bytes-like object.

        ValueError
            If `stream` contains invalid :code:`CUESHEET_TRACK` or
            :code:`CUESHEET_TRACK_INDEX` data.
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
        if strict and (flags & 0x3F or reserved != 13 * b"\x00"):
            raise ValueError(
                "Non-zero bits found in reserved section of "
                "CUESHEET_TRACK data."
            )

        _from_unpack = FLACCueSheetTrackIndex._from_unpack
        indices = tuple(
            _from_unpack(data, strict=strict)
            for data in FLACCueSheetTrackIndex._STRUCT.iter_unpack(
                stream[36 : 36 + 12 * num_indices]
            )
        )
        cls._validate_indices(indices, custom=False, strict=strict)

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
        indices: tuple[FLACCueSheetTrackIndex, ...],
        /,
        *,
        custom: bool = True,
        strict: bool = True,
    ) -> None:
        """
        Validate track indices (:code:`CUESHEET_TRACK_INDEX`) in a
        cue sheet track (:code:`CUESHEET_TRACK`).

        Parameters
        ----------
        indices : tuple[minim.media.flac.FLACCueSheetTrackIndex, ...]; \
        positional-only
            Track indices.

        custom : bool; keyword-only; default: :code:`True`
            Whether the track indices are user-defined and should have
            their types validated.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the FLAC
            format specifications.

        Raises
        ------
        TypeError
            If any of `indices` are not :class:`FLACCueSheetTrackIndex`
            objects.

        ValueError
            If `tracks` contain :class:`FLACCueSheetTrackIndex` objects
            with indices that are non-sequential or out of order.
        """
        if strict:
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
        elif custom:
            for index_idx, index in enumerate(indices):
                validate_type(
                    f"indices[{index_idx}]", index, FLACCueSheetTrackIndex
                )

    @property
    def _length(self) -> int:
        """
        Length of the encoded :code:`CUESHEET_TRACK` data, in bytes.
        """
        return 36 + 12 * len(self.indices)

    def serialize(self) -> bytes:
        """
        Serialize the :code:`CUESHEET_TRACK` data to a bytestream.

        Returns
        -------
        stream : bytes
            Bytestream containing the :code:`CUESHEET_TRACK` data.
        """
        return self._STRUCT.pack(
            self.sample_offset,
            self.number,
            self.isrc.encode(encoding="utf-8") if self.isrc else 12 * b"\x00",
            (self.is_audio << 7) | (self.has_pre_emphasis << 6),
            13 * b"\x00",
            len(self.indices),
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

    Raises
    ------
    TypeError
        If `sample_offset` or `number` are not integers.

    ValueError
        If `sample_offset` or `number` are not zero or positive.
    """

    _STRUCT: ClassVar[struct.Struct] = struct.Struct(">QB3s")

    __slots__ = ()

    #: :bdg-primary:`get` :bdg-secondary-line:`set` :code:`self[0]` –
    #: Sample offset of the index point relative to the track offset.
    sample_offset: int
    #: :bdg-primary:`get` :bdg-secondary-line:`set` :code:`self[1]` –
    #: Track index number.
    number: int

    def __new__(cls, sample_offset: int, number: int) -> Self:
        validate_number("sample_offset", sample_offset, int, 0)
        validate_number("number", number, int, 0)
        return tuple.__new__(cls, (sample_offset, number))

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(sample_offset={self.sample_offset}, "
            f"number={self.number})"
        )

    @classmethod
    def _from_unpack(
        cls, data: tuple[int, int, bytes], /, *, strict: bool = True
    ) -> Self:
        """
        Instantiate a :class:`FLACCueSheetTrackIndex` object using data
        unpacked from a bytes-like object.

        Parameters
        ----------
        data : tuple[int, int, bytes]; positional-only
            Unpacked :class:`FLACCueSheetTrackIndex` data.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the FLAC
            format specifications.

        Returns
        -------
        track_index : minim.media.flac.FLACCueSheetTrackIndex
            :code:`CUESHEET_TRACK_INDEX` data.

        Raises
        ------
        ValueError
            If `data` contains non-zero bits in the reserved section of
            CUESHEET_TRACK_INDEX data.
        """
        if strict and data[2] != 3 * b"\x00":
            raise ValueError(
                "Non-zero bits found in reserved section of "
                "CUESHEET_TRACK_INDEX data."
            )

        return tuple.__new__(cls, data[:2])

    @classmethod
    def from_stream(cls, stream: BytesLike, /, *, strict: bool = True) -> Self:
        """
        Instantiate a :class:`FLACCueSheetTrackIndex` object from a
        bytes-like object.

        Parameters
        ----------
        stream : BytesLike; positional-only; optional
            Bytes-like object containing :code:`CUESHEET_TRACK_INDEX`
            data.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the FLAC
            format specifications.

        Returns
        -------
        track_index : minim.media.flac.FLACCueSheetTrackIndex
            :code:`CUESHEET_TRACK_INDEX` data.

        Raises
        ------
        TypeError
            If `stream` is not a bytes-like object.

        ValueError
            If `stream` contains non-zero bits in the reserved section
            of CUESHEET_TRACK_INDEX data.
        """
        *data, reserved = cls._STRUCT.unpack_from(as_buffer(stream))
        if strict and reserved != 3 * b"\x00":
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
        stream : bytes
            Bytestream containing the :code:`CUESHEET_TRACK_INDEX` data.
        """
        return self._STRUCT.pack(*self, 3 * b"\x00")


@dataclass(frozen=True, init=False, repr=False, slots=True)
class FLACPicture(FLACMetadataBlock, ID3v2APICFrame):
    """
    FLAC :code:`PICTURE` metadata block.
    """

    _STRUCT_II: ClassVar[struct.Struct] = struct.Struct(">II")
    _STRUCT_IIIII: ClassVar[struct.Struct] = struct.Struct(">5I")
    _frame_ids: ClassVar[dict[int, bytes]] = {}
    _block_type: ClassVar[int] = 6

    #: :bdg-primary:`get` :bdg-secondary-line:`set` Image width, in
    #: pixels.
    width: int = 0
    #: :bdg-primary:`get` :bdg-secondary-line:`set` Image height, in
    #: pixels.
    height: int = 0
    #: :bdg-primary:`get` :bdg-secondary-line:`set` Color depth, in
    #: bits per pixel.
    color_depth: int = 0
    #: :bdg-primary:`get` :bdg-secondary-line:`set` Number of indexed
    #: colors.
    num_indexed_colors: int = 0

    def __init__(
        self,
        *,
        picture_type: int,
        mime_type: str,
        picture_data: bytes,
        description: str = "",
        text_encoding: str = "utf-16",
        flags: ID3v2FrameFlags | None = None,
        group_id: int | None = None,
        width: int = 0,
        height: int = 0,
        color_depth: int = 0,
        num_indexed_colors: int = 0,
    ) -> None:
        """
        Parameters
        ----------
        picture_type : int; keyword-only
            Picture type.

        mime_type : str; keyword-only
            MIME type.

            **Examples**: :code:`"image/jpeg"`, :code:`"image/png"`,
            :code:`"-->"`.

        picture_data : bytes; keyword-only
            Picture data.

        description : str; keyword-only; default: :code:`""`
            Picture description.

        text_encoding : str; keyword-only; default: :code:`"utf-16"`
            Text encoding for the picture description.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        flags : minim.media.metadata.ID3v2FrameFlags; keyword-only; \
        optional
            Flags for the ID3v2 frame.

        group_id : int; keyword-only; optional
            Group identifier.

            **Valid range**: :code:`0` to :code:`255`.

        width : int; keyword-only; default: :code:`0`
            Image width, in pixels. Use :code:`0` if unknown.

        height : int; keyword-only; default: :code:`0`
            Image height, in pixels. Use :code:`0` if unknown.

        color_depth : int; keyword-only; default: :code:`0`
            Color depth, in bits per pixel. Use :code:`0` if unknown.

        num_indexed_colors : int; keyword-only; default: :code:`0`
            Number of indexed colors. Use :code:`0` if unknown or not
            applicable.

        Raises
        ------
        TypeError
            If any of the arguments are not of the correct type.

        ValueError
            If any of the numeric arguments are outside their allowed
            ranges.
        """
        if flags is None:
            set_obj_attr(self, "_flags", ID3v2FrameFlags())
            set_obj_attr(self, "_group_id", None)
        else:
            validate_type("flags", flags, ID3v2FrameFlags)
            set_obj_attr(self, "_flags", flags)
            if flags._has_group_id:
                validate_number("group_id", group_id, int, 0, 255)
            elif group_id is not None:
                raise ValueError(
                    "A grouping identifier was specified, but the "
                    "ID3v2 frame flags do not indicate grouping."
                )
            set_obj_attr(self, "_group_id", group_id)

        validate_number("picture_type", picture_type, int, 0, 20)
        set_obj_attr(self, "_picture_type", picture_type)

        validate_type("mime_type", mime_type, str)
        mime_type = mime_type.lower()
        if not ASCII_CHARS_REGEX.match(mime_type):
            raise ValueError(
                "`mime_type` must contain only ASCII characters 0x20 "
                "(' ') through 0x7D ('}')."
            )
        set_obj_attr(self, "_mime_type", mime_type)

        validate_type("picture_data", picture_data, bytes)
        set_obj_attr(self, "_picture_data", picture_data)

        validate_type("description", description, str)
        set_obj_attr(self, "_description", description)

        validate_type("text_encoding", text_encoding, str)
        text_encoding = text_encoding.lower()
        if text_encoding not in self._TEXT_ENCODINGS.values():
            raise ValueError(
                f"Invalid text encoding {text_encoding!r}. Valid "
                f"values: {join_values(self._TEXT_ENCODINGS.values())}."
            )
        if text_encoding == "iso-8859-1":
            try:
                description.encode(encoding=text_encoding)
                is_utf = False
            except UnicodeEncodeError:
                is_utf = True
            if is_utf:
                raise ValueError(
                    "`picture_description` cannot be encoded using ISO-8859-1."
                )
        set_obj_attr(self, "_text_encoding", text_encoding)

        validate_number("width", width, int, 0)
        set_obj_attr(self, "width", width)
        validate_number("height", height, int, 0)
        set_obj_attr(self, "height", height)
        validate_number("color_depth", color_depth, int, 0)
        set_obj_attr(self, "color_depth", color_depth)
        validate_number("num_indexed_colors", num_indexed_colors, int, 0)
        set_obj_attr(self, "num_indexed_colors", num_indexed_colors)

    def __repr__(self) -> str:
        optional_kwargs = [""]
        if self.width:
            optional_kwargs.append(f"width={self.width}")
        if self.height:
            optional_kwargs.append(f"height={self.height}")
        if self.color_depth:
            optional_kwargs.append(f"color_depth={self.color_depth}")
        if self.num_indexed_colors:
            optional_kwargs.append(
                f"num_indexed_colors={self.num_indexed_colors}"
            )
        return (
            f"{type(self).__name__}(picture_type={self._picture_type!r}, "
            f"mime_type={self._mime_type!r}, "
            f"picture_data=<{len(self._picture_data)} byte(s)>, "
            f"description={self._description!r}, "
            f"text_encoding={self._text_encoding!r}, "
            f"flags={self._flags!r}, group_id={self._group_id}"
            f"{', '.join(optional_kwargs)})"
        )

    @classmethod
    def from_stream(cls, stream: BytesLike, /) -> Self:
        """
        Instantiate an :class:`FLACPicture` object from a bytes-like
        object.

        Parameters
        ----------
        stream : BytesLike; positional-only; optional
            Bytes-like object containing :code:`PICTURE` metadata block
            data.

        Returns
        -------
        picture : minim.media.flac.FLACPicture
            FLAC :code:`PICTURE` metadata block.

        Raises
        ------
        TypeError
            If `stream` is not a bytes-like object.

        ValueError
            If `stream` contains an invalid :code:`PICTURE` block.
        """
        picture_type, mime_type_length = cls._STRUCT_II.unpack_from(stream)
        validate_number("picture_type", picture_type, int, 0, 20)

        offset = 8 + mime_type_length
        mime_type = stream[8:offset].tobytes().decode(encoding="ascii")

        end_offset = offset + 4
        description_length = int.from_bytes(stream[offset:end_offset])
        offset = end_offset
        end_offset = offset + description_length
        description = (
            stream[offset:end_offset].tobytes().decode(encoding="utf-8")
        )

        offset = end_offset
        width, height, color_depth, num_indexed_colors, data_length = (
            cls._STRUCT_IIIII.unpack_from(stream, offset)
        )
        offset += 20

        obj = cls.__new__(cls)
        set_obj_attr(obj, "_picture_type", picture_type)
        set_obj_attr(obj, "_mime_type", mime_type)
        set_obj_attr(
            obj,
            "_picture_data",
            stream[offset : offset + data_length].tobytes(),
        )
        set_obj_attr(obj, "_description", description)
        set_obj_attr(obj, "_text_encoding", "utf-16")
        set_obj_attr(obj, "_flags", ID3v2FrameFlags())
        set_obj_attr(obj, "_group_id", None)
        set_obj_attr(obj, "width", width)
        set_obj_attr(obj, "height", height)
        set_obj_attr(obj, "color_depth", color_depth)
        set_obj_attr(obj, "num_indexed_colors", num_indexed_colors)
        return obj

    @property
    def _block_data_length(self) -> int:
        """
        Length of the encoded :code:`PICTURE` metadata block data, in
        bytes.
        """
        return (
            32
            + len(self._mime_type.encode(encoding="ascii"))
            + len(self._description.encode(encoding="utf-8"))
            + len(self._picture_data)
        )

    @property
    def text_encoding(self) -> str:
        """
        :bdg-primary:`get` :bdg-secondary-line:`set` Text encoding.
        """
        return self._text_encoding

    def serialize(self) -> bytes:
        """
        Serialize the :code:`PICTURE` metadata block data to a
        bytestream.

        Returns
        -------
        stream : bytes
            Bytestream containing the :code:`PICTURE` metadata block
            data.
        """
        mime_type = self._mime_type.encode(encoding="ascii")
        description = self._description.encode(encoding="utf-8")
        return b"".join(
            (
                self._STRUCT_II.pack(self._picture_type, len(mime_type)),
                mime_type,
                len(description).to_bytes(length=4, byteorder="big"),
                description,
                self._STRUCT_IIIII.pack(
                    self.width,
                    self.height,
                    self.color_depth,
                    self.num_indexed_colors,
                    len(self._picture_data),
                ),
                self._picture_data,
            )
        )


class UnknownFLACMetadataBlock(FLACMetadataBlock):
    """
    Unknown FLAC metadata block.
    """

    __slots__ = ("_block_data", "_block_type")

    def __init__(self, block_type: int, block_data: bytes | bytearray) -> None:
        """
        Parameters
        ----------
        block_type : int
            Metadata block type.

            **Valid range**: :code:`7` to :code:`126`.

        block_data : bytes or bytearray
            Metadata block data.

        Raises
        ------
        TypeError
            If `block_type` is not an integer or `block_data` is not a
            bytes-like object.

        ValueError
            If `block_type` is not a reserved FLAC metadata block type.
        """
        validate_number("block_type", block_type, int, 7, 126)
        set_obj_attr(self, "_block_type", block_type)
        validate_type("block_data", block_data, bytes | bytearray)
        set_obj_attr(self, "_block_data", bytes(block_data))

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(block_type={self._block_type}, "
            f"block_data=<{len(self._block_data)} byte(s)>)"
        )

    def __setattr__(self, name: str, value: Any) -> None:
        raise FrozenInstanceError(f"Cannot assign to field {name!r}.")

    def __delattr__(self, name: str) -> None:
        raise FrozenInstanceError(f"Cannot delete field {name!r}.")

    @classmethod
    def from_stream(
        cls, stream: BytesLike, /, block_type: int
    ) -> UnknownFLACMetadataBlock:
        """
        Instantiate a :class:`UnknownFLACMetadataBlock` object from a
        bytes-like object.

        Parameters
        ----------
        stream : BytesLike; positional-only; optional
            Bytes-like object containing the metadata block data.

        block_type : int
            Metadata block type.

            **Valid range**: :code:`7` to :code:`126`.

        Returns
        -------
        block : minim.media.flac.UnknownFLACMetadataBlock
            Metadata block.

        Raises
        ------
        TypeError
            If `stream` is not a bytes-like object or `block_type` is
            not an integer.

        ValueError
            If `block_type` is not a reserved FLAC metadata block type.
        """
        validate_type("stream", stream, BytesLike)
        validate_number("block_type", block_type, int, 7, 126)
        obj = cls.__new__(cls)
        set_obj_attr(obj, "_block_data", bytes(stream))
        set_obj_attr(obj, "_block_type", block_type)
        return obj

    @property
    def _block_data_length(self) -> int:
        """
        Length of the encoded metadata block data, in bytes.
        """
        return len(self._block_data)

    @property
    def block_data(self) -> bytes:
        """
        :bdg-primary:`get` :bdg-secondary-line:`set`
        Metadata block data.
        """
        return self._block_data

    def serialize(self) -> bytes:
        """
        Serialize the metadata block data to a bytestream.

        Returns
        -------
        stream : bytes
            Bytestream containing the metadata block data.
        """
        return self._block_data


class FLACMetadataView:
    """
    View of FLAC metadata blocks.

    .. important::

       This class is managed by :class:`FLACAudio` and should not be
       instantiated directly.

    This class implements the following special methods:

    * :code:`__getitem__` – Return the metadata block at an index.

    * :code:`__iter__` – Return an iterator of the metadata blocks.

    * :code:`__len__` – Return the number of metadata blocks.
    """

    __slots__ = ("_blocks", "_type_index")

    def __init__(
        self,
        blocks: list[FLACMetadataBlock | VorbisComment],
        /,
        *,
        type_index: dict[int, list[FLACMetadataBlock | VorbisComment]]
        | None = None,
    ) -> None:
        """
        Parameters
        ----------
        blocks : list[minim.media.flac.FLACMetadataBlock \
        | minim.media.metadata.VorbisComment]
            FLAC metadata blocks.

        type_index : dict[int, list[minim.media.flac.FLACMetadataBlock \
        | minim.media.metadata.VorbisComment]]; keyword-only; optional
            Mapping of FLAC metadata block types to lists of the
            corresponding metadata blocks.
        """
        self._blocks = blocks
        if type_index is None:
            self._type_index = defaultdict(list)
            for block in blocks:
                self._type_index[block._block_type].append(block)
        else:
            self._type_index = type_index

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(<{len(self._blocks)} metadata block(s)>)"
        )

    def __getitem__(self, index: int, /) -> FLACMetadataBlock | VorbisComment:
        return self._blocks[index]

    def __iter__(self) -> Iterator[FLACMetadataBlock | VorbisComment]:
        return iter(self._blocks)

    def __len__(self) -> int:
        return len(self._blocks)

    def get(
        self,
        block_types: int
        | type[FLACMetadataBlock | VorbisComment]
        | Collection[int | type[FLACMetadataBlock | VorbisComment]],
        /,
    ) -> (
        list[FLACMetadataBlock | VorbisComment]
        | dict[int, list[FLACMetadataBlock | VorbisComment]]
    ):
        """
        Get FLAC metadata blocks by type.

        .. important::

           It is *not* guaranteed that the metadata blocks are in the
           same order as they are found in the FLAC audio file,
           especially after metadata blocks have been added, moved, or
           removed.

        Parameters
        ----------
        block_types : int, type[minim.media.flac.FLACMetadataBlock \
        | minim.media.metadata.VorbisComment], or Collection[int \
        | type[minim.media.flac.FLACMetadataBlock \
        | minim.media.metadata.VorbisComment]]; positional-only
            Metadata block types.

            **Valid values**:

            * :code:`0` or :class:`FLACStreamInfo` – :code:`STREAMINFO`.
            * :code:`1` or :class:`FLACPadding` – :code:`PADDING`.
            * :code:`2` or :class:`FLACApplication` – :code:`APPLICATION`.
            * :code:`3` or :class:`FLACSeekTable` – :code:`SEEKTABLE`.
            * :code:`4` or :class:`~minim.media.metadata.VorbisComment` –
              :code:`VORBIS_COMMENT`.
            * :code:`5` or :class:`FLACCueSheet` – :code:`CUESHEET`.
            * :code:`6` or :class:`FLACPicture` – :code:`PICTURE`.

        Returns
        -------
        blocks : list[minim.media.flac.FLACMetadataBlock \
        | minim.media.metadata.VorbisComment] or dict[int, \
        list[minim.media.flac.FLACMetadataBlock \
        | minim.media.metadata.VorbisComment]]
            Metadata blocks. If `block_types` is a collection, a
            dictionary mapping the metadata block types to the metadata
            blocks is returned.
        """
        if isinstance(block_types, int):
            block_types = {block_types}
        elif issubclass(block_types, FLACMetadataBlock | VorbisComment):
            block_types = {block_types._block_type}
        elif isinstance(block_types, COLLECTION_TYPES):
            block_types = {
                block_type
                if isinstance(block_type, int)
                else block_type._block_type
                for block_type in block_types
            }
        if len(block_types) == 1:
            return self._type_index[block_types.pop()] or None
        return {
            block_type: self._type_index[block_type] or None
            for block_type in block_types
        }


class FLACAudio(Audio):
    """
    FLAC audio file.
    """

    __slots__ = ("_audio_offset", "_metadata_view", "_type_index")

    @property
    def metadata(self) -> FLACMetadataView:
        """
        :bdg-primary:`get` :bdg-secondary-line:`set` Metadata blocks.
        """
        return self._metadata_view

    def _merge_adjacent_padding(self) -> None:
        """
        Merge adjacent :code:`PADDING` metadata blocks, reclaiming
        redundant four-byte headers.
        """
        blocks = self._metadata[:1]
        type_index = self._type_index
        for block in self._metadata[1:]:
            prev_block = blocks[-1]
            if prev_block._block_type == block._block_type == 1:
                prev_block.adjust_length(4 + block._block_data_length)
                type_index[block._block_type].remove(block)
            else:
                blocks.append(block)
        self._metadata = self._metadata_view._blocks = blocks

    def load_metadata(self) -> None:
        """
        Load metadata blocks from the FLAC audio file.

        .. note::

           If multiple Vorbis comments are found, they are merged into a
           single Vorbis comment, with field values concatenated in
           container order and the vendor name from the last occurrence
           retained.
        """
        self.open()
        file_path = self._file_path
        view = self._view

        offset = 4
        if view[:offset] != b"fLaC":
            raise ValueError(f"{file_path} is not a valid FLAC file.")

        self._metadata = blocks = []
        self._type_index = type_index = defaultdict(list)
        self._tags = None
        strict = self._strict
        seen_vorbis_comment = False
        block_header = 0x7F
        while not block_header & 0x80:
            block_header = view[offset]
            offset += 1

            end_offset = offset + 3
            block_data_length = int.from_bytes(
                view[offset:end_offset], byteorder="big"
            )
            offset = end_offset

            end_offset = offset + block_data_length
            block_data = view[offset:end_offset]
            offset = end_offset

            match block_type := block_header & 0x7F:
                case 0:  # STREAMINFO
                    if blocks:
                        raise RuntimeError(
                            "STREAMINFO block is not the first "
                            "metadata block or appears multiple times "
                            f"in '{file_path}'."
                        )

                    if block_data_length != 34:
                        raise RuntimeError(
                            "STREAMINFO block data does not have length 34."
                        )

                    self._stream_info = block = FLACStreamInfo.from_stream(
                        block_data, strict=strict
                    )
                case 1:  # PADDING
                    if blocks and (prev_block := blocks[-1])._block_type == 1:
                        if strict and any(block_data):
                            raise ValueError(
                                "Non-zero bits found in PADDING block."
                            )
                        prev_block.adjust_length(4 + block_data_length)
                        continue
                    else:
                        block = FLACPadding.from_stream(
                            block_data, strict=strict
                        )
                case 2:  # APPLICATION
                    block = FLACApplication.from_stream(block_data)
                case 3:  # SEEKTABLE
                    block = FLACSeekTable.from_stream(
                        block_data, strict=strict
                    )
                case 4:  # VORBIS_COMMENT
                    if strict and seen_vorbis_comment:
                        raise RuntimeError(
                            "VORBIS_COMMENT block appears multiple "
                            f"times in '{file_path}'."
                        )

                    block = VorbisComment.from_stream(block_data)
                    if seen_vorbis_comment:
                        self._tags |= block
                        continue
                    else:
                        seen_vorbis_comment = True
                        self._tags = block
                case 5:  # CUESHEET
                    block = FLACCueSheet.from_stream(block_data, strict=strict)
                case 6:  # PICTURE
                    block = FLACPicture.from_stream(block_data)
                case 127:  # INVALID
                    raise ValueError(
                        "Metadata block with invalid block type found "
                        f"in '{file_path}'."
                    )
                case _:  # RESERVED
                    msg = (
                        "Metadata block with reserved block type "
                        f"{block_type} found in '{file_path}'."
                    )
                    if strict:
                        raise ValueError(msg)

                    warnings.warn(msg)
                    block = UnknownFLACMetadataBlock.from_stream(
                        block_data, block_type=block_type
                    )
            blocks.append(block)
            type_index[block_type].append(block)

        block_data = None
        self.close()

        if not blocks or blocks[0]._block_type != 0:
            raise RuntimeError(
                f"STREAMINFO block was not found in '{file_path}'."
            )

        self._audio_offset = offset
        self._metadata_view = FLACMetadataView(
            self._metadata, type_index=self._type_index
        )

    def add_metadata(
        self,
        metadata: FLACMetadataBlock
        | VorbisComment
        | OrderedCollection[FLACMetadataBlock | VorbisComment],
        /,
        *,
        index: int | None = None,
    ) -> None:
        """
        Add FLAC metadata blocks.

        Parameters
        ----------
        metadata : minim.media.flac.FLACMetadataBlock, \
        minim.media.metadata.VorbisComment, or \
        OrderedCollection[minim.media.flac.FLACMetadataBlock \
        | minim.media.metadata.VorbisComment]; positional-only
            Metadata blocks to add.

            .. note::

               Adjacent :code:`PADDING` metadata blocks are always
               merged, with the redundant four-byte headers reclaimed.

        index : int; keyword-only; optional
            Index at which to insert the new metadata blocks. If
            :code:`None`, existing :code:`PADDING` metadata blocks of
            sufficient size are overwritten to avoid file restructuring.
            If no suitable :code:`PADDING` metadata blocks are
            available, the new data is appended to the end of the
            existing metadata blocks.
        """
        if not isinstance(metadata, ORDERED_COLLECTION_TYPES):
            metadata = [metadata]

        for block in metadata:
            if not isinstance(block, FLACMetadataBlock | VorbisComment):
                raise TypeError(
                    "`metadata` must be a FLAC metadata block instance "
                    "or an ordered collection of FLAC metadata block "
                    "instances."
                )

            if not block._block_type:
                raise ValueError(
                    "STREAMINFO metadata blocks cannot be added, "
                    "moved, or removed."
                )

        blocks = self._metadata
        num_blocks = len(blocks)
        if index is not None:
            if index < 0:
                index += num_blocks
            if not 0 <= index <= num_blocks:
                raise ValueError(
                    f"Metadata block index {index} is out of range."
                )

        type_index = self._type_index
        for new_block in metadata:
            placed_idx = None
            is_padding = new_block._block_type == 1

            # Try to insert new non-PADDING blocks inside existing
            # PADDING blocks if a target index was not specified
            if index is None and not is_padding:
                for idx, block in enumerate(blocks):
                    if block._block_type == 1:
                        if (
                            block._block_data_length
                            == new_block._block_data_length
                        ):
                            blocks[idx] = new_block
                            type_index[1].remove(block)
                            placed_idx = idx
                            break
                        elif block._block_data_length >= (
                            new_block_length := 4
                            + new_block._block_data_length
                        ):
                            block.adjust_length(-new_block_length)
                            blocks.insert(idx, new_block)
                            placed_idx = idx
                            num_blocks += 1
                            break

            # Add new block at the user-specified index or at the end if
            # no suitable PADDING block was found for it
            if placed_idx is None:
                placed_idx = num_blocks if index is None else index
                blocks.insert(placed_idx, new_block)
                num_blocks += 1
                if index is not None:
                    index += 1

            # If the new block is PADDING, check adjacent blocks to
            # merge
            if is_padding:
                if (adj_idx := placed_idx + 1) < num_blocks and blocks[
                    adj_idx
                ]._block_type == 1:  # right
                    block = blocks.pop(adj_idx)
                    new_block.adjust_length(4 + block._block_data_length)
                    type_index[1].remove(block)
                    num_blocks -= 1
                if (adj_idx := placed_idx - 1) >= 0 and blocks[
                    adj_idx
                ]._block_type == 1:  # left
                    block = blocks.pop(adj_idx)
                    new_block.adjust_length(4 + block._block_data_length)
                    type_index[1].remove(block)
                    num_blocks -= 1
                    if index is not None:
                        index -= 1
            type_index[new_block._block_type].append(new_block)

    def move_metadata(
        self,
        *,
        to_index: int,
        indices: int | OrderedCollection[int] | None = None,
        block_types: int
        | type[FLACMetadataBlock | VorbisComment]
        | Collection[int | type[FLACMetadataBlock | VorbisComment]]
        | None = None,
    ) -> None:
        """
        Move FLAC metadata blocks.

        .. note::

           Adjacent :code:`PADDING` metadata blocks are always merged,
           with the redundant four-byte headers reclaimed.

        .. important::

           Exactly one of `indices` or `block_types` must be provided.

        Parameters
        ----------
        to_index : int; keyword-only
            Index to move metadata blocks to. Use
            :code:`len(self.metadata)` to append metadata blocks to the
            end.

        indices : int or Collection[int]; keyword-only; optional
            Indices of metadata blocks to move.

        block_types : int, type[minim.media.flac.FLACMetadataBlock \
        | minim.media.metadata.VorbisComment], or Collection[int \
        | type[minim.media.flac.FLACMetadataBlock \
        | minim.media.metadata.VorbisComment]]; keyword-only; optional
            Types of metadata blocks to move.

            **Valid values**:

            * :code:`1` or :class:`FLACPadding` – :code:`PADDING`.
            * :code:`2` or :class:`FLACApplication` – :code:`APPLICATION`.
            * :code:`3` or :class:`FLACSeekTable` – :code:`SEEKTABLE`.
            * :code:`4` or :class:`~minim.media.metadata.VorbisComment` –
              :code:`VORBIS_COMMENT`.
            * :code:`5` or :class:`FLACCueSheet` – :code:`CUESHEET`.
            * :code:`6` or :class:`FLACPicture` – :code:`PICTURE`.
        """
        has_indices = indices is not None
        has_types = block_types is not None
        if has_indices == has_types:
            raise ValueError(
                "Exactly one of `indices` or `block_types` must be specified."
            )

        blocks = self._metadata
        num_blocks = len(blocks)
        max_block_index = num_blocks - 1
        validate_number("to_index", to_index, int, -num_blocks, num_blocks)
        if to_index < num_blocks:
            to_index %= num_blocks
        if not to_index:
            raise ValueError(
                "Metadata blocks cannot be moved to the first "
                "position, which is reserved for the STREAMINFO block."
            )

        if has_indices:
            validate_type("indices", indices, int | ORDERED_COLLECTION_TYPES)
            if isinstance(indices, int):
                indices = [indices]
            seen_block_indices = set()
            block_indices = []
            for idx, block_index in enumerate(indices):
                validate_number(
                    f"indices[{idx}]",
                    block_index,
                    int,
                    -num_blocks,
                    max_block_index,
                )
                block_index %= num_blocks
                if block_index == 0:
                    raise ValueError(
                        "STREAMINFO metadata blocks cannot be "
                        "added, moved, or removed."
                    )

                if block_index in seen_block_indices:
                    raise ValueError(
                        "Duplicate metadata block index "
                        f"{block_index} encountered."
                    )

                seen_block_indices.add(block_index)
                block_indices.append(block_index)
        else:
            if isinstance(block_types, int):
                block_types = {block_types}
            elif issubclass(block_types, FLACMetadataBlock | VorbisComment):
                block_types = {block_types._block_type}
            elif isinstance(block_types, COLLECTION_TYPES):
                block_types = {
                    block_type
                    if isinstance(block_type, int)
                    else block_type._block_type
                    for block_type in block_types
                }
            else:
                raise TypeError(
                    "`block_types` must be an integer, a subclass of "
                    "FLACMetadataBlock, or collection of integers and "
                    "classes."
                )
            if 0 in block_types:
                raise ValueError(
                    "STREAMINFO metadata blocks cannot be added, "
                    "moved, or removed."
                )

            block_indices = [
                block_index
                for block_index, block in enumerate(blocks)
                if block._block_type in block_types
            ]

        if (
            not block_indices
            or len(block_indices) == 1
            and block_indices[0] == to_index
        ):
            return

        moved_blocks = [
            blocks[block_index] for block_index in reversed(block_indices)
        ]
        for block_index in sorted(block_indices, reverse=True):
            del blocks[block_index]
            if block_index < to_index:
                to_index -= 1

        for block in moved_blocks:
            blocks.insert(to_index, block)
        self._merge_adjacent_padding()

    def optimize_padding(self) -> None:
        """
        Consolidate all :code:`PADDING` metadata blocks into a single
        one at the end of the FLAC metadata stream, reclaiming redundant
        four-byte headers.
        """
        blocks = []
        padding_length = -4
        has_padding = False

        for block in self._metadata:
            if block._block_type == 1:
                padding_length += 4 + block._block_data_length
                has_padding = True
            else:
                blocks.append(block)

        if not has_padding:
            return

        padding = FLACPadding(padding_length)
        blocks.append(padding)
        self._metadata = self._metadata_view._blocks = blocks
        self._type_index[1] = [padding]

    def remove_metadata(
        self,
        *,
        indices: int | Collection[int] | None = None,
        block_types: int
        | type[FLACMetadataBlock | VorbisComment]
        | Collection[int | type[FLACMetadataBlock | VorbisComment]]
        | None = None,
    ) -> None:
        """
        Remove FLAC metadata blocks.

        .. note::

           To minimize disk I/O overhead, removed metadata blocks are
           transparently replaced with :code:`PADDING` metadata blocks
           of equivalent length. This preserves the existing file
           offsets and avoids a full rewrite of the audio stream. To
           reclaim disk space by stripping all :code:`PADDING` metadata
           blocks, specify :code:`remove_padding=True` when invoking
           :meth:`save_metadata`.

           Adjacent :code:`PADDING` metadata blocks are always merged,
           with the redundant four-byte headers reclaimed.

        .. important::

           Exactly one of `indices` or `block_types` must be provided.

        Parameters
        ----------
        indices : int or Collection[int]; keyword-only; optional
            Indices of metadata blocks to remove.

        block_types : int, type[minim.media.flac.FLACMetadataBlock \
        | minim.media.metadata.VorbisComment], or Collection[int \
        | type[minim.media.flac.FLACMetadataBlock \
        | minim.media.metadata.VorbisComment]]; keyword-only; optional
            Types of metadata blocks to remove.

            **Valid values**:

            * :code:`2` or :class:`FLACApplication` – :code:`APPLICATION`.
            * :code:`3` or :class:`FLACSeekTable` – :code:`SEEKTABLE`.
            * :code:`4` or :class:`~minim.media.metadata.VorbisComment` –
              :code:`VORBIS_COMMENT`.
            * :code:`5` or :class:`FLACCueSheet` – :code:`CUESHEET`.
            * :code:`6` or :class:`FLACPicture` – :code:`PICTURE`.
        """
        has_indices = indices is not None
        has_types = block_types is not None
        if has_indices == has_types:
            raise ValueError(
                "Exactly one of `indices` or `block_types` must be specified."
            )

        blocks = self._metadata
        type_index = self._type_index
        if has_indices:
            num_blocks = len(blocks)
            max_block_index = num_blocks - 1
            validate_type("indices", indices, int | COLLECTION_TYPES)
            if isinstance(indices, int):
                validate_range(
                    "indices", indices, -num_blocks, max_block_index
                )
                indices %= num_blocks
                if not indices:
                    raise ValueError(
                        "STREAMINFO metadata blocks cannot be added, "
                        "moved, or removed."
                    )

                block = blocks[indices]
                blocks[indices] = FLACPadding(block._block_data_length)
                type_index[block._block_type].remove(block)
            else:
                for idx, block_index in enumerate(indices):
                    validate_number(
                        f"indices[{idx}]",
                        block_index,
                        int,
                        -num_blocks,
                        max_block_index,
                    )
                    block_index %= num_blocks
                    if not block_index:
                        raise ValueError(
                            "STREAMINFO metadata blocks cannot be "
                            "added, moved, or removed."
                        )

                    block = blocks[block_index]
                    blocks[block_index] = FLACPadding(block._block_data_length)
                    type_index[block._block_type].remove(block)
        else:
            if isinstance(block_types, int):
                block_types = {block_types}
            elif issubclass(block_types, FLACMetadataBlock | VorbisComment):
                block_types = {block_types._block_type}
            elif isinstance(block_types, COLLECTION_TYPES):
                block_types = {
                    block_type
                    if isinstance(block_type, int)
                    else block_type._block_type
                    for block_type in block_types
                }
            else:
                raise TypeError(
                    "`block_types` must be an integer, a subclass of "
                    "FLACMetadataBlock, or collection of integers and "
                    "classes."
                )
            block_types.discard(1)
            if 0 in block_types:
                raise ValueError(
                    "STREAMINFO metadata blocks cannot be added, "
                    "moved, or removed."
                )

            for block_index, block in enumerate(blocks):
                if block._block_type in block_types:
                    blocks[block_index] = FLACPadding(block._block_data_length)
                    type_index[block._block_type].remove(block)

        self._merge_adjacent_padding()

    def save(
        self,
        file_path: PathLike | None = None,
        /,
        *,
        include_padding: bool = True,
    ) -> None:
        """
        Write changes to disk.

        Parameters
        ----------
        file_path : PathLike; positional-only
            Path to or name of the FLAC audio file. If not specified,
            changes are written back to the source file.

        include_padding : bool; keyword-only; default: :code:`True`
            Whether to keep all :code:`PADDING` metadata blocks.
        """
        blocks = (
            self._metadata
            if include_padding
            else [block for block in self._metadata if block._block_type != 1]
        )
        metadata_length = 4 + sum(
            4 + block._block_data_length for block in blocks
        )

        last_block_index = len(blocks) - 1
        serialized_blocks = (
            (
                ((block_index == last_block_index) << 7) | block._block_type
            ).to_bytes(1, byteorder="big")
            + block._block_data_length.to_bytes(length=3, byteorder="big")
            + block.serialize()
            for block_index, block in enumerate(blocks)
        )
        if file_path is None and metadata_length == self._audio_offset:
            with open(self._file_path, "r+b") as f:
                f.seek(4)
                f.write(b"".join(serialized_blocks))
        else:
            serialized_blocks = [b"fLaC", *serialized_blocks]
            with open(self._file_path, "rb") as f:
                f.seek(self._audio_offset)
                serialized_blocks.append(f.read())
            with open(file_path or self._file_path, "wb") as f:
                f.write(b"".join(serialized_blocks))
