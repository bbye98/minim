from collections.abc import Collection
from datetime import datetime
from typing import TYPE_CHECKING, Any

from ..._shared import ResourceAPI, _copy_docstring
from .albums import AlbumsAPI
from .artists import ArtistsAPI
from .audiobooks import AudiobooksAPI
from .episodes import EpisodesAPI
from .playlists import PlaylistsAPI
from .shows import ShowsAPI
from .tracks import TracksAPI

if TYPE_CHECKING:
    from .. import SpotifyWebAPI


class UsersAPI(ResourceAPI):
    """
    Users API endpoints for the Spotify Web API.

    .. note::

       This class is managed by :class:`minim.api.spotify.SpotifyWebAPI`
       and should not be instantiated directly.
    """

    _TIME_RANGES = {"long_term", "medium_term", "short_term"}
    _client: "SpotifyWebAPI"

    def get_user_profile(self, user_id: str | None = None, /) -> dict[str, Any]:
        """
        `Users > Get Current User's Profile
        <https://developer.spotify.com/documentation/web-api/reference
        /get-current-users-profile>`_: Get detailed profile information
        for the current user․
        `Users > Get User's Profile <https://developer.spotify.com
        /documentation/web-api/reference/get-users-profile>`_: Get
        public profile information for a specific Spotify user.

        .. admonition:: Authorization scopes
           :class: authorization-scope

           .. tab:: Optional

              :code:`user-read-private`
                 Access your subscription details. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#user-read-private>`__

              :code:`user-read-email`
                 Get your real email address. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#user-read-email>`__

        Parameters
        ----------
        user_id : str, positional-only, optional
            Spotify user ID. If not provided, the current user's
            profile will be returned.

            **Example**: :code:`"smedjan"`.

        Returns
        -------
        profile : dict[str, Any]
            User's profile information.

            .. admonition:: Sample responses
               :class: dropdown

               .. tab:: Current user

                  .. code::

                     {
                       "country": <str>,
                       "display_name": <str>,
                       "email": <str>,
                       "explicit_content": {
                         "filter_enabled": <bool>,
                         "filter_locked": <bool>
                       },
                       "external_urls": {
                         "spotify": <str>
                       },
                       "followers": {
                         "href": <str>,
                         "total": <int>
                       },
                       "href": <str>,
                       "id": <str>,
                       "images": [
                         {
                           "height": <int>,
                           "url": <str>,
                           "width": <int>
                         }
                       ],
                       "product": <str>,
                       "type": "user",
                       "uri": <str>
                     }

               .. tab:: Public user

                  .. code::

                     {
                       "display_name": <str>,
                       "external_urls": {
                         "spotify": <str>
                       },
                       "followers": {
                         "href": <str>,
                         "total": <int>
                       },
                       "href": <str>,
                       "id": <str>,
                       "images": [
                         {
                           "height": <int>,
                           "url": <str>,
                           "width": <int>
                         }
                       ],
                       "type": "user",
                       "uri": <str>
                     }
        """
        if user_id:
            self._client._validate_spotify_id(user_id, strict_length=False)
            return self._client._request("GET", f"users/{user_id}").json()

        return self._client._request("GET", "me").json()

    @_copy_docstring(ArtistsAPI.get_my_top_artists)
    def get_my_top_artists(
        self,
        *,
        time_range: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.artists.get_my_top_artists(
            time_range=time_range, limit=limit, offset=offset
        )

    @_copy_docstring(TracksAPI.get_my_top_tracks)
    def get_my_top_tracks(
        self,
        *,
        time_range: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.tracks.get_my_top_tracks(
            time_range=time_range, limit=limit, offset=offset
        )

    @_copy_docstring(PlaylistsAPI.follow_playlist)
    def follow_playlist(
        self, playlist_id: str, /, *, public: bool | None = None
    ) -> None:
        self._client.playlists.follow_playlist(playlist_id, public=public)

    @_copy_docstring(PlaylistsAPI.unfollow_playlist)
    def unfollow_playlist(self, playlist_id: str, /) -> None:
        self._client.playlists.unfollow_playlist(playlist_id)

    @_copy_docstring(ArtistsAPI.get_my_followed_artists)
    def get_my_followed_artists(
        self, *, after: str | None = None, limit: int | None = None
    ) -> dict[str, Any]:
        return self._client.artists.get_my_followed_artists(
            after=after, limit=limit
        )

    @_copy_docstring(ArtistsAPI.follow_artists)
    def follow_artists(self, artist_ids: str | Collection[str], /) -> None:
        self._client.artists.follow_artists(artist_ids)

    def follow_users(self, user_ids: str | Collection[str], /) -> None:
        """
        `Users > Follow Users <https://developer.spotify.com
        /documentation/web-api/reference/follow-artists-users>`_: Follow
        one or more Spotify users.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-follow-modify` scope
                 Manage your saved content. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#user-follow-modify>`__

        Parameters
        ----------
        user_ids : str or Collection[str], positional-only
            Spotify user IDs, provided as either a comma-separated
            string or a collection of strings. A maximum of 50 IDs can
            be sent in one request.

            **Examples**: :code:`"smedjan"`, :code:`"smedjan,bbye98"`,
            :code:`["smedjan", "bbye98"]`.
        """
        self._client._require_scopes("users.follow_users", "user-follow-modify")
        self._client._request(
            "PUT",
            "me/following",
            params={
                "type": "user",
                "ids": self._client._prepare_spotify_ids(
                    user_ids, limit=50, strict_length=False
                )[0],
            },
        )

    @_copy_docstring(ArtistsAPI.unfollow_artists)
    def unfollow_artists(self, artist_ids: str | Collection[str], /) -> None:
        self._client.artists.unfollow_artists(artist_ids)

    def unfollow_users(self, user_ids: str | Collection[str], /) -> None:
        """
        `Users > Unfollow Users <https://developer.spotify.com
        /documentation/web-api/reference/unfollow-artists-users>`_:
        Unfollow one or more Spotify users.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-follow-modify` scope
                 Manage your saved content. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#user-follow-modify>`__

        Parameters
        ----------
        user_ids : str or Collection[str], positional-only
            Spotify user IDs, provided as either a comma-separated
            string or a collection of strings. A maximum of 50 IDs can
            be sent in one request.

            **Examples**: :code:`"smedjan"`, :code:`"smedjan,bbye98"`,
            :code:`["smedjan", "bbye98"]`.
        """
        self._client._require_scopes(
            "users.unfollow_users", "user-follow-modify"
        )
        self._client._request(
            "DELETE",
            "me/following",
            params={
                "type": "user",
                "ids": self._client._prepare_spotify_ids(
                    user_ids, limit=50, strict_length=False
                )[0],
            },
        )

    @_copy_docstring(ArtistsAPI.is_following_artists)
    def is_following_artists(
        self, artist_ids: str | Collection[str], /
    ) -> list[bool]:
        return self._client.artists.is_following_artists(artist_ids)

    def is_following_users(
        self, user_ids: str | Collection[str], /
    ) -> list[bool]:
        """
        `Users > Check If User Follows Users
        <https://developer.spotify.com/documentation/web-api/reference
        /check-current-user-follows>`_: Check whether the current user
        is following one or more Spotify users.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-follow-read` scope
                 Access your followers and who you are following. `Learn
                 more. <https://developer.spotify.com/documentation
                 /web-api/concepts/scopes#user-follow-read>`__

        Parameters
        ----------
        user_ids : str or Collection[str], positional-only
            Spotify user IDs, provided as either a comma-separated
            string or a collection of strings. A maximum of 50 IDs can
            be sent in one request.

            **Examples**: :code:`"smedjan"`, :code:`"smedjan,bbye98"`,
            :code:`["smedjan", "bbye98"]`.

        Returns
        -------
        following : list[bool]
            Whether the current user follows each specified user.

            **Sample response**: :code:`[False, True]`.
        """
        self._client._require_scopes(
            "users.is_following_users", "user-follow-read"
        )
        return self._client._request(
            "GET",
            "me/following/contains",
            params={
                "type": "user",
                "ids": self._client._prepare_spotify_ids(
                    user_ids, limit=50, strict_length=False
                )[0],
            },
        ).json()

    @_copy_docstring(PlaylistsAPI.is_following_playlist)
    def is_following_playlist(self, playlist_id: str, /) -> bool:
        return self._client.playlists.is_following_playlist(playlist_id)

    @_copy_docstring(AlbumsAPI.get_my_saved_albums)
    def get_my_saved_albums(
        self,
        *,
        market: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.albums.get_my_saved_albums(
            market=market, limit=limit, offset=offset
        )

    @_copy_docstring(AlbumsAPI.save_albums)
    def save_albums(self, album_ids: str | Collection[str], /) -> None:
        self._client.albums.save_albums(album_ids)

    @_copy_docstring(AlbumsAPI.remove_saved_albums)
    def remove_saved_albums(self, album_ids: str | Collection[str], /) -> None:
        self._client.albums.remove_saved_albums(album_ids)

    @_copy_docstring(AlbumsAPI.are_albums_saved)
    def are_albums_saved(
        self, album_ids: str | Collection[str], /
    ) -> list[bool]:
        return AlbumsAPI.are_albums_saved(album_ids)

    @_copy_docstring(AudiobooksAPI.get_my_saved_audiobooks)
    def get_my_saved_audiobooks(
        self,
        *,
        market: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.audiobooks.get_my_saved_audiobooks(
            market=market, limit=limit, offset=offset
        )

    @_copy_docstring(AudiobooksAPI.save_audiobooks)
    def save_audiobooks(self, audiobook_ids: str | Collection[str], /) -> None:
        self._client.audiobooks.save_audiobooks(audiobook_ids)

    @_copy_docstring(AudiobooksAPI.remove_saved_audiobooks)
    def remove_saved_audiobooks(
        self, audiobook_ids: str | Collection[str], /
    ) -> None:
        self._client.audiobooks.remove_saved_audiobooks(audiobook_ids)

    @_copy_docstring(AudiobooksAPI.are_audiobooks_saved)
    def are_audiobooks_saved(
        self, audiobook_ids: str | Collection[str], /
    ) -> list[bool]:
        return self._client.audiobooks.are_audiobooks_saved(audiobook_ids)

    @_copy_docstring(EpisodesAPI.get_my_saved_episodes)
    def get_my_saved_episodes(
        self,
        *,
        market: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.episodes.get_my_saved_episodes(
            market=market, limit=limit, offset=offset
        )

    @_copy_docstring(EpisodesAPI.save_episodes)
    def save_episodes(self, episode_ids: str | Collection[str], /) -> None:
        self._client.episodes.save_episodes(episode_ids)

    @_copy_docstring(EpisodesAPI.remove_saved_episodes)
    def remove_saved_episodes(
        self, episode_ids: str | Collection[str], /
    ) -> None:
        self._client.episodes.remove_saved_episodes(episode_ids)

    @_copy_docstring(EpisodesAPI.are_episodes_saved)
    def are_episodes_saved(
        self, episode_ids: str | Collection[str], /
    ) -> list[bool]:
        return self._client.episodes.are_episodes_saved(episode_ids)

    def get_my_playlists(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> dict[str, Any]:
        """
        `Playlists > Get Current User's Playlists
        <https://developer.spotify.com/documentation/web-api/reference
        /get-a-list-of-current-users-playlists>`_: Get Spotify catalog
        information for playlists owned or followed by the current user.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`playlist-read-private` scope
                 Access your private playlists. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#playlist-read-private>`__

        Parameters
        ----------
        limit : int, keyword-only, optional
            Maximum number of playlists to return.

            **Valid range**: :code:`1` to :code:`50`.

            **Default**: :code:`20`.

        offset : int, keyword-only, optional
            Index of the first playlist to return. Use with `limit` to
            get the next set of playlists.

            **Minimum value**: :code:`0`.

            **Default**: :code:`0`.

        Returns
        -------
        playlists : dict[str, Any]
            Pages of Spotify content metadata for the current user's
            playlists.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "items": [
                      {
                        "collaborative": <bool>,
                        "description": <str>,
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "id": <str>,
                        "images": [
                          {
                            "height": <int>,
                            "url": <str>,
                            "width": <int>
                          }
                        ],
                        "name": <str>,
                        "owner": {
                          "display_name": <str>,
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "type": <str>,
                          "uri": <str>
                        },
                        "public": <bool>,
                        "snapshot_id": <str>,
                        "tracks": {
                          "href": <str>,
                          "total": <int>
                        },
                        "type": <str>,
                        "uri": <str>
                      }
                    ],
                    "limit": <int>,
                    "next": <str>,
                    "offset": <int>,
                    "previous": <str>,
                    "total": <int>
                  }
        """
        return self._client.playlists.get_user_playlists(
            limit=limit, offset=offset
        )

    @_copy_docstring(ShowsAPI.get_my_saved_shows)
    def get_my_saved_shows(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> dict[str, Any]:
        return self._client.shows.get_my_saved_shows(limit=limit, offset=offset)

    @_copy_docstring(ShowsAPI.save_shows)
    def save_shows(self, show_ids: str | Collection[str], /) -> None:
        self._client.shows.save_shows(show_ids)

    @_copy_docstring(ShowsAPI.remove_saved_shows)
    def remove_saved_shows(self, show_ids: str | Collection[str], /) -> None:
        self._client.shows.remove_saved_shows(show_ids)

    @_copy_docstring(ShowsAPI.are_shows_saved)
    def are_shows_saved(self, show_ids: str | Collection[str], /) -> list[bool]:
        return self._client.shows.are_shows_saved(show_ids)

    @_copy_docstring(TracksAPI.get_my_saved_tracks)
    def get_my_saved_tracks(
        self,
        *,
        market: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.tracks.get_my_saved_tracks(
            market=market, limit=limit, offset=offset
        )

    @_copy_docstring(TracksAPI.save_tracks)
    def save_tracks(
        self,
        track_ids: str
        | tuple[str, str | datetime]
        | dict[str, str | datetime]
        | list[str | tuple[str, str | datetime] | dict[str, str | datetime]],
        /,
    ) -> None:
        self._client.tracks.save_tracks(track_ids)

    @_copy_docstring(TracksAPI.remove_saved_tracks)
    def remove_saved_tracks(self, track_ids: str | Collection[str], /) -> None:
        self._client.tracks.remove_saved_tracks(track_ids)

    @_copy_docstring(TracksAPI.are_tracks_saved)
    def are_tracks_saved(
        self, track_ids: str | Collection[str], /
    ) -> list[bool]:
        return self._client.tracks.are_tracks_saved(track_ids)

    def _validate_time_range(self, time_range: str, /) -> None:
        """
        Validate time frame.

        Parameters
        ----------
        time_range : str, positional-only
            Time frame.
        """
        if (
            not isinstance(time_range, str)
            or time_range not in self._TIME_RANGES
        ):
            ranges_ = "', '".join(self._TIME_RANGES)
            raise ValueError(
                f"Invalid time frame {time_range!r}. Valid values: '{ranges_}'."
            )
