from __future__ import annotations
from typing import TYPE_CHECKING

from .._utility import decode_32_bit_synchsafe_int
from ._shared import Audio
from .metadata._shared import AudioStreamInfo
from .metadata.id3._core import ID3v2

if TYPE_CHECKING:
    from .._types import BytesLike

__all__ = ["MPEGAudio"]


class MPEGAudio(Audio):
    """
    Moving Picture Experts Group (MPEG) audio file.
    """

    _BITRATES = {
        (2, 1): (  # MPEG-2, layer III
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
        (2, 3): (  # MPEG-2, layer I
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
        (3, 1): (  # MPEG-1, layer III (MP3)
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
        (3, 2): (  # MPEG-1, layer II
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
        (3, 3): (  # MPEG-1, layer I
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
    _FRAME_SIZES = {
        1: 1_152,  # Layer III
        2: 1_152,  # Layer II
        3: 384,  # Layer I
    }
    _SAMPLE_RATES = {
        0: (11_025, 12_000, 8_000),  # MPEG-2.5
        2: (22_050, 24_000, 16_000),  # MPEG-2
        3: (44_100, 48_000, 32_000),  # MPEG-1
    }

    __slots__ = ("_audio_offset",)

    @staticmethod
    def _get_stream_info(
        stream: BytesLike, /, end_byte: int | None = None
    ) -> AudioStreamInfo:
        """ """
        if end_byte is None:
            end_byte = len(stream) - 4

        num_channels = sample_rate = bit_depth = num_samples = 1  # TODO

        return AudioStreamInfo(
            num_channels=num_channels,
            sample_rate=sample_rate,
            bit_depth=bit_depth,
            num_samples=num_samples,
        )

    def load_metadata(self) -> None:
        """
        Load ID3 tags and MPEG stream information.
        """
        self.open()
        # file_path = self._file_path
        view = self._view

        self._format_metadata = []
        strict = self._strict
        if strict:
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

            # Process audio data to get stream information
            # TODO: Get end_byte by subtracting ID3v1 and APE tags.
            self._stream_info = self._get_stream_info(view[offset:])
        else:
            raise NotImplementedError

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
