from __future__ import annotations

from .._utility import decode_32_bit_synchsafe_int
from ._shared import Audio
from .metadata.id3._core import ID3v2

__all__ = ["MP3Audio"]


class MP3Audio(Audio):
    """
    MP3 audio file.
    """

    __slots__ = "_audio_offset", "_infer_frame"

    def load_metadata(self) -> None:
        """
        Load MP3 metadata blocks.
        """
        self.open()
        file_path = self._file_path
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
