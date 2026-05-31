from __future__ import annotations
from math import floor
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
    _XING_OFFSETS = {(2, 1): 13, (3, 1): 21, (3, 2): 36}
    _XING_OFFSETS[(0, 1)] = _XING_OFFSETS[(2, 1)]
    _XING_OFFSETS[(0, 2)] = _XING_OFFSETS[(2, 2)] = _XING_OFFSETS[(3, 1)]

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
        stream: BytesLike, /, end_byte: int | None = None
    ) -> list[AudioStreamInfo]:
        """ """
        if end_byte is None:
            end_byte = len(stream) - 4

        # Read first audio frame and process Xing/LAME VBR header frame,
        # if any
        offset = MPEGAudio._find_next_audio_frame(
            stream, offset=0, end_byte=end_byte
        )
        byte_2 = stream[offset + 1]
        mpeg = (byte_2 >> 3) & 3
        byte_3 = stream[offset + 2]
        num_channels = 2 - ((stream[offset + 3] >> 6) == 3)
        xing_offset = (
            offset
            + MPEGAudio._XING_OFFSETS[mpeg, num_channels]
            + 2 * (not (byte_2 & 1))
        )
        if (magic_string := stream[xing_offset : xing_offset + 4]) == b"Info":
            debug = True
        elif magic_string == b"Xing":
            debug = True
        else:
            sample_rate = MPEGAudio._SAMPLE_RATES[mpeg][(byte_3 >> 2) & 3]
            bitrate = MPEGAudio._BITRATES[mpeg, (byte_2 >> 1) & 3][byte_3 >> 4]
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
        self._stream_info = self._get_stream_info(view[offset:])

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
