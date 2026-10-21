from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .._shared import Audio, MetadataView
from ..metadata._shared import AudioStreamInfo, AudioTags
from ._boxes import MP4Box, MP4ContainerBox, MP4mdatBox

if TYPE_CHECKING:
    from ..._types import Collection


@dataclass(frozen=True, kw_only=True, repr=False, slots=True)
class MP4StreamInfo(AudioStreamInfo):
    """
    MP4 :code:`moov > trak > mdia > minf > stbl > stsd > alac/mp4a` or
    audio stream information.
    """

    # TODO


class MP4MetadataView(MetadataView):
    """
    View of MP4 boxes.

    .. important::

       This class is managed by :class:`MP4Audio` and should not be
       instantiated directly.

    This class implements the following special methods:

    * :code:`__getitem__` – Return the top-level box at an index.

    * :code:`__iter__` – Return an iterator of the top-level boxes.

    * :code:`__len__` – Return the number of top-level boxes.
    """

    __slots__ = ("_audio",)

    def __init__(self, audio: MP4Audio, /) -> None:
        """
        Parameters
        ----------
        audio : MP4Audio
            MP4 audio handler.
        """
        self._audio = audio
        self._metadata = audio._metadata

    def __repr__(self) -> str:
        return f"{type(self).__name__}(<{len(self._metadata)} MP4 box(es)>)"

    def _type_index(self) -> dict[type[MP4Box], list[MP4Box]]:
        return self._audio._type_index

    def get(
        self, types: type[MP4Box] | Collection[type[MP4Box]], /
    ) -> list[MP4Box] | dict[type[MP4Box], list[MP4Box]]:
        """
        Get top-level MP4 boxes and their descendents by type.

        Parameters
        ----------
        types : type[MP4Box] or Collection[type[MP4Box]]; \
        positional-only
            Types of MP4 boxes.

        Returns
        -------
        boxes : list[MP4Box] or dict[type[MP4Box], list[MP4Box]]
            MP4 boxes. If `types` is a collection, a dictionary mapping 
            the MP4 box types to the MP4 boxes is returned.
        """
        raise NotImplementedError()  # TODO


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

    __slots__ = ()

    @property
    def _type_index(self) -> defaultdict[MP4Box, list[MP4Box]]:
        type_index = defaultdict(list)
        for box in self._metadata:
            self._index_box(box, type_index=type_index)
        return type_index

    @property
    def audio_data(self):
        raise NotImplementedError()  # TODO

    @property
    def metadata(self):
        raise NotImplementedError()  # TODO

    @staticmethod
    def _index_box(
        box: MP4Box,
        /,
        type_index: defaultdict[MP4Box, list[MP4Box]],
    ) -> None:
        """
        Recursively add boxes to the type index in-place.

        Parameters
        ----------
        box : MP4Box; positional-only
            MP4 box.

        type_index : defaultdict[MP4Box, list[MP4Box]]; keyword-only
            Type index.

            .. note::

               This `defaultdict` is mutated in-place.
        """
        type_index[box._fourcc].append(box)
        if isinstance(box, MP4ContainerBox):
            for pl in box._payload:
                MP4Audio._index_box(pl, type_index=type_index)

    def _set_active_tags(self) -> None:
        raise NotImplementedError()  # TODO

    def add_metadata(self) -> None:
        raise NotImplementedError()  # TODO

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
        self._metadata_view = MP4MetadataView(self)
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
            offset += box._box_length

        self.close()

    def remove_metadata(self) -> None:
        raise NotImplementedError()  # TODO

    def save(self) -> None:
        raise NotImplementedError()  # TODO
