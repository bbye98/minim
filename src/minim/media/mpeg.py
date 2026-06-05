from __future__ import annotations
from dataclasses import dataclass, field

from .._utility import decode_32_bit_synchsafe_int
from ._shared import Audio
from .metadata._shared import AudioStreamInfo
from .metadata.id3._core import ID3v1, ID3v2

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
        end_byte = len(view)
        if view[-128:-125] == b"TAG":
            tags = ID3v1.from_stream(view[-128:], strict=strict)
            self._format_metadata.append(tags)
            if not hasattr(self, "_tags"):
                self._tags = tags
            end_byte -= 128

        # Process APE tags, if any
        ...  # TODO

        # Process Lyrics3 tags, if any
        ...  # TODO

        # Process audio data to get stream information
        # TODO: Get end_byte by subtracting ID3v1, APE, and Lyrics3 tags.
        # self._stream_info = self._get_stream_info(view[offset:], strict=strict)

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
