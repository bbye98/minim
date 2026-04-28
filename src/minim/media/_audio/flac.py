from __future__ import annotations
from dataclasses import dataclass
import re
import string
import struct
from typing import TYPE_CHECKING
import warnings

from ..._utility import prepare_isrc, validate_number, validate_type
from .._shared import as_buffer
from ..metadata import VorbisComment
from ._shared import AudioStreamInfo, Audio

if TYPE_CHECKING:
    from ..._types import BytesLike


_obj_set_attr = object.__setattr__


@dataclass(frozen=True, slots=True)
class FLACMetadataBlock:
    """
    FLAC metadata block.
    """

    type: int | None = None
    size: int | None = None
    data: (
        FLACApplication
        | FLACSeekTable
        | FLACCueSheet
        | FLACStreamInfo
        | VorbisComment
        | None
    ) = None

    def __post_init__(self) -> None:
        if (type_ := self.type) is None:
            ...  # TODO
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

                    if self.size is None:
                        self.size = 34
                    elif self.size != 34:
                        raise ValueError(
                            "STREAMINFO block size must be 34, not "
                            f"{self.size}."
                        )
                case 1:  # PADDING
                    validate_number("size", self.size, int, 0)
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

                    actual_size = 4 + len(app["app_data"])
                    if self.size is None:
                        self.size = actual_size
                    elif self.size != actual_size:
                        raise ValueError(
                            "APPLICATION block size does not match the "
                            "size of the block data."
                        )
                case 3:  # SEEKTABLE
                    if not isinstance(self.data, FLACSeekTable):
                        raise TypeError(
                            "SEEKTABLE block data must be an instance "
                            "of FLACSeekTable, not "
                            f"{type(self.data).__name__}."
                        )

                    actual_size = 18 * len(self.data.seek_points)
                    if self.size is None:
                        self.size = actual_size
                    elif self.size != actual_size:
                        raise ValueError(
                            "SEEKTABLE block size does not match the "
                            "size of the block data."
                        )

                case 4:  # VORBIS_COMMENT
                    if not isinstance(self.data, VorbisComment):
                        raise TypeError(
                            "VORBIS_COMMENT block data must be an "
                            "instance of VorbisComment, not "
                            f"{type(self.data).__name__}."
                        )

                    actual_size = len(self.data.serialize())
                    if self.size is None:
                        self.size = actual_size
                    elif self.size != actual_size:
                        raise ValueError(
                            "VORBIS_COMMENT block size does not match "
                            "the size of the block data."
                        )
                case 5:  # CUESHEET
                    if not isinstance(self.data, FLACCueSheet):
                        raise TypeError(
                            "CUESHEET block data must be an instance "
                            "of FLACCueSheet, not "
                            f"{type(self.data).__name__}."
                        )

                    actual_size = len(self.data.serialize())
                    if self.size is None:
                        self.size = actual_size
                    elif self.size != actual_size:
                        raise ValueError(
                            "CUESHEET block size does not match the "
                            "size of the block data."
                        )
                case 6:  # PICTURE
                    pass  # TODO

    @classmethod
    def from_stream(
        cls, stream: BytesLike, /, type_: int, size: int | None = None
    ) -> FLACMetadataBlock:
        """ """
        obj = cls.__new__(cls)
        validate_number("type", type_, int, 0, 6)
        _obj_set_attr(obj, "type", type_)

        stream = as_buffer(stream)
        if size is None:
            size = len(stream)
        _obj_set_attr(obj, "size", size)

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
                pass
        _obj_set_attr(obj, "data", data)

        return obj

    def serialize(self) -> bytes:
        """
        Serialize only the metadata block data to a bytestream. The
        metadata block header should be prefixed by the calling scope
        since this class does not know whether the metadata block is the
        last metadata block before the audio data.
        """
        match self.type:
            case 1:  # PADDING
                return bytes(self.size)
            case 6:  # PICTURE
                pass  # TODO
            case _:
                return self.data.serialize()


@dataclass(frozen=True, slots=True)
class FLACStreamInfo(AudioStreamInfo):
    """
    FLAC :code:`STREAMINFO` metadata block data.

    Parameters
    ----------
    min_block_size : int
        Minimum block size in samples.

        **Valid range**: :code:`16` to :code:`65_535`.

    max_block_size : int
        Maximum block size in samples.

        **Valid range**: :code:`16` to :code:`65_535`.

    min_frame_size : int
        Minimum frame size in bytes.

        **Minimum value**: :code:`0` to :code:`16_777_215`.

    max_frame_size : int
        Maximum frame size in bytes.

        **Maximum value**: :code:`0` to :code:`16_777_215`.

    md5 : str
        MD5 hash of the unencoded audio data.
    """

    _HEX_DIGITS = set(string.hexdigits)
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
        max_frame_size = int.from_bytes(stream[4:10], byteorder="big")
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

        num_samples = ((stream[13] & 0x0F) << 32) + int.from_bytes(
            stream[14:18], byteorder="big"
        )

        md5 = stream[18:].hex()
        if len(md5) != 32 or not all(c in cls._HEX_DIGITS for c in md5):
            raise ValueError(
                "`md5` must be a 32-character hexadecimal string."
            )

        obj = cls.__new__(cls)
        _obj_set_attr(obj, "min_block_size", min_block_size)
        _obj_set_attr(obj, "max_block_size", max_block_size)
        _obj_set_attr(obj, "min_frame_size", min_frame_size)
        _obj_set_attr(obj, "max_frame_size", max_frame_size)
        _obj_set_attr(obj, "sample_rate", sample_rate)
        _obj_set_attr(obj, "num_channels", num_channels)
        _obj_set_attr(obj, "bit_depth", bit_depth)
        _obj_set_attr(obj, "num_samples", num_samples)
        _obj_set_attr(obj, "md5", md5)
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
        return (
            self.min_block_size.to_bytes(2, byteorder="big")
            + self.max_block_size.to_bytes(2, byteorder="big")
            + self.min_frame_size.to_bytes(3, byteorder="big")
            + self.max_frame_size.to_bytes(3, byteorder="big")
            + (
                (self.sample_rate << 4)
                | ((self.num_channels - 1) << 1)
                | ((self.bit_depth - 1) >> 4)
            ).to_bytes(2, byteorder="big")
            + (
                ((self.bit_depth - 1) << 4) | ((self.num_samples >> 32) & 0x0F)
            ).to_bytes(2, byteorder="big")
            + (self.num_samples & 0xFFFFFFFF).to_bytes(4, byteorder="big")
            + bytes.fromhex(self.md5)
        )


@dataclass(frozen=True, slots=True)
class FLACApplication:
    """
    FLAC :code:`APPLICATION` metadata block data.

    Parameters
    ----------
    app_id : bytes or bytearray
        Application ID.

        .. seealso::

           `FLAC Application Metadata Block IDs
           <https://www.iana.org/assignments/flac/flac.xhtml>`_ –
           Registry of 8-digit hexadecimal IDs for third-party
           applications.

    app_data : bytes or bytearray
        Application data.
    """

    #: Application ID.
    app_id: bytes | bytearray
    #: Application data.
    app_data: bytes | bytearray

    def __post_init__(self) -> None:
        validate_type("app_id", self.app_id, bytes | bytearray)
        if len(self.app_id) != 4:
            raise ValueError("`app_id` must have length 4.")
        validate_type("app_data", self.app_data, bytes | bytearray)

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
        _obj_set_attr(obj, "app_id", stream[:4].tobytes())
        _obj_set_attr(obj, "app_data", stream[4:].tobytes())
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


@dataclass(frozen=True, slots=True)
class FLACSeekTable:
    """
    FLAC :code:`SEEKTABLE` metadata block data.

    Parameters
    ----------
    seek_points : OrderedCollection[FLACSeekPoint, ...]
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
        size = len(stream)
        num_seek_points, remainder = divmod(size, 18)
        if remainder:
            raise ValueError(
                f"Invalid SEEKTABLE block size of {size}, "
                "which is not divisible by 18."
            )
        seek_points = tuple(
            FLACSeekPoint._from_unpack(*data)
            for data in FLACSeekPoint._STRUCT.iter_unpack(
                stream[: 18 * num_seek_points]
            )
        )
        cls._validate_seek_points(seek_points, custom=False)

        obj = cls.__new__(cls)
        _obj_set_attr(obj, "seek_points", seek_points)
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


@dataclass(frozen=True, slots=True)
class FLACSeekPoint:
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
    _pack = _STRUCT.pack
    _unpack_from = _STRUCT.unpack_from

    #: Sample number of the first sample in the target frame.
    sample_number: int
    #: Byte offset of the target frame header relative to the first
    #: frame header.
    byte_offset: int
    #: Number of samples in the target frame.
    num_samples: int

    def __post_init__(self) -> None:
        validate_number("sample_number", self.sample_number, int, 0)
        validate_number("byte_offset", self.byte_offset, int, 0)
        validate_number("num_samples", self.num_samples, int, 0)

    @classmethod
    def _from_unpack(
        cls, sample_number: int, byte_offset: int, num_samples: int
    ) -> FLACSeekPoint:
        """
        Instantiate a :class:`FLACSeekPoint` object using data unpacked
        from a bytes-like object.

        Parameters
        ----------
        sample_number : int
            Sample number of the first sample in the target frame.

        byte_offset : int
            Byte offset of the target frame header relative to the first
            frame header.

        num_samples : int
            Number of samples in the target frame.

        Returns
        -------
        seek_point : minim.media.flac.FLACSeekPoint
            :code:`SEEKPOINT` data.
        """
        obj = cls.__new__(cls)
        _obj_set_attr(obj, "sample_number", sample_number)
        _obj_set_attr(obj, "byte_offset", byte_offset)
        _obj_set_attr(obj, "num_samples", num_samples)
        return obj

    @classmethod
    def from_stream(cls, stream: BytesLike, /) -> FLACSeekPoint:
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
        return cls._from_unpack(*cls._unpack_from(as_buffer(stream)))

    def serialize(self) -> bytes:
        """
        Serialize the :code:`SEEKPOINT` data to a bytestream.

        Returns
        -------
        bytestream : bytes
            Bytestream containing :code:`SEEKPOINT` data.
        """
        return self._pack(
            self.sample_number, self.byte_offset, self.num_samples
        )


@dataclass(frozen=True, slots=True)
class FLACCueSheet:
    """
    FLAC :code:`CUESHEET` metadata block data.

    Parameters
    ----------
    media_catalog_number : str
        Media catalog number.

    num_lead_in_samples : int
        Number of lead-in samples for CD-DA cue sheets.

    is_cd : bool
        Whether the cue sheet is for CD-DA.

    tracks : OrderedCollection[minim.media.flac.FLACCueSheetTrack, ...]
        Tracks.
    """

    _ASCII_CHARS_REGEX = re.compile("[\x20-\x7e]*$")
    _STRUCT = struct.Struct(">128sQB258sB")
    _pack = _STRUCT.pack
    _unpack_from = _STRUCT.unpack_from

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
        if not self._ASCII_CHARS_REGEX.match(media_catalog_number):
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
        ) = cls._unpack_from(stream)
        if is_cd & 0x7F or reserved != 258 * b"\x00":
            raise ValueError(
                "Non-zero bits found in reserved section of CUESHEET block."
            )

        if not num_tracks:
            raise ValueError(
                f"Invalid number of tracks ({num_tracks}) in CUESHEET block."
            )

        is_cd &= 0x80
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

        cls._validate_tracks(tracks, is_cd=is_cd, custom=False)

        obj = cls.__new__(cls)
        _obj_set_attr(
            obj,
            "media_catalog_number",
            media_catalog_number.rstrip(b"\x00").decode(),
        )
        _obj_set_attr(obj, "num_lead_in_samples", num_lead_in_samples)
        _obj_set_attr(obj, "is_cd", bool(is_cd))
        _obj_set_attr(obj, "tracks", tuple(tracks))
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
        return self._pack(
            self.media_catalog_number.encode(),
            self.num_lead_in_samples,
            self.is_cd << 7,
            258 * b"\x00",
            self.num_tracks,
        ) + b"".join(track.serialize() for track in self.tracks)


@dataclass(frozen=True, slots=True)
class FLACCueSheetTrack:
    """
    FLAC :code:`CUESHEET_TRACK` data.

    Parameters
    ----------
    sample_offset : int
        Sample offset of the track relative to the beginning of the FLAC
        audio stream.

    number : int
        Track number.

    isrc : str
        International Standard Recording Code (ISRC).

    is_audio : bool
        Whether the track contains audio data.

    has_pre_emphasis : bool
        Whether the track has pre-emphasis.

    tracks : OrderedCollection[minim.media.flac.FLACCueSheetTrackIndex]
        Track indices.
    """

    _STRUCT = struct.Struct(">QB12sB13sB")
    _pack = _STRUCT.pack
    _unpack_from = _STRUCT.unpack_from

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
        ) = cls._unpack_from(stream)
        isrc = "" if isrc == 12 * b"\x00" else prepare_isrc(isrc.decode())
        is_audio = bool(flags & 0x80)
        has_pre_emphasis = bool(flags & 0x40)
        if flags & 0x3F or reserved != 13 * b"\x00":
            raise ValueError(
                "Non-zero bits found in reserved section of "
                "CUESHEET_TRACK data."
            )

        indices = tuple(
            FLACCueSheetTrackIndex._from_unpack(*data)
            for data in FLACCueSheetTrackIndex._STRUCT.iter_unpack(
                stream[36 : 36 + 12 * num_indices]
            )
        )
        cls._validate_indices(indices, custom=False)

        obj = cls.__new__(cls)
        _obj_set_attr(obj, "sample_offset", sample_offset)
        _obj_set_attr(obj, "number", number)
        _obj_set_attr(obj, "isrc", isrc)
        _obj_set_attr(obj, "is_audio", is_audio)
        _obj_set_attr(obj, "has_pre_emphasis", has_pre_emphasis)
        _obj_set_attr(obj, "indices", indices)
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
        return self._pack(
            self.sample_offset,
            self.number,
            self.isrc.encode() if self.isrc else 12 * b"\x00",
            (self.is_audio << 7) | (self.has_pre_emphasis << 6),
            13 * b"\x00",
            self.num_indices,
        ) + b"".join(index.serialize() for index in self.indices)


@dataclass(frozen=True, slots=True)
class FLACCueSheetTrackIndex:
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
    _pack = _STRUCT.pack
    _unpack_from = _STRUCT.unpack_from

    #: Sample offset of the index point relative to the track offset.
    sample_offset: int
    #: Track index number.
    number: int

    def __post_init__(self) -> None:
        validate_number("sample_offset", self.sample_offset, int, 0)
        validate_number("number", self.number, int, 0)

    @classmethod
    def _from_unpack(
        cls, sample_offset: int, number: int, reserved: bytes
    ) -> FLACCueSheetTrackIndex:
        """
        Instantiate a :class:`FLACCueSheetTrackIndex` object using data
        unpacked from a bytes-like object.

        Parameters
        ----------
        sample_offset : int
            Sample offset of the index point relative to the track
            offset.

        number : int
            Track index number.

        reserved : bytes
            Reserved space in a :code:`CUESHEET_TRACK_INDEX`.

        Returns
        -------
        track_index : minim.media.flac.FLACCueSheetTrackIndex
            :code:`CUESHEET_TRACK_INDEX` data.
        """
        if reserved != 3 * b"\x00":
            raise ValueError(
                "Non-zero bits found in reserved section of "
                "CUESHEET_TRACK_INDEX data."
            )

        obj = cls.__new__(cls)
        _obj_set_attr(obj, "sample_offset", sample_offset)
        _obj_set_attr(obj, "number", number)
        return obj

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
        return cls._from_unpack(*cls._unpack_from(as_buffer(stream)))

    def serialize(self) -> bytes:
        """
        Serialize the :code:`CUESHEET_TRACK_INDEX` data to a bytestream.

        Returns
        -------
        bytestream : bytes
            Bytestream containing :code:`CUESHEET_TRACK_INDEX` data.
        """
        return self._pack(self.sample_offset, self.number, 3 * b"\x00")


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

    # __slots__ = ()  # TODO

    def load_metadata(self) -> None:
        """ """
        self.open()
        file_path = self._file_path
        view = self._view

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
                        FLACMetadataBlock.from_stream(
                            block_data,
                            type_=block_type,
                            size=block_size,
                        )
                    )
                case (
                    1 | 2 | 3 | 5
                ):  # PADDING / APPLICATION / SEEKTABLE / CUESHEET
                    self._metadata.append(
                        FLACMetadataBlock.from_stream(
                            block_data,
                            type_=block_type,
                            size=block_size,
                        )
                    )
                case 4:  # VORBIS_COMMENT
                    metadata_block = FLACMetadataBlock.from_stream(
                        block_data,
                        type_=block_type,
                        size=block_size,
                    )
                    self._metadata.append(metadata_block)
                    self._tags = metadata_block.data
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

        if not self._metadata or self._metadata[0].type != 0:
            raise RuntimeError(
                f"A STREAMINFO block was not found in '{file_path}'."
            )

        del block_data
        self.close()

    def save_metadata(self) -> None: ...  # TODO
