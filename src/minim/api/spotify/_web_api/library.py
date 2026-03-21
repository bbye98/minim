from ..._shared import _copy_docstring
from ._shared import SpotifyResourceAPI
from .users import UsersAPI


class LibraryAPI(SpotifyResourceAPI):
    """
    Library API endpoints for the Spotify Web API.

    .. important::

       This class is managed by
       :class:`~minim.api.spotify.SpotifyWebAPIClient` and should not be
       instantiated directly.
    """

    @_copy_docstring(UsersAPI.save_items)
    def save_items(self, spotify_uris: str | list[str], /) -> None:
        self._client.users.save_items(spotify_uris)

    @_copy_docstring(UsersAPI.remove_saved_items)
    def remove_saved_items(self, spotify_uris: str | list[str], /) -> None:
        self._client.users.remove_saved_items(spotify_uris)

    @_copy_docstring(UsersAPI.are_items_saved)
    def are_items_saved(self, spotify_uris: str | list[str], /) -> list[bool]:
        return self._client.users.are_items_saved(spotify_uris)
