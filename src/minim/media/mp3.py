from __future__ import annotations
from typing import TYPE_CHECKING

from .._utility import decode_32_bit_synchsafe_int, validate_type
from ._shared import Audio
from .metadata.id3._core import ID3v2

if TYPE_CHECKING:
    from .._types import PathLike

__all__ = ["MP3Audio"]


class MP3Audio(Audio):
    """
    MP3 audio file.
    """

    __slots__ = "_audio_offset", "_infer_frame"

    def __init__(
        self,
        file_path: PathLike,
        /,
        *,
        infer_frame: bool = False,
        strict: bool = True,
    ) -> None:
        """
        Parameters
        ----------
        file_path : str or pathlib.Path; positional-only
            Path to or name of the MP3 audio file.

        infer_frame : bool; keyword-only; default: :code:`False`
            Whether to check if the description of a :code:`TXXX` frame
            matches a standard ID3v2 frame ID and automatically upgrade
            the resulting object to that specialized frame type.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the MP3
            format specifications.
        """
        validate_type("infer_frame", infer_frame, bool)
        self._infer_frame = infer_frame
        super().__init__(file_path, strict=strict)

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
            offset = 10 + decode_32_bit_synchsafe_int(*view[6:10])
            if view[:3] == b"ID3":
                tags = ID3v2.from_stream(
                    view[:offset], infer_frame=self._infer_frame, strict=strict
                )
                self._format_metadata.append(tags)
                self._tags = tags
                self._audio_offset = offset
                ...  # TODO
            else:
                self._audio_offset = 0

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
