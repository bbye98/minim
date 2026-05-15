from __future__ import annotations

from ._shared import Audio


class MP3Audio(Audio):
    """
    MP3 audio file.
    """

    __slots__ = ("_audio_offset",)

    def load_metadata(self) -> None:
        """
        Load MP3 metadata blocks.
        """
        self.open()
        file_path = self._file_path
        view = self._view

        if self._strict:
            if view[:3] == b"ID3":
                debug = True
            else:
                self._audio_offset = 0

        else:
            raise NotImplementedError

        self.close()

    def add_metadata(self) -> None:
        pass

    def remove_metadata(self) -> None:
        pass

    def save(self) -> None:
        pass
