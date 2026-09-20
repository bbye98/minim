"""
Moving Picture Experts Group (MPEG) audio file handler and stream
information reporter.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

from .._types import COLLECTION_TYPES
from .._utility import join_values, set_obj_attr, validate_type
from ._shared import Audio, MetadataView
from .metadata._shared import AudioStreamInfo
from .metadata.id3._core import ID3v1, ID3v2
from .metadata.id3._shared import decode_synchsafe_int

if TYPE_CHECKING:
    from typing import Any, Self

    from .._types import Collection, PathLike


__all__ = ["MPEGAudio", "MPEGStreamInfo"]


@dataclass(frozen=True, kw_only=True, repr=False, slots=True)
class MPEGStreamInfo(AudioStreamInfo):
    """
    MPEG audio stream information.

    Parameters
    ----------
    num_channels : int; keyword-only
        Number of channels.

    sample_rate : int; keyword-only
        Sample rate, in hertz.

    num_samples : int; keyword-only
        Total number of samples.

    bitrate : int; keyword-only
        Bitrate, in kilobits per second.

    mpeg_version : int or float; keyword-only
        MPEG version.

        **Valid values**: :code:`1`, :code:`2`, :code:`2.5`.

    layer : int; keyword-only
        Layer.

    bitrate_mode : str; keyword-only
        Bitrate mode.

    source : str; keyword-only; default: :code:`None`
        Type of frame the stream information is sourced from.

    encoder : str; keyword-only; default: :code:`None`
        Encoder.
    """

    _NUM_CHANNELS_RANGE: ClassVar[tuple[int, int]] = (1, 2)
    _SAMPLE_RATE_RANGE: ClassVar[tuple[int, int]] = (8_000, 48_000)

    bit_depth: None = field(default=None, init=False)

    #: :bdg-primary:`get` :bdg-secondary-line:`set` Bitrate, in kilobits
    #: per second.
    bitrate: int
    #: :bdg-primary:`get` :bdg-secondary-line:`set` MPEG version.
    mpeg_version: int | float
    #: :bdg-primary:`get` :bdg-secondary-line:`set` Layer.
    layer: int
    #: :bdg-primary:`get` :bdg-secondary-line:`set` Bitrate mode.
    bitrate_mode: str
    #: :bdg-primary:`get` :bdg-secondary-line:`set` Type of frame the
    #: stream information is sourced from.
    source: str | None = None
    #: :bdg-primary:`get` :bdg-secondary-line:`set` Encoder.
    encoder: str | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        mpeg_version = self.mpeg_version
        if mpeg_version not in (mpeg_versions := {1, 2, 2.5}):
            raise ValueError(
                f"Invalid MPEG version {mpeg_version!r}. "
                f"Valid values: {join_values(mpeg_versions)}."
            )
        mpeg_version = 0 if mpeg_version == 2.5 else (4 - mpeg_version)

        layer = self.layer
        if layer not in (layers := range(1, 4)):
            raise ValueError(
                f"Invalid layer {layer!r}. "
                f"Valid values: {join_values(tuple(layers))}."
            )
        layer = 4 - layer

        if self.bitrate not in (
            bitrates := MPEGAudio._BITRATES[mpeg_version, layer]
        ):
            raise ValueError(
                f"Invalid bitrate {self.bitrate!r}. "
                f"Valid values: {join_values(bitrates)}."
            )

        if self.bitrate_mode not in (bitrate_modes := {"CBR", "VBR"}):
            raise ValueError(
                f"Invalid bitrate mode {self.bitrate_mode!r}. "
                f"Valid values: {join_values(bitrate_modes)}."
            )

        if self.source is not None:
            validate_type("source", self.source, str)

        if self.encoder is not None:
            validate_type("encoder", self.encoder, str)

    @classmethod
    def _from_data(
        cls,
        *,
        num_channels: int,
        sample_rate: int,
        num_samples: int,
        bitrate: int,
        mpeg_version: int | float,  # noqa: PYI041
        layer: int,
        bitrate_mode: str,
        source: str | None = None,
        encoder: str | None = None,
    ) -> Self:
        """
        Instantiate a :class:`MPEGStreamInfo` object directly from data.

        Parameters
        ----------
        num_channels : int; keyword-only
            Number of channels.

        sample_rate : int; keyword-only
            Sample rate, in hertz.

        num_samples : int; keyword-only
            Total number of samples.

        bitrate : int; keyword-only
            Bitrate, in kilobits per second.

        mpeg_version : int or float; keyword-only
            MPEG version.

            **Valid values**: :code:`1`, :code:`2`, :code:`2.5`.

        layer : int; keyword-only
            Layer.

        bitrate_mode : str; keyword-only
            Bitrate mode.

        source : str; keyword-only; default: :code:`None`
            Type of frame the stream information is sourced from.

        encoder : str; keyword-only; default: :code:`None`
            Encoder.

        Returns
        -------
        stream_info : minim.media.mpeg.MPEGStreamInfo
            MPEG audio stream information.
        """
        obj = cls.__new__(cls)
        set_obj_attr(obj, "num_channels", num_channels)
        set_obj_attr(obj, "sample_rate", sample_rate)
        set_obj_attr(obj, "bit_depth", None)
        set_obj_attr(obj, "num_samples", num_samples)
        set_obj_attr(obj, "bitrate", bitrate)
        set_obj_attr(obj, "mpeg_version", mpeg_version)
        set_obj_attr(obj, "layer", layer)
        set_obj_attr(obj, "bitrate_mode", bitrate_mode)
        set_obj_attr(obj, "source", source)
        set_obj_attr(obj, "encoder", encoder)
        return obj


class MPEGMetadataView(MetadataView):
    """
    View of MPEG metadata containers.

    .. important::

       This class is managed by :class:`MPEGAudio` and should not be
       instantiated directly.

    This class implements the following special methods:

    * :code:`__getitem__` – Return the metadata container at an index.

    * :code:`__iter__` – Return an iterator of the metadata containers.

    * :code:`__len__` – Return the number of metadata containers.
    """

    def get(
        self,
        types: type[ID3v1 | ID3v2] | Collection[type[ID3v1 | ID3v2]],
        /,
    ) -> list[ID3v1 | ID3v2] | dict[type[ID3v1 | ID3v2], list[ID3v1 | ID3v2]]:
        """
        Get MPEG metadata containers by type.

        .. important::

           It is *not* guaranteed that the metadata containers are in
           the same order as they are found in the MPEG audio file,
           especially after metadata containers have been added or
           removed.

        Parameters
        ----------
        types : type[minim.media.metadata.ID3v1 \
        | minim.media.metadata.ID3v2], or \
        Collection[type[minim.media.metadata.ID3v1 \
        | minim.media.metadata.ID3v2]]; positional-only
            Types of metadata containers.

            **Valid values**: :class:`~minim.media.metadata.ID3v1`,
            :class:`~minim.media.metadata.ID3v2`.

        Returns
        -------
        blocks : list[minim.media.metadata.ID3v1 \
        | minim.media.metadata.ID3v2] or \
        dict[type[minim.media.metadata.ID3v1 \
        | minim.media.metadata.ID3v2], list[minim.media.metadata.ID3v1 \
        | minim.media.metadata.ID3v2]]
            Metadata containers. If `types` is a collection, a
            dictionary mapping the metadata container types to the
            metadata blocks is returned.
        """
        if not isinstance(types, COLLECTION_TYPES):
            types = {types}

        types_ = set()
        for type_ in types:
            if isinstance(type_, type) and type_ in (ID3v1, ID3v2):
                types_.add(type_)
            else:
                raise TypeError(
                    "`types` must be one or more classes of MPEG "
                    "metadata containers. "
                )

        if len(types_) == 1:
            return self._type_index[types_.pop()] or None

        return {type_: self._type_index[type_] or None for type_ in types_}


class MPEGAudio(Audio):
    """
    MPEG audio file.
    """

    _BITRATES: ClassVar[dict[tuple[int, int], tuple[int, ...]]] = {
        (2, 1): (  # MPEG-2 Audio Layer III
            0,
            8,
            16,
            24,
            32,
            40,
            48,
            56,
            64,
            80,
            96,
            112,
            128,
            144,
            160,
        ),
        (2, 3): (  # MPEG-2 Audio Layer I
            0,
            32,
            44,
            48,
            56,
            64,
            80,
            96,
            112,
            128,
            160,
            192,
            224,
            256,
            384,
        ),
        (3, 1): (  # MPEG-1 Audio Layer III
            0,
            32,
            40,
            48,
            56,
            64,
            80,
            96,
            112,
            128,
            160,
            192,
            224,
            256,
            320,
        ),
        (3, 2): (  # MPEG-1 Audio Layer II
            0,
            32,
            48,
            56,
            64,
            80,
            96,
            112,
            128,
            160,
            192,
            224,
            256,
            320,
            384,
        ),
        (3, 3): (  # MPEG-1 Audio Layer I
            0,
            32,
            64,
            96,
            128,
            160,
            192,
            224,
            256,
            288,
            320,
            352,
            384,
            416,
            448,
        ),
    }
    _BITRATES[(0, 1)] = _BITRATES[(0, 2)] = _BITRATES[(2, 2)] = _BITRATES[
        (2, 1)
    ]
    _BITRATES[(0, 3)] = _BITRATES[(2, 3)]

    _SAMPLES_PER_FRAME: ClassVar[dict[tuple[int, int], int]] = {
        (2, 1): 576,  # MPEG-2 Audio Layer III
        (2, 2): 1_152,  # MPEG-2 Audio Layer II
        (2, 3): 384,  # MPEG-2 Audio Layer I
        (3, 1): 1_152,  # MPEG-1 Audio Layer III
        (3, 2): 1_152,  # MPEG-1 Audio Layer II
        (3, 3): 384,  # MPEG-1 Audio Layer I
    }
    _SAMPLES_PER_FRAME[(0, 1)] = _SAMPLES_PER_FRAME[
        (2, 1)
    ]  # MPEG-2.5 Audio Layer III
    _SAMPLES_PER_FRAME[(0, 2)] = _SAMPLES_PER_FRAME[
        (2, 2)
    ]  # MPEG-2.5 Audio Layer II
    _SAMPLES_PER_FRAME[(0, 3)] = _SAMPLES_PER_FRAME[
        (2, 3)
    ]  # MPEG-2.5 Audio Layer I

    _SAMPLE_RATES: ClassVar[dict[int, tuple[int, ...]]] = {
        0: (11_025, 12_000, 8_000),  # MPEG-2.5
        2: (22_050, 24_000, 16_000),  # MPEG-2
        3: (44_100, 48_000, 32_000),  # MPEG-1
    }

    _XING_OFFSETS: ClassVar[dict[tuple[int, int], int]] = {
        (3, 1): 21,  # MPEG-1 Audio Layer III, mono
        (2, 1): 13,  # MPEG-2 Audio Layer III, mono
        (0, 1): 13,  # MPEG-2.5 Audio Layer III, mono
        (3, 2): 36,  # MPEG-1 Audio Layer III, stereo
        (2, 2): 21,  # MPEG-2 Audio Layer III, stereo
        (0, 2): 21,  # MPEG-2.5 Audio Layer III, stereo
    }

    _LAME_BITRATE_MODES: ClassVar[dict[int, str]] = {
        0: "CBR",
        1: "VBR",
        2: "VBR",
        3: "ABR",
        4: "ABR",
        5: "ABR",
        6: "ABR",
        7: "VBR",
        8: "VBR",
        9: "ABR",
    }

    __slots__ = ("_end_audio_offset",)

    @staticmethod
    def _sync_audio_frames(
        stream: memoryview,
        /,
        offset: int = 0,
        *,
        num_consecutive_frames: int = 2,
    ) -> int | None:
        """
        Synchronize to the MPEG audio frames.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the MPEG audio stream.

        offset : int; default: :code:`0`
            Byte offset in `stream` where the MPEG audio stream begins.

        num_consecutive_frames : int; default: :code:`2`
            Number of consecutive frames to check to be confident that
            the parser is synchronized to the MPEG audio stream.

        Return
        ------
        offset : int or None
           Byte offset of the first MPEG audio frame. If :code:`None`,
           the MPEG audio stream could not be synchronized.
        """
        max_length = len(stream) - 4
        while offset < max_length:
            check_offset = offset
            for _ in range(num_consecutive_frames):
                if check_offset >= max_length:
                    break

                byte_2 = stream[check_offset + 1]
                if stream[check_offset] != 0xFF or (byte_2 & 0xE0) != 0xE0:
                    break

                raw_mpeg_version = (byte_2 >> 3) & 3
                raw_layer = (byte_2 >> 1) & 3
                if raw_mpeg_version == 1 or not raw_layer:
                    break

                byte_3 = stream[check_offset + 2]
                try:
                    sample_rate = MPEGAudio._SAMPLE_RATES[raw_mpeg_version][
                        (byte_3 >> 2) & 3
                    ]
                    bitrate = MPEGAudio._BITRATES[raw_mpeg_version, raw_layer][
                        byte_3 >> 4
                    ]
                    frame_length = 125 * MPEGAudio._SAMPLES_PER_FRAME[
                        raw_mpeg_version, raw_layer
                    ] * bitrate // sample_rate + ((byte_3 >> 1) & 1)
                    if not frame_length:
                        break
                except (KeyError, IndexError):
                    break

                check_offset += frame_length
            else:
                return offset

            offset += 1

    @staticmethod
    def _scan_audio_frame_headers(
        stream: memoryview,
        /,
        offset: int,
        *,
        raw_mpeg_version: int,
        raw_layer: int,
        num_channels: int,
        sample_rate: int,
    ) -> tuple[int, int, str]:
        """
        Scan audio frame headers and report the total number of samples,
        the average bitrate, and the bitrate mode.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the MPEG audio stream.

        offset : int
            Byte offset in `stream` where the MPEG audio stream begins.

        raw_mpeg_version : int; keyword-only
            Raw frame header bits indicating MPEG version.

        raw_layer : int; keyword-only
            Raw frame header bits indicating layer.

        num_channels : int; keyword-only
            Number of channels.

        sample_rate : int; keyword-only
            Sample rate, in hertz.

        Returns
        -------
        num_samples : int
            Total number of samples.

        bitrate : int
            Bitrate, in kilobits per second.

        bitrate_mode : str
            Bitrate mode.
        """
        max_length = len(stream) - 4
        num_samples = total_bytes = 0
        seen_bitrates = set()
        while offset < max_length:
            byte_2 = stream[offset + 1]
            if stream[offset] != 0xFF or (byte_2 & 0xE0) != 0xE0:
                break

            _raw_mpeg_version = (byte_2 >> 3) & 3
            if _raw_mpeg_version == 1:
                break
            if _raw_mpeg_version != raw_mpeg_version:
                break

            _raw_layer = (byte_2 >> 1) & 3
            if not _raw_layer:
                break
            if _raw_layer != raw_layer:
                break

            byte_3 = stream[offset + 2]
            try:
                if (
                    MPEGAudio._SAMPLE_RATES[raw_mpeg_version][
                        (byte_3 >> 2) & 3
                    ]
                    != sample_rate
                ):
                    break

                if (2 - ((stream[offset + 3] >> 6) == 3)) != num_channels:
                    break

                samples_per_frame = MPEGAudio._SAMPLES_PER_FRAME[
                    raw_mpeg_version, raw_layer
                ]
                bitrate = MPEGAudio._BITRATES[raw_mpeg_version, raw_layer][
                    byte_3 >> 4
                ]
                frame_length = (
                    125 * samples_per_frame * bitrate // sample_rate
                    + ((byte_3 >> 1) & 1)
                )
                if not frame_length:
                    break

                seen_bitrates.add(bitrate)
                num_samples += samples_per_frame
                total_bytes += frame_length
            except (KeyError, IndexError):
                break

            offset += frame_length

        return (
            num_samples,
            round(total_bytes * sample_rate / (125 * num_samples)),
            "CBR" if len(seen_bitrates) <= 1 else "VBR",
        )

    @staticmethod
    def _parse_vbri_header(
        stream: memoryview,
        /,
        *,
        raw_mpeg_version: int,
        raw_layer: int,
        num_channels: int,
        sample_rate: int,
        vbri_offset: int,
    ) -> Self:
        """
        Parse a VBR Info header.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the VBR Info header.

        raw_mpeg_version : int; keyword-only
            Raw frame header bits indicating MPEG version.

        raw_layer : int; keyword-only
            Raw frame header bits indicating layer.

        num_channels : int; keyword-only
            Number of channels.

        sample_rate : int; keyword-only
            Sample rate, in hertz.

        vbri_offset : int; keyword-only
            Byte offset in `stream` where the VBR Info header signature
            ends.

        Returns
        -------
        stream_info : minim.media.mpeg.MPEGStreamInfo
            MPEG audio stream information.
        """
        num_samples = (
            int.from_bytes(
                stream[vbri_offset + 10 : vbri_offset + 14], byteorder="big"
            )
            * MPEGAudio._SAMPLES_PER_FRAME[raw_mpeg_version, raw_layer]
        )
        return MPEGStreamInfo._from_data(
            num_channels=num_channels,
            sample_rate=sample_rate,
            num_samples=num_samples,
            bitrate=round(
                int.from_bytes(
                    stream[vbri_offset + 6 : vbri_offset + 10], byteorder="big"
                )
                * sample_rate
                / (125 * num_samples)
            ),
            mpeg_version=(4 - raw_mpeg_version) if raw_mpeg_version else 2.5,
            layer=4 - raw_layer,
            source="VBRI",
            bitrate_mode="VBR",
            encoder="Fraunhofer IIS",
        )

    @staticmethod
    def _parse_xing_header(
        stream: memoryview,
        /,
        *,
        offset: int,
        raw_mpeg_version: int,
        raw_layer: int,
        num_channels: int,
        sample_rate: int,
        frame_length: int,
        signature: bytes,
        xing_offset: int,
        strict: bool,
    ) -> Self:
        """
        Parse a Xing header.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the Xing header.

        offset : int; keyword-only
            Byte offset in `stream` where the MPEG audio frame
            containing the Xing header begins.

        raw_mpeg_version : int; keyword-only
            Raw frame header bits indicating MPEG version.

        raw_layer : int; keyword-only
            Raw frame header bits indicating layer.

        num_channels : int; keyword-only
            Number of channels.

        sample_rate : int; keyword-only
            Sample rate, in hertz.

        frame_length : int; keyword-only
            MPEG audio frame length.

        signature : bytes; keyword-only
            Xing header signature.

        xing_offset : int; keyword-only
            Byte offset in `stream` where the Xing header signature
            ends.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the MPEG
            format specifications.

        Returns
        -------
        stream_info : minim.media.mpeg.MPEGStreamInfo
            MPEG audio stream information.
        """
        end_xing_offset = xing_offset + 4
        if (
            strict
            and int.from_bytes(
                stream[xing_offset:end_xing_offset], byteorder="big"
            )
            >> 4
        ):
            raise ValueError(
                "Non-zero bits found in reserved section of Xing header."
            )

        bitrate_mode = "CBR" if signature == b"Info" else "VBR"
        xing_flags = stream[xing_offset + 3]
        xing_offset = end_xing_offset
        has_num_samples = xing_flags & 1
        if has_num_samples:
            end_xing_offset = xing_offset + 4
            num_samples = (
                int.from_bytes(
                    stream[xing_offset:end_xing_offset], byteorder="big"
                )
                * MPEGAudio._SAMPLES_PER_FRAME[raw_mpeg_version, raw_layer]
            )
            xing_offset = end_xing_offset

        has_bitrate = has_num_samples and (xing_flags & 2)
        if has_bitrate:
            end_xing_offset = xing_offset + 4
            bitrate = round(
                8
                * sample_rate
                * int.from_bytes(
                    stream[xing_offset:end_xing_offset], byteorder="big"
                )
                / (1_000 * num_samples)
            )
            xing_offset = end_xing_offset

        # Skip table of contents and quality indicator, if any
        xing_offset += 4 * bool(xing_flags & 8) + 100 * bool(xing_flags & 4)

        # Process the LAME header, if any
        try:
            xing_bitrate_offset = xing_offset + 9
            encoder = (
                stream[xing_offset:xing_bitrate_offset]
                .tobytes()
                .decode(encoding="ascii")
            )
            bitrate_mode = MPEGAudio._LAME_BITRATE_MODES[
                stream[xing_bitrate_offset] & 0x0F
            ]
        except UnicodeDecodeError:
            encoder = None

        # If number of samples is unknown or bitrate is unknown for a
        # VBR audio stream, scan all audio frame headers
        if (
            not has_num_samples
            or not has_bitrate
            and (has_variable_bitrate := bitrate_mode != "CBR")
        ):
            num_samples, bitrate, bitrate_mode = (
                MPEGAudio._scan_audio_frame_headers(
                    stream,
                    offset=offset + frame_length,
                    raw_mpeg_version=raw_mpeg_version,
                    raw_layer=raw_layer,
                    num_channels=num_channels,
                    sample_rate=sample_rate,
                )
            )

        # If bitrate is unknown for a CBR audio stream, look at the next
        # audio frame header
        elif not has_bitrate and not has_variable_bitrate:
            offset += frame_length
            if offset < len(stream) - 4:
                byte_2 = stream[offset + 1]
                if (byte_2 >> 3) & 3 != raw_mpeg_version:
                    raise ValueError(
                        "MPEG version mismatch between Xing header "
                        "and audio frame immediately after it."
                    )
                if (byte_2 >> 1) & 3 != raw_layer:
                    raise ValueError(
                        "MPEG layer mismatch between Xing header "
                        "and audio frame immediately after it."
                    )
                bitrate = MPEGAudio._BITRATES[raw_mpeg_version, raw_layer][
                    stream[offset + 2] >> 4
                ]
            else:
                bitrate = 0

        return MPEGStreamInfo._from_data(
            num_channels=num_channels,
            sample_rate=sample_rate,
            num_samples=num_samples,
            bitrate=bitrate,
            mpeg_version=(4 - raw_mpeg_version) if raw_mpeg_version else 2.5,
            layer=4 - raw_layer,
            source=signature.decode(encoding="ascii"),
            bitrate_mode=bitrate_mode,
            encoder=encoder,
        )

    @staticmethod
    def _get_stream_info(
        stream: memoryview, /, *, strict: bool
    ) -> Self | None:
        """
        Get MPEG audio stream information.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the MPEG audio stream.

        strict : bool; keyword-only
            Whether to ensure metadata strictly adheres to the MPEG
            format specifications.

        Returns
        -------
        stream_info : minim.media.mpeg.MPEGStreamInfo or None
            MPEG audio stream information. If :code:`None`, no audio
            frames were found.
        """
        # Sync and read first audio frame header
        offset = MPEGAudio._sync_audio_frames(stream)
        if offset is None:
            return

        byte_2 = stream[offset + 1]
        raw_mpeg_version = (byte_2 >> 3) & 3
        raw_layer = (byte_2 >> 1) & 3
        byte_3 = stream[offset + 2]
        sample_rate = MPEGAudio._SAMPLE_RATES[raw_mpeg_version][
            (byte_3 >> 2) & 3
        ]
        bitrate = MPEGAudio._BITRATES[raw_mpeg_version, raw_layer][byte_3 >> 4]
        frame_length = 125 * MPEGAudio._SAMPLES_PER_FRAME[
            raw_mpeg_version, raw_layer
        ] * bitrate // sample_rate + (byte_3 & 0x0F)
        num_channels = 2 - ((stream[offset + 3] >> 6) == 3)

        if raw_layer == 1:
            # Process the Xing header, if any
            num_crc_bytes = 2 * (not (byte_2 & 1))
            if (
                signature := stream[
                    (
                        xing_offset := (
                            offset
                            + MPEGAudio._XING_OFFSETS[
                                raw_mpeg_version, num_channels
                            ]
                            + num_crc_bytes
                        )
                    ) : (end_xing_offset := xing_offset + 4)
                ].tobytes()
            ) in (b"Info", b"Xing"):
                return MPEGAudio._parse_xing_header(
                    stream,
                    offset=offset,
                    raw_mpeg_version=raw_mpeg_version,
                    raw_layer=raw_layer,
                    num_channels=num_channels,
                    sample_rate=sample_rate,
                    frame_length=frame_length,
                    signature=signature,
                    xing_offset=end_xing_offset,
                    strict=strict,
                )

            # Process the VBR Info header, if any
            elif (
                stream[
                    (vbri_offset := offset + 36 + num_crc_bytes) : (
                        end_vbri_offset := vbri_offset + 4
                    )
                ]
                == b"VBRI"
            ):
                return MPEGAudio._parse_vbri_header(
                    stream,
                    raw_mpeg_version=raw_mpeg_version,
                    raw_layer=raw_layer,
                    num_channels=num_channels,
                    sample_rate=sample_rate,
                    vbri_offset=end_vbri_offset,
                )

        num_samples, bitrate, bitrate_mode = (
            MPEGAudio._scan_audio_frame_headers(
                stream,
                offset=offset,
                raw_mpeg_version=raw_mpeg_version,
                raw_layer=raw_layer,
                num_channels=num_channels,
                sample_rate=sample_rate,
            )
        )
        return MPEGStreamInfo._from_data(
            num_channels=num_channels,
            sample_rate=sample_rate,
            num_samples=num_samples,
            bitrate=bitrate,
            mpeg_version=(4 - raw_mpeg_version) if raw_mpeg_version else 2.5,
            layer=4 - raw_layer,
            source=None,
            bitrate_mode=bitrate_mode,
            encoder=None,
        )

    @property
    def metadata(self) -> MPEGMetadataView:
        """
        :bdg-primary:`get` :bdg-secondary-line:`set` Metadata containers.
        """
        return self._metadata_view

    def load_metadata(self) -> None:
        """
        Load ID3 tags and MPEG stream information.
        """
        self.open()
        view = self._view
        strict = self._strict
        self._metadata = metadata = []
        self._type_index = type_index = defaultdict(list)
        self._metadata_view = MPEGMetadataView(metadata, type_index=type_index)

        # Process ID3v2 tags, if any
        offset = end_offset = 0
        while view[offset : offset + 3] == b"ID3":
            if strict and metadata:
                raise RuntimeError(
                    "Multiple ID3v2 tags found in the MPEG audio file."
                )

            end_offset = (
                offset
                + 10
                + decode_synchsafe_int(*view[offset + 6 : offset + 10])
            )
            tags = ID3v2.from_stream(view[offset:end_offset], strict=strict)
            offset = end_offset
            metadata.append(tags)
            type_index[ID3v2].append(tags)
            if not hasattr(self, "_tags"):
                self._tags = tags
        self._audio_offset = end_offset

        # Process ID3v1 tags, if any
        end_audio_offset = len(view)
        if view[-128:-125] == b"TAG":
            tags = ID3v1.from_stream(view[-128:])
            metadata.append(tags)
            type_index[ID3v1].append(tags)
            if not hasattr(self, "_tags"):
                self._tags = tags
            end_audio_offset -= 128

        # TODO: Allow for multiple ID3v1 tags when strict=False
        # TODO: Find APE and Lyrics3 tags, if any, using their footers
        # and then process them

        # Process audio data to get stream information
        self._end_audio_offset = end_audio_offset
        self._stream_info = self._get_stream_info(
            view[offset:end_audio_offset], strict=strict
        )

        self.close()

    def add_metadata(
        self, metadata: ID3v1 | ID3v2 | Collection[ID3v1 | ID3v2], /
    ) -> None:
        """
        Add MPEG metadata containers.

        Parameters
        ----------
        metadata : minim.media.metadata.ID3v1, \
        minim.media.metadata.ID3v2, or \
        Collection[minim.media.metadata.ID3v1 \
        | minim.media.metadata.ID3v2]; positional-only
            Metadata containers to add.
        """
        raise NotImplementedError  # TODO

    def remove_metadata(
        self,
        *,
        metadata: int
        | ID3v1
        | ID3v2
        | Collection[int | ID3v1 | ID3v2]
        | None = None,
        types: type[ID3v1 | ID3v2]
        | Collection[type[ID3v1 | ID3v2]]
        | None = None,
    ) -> None:
        """
        Remove MPEG metadata containers.

        .. important::

           Exactly one of `indices`, `metadata`, or `types` must be
           provided.

        Parameters
        ----------
        metadata : minim.media.metadata.ID3v1, \
        minim.media.metadata.ID3v2, or \
        Collection[minim.media.metadata.ID3v1 \
        | minim.media.metadata.ID3v2]; keyword-only; optional
            Indices or instances of metadata containers to remove.

        types : type[minim.media.metadata.ID3v1 \
        | minim.media.metadata.ID3v2] or \
        Collection[type[minim.media.metadata.ID3v1 \
        | minim.media.metadata.ID3v2]]; keyword-only; optional
            Types of metadata containers to remove.

            **Valid values**: :class:`~minim.media.metadata.ID3v1`,
            :class:`~minim.media.metadata.ID3v2`.
        """
        raise NotImplementedError  # TODO

    def save(
        self,
        file_path: PathLike | None = None,
        /,
        *,
        id3v1: dict[str, Any] | None = None,
        id3v2: dict[str, Any] | None = None,
    ) -> None:
        """
        Write changes to disk.

        Parameters
        ----------
        file_path : PathLike; positional-only
            Path to or name of the MPEG audio file. If not specified,
            changes are written back to the source file.

        id3v1 : dict[str, Any]; keyword-only; optional
            Save options for ID3v1 tags.

            .. admonition:: Available options
               :class: response dropdown

               tag_version : str or tuple[int, int]; \
               default: :code:`(1, 1)`
                   ID3v1 tag version.

                   **Valid values**: :code:`"1.0"` or :code:`(1, 0)`,
                   :code:`"1.1"` or :code:`(1, 1)`.

        id3v2 : dict[str, Any]; keyword-only; optional
            Save options for ID3v2 tags.

            .. admonition:: Available options
               :class: response dropdown

               tag_version : str or tuple[int, int, int]; \
               default: :code:`(2, 4, 0)`
                   ID3v2 tag version.

                   **Valid values**: :code:`"2.2.0"` or
                   :code:`(2, 2, 0)`, :code:`"2.3.0"` or
                   :code:`(2, 3, 0)`, :code:`"2.4.0"` or
                   :code:`(2, 4, 0)`.

               text_encoding : str; optional
                   Text encoding to use for all ID3v2 frames. If
                   :code:`None`, the text encodings already associated
                   with the frames are used.

                   **Valid values**: :code:`"iso-8859-1"`,
                   :code:`"utf-16"`, :code:`"utf-16be"`,
                   :code:`"utf-8"`.

               include_padding : bool; default: :code:`True`
                   Whether to keep padding in ID3v2 tags.
        """
        raise NotImplementedError  # TODO
