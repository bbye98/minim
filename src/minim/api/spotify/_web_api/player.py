from collections.abc import Collection
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .. import WebAPI


class WebAPIPlayerEndpoints:
    """
    Spotify Web API player endpoints.

    .. important::

       This class is managed by :class:`minim.api.spotify.WebAPI` and
       should not be instantiated directly.
    """

    def __init__(self, client: "WebAPI", /) -> None:
        """
        Parameters
        ----------
        client : minim.api.spotify.WebAPI
            Minim's Spotify Web API client.
        """
        self._client = client

    def get_state(
        self, *, market: str | None = None, additional_types: str | None = None
    ) -> dict[str, Any]:
        pass

    def transfer(self, device_id: str, /, play: bool | None = None) -> None:
        pass

    def get_devices(
        self,
    ) -> dict[str, list[dict[str, bool | int | str]]]:
        pass

    def get_currently_playing(
        self, *, market: str | None = None, additional_types: str | None = None
    ) -> dict[str, Any]:
        pass

    def start(
        self,
        device_id: str,
        /,
        context_uri: str | None = None,
        track_uris: str | Collection[str] | None = None,
        offset: dict[str, int | str] | None = None,
    ) -> None:
        pass

    def pause(self, device_id: str, /) -> None:
        pass

    def skip_next(self, device_id: str, /) -> None:
        pass

    def skip_previous(self, device_id: str, /) -> None:
        pass

    def seek(self, position_ms: int, *, device_id: str | None = None) -> None:
        pass

    def set_repeat(
        self, state: str, /, *, device_id: str | None = None
    ) -> None:
        pass

    def set_volume(
        self, volume_percent: int, /, *, device_id: str | None = None
    ) -> None:
        pass

    def set_shuffle(
        self, state: bool, /, *, device_id: str | None = None
    ) -> None:
        pass

    def get_recently_played(
        self,
        *,
        limit: int | None = None,
        after: int | None = None,
        before: int | None = None,
    ) -> dict[str, Any]:
        pass

    def get_queue(self) -> dict[str, Any]:
        pass

    def add_to_queue(
        self, uri: str, /, *, device_id: str | None = None
    ) -> None:
        pass
