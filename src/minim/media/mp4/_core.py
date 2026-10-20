from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from .._shared import Audio, MetadataView
from ..metadata._shared import AudioStreamInfo, AudioTags
from ._boxes import MP4Box, MP4mdatBox


# @dataclass(frozen=True, kw_only=True, repr=False, slots=True)
# class MP4StreamInfo(AudioStreamInfo):
#     """
#     MP4 :code:`moov > trak > mdia > minf > stbl > stsd > alac/mp4a` or
#     audio stream information.
#     """


class MP4Audio(Audio):
    """
    MP4 audio file.

    .. note::

       Metadata structures and ancillary information are loaded from
       the audio file when the object is instantiated.

       .. seealso::

          :meth:`load_metadata` – Load metadata structures and ancillary
          information from the audio file.
    """

    @property
    def audio_data(self):
        raise NotImplementedError()

    @property
    def metadata(self):
        raise NotImplementedError()

    def _set_active_tags(self) -> None:
        raise NotImplementedError()

    def add_metadata(self) -> None:
        raise NotImplementedError()

    def load_metadata(self) -> None:
        """
        Load metadata blocks from the MP4 audio file.
        """
        self.open()
        file_path = self._file_path
        view = self._view
        view_length = len(view)
        strict = self._strict

        self._metadata = boxes = []
        self._type_index = type_index = defaultdict(list)
        # self._metadata_view = MP4MetadataView(metadata, type_index=type_index)
        self._tags = None

        offset = 0
        while offset < view_length:
            if (
                box_cls := MP4Box._get_class(view[offset + 4 : offset + 8])
            ) is MP4mdatBox:
                box = box_cls._from_stream(
                    view[offset:],
                    file_path=file_path,
                    offset=offset,
                    strict=strict,
                )
            else:
                box = box_cls._from_stream(view[offset:], strict=strict)
            boxes.append(box)
            type_index[box._fourcc].append(box)
            offset += box._box_length

        # TODO

    def remove_metadata(self) -> None:
        raise NotImplementedError()

    def save(self) -> None:
        raise NotImplementedError()
