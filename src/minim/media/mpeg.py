from __future__ import annotations
from dataclasses import dataclass, field
from math import floor
from typing import TYPE_CHECKING

from .._utility import decode_32_bit_synchsafe_int
from ._shared import Audio
from .metadata._shared import AudioStreamInfo
from .metadata.id3._core import ID3v2

if TYPE_CHECKING:
    from .._types import BytesLike

__all__ = ["MPEGAudio"]


@dataclass(frozen=True, kw_only=True, repr=False, slots=True)
class MPEGStreamInfo(AudioStreamInfo):
    """
    Moving Pictures Expert Group (MPEG) audio stream information.

    Parameters
    ----------
    num_channels : int; keyword-only
        Number of channels.

    sample_rate : int; keyword-only
        Sample rate in hertz.

    num_samples : int; keyword-only
        Total number of samples.
    """

    _NUM_CHANNELS_RANGE = (1, 2)
    _SAMPLE_RATE_RANGE = (8_000, 48_000)

    bit_depth: None = field(default=None, init=False)

    #: Number of channels.
    num_channels: int
    #: Sample rate in hertz.
    sample_rate: int
    #: Total number of samples.
    num_samples: int
    #: Bitrate in kilobits per second.
    bitrate: int
    #: MPEG version.
    mpeg_version: int | float
    #: Layer.
    layer: int
    #: Type of frame the stream information is sourced from.
    source: str
    #: Bitrate mode.
    bitrate_mode: str
    #: Encoder.
    encoder: str | None


class MPEGAudio(Audio):
    """
    Moving Picture Experts Group (MPEG) audio file.
    """

    _BITRATES = {
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
    _SAMPLES_PER_FRAME = {
        (2, 1): 576,  # MPEG-2 Audio Layer III
        (2, 2): 1_152,  # MPEG-2 Audio Layer II
        (2, 3): 384,  # MPEG-2 Audio Layer I
        (3, 1): 1_152,  # MPEG-1 Audio Layer III
        (3, 2): 1_152,  # MPEG-1 Audio Layer II
        (3, 3): 384,  # MPEG-1 Audio Layer I
    }
    _SAMPLES_PER_FRAME[(0, 1)] = _SAMPLES_PER_FRAME[(2, 1)]
    _SAMPLES_PER_FRAME[(0, 2)] = _SAMPLES_PER_FRAME[(2, 2)]
    _SAMPLES_PER_FRAME[(0, 3)] = _SAMPLES_PER_FRAME[(2, 3)]
    _SAMPLE_RATES = {
        0: (11_025, 12_000, 8_000),  # MPEG-2.5
        2: (22_050, 24_000, 16_000),  # MPEG-2
        3: (44_100, 48_000, 32_000),  # MPEG-1
    }
    _XING_OFFSETS = {
        (3, 1): 21,  # MPEG-1 Audio Layer III, mono
        (2, 1): 13,  # MPEG-2 Audio Layer III, mono
        (0, 1): 13,  # MPEG-2.5 Audio Layer III, mono
        (3, 2): 36,  # MPEG-1 Audio Layer III, stereo
        (2, 2): 21,  # MPEG-2 Audio Layer III, stereo
        (0, 2): 21,  # MPEG-2.5 Audio Layer III, stereo
    }
    _LAME_BITRATE_MODES = {
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

    __slots__ = ("_audio_offset",)

    @staticmethod
    def _find_next_audio_frame(
        stream: BytesLike, /, offset: int, end_byte: int
    ) -> int | None:
        """ """
        while offset < end_byte:
            if stream[offset] == 0xFF and (stream[offset + 1] & 0xE0) == 0xE0:
                return offset
            else:
                offset += 1

    @staticmethod
    def _get_audio_frame_stream_info(
        stream: BytesLike, /, offset: int
    ) -> AudioStreamInfo:
        """ """
        ...  # TODO

    @staticmethod
    def _get_stream_info(
        stream: BytesLike,
        /,
        end_byte: int | None = None,
        *,
        strict: bool = True,
    ) -> MPEGStreamInfo:
        """ """
        if end_byte is None:
            end_byte = len(stream) - 4

        # Read first audio frame
        offset = MPEGAudio._find_next_audio_frame(
            stream, offset=0, end_byte=end_byte
        )
        byte_2 = stream[offset + 1]
        raw_mpeg_version = (byte_2 >> 3) & 3
        raw_layer = (byte_2 >> 1) & 3
        byte_3 = stream[offset + 2]
        sample_rate = MPEGAudio._SAMPLE_RATES[raw_mpeg_version][
            (byte_3 >> 2) & 3
        ]
        num_channels = 2 - ((stream[offset + 3] >> 6) == 3)

        if raw_layer == 1:
            # Process the Xing header, if any
            if (
                magic_string := stream[
                    (
                        xing_offset := (
                            offset
                            + MPEGAudio._XING_OFFSETS[
                                raw_mpeg_version, num_channels
                            ]
                            + 2 * (not (byte_2 & 1))
                        )
                    ) : (end_xing_offset := xing_offset + 4)
                ].tobytes()
            ) in {b"Info", b"Xing"}:
                xing_offset = end_xing_offset
                end_xing_offset = xing_offset + 4
                if (
                    strict
                    and int.from_bytes(stream[xing_offset:end_xing_offset])
                    >> 4
                ):
                    raise ValueError(
                        "Non-zero bits found in reserved section of Xing header."
                    )

                bitrate_mode = "CBR" if magic_string == b"Info" else "VBR"
                xing_flags = stream[xing_offset + 3]
                xing_offset = end_xing_offset
                has_xing_frames_flag = xing_flags & 1
                if has_xing_frames_flag:
                    end_xing_offset = xing_offset + 4
                    total_frames = int.from_bytes(
                        stream[xing_offset:end_xing_offset]
                    )
                    num_samples = (
                        total_frames
                        * MPEGAudio._SAMPLES_PER_FRAME[
                            raw_mpeg_version, raw_layer
                        ]
                    )
                    xing_offset = end_xing_offset
                if has_xing_frames_flag and xing_flags & 2:
                    end_xing_offset = xing_offset + 4
                    bitrate = round(
                        8
                        * sample_rate
                        * int.from_bytes(stream[xing_offset:end_xing_offset])
                        / (1_000 * num_samples)
                    )
                    xing_offset = end_xing_offset
                elif bitrate_mode == "CBR":
                    ...  # TODO: Get bitrate using next frame.
                else:
                    ...  # TODO: Compute bitrate.

                # Skip table of contents and quality indicator, if any
                xing_offset += 4 * bool(xing_flags & 8) + 100 * bool(
                    xing_flags & 4
                )

                # Process the LAME header, if any
                try:
                    encoder = (
                        stream[xing_offset : xing_offset + 9]
                        .tobytes()
                        .decode(encoding="ascii")
                    )
                    bitrate_mode = MPEGAudio._LAME_BITRATE_MODES[
                        stream[xing_offset + 9] & 0x0F
                    ]

                except UnicodeDecodeError:
                    encoder = None

                return MPEGStreamInfo(
                    num_channels=num_channels,
                    sample_rate=sample_rate,
                    num_samples=num_samples,
                    bitrate=bitrate,
                    mpeg_version=(4 - raw_mpeg_version)
                    if raw_mpeg_version
                    else 2.5,
                    layer=4 - raw_layer,
                    source=magic_string.decode(encoding="ascii"),
                    bitrate_mode=bitrate_mode,
                    encoder=encoder,
                )

            # Process the VBR Info header, if any
            elif (
                magic_string := stream[
                    (vbri_offset := (offset + 36 + 2 * (not (byte_2 & 1)))) : (
                        end_vbri_offset := vbri_offset + 4
                    )
                ].tobytes()
            ) == b"VBRI":
                debug = True

        # Process the frame header
        else:
            bitrate = MPEGAudio._BITRATES[raw_mpeg_version, raw_layer][
                byte_3 >> 4
            ]
            debug = True
        offset += floor(144_000 * bitrate / sample_rate)
        return

    def load_metadata(self) -> None:
        """
        Load ID3 tags and MPEG stream information.
        """
        self.open()
        # file_path = self._file_path
        view = self._view

        self._format_metadata = []
        strict = self._strict

        # Process ID3v2 tags, if any
        if view[:3] == b"ID3":
            offset = 10 + decode_32_bit_synchsafe_int(*view[6:10])
            tags = ID3v2.from_stream(view[:offset], strict=strict)
            self._format_metadata.append(tags)
            self._tags = tags
            self._audio_offset = offset
        else:
            self._audio_offset = 0

        # Process ID3v1 tags, if any
        ...  # TODO

        # Process APE tags, if any
        ...  # TODO

        # Process Lyrics3 tags, if any
        ...  # TODO

        # Process audio data to get stream information
        # TODO: Get end_byte by subtracting ID3v1, APE, and Lyrics3 tags.
        self._stream_info = self._get_stream_info(view[offset:], strict=strict)

        self.close()

    def add_metadata(self) -> None:
        """ """
        ...  # TODO

    def remove_metadata(self) -> None:
        """ """
        ...  # TODO

    def save(self) -> None:
        """ """
        ...  # TODO
