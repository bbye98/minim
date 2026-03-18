from ._shared import SpotifyResourceAPI


class LibraryAPI(SpotifyResourceAPI):
    """
    Library API endpoints for the Spotify Web API.

    .. important::

       This class is managed by
       :class:`~minim.api.spotify.SpotifyWebAPIClient` and should not be
       instantiated directly.
    """

    def save_items(self, spotify_uris: str | list[str], /) -> None:
        """
        `Library > Save Items to Library <https://developer.spotify.com
        /documentation/web-api/reference/save-library-items>`_: Save one
        or more items to the current user's library.

        .. admonition:: Authorization scope
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 :code:`user-library-modify` scope
                    Manage your saved content. `Learn more.
                    <https://developer.spotify.com/documentation/web-api
                    /concepts/scopes#user-library-modify>`__

                 :code:`user-follow-modify` scope
                    Manage your saved content. `Learn more.
                    <https://developer.spotify.com/documentation/web-api
                    /concepts/scopes#user-follow-modify>`__

                 :code:`playlist-modify-public` scope
                    Manage your public playlists. `Learn more.
                    <https://developer.spotify.com/documentation/web-api
                    /concepts/scopes#playlist-modify-public>`__

        Parameters
        ----------
        spotify_uris : str or list[str]; positional-only
            Comma-separated string or list of Spotify URIs. A maximum of
            40 URIs can be sent in a request.
        """
        self._client._request(
            "PUT",
            "me/library",
            params={
                "uris": ",".join(
                    self._prepare_spotify_uris(
                        spotify_uris,
                        limit=40,
                        resource_types={
                            "track",
                            "album",
                            "episode",
                            "show",
                            "audiobook",
                            "user",
                            "playlist",
                        },
                    )
                )
            },
        )

    def remove_saved_items(self, spotify_uris: str | list[str], /) -> None:
        """
        `Library > Remove Items from Library
        <https://developer.spotify.com/documentation/web-api/reference
        /remove-library-items>`_: Remove one or more items from the
        current user's library.

        .. admonition:: Authorization scope
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 :code:`user-library-modify` scope
                    Manage your saved content. `Learn more.
                    <https://developer.spotify.com/documentation/web-api
                    /concepts/scopes#user-library-modify>`__

                 :code:`user-follow-modify` scope
                    Manage your saved content. `Learn more.
                    <https://developer.spotify.com/documentation/web-api
                    /concepts/scopes#user-follow-modify>`__

                 :code:`playlist-modify-public` scope
                    Manage your public playlists. `Learn more.
                    <https://developer.spotify.com/documentation/web-api
                    /concepts/scopes#playlist-modify-public>`__

        Parameters
        ----------
        spotify_uris : str or list[str]; positional-only
            Comma-separated string or list of Spotify URIs. A maximum of
            40 URIs can be sent in a request.
        """
        self._client._request(
            "DELETE",
            "me/library",
            params={
                "uris": ",".join(
                    self._prepare_spotify_uris(
                        spotify_uris,
                        limit=40,
                        resource_types={
                            "track",
                            "album",
                            "episode",
                            "show",
                            "audiobook",
                            "user",
                            "playlist",
                        },
                    )
                )
            },
        )

    def are_items_saved(self, spotify_uris: str | list[str], /) -> list[bool]:
        """
        `Library > Check User's Saved Items
        <https://developer.spotify.com/documentation/web-api/reference
        /check-library-contains>`_: Check whether one or more items are
        saved in the current user's library.

        .. admonition:: Authorization scope
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 :code:`user-library-read` scope
                    Access your saved content. `Learn more.
                    <https://developer.spotify.com/documentation/web-api
                    /concepts/scopes#user-library-read>`__

                 :code:`user-follow-read` scope
                    Access your followers and who you are following.
                    `Learn more. <https://developer.spotify.com
                    /documentation/web-api/concepts
                    /scopes#user-follow-read>`__

                 :code:`playlist-read-private` scope
                    Access your private playlists. `Learn more.
                    <https://developer.spotify.com/documentation/web-api
                    /concepts/scopes#playlist-read-private>`__

        Parameters
        ----------
        spotify_uris : str or list[str]; positional-only
            Comma-separated string or list of Spotify URIs. A maximum of
            40 URIs can be sent in a request.

        Returns
        -------
        saved : list[bool]
            Whether the current user has the specified albums saved in
            their library.
        """
        return self._client._request(
            "GET",
            "me/library/contains",
            params={
                "ids": ",".join(
                    self._prepare_spotify_uris(
                        spotify_uris,
                        limit=40,
                        resource_types={
                            "track",
                            "album",
                            "episode",
                            "show",
                            "audiobook",
                            "user",
                            "playlist",
                        },
                    )
                )
            },
        )
